# file: agent1_coordinator/nodes.py
import os
import json
import requests
from uuid import uuid4
from openai import OpenAI

from pocketflow import Node
# 从 common 导入我们创建的通用客户端函数
from common.ai_client import call_gitee_ai
# call_agent2 仍然需要，可以放在这里或移到 common 模块
from .utils import call_agent2 # 假设 call_agent2 在 utils.py
# 这行代码会自动查找并加载项目根目录下的 .env 文件


# ======================================================================
# 工具函数定义区
# ======================================================================

AGENT2_URL = "http://localhost:8001/"

def call_agent2(skill_id: str, context: dict):
    """通过 A2A 协议调用 Agent 2。"""
    payload = {
        "jsonrpc": "2.0", "method": "tasks/send",
        "params": {
            "id": str(uuid4()),
            "message": {"role": "user", "parts": [{"type": "data", "data": context}]},
            "metadata": {"skillId": skill_id}
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
        print(f"[Agent 1] 调用 Agent 2 失败: {e}")
    return None

# ======================================================================
# Node 类定义区
# ======================================================================

class Initialize(Node):
    def prep(self, shared):
        return shared['question']
        
    def exec(self, user_query):
        # 构造专门用于信息提取的 Prompt
        prompt = f"""
        你是一个信息提取助手。请从以下用户请求中提取"时间"和"预算"。
        预算应该是一个整数。请严格按照以下 JSON 格式返回，不要有任何额外解释。
        格式: {{"time": "提取的时间", "budget": 提取的预算整数}}
        用户请求: "{user_query}"
        """
        # 调用通用函数，并指定要使用的模型
        return call_gitee_ai(prompt, model_name="Qwen2-7B-Instruct")

    def post(self, shared, prep_res, exec_res):
        if exec_res and isinstance(exec_res, dict):
            shared["time"] = exec_res.get("time", "今晚")
            budget = exec_res.get("budget")
            
            # 处理预算为 None 的情况
            if budget is None:
                shared["user_budget"] = 10000  # 设置默认预算
                print(f"[Agent 1] Gitee AI 解析完成. 时间: {shared['time']}, 用户预算: 未指定(使用默认: {shared['user_budget']})")
            else:
                shared["user_budget"] = budget
                print(f"[Agent 1] Gitee AI 解析完成. 时间: {shared['time']}, 用户预算: {shared['user_budget']}")
        else:
            print("[Agent 1] Gitee AI 解析失败，使用默认值。")
            shared["time"] = "今晚"
            shared["user_budget"] = 10000  # 默认预算
        
        shared["current_max_price"] = 10000
        return "find_restaurant"

class CallFindRestaurants(Node):
    def prep(self, shared): 
        return {"max_price": shared['current_max_price'], "time": shared['time']}
    
    def exec(self, inputs):
        print(f"[Agent 1] 正在调用 Agent 2 查找餐厅, 最高预算: {inputs['max_price']}")
        return call_agent2("find_restaurants", {"max_price": inputs['max_price'], "time": inputs['time']})
    
    def post(self, shared, prep_res, exec_res):
        print(f"[Agent 1] Agent 2 返回的完整结果: {exec_res}")  # 调试日志
        
        # 检查 exec_res 是否包含 proposal
        if exec_res and "proposal" in exec_res:
            proposal = exec_res["proposal"]
            
            # 检查 proposal 是否有效
            if proposal and isinstance(proposal, dict):
                shared["proposal"] = proposal
                shared["proposal_price"] = proposal.get("price", 0)
                
                restaurant_name = proposal.get("name", "未知餐厅")
                print(f"[Agent 1] Agent 2 提议: {restaurant_name} (价格: {proposal.get('price', 0)})")
                return "evaluate_proposal"
            else:
                print(f"[Agent 1] Proposal 格式无效: {proposal}")
        else:
            print(f"[Agent 1] 响应中缺少 proposal 字段: {exec_res}")
        
        # 查找失败的情况
        shared["final_result"] = "未能找到合适的餐厅。"
        return "end"
    
class EvaluateProposal(Node):
    def prep(self, shared):
        # 准备比较所需的数据
        return {
            "proposal_price": shared.get("proposal_price", 0),
            "user_budget": shared.get("user_budget")
        }
    
    def exec(self, inputs):
        # 执行预算比较逻辑
        proposal_price = inputs["proposal_price"]
        user_budget = inputs["user_budget"]
        
        # 处理预算比较
        if user_budget is None:
            return {"accepted": True, "reason": "无预算限制"}
        elif proposal_price > user_budget:
            return {"accepted": False, "reason": "超出预算"}
        else:
            return {"accepted": True, "reason": "在预算内"}
    
    def post(self, shared, prep_res, exec_res):
        if exec_res["accepted"]:
            print(f"[Agent 1] 预算合适，确认方案。原因: {exec_res['reason']}")
            return "confirm_booking"
        else:
            print(f"[Agent 1] 提议超出预算，需要调整。原因: {exec_res['reason']}")
            shared["current_max_price"] = shared["user_budget"]
            return "adjust_and_retry"

class CallBookRestaurant(Node):
    def prep(self, shared):
        # 安全地获取提案
        proposal = shared.get("proposal", {})
        return {
            "restaurant_id": proposal.get("id", "unknown"),
            "restaurant_name": proposal.get("name", "未知餐厅"),  # 确保传递名称
            "time": shared.get("time", "")
        }
    
    def exec(self, inputs):
        print(f"[Agent 1] 正在调用 Agent 2 预定餐厅: {inputs['restaurant_name']}")
        return call_agent2("book_restaurant", {
            "restaurant_id": inputs['restaurant_id'],
            "restaurant_name": inputs['restaurant_name'],  # 传递名称
            "time": inputs['time']
        })
    
    def post(self, shared, prep_res, exec_res):
        print(f"[Agent 1] 预定结果处理: {exec_res}")
        if exec_res and exec_res.get("status") == "success":
            shared["final_result"] = exec_res["info"]
            print(f"[Agent 1] 预定成功: {exec_res['info']}")
        else:
            shared["final_result"] = "预定失败。"
            print("[Agent 1] 预定失败")
        return "end"