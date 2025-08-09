from graph import build_graph

if __name__ == "__main__":
    graph = build_graph()

    # Example 1: RAG query
    result = graph.invoke({"query": "What does the CNC spindle load data say?"})
    print(result)

    # Example 2: DB query
    result = graph.invoke({"query": "SELECT COUNT(*) FROM cnc_data;"})
    print(result)
