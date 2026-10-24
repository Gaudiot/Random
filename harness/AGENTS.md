# Agent Working Agreement

These instructions apply to all repositories unless superseded by more specific project instructions.

## Analyze and decompose first

Before editing files, inspect the request, applicable repository instructions, relevant code paths, and the current working tree.

For non-trivial changes, create a concise work plan with cohesive, independently verifiable work items.

For simple, localized changes, proceed directly after briefly identifying the intended modification and its validation.

Keep planning proportional to task complexity.

Break the request into cohesive work items. Each item should be comparable to a small, focused pull request that a human can understand and review without unrelated context:

- One clear purpose and observable outcome.
- A narrow, explicit file or module scope.
- Minimal coupling to other work items.
- Its own relevant validation.
- No unrelated cleanup or opportunistic refactoring.

Record dependencies between work items and choose a safe execution order. Do not split a naturally atomic change merely to create more tasks, and do not combine independent concerns into one large change.

## Use parallel agents deliberately

Multiple agents may be spawned when two or more work items can proceed independently. Prefer parallel delegation for independent codebase exploration, implementation in non-overlapping modules, test analysis, documentation, or other work with clearly separated ownership.

When delegating:

- Give each agent a bounded objective, owned files or responsibility, relevant context, and expected validation or output.
- Tell implementation agents that they share the repository with other agents, must preserve existing and concurrent changes, and must not revert work they do not own.
- Avoid parallel edits to the same files or tightly coupled behavior. Run dependent work sequentially.
- Keep integration responsibility with the primary agent. Review every agent result, reconcile cross-cutting assumptions, and validate the combined state rather than trusting summaries alone.
- Use the fewest agents that materially improve speed, focus, or review quality. Parallelism is not a goal by itself.

## Implementation standards

Follow established project conventions before broader ecosystem practices, and broader ecosystem practices before general language conventions. Make the smallest coherent change that satisfies the requested behavior. Preserve unrelated user changes and keep each work item easy to review.

While implementing, consider validation, error paths, boundary conditions, compatibility, and testability. Do not defer obvious correctness work to the final review phase.

## Specialized quality passes

For meaningful application behavior changes, use
specialized agents when their contribution justifies
the execution cost and available time.

Preferred sequence:
1. unit_test_engineer: analyze and implement focused
   tests where unit testing is appropriate.
2. maintainability_reviewer: perform a read-only
   review after implementation and relevant tests
   are coherent.

For small or time-sensitive changes, the primary agent
may perform focused testing and review directly.

Prioritize delivering correct, validated functionality
over completing every specialized pass.

When skipping a relevant agent, briefly state why.

## Validation and handoff

Validate each work item with the narrowest relevant checks, then run the broader applicable suite after integration when practical. Never claim a command or test passed unless it was actually run.

The final report must summarize:

- The work items completed and their outcomes.
- Delegated agents used and what each contributed.
- Tests and validation commands run, with results.
- Maintainability findings addressed or intentionally deferred, including rationale.
- Remaining risks, coverage gaps, or checks that could not be performed.
