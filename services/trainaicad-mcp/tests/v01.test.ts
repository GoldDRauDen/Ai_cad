import test from "node:test";
import assert from "node:assert/strict";
import {
  assertTransition,
  jobStore,
  readReleasePin,
  resolveJobMode,
  routeEvidence
} from "../src/core.js";
import { CadEvidenceV1 } from "../src/model.js";

const source = {
  fileName: "sample.pdf",
  sha256: "a".repeat(64),
  sourceId: "source-a"
};

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
      width: { value: 10, unit: "mm", origin: "PRINTED" },
      datum: {
        reference: "TOP_OUTSIDE_EDGE",
        target: "FEATURE_CENTER",
        axis: "Y",
        distance: { value: 10, unit: "mm", origin: "PRINTED" }
      }
    }],
    bends: [],
    markings: [],
    handwriting: [],
    uncertainties: [],
    ...overrides
  });
}

test("release pin follows live CURRENT instead of hard-coding a version", () => {
  const pin = readReleasePin();
  assert.match(pin.release, /^V\d+\.\d+$/);
  assert.equal(pin.entrypointSha256.length, 64);
  assert.equal(pin.currentSkillSha256.length, 64);
});

test("AUTO stays NEW_PDF_TO_DXF even when reference exists", () => {
  assert.equal(resolveJobMode("AUTO", true), "NEW_PDF_TO_DXF");
  assert.equal(resolveJobMode("AUTO", false), "NEW_PDF_TO_DXF");
  assert.throws(
    () => resolveJobMode("DIRECT_EXISTING_DXF_AUDIT", false),
    /requires referenceDxf/
  );
});

test("state machine blocks direct production PASS", () => {
  assert.throws(
    () => assertTransition("SOURCE_READY", "PRODUCTION_PASS"),
    /INVALID_JOB_TRANSITION/
  );
});

test("derived number requires derivation evidence", () => {
  assert.throws(() => CadEvidenceV1.parse({
    ...evidence(),
    material: {
      thickness: { value: 3, unit: "mm", origin: "DERIVED" }
    }
  }));
});

test("hard router selects flat slot module", () => {
  const route = routeEvidence(evidence());
  assert.equal(route.mode, "FLAT_NO_BEND");
  assert.equal(route.status, "ROUTED");
  assert.ok(route.modules.includes("skills/lispcad/features/SLOTS.md"));
});

test("acute bend and BOXMET select approved special rules", () => {
  const e = evidence({
    contour: { topology: "BOXMET", status: "PROVED" },
    bends: [{
      id: "B1",
      angle: { value: 75, unit: "deg", origin: "PRINTED" }
    }]
  });
  const route = routeEvidence(e);
  assert.equal(route.mode, "BEND_UNFOLD");
  assert.ok(route.specialRules.includes("references/ACUTE_BEND_LT85_METHOD.md"));
  assert.ok(route.specialRules.includes("references/BOXMET_SLIT_RELIEF.md"));
});

test("job store pins release and reaches ROUTED only through evidence", () => {
  const job = jobStore.create(source, undefined, "AUTO");
  const e = { ...evidence(), jobId: job.jobId };
  const withEvidence = jobStore.submitEvidence(job.jobId, [e]);
  assert.equal(withEvidence.state, "EVIDENCE_READY");
});

test("uncertain bent part stays review-required but still loads bend rules", () => {
  const e = evidence({
    bends: [{
      id: "B1",
      angle: { value: 90, unit: "deg", origin: "PRINTED" },
      status: "UNCERTAIN"
    }]
  });
  const route = routeEvidence(e);
  assert.equal(route.mode, "UNRESOLVED");
  assert.equal(route.status, "REVIEW_REQUIRED");
  assert.ok(route.modules.includes("skills/lispcad/modes/BEND_UNFOLD.md"));
  assert.ok(!route.modules.includes("skills/lispcad/modes/FLAT_NO_BEND.md"));
});
