# file: agent1_coordinator/a2a_server.py
from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill
from .task_manager import CoordinatorTaskManager

def main():
    agent_card = AgentCard(
        name="Coordinator Agent (Agent 1)",
        description="Coordinates restaurant booking and budget negotiation",
        url="http://0.0.0.0:8000", # <-- ADD THIS LINE
        version="1.0.0",           # <-- ADD THIS LINE
        skills=[AgentSkill(id="handle_reservation", name="Handle Reservation")],
        capabilities=AgentCapabilities(streaming=False)
    )
    server = A2AServer(
        agent_card=agent_card,
        task_manager=CoordinatorTaskManager(),
        host="0.0.0.0",
        port=8000 # Agent 1 uses port 8000
    )
    print("Agent 1 (Coordinator) is running on http://0.0.0.0:8000")
    server.start()

if __name__ == "__main__":
    main()