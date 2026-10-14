import * as z from "zod/v4";
import type { CanonicalGeometryV1, GeometrySourceV1 } from "./geometry.js";
import type { ManufacturingQaV1, DxfOutputRecord, DxfAuditRecord } from "./dxf.js";

export const Provenance = z.enum([
  "PRINTED",
  "DERIVED",
  "HANDWRITTEN",
  "REFERENCE_DXF",
  "USER_CONFIRMED",
  "AI_INFERENCE"
]);
export type Provenance = z.infer<typeof Provenance>;

export const TechnicalNumber = z.object({
  value: z.number().finite(),
  unit: z.enum(["mm", "deg"]).default("mm"),
  origin: Provenance,
  page: z.number().int().positive().optional(),
  view: z.string().min(1).optional(),
  derivedFrom: z.array(z.string().min(1)).optional(),
  rule: z.string().min(1).optional()
}).superRefine((v, ctx) => {
  if (v.origin === "DERIVED" && (!v.derivedFrom?.length || !v.rule)) {
    ctx.addIssue({
      code: "custom",
      message: "DERIVED values require derivedFrom[] and rule"
    });
  }
});
export type TechnicalNumber = z.infer<typeof TechnicalNumber>;

export const Datum = z.object({
  reference: z.enum([
    "LEFT_OUTSIDE_EDGE",
    "RIGHT_OUTSIDE_EDGE",
    "TOP_OUTSIDE_EDGE",
    "BOTTOM_OUTSIDE_EDGE",
    "CENTERLINE",
    "FEATURE_CENTER",
    "OTHER"
  ]),
  target: z.enum(["FEATURE_CENTER", "EDGE", "BEND_LINE", "OTHER"]),
  distance: TechnicalNumber,
  axis: z.enum(["X", "Y"]).optional()
});

export const Feature = z.object({
  id: z.string().min(1),
  family: z.enum([
    "SLOT",
    "CURVED_SLOT",
    "HOLE",
    "TAP",
    "CHAMFER",
    "RADIUS",
    "FORMING",
    "CUTOUT",
    "PIASU",
    "SLIT_RELIEF",
    "RIB",
    "OTHER"
  ]),
  quantity: z.number().int().positive(),
  width: TechnicalNumber.optional(),
  diameter: TechnicalNumber.optional(),
  radius: TechnicalNumber.optional(),
  callout: z.string().optional(),
  datum: Datum.optional(),
  status: z.enum(["PROVED", "UNCERTAIN"]).default("PROVED")
});

export const Bend = z.object({
  id: z.string().min(1),
  angle: TechnicalNumber,
  axis: z.enum(["X", "Y", "OTHER"]).optional(),
  sign: z.enum(["POSITIVE", "NEGATIVE", "UNKNOWN"]).optional(),
  rin: TechnicalNumber.optional(),
  nobi: TechnicalNumber.optional(),
  status: z.enum(["PROVED", "UNCERTAIN"]).default("PROVED")
});

export const PartClass = z.enum([
  "FLAT_NO_BEND",
  "SINGLE_BEND_L",
  "DOUBLE_BEND_U",
  "OFFSET_Z_JOG",
  "MULTI_FACE_ORTHOGONAL",
  "STEPPED_BENT",
  "BOX_4_FLANGE",
  "INSIDE_VIEW_ASSEMBLY",
  "MIRROR_PART",
  "OTHER_PROVED_TOPOLOGY"
]);
export type PartClass = z.infer<typeof PartClass>;

export const CadEvidenceV1 = z.object({
  schema: z.literal("CAD_EVIDENCE_V1"),
  jobId: z.string().min(1),
  code: z.string().min(1),
  source: z.object({
    sourceId: z.string().min(1),
    page: z.number().int().positive(),
    revision: z.string().nullable().optional()
  }),
  material: z.object({
    printed: z.string().min(1).optional(),
    family: z.string().min(1).optional(),
    thickness: TechnicalNumber.optional()
  }).default({}),
  views: z.array(z.object({
    id: z.string().min(1),
    type: z.enum(["FRONT", "SIDE", "TOP", "SECTION", "DETAIL", "FORMED", "FLAT", "OTHER"]),
    role: z.string().optional()
  })).default([]),
  contour: z.object({
    topology: z.enum([
      "PLATE",
      "L_PROFILE",
      "U_PROFILE",
      "MULTI_FACE",
      "STEPPED_PROFILE",
      "BOXMET",
      "UNKNOWN"
    ]),
    status: z.enum(["PROVED", "UNCERTAIN"]),
    overallX: TechnicalNumber.optional(),
    overallY: TechnicalNumber.optional()
  }),
  faceCount: z.number().int().positive().optional(),
  partClassHint: PartClass.optional(),
  features: z.array(Feature).default([]),
  bends: z.array(Bend).default([]),
  markings: z.array(z.object({
    id: z.string().min(1),
    family: z.enum(["KEGAKI", "RIB", "OTHER"]),
    quantity: z.number().int().positive(),
    status: z.enum(["PROVED", "UNCERTAIN"]).default("PROVED")
  })).default([]),
  handwriting: z.array(z.string()).default([]),
  uncertainties: z.array(z.object({
    code: z.string().min(1),
    evidence: z.string().min(1),
    blocking: z.boolean().default(true)
  })).default([])
});
export type CadEvidenceV1 = z.infer<typeof CadEvidenceV1>;

export const JobModeRequested = z.enum([
  "AUTO",
  "PDF_ONLY",
  "PDF_DATA_RAW",
  "TRAIN_REFERENCE",
  "DIRECT_EXISTING_DXF_AUDIT"
]);
export type JobModeRequested = z.infer<typeof JobModeRequested>;
export type JobMode = Exclude<JobModeRequested, "AUTO">;

export const JobState = z.enum([
  "CREATED",
  "SOURCE_READY",
  "EVIDENCE_READY",
  "ROUTED",
  "REVIEW_REQUIRED",
  "GEOMETRY_READY",
  "DXF_WRITTEN",
  "DXF_READBACK",
  "QA_COMPLETE",
  "PRODUCTION_PASS",
  "REVIEW_ONLY",
  "VIEWS_ONLY",
  "SOURCE_CONFLICT"
]);
export type JobState = z.infer<typeof JobState>;

export const SourceDescriptor = z.object({
  fileName: z.string().min(1),
  sha256: z.string().regex(/^[a-fA-F0-9]{64}$/),
  mimeType: z.string().optional(),
  sourceId: z.string().min(1).optional()
});
export type SourceDescriptor = z.infer<typeof SourceDescriptor>;

export type DxfRole = "DATA_DXF" | "TRAIN_REFERENCE" | "APPROVED_REFERENCE";

export type SourcePolicy = {
  geometryAuthority:
    | "PDF_OR_IMAGE"
    | "DATA_DXF"
    | "PDF_OR_IMAGE_INDEPENDENT"
    | "AI_DXF_VS_APPROVED_REFERENCE";
  semanticAuthority:
    | "PDF_OR_IMAGE"
    | "PDF_OR_IMAGE_CONTROL"
    | "PDF_OR_IMAGE_INDEPENDENT"
    | "AUDIT_PAIR_FIRST_THEN_SOURCE";
  dxfUse: "NONE" | "RAW_GEOMETRY" | "AUDIT_ONLY" | "GROUND_TRUTH_AUDIT";
};

export type ReleasePin = {
  release: string;
  entrypointSha256: string;
  currentSkillSha256: string;
};

export type MechanicalClassification = {
  sourceMode: JobMode;
  partClass: PartClass;
  faceCount: number | null;
  bendAxes: Array<{ bendId: string; axis: "X" | "Y" | "OTHER" | "UNPROVED" }>;
  bendAnglesAndSigns: Array<{
    bendId: string;
    angleDeg: number;
    sign: "POSITIVE" | "NEGATIVE" | "UNKNOWN" | "UNPROVED";
  }>;
  featureInventory: string[];
  evidenceStatus: "PROVED" | "REVIEW_REQUIRED";
  loadedModules: string[];
};

export type RouteResult = {
  code: string;
  mode: "FLAT_NO_BEND" | "BEND_UNFOLD" | "UNRESOLVED";
  topology: CadEvidenceV1["contour"]["topology"];
  modules: string[];
  specialRules: string[];
  status: "ROUTED" | "REVIEW_REQUIRED";
  mechanical: MechanicalClassification;
  jev: { mode: string; configured: boolean; verdict: "UNAVAILABLE" | "MOCK_MATCH"; detail: string };
};

export type CadJob = {
  jobId: string;
  mode: JobMode;
  sourcePolicy: SourcePolicy;
  state: JobState;
  production: ReleasePin;
  source: SourceDescriptor;
  dxf?: SourceDescriptor;
  dxfRole?: DxfRole;
  evidence: CadEvidenceV1[];
  routes: RouteResult[];
  geometrySources: GeometrySourceV1[];
  geometry: CanonicalGeometryV1[];
  manufacturingQa: ManufacturingQaV1[];
  dxfOutput?: DxfOutputRecord;
  dxfAudit?: DxfAuditRecord;
  flags: string[];
  createdAt: string;
  updatedAt: string;
};
