**Title:** Add Support for `--append-system-prompt-file` CLI Flag

---

## Summary

Add support for the `--append-system-prompt-file` flag in the Claude Agent SDK for Python to enable passing large system prompts via file paths instead of inline text, avoiding CLI argument size limits.

## Problem Statement

Currently, when using the SDK with custom system prompts that need to be appended to the `claude_code` preset, users must pass the entire prompt content as inline text using the `append` parameter. This approach has significant limitations:

1. **CLI Argument Size Limits**: Operating systems impose limits on command-line argument sizes (typically 131KB on most systems). Large system prompts exceed this limit and cause failures.

2. **Readability and Maintainability**: Embedding large prompt text in code makes it harder to read, maintain, and version control separately.

3. **Existing CLI Support**: The Claude Code CLI already supports the `--append-system-prompt-file` flag (available since v2.0.34), but the Python SDK doesn't expose this functionality.

## Use Cases

1. **Large Custom Rules**: Users who need to append extensive custom instructions, coding standards, or domain-specific rules to the Claude Code preset.

2. **External Prompt Management**: Teams that manage system prompts in separate files for easier editing, version control, and collaboration.

3. **Dynamic Prompt Loading**: Applications that need to load different prompt files based on context or user preferences.

4. **CI/CD Integration**: Automated workflows that generate or update system prompt files independently from the main codebase.

## Proposed Solution

Extend the `SystemPromptPreset` TypedDict to include an `append_file` parameter that accepts a file path (string or `Path` object). When provided, the SDK should:

1. Validate that the file exists before invoking the CLI
2. Pass the file path to the CLI using the `--append-system-prompt-file` flag
3. Provide clear error messages if the file is not found

### API Design

```python
from claude_agent_sdk import ClaudeAgentOptions

# Current approach (limited by CLI argument size)
options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": "Very long prompt text..."  # Limited to ~131KB
    }
)

# Proposed approach (no size limits)
options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append_file": "/path/to/custom-rules.txt"  # No size limit
    }
)
```

### Type Definition

```python
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

class SystemPromptPreset(TypedDict):
    """System prompt preset configuration."""
    type: Literal["preset"]
    preset: Literal["claude_code"]
    append: NotRequired[str | list[str]]
    append_file: NotRequired[str | Path]  # New parameter
```

## Benefits

1. **No Size Limits**: File-based prompts aren't subject to CLI argument size restrictions
2. **Better Organization**: Separates prompt content from application code
3. **Easier Maintenance**: Prompts can be edited without modifying code
4. **Version Control**: Prompt files can be tracked and versioned separately
5. **Consistency**: Aligns Python SDK with existing CLI capabilities

## Alternatives Considered

1. **Reading file content in Python**: Reading the file content in Python and passing it via `append` doesn't solve the CLI argument size limit issue.

2. **Environment Variables**: Using environment variables for large prompts is cumbersome and has similar size limitations.

3. **Temporary Files**: Automatically creating temporary files adds complexity and doesn't improve the developer experience.

## Additional Context

This feature is already implemented and tested in a branch with:
- Type definitions updated in `src/claude_agent_sdk/types.py`
- Implementation in `src/claude_agent_sdk/_internal/transport/subprocess_cli.py`
- Test coverage in `tests/test_transport.py`

Related upstream issue: https://github.com/anthropics/claude-code/issues/6153
