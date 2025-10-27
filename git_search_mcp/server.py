import re
import asyncio
from pathlib import Path
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
            name="search_git_diffs_by_msg",
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
                    "file_glob": {
                        "type": "string",
                        "description": "Glob pattern for files to search in (default **/*.py). Wildcard globs matching many files can be helpful in early phase of search, while later on, when relevant files are identified, the search can be narrowed to certain files only.",
                        "default": "**/*.py",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum character limit of return value (default 1000)",
                        "default": 1000,
                    },
                },
                "required": ["regex"],
            },
        ),
        Tool(
            name="search_git_diff_by_content",
            description="Search last 5 commits where diff content matches regex using git log -G",
            inputSchema={
                "type": "object",
                "properties": {
                    "regex": {
                        "type": "string",
                        "description": "Regex pattern to search in diff content",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (defaults to current directory)",
                        "default": ".",
                    },
                    "file_glob": {
                        "type": "string",
                        "description": "Glob pattern for files to search in (default **/*.py). Wildcard globs matching many files can be helpful in early phase of search, while later on, when relevant files are identified, the search can be narrowed to certain files only.",
                        "default": "**/*.py",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum character limit of return value (default 1000)",
                        "default": 1000,
                    },
                },
                "required": ["regex"],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "search_git_diffs_by_msg":
        return await search_git_diffs_by_msg(arguments)
    elif name == "search_git_diff_by_content":
        return await search_git_diff_by_content(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def search_git_diffs_by_msg(arguments: dict[str, Any]) -> list[TextContent]:
    regex_pattern = arguments["regex"]
    repo_path = arguments.get("repo_path", ".")
    file_glob = arguments.get("file_glob", "**/*.py")
    max_chars = arguments.get("max_chars", 1000)

    try:
        repo = git.Repo(repo_path)
        commits = list(
            repo.iter_commits(
                grep=regex_pattern, max_count=5, **{"extended-regexp": True}
            )
        )

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
                if item.diff and (
                    (item.a_path and Path(item.a_path).match(file_glob))
                    or (item.b_path and Path(item.b_path).match(file_glob))
                ):
                    result += item.diff.decode("utf-8", errors="ignore")
            result += "-" * 80 + "\n\n"

        return [TextContent(type="text", text=result[:max_chars])]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def search_git_diff_by_content(arguments: dict[str, Any]) -> list[TextContent]:
    regex_pattern = arguments["regex"]
    repo_path = arguments.get("repo_path", ".")
    file_glob = arguments.get("file_glob", "**/*.py")
    max_chars = arguments.get("max_chars", 1000)

    try:
        repo = git.Repo(repo_path)

        # Use git log -G with extended-regexp
        commit_hashes = repo.git.log(
            "-G", regex_pattern, "--extended-regexp", "--format=%H", "-5"
        ).split("\n")

        commits = [repo.commit(h) for h in commit_hashes if h]

        if not commits:
            return [
                TextContent(
                    type="text",
                    text=f"No commits found with diff content matching pattern '{regex_pattern}'",
                )
            ]

        result = f"Found {len(commits)} commits with diff content matching pattern '{regex_pattern}':\n\n"
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
                if item.diff and (
                    (item.a_path and Path(item.a_path).match(file_glob))
                    or (item.b_path and Path(item.b_path).match(file_glob))
                ):
                    result += item.diff.decode("utf-8", errors="ignore")
            result += "-" * 80 + "\n\n"

        return [TextContent(type="text", text=result[:max_chars])]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    # Run the server using stdin/stdout streams

    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions
    import mcp.server.stdio

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="git-search-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def cli():
    asyncio.run(main())


if __name__ == "__main__":
    cli()
