# file: a2a_client.py
import requests
import json
from uuid import uuid4

AGENT1_URL = "http://localhost:8000/"

def main():
    user_request = "预定明晚8点上海的餐厅,预算500元"
    print(f"--- 客户端发起请求: '{user_request}' ---")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "id": str(uuid4()),
            "skillId": "handle_reservation",
            "message": {"role": "user", "parts": [{"type": "text", "text": user_request}]}
        },
        "id": str(uuid4())
    }
    
    response = requests.post(AGENT1_URL, json=payload).json()
    
    if "result" in response:
        final_result = response["result"]["artifacts"][0]["parts"][0]["text"]
        print("\n--- 客户端收到最终结果 ---")
        print(final_result)
    else:
        print("\n--- 请求失败 ---")
        print(response.get("error"))

if __name__ == "__main__":
    main()