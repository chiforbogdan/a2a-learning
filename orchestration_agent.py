import asyncio
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.client_factory import ClientFactory
from a2a.types.a2a_pb2 import Message, Part, Role, SendMessageRequest
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


class A2AQuery(BaseModel):
    query: str = Field(..., description="Full natural-language request to forward to the specialist agent, including any location.")

DOCTORS_URL = "http://localhost:9998"
RESTAURANTS_URL = "http://localhost:9999"

SYSTEM_PROMPT = (
    "You are an orchestrator agent which can send queries to specialized agents."
    "When being asked information regarding a specific location query the available tools with the indicated location"
)


async def _call_a2a(base_url: str, query: str) -> str:
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        card = await resolver.get_agent_card()
        client = ClientFactory(config=ClientConfig(streaming=True)).create(card)
        request = SendMessageRequest(
            message=Message(
                role=Role.ROLE_USER,
                parts=[Part(text=query)],
                message_id=uuid4().hex,
            )
        )
        chunks: list[str] = []
        async for _stream_response, task in client.send_message(request):
            for artifact in getattr(task, "artifacts", []) or []:
                for part in artifact.parts:
                    if part.text:
                        chunks.append(part.text)
        await client.close()
        resp = "\n".join(chunks)
        print(f"Response from {base_url} is {resp!r}")
        return resp

def _describe_card(card) -> str:
    lines = [f"{card.name}: {card.description}"]
    for skill in card.skills:
        lines.append(f"- Skill '{skill.name}': {skill.description}")
        if skill.examples:
            lines.append(f"  Examples: {'; '.join(skill.examples)}")
    return "\n".join(lines)


async def build_a2a_tool(base_url: str) -> StructuredTool:
    async with httpx.AsyncClient() as httpx_client:
        card = await A2ACardResolver(httpx_client=httpx_client, base_url=base_url).get_agent_card()

    async def _run(query: str) -> str:
        return await _call_a2a(base_url, query)

    description = _describe_card(card)
    print(f"Tool:\n{description}\n")

    return StructuredTool.from_function(
        coroutine=_run,
        name=card.name.lower().replace(" ", "_"),
        description=description,
        args_schema=A2AQuery,
    )

async def main():
    restaurants_tool, doctors_tool = await asyncio.gather(
        build_a2a_tool(RESTAURANTS_URL),
        build_a2a_tool(DOCTORS_URL),
    )

    llm = ChatOpenAI(
        model="Qwen/Qwen3.5-122B-A10B-FP8",
        openai_api_base="http://localhost:8881/v1",
        openai_api_key="EMPTY",
        temperature=0,
    )
    agent = create_react_agent(llm, [restaurants_tool, doctors_tool], prompt=SYSTEM_PROMPT)
    result = await agent.ainvoke({
        "messages": [(
            "user",
            "Get me a good restaurant in Rome and a doctor in case I get sick afterwards",
        )],
    })
    for m in result["messages"]:
        m.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
