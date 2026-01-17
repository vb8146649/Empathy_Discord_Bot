import asyncio
from agents import EmpathySystem

async def run_terminal_demo():
    system = EmpathySystem()
    print("\n--- 🛡️  EMPATHY BRIDGE TERMINAL DEMO 🛡️ ---")
    print("Type a message to test the agents. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        print("... Agent A (Watcher) is analyzing ...")
        analysis = await system.agent_watcher(user_input)

        if analysis.is_toxic:
            print(f"\n[!] TOXICITY DETECTED (Score: {analysis.score})")
            print(f"[!] Reason: {analysis.reason}")
            
            print("... Agent B (Diplomat) is rewriting ...")
            rewrite = await system.agent_diplomat(user_input)
            print(f"--> Diplomat Suggestion: {rewrite}")
            
            print("... Agent C (Coach) is drafting DM ...")
            coach_msg = await system.agent_coach(user_input, rewrite)
            print(f"--> Coach DM: {coach_msg}\n")
        else:
            print(f"✅ Message Safe (Score: {analysis.score}). Sent.\n")

if __name__ == "__main__":
    asyncio.run(run_terminal_demo())