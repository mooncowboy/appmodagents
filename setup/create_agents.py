import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

from utils.utils import *

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
        # Create IssueAgent 
        print("Creating AM_Issue agent")
        issue_agent = agent_client.create_agent(
                model=model_deployment,
                name="AM_Issue",
                instructions=get_instructions("issue_agent"),
            )

if __name__ == '__main__': 
    main()