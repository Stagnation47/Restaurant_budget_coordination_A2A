# file: agent2_booking/task_manager.py
from typing import Union, AsyncIterable
from common.server.task_manager import InMemoryTaskManager
from common.types import *
import common.server.utils as server_utils
from common.ai_client import call_gitee_ai

class BookingAgentTaskManager(InMemoryTaskManager):
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        await self.update_store(request.params.id, TaskStatus(state=TaskState.WORKING), [])

        # 获取 skillId
        skill_id = ""
        if request.params.metadata and "skillId" in request.params.metadata:
            skill_id = request.params.metadata["skillId"]
        else:
            skill_id = getattr(request.params, 'skillId', '')
        
        input_data = {}
        if request.params.message and request.params.message.parts:
            for part in request.params.message.parts:
                if isinstance(part, DataPart):
                    input_data = part.data
                    break
        
        result_data = {}

        if skill_id == "find_restaurants":
            max_price = input_data.get("max_price", 10000)
            time = input_data.get("time", "")
            
            # 构造专门用于餐厅推荐的 Prompt
            prompt = f"请推荐一个价格不超过 {max_price} 元的餐厅，用餐时间：{time}。请严格以包含 id, name, price 的 JSON 格式返回。"
            
            # 调用AI推荐餐厅
            proposal = call_gitee_ai(prompt, model_name="Qwen2.5-14B-Instruct")
            
            result_data = {"proposal": proposal}
            
        elif skill_id == "book_restaurant":
            r_id = input_data.get("restaurant_id")
            time = input_data.get("time")
            restaurant_name = input_data.get("restaurant_name", "未知餐厅")  # 新增：获取餐厅名称
            
            # 实现预定逻辑 - 不再检查数据库
            result_data = self._book_restaurant(r_id, restaurant_name, time)
            
        else:
            return SendTaskResponse(id=request.id, error=InvalidParamsError(message="Unknown or missing skillId in metadata"))

        final_status = TaskStatus(state=TaskState.COMPLETED)
        artifact = Artifact(parts=[DataPart(data=result_data)])
        final_task = await self.update_store(request.params.id, final_status, [artifact])

        return SendTaskResponse(id=request.id, result=final_task)

    def _book_restaurant(self, restaurant_id: str, restaurant_name: str, time: str) -> dict:
        """预定餐厅的实现 - 直接接受LLM推荐的餐厅"""
        print(f"[Agent 2 TaskManager] 正在为 {time} 预定 {restaurant_name} (ID: {restaurant_id})...")
        
        # 直接预定成功，不再检查数据库
        return {
            "status": "success",
            "info": f"成功预定 {restaurant_name}，时间：{time}。预定编号: RES-{restaurant_id}-2024"
        }

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        print(f"[Agent 2] Streaming request received but not supported.")
        return JSONRPCResponse(
            id=request.id,
            error=UnsupportedOperationError(message="Streaming is not supported by this agent.")
        )