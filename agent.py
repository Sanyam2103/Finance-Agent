
# import json
# import os
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv
# from tools import TOOLS, CURRENT_SESSION

# # Load environment variables from .env file
# load_dotenv()

# # Configuration for Gemini
# # Using the most standard model identifier for the Google AI SDK
# MODEL = "gemini-1.5-flash" 
# MEMORY_FILE = "memory.json"

# # Configure the Gemini client
# api_key = os.environ.get("GEMINI_API_KEY")
# if not api_key:
#     print("FATAL: Please set the GEMINI_API_KEY in your .env file.")
#     exit(1)

# # The new SDK uses genai.Client for Google AI (API Key)
# client = genai.Client(api_key=api_key)

# def load_memory():
#     """Loads memory from the JSON file."""
#     with open(MEMORY_FILE, "r") as f:
#         return json.load(f)

# def save_memory(memory):
#     """Saves memory to the JSON file."""
#     with open(MEMORY_FILE, "w") as f:
#         json.dump(memory, f, indent=2)

# def run_agent(user_input):
#     if not user_input.strip():
#         return "Please say something!"

#     memory = load_memory()
#     today = "2025-11-03" if CURRENT_SESSION == 1 else "2025-11-06"
    
#     facts_str = "\n".join(memory.get("learned_facts", []))
    
#     # In the new SDK, we can pass functions directly to 'tools'
#     # The SDK will automatically handle the schema generation
#     config = types.GenerateContentConfig(
#         system_instruction=(
#             f"You are a helpful finance companion for Priya Sharma. Today is {today}. "
#             f"Base your advice on her stated goal: {memory['user_profile']['stated_goal']}. "
#             "IMPORTANT:\n"
#             "1. Always check tools for current balances and upcoming bills before giving advice.\n"
#             "2. Remember previous commitments (e.g., savings plans) from memory.\n"
#             "3. Connect new requests to existing goals.\n"
#             f"Known facts from previous sessions:\n{facts_str}"
#         ),
#         tools=list(TOOLS.values()),
#     )

#     # Convert stored history back to Content objects
#     # Gemini roles must be 'user' or 'model'
#     history = []
#     for msg in memory.get("conversation_history", []):
#         role = "model" if msg["role"] == "assistant" else msg["role"]
#         history.append(types.Content(role=role, parts=[types.Part(**p) for p in msg["parts"]]))

#     # Create a chat session
#     chat = client.chats.create(model=MODEL, config=config, history=history)

#     # Send the message
#     response = chat.send_message(user_input)
    
#     # The new SDK handles the tool loop naturally if configured, 
#     # but we'll stick to a manual loop for full control as requested by the assignment
#     while True:
#         # Check if the last response has a function call
#         tool_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
        
#         if not tool_calls:
#             break
            
#         responses = []
#         for call in tool_calls:
#             fn_name = call.name
#             args = call.args
#             print(f">>> TOOL CALL: {fn_name}({args})")
#             result = TOOLS[fn_name](**args)
#             print(f"<<< TOOL RESULT: {result}")
            
#             responses.append(types.Part(
#                 function_response=types.FunctionResponse(
#                     name=fn_name,
#                     response={"content": json.dumps(result)}
#                 )
#             ))
        
#         # Send tool results back
#         response = chat.send_message(responses)

#     # Extract the final response text
#     final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text])

#     # Update history in memory
#     serializable_history = []
#     for content in chat.history:
#         parts = []
#         for part in content.parts:
#             p_dict = {}
#             if part.text: p_dict["text"] = part.text
#             if part.function_call:
#                 p_dict["function_call"] = {
#                     "name": part.function_call.name,
#                     "args": part.function_call.args
#                 }
#             if part.function_response:
#                 p_dict["function_response"] = {
#                     "name": part.function_response.name,
#                     "response": part.function_response.response
#                 }
#             parts.append(p_dict)
#         serializable_history.append({"role": content.role, "parts": parts})

#     memory["conversation_history"] = serializable_history
#     save_memory(memory)
#     return final_text

# if __name__ == "__main__":
#     print(f"--- Session {CURRENT_SESSION} ---")
#     while True:
#         try:
#             user_input = input("User: ")
#             if user_input.lower() in ["exit", "quit"]: break
#             if not user_input.strip(): continue
            
#             response = run_agent(user_input)
#             print(f"Agent: {response}")
#         except KeyboardInterrupt:
#             break

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

def run_agent(user_input):
    if not user_input.strip():
        return "Please say something!"

    memory = load_memory()
    today = "2025-11-03" if CURRENT_SESSION == 1 else "2025-11-06"
    
    facts_str = "\n".join(memory.get("learned_facts", []))
    
    # In the new SDK, passing a list of Python functions directly to 'tools' works automatically.
    # To maintain manual control, we must disable automatic_function_calling.
    config = types.GenerateContentConfig(
        system_instruction=(
            f"You are a helpful finance companion for Priya Sharma. Today is {today}. "
            f"Base your advice on her stated goal: {memory['user_profile']['stated_goal']}. "
            "IMPORTANT:\n"
            "1. Always check tools for current balances and upcoming bills before giving advice.\n"
            "2. Remember previous commitments (e.g., savings plans) from memory.\n"
            "3. Connect new requests to existing goals.\n"
            f"Known facts from previous sessions:\n{facts_str}"
        ),
        tools=list(TOOLS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    # Convert stored history back to Content objects safely
    history = []
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
            
            # Execute the actual tool
            result = TOOLS[fn_name](**args)
            print(f"<<< TOOL RESULT: {result}")
            
            # Construct function response. Gemini 3+ models require 'id' to map responses correctly.
            func_resp_kwargs = {
                "name": fn_name,
                "response": {"result": result}
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