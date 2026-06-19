# Workflow Implementation Notes

## NEEDLE Research (2026-06-17)

- NEEDLE dispatch interface: YAML adapter → `bash -c` with rendered template → waits for exit code
- Adding a new agent requires only a YAML file (no code changes)
- `claude-interactive` plugin wraps CLI in PTY for subscription billing
- Key NEEDLE repos: jedarden/NEEDLE, jedarden/bead-forge, jedarden/claude-governor
- Kiro CLI has no headless/batch mode — would need a PTY wrapper adapter (like claude-interactive) to integrate with NEEDLE
- bead-forge (`bf`) is the correct CLI for multi-worker fleets (not bare `br`)

## Subagent vs NEEDLE Comparison

| Feature | Subagents (current) | NEEDLE |
|---------|-------------------|--------|
| Parallel execution | ✅ | ✅ |
| Role-based routing | ✅ | ✅ (via adapter YAML) |
| Dependencies | ✅ (depends_on) | ✅ (bf dep add) |
| Persistent queue | ❌ (ephemeral) | ✅ (SQLite) |
| Retry | ❌ | ✅ |
| Work-stealing | ❌ | ✅ |
| Crash recovery | Manual (pickup-memory) | Relaunch workers, queue intact |
| Setup complexity | Zero (built-in) | Rust toolchain + bead-forge + adapters |

## Safety Posture Tiers (Reference)

- **Tier 0:** Local code only. No cloud, no DB, no network. (Current choice for subagents)
- **Tier 1:** Staging-only access controls, read-write staging DB (DROP/TRUNCATE denied), feature branch push only
- **Tier 2:** Network isolation (ExitBox/containers), explicit egress allowlist, filesystem mounts, spend-cap proxy

## Crash Recovery Path (Subagents)

1. `/pickup-memory <feature>` — reads active-work + plan.md
2. Check which plan items are marked complete
3. Diff worktree against branch to see what code landed
4. Re-spawn subagents for unchecked items
