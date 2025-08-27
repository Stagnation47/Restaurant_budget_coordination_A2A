# file: agent2_booking/a2a_server.py
from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill
# Ensure the relative import for the task manager is correct
from .task_manager import BookingAgentTaskManager

def main():
    agent_card = AgentCard(
        name="Booking Expert Agent (Agent 2)",
        description="Provides restaurant finding and booking services",
        url="http://0.0.0.0:8001",
        version="1.0.0",
        skills=[
            AgentSkill(id="find_restaurants", name="Find Restaurants"),
            AgentSkill(id="book_restaurant", name="Book a Restaurant")
        ],
        capabilities=AgentCapabilities(streaming=False)
    )
    server = A2AServer(
        agent_card=agent_card,
        task_manager=BookingAgentTaskManager(),
        host="0.0.0.0",
        port=8001
    )
    print("Agent 2 (Booking Expert) is running on http://0.0.0.0:8001")
    server.start()

# --- THIS IS THE CRITICAL PART ---
# Ensure this block exists at the end of the file and is not indented.
if __name__ == "__main__":
    main()