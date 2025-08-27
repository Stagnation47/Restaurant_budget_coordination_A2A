# file: agent1_coordinator/flow.py
from pocketflow import Flow
from .nodes import *

def create_coordination_flow():
    # 1. Instantiate the nodes
    initialize = Initialize()
    find = CallFindRestaurants()
    evaluate = EvaluateProposal()
    book = CallBookRestaurant()
    
    # 2. Connect the nodes using the operator syntax `>>`
    initialize - "find_restaurant" >> find
    
    find - "evaluate_proposal" >> evaluate
    # When find returns "end", the flow stops automatically
    
    evaluate - "adjust_and_retry" >> find # <-- This creates the negotiation loop
    evaluate - "confirm_booking" >> book
    
    # When book returns "end", the flow stops automatically
    
    # 3. Create and return the Flow, specifying the starting node
    return Flow(start=initialize)