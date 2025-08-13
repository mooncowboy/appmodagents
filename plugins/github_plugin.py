
from services.github_service import create_issue
from semantic_kernel.functions import kernel_function

class GithubPlugin:
	@kernel_function(
		name="create_issue",
		description="Create a new GitHub issue in the given repository URL (https://github.com/<owner>/<repo>). Provide a clear title and body describing the problem or task."
	)
	def create_issue(self, repo_url: str, title: str, body: str) -> str:
		"""Create an issue via the GitHub GraphQL API.

		Args:
			repo_url: Full HTTPS repo URL, e.g. https://github.com/owner/repo
			title: Concise issue title.
			body: Detailed issue body (may include markdown).
		Returns:
			A confirmation string containing the created issue identifier or error text.
		"""
		try:
			issue_id = create_issue(repo_url, title, body)
			return f"GitHub issue created successfully. Issue node id: {issue_id}"
		except Exception as e:
			# Return the error so the model can surface it or decide to retry / ask user.
			return f"Failed to create issue: {type(e).__name__}: {e}"
