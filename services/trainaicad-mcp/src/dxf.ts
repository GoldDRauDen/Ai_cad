import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import * as z from "zod/v4";
import type { CadJob } from "./model.js";
import type { CanonicalGeometryV1, LocalFeatureGeometry, Point2 } from "./geometry.js";
import { dataRoot } from "./ingest.js";

const CheckValue = z.enum(["PASS", "N/A"]);

export const ManufacturingQaV1 = z.object({
  schema: z.literal("MANUFACTURING_QA_V1"),
  jobId: z.string().min(1),
  code: z.string().min(1),
  checks: z.object({
    contour_topology: CheckValue,
    datum: CheckValue,
    feature_count: CheckValue,
    unfold: CheckValue,
    containment: CheckValue,
    bend_domain: CheckValue,
    material_rules: CheckValue,
    slot_semantics: CheckValue
  }),
  foldBack: z.enum(["PASS", "N/A"]),
  approvedForExport: z.literal(true)
});
export type ManufacturingQaV1 = z.infer<typeof ManufacturingQaV1>;

export type DxfOutputRecord = {
  fileName: string;
  relativePath: string;
  absolutePath: string;
  manifestPath: string;
  serializerContract: string;
  codeOrder: string[];
  writtenAt: string;
};

export type DxfAuditRecord = {
  ok: boolean;
  auditErrorCount: number;
  auditFixCount: number;
  insunits: number;
  entityCount: number;
  layers: Record<string, number>;
  entityTypes: Record<string, number>;
  labels: string[];
  aiMetaPlot: number | null;
  auditedAt: string;
};

function pythonExe(): string {
  return process.env.TRAINAICAD_PYTHON ?? (process.platform === "win32" ? "python" : "python3");
}

function bridgePath(repoRoot: string): string {
  return join(repoRoot, "services", "trainaicad-mcp", "bridge", "dxf_bridge.py");
}

function runBridge(repoRoot: string, args: string[]): any {
  const proc = spawnSync(pythonExe(), [bridgePath(repoRoot), ...args], {
    cwd: repoRoot,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024
  });
  if (proc.error) throw proc.error;
  if (proc.status !== 0) {
    throw new Error(`DXF_BRIDGE_FAILED: ${(proc.stderr || proc.stdout || "").trim()}`);
  }
  const lines = (proc.stdout || "").trim().split(/\r?\n/).filter(Boolean);
  if (!lines.length) throw new Error("DXF_BRIDGE_EMPTY_OUTPUT");
  return JSON.parse(lines.at(-1)!);
}

function signedArea(points: Point2[], bulges: number[]): number {
  let area = 0;
  for (let i = 0; i < points.length; i++) {
    const a = points[i]!;
    const b = points[(i + 1) % points.length]!;
    area += (a.x * b.y - b.x * a.y) / 2;
    const bulge = bulges[i] ?? 0;
    if (bulge) {
      const chord = Math.hypot(b.x - a.x, b.y - a.y);
      const theta = 4 * Math.atan(bulge);
      const sin = Math.sin(theta / 2);
      if (Math.abs(sin) < 1e-12) throw new Error("INVALID_BULGE");
      const radius = chord / (2 * Math.abs(sin));
      area += radius * radius * (theta - Math.sin(theta)) / 2;
    }
  }
  return area;
}

function reverseBulged(points: Point2[], bulges: number[]): { points: Point2[]; bulges: number[] } {
  const n = points.length;
  const rp = [...points].reverse();
  const rb = Array.from({ length: n }, (_, j) => {
    const originalEdge = (n - 2 - j + n) % n;
    return -(bulges[originalEdge] ?? 0);
  });
  return { points: rp, bulges: rb };
}

function lwpoly(points: Point2[], bulges: number[], role: string, clockwise: boolean) {
  if (points.length < 3) throw new Error(`DXF_POLYLINE_TOO_SHORT:${role}`);
  let p = points;
  let b = bulges.length === points.length ? bulges : points.map(() => 0);
  const area = signedArea(p, b);
  if ((clockwise && area > 0) || (!clockwise && area < 0)) {
    const reversed = reverseBulged(p, b);
    p = reversed.points;
    b = reversed.bulges;
  }
  return {
    type: "LWPOLYLINE",
    role,
    closed: true,
    vertices: p.map((pt, i) => [pt.x, pt.y, b[i] ?? 0])
  };
}

function rotatePoint(p: Point2, center: Point2, angleDeg: number): Point2 {
  const a = angleDeg * Math.PI / 180;
  const c = Math.cos(a);
  const s = Math.sin(a);
  const dx = p.x - center.x;
  const dy = p.y - center.y;
  return { x: center.x + dx * c - dy * s, y: center.y + dx * s + dy * c };
}

function stadium(g: Extract<LocalFeatureGeometry, {kind: "SLOT"}>) {
  const straight = g.overallLength - g.width;
  if (straight < -1e-9) throw new Error("SLOT_LENGTH_LT_WIDTH");
  const hx = Math.max(0, straight) / 2;
  const hy = g.width / 2;
  const raw = [
    { x: g.center.x - hx, y: g.center.y + hy },
    { x: g.center.x + hx, y: g.center.y + hy },
    { x: g.center.x + hx, y: g.center.y - hy },
    { x: g.center.x - hx, y: g.center.y - hy }
  ];
  const pts = raw.map((p) => rotatePoint(p, g.center, g.angleDeg));
  return lwpoly(pts, [0, -1, 0, -1], "slot", true);
}

function featureEntities(feature: CanonicalGeometryV1["features"][number]): any[] {
  const g = feature.geometry;
  const family = feature.family;

  if (g.kind === "CIRCLE") {
    if (!["HOLE", "TAP"].includes(family)) {
      throw new Error(`UNSAFE_CIRCLE_FAMILY:${feature.featureId}:${family}`);
    }
    return [{ type: "CIRCLE", role: "hole", center: [g.center.x, g.center.y], radius: g.diameter / 2 }];
  }

  if (g.kind === "SLOT") {
    if (!["SLOT", "CURVED_SLOT"].includes(family)) {
      throw new Error(`UNSAFE_SLOT_FAMILY:${feature.featureId}:${family}`);
    }
    return [stadium(g)];
  }

  if (g.kind === "POINT") {
    if (family !== "PIASU") throw new Error(`UNSAFE_POINT_FAMILY:${feature.featureId}:${family}`);
    return [{ type: "POINT", role: "through_piercing", color: 3, point: [g.point.x, g.point.y] }];
  }

  if (g.kind === "ARC") {
    if (family !== "SLIT_RELIEF") throw new Error(`UNSAFE_ARC_FAMILY:${feature.featureId}:${family}`);
    return [{
      type: "ARC", role: "relief", color: 3,
      center: [g.center.x, g.center.y], radius: g.radius,
      start_angle: g.startAngleDeg, end_angle: g.endAngleDeg
    }];
  }

  if (g.kind === "LINE") {
    if (family === "KEGAKI") {
      return [{ type: "LINE", role: "kegaki", color: 1, start: [g.start.x, g.start.y], end: [g.end.x, g.end.y] }];
    }
    if (family === "SLIT_RELIEF") {
      return [{ type: "LINE", role: "relief", color: 3, start: [g.start.x, g.start.y], end: [g.end.x, g.end.y] }];
    }
    throw new Error(`UNSAFE_LINE_FAMILY:${feature.featureId}:${family}`);
  }

  if (g.kind === "POLYLINE") {
    const bulges = g.bulges ?? g.points.map(() => 0);
    if (family === "CUTOUT") return [lwpoly(g.points, bulges, "cutout", true)];
    if (family === "SLOT" || family === "CURVED_SLOT") return [lwpoly(g.points, bulges, "slot", true)];
    if (family === "KEGAKI") {
      if (g.closed) throw new Error(`KEGAKI_CLOSED_POLYLINE_UNSUPPORTED:${feature.featureId}`);
      const lines = [];
      for (let i = 0; i < g.points.length - 1; i++) {
        const a = g.points[i]!, b = g.points[i + 1]!;
        if ((bulges[i] ?? 0) !== 0) throw new Error(`KEGAKI_BULGE_UNSUPPORTED:${feature.featureId}`);
        lines.push({ type: "LINE", role: "kegaki", color: 1, start: [a.x, a.y], end: [b.x, b.y] });
      }
      return lines;
    }
    if (family === "SLIT_RELIEF") {
      if (g.closed) throw new Error(`SLIT_CLOSED_POLYLINE_UNSUPPORTED:${feature.featureId}`);
      const ents = [];
      for (let i = 0; i < g.points.length - 1; i++) {
        const a = g.points[i]!, b = g.points[i + 1]!;
        const bulge = bulges[i] ?? 0;
        if (bulge === 0) {
          ents.push({ type: "LINE", role: "relief", color: 3, start: [a.x, a.y], end: [b.x, b.y] });
        } else {
          throw new Error(`SLIT_BULGED_POLYLINE_REQUIRES_EXPLICIT_ARC:${feature.featureId}`);
        }
      }
      return ents;
    }
    throw new Error(`UNSAFE_POLYLINE_FAMILY:${feature.featureId}:${family}`);
  }

  throw new Error(`UNSUPPORTED_FEATURE_GEOMETRY:${feature.featureId}`);
}

function buildSerializerPart(job: CadJob, geometry: CanonicalGeometryV1, qa: ManufacturingQaV1) {
  const evidence = job.evidence.find((e) => e.code === geometry.code);
  if (!evidence) throw new Error(`DXF_EVIDENCE_NOT_FOUND:${geometry.code}`);
  const material = evidence.material.printed ?? evidence.material.family;
  const thickness = evidence.material.thickness?.value;
  if (!material || !thickness || thickness <= 0) {
    throw new Error(`DXF_MATERIAL_THICKNESS_UNPROVED:${geometry.code}`);
  }

  for (const key of ["contour_topology", "datum", "feature_count", "containment", "material_rules"] as const) {
    if (qa.checks[key] !== "PASS") throw new Error(`DXF_CRITICAL_QA_NOT_PASS:${geometry.code}:${key}`);
  }
  if (geometry.bendZones.length && (qa.checks.unfold !== "PASS" || qa.checks.bend_domain !== "PASS" || qa.foldBack !== "PASS")) {
    throw new Error(`DXF_BENT_QA_NOT_PASS:${geometry.code}`);
  }

  if (geometry.outerContours.length !== 1) throw new Error(`DXF_REQUIRES_ONE_OUTER:${geometry.code}`);
  const outer = lwpoly(
    geometry.outerContours[0]!,
    geometry.outerBulges[0] ?? geometry.outerContours[0]!.map(() => 0),
    "outer",
    false
  );

  const entities: any[] = [outer];
  for (const feature of geometry.features) entities.push(...featureEntities(feature));
  for (const bend of geometry.bendZones) {
    entities.push(
      { type: "LINE", role: "bend", linetype: "DASHED", start: [bend.x1, bend.yMin], end: [bend.x1, bend.yMax] },
      { type: "LINE", role: "bend", linetype: "DASHED", start: [bend.x2, bend.yMin], end: [bend.x2, bend.yMax] }
    );
  }

  return {
    code: geometry.code,
    material,
    thickness_mm: thickness,
    status: "PASS",
    checks: qa.checks,
    entities
  };
}

export function createExportPayload(job: CadJob, rawQa: unknown[]) {
  if (job.state !== "GEOMETRY_READY") throw new Error(`DXF_EXPORT_NOT_ALLOWED_IN_STATE:${job.state}`);
  if (!job.geometry.length) throw new Error("DXF_EXPORT_NO_GEOMETRY");

  const qa = rawQa.map((x) => ManufacturingQaV1.parse(x));
  const qaByCode = new Map(qa.map((q) => [q.code, q] as const));
  if (qaByCode.size !== qa.length) throw new Error("DXF_DUPLICATE_QA_CODE");

  const codes = job.geometry.map((g) => g.code);
  if (codes.some((c) => !qaByCode.has(c)) || qa.some((q) => !codes.includes(q.code))) {
    throw new Error("DXF_QA_CODE_SET_MISMATCH");
  }
  for (const q of qa) {
    if (q.jobId !== job.jobId) throw new Error(`DXF_QA_JOB_MISMATCH:${q.code}`);
  }

  return {
    job_id: job.jobId,
    parts: job.geometry.map((g) => buildSerializerPart(job, g, qaByCode.get(g.code)!))
  };
}

export function exportWithBridge(job: CadJob, rawQa: unknown[], repoRoot: string): {
  output: DxfOutputRecord;
  qa: ManufacturingQaV1[];
} {
  const payload = createExportPayload(job, rawQa);
  const outDir = join(dataRoot(), "outputs", job.jobId);
  mkdirSync(outDir, { recursive: true });
  const inputPath = join(outDir, "serializer_input.json");
  writeFileSync(inputPath, JSON.stringify(payload, null, 2));

  const result = runBridge(repoRoot, ["export", inputPath, outDir]);
  if (!result?.ok || !result?.manifest?.filename || !result?.dxf_path || !result?.manifest_path) {
    throw new Error("DXF_EXPORT_BRIDGE_INVALID_RESULT");
  }
  const abs = resolve(result.dxf_path);
  if (!existsSync(abs)) throw new Error("DXF_EXPORT_FILE_MISSING");

  return {
    qa: rawQa.map((x) => ManufacturingQaV1.parse(x)),
    output: {
      fileName: result.manifest.filename,
      relativePath: join("outputs", job.jobId, result.manifest.filename),
      absolutePath: abs,
      manifestPath: resolve(result.manifest_path),
      serializerContract: result.manifest.contract,
      codeOrder: result.manifest.parts.map((p: any) => p.code),
      writtenAt: new Date().toISOString()
    }
  };
}

export function auditWithBridge(output: DxfOutputRecord, repoRoot: string): DxfAuditRecord {
  if (!existsSync(output.absolutePath)) throw new Error("DXF_AUDIT_FILE_MISSING");
  const result = runBridge(repoRoot, ["audit", output.absolutePath]);
  const audit: DxfAuditRecord = {
    ok: Boolean(result.ok),
    auditErrorCount: Number(result.audit_error_count ?? -1),
    auditFixCount: Number(result.audit_fix_count ?? -1),
    insunits: Number(result.insunits ?? 0),
    entityCount: Number(result.entity_count ?? 0),
    layers: result.layers ?? {},
    entityTypes: result.entity_types ?? {},
    labels: Array.isArray(result.labels) ? result.labels : [],
    aiMetaPlot: result.ai_meta_plot === null || result.ai_meta_plot === undefined ? null : Number(result.ai_meta_plot),
    auditedAt: new Date().toISOString()
  };

  if (!audit.ok || audit.auditErrorCount !== 0) throw new Error("DXF_READBACK_AUDIT_FAILED");
  if (audit.insunits !== 4) throw new Error("DXF_READBACK_UNITS_NOT_MM");
  if (audit.aiMetaPlot !== 0) throw new Error("DXF_READBACK_AI_META_PLOT_ENABLED");
  if (audit.labels.join("|") !== output.codeOrder.join("|")) throw new Error("DXF_READBACK_CODE_ORDER_MISMATCH");
  if (!audit.layers["0"]) throw new Error("DXF_READBACK_NO_MANUFACTURING_GEOMETRY");
  return audit;
}
