import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

def main():
    load_dotenv()
    project_endpoint= os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # Connect to the Agent client
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        )
    )
    with agent_client:
        ISSUE_AGENT_ID = os.getenv("AM_ISSUE_AGENT_ID")
        # Get list of agents in AI Agent Service
        agents = agent_client.list_agents()
        for agent in agents:
            if agent.id == ISSUE_AGENT_ID:
                print(f"Found agent: {agent.name} (ID: {agent.id})")
                agent_client.delete_agent(agent_id=agent.id)

if __name__ == '__main__': 
    main()