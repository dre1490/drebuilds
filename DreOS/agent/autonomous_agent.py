# autonomous_agent.py
# DreOS Phase 12 — Step 2
# The ReAct reasoning loop — Reason, Act, Observe, repeat
# Location: DreOS\agent\autonomous_agent.py

import os
import sys
import json
from datetime import datetime
from groq import Groq

# ── Path setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
sys.path.insert(0, os.path.join(BASE_DIR, "agent"))

from tool_registry import TOOL_REGISTRY, dispatch_tool

# ── Groq client ────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = MODEL = "llama-3.3-70b-versatile"

# ── Max reasoning steps before we force a final answer ────────────────────────
MAX_STEPS = 8


# ══════════════════════════════════════════════════════════════════════════════
# TOOL DEFINITIONS — formatted for Groq's tool calling API
# ══════════════════════════════════════════════════════════════════════════════
GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_market_data",
            "description": "Fetch current prices for all 25 tracked assets (stocks, crypto, mutual funds)",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Fetch today's top news headlines and weather summary",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_history",
            "description": "Get recent price history for a specific ticker from the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Asset symbol e.g. AAPL, BTC, VFIAX, NVDA"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back, default 7"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_jira_status",
            "description": "Get current status of all Jira tickets on the KAN board",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_figma_status",
            "description": "Check recent activity on the DreOS Figma design file",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_price_spike",
            "description": "Scan all tracked assets for price moves above a threshold percentage",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold_pct": {
                        "type": "number",
                        "description": "Alert threshold percentage, default 5.0"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_alert",
            "description": "Send an alert message to terminal and Gmail email",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The alert message body"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line, default 'DreOS Agent Alert'"
                    }
                },
                "required": ["message"]
            }
        }
    }
]


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT — tells Groq who it is and how to reason
# ══════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are DreOS Agent — an autonomous personal intelligence assistant for Dre.

You have access to tools that let you check market prices, read news, query price history, 
check Jira project status, check Figma design activity, detect price spikes, and send alerts.

Your job is to reason through goals step by step using the ReAct pattern:
1. THINK — reason about what you know and what you need to find out
2. ACT — call a tool to get more information
3. OBSERVE — read the tool result
4. Repeat until you have enough to give a complete, useful answer

Rules:
- Always use tools to get real data — never make up prices or statistics
- If you detect something unusual (price spike, urgent news, overdue tickets), call send_alert
- Be concise and direct in your final answer — Dre is busy
- If a goal involves multiple data sources, chain the tools together
- Always end with a clear summary of what you found and what action (if any) you took

You are proactive. If you notice something worth flagging while completing a task, flag it.
"""


# ══════════════════════════════════════════════════════════════════════════════
# AGENT LOG — saves the reasoning trace to outputs/agent_log.json
# ══════════════════════════════════════════════════════════════════════════════
def save_agent_log(goal: str, steps: list, final_answer: str):
    log = {
        "timestamp": datetime.now().isoformat(),
        "goal": goal,
        "steps": steps,
        "final_answer": final_answer,
        "tool_calls_made": sum(1 for s in steps if s.get("type") == "tool_call")
    }
    log_path = os.path.join(OUTPUTS_DIR, "agent_log.json")
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"[autonomous_agent] 📝 reasoning log saved → outputs/agent_log.json")


# ══════════════════════════════════════════════════════════════════════════════
# REACT LOOP — the core reasoning engine
# ══════════════════════════════════════════════════════════════════════════════
def run_agent(goal: str) -> str:
    """
    Runs the ReAct reasoning loop for a given goal.
    Args:
        goal: What you want the agent to do in plain English
    Returns the agent's final answer as a string.
    """
    print("\n" + "="*60)
    print(f"🤖 DreOS Agent — Starting")
    print(f"🎯 Goal: {goal}")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Build the conversation history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal}
    ]

    steps = []      # reasoning trace for the log
    step_num = 0

    # ── ReAct loop ─────────────────────────────────────────────────────────────
    while step_num < MAX_STEPS:
        step_num += 1
        print(f"\n[Step {step_num}] Thinking...")

        # Call Groq — let it reason and optionally call a tool
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=GROQ_TOOLS,
            tool_choice="auto",
            max_tokens=1024
        )

        choice = response.choices[0]
        finish_reason = choice.finish_reason
        assistant_message = choice.message

        # ── No tool call — agent has a final answer ────────────────────────────
        if finish_reason == "stop" or not assistant_message.tool_calls:
            final_answer = assistant_message.content or "Task complete."
            print(f"\n[Step {step_num}] ✅ Final answer reached\n")
            print("="*60)
            print("🤖 AGENT RESPONSE:")
            print("="*60)
            print(final_answer)
            print("="*60 + "\n")

            steps.append({"type": "final_answer", "content": final_answer})
            save_agent_log(goal, steps, final_answer)
            return final_answer

        # ── Tool call — agent wants to use a tool ──────────────────────────────
        # Add assistant's message to history
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_params = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_params = {}

            print(f"[Step {step_num}] 🔧 Calling tool: {tool_name}({tool_params})")

            # Dispatch the tool
            tool_result = dispatch_tool(tool_name, tool_params)
            result_str = json.dumps(tool_result, indent=2)

            # Log the step
            steps.append({
                "type": "tool_call",
                "step": step_num,
                "tool": tool_name,
                "params": tool_params,
                "result_preview": result_str[:300] + "..." if len(result_str) > 300 else result_str
            })

            print(f"[Step {step_num}] 📦 Tool result: {result_str[:200]}{'...' if len(result_str) > 200 else ''}")

            # Add tool result back into conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_str
            })

    # ── Hit max steps — force a final answer ───────────────────────────────────
    print(f"\n[autonomous_agent] ⚠️  Max steps ({MAX_STEPS}) reached — requesting final answer")

    messages.append({
        "role": "user",
        "content": "You have reached the maximum number of steps. Please provide your final answer now based on everything you have gathered so far."
    })

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1024
    )

    final_answer = final_response.choices[0].message.content or "Max steps reached. Check agent_log.json for details."

    print("\n" + "="*60)
    print("🤖 AGENT RESPONSE (max steps):")
    print("="*60)
    print(final_answer)
    print("="*60 + "\n")

    steps.append({"type": "final_answer_forced", "content": final_answer})
    save_agent_log(goal, steps, final_answer)
    return final_answer


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST — run directly to test the agent
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\nDreOS Autonomous Agent — Phase 12 Step 2")
    print("Testing with a simple goal...\n")

    # Test 1 — simple single tool
    run_agent("What are the current prices for my tracked assets?")
