# Git Search MCP Server

MCP server to find relevant git diffs. In contrast to plain file analysis, this can establish a connection between commit messages and diffs for relevant regular expressions. 

The server works well for code changes that often touch similar places in the code base and contain similar commit messages, such as:

- introducing new boilerplate code such as new parameter that have to be propagated through a system.
- config changes that always happen in the same files.

This is an experimental project.

## Installation

```bash
uv sync
```

Only source installation is supported.

## Usage

Run the server:
```bash
uv run git-search-mcp
```

The server exposes two tools:
- `git_diffs_by_msg`: Returns last 5 git commit diffs matching a regex pattern in commit messages.
- `git_diff_by_content`: Returns last 5 commits where diff content matches regex using git log -G.

## Tool Parameters

### Both tools support:
- `regex` (required): Regex pattern to search
- `repo_path` (optional): Path to git repository (defaults to current directory)
- `file_glob` (optional): Glob pattern for files to search in (default **/*.py)
- `max_chars` (optional): Maximum character limit of return value (default 3000)