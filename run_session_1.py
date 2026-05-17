from agent import run_agent,load_memory, save_memory, extract_learned_facts
import os
import json

session_1_inputs = [
    "I just got my salary credited. Help me figure out how much I can realistically save this month.",
    "I feel like I'm spending too much on food delivery. How much did I actually spend on it last month?",
    "Okay that's worse than I thought. Let's say I want to cut that in half AND put aside ₹30,000 for my house fund this month — is that realistic given my upcoming bills?",
    "Got it. Remind me to actually transfer the ₹30,000 to my house fund on the 25th."
]

def run_session_1():
    print("--- Starting Session 1 ---")
    
    # Initialize/Clear memory.json for a clean test run
    base_memory = {
        "user_profile": {
            "name": "Priya Sharma",
            "age": 28,
            "city": "Bangalore",
            "monthly_income_inr": 120000,
            "stated_goal": "Save ₹15 lakh in 2 years for a house down payment in Bangalore"
        },
        "learned_facts": [],
        "reminders": [],
        "conversation_history": []
    }
    
    with open("memory.json", "w") as f:
        json.dump(base_memory, f, indent=2)
            
    for i, user_input in enumerate(session_1_inputs, 1):
        print(f"\n[Turn {i}] User: {user_input}")
        response = run_agent(user_input, use_full_history=True)
        print(f"Agent: {response}")

     # --- NEW: End-of-session memory compression ---
    final_memory = load_memory()
    new_facts = extract_learned_facts(final_memory["conversation_history"])
    final_memory["learned_facts"].extend(new_facts)
    save_memory(final_memory)

    print("\n--- Session 1 Complete ---")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        # Check .env as well manually just in case
        # pyrefly: ignore [missing-import]
        from dotenv import load_dotenv
        load_dotenv()
        if not os.environ.get("GEMINI_API_KEY"):
            print("Error: GEMINI_API_KEY not found in environment or .env file.")
        else:
            run_session_1()
    else:
        run_session_1()
