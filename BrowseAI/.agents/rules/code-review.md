# Code Review & Verification Policy

## Purpose
To ensure code quality, minimize bugs, increase efficiency, and enforce the DRY (Don't Repeat Yourself) principle across the NexusAI codebase.

## Rule 1: Mandatory Self-Review
Before marking any task as complete in `task.md` or informing the user that a phase is done, you MUST perform a self-review of the code you just wrote. 

During self-review, check for:
- **DRY Principle violations**: Are there duplicated logic blocks that could be extracted into a shared utility function in `@nexusai/shared`?
- **TypeScript strictness**: Are there any missing types, implicit `any`s, or unhandled Promises?
- **Security**: Are we exposing any sensitive API keys or violating the `fork-policy.md`?

## Rule 2: Post-Implementation Verification Step
Every implementation step must include a verification phase.
- Do not assume code works just because it was written.
- Run the build process (`pnpm build`) for the affected packages.
- If it's a CLI tool, run a dry-run command or `--help` to verify execution.
- If it's a UI component, verify it compiles without warnings in Vite/WXT.

## Rule 3: Refactoring for Efficiency
If you encounter messy or duplicated code inherited from the original source repo (`source-repo`), **refactor it**.
Do not blindly copy inefficient code. Clean it up, modularize it, and document the refactor in the phase documents.

## Rule 4: Explicit Review Confirmation
When presenting your completed work to the user, include a brief "Code Review & Verification" summary explaining what you reviewed, what DRY improvements you made, and how you verified the build.
