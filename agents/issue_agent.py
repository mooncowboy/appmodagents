import os
from dotenv import load_dotenv
import asyncio
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread




async def main():
    load_dotenv()

    settings = AzureAIAgentSettings(
        endpoint=os.getenv("PROJECT_ENDPOINT")
    )

    kernel = Kernel()

    issue_agent_id = os.getenv("AM_ISSUE_AGENT_ID")

    async with(
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        ) as creds,
        AzureAIAgent.create_client(credential=creds, endpoint=settings.endpoint) as client,
    ):
        # 1) Load existing agent definition from Agent Service
        definition = await client.agents.get_agent(agent_id=issue_agent_id)
        # 2) Create SK AzureAIAgent and attach plugins (tools)
        agent = AzureAIAgent(
            client=client,
            definition=definition,
            kernel=kernel,
            plugins=[],
        )
        # 3) Talk to the hosted agent; it can now call your SK tools
        thread = AzureAIAgentThread(client=client)  # keeps conversation state server-side

        # Loop until user types 'quit'
        while True:
            user_prompt = input("Enter a prompt or type 'quit': ")
            if user_prompt.lower() == 'quit':
                break
            if len(user_prompt) == 0:
                print ("Please enter a prompt")
                continue

            # from https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-types/azure-ai-agent?pivots=programming-language-python
            response = await agent.get_response(messages=[user_prompt], thread=thread)
            print(response)
            thread = response.thread

if __name__ == "__main__":
    asyncio.run(main())