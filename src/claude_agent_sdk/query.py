"""Query function for one-shot interactions with Claude Code."""

import os
from contextlib import aclosing
from collections.abc import AsyncIterable, AsyncIterator
from typing import Any

from ._internal.client import InternalClient
from ._internal.transport import Transport
from .types import ClaudeAgentOptions, Message


async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None,
) -> AsyncIterator[Message]:
    """
    Query Claude Code for one-shot or unidirectional streaming interactions.

    This function is ideal for simple, stateless queries where you don't need
    bidirectional communication or conversation management. For interactive,
    stateful conversations, use ClaudeSDKClient instead.

    Key differences from ClaudeSDKClient:
    - **Unidirectional**: Send all messages upfront, receive all responses
    - **Stateless**: Each query is independent, no conversation state
    - **Simple**: Fire-and-forget style, no connection management
    - **No interrupts**: Cannot interrupt or send follow-up messages

    When to use query():
    - Simple one-off questions ("What is 2+2?")
    - Batch processing of independent prompts
    - Code generation or analysis tasks
    - Automated scripts and CI/CD pipelines
    - When you know all inputs upfront

    When to use ClaudeSDKClient:
    - Interactive conversations with follow-ups
    - Chat applications or REPL-like interfaces
    - When you need to send messages based on responses
    - When you need interrupt capabilities
    - Long-running sessions with state

    Args:
        prompt: The prompt to send to Claude. Can be a string for single-shot queries
                or an AsyncIterable[dict] for streaming mode with continuous interaction.
                In streaming mode, each dict should have the structure:
                {
                    "type": "user",
                    "message": {"role": "user", "content": "..."},
                    "parent_tool_use_id": None,
                    "session_id": "..."
                }
        options: Optional configuration (defaults to ClaudeAgentOptions() if None).
                 Set options.permission_mode to control tool execution:
                 - 'default': CLI prompts for dangerous tools
                 - 'acceptEdits': Auto-accept file edits
                 - 'bypassPermissions': Allow all tools (use with caution)
                 Set options.cwd for working directory.
        transport: Optional transport implementation. If provided, this will be used
                  instead of the default transport selection based on options.
                  The transport will be automatically configured with the prompt and options.

    Yields:
        Messages from the conversation

    Example - Simple query:
        ```python
        # One-off question
        async for message in query(prompt="What is the capital of France?"):
            print(message)
        ```

    Example - With options:
        ```python
        # Code generation with specific settings
        async for message in query(
            prompt="Create a Python web server",
            options=ClaudeAgentOptions(
                system_prompt="You are an expert Python developer",
                cwd="/home/user/project"
            )
        ):
            print(message)
        ```

    Example - Streaming mode (still unidirectional):
        ```python
        async def prompts():
            yield {"type": "user", "message": {"role": "user", "content": "Hello"}}
            yield {"type": "user", "message": {"role": "user", "content": "How are you?"}}

        # All prompts are sent, then all responses received
        async for message in query(prompt=prompts()):
            print(message)
        ```

    Example - With custom transport:
        ```python
        from claude_agent_sdk import query, Transport

        class MyCustomTransport(Transport):
            # Implement custom transport logic
            pass

        transport = MyCustomTransport()
        async for message in query(
            prompt="Hello",
            transport=transport
        ):
            print(message)
        ```

    """
    if options is None:
        options = ClaudeAgentOptions()

    os.environ["CLAUDE_CODE_ENTRYPOINT"] = "sdk-py"

    client = InternalClient()

    # aclosing() on the INNER generator is load-bearing, not defensive.
    #
    # When a caller exits this generator early (a `break`, or an exception
    # raised out of its loop body), `query()`'s own frame unwinds and drops its
    # only reference to `client.process_query(...)`. That inner generator is
    # then garbage, and asyncio finalizes it via `loop._asyncgen_finalizer_hook`
    # -> `create_task(agen.aclose())` -- in a NEW, FOREIGN task.
    #
    # Its `finally: await query.close()` (_internal/client.py) therefore runs in
    # that foreign task and calls `Query.close()`, which does
    # `self._tg.cancel_scope.cancel()`. But `_tg` was entered by
    # `Query.start()` in the CALLER's task, so anyio delivers that cancellation
    # to the caller -- cancelling whatever it happens to be awaiting, typically
    # something completely unrelated. Worse, `__aexit__` from a foreign task
    # raises `RuntimeError: Attempted to exit cancel scope in a different task`,
    # which `Query.close()`'s cancel-only `suppress()` does NOT catch, so the
    # scope is cancelled but never exited and anyio re-delivers the
    # cancellation on every subsequent await, permanently.
    #
    # Closing the inner generator HERE keeps that teardown in the owning task.
    # Receipts: three multi-hour SF3 E2E runs killed this way (2026-07-29/30) by
    # a bare `CancelledError` at an unrelated subprocess spawn; a caller-side
    # `aclosing(query(...))` alone does NOT prevent it -- it is precisely what
    # orphans this generator.
    async with aclosing(
        client.process_query(prompt=prompt, options=options, transport=transport)
    ) as inner:
        async for message in inner:
            yield message
