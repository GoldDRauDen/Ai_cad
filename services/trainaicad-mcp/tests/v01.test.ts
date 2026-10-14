import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  allowedTransitions,
  assertTransition,
  jobStore,
  readReleasePin,
  resolveJobMode,
  resolveRepoRoot,
  routeEvidence,
  sourcePolicyForMode
} from "../src/core.js";
import { CadEvidenceV1 } from "../src/model.js";

process.env.TRAINAICAD_MCP_DATA = mkdtempSync(join(tmpdir(), "trainaicad-mcp-v011-"));

const source = {
  fileName: "sample.pdf",
  sha256: "a".repeat(64),
  sourceId: "source-a"
};
const genericDxf = { fileName: "data.dxf", sha256: "b".repeat(64) };
const referenceDxf = { fileName: "approved.dxf", sha256: "c".repeat(64) };

function evidence(overrides: Record<string, unknown> = {}) {
  return CadEvidenceV1.parse({
    schema: "CAD_EVIDENCE_V1",
    jobId: "cad_test",
    code: "056648",
    source: { sourceId: "source-a", page: 1 },
    material: {
      printed: "SS400",
      family: "SS",
      thickness: { value: 3, unit: "mm", origin: "PRINTED" }
    },
    views: [{ id: "A", type: "FLAT" }],
    contour: {
      topology: "PLATE",
      status: "PROVED",
      overallX: { value: 50, unit: "mm", origin: "PRINTED" },
      overallY: { value: 32, unit: "mm", origin: "PRINTED" }
    },
    features: [{
      id: "S1",
      family: "SLOT",
      quantity: 1,
      width: { value: 10, unit: "mm", origin: "PRINTED" }
    }],
    bends: [],
    markings: [],
    handwriting: [],
    uncertainties: [],
    ...overrides
  });
}

test("release pin follows ROUTER.yaml release (portable snapshot is not authority)", () => {
  const pin = readReleasePin();
  const router = readFileSync(join(resolveRepoRoot(), "skills/lispcad/router/ROUTER.yaml"), "utf8");
  assert.equal(pin.release, router.match(/^release:\s*(V\d+\.\d+)\s*$/m)?.[1]);
  assert.equal(pin.entrypointSha256.length, 64);
});

test("V4.20 source classification is deterministic", () => {
  assert.equal(resolveJobMode("AUTO", false), "PDF_ONLY");
  assert.equal(resolveJobMode("AUTO", true), "PDF_DATA_RAW");
  assert.equal(resolveJobMode("AUTO", true, true), "TRAIN_REFERENCE");
  assert.equal(resolveJobMode("PDF_DATA_RAW", true), "PDF_DATA_RAW");
  assert.equal(resolveJobMode("TRAIN_REFERENCE", true), "TRAIN_REFERENCE");
  assert.throws(() => resolveJobMode("PDF_DATA_RAW", false), /requires DXF/);
  assert.throws(() => resolveJobMode("DIRECT_EXISTING_DXF_AUDIT", false), /approved reference DXF/);
  assert.throws(() => resolveJobMode("PDF_ONLY", true), /cannot include DXF/);
});

test("V4.20 source authority split is encoded", () => {
  assert.deepEqual(sourcePolicyForMode("PDF_DATA_RAW"), {
    geometryAuthority: "DATA_DXF",
    semanticAuthority: "PDF_OR_IMAGE_CONTROL",
    dxfUse: "RAW_GEOMETRY"
  });
  assert.equal(sourcePolicyForMode("TRAIN_REFERENCE").dxfUse, "AUDIT_ONLY");
  assert.equal(sourcePolicyForMode("DIRECT_EXISTING_DXF_AUDIT").dxfUse, "GROUND_TRUTH_AUDIT");
});

test("state machine allows PRODUCTION_PASS only after QA_COMPLETE", () => {
  assert.throws(
    () => assertTransition("SOURCE_READY", "PRODUCTION_PASS"),
    /INVALID_JOB_TRANSITION/
  );
  for (const [from, targets] of Object.entries(allowedTransitions)) {
    const canPass = targets.includes("PRODUCTION_PASS");
    assert.equal(canPass, from === "QA_COMPLETE", `production path from ${from}`);
  }
});

test("derived number requires derivation evidence", () => {
  assert.throws(() => CadEvidenceV1.parse({
    ...evidence(),
    material: {
      thickness: { value: 3, unit: "mm", origin: "DERIVED" }
    }
  }));
});

test("flat router loads V4.20 source/mechanical references and slot module", () => {
  const route = routeEvidence(evidence(), "PDF_ONLY");
  assert.equal(route.mode, "FLAT_NO_BEND");
  assert.equal(route.status, "ROUTED");
  assert.equal(route.mechanical.sourceMode, "PDF_ONLY");
  assert.equal(route.mechanical.partClass, "FLAT_NO_BEND");
  assert.equal(route.mechanical.faceCount, 1);
  assert.ok(route.modules.includes("references/SOURCE_DATA_CLASSIFICATION.md"));
  assert.ok(route.modules.includes("references/MECHANICAL_CLASSIFIER.md"));
  assert.ok(route.modules.includes("skills/lispcad/features/SLOTS.md"));
});

test("V4.20 feature inventory routes independent manufacturing families", () => {
  const e = evidence({
    features: [
      { id: "C1", family: "CURVED_SLOT", quantity: 1 },
      { id: "P1", family: "PIASU", quantity: 2 },
      { id: "SL1", family: "SLIT_RELIEF", quantity: 1 },
      { id: "R1", family: "RIB", quantity: 1 }
    ],
    markings: [
      { id: "K1", family: "KEGAKI", quantity: 2, status: "PROVED" }
    ]
  });
  const route = routeEvidence(e, "PDF_DATA_RAW");
  for (const module of [
    "skills/lispcad/features/CURVED_SLOT.md",
    "skills/lispcad/features/HOLES_TAPS.md",
    "skills/lispcad/features/FORMING_FEATURES.md",
    "skills/lispcad/features/SLIT_RELIEF.md",
    "skills/lispcad/features/RIB.md",
    "skills/lispcad/features/KEGAKI.md"
  ]) {
    assert.ok(route.modules.includes(module), module);
  }
  for (const family of ["CURVED_SLOT", "PIASU_PIERCING", "SLIT_RELIEF", "RIB", "KEGAKI"]) {
    assert.ok(route.mechanical.featureInventory.includes(family), family);
  }
});

test("every proved bent/multi-face route loads BEND_UNFOLD and FACE_GRAPH", () => {
  const e = evidence({
    contour: { topology: "MULTI_FACE", status: "PROVED" },
    faceCount: 3,
    bends: [
      {
        id: "B1",
        angle: { value: 90, unit: "deg", origin: "PRINTED" },
        axis: "X",
        sign: "POSITIVE",
        status: "PROVED"
      },
      {
        id: "B2",
        angle: { value: 90, unit: "deg", origin: "PRINTED" },
        axis: "Y",
        sign: "NEGATIVE",
        status: "PROVED"
      }
    ]
  });
  const route = routeEvidence(e, "PDF_DATA_RAW");
  assert.equal(route.mode, "BEND_UNFOLD");
  assert.equal(route.status, "ROUTED");
  assert.ok(route.modules.includes("skills/lispcad/modes/BEND_UNFOLD.md"));
  assert.ok(route.specialRules.includes("references/FACE_GRAPH_UNFOLD_PROTOCOL.md"));
  assert.equal(route.mechanical.faceCount, 3);
  assert.equal(route.mechanical.evidenceStatus, "PROVED");
});

test("bent part without signed bend evidence is review-required but keeps bend rules", () => {
  const e = evidence({
    contour: { topology: "L_PROFILE", status: "PROVED" },
    bends: [{
      id: "B1",
      angle: { value: 90, unit: "deg", origin: "PRINTED" },
      status: "PROVED"
    }]
  });
  const route = routeEvidence(e);
  assert.equal(route.mode, "UNRESOLVED");
  assert.equal(route.status, "REVIEW_REQUIRED");
  assert.ok(route.modules.includes("skills/lispcad/modes/BEND_UNFOLD.md"));
  assert.ok(route.specialRules.includes("references/FACE_GRAPH_UNFOLD_PROTOCOL.md"));
  assert.equal(route.mechanical.bendAxes[0]?.axis, "UNPROVED");
});

test("acute BOXMET keeps acute and BOXMET rules plus FACE_GRAPH", () => {
  const bends = [75, 90, 90, 90].map((angle, i) => ({
    id: `B${i + 1}`,
    angle: { value: angle, unit: "deg" as const, origin: "PRINTED" as const },
    axis: i < 2 ? "X" as const : "Y" as const,
    sign: i % 2 ? "NEGATIVE" as const : "POSITIVE" as const,
    status: "PROVED" as const
  }));
  const e = evidence({
    contour: { topology: "BOXMET", status: "PROVED" },
    bends
  });
  const route = routeEvidence(e);
  assert.equal(route.mode, "BEND_UNFOLD");
  assert.equal(route.mechanical.partClass, "BOX_4_FLANGE");
  assert.equal(route.mechanical.faceCount, 5);
  assert.ok(route.specialRules.includes("references/FACE_GRAPH_UNFOLD_PROTOCOL.md"));
  assert.ok(route.specialRules.includes("references/ACUTE_BEND_LT85_METHOD.md"));
  assert.ok(route.specialRules.includes("references/BOXMET_SLIT_RELIEF.md"));
});

test("job store records raw DATA vs explicit training reference separately", () => {
  const raw = jobStore.create(source, genericDxf, "AUTO");
  assert.equal(raw.mode, "PDF_DATA_RAW");
  assert.equal(raw.dxfRole, "DATA_DXF");
  assert.equal(raw.sourcePolicy.geometryAuthority, "DATA_DXF");

  const ref = jobStore.create(source, referenceDxf, "AUTO", true);
  assert.equal(ref.mode, "TRAIN_REFERENCE");
  assert.equal(ref.dxfRole, "TRAIN_REFERENCE");
  assert.equal(ref.sourcePolicy.dxfUse, "AUDIT_ONLY");
});

test("job reaches routing only through accepted evidence", () => {
  const job = jobStore.create(source, undefined, "AUTO");
  const e = { ...evidence(), jobId: job.jobId };
  const withEvidence = jobStore.submitEvidence(job.jobId, [e]);
  assert.equal(withEvidence.state, "EVIDENCE_READY");
});
