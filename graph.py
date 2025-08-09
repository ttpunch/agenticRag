# graph.py
from langgraph.graph import Graph
from agents.supervisor import supervisor_agent
from agents.auth_agent import auth_agent
from agents.rag_agent import rag_agent
from agents.db_agent import db_agent

def build_graph():
    graph = Graph()
    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("auth", auth_agent)
    graph.add_node("rag", rag_agent)
    graph.add_node("db", db_agent)

    # supervisor decides task (as before) and then we route:
    graph.add_edge("supervisor", "auth")  # first check auth
    graph.add_edge("auth", "rag", condition=lambda s: s.get("task") == "rag" and s.get("authorized"))
    graph.add_edge("auth", "db", condition=lambda s: s.get("task") == "db" and s.get("authorized"))

    graph.set_entry_point("supervisor")
    return graph
