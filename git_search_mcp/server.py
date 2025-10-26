import re
import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import git


app = Server("git-search-mcp")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_git_diffs",
            description="Search last 5 git commit diffs matching a regex pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "regex": {
                        "type": "string",
                        "description": "Regex pattern to search in commit diffs",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (defaults to current directory)",
                        "default": ".",
                    },
                },
                "required": ["regex"],
            },
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name != "search_git_diffs":
        raise ValueError(f"Unknown tool: {name}")

    regex_pattern = arguments["regex"]
    repo_path = arguments.get("repo_path", ".")

    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits(grep=regex_pattern, max_count=5))

        if not commits:
            return [
                TextContent(
                    type="text",
                    text=f"No commits found matching pattern '{regex_pattern}'",
                )
            ]

        result = f"Found {len(commits)} commits matching pattern '{regex_pattern}':\n\n"
        for commit in commits:
            result += f"Commit: {commit.hexsha[:8]}\n"
            result += f"Author: {str(commit.author)}\n"
            result += f"Date: {commit.committed_datetime.isoformat()}\n"
            result += f"Message: {commit.message.strip()}\n"

            # Get diff
            diff = commit.diff(
                commit.parents[0] if commit.parents else git.NULL_TREE,
                create_patch=True,
            )
            result += "Diff:\n"
            for item in diff:
                if item.diff:
                    result += item.diff.decode("utf-8", errors="ignore")
            result += "-" * 80 + "\n\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
