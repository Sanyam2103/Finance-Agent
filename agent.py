
import json
import os
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from tools import TOOLS, CURRENT_SESSION

# Load environment variables from .env file
load_dotenv()

# Configuration for Gemini
# Using the latest Flash model for optimal speed and reasoning
MODEL = "gemini-2.5-flash"
MEMORY_FILE = "memory.json"

# Configure the Gemini client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("FATAL: Please set the GEMINI_API_KEY in your .env file.")
    exit(1)

# The new SDK uses genai.Client
client = genai.Client(api_key=api_key)

def load_memory():
    """Loads memory from the JSON file."""
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    """Saves memory to the JSON file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def extract_learned_facts(conversation_history):
    """
    Uses the LLM to extract key facts and commitments from a conversation.
    """
    print("\n--- Extracting Learned Facts ---")
    
    history_str = ""
    for entry in conversation_history:
        role = entry['role']
        text = ""
        for part in entry['parts']:
            if 'text' in part:
                text += part['text']
        history_str += f"{role.capitalize()}: {text}\n"

    prompt = (
        "You are a summarization expert. Read the following conversation and extract key facts, decisions, and commitments made by the user. "
        "Do not leave out any type of expense (eg. entertainment, groceries etc.)"
        "Present them as a concise list of bullet points. Focus on things that will be important for future financial advice.\n\n"
        "CONVERSATION:\n"
        f"{history_str}\n\n"
        "EXTRACTED FACTS:"
    )

    # Use the globally defined 'client' and 'MODEL' from the new SDK
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    
    # Safely extract the text response
    if response.text:
        facts = response.text.strip().split('\n')
        # Improved cleaning: removes various bullet styles like '-', '*', or '•'
        cleaned_facts = [fact.lstrip('*-• ').strip() for fact in facts if fact.strip()]
    else:
        cleaned_facts = []
        
    print(f"Facts extracted: {cleaned_facts}")
    return cleaned_facts


def process_tool_result(fn_name, raw_result):
    """
    Processes raw tool output to perform calculations and return a summary.
    This keeps arithmetic out of the LLM.
    """
    if fn_name == "get_recent_transactions":
        # Ensure raw_result is a list for proper processing
        if not isinstance(raw_result, list):
            print(f"Warning: Expected list for get_recent_transactions, got {type(raw_result)}")
            return raw_result # Or handle error appropriately

        # Dynamically calculate spend for each category
        category_spend = {}
        for t in raw_result:
            category = t.get('category')
            amount = t.get('amount')
            if category and amount is not None and amount < 0:
                category_spend[category] = category_spend.get(category, 0) + abs(amount)

        total_spend = sum(category_spend.values())
        
        return {
            "summary": {
                "total_spend_in_period": total_spend,
                "spend_by_category": category_spend,
                "transaction_count": len(raw_result)
            },
            "raw_data_hint": "Full transaction list is available if needed for specific details."
        }
    elif fn_name == "get_upcoming_bills":
        if not isinstance(raw_result, list):
            print(f"Warning: Expected list for get_upcoming_bills, got {type(raw_result)}")
            return raw_result
        
        total_bills = sum(b['amount'] for b in raw_result if b.get('amount') is not None)
        
        return {
            "summary": {
                "total_upcoming_bills": total_bills,
                "bill_count": len(raw_result)
            },
            "bills": raw_result # Still include the detailed list for the LLM to read
        }
        
    # For other tools, return the result as is
    return raw_result

def run_agent(user_input, use_full_history=True):
    if not user_input.strip():
        return "Please say something!"

    memory = load_memory()
    today = "2025-11-03" if CURRENT_SESSION == 1 else "2025-11-06"
    
    facts_str = "\n".join(memory.get("learned_facts", []))
    
    # In the new SDK, passing a list of Python functions directly to 'tools' works automatically.
    # To maintain manual control, we must disable automatic_function_calling.
    config = types.GenerateContentConfig(
        system_instruction=(
            f"You are a helpful finance companion. Today is {today}. "
            f"You are a helpful finance companion for {memory['user_profile']['name']}. Her monthly income is ₹{memory['user_profile']['monthly_income_inr']}. "
            f"Base your advice on her stated goal: {memory['user_profile']['stated_goal']}. "
            "IMPORTANT:\n"
            "1. Use tools to get data. DO NOT make up numbers.\n"
            "2. When tools provide a 'summary', use those numbers for your reasoning.\n"
            "3. Connect new requests to existing goals and previously stated commitments.\n"
            f"Known facts from previous sessions:\n{facts_str}"
            f"4. when calculating savings, keep in account the average monthly costs that incur."
            "5. Average monthly costs should not include fixed costs (eg. rent, SIP). "
            "TOOL USAGE GUIDELINES:\n"
            "- For questions about 'this month' or a monthly analysis, use `get_recent_transactions(days=30)`.\n"
            "- For questions about 'this week' or recent activity, use `get_recent_transactions(days=7)`."
        ),
        tools=list(TOOLS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    # Convert stored history back to Content objects safely
    history = []
    if use_full_history:
        for msg in memory.get("conversation_history", []):
            role = "model" if msg["role"] == "assistant" else msg["role"]
            parts = []
            for p in msg["parts"]:
                if "text" in p:
                    parts.append(types.Part.from_text(text=p["text"]))
                elif "function_call" in p:
                    parts.append(types.Part(function_call=types.FunctionCall(**p["function_call"])))
                elif "function_response" in p:
                    parts.append(types.Part(function_response=types.FunctionResponse(**p["function_response"])))
                    
            history.append(types.Content(role=role, parts=parts))

    # Create a chat session
    chat = client.chats.create(model=MODEL, config=config, history=history)

    # Send the initial user message
    response = chat.send_message(user_input)
    
    # Manual tool loop
    while True:
        # The new SDK provides a direct property for function_calls
        tool_calls = response.function_calls
        
        if not tool_calls:
            break
            
        responses = []
        for call in tool_calls:
            fn_name = call.name
            args = call.args
            print(f">>> TOOL CALL: {fn_name}({args})")
            
            # Execute the actual tool to get raw result
            raw_result = TOOLS[fn_name](**args)
            
            # Process the raw result to get a summarized version
            processed_result = process_tool_result(fn_name, raw_result)
            print(f"<<< PROCESSED TOOL RESULT: {processed_result}")
            
            # Construct function response. Gemini 3+ models require 'id' to map responses correctly.
            func_resp_kwargs = {
                "name": fn_name,
                "response": {"content": json.dumps(processed_result)} # Use processed_result here
            }
            if hasattr(call, "id") and call.id:
                func_resp_kwargs["id"] = call.id

            responses.append(types.Part(
                function_response=types.FunctionResponse(**func_resp_kwargs)
            ))
        
        # Send tool results back to the model
        response = chat.send_message(responses)

    # Extract the final response text safely using the new top-level property
    final_text = response.text

    # Update history in memory
    serializable_history = []
    
    # Depending on SDK minor build version, history is accessible natively or via getter
    chat_history_list = chat.get_history() if hasattr(chat, "get_history") else chat.history
    
    for content in chat_history_list:
        parts = []
        for part in content.parts:
            p_dict = {}
            if part.text: 
                p_dict["text"] = part.text
            if part.function_call:
                p_dict["function_call"] = {
                    "name": part.function_call.name,
                    "args": part.function_call.args
                }
                # Preserve the required IDs across loads/saves
                if hasattr(part.function_call, "id") and part.function_call.id:
                    p_dict["function_call"]["id"] = part.function_call.id
                    
            if part.function_response:
                p_dict["function_response"] = {
                    "name": part.function_response.name,
                    "response": part.function_response.response
                }
                if hasattr(part.function_response, "id") and part.function_response.id:
                    p_dict["function_response"]["id"] = part.function_response.id
            parts.append(p_dict)
            
        serializable_history.append({"role": content.role, "parts": parts})

    memory["conversation_history"] = serializable_history
    save_memory(memory)
    
    return final_text

if __name__ == "__main__":
    print(f"--- Session {CURRENT_SESSION} ---")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue
            
            response = run_agent(user_input)
            print(f"Agent: {response}")
        except KeyboardInterrupt:
            break
