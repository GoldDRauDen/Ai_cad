import { createHash } from "node:crypto";
import * as z from "zod/v4";
import {
  TechnicalNumber,
  type CadEvidenceV1,
  type CadJob,
  type JobMode
} from "./model.js";

export const Point2 = z.object({
  x: z.number().finite(),
  y: z.number().finite()
});
export type Point2 = z.infer<typeof Point2>;

const GateProof = z.object({
  evidenceRefs: z.array(z.string().min(1)).min(1)
});

const FaceGraphProofs = z.object({
  topologyLocked: GateProof,
  dimensionWitnessLocked: GateProof,
  featureOwnershipLocked: GateProof,
  faceOrderLocked: GateProof,
  bendSignLocked: GateProof,
  bendDomainLocked: GateProof,
  constraintsClosed: GateProof
});

const CircleGeometry = z.object({
  kind: z.literal("CIRCLE"),
  center: Point2,
  diameter: z.number().positive()
});

const SlotGeometry = z.object({
  kind: z.literal("SLOT"),
  center: Point2,
  overallLength: z.number().positive(),
  width: z.number().positive(),
  angleDeg: z.number().finite().default(0)
}).superRefine((v, ctx) => {
  if (v.overallLength < v.width) {
    ctx.addIssue({ code: "custom", message: "SLOT overallLength must be >= width" });
  }
});

const PolylineGeometry = z.object({
  kind: z.literal("POLYLINE"),
  closed: z.boolean(),
  points: z.array(Point2).min(2)
});

const LineGeometry = z.object({
  kind: z.literal("LINE"),
  start: Point2,
  end: Point2
});

export const LocalFeatureGeometry = z.discriminatedUnion("kind", [
  CircleGeometry,
  SlotGeometry,
  PolylineGeometry,
  LineGeometry
]);
export type LocalFeatureGeometry = z.infer<typeof LocalFeatureGeometry>;

const GeometryFeatureSource = z.object({
  featureId: z.string().min(1),
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
    "KEGAKI",
    "OTHER"
  ]),
  hostFace: z.string().min(1),
  geometries: z.array(LocalFeatureGeometry).min(1)
});

const GeometryFaceSource = z.object({
  faceId: z.string().min(1),
  sourceView: z.string().min(1),
  contour: z.array(Point2).min(3),
  outsideLength: TechnicalNumber.optional(),
  transverseWidth: TechnicalNumber.optional()
});

const GeometryBendSource = z.object({
  bendId: z.string().min(1),
  faceA: z.string().min(1),
  faceB: z.string().min(1),
  axis: z.enum(["X", "Y", "OTHER"]),
  sign: z.enum(["POSITIVE", "NEGATIVE"]),
  angleDeg: TechnicalNumber,
  nobi: TechnicalNumber
});

export const GeometrySourceV1 = z.object({
  schema: z.literal("GEOMETRY_SOURCE_V1"),
  jobId: z.string().min(1),
  code: z.string().min(1),
  sourceSha256: z.string().regex(/^[a-fA-F0-9]{64}$/),
  origin: z.enum(["PDF_SOURCE", "DATA_DXF"]),
  buildKind: z.enum(["FLAT_SINGLE_FACE", "LINEAR_CHAIN"]),
  faces: z.array(GeometryFaceSource).min(1),
  faceOrder: z.array(z.string().min(1)).min(1),
  bends: z.array(GeometryBendSource).default([]),
  features: z.array(GeometryFeatureSource).default([]),
  proofs: FaceGraphProofs.partial().default({})
});
export type GeometrySourceV1 = z.infer<typeof GeometrySourceV1>;

export type CanonicalFeature = {
  featureId: string;
  family: string;
  hostFace: string;
  instance: number;
  geometry: LocalFeatureGeometry;
};

export type CanonicalBendZone = {
  bendId: string;
  x1: number;
  x2: number;
  yMin: number;
  yMax: number;
  sign: "POSITIVE" | "NEGATIVE";
  angleDeg: number;
  nobi: number;
};

export type CanonicalGeometryV1 = {
  schema: "CANONICAL_GEOMETRY_V1";
  geometryId: string;
  jobId: string;
  code: string;
  units: "mm";
  buildKind: "FLAT_SINGLE_FACE" | "LINEAR_CHAIN";
  sourceMode: JobMode;
  sourceSha256: string;
  outerContours: Point2[][];
  features: CanonicalFeature[];
  bendZones: CanonicalBendZone[];
  faceMap: Array<{
    faceId: string;
    flatStartX?: number;
    flatEndX?: number;
  }>;
  qa: {
    polygonClosed: boolean;
    topologyClosed: boolean;
    faceGraphG1toG7: "NOT_APPLICABLE" | "PASS";
    foldBack: "NOT_APPLICABLE" | "STRUCTURAL_ONLY_V02";
    numericResidualMaxMm: number;
  };
  flags: string[];
};

export type GeometryBuildResult = {
  code: string;
  status: "READY" | "REVIEW_REQUIRED";
  geometry?: CanonicalGeometryV1;
  flags: string[];
};

function hashId(value: unknown): string {
  return createHash("sha256").update(JSON.stringify(value)).digest("hex").slice(0, 20);
}

function samePoint(a: Point2, b: Point2, eps = 1e-9): boolean {
  return Math.abs(a.x - b.x) <= eps && Math.abs(a.y - b.y) <= eps;
}

function orient(a: Point2, b: Point2, c: Point2): number {
  return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

function onSegment(a: Point2, b: Point2, p: Point2, eps = 1e-9): boolean {
  return Math.min(a.x, b.x) - eps <= p.x && p.x <= Math.max(a.x, b.x) + eps &&
    Math.min(a.y, b.y) - eps <= p.y && p.y <= Math.max(a.y, b.y) + eps &&
    Math.abs(orient(a, b, p)) <= eps;
}

function segmentsIntersect(a: Point2, b: Point2, c: Point2, d: Point2): boolean {
  const o1 = orient(a, b, c);
  const o2 = orient(a, b, d);
  const o3 = orient(c, d, a);
  const o4 = orient(c, d, b);
  const eps = 1e-9;

  if (((o1 > eps && o2 < -eps) || (o1 < -eps && o2 > eps)) &&
      ((o3 > eps && o4 < -eps) || (o3 < -eps && o4 > eps))) return true;

  return Math.abs(o1) <= eps && onSegment(a, b, c) ||
    Math.abs(o2) <= eps && onSegment(a, b, d) ||
    Math.abs(o3) <= eps && onSegment(c, d, a) ||
    Math.abs(o4) <= eps && onSegment(c, d, b);
}

function polygonArea(points: Point2[]): number {
  let area = 0;
  for (let i = 0; i < points.length; i++) {
    const a = points[i]!;
    const b = points[(i + 1) % points.length]!;
    area += a.x * b.y - b.x * a.y;
  }
  return area / 2;
}

function validateSimplePolygon(points: Point2[]): string[] {
  const flags: string[] = [];
  if (points.length < 3) return ["CONTOUR_TOO_FEW_POINTS"];
  if (Math.abs(polygonArea(points)) <= 1e-9) flags.push("CONTOUR_ZERO_AREA");

  for (let i = 0; i < points.length; i++) {
    const a = points[i]!;
    const b = points[(i + 1) % points.length]!;
    if (samePoint(a, b)) flags.push("CONTOUR_ZERO_LENGTH_EDGE");
  }

  for (let i = 0; i < points.length; i++) {
    const a1 = points[i]!;
    const a2 = points[(i + 1) % points.length]!;
    for (let j = i + 1; j < points.length; j++) {
      const adjacent =
        j === i ||
        j === (i + 1) % points.length ||
        i === (j + 1) % points.length;
      if (adjacent) continue;
      if (i === 0 && j === points.length - 1) continue;
      const b1 = points[j]!;
      const b2 = points[(j + 1) % points.length]!;
      if (segmentsIntersect(a1, a2, b1, b2)) flags.push("CONTOUR_SELF_INTERSECTION");
    }
  }
  return [...new Set(flags)];
}

function expectedGeometryAuthority(job: CadJob): {
  origin: "PDF_SOURCE" | "DATA_DXF";
  sha256: string;
} {
  if (job.mode === "PDF_DATA_RAW") {
    if (!job.dxf) throw new Error("GEOMETRY_AUTHORITY_MISSING_DATA_DXF");
    return { origin: "DATA_DXF", sha256: job.dxf.sha256 };
  }
  if (job.mode === "DIRECT_EXISTING_DXF_AUDIT") {
    throw new Error("GEOMETRY_BUILD_NOT_APPLICABLE_TO_DIRECT_AUDIT");
  }
  return { origin: "PDF_SOURCE", sha256: job.source.sha256 };
}

function evidenceForCode(job: CadJob, code: string): CadEvidenceV1 {
  const evidence = job.evidence.find((item) => item.code === code);
  if (!evidence) throw new Error(`GEOMETRY_EVIDENCE_NOT_FOUND: ${code}`);
  return evidence;
}

function routeForCode(job: CadJob, code: string) {
  const route = job.routes.find((item) => item.code === code);
  if (!route) throw new Error(`GEOMETRY_ROUTE_NOT_FOUND: ${code}`);
  return route;
}

function validateSourceIdentity(job: CadJob, source: GeometrySourceV1): string[] {
  const flags: string[] = [];
  const expected = expectedGeometryAuthority(job);
  if (source.origin !== expected.origin) {
    flags.push(`GEOMETRY_AUTHORITY_ORIGIN_MISMATCH:${source.origin}->${expected.origin}`);
  }
  if (source.sourceSha256.toLowerCase() !== expected.sha256.toLowerCase()) {
    flags.push("GEOMETRY_AUTHORITY_SHA_MISMATCH");
  }
  return flags;
}

function validateFaceIds(source: GeometrySourceV1): string[] {
  const flags: string[] = [];
  const ids = source.faces.map((f) => f.faceId);
  if (new Set(ids).size !== ids.length) flags.push("DUPLICATE_FACE_ID");
  if (new Set(source.faceOrder).size !== source.faceOrder.length) flags.push("DUPLICATE_FACE_ORDER_ID");
  if (source.faceOrder.length !== ids.length) flags.push("FACE_ORDER_COUNT_MISMATCH");
  const a = [...ids].sort().join("|");
  const b = [...source.faceOrder].sort().join("|");
  if (a !== b) flags.push("FACE_ORDER_MEMBERSHIP_MISMATCH");
  for (const feature of source.features) {
    if (!ids.includes(feature.hostFace)) flags.push(`FEATURE_HOST_FACE_UNKNOWN:${feature.featureId}`);
  }
  return flags;
}

function validateEvidenceFeatureOwnership(job: CadJob, source: GeometrySourceV1): string[] {
  const evidence = evidenceForCode(job, source.code);
  const flags: string[] = [];
  const byId = new Map(source.features.map((f) => [f.featureId, f] as const));
  for (const feature of evidence.features) {
    const sourceFeature = byId.get(feature.id);
    if (!sourceFeature) {
      flags.push(`FEATURE_GEOMETRY_MISSING:${feature.id}`);
      continue;
    }
    if (sourceFeature.family !== feature.family) {
      flags.push(`FEATURE_FAMILY_MISMATCH:${feature.id}`);
    }
    if (sourceFeature.geometries.length !== feature.quantity) {
      flags.push(`FEATURE_QUANTITY_MISMATCH:${feature.id}`);
    }
  }
  for (const marking of evidence.markings) {
    if (marking.family === "KEGAKI" || marking.family === "RIB") {
      const sourceFeature = byId.get(marking.id);
      if (!sourceFeature) {
        flags.push(`MARKING_GEOMETRY_MISSING:${marking.id}`);
        continue;
      }
      if (sourceFeature.family !== marking.family) {
        flags.push(`MARKING_FAMILY_MISMATCH:${marking.id}`);
      }
      if (sourceFeature.geometries.length !== marking.quantity) {
        flags.push(`MARKING_QUANTITY_MISMATCH:${marking.id}`);
      }
    }
  }
  return flags;
}

function buildFlat(job: CadJob, source: GeometrySourceV1): GeometryBuildResult {
  const flags = [
    ...validateSourceIdentity(job, source),
    ...validateFaceIds(source)
  ];
  const route = routeForCode(job, source.code);
  if (route.mode !== "FLAT_NO_BEND") flags.push("FLAT_SOURCE_ON_NONFLAT_ROUTE");
  if (source.faces.length !== 1 || source.faceOrder.length !== 1) flags.push("FLAT_REQUIRES_ONE_FACE");
  if (source.bends.length) flags.push("FLAT_CANNOT_HAVE_BENDS");

  const face = source.faces[0];
  if (face) flags.push(...validateSimplePolygon(face.contour));
  flags.push(...validateEvidenceFeatureOwnership(job, source));

  if (flags.length) return { code: source.code, status: "REVIEW_REQUIRED", flags: [...new Set(flags)] };

  const geometry: CanonicalGeometryV1 = {
    schema: "CANONICAL_GEOMETRY_V1",
    geometryId: `geo_${hashId(source)}`,
    jobId: job.jobId,
    code: source.code,
    units: "mm",
    buildKind: "FLAT_SINGLE_FACE",
    sourceMode: job.mode,
    sourceSha256: source.sourceSha256,
    outerContours: [face!.contour],
    features: source.features.flatMap((f) =>
      f.geometries.map((geometry, index) => ({
        featureId: f.featureId,
        family: f.family,
        hostFace: f.hostFace,
        instance: index + 1,
        geometry
      }))
    ),
    bendZones: [],
    faceMap: [{ faceId: face!.faceId }],
    qa: {
      polygonClosed: true,
      topologyClosed: true,
      faceGraphG1toG7: "NOT_APPLICABLE",
      foldBack: "NOT_APPLICABLE",
      numericResidualMaxMm: 0
    },
    flags: []
  };
  return { code: source.code, status: "READY", geometry, flags: [] };
}

function allBentProofsPresent(source: GeometrySourceV1): boolean {
  const p = source.proofs;
  return Boolean(
    p.topologyLocked &&
    p.dimensionWitnessLocked &&
    p.featureOwnershipLocked &&
    p.faceOrderLocked &&
    p.bendSignLocked &&
    p.bendDomainLocked &&
    p.constraintsClosed
  );
}

function buildLinearChain(job: CadJob, source: GeometrySourceV1): GeometryBuildResult {
  const flags = [
    ...validateSourceIdentity(job, source),
    ...validateFaceIds(source)
  ];
  const route = routeForCode(job, source.code);
  if (route.mode !== "BEND_UNFOLD") flags.push("LINEAR_CHAIN_REQUIRES_BEND_UNFOLD_ROUTE");
  if (!allBentProofsPresent(source)) flags.push("FACE_GRAPH_G1_G7_NOT_CLOSED");
  if (source.faces.length < 2) flags.push("LINEAR_CHAIN_REQUIRES_AT_LEAST_TWO_FACES");
  if (source.bends.length !== Math.max(0, source.faces.length - 1)) flags.push("BEND_COUNT_NOT_CHAIN_CLOSED");

  if (source.features.length) {
    flags.push("V02_BENT_FEATURE_TRANSFORM_NOT_IMPLEMENTED");
  }

  const ordered = source.faceOrder
    .map((id) => source.faces.find((f) => f.faceId === id))
    .filter((f): f is NonNullable<typeof f> => Boolean(f));

  const lengths = ordered.map((f) => f.outsideLength?.value);
  const widths = ordered.map((f) => f.transverseWidth?.value);
  if (lengths.some((v) => v === undefined || v <= 0)) flags.push("FACE_OUTSIDE_LENGTH_MISSING");
  if (widths.some((v) => v === undefined || v <= 0)) flags.push("FACE_TRANSVERSE_WIDTH_MISSING");

  const width0 = widths[0];
  if (width0 !== undefined && widths.some((v) => v !== undefined && Math.abs(v - width0) > 1e-9)) {
    flags.push("V02_LINEAR_CHAIN_REQUIRES_CONSTANT_WIDTH");
  }

  const bendByPair = new Map<string, GeometrySourceV1["bends"][number]>();
  for (const bend of source.bends) {
    if (bend.axis !== "X") flags.push(`V02_LINEAR_CHAIN_AXIS_UNSUPPORTED:${bend.bendId}`);
    if (bend.nobi.value < 0) flags.push(`NEGATIVE_NOBI:${bend.bendId}`);
    const key1 = `${bend.faceA}|${bend.faceB}`;
    const key2 = `${bend.faceB}|${bend.faceA}`;
    if (bendByPair.has(key1) || bendByPair.has(key2)) flags.push(`DUPLICATE_BEND_PAIR:${bend.bendId}`);
    bendByPair.set(key1, bend);
  }

  for (let i = 0; i < source.faceOrder.length - 1; i++) {
    const a = source.faceOrder[i]!;
    const b = source.faceOrder[i + 1]!;
    if (!bendByPair.has(`${a}|${b}`) && !bendByPair.has(`${b}|${a}`)) {
      flags.push(`CHAIN_ADJACENCY_BEND_MISSING:${a}->${b}`);
    }
  }

  if (flags.length) return { code: source.code, status: "REVIEW_REQUIRED", flags: [...new Set(flags)] };

  const numericLengths = lengths as number[];
  const width = width0 as number;
  const bendZones: CanonicalBendZone[] = [];
  const faceMap: CanonicalGeometryV1["faceMap"] = [];
  let cumulativeOutside = 0;
  let cumulativeNobi = 0;

  for (let i = 0; i < ordered.length; i++) {
    const face = ordered[i]!;
    const start = i === 0 ? 0 : cumulativeOutside - cumulativeNobi;
    cumulativeOutside += numericLengths[i]!;
    const end = cumulativeOutside - cumulativeNobi;
    faceMap.push({ faceId: face.faceId, flatStartX: start, flatEndX: end });

    if (i < ordered.length - 1) {
      const next = ordered[i + 1]!;
      const bend = bendByPair.get(`${face.faceId}|${next.faceId}`) ??
        bendByPair.get(`${next.faceId}|${face.faceId}`)!;
      const nobi = bend.nobi.value;
      const x2 = end;
      const x1 = x2 - nobi;
      bendZones.push({
        bendId: bend.bendId,
        x1,
        x2,
        yMin: 0,
        yMax: width,
        sign: bend.sign,
        angleDeg: bend.angleDeg.value,
        nobi
      });
      cumulativeNobi += nobi;
    }
  }

  const flatLength = cumulativeOutside - cumulativeNobi;
  if (!(flatLength > 0)) {
    return { code: source.code, status: "REVIEW_REQUIRED", flags: ["NONPOSITIVE_FLAT_LENGTH"] };
  }

  const geometry: CanonicalGeometryV1 = {
    schema: "CANONICAL_GEOMETRY_V1",
    geometryId: `geo_${hashId(source)}`,
    jobId: job.jobId,
    code: source.code,
    units: "mm",
    buildKind: "LINEAR_CHAIN",
    sourceMode: job.mode,
    sourceSha256: source.sourceSha256,
    outerContours: [[
      { x: 0, y: 0 },
      { x: flatLength, y: 0 },
      { x: flatLength, y: width },
      { x: 0, y: width }
    ]],
    features: [],
    bendZones,
    faceMap,
    qa: {
      polygonClosed: true,
      topologyClosed: true,
      faceGraphG1toG7: "PASS",
      foldBack: "STRUCTURAL_ONLY_V02",
      numericResidualMaxMm: 0
    },
    flags: []
  };

  return { code: source.code, status: "READY", geometry, flags: [] };
}

export function buildGeometrySource(job: CadJob, raw: unknown): GeometryBuildResult {
  const source = GeometrySourceV1.parse(raw);
  if (source.jobId !== job.jobId) {
    return { code: source.code, status: "REVIEW_REQUIRED", flags: ["GEOMETRY_JOB_MISMATCH"] };
  }
  evidenceForCode(job, source.code);
  routeForCode(job, source.code);

  return source.buildKind === "FLAT_SINGLE_FACE"
    ? buildFlat(job, source)
    : buildLinearChain(job, source);
}

export function buildJobGeometry(job: CadJob, rawSources: unknown[]): {
  results: GeometryBuildResult[];
  ready: CanonicalGeometryV1[];
  flags: string[];
} {
  if (job.mode === "DIRECT_EXISTING_DXF_AUDIT") {
    throw new Error("GEOMETRY_BUILD_NOT_APPLICABLE_TO_DIRECT_AUDIT");
  }
  if (!["ROUTED", "REVIEW_REQUIRED"].includes(job.state)) {
    throw new Error(`GEOMETRY_BUILD_NOT_ALLOWED_IN_STATE: ${job.state}`);
  }
  if (job.routes.some((route) => route.status !== "ROUTED")) {
    throw new Error("GEOMETRY_BUILD_BLOCKED_BY_ROUTING_REVIEW");
  }

  const parsed = rawSources.map((raw) => GeometrySourceV1.parse(raw));
  const codes = job.routes.map((r) => r.code).sort();
  const inputCodes = parsed.map((s) => s.code).sort();
  if (new Set(inputCodes).size !== inputCodes.length) throw new Error("DUPLICATE_GEOMETRY_CODE");
  if (codes.join("|") !== inputCodes.join("|")) {
    throw new Error("GEOMETRY_CODE_SET_MISMATCH");
  }

  const results = parsed.map((source) => buildGeometrySource(job, source));
  const ready = results.flatMap((r) => r.geometry ? [r.geometry] : []);
  const flags = results.flatMap((r) => r.flags.map((flag) => `${r.code}:${flag}`));
  return { results, ready, flags };
}
