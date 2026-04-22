import asyncio
from restaurants_agent import RestaurantsAgent

async def main():
    agent = RestaurantsAgent()
    resp = await agent.invoke("Recommend me a good restaurant in Rome")
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())

