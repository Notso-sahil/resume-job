# Development Workflow Rules

## Rule 1: Phase Gating

Every piece of work in this project is organized into numbered phases. The following applies:

- **Do not start Phase N+1 until Phase N is verified complete.**
- Mark phase tasks as complete in `task.md` only after testing confirms they work.
- If a phase reveals new complexity, update `implementation_plan.md` before proceeding.

---

## Rule 2: Build Order

Packages must always be built in dependency order:

```
@nexusai/shared  →  @nexusai/bridge  →  @nexusai/extension
```

Never attempt to build `bridge` or `extension` before `shared` has a successful `dist/` output.

The command to build all in order:
```bash
pnpm --filter @nexusai/shared build && pnpm --filter @nexusai/bridge build
```

---

## Rule 3: File Organization

- **Never create source files in the root** of `NexusAI/`. All source code goes inside `packages/`.
- Documentation goes in `docs/`.
- Scripts (PowerShell, Node.js utilities) go in `scripts/`.
- Agent configuration goes in `.agents/`.
- The cloned source reference repo (`source-repo/`) must never be edited — it is read-only reference material.

---

## Rule 4: Extension Identity

The extension MUST NOT have a `key` field in its `manifest.json` or `wxt.config.ts`. This ensures Chrome generates a fresh Extension ID that belongs to us, not to the original project.

After loading the extension unpacked:
1. Note the new Extension ID from `chrome://extensions/`.
2. Update the `allowed_origins` in the native messaging manifest.
3. Run `nexus-bridge register` again to write the updated manifest.

---

## Rule 5: Port Discipline

| Service | Port | Notes |
|:---|:---|:---|
| NexusAI Bridge | **12307** | Our bridge — always use this |
| mcp-chrome-bridge (old) | 12306 | May still be installed; do not touch it |

Never use port 12306 in any new code. If 12307 is in use, diagnose with:
```powershell
netstat -ano | findstr 12307
```

---

## Rule 6: TypeScript Strictness

All code in this project uses TypeScript `strict: true`. This means:
- No `any` types except in `tool-schemas.ts` where JSON Schema objects are typed as `any`.
- No `!` non-null assertions unless unavoidable — use optional chaining (`?.`) instead.
- All async functions must be `try/catch` wrapped or have explicit error handling.

---

## Rule 7: Testing Before Marking Complete

A phase task is only `[x]` complete when:
1. The code compiles without TypeScript errors.
2. The specific functionality was manually verified in the browser.
3. Any relevant entry in `task.md` is updated.
