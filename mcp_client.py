from mcpclient import connect
import asyncio

async def run_mcp_tool(tool_name, **kwargs):
    async with connect("localhost", 8080) as client:
        return await client.call_tool(tool_name, kwargs)
