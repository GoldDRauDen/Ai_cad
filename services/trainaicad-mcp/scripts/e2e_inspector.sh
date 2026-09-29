#!/usr/bin/env bash
# E2E smoke for TrainAiCad MCP V0.1 via MCP Inspector CLI (HTTP transport).
set -u
cd "$(dirname "$0")/.." || exit 1
INS="npx -y @modelcontextprotocol/inspector@2.8.0 --cli --server-url http://127.0.0.1:8787/mcp --transport http"
PASS=0; FAIL=0
ok()   { echo "PASS: $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

# unescape the JSON text payload so greps read like plain JSON
call() {
  local tool="$1"; shift
  local cmd="$INS --method tools/call --tool-name $tool"
  while [ $# -gt 0 ]; do cmd="$cmd --tool-arg '$1'"; shift; done
  eval "$cmd" 2>&1 | sed 's/\\"/"/g'
}

SHA_A=$(printf 'a%.0s' {1..64})
SHA_B=$(printf 'b%.0s' {1..64})
# expected production release read from the live entrypoint (never hard-coded)
EXPECT=$(grep -o 'Current production release is \*\*V[0-9.]*\*\*' ../../AI_ENTRYPOINT.md | grep -o 'V[0-9.]*')
[ -n "$EXPECT" ] || { echo "FAIL: cannot resolve release from AI_ENTRYPOINT.md"; exit 1; }
echo "expected release pin: $EXPECT"

LIST=$($INS --method tools/list 2>/dev/null)
for t in open_cad_job submit_cad_evidence route_cad_parts get_cad_job; do
  echo "$LIST" | grep -q "\"name\": \"$t\"" && ok "tool listed: $t" || bad "tool listed: $t"
done

# 1. AUTO + reference DXF must stay NEW_PDF_TO_DXF
OUT=$(call open_cad_job "drawing={\"fileName\":\"sample.pdf\",\"sha256\":\"$SHA_A\"}" \
  "referenceDxf={\"fileName\":\"ref.dxf\",\"sha256\":\"$SHA_B\"}" "mode=AUTO")
echo "$OUT" | grep -q '"mode": "NEW_PDF_TO_DXF"' && ok "AUTO+reference => NEW_PDF_TO_DXF" || bad "AUTO+reference: $OUT"
JOB=$(echo "$OUT" | grep -o 'cad_[0-9a-f]\{16\}' | head -1)
[ -n "$JOB" ] && ok "jobId=$JOB" || bad "jobId missing"

# 2. DIRECT audit without reference must FAIL
ERR=$(call open_cad_job "drawing={\"fileName\":\"sample.pdf\",\"sha256\":\"$SHA_A\"}" \
  "mode=DIRECT_EXISTING_DXF_AUDIT")
echo "$ERR" | grep -q 'requires referenceDxf' && ok "direct audit w/o reference FAILs" || bad "direct audit: $ERR"

# 3. submit evidence
EV='{"schema":"CAD_EVIDENCE_V1","jobId":"'"$JOB"'","code":"056648","source":{"sourceId":"'"$SHA_A"'","page":1},"material":{"printed":"SS400","family":"SS","thickness":{"value":3,"unit":"mm","origin":"PRINTED"}},"views":[{"id":"A","type":"FLAT"}],"contour":{"topology":"PLATE","status":"PROVED","overallX":{"value":50,"unit":"mm","origin":"PRINTED"},"overallY":{"value":32,"unit":"mm","origin":"PRINTED"}},"features":[{"id":"S1","family":"SLOT","quantity":1,"width":{"value":10,"unit":"mm","origin":"PRINTED"}}],"bends":[],"markings":[],"handwriting":[],"uncertainties":[]}'
OUT=$(call submit_cad_evidence "jobId=$JOB" "evidence=[$EV]")
echo "$OUT" | grep -q '"state": "EVIDENCE_READY"' && ok "submit_cad_evidence => EVIDENCE_READY" || bad "submit: $OUT"

# 4. route
OUT=$(call route_cad_parts "jobId=$JOB")
echo "$OUT" | grep -q '"mode": "FLAT_NO_BEND"' && ok "route => FLAT_NO_BEND" || bad "route: $OUT"
echo "$OUT" | grep -q 'SLOTS.md' && ok "route loads SLOTS module" || bad "route modules: $OUT"

# 5. get
OUT=$(call get_cad_job "jobId=$JOB")
echo "$OUT" | grep -q "\"release\": \"$EXPECT\"" && ok "release pin $EXPECT" || bad "release pin ($EXPECT): $OUT"
echo "$OUT" | grep -q 'PRODUCTION_PASS' && bad "job reached PRODUCTION_PASS" || ok "no PRODUCTION_PASS shortcut"

# 6. ingest drawing PDF (base64) bound to job
PDF_B64=$(printf '%%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n%%%%EOF\n' | base64 -w0)
OUT=$(call ingest_cad_file "fileName=../../evil sample.pdf" "role=DRAWING" "data=$PDF_B64" "jobId=$JOB")
echo "$OUT" | grep -q '"kind": "PDF"' && ok "ingest PDF (base64) => kind PDF" || bad "ingest pdf: $OUT"
echo "$OUT" | grep -q '"fileName": "evil sample.pdf"' && ok "filename sanitized" || bad "filename: $OUT"
echo "$OUT" | grep -q "sources/DRAWING/" && ok "drawing stored under DRAWING/" || bad "path: $OUT"
DRAW_SHA=$(echo "$OUT" | grep -o '"sha256": "[0-9a-f]\{64\}"' | head -1 | grep -o '[0-9a-f]\{64\}')

# 7. ingest reference DXF separately
DXF_B64=$(printf '0\nSECTION\n2\nENTITIES\n0\nENDSEC\n0\nEOF\n' | base64 -w0)
OUT=$(call ingest_cad_file "fileName=ref.dxf" "role=REFERENCE_DXF" "data=$DXF_B64" "jobId=$JOB")
echo "$OUT" | grep -q '"kind": "DXF"' && ok "ingest DXF => kind DXF" || bad "ingest dxf: $OUT"
echo "$OUT" | grep -q "sources/REFERENCE_DXF/" && ok "reference stored under REFERENCE_DXF/" || bad "ref path: $OUT"
REF_SHA=$(echo "$OUT" | grep -o '"sha256": "[0-9a-f]\{64\}"' | head -1 | grep -o '[0-9a-f]\{64\}')
[ -n "$DRAW_SHA" ] && [ -n "$REF_SHA" ] && [ "$DRAW_SHA" != "$REF_SHA" ] \
  && ok "drawing and reference are distinct sources" || bad "sha draw=$DRAW_SHA ref=$REF_SHA"

# 8. rejected inputs
ERR=$(call ingest_cad_file "fileName=payload.exe" "role=DRAWING" "data=$PDF_B64")
echo "$ERR" | grep -q 'UNSUPPORTED_FILE_TYPE' && ok "extension whitelist rejects .exe" || bad "exe: $ERR"
ERR=$(call ingest_cad_file "fileName=a.pdf" "role=DRAWING")
echo "$ERR" | grep -q 'PROVIDE_EXACTLY_ONE_OF_DATA_OR_URI' && ok "data/uri exclusivity enforced" || bad "exclusivity: $ERR"
ERR=$(call ingest_cad_file "fileName=a.pdf" "uri=file:///etc/passwd" "role=DRAWING")
echo "$ERR" | grep -q 'UNSUPPORTED_URI_SCHEME' && ok "file:// URI rejected" || bad "scheme: $ERR"
ERR=$(call ingest_cad_file "fileName=a.pdf" "uri=http://127.0.0.1:9/a.pdf" "role=DRAWING")
echo "$ERR" | grep -q 'PRIVATE_ADDRESS_BLOCKED' && ok "private address blocked" || bad "ssrf: $ERR"

# 9. DRAWING binding is immutable per job: new valid PDF content must be refused
PDF2_B64=$(printf '%%PDF-1.7\nother content\ntrailer\n%%%%EOF\n' | base64 -w0)
ERR=$(call ingest_cad_file "fileName=other.pdf" "role=DRAWING" "data=$PDF2_B64" "jobId=$JOB")
echo "$ERR" | grep -q 'SOURCE_ALREADY_BOUND' && ok "DRAWING binding immutable" || bad "rebind: $ERR"

# 10. unknown job cannot be bound
ERR=$(call ingest_cad_file "fileName=a.pdf" "role=DRAWING" "data=$PDF_B64" "jobId=cad_0000000000000000")
echo "$ERR" | grep -q 'JOB_NOT_FOUND' && ok "binding unknown job fails closed" || bad "unknown job: $ERR"

echo "---- inspector e2e: $PASS passed, $FAIL failed ----"
echo "JOB_ID=$JOB"
[ "$FAIL" -eq 0 ]
