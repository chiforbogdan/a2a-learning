from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import asyncio

@tool
def get_restaurants(location: str) -> str:
    """This tool can get the restaurants in a certain location"""
    print(f"Restaurant tool location is {location}")
    if location != "Rome":
        return "The only supported location is Rome"

    return "Jack&Joe"


class RestaurantsAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="Qwen/Qwen3.5-122B-A10B-FP8",
            openai_api_base="http://localhost:8881/v1",
            openai_api_key="EMPTY",
            temperature=0,
        ).bind_tools([get_restaurants])

    async def invoke(self, prompt: str) -> str:
        print(f"I got invoked with prompt {prompt}")
        messages = [HumanMessage(prompt)]
        ai_msg = self.llm.invoke(messages)
        messages.append(ai_msg)
        for call in ai_msg.tool_calls:
            result = get_restaurants.invoke(call["args"])
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": str(result)})

        resp = self.llm.invoke(messages).content
        print(f"My response is {resp}")
        return resp
