# No Temporary Solutions

Production work must use the correct architecture path. Temporary fixes are not
allowed to pass review.

## Rules

- No placeholders.
- No fake data in delivered behavior.
- No temporary fixes.
- No "for now" implementations.
- No parallel bypass of an existing system.
- No hidden fallback that changes business behavior silently.
- No local-only behavior presented as production-ready.

## Blocked Work

If proper implementation is blocked:

1. Stop.
2. Describe the blocker.
3. Identify the affected files, modules, or contracts.
4. Propose the proper architectural solution.
5. Record the decision needed from the user or owner.

Do not ship a workaround while waiting for the decision.

## Review Rule

Any task containing a temporary solution must be marked `CHANGES_REQUIRED` or
`BLOCKED`, never `DONE`.
