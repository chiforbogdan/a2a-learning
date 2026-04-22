Structure:

agent restaurant: langchain -> tool [get restaurants in a certain location]
agent doctors: langchain -> MCP tool [get doctors in a specific location]
agent orchestration: integrate restaurant and doctors agent

How to test:

1. Test each individual agent: uv run doctors_agent_test.py, uv run restaurants_agent_test.py
2. Each A2A server: uv run client_a2a.py --url http://localhost:9999 --message "Recommend me a good restaurant in Rome", uv run client_a2a.py --url http://localhost:9998 --message "Recommend me a good doctor in Rome"
