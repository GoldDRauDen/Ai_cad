import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { jobStore, routeJob } from "../src/core.js";
import { createExportPayload } from "../src/dxf.js";

process.env.TRAINAICAD_MCP_DATA = mkdtempSync(join(tmpdir(), "trainaicad-mcp-v03-"));

const SHA = "a".repeat(64);
const source = { fileName: "drawing.pdf", sha256: SHA, sourceId: SHA };

function n(value: number, unit: "mm" | "deg" = "mm") {
  return { value, unit, origin: "PRINTED" as const };
}

function readyJob() {
  const job = jobStore.create(source, undefined, "AUTO");
  jobStore.submitEvidence(job.jobId, [{
    schema: "CAD_EVIDENCE_V1",
    jobId: job.jobId,
    code: "P1",
    source: { sourceId: SHA, page: 1 },
    material: { printed: "SS400", family: "SS", thickness: n(2) },
    views: [{ id: "A", type: "FLAT" }],
    contour: { topology: "PLATE", status: "PROVED", overallX: n(50), overallY: n(30) },
    features: [{ id: "H1", family: "HOLE", quantity: 1, diameter: n(6), status: "PROVED" }],
    bends: [],
    markings: [],
    handwriting: [],
    uncertainties: []
  }]);
  routeJob(job.jobId);
  return jobStore.buildGeometry(job.jobId, [{
    schema: "GEOMETRY_SOURCE_V1",
    jobId: job.jobId,
    code: "P1",
    sourceSha256: SHA,
    origin: "PDF_SOURCE",
    buildKind: "FLAT_SINGLE_FACE",
    faces: [{
      faceId: "F1",
      sourceView: "A",
      contour: [{x:0,y:0},{x:50,y:0},{x:50,y:30},{x:0,y:30}]
    }],
    faceOrder: ["F1"],
    bends: [],
    features: [{
      featureId: "H1",
      family: "HOLE",
      hostFace: "F1",
      geometries: [{ kind: "CIRCLE", center: {x:25,y:15}, diameter: 6 }]
    }],
    proofs: {}
  }]);
}

function qa(jobId: string) {
  return [{
    schema: "MANUFACTURING_QA_V1",
    jobId,
    code: "P1",
    checks: {
      contour_topology: "PASS",
      datum: "PASS",
      feature_count: "PASS",
      unfold: "N/A",
      containment: "PASS",
      bend_domain: "N/A",
      material_rules: "PASS",
      slot_semantics: "N/A"
    },
    foldBack: "N/A",
    approvedForExport: true
  }];
}

test("serializer payload is production-shaped and preserves hole geometry", () => {
  const job = readyJob();
  assert.equal(job.state, "GEOMETRY_READY");
  const payload = createExportPayload(job, qa(job.jobId));
  assert.equal(payload.parts.length, 1);
  assert.equal(payload.parts[0]?.status, "PASS");
  assert.equal(payload.parts[0]?.entities[0]?.role, "outer");
  assert.equal(payload.parts[0]?.entities[1]?.type, "CIRCLE");
  assert.equal(payload.parts[0]?.entities[1]?.radius, 3);
});

test("critical QA cannot be N/A", () => {
  const job = readyJob();
  const bad = qa(job.jobId);
  (bad[0]!.checks as any).datum = "N/A";
  assert.throws(() => createExportPayload(job, bad), /DXF_CRITICAL_QA_NOT_PASS/);
});

test("bent production export requires full fold-back PASS", () => {
  const job = readyJob();
  job.geometry[0]!.bendZones = [{
    bendId: "B1", x1: 10, x2: 12, yMin: 0, yMax: 30,
    sign: "POSITIVE", angleDeg: 90, nobi: 2
  }];
  const bad = qa(job.jobId);
  assert.throws(() => createExportPayload(job, bad), /DXF_BENT_QA_NOT_PASS/);
});
