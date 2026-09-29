# TrainAiCad MCP V0.1 — EXPERIMENTAL

This service is an experimental MCP runtime boundary for TrainAiCad. It does **not** modify or replace the current production LISPCAD skill.

## V0.1 scope

Implemented:
- `CAD_EVIDENCE_V1` schema with provenance on technical numbers.
- Job state machine with fail-closed transitions.
- Runtime production-release pinning from repository `AI_ENTRYPOINT.md` + `SKILL_LISPCAD_CURRENT.md`.
- Deterministic first-pass routing for FLAT/BEND, topology, features, acute bends and BOXMET.
- Jev policy boundary plus disabled/mock/shadow adapter contract. V0.1 performs no Jev network call.
- Four MCP tools: `open_cad_job`, `submit_cad_evidence`, `route_cad_parts`, `get_cad_job`.
- Loopback-only Streamable HTTP endpoint at `/mcp`.

Not implemented in V0.1:
- PDF/image/DXF byte ingestion.
- Vision/OCR.
- Canonical manufacturing geometry.
- Nobi/unfold calculation.
- DXF write/read-back.
- Production PASS.
- Persistent database.
- Authentication or public-network deployment.

## Safety boundaries

- `AUTO` resolves to `NEW_PDF_TO_DXF` even when a DATA/reference DXF is present. Direct AI-DXF vs approved-reference audit must be selected explicitly.
- Jev is advisory only and cannot author dimensions, coordinates, Nobi, geometry, DXF entities or production PASS.
- Every job pins the production release detected in the repository. Startup/job creation fails closed with `SKILL_FRESHNESS_UNVERIFIED` if entrypoint and CURRENT disagree.
- V0.1 cannot transition directly to `PRODUCTION_PASS`.

## Run locally

Requires Node.js 22+.

```bash
cd services/trainaicad-mcp
npm install
npm run check
npm run dev
```

Default endpoint:

```text
http://127.0.0.1:8787/mcp
```

Use MCP Inspector against that endpoint. V0.1 intentionally binds loopback only.

## Environment

Copy `.env.example` to `.env` when local runtime configuration is needed.

`JEV_MODE` may be `disabled`, `mock`, or `shadow`. In V0.1 all modes remain non-authoritative; `shadow` is a contract placeholder until credentials/runtime are configured.

## Next milestones

V0.2: canonical geometry boundary and deterministic builders.

V0.3: composite DXF export, re-open/read-back and independent CUT/HOLE/BEND/KEGAKI/RIB QA.
