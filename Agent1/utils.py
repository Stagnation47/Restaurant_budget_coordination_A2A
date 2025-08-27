# file: agent1_coordinator/utils.py
import os
import requests
import json
from uuid import uuid4
from openai import OpenAI
from dotenv import load_dotenv

# Load variables from the .env file in the project root
load_dotenv()

# --- Utility function to call Agent 2 ---
AGENT2_URL = "http://localhost:8001/"

def call_agent2(skill_id: str, context: dict):
    """
    A simple A2A client to call Agent 2, using DataPart for data exchange.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "id": str(uuid4()),
            "skillId": skill_id,
            "message": {
                "role": "user",
                "parts": [{"type": "data", "data": context}]
            }
        },
        "id": str(uuid4())
    }
    try:
        response = requests.post(AGENT2_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if "result" in result and result["result"]["artifacts"]:
            for part in result["result"]["artifacts"][0]["parts"]:
                if part.get("type") == "data":
                    return part.get("data")
                    
    except requests.RequestException as e:
        print(f"[Agent 1] Failed to call Agent 2: {e}")
    return None

# --- Utility function to call Gitee AI ---
def call_gitee_ai_to_extract_info(user_query: str):
    """
    Calls Gitee AI to extract time and budget from a user's query.
    """
    api_key = os.getenv("GITEE_AI_API_KEY")
    if not api_key:
        print("[Agent 1] ERROR: GITEE_AI_API_KEY not found in .env file or environment variables!")
        return None

    # Initialize the client according to the Gitee AI guide
    client = OpenAI(
        base_url="https://ai.gitee.com/v1",
        api_key=api_key,
    )
    
    # A powerful prompt instructing the model to return JSON
    prompt = f"""
    You are an information extraction assistant. From the user's request below, extract the "time" and "budget".
    The budget should be an integer.
    Respond strictly in the following JSON format without any extra explanations or markdown code blocks.

    Example format:
    {{"time": "extracted time", "budget": extracted budget as an integer}}

    If a piece of information is missing, set its value to null.

    User Request:
    "{user_query}"
    """
    
    try:
        print("[Agent 1] Calling Gitee AI to parse user intent...")
        response = client.chat.completions.create(
            model="DeepSeek-V3",  # Model specified in the guide
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts information into JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        response_content = response.choices[0].message.content
        print(f"[Agent 1] Gitee AI response content: {response_content}")
        return json.loads(response_content)

    except Exception as e:
        print(f"[Agent 1] An error occurred while calling Gitee AI: {e}")
        return None