# RUNTIME_AUTHORITY_GUARD — repo-direct precedence

**Status:** USER APPROVED 2026-10-05.

## Purpose

Prevent inherited compatibility wording inside older active core text from overriding the current repo-direct production architecture.

## Runtime authority

For every normal CAD job, authority is:

`USER TASK -> AI_ENTRYPOINT.md -> ROUTER.yaml -> routed active CORE/MODE/FEATURE/REFERENCE modules -> validation -> output`.

`AGENTS.md` is orchestration policy only. Historical releases and the portable compatibility snapshot are not normal production authority.

If inherited text inside an active modular file says that the portable skill is the single source, must be read in full, or otherwise implies a portable-first runtime, treat that wording as **LEGACY_COMPATIBILITY_TEXT**. It does not authorize loading `skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md` in a normal repo-direct job.

The portable snapshot may be read only for the purposes allowed by `ROUTER.yaml`: compatibility/audit or diagnosis of `ROUTING_COVERAGE_GAP`. A route gap remains a hard stop; portable text may not be used as a silent production fallback.

## Output-contract precedence

When inherited wording describes an older packaging contract such as automatic individual DXFs plus a combined DXF, the currently routed `skills/lispcad/core/CAD_OUTPUT.md` controls output packaging. Legacy packaging prose does not override the current one-composite default.

## Conflict handling

If two currently routed engineering modules still make materially incompatible manufacturing decisions after applying this authority guard, report `SKILL_CONFLICT`; do not choose by file age, filename version, chat memory, or convenience.

This guard changes no geometry formula, Nobi table, material rule, tolerance rule, thread rule, or DXF numeric convention.