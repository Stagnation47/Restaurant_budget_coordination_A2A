# file: agent2_booking/utils.py

# 模拟餐厅数据库
RESTAURANT_DB = {
    "r001": {"name": "豪华牛排馆", "price": 800},
    "r002": {"name": "温馨意大利餐厅", "price": 400},
    "r003": {"name": "实惠家常菜馆", "price": 100},
}

def find_restaurants_from_db(max_price: int):
    """根据预算查找餐厅"""
    options = []
    for r_id, info in RESTAURANT_DB.items():
        if info["price"] <= max_price:
            options.append({"id": r_id, **info})
    
    # 为了模拟流程图，优先返回最贵的选项
    if options:
        return max(options, key=lambda x: x['price'])
    return None

def book_restaurant_in_db(restaurant_id: str, time: str):
    """根据ID和时间预定餐厅"""
    if restaurant_id in RESTAURANT_DB:
        name = RESTAURANT_DB[restaurant_id]["name"]
        return {"status": "success", "info": f"成功预定 {name}，时间：{time}"}
    return {"status": "failed", "info": f"餐厅ID {restaurant_id} 不存在"}