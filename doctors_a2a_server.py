import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
from agent_executor import (
    CustomAgentExecutor,
)
from doctors_agent import DoctorsAgent

if __name__ == '__main__':
    skill = AgentSkill(
        id='doctors_agent',
        name='Doctors agent',
        description='Returns a list of doctors from a specific location',
        tags=['doctors'],
    )

    public_agent_card = AgentCard(
        name='Doctors Agent',
        description='Doctors recommendation in a specific location. When someone is asking for a doctor in a specific location this agent can suggest an answer',
        icon_url='http://localhost:9998/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(
            streaming=True,
        ),
        supported_interfaces=[
            AgentInterface(
                protocol_binding='JSONRPC',
                url='http://localhost:9998',
            )
        ],
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor = CustomAgentExecutor(DoctorsAgent()),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host='127.0.0.1', port=9998)
