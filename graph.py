from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from agents.supervisor import supervisor_agent
from agents.auth_agent import auth_agent
from agents.rag_agent import rag_agent
from agents.db_agent import db_agent

# Define the state with proper typing
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str = None
    authorized: bool = False

def build_graph():
    # Initialize the graph with the state schema
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("auth", auth_agent)
    workflow.add_node("rag", rag_agent)
    workflow.add_node("db", db_agent)
    
    # Define the flow
    workflow.add_edge("supervisor", "auth")
    
    # Conditional routing after auth
    def route_after_auth(state: AgentState) -> str:
        if state.get("task") == "rag" and state.get("authorized"):
            return "rag"
        elif state.get("task") == "db" and state.get("authorized"):
            return "db"
        return END  # End if not authorized or no matching task
    
    workflow.add_conditional_edges(
        "auth",
        route_after_auth,
        {
            "rag": "rag",
            "db": "db",
            END: END
        }
    )
    
    # Terminal nodes
    workflow.add_edge("rag", END)
    workflow.add_edge("db", END)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Compile the graph
    return workflow.compile()

# For backward compatibility
graph = build_graph()