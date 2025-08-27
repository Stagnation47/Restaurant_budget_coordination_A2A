# file: agent2/nodes.py
from pocketflow import Node

# 模拟餐厅数据库
RESTAURANT_DB = {
    "r001": {"name": "豪华牛排馆", "price": 800},
    "r002": {"name": "温馨意大利餐厅", "price": 400},
    "r003": {"name": "实惠家常菜馆", "price": 100},
 
}

class FindRestaurants(Node):
    """根据预算查找餐厅的节点"""
    
    def prep(self, shared):
        # 准备查找参数
        return {
            "max_price": shared.get("max_price", 10000),
            "time": shared.get("time", "")
        }
    
    def exec(self, inputs):
        # 执行查找逻辑
        max_price = inputs["max_price"]
        time = inputs["time"]

        print(f"[Agent 2] 收到查找请求：时间 {time}, 最高预算 {max_price}")
        
        options = []
        for r_id, info in RESTAURANT_DB.items():
            if info["price"] <= max_price:
                options.append({"id": r_id, **info})
        
        # 优先返回最贵的
        if options:
            best_option = max(options, key=lambda x: x['price'])
            print(f"[Agent 2] 已找到方案: {best_option['name']}")
            return {
                "proposal": best_option,
                "status": "success"
            }
        else:
            print(f"[Agent 2] 未找到符合预算的餐厅")
            return {
                "proposal": None,
                "status": "failed"
            }
    
    def post(self, shared, prep_res, exec_res):
        # 存储结果到共享上下文
        if exec_res and exec_res.get("status") == "success":
            shared["proposal"] = exec_res["proposal"]
        else:
            shared["proposal"] = None
        return "done"


class BookRestaurant(Node):
    """执行预定的节点"""
    
    def prep(self, shared):
        # 准备预定参数
        return {
            "restaurant_id": shared.get("restaurant_id"),
            "time": shared.get("time", "")
        }
    
    def exec(self, inputs):
        # 执行预定逻辑
        restaurant_id = inputs["restaurant_id"]
        time = inputs["time"]
        
        if restaurant_id in RESTAURANT_DB:
            restaurant_name = RESTAURANT_DB[restaurant_id]["name"]
            print(f"[Agent 2] 正在为 {time} 预定 {restaurant_name}...")
            
            # 模拟预定成功
            return {
                "status": "success",
                "info": f"成功预定 {restaurant_name}，时间：{time}。预定编号: RES-{restaurant_id}-2024"
            }
        else:
            print(f"[Agent 2] 预定失败！餐厅ID {restaurant_id} 不存在")
            return {
                "status": "failed",
                "info": f"餐厅ID {restaurant_id} 不存在"
            }
    
    def post(self, shared, prep_res, exec_res):
        # 存储预定结果
        if exec_res and exec_res.get("status") == "success":
            shared["booking_status"] = "success"
            shared["booking_info"] = exec_res["info"]
            print(f"[Agent 2] 预定成功！")
        else:
            shared["booking_status"] = "failed"
            shared["booking_info"] = exec_res.get("info", "预定失败") if exec_res else "预定失败"
            print(f"[Agent 2] 预定失败！")
            
        return "done"