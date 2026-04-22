import argparse
import logging

from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.client_factory import ClientFactory
from a2a.types.a2a_pb2 import (
    GetExtendedAgentCardRequest,
    Message,
    Part,
    Role,
    SendMessageRequest,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


async def main(base_url: str, user_message: str) -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        try:
            logger.info(
                '\nAttempting to fetch public agent card from: %s%s',
                base_url,
                AGENT_CARD_WELL_KNOWN_PATH,
            )
            _public_card = (
                await resolver.get_agent_card()
            )  # Fetches from default public path
            logger.info('\nSuccessfully fetched public agent card:')
            logger.info(_public_card)

        except Exception as e:
            logger.exception('\nCritical error fetching public agent card.')
            raise RuntimeError(
                '\nFailed to fetch the public agent card. Cannot continue.'
            ) from e

        client_factory = ClientFactory(config=ClientConfig(streaming=True))
        client = client_factory.create(_public_card)
        parts = [Part(text=user_message)]
        message = Message(
            role=Role.ROLE_USER,
            parts=parts,
            message_id=uuid4().hex,
        )
        request = SendMessageRequest(message=message)

        response = client.send_message(request)

        async for chunk in response:
            print('Response:')
            task, _ = chunk
            print(f"Task is {task}")

        await client.close()

if __name__ == '__main__':
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        help='Base URL of the A2A agent server.',
    )
    parser.add_argument(
        '--message',
        required=True,
        help='User message to send to the agent.',
    )
    args = parser.parse_args()

    asyncio.run(main(base_url=args.url, user_message=args.message))

