# file: agent1_coordinator/task_manager.py
from typing import Union, AsyncIterable
from common.server.task_manager import InMemoryTaskManager
from common.types import *
import common.server.utils as server_utils
from .flow import create_coordination_flow

class CoordinatorTaskManager(InMemoryTaskManager):
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        await self.update_store(request.params.id, TaskStatus(state=TaskState.WORKING), [])
        
        user_query = ""
        # --- START: MODIFIED CODE TO FIX AttributeError ---
        if request.params.message and request.params.message.parts:
            # 兼容处理 part 可能是对象或字典两种情况
            for part in request.params.message.parts:
                part_text = None
                if isinstance(part, TextPart):
                    # 如果是 TextPart 对象，直接访问 .text
                    part_text = part.text
                elif isinstance(part, dict) and part.get("type") == "text":
                    # 如果是字典，使用 .get('text')
                    part_text = part.get("text")

                if part_text:
                    user_query = part_text
                    break
        # --- END: MODIFIED CODE ---
        
        shared = {"question": user_query}
        flow = create_coordination_flow()
        flow.run(shared) # 运行 PocketFlow 逻辑
        
        final_answer = shared.get("final_result", "处理过程中发生错误。")

        final_status = TaskStatus(state=TaskState.COMPLETED)
        artifact = Artifact(parts=[TextPart(text=final_answer)])
        final_task = await self.update_store(request.params.id, final_status, [artifact])
        
        return SendTaskResponse(id=request.id, result=final_task)

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        """
        处理流式请求。此代理不支持流式传输，因此按 A2A 规范返回错误。
        """
        print(f"[Agent 1] 收到流式请求但不支持。")
        return JSONRPCResponse(
            id=request.id,
            error=UnsupportedOperationError(message="此代理不支持流式传输。")
        )