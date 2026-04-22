import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

MCP_SERVERS = {
    "doctors": {
        "command": "python",
        "args": ["mcp_doctors.py"],
        "transport": "stdio",
    },
}

class DoctorsAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="Qwen/Qwen3.5-122B-A10B-FP8",
            openai_api_base="http://localhost:8881/v1",
            openai_api_key="EMPTY",
            temperature=0,
        )
        self.mcp_client = MultiServerMCPClient(MCP_SERVERS)

    async def invoke(self, prompt: str) -> str:
        print(f"I got invoked with prompt {prompt}")
        tools = await self.mcp_client.get_tools()
        agent = create_react_agent(self.llm, tools)
        result = await agent.ainvoke({"messages": [("user", prompt)]})
        resp = result["messages"][-1].content
        print(f"My response is {resp}")

        return resp
