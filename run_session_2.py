from agent import run_agent
import os
from tools import CURRENT_SESSION

session_2_inputs = [
    "Hey, my colleague is selling his MacBook for ₹80,000, barely used. I've been wanting to upgrade. Should I buy it?"
]

def run_session_2():
    if CURRENT_SESSION != 2:
        print("Error: CURRENT_SESSION in tools.py must be set to 2 before running Session 2.")
        return
        
    print("--- Starting Session 2 ---")
    for i, user_input in enumerate(session_2_inputs, 1):
        print(f"\n[Turn {i}] User: {user_input}")
        response = run_agent(user_input)
        print(f"Agent: {response}")
    print("\n--- Session 2 Complete ---")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
    else:
        run_session_2()
