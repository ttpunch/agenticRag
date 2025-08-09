import asyncio
from mcp_client import run_mcp_tool

def db_agent(state):
    query = state.get("query", "SELECT NOW();")
    result = asyncio.run(run_mcp_tool("run_query", query=query))
    return {"db_result": result}
