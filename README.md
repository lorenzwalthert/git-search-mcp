# Git Search MCP Server

***
This is an experimental project. No warranty.
***

Read-only MCP server to find relevant git diffs. In contrast to plain file analysis, this can 
* establish a connection between commit messages and diffs for relevant regular expressions. 
* reduce noise from the context window by focussing on a diff instead of whole files.

The server is useful to extract relevant information for code changes that often touch similar places in the code base and contain similar commit messages, such as:

- introducing new boilerplate code such as new parameter that have to be propagated through a system.
- config changes that always happen in the same files.
- code changes where the commit message adds information on top of the diff (because the two are not similar).

This information can ehance agent behaviour in learning from human committers to perform similar tasks.

## Installation

First install `uv`, then you can add the server to your mcp config with the following setting: 
* command: `uvx`
* args: `git+https://github.com/lorenzwalthert/git-search-mcp.git` and `git-search-mcp`


The server exposes two tools:
- `git_diffs_by_msg`: Returns last 5 git commit diffs matching a regex pattern in commit messages.
- `git_diff_by_content`: Returns last 5 commit diffs where diff content matches regex using `git log -G`.

# Usage

in AWS Q for example, you can transparently see tool invocation: 

![alt text](fig/q-1.png)

## Tool Parameters

### Both tools support:
- `regex` (required): Regex pattern to search
- `repo_path` (optional): Path to git repository (defaults to current directory)
- `file_glob` (optional): Glob pattern for files to search in (default **/*.py)
- `max_chars` (optional): Maximum character limit of return value (default 3000)


## Development

```bash
uv sync
```
