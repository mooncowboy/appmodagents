import requests
from dotenv import load_dotenv
import os

load_dotenv()

github_graph_url = 'https://api.github.com/graphql'

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 


def create_issue(repo_url: str, title: str, body: str) -> str:
    """Create a new issue in the specified GitHub repository.
        See https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/assign-copilot-to-an-issue for API usage.

    Args:
        repo_url (str): The URL of the repository.
        title (str): The title of the issue.
        body (str): The body content of the issue.

    Returns:
        str: The URL of the created issue.
    """

    # Extract the repository owner and name from the URL
    repo_parts = repo_url.split("/")
    if len(repo_parts) < 5:
        raise ValueError("Invalid repository URL")

    owner = repo_parts[3]
    name = repo_parts[4]
    print(f"Using repository {owner}/{name}")

    # Check if repo has coding agent enabled
    coding_agent_id = get_coding_agent_id(owner, name)
    if not coding_agent_id:
        raise ValueError("Error: Repository does not have a coding agent enabled.")
    print(f"Using coding_agent_id {coding_agent_id}")

    # Get the global repo ID
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
        }
    }
    """
    variables = {"owner": owner, "name": name}
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(github_graph_url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()
    print(data)
    repo_id = data.get("data", {}).get("repository", {}).get("id", "")
    if response.status_code != 200:
            raise RuntimeError(f"GitHub API error: {response.status_code} {response.text}")


    # assign to Coding Agent
    query = """
    mutation($repositoryId: ID!, $title: String!, $body: String!, $assigneeIds: [ID!]!) {
        createIssue(input: {repositoryId: $repositoryId, title: $title, body: $body, assigneeIds: $assigneeIds}) {
            issue {
            id
            title
            assignees(first: 10) {
                nodes {
                login
                }
            }
            }
        }
        }
    """

    variables = {"repositoryId": repo_id, "assigneeIds": [coding_agent_id], "title": title, "body": body}
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(github_graph_url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()
    issue_id = data.get("data", {}).get("createIssue", {}).get("issue", {}).get("id", "")
    print(data)
    if response.status_code != 200:
            raise RuntimeError(f"GitHub API error: {response.status_code} {response.text}")

    return issue_id


def get_coding_agent_id(owner: str, name: str) -> str:
        """Returns the Id of Copilot Coding Agent if a suggested actor for the repo includes a Bot.

        Uses GitHub GraphQL API with variables (safer than direct f-string interpolation).
        """
        if not GITHUB_TOKEN:
            raise RuntimeError("GITHUB_TOKEN not set in environment")

        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
                    nodes {
                        login
                        __typename
                        ... on Bot { id }
                        ... on User { id }
                    }
                }
            }
        }
        """
        variables = {"owner": owner, "name": name}

        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        response = requests.post(github_graph_url, headers=headers, json={"query": query, "variables": variables})
        if response.status_code != 200:
                raise RuntimeError(f"GitHub API error: {response.status_code} {response.text}")

        data = response.json()
        print(data)
        nodes = (
                data.get("data", {})
                        .get("repository", {})
                        .get("suggestedActors", {})
                        .get("nodes", [])
        )
        coding_agent_node = next((node for node in nodes if node.get("__typename") == "Bot"), None)
        if coding_agent_node:
            return coding_agent_node.get("id")
        raise ValueError("Coding agent not found for repo")

__all__ = ["get_static_message", "get_coding_agent_id", "create_issue"]

# CLI runner for has_coding_agent
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create an issue in the given repo.")
    parser.add_argument("repo_url", type=str, help="Repository url")
    args = parser.parse_args()
    result = create_issue(args.repo_url, "Migrate to .net 8", "Migrate to .NET 8")
    print(result)

