#!/usr/bin/env python3
import asyncio
from git_search_mcp.server import handle_call_tool


async def debug():
    result = await handle_call_tool(
        name="search_git_diffs_by_msg",
        arguments={
            "regex": "feat.*parameter|add.*parameter|parameter.*feat|new.*param",
            "file_extensions": [
                ".py",
            ],
            "repo_path": "/Users/lorenz/git/signals",
        },
    )
    print(result[0].text)


if __name__ == "__main__":
    asyncio.run(debug())
