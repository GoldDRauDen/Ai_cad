import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { jobStore, routeJob } from "../src/core.js";

process.env.TRAINAICAD_MCP_DATA = mkdtempSync(join(tmpdir(), "trainaicad-mcp-v02-"));

const PDF_SHA = "d".repeat(64);
const DATA_SHA = "e".repeat(64);
const REF_SHA = "f".repeat(64);

const drawing = {
  fileName: "drawing.pdf",
  sha256: PDF_SHA,
  sourceId: "drawing-source"
};

function number(value: number, unit: "mm" | "deg" = "mm", origin = "PRINTED") {
  return { value, unit, origin };
}

function proofs() {
  const p = { evidenceRefs: ["page:1"] };
  return {
    topologyLocked: p,
    dimensionWitnessLocked: p,
    featureOwnershipLocked: p,
    faceOrderLocked: p,
    bendSignLocked: p,
    bendDomainLocked: p,
    constraintsClosed: p
  };
}

function openRoutedFlat(quantity = 2) {
  const job = jobStore.create(drawing, undefined, "AUTO");
  jobStore.submitEvidence(job.jobId, [{
    schema: "CAD_EVIDENCE_V1",
    jobId: job.jobId,
    code: "FLAT01",
    source: { sourceId: "drawing-source", page: 1 },
    material: { printed: "SS400", family: "SS", thickness: number(3) },
    views: [{ id: "A", type: "FLAT" }],
    contour: {
      topology: "PLATE",
      status: "PROVED",
      overallX: number(50),
      overallY: number(32)
    },
    features: [{
      id: "H1",
      family: "HOLE",
      quantity,
      diameter: number(6),
      status: "PROVED"
    }],
    bends: [],
    markings: [],
    handwriting: [],
    uncertainties: []
  }]);
  return routeJob(job.jobId);
}

function flatGeometry(jobId: string, holeCount = 2, sha = PDF_SHA, origin: "PDF_SOURCE" | "DATA_DXF" = "PDF_SOURCE") {
  return {
    schema: "GEOMETRY_SOURCE_V1",
    jobId,
    code: "FLAT01",
    sourceSha256: sha,
    origin,
    buildKind: "FLAT_SINGLE_FACE",
    faces: [{
      faceId: "F1",
      sourceView: "A",
      contour: [
        { x: 0, y: 0 },
        { x: 50, y: 0 },
        { x: 50, y: 32 },
        { x: 0, y: 32 }
      ]
    }],
    faceOrder: ["F1"],
    bends: [],
    features: [{
      featureId: "H1",
      family: "HOLE",
      hostFace: "F1",
      geometries: Array.from({ length: holeCount }, (_, i) => ({
        kind: "CIRCLE",
        center: { x: 10 + i * 30, y: 16 },
        diameter: 6
      }))
    }],
    proofs: {}
  };
}

function openRoutedLinear(dxf = false) {
  const data = dxf ? { fileName: "data.dxf", sha256: DATA_SHA } : undefined;
  const job = jobStore.create(drawing, data, "AUTO");
  jobStore.submitEvidence(job.jobId, [{
    schema: "CAD_EVIDENCE_V1",
    jobId: job.jobId,
    code: "L01",
    source: { sourceId: "drawing-source", page: 1 },
    material: { printed: "SS400", family: "SS", thickness: number(3) },
    views: [{ id: "FORMED", type: "FORMED" }],
    contour: { topology: "L_PROFILE", status: "PROVED" },
    faceCount: 2,
    features: [],
    bends: [{
      id: "B1",
      angle: number(90, "deg"),
      axis: "X",
      sign: "POSITIVE",
      nobi: { value: 4.4, unit: "mm", origin: "HANDWRITTEN" },
      status: "PROVED"
    }],
    markings: [],
    handwriting: [],
    uncertainties: []
  }]);
  return routeJob(job.jobId);
}

function linearGeometry(jobId: string, sha = PDF_SHA, origin: "PDF_SOURCE" | "DATA_DXF" = "PDF_SOURCE", axis: "X" | "Y" = "X") {
  return {
    schema: "GEOMETRY_SOURCE_V1",
    jobId,
    code: "L01",
    sourceSha256: sha,
    origin,
    buildKind: "LINEAR_CHAIN",
    faces: [
      {
        faceId: "F1",
        sourceView: "FORMED",
        contour: [{ x: 0, y: 0 }, { x: 150, y: 0 }, { x: 150, y: 25 }, { x: 0, y: 25 }],
        outsideLength: number(150),
        transverseWidth: number(25)
      },
      {
        faceId: "F2",
        sourceView: "FORMED",
        contour: [{ x: 0, y: 0 }, { x: 23.2, y: 0 }, { x: 23.2, y: 25 }, { x: 0, y: 25 }],
        outsideLength: number(23.2),
        transverseWidth: number(25)
      }
    ],
    faceOrder: ["F1", "F2"],
    bends: [{
      bendId: "B1",
      faceA: "F1",
      faceB: "F2",
      axis,
      sign: "POSITIVE",
      angleDeg: number(90, "deg"),
      nobi: { value: 4.4, unit: "mm", origin: "HANDWRITTEN" }
    }],
    features: [],
    proofs: proofs()
  };
}

test("flat canonical geometry preserves proved contour and all feature instances", () => {
  const routed = openRoutedFlat(2);
  const built = jobStore.buildGeometry(routed.jobId, [flatGeometry(routed.jobId)]);
  assert.equal(built.state, "GEOMETRY_READY");
  assert.equal(built.geometry.length, 1);
  assert.equal(built.geometry[0]?.outerContours[0]?.length, 4);
  assert.equal(built.geometry[0]?.features.length, 2);
  assert.equal(built.geometry[0]?.features[0]?.instance, 1);
  assert.equal(built.geometry[0]?.features[1]?.instance, 2);
  assert.equal(built.geometry[0]?.qa.faceGraphG1toG7, "NOT_APPLICABLE");
});

test("feature quantity mismatch goes REVIEW_REQUIRED and corrected geometry can retry", () => {
  const routed = openRoutedFlat(2);
  const failed = jobStore.buildGeometry(routed.jobId, [flatGeometry(routed.jobId, 1)]);
  assert.equal(failed.state, "REVIEW_REQUIRED");
  assert.ok(failed.flags.some((f) => f.includes("FEATURE_QUANTITY_MISMATCH:H1")));

  const fixed = jobStore.buildGeometry(routed.jobId, [flatGeometry(routed.jobId, 2)]);
  assert.equal(fixed.state, "GEOMETRY_READY");
  assert.equal(fixed.flags.length, 0);
});

test("linear chain deterministically computes flat length and double bend zone", () => {
  const routed = openRoutedLinear(false);
  const built = jobStore.buildGeometry(routed.jobId, [linearGeometry(routed.jobId)]);
  assert.equal(built.state, "GEOMETRY_READY");
  const g = built.geometry[0]!;
  const maxX = Math.max(...g.outerContours[0]!.map((p) => p.x));
  assert.ok(Math.abs(maxX - 168.8) < 1e-9);
  assert.equal(g.bendZones.length, 1);
  assert.ok(Math.abs(g.bendZones[0]!.x1 - 145.6) < 1e-9);
  assert.ok(Math.abs(g.bendZones[0]!.x2 - 150.0) < 1e-9);
  assert.equal(g.qa.faceGraphG1toG7, "PASS");
  assert.equal(g.qa.foldBack, "STRUCTURAL_ONLY_V02");
});

test("PDF_DATA_RAW accepts only the bound DATA DXF as geometry authority", () => {
  const routed = openRoutedLinear(true);
  assert.equal(routed.mode, "PDF_DATA_RAW");

  const wrong = jobStore.buildGeometry(
    routed.jobId,
    [linearGeometry(routed.jobId, PDF_SHA, "PDF_SOURCE")]
  );
  assert.equal(wrong.state, "REVIEW_REQUIRED");
  assert.ok(wrong.flags.some((f) => f.includes("GEOMETRY_AUTHORITY_ORIGIN_MISMATCH")));
  assert.ok(wrong.flags.some((f) => f.includes("GEOMETRY_AUTHORITY_SHA_MISMATCH")));

  const fixed = jobStore.buildGeometry(
    routed.jobId,
    [linearGeometry(routed.jobId, DATA_SHA, "DATA_DXF")]
  );
  assert.equal(fixed.state, "GEOMETRY_READY");
});

test("TRAIN_REFERENCE cannot use the approved reference DXF as construction input", () => {
  const job = jobStore.create(drawing, { fileName: "ref.dxf", sha256: REF_SHA }, "AUTO", true);
  jobStore.submitEvidence(job.jobId, [{
    schema: "CAD_EVIDENCE_V1",
    jobId: job.jobId,
    code: "FLAT01",
    source: { sourceId: "drawing-source", page: 1 },
    material: {},
    views: [{ id: "A", type: "FLAT" }],
    contour: { topology: "PLATE", status: "PROVED" },
    features: [{ id: "H1", family: "HOLE", quantity: 2, status: "PROVED" }],
    bends: [],
    markings: [],
    handwriting: [],
    uncertainties: []
  }]);
  routeJob(job.jobId);

  const failed = jobStore.buildGeometry(
    job.jobId,
    [flatGeometry(job.jobId, 2, REF_SHA, "DATA_DXF")]
  );
  assert.equal(failed.state, "REVIEW_REQUIRED");
  assert.ok(failed.flags.some((f) => f.includes("GEOMETRY_AUTHORITY_ORIGIN_MISMATCH")));
  assert.ok(failed.flags.some((f) => f.includes("GEOMETRY_AUTHORITY_SHA_MISMATCH")));
});

test("V0.2 fails closed on non-X linear chain instead of inventing a transform", () => {
  const routed = openRoutedLinear(false);
  const failed = jobStore.buildGeometry(
    routed.jobId,
    [linearGeometry(routed.jobId, PDF_SHA, "PDF_SOURCE", "Y")]
  );
  assert.equal(failed.state, "REVIEW_REQUIRED");
  assert.ok(failed.flags.some((f) => f.includes("V02_LINEAR_CHAIN_AXIS_UNSUPPORTED:B1")));
});

test("DIRECT_EXISTING_DXF_AUDIT has no canonical-build generation path", () => {
  const job = jobStore.create(
    { fileName: "ai.dxf", sha256: PDF_SHA, sourceId: "drawing-source" },
    { fileName: "approved.dxf", sha256: REF_SHA },
    "DIRECT_EXISTING_DXF_AUDIT"
  );
  assert.throws(
    () => jobStore.buildGeometry(job.jobId, []),
    /GEOMETRY_BUILD_NOT_APPLICABLE_TO_DIRECT_AUDIT|GEOMETRY_BUILD_NOT_ALLOWED_IN_STATE/
  );
});
