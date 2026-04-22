import asyncio
from doctors_agent import DoctorsAgent

async def main():
    agent = DoctorsAgent()
    resp = await agent.invoke("Find me a doctor in Rome")
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())
