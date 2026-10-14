# TrainAiCad MCP V0.3 — Full Pipeline Runtime

This service is an experimental MCP runtime boundary for TrainAiCad. It does **not** modify or replace the current production LISPCAD skill.

## Implemented through V0.2

Implemented:
- `CAD_EVIDENCE_V1` schema with provenance on technical numbers.
- Job state machine with fail-closed transitions.
- Runtime production-release pinning from repository `AI_ENTRYPOINT.md` + `SKILL_LISPCAD_CURRENT.md`.
- V4.20 source classification: `PDF_ONLY`, `PDF_DATA_RAW`, `TRAIN_REFERENCE`, `DIRECT_EXISTING_DXF_AUDIT`.\n- Mandatory mechanical classification record and V4.20 feature routing (KEGAKI, SLIT/RELIEF, RIB, curved slot, PIASU).\n- Every bent/multi-face route loads `BEND_UNFOLD` + `FACE_GRAPH_UNFOLD_PROTOCOL`; missing signed bend/face evidence is REVIEW_REQUIRED.
- Jev policy boundary plus disabled/mock/shadow adapter contract. V0.1 performs no Jev network call.
- Six MCP tools: `ingest_cad_file`, `open_cad_job`, `submit_cad_evidence`, `route_cad_parts`, `build_canonical_geometry`, `get_cad_job`.
- Loopback-only Streamable HTTP endpoint at `/mcp`.
- File ingestion (`ingest_cad_file`): inline base64 or http(s) URI, SHA256, magic-byte signature sniffing, MIME/extension/size validation, filename sanitization, SSRF-guarded download (http(s) only, private ranges blocked by default, bounded redirects/size/time), immutable content-addressed storage under `data/sources/<ROLE>/`.
- DXFs are role-separated (`DATA_DXF`, `REFERENCE_DXF`, `AI_DXF`). In `PDF_DATA_RAW`, DATA is geometry authority and PDF controls semantics/dimensions/revisions/Nobi. In `TRAIN_REFERENCE`, reference DXF is audit-only.
- Filesystem job store under `data/jobs/<jobId>.json` (write-through), so jobs survive restarts and do not depend on a chat session.

Not implemented in V0.1:
- Vision/OCR.
- Canonical manufacturing geometry.
- Nobi/unfold calculation.
- DXF write/read-back.
- Production PASS.
- Authentication or public-network deployment.

## Safety boundaries

- `AUTO` + no DXF => `PDF_ONLY`; `AUTO` + generic DXF => `PDF_DATA_RAW`; explicit `referenceDxf` => `TRAIN_REFERENCE`; direct existing-DXF audit remains explicit.
- Jev is advisory only and cannot author dimensions, coordinates, Nobi, geometry, DXF entities or production PASS.
- Every job pins the production release detected in the repository. Startup/job creation fails closed with `SKILL_FRESHNESS_UNVERIFIED` if entrypoint and CURRENT disagree.
- V0.2 cannot transition directly to `PRODUCTION_PASS`; `GEOMETRY_READY` is not manufacturing PASS.

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

```bash
npx -y @modelcontextprotocol/inspector@2.8.0 --cli \
  --server-url http://127.0.0.1:8787/mcp --transport http --method tools/list
```

## Environment

Copy `.env.example` to `.env` when local runtime configuration is needed.

- `TRAINAICAD_MCP_PORT` (default `8787`), `TRAINAICAD_REPO_ROOT`, `TRAINAICAD_MCP_DATA` (default `services/trainaicad-mcp/data`).
- `TRAINAICAD_MAX_SOURCE_BYTES` (default 25 MiB), `TRAINAICAD_ALLOW_PRIVATE_URL=1` to permit loopback/private download targets during local testing.
- `JEV_MODE` may be `disabled`, `mock`, or `shadow`. In V0.1 all modes remain non-authoritative; `shadow` is a contract placeholder until credentials/runtime are configured. Adding `TYPESAFE_API_KEY` flips the adapter's `configured` flag; V0.1 still performs no Jev network call and never blocks the MCP.

## Next milestones

V0.2: canonical geometry boundary and deterministic builders.

V0.3: composite DXF export, re-open/read-back and independent CUT/HOLE/BEND/KEGAKI/RIB QA.


## V0.2 canonical geometry boundary

- `GEOMETRY_SOURCE_V1` is the explicit source-authorized geometry input contract.
- `PDF_DATA_RAW` geometry must match the bound DATA DXF SHA.
- `TRAIN_REFERENCE` construction must still use the drawing/source SHA; the reference remains audit-only.
- Flat single-face geometry validates non-degenerate/simple contours and exact feature-instance quantity.
- Constant-width X-axis linear bend chains build deterministic flat length and double bend zones from ordered outside lengths and Nobi after FACE_GRAPH G1–G7 proof fields are present.
- Unsupported mixed-axis, variable-width, bent-feature-transform, relief-domain or incomplete graph cases fail to `REVIEW_REQUIRED`; V0.2 does not guess or reverse-fit.
- `foldBack=STRUCTURAL_ONLY_V02` is explicitly not G8 production proof.



## V0.3 full runtime

V0.3 closes the runtime pipeline:
`ingest -> source mode -> CAD_EVIDENCE_V1 -> routing -> GEOMETRY_SOURCE_V1 -> CANONICAL_GEOMETRY_V1 -> MANUFACTURING_QA_V1 -> export_dxf -> audit_dxf -> PRODUCTION_PASS`.

- `export_dxf` reuses the approved repository serializer `tools/export_dxf.py` and produces one code-labeled composite mm DXF.
- The serializer performs its own write/read-back structural audit.
- `audit_dxf` then independently re-opens the produced file again through the MCP bridge and validates DXF audit errors, mm units, Layer 0 manufacturing geometry, non-plot AI_META and exact code-label order.
- `PRODUCTION_PASS` is reachable only through `GEOMETRY_READY -> DXF_WRITTEN -> DXF_READBACK -> QA_COMPLETE -> PRODUCTION_PASS`.
- Bent parts additionally require explicit full `foldBack=PASS`; V0.2 structural-only fold-back can never authorize production export.
- Unsafe/unsupported feature serialization fails closed rather than approximating geometry.

Runtime prerequisites now include Node 22+ and Python with repo `requirements.txt`.
