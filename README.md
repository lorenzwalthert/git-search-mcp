# Git Search MCP Server

MCP server that exposes a tool to search git commit diffs using regex patterns.

## Installation

```bash
uv sync
```

## Usage

Run the server:
```bash
uv run git-search-mcp
```

The server exposes one tool:
- `search_git_diffs`: Takes a regex pattern and returns the last 5 commits with diffs matching that pattern

## Tool Parameters

- `regex` (required): Regex pattern to search in commit diffs
- `repo_path` (optional): Path to git repository (defaults to current directory)