from langgraph.graph import StateGraph, END
from src.models.state import GraphState
import logging

logger = logging.getLogger(__name__)

# --- Node Placeholders (Logic to be added in Phase 2) ---

async def classifier_node(state: GraphState):
    """
    Analyzes user intent using Gemini Pro.
    Currently a stub that passes through to Router.
    """
    logger.info("--- CLASSIFIER NODE ---")
    # TODO: Implement Gemini Pro Classification
    return {"next_step": "router"}

async def router_node(state: GraphState):
    """
    Routes to specific agents based on classifier output.
    Currently stubbed to end conversation.
    """
    logger.info("--- ROUTER NODE ---")
    # TODO: Implement Routing Logic
    return {"next_step": "end"}

async def agent_node_stub(state: GraphState):
    """Placeholder for future parallel agents"""
    pass

# --- Edge Logic ---

def route_decision(state: GraphState):
    """Determines where to go next based on state.next_step"""
    return state["next_step"]

# --- Graph Construction ---

def create_workflow():
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("router", router_node)

    # Set Entry Point
    workflow.set_entry_point("classifier")

    # Add Edges
    workflow.add_conditional_edges(
        "classifier",
        route_decision,
        {
            "router": "router",
            "end": END
        }
    )

    workflow.add_edge("router", END) # Stubbed to end immediately

    return workflow.compile()

app_workflow = create_workflow()
