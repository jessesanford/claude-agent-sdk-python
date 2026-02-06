# How to File the Feature Request Issue

This directory contains the documentation needed to file an issue for the `--append-system-prompt-file` feature with the upstream repository.

## Files Created

1. **GITHUB_ISSUE_TEXT.md** - Ready-to-copy text for pasting directly into a GitHub issue
2. **FEATURE_REQUEST_ISSUE.md** - Detailed feature request with full context and documentation
3. **.github/ISSUE_TEMPLATE/feature_request.md** - Reusable GitHub issue template for future feature requests

## How to File the Issue

### Option 1: Quick Copy-Paste (Recommended)

1. Navigate to the upstream repository's issues page
2. Click "New Issue"
3. Open `GITHUB_ISSUE_TEXT.md` in this repository
4. Copy the entire content (including the title at the top)
5. Paste into the GitHub issue form:
   - Use the title from line 1 of the file
   - Paste the rest of the content into the issue body
6. Submit the issue

### Option 2: Use the Detailed Document

1. Navigate to the upstream repository's issues page
2. Click "New Issue"
3. Open `FEATURE_REQUEST_ISSUE.md` in this repository
4. Copy the content and adapt as needed
5. Submit the issue

## What's Included

The issue documents cover:

- **Problem Statement**: CLI argument size limits (~131KB) preventing large system prompts
- **Use Cases**: Large custom rules, external prompt management, dynamic loading, CI/CD integration
- **Proposed Solution**: Add `append_file` parameter to `SystemPromptPreset`
- **API Design**: Clear examples of current vs. proposed usage
- **Benefits**: No size limits, better organization, easier maintenance
- **Implementation**: References to the existing implementation on this branch
- **Related Issue**: Link to upstream issue #6153

## Next Steps

After filing the issue:

1. Note the issue number (e.g., #123)
2. Reference that issue number when creating a Pull Request from this branch
3. Update the PR description to link to the issue

## Feature Implementation

The feature is already implemented on this branch (`copilot/add-append-system-prompt-file-support`) with:

- Type definitions in `src/claude_agent_sdk/types.py`
- Implementation in `src/claude_agent_sdk/_internal/transport/subprocess_cli.py`
- Test coverage in `tests/test_transport.py`
- Example usage can be demonstrated

The PR will include all of these changes.
