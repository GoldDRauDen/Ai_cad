import { createHash, randomUUID } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { bindSourceToJob, dataRoot, type IngestResult, type SourceRole } from "./ingest.js";
import { jevStatus } from "./jev.js";
import {
  CadEvidenceV1,
  type CadEvidenceV1 as Evidence,
  type CadJob,
  type DxfRole,
  type JobMode,
  type JobModeRequested,
  type JobState,
  type PartClass,
  type ReleasePin,
  type RouteResult,
  type SourceDescriptor,
  type SourcePolicy
} from "./model.js";

function sha256(text: string): string {
  return createHash("sha256").update(text).digest("hex");
}

export function resolveRepoRoot(start = process.env.TRAINAICAD_REPO_ROOT ?? process.cwd()): string {
  let current = resolve(start);
  for (;;) {
    const entry = join(current, "AI_ENTRYPOINT.md");
    const skill = join(current, "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md");
    if (existsSync(entry) && existsSync(skill)) return current;
    const parent = dirname(current);
    if (parent === current) throw new Error("SKILL_FRESHNESS_UNVERIFIED: TrainAiCad repo root not found");
    current = parent;
  }
}

export function readReleasePin(repoRoot = resolveRepoRoot()): ReleasePin {
  const entrypoint = readFileSync(join(repoRoot, "AI_ENTRYPOINT.md"), "utf8");
  const currentSkill = readFileSync(
    join(repoRoot, "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"),
    "utf8"
  );

  const entryMatch = entrypoint.match(/Current production release is \*\*(V\d+\.\d+)\*\*/);
  const skillMatch = currentSkill.match(/^# SKILL_LISPCAD (V\d+\.\d+) PORTABLE/m);
  if (!entryMatch?.[1] || !skillMatch?.[1] || entryMatch[1] !== skillMatch[1]) {
    throw new Error("SKILL_FRESHNESS_UNVERIFIED: AI_ENTRYPOINT and CURRENT disagree");
  }

  return {
    release: entryMatch[1],
    entrypointSha256: sha256(entrypoint),
    currentSkillSha256: sha256(currentSkill)
  };
}

export const allowedTransitions: Readonly<Record<JobState, readonly JobState[]>> = {
  CREATED: ["SOURCE_READY"],
  SOURCE_READY: ["EVIDENCE_READY"],
  EVIDENCE_READY: ["ROUTED", "REVIEW_REQUIRED"],
  ROUTED: ["EVIDENCE_READY"],
  REVIEW_REQUIRED: ["EVIDENCE_READY"],
  GEOMETRY_READY: [],
  DXF_WRITTEN: [],
  DXF_READBACK: [],
  QA_COMPLETE: [],
  PRODUCTION_PASS: [],
  REVIEW_ONLY: [],
  VIEWS_ONLY: [],
  SOURCE_CONFLICT: []
};

export function assertTransition(from: JobState, to: JobState): void {
  if (!allowedTransitions[from].includes(to)) {
    throw new Error(`INVALID_JOB_TRANSITION: ${from} -> ${to}`);
  }
}

export function resolveJobMode(
  requested: JobModeRequested,
  hasDxf: boolean,
  declaredReference = false
): JobMode {
  if (requested === "AUTO") {
    if (declaredReference) {
      if (!hasDxf) throw new Error("TRAIN_REFERENCE requires DXF");
      return "TRAIN_REFERENCE";
    }
    return hasDxf ? "PDF_DATA_RAW" : "PDF_ONLY";
  }

  if (requested === "PDF_ONLY") {
    if (hasDxf) throw new Error("PDF_ONLY cannot include DXF; use AUTO/PDF_DATA_RAW/TRAIN_REFERENCE");
    return requested;
  }

  if (requested === "PDF_DATA_RAW") {
    if (!hasDxf) throw new Error("PDF_DATA_RAW requires DXF");
    if (declaredReference) throw new Error("PDF_DATA_RAW cannot use an explicitly declared reference DXF");
    return requested;
  }

  if (requested === "TRAIN_REFERENCE") {
    if (!hasDxf) throw new Error("TRAIN_REFERENCE requires DXF");
    return requested;
  }

  if (!hasDxf) throw new Error("DIRECT_EXISTING_DXF_AUDIT requires approved reference DXF");
  return "DIRECT_EXISTING_DXF_AUDIT";
}

export function sourcePolicyForMode(mode: JobMode): SourcePolicy {
  switch (mode) {
    case "PDF_ONLY":
      return {
        geometryAuthority: "PDF_OR_IMAGE",
        semanticAuthority: "PDF_OR_IMAGE",
        dxfUse: "NONE"
      };
    case "PDF_DATA_RAW":
      return {
        geometryAuthority: "DATA_DXF",
        semanticAuthority: "PDF_OR_IMAGE_CONTROL",
        dxfUse: "RAW_GEOMETRY"
      };
    case "TRAIN_REFERENCE":
      return {
        geometryAuthority: "PDF_OR_IMAGE_INDEPENDENT",
        semanticAuthority: "PDF_OR_IMAGE_INDEPENDENT",
        dxfUse: "AUDIT_ONLY"
      };
    case "DIRECT_EXISTING_DXF_AUDIT":
      return {
        geometryAuthority: "AI_DXF_VS_APPROVED_REFERENCE",
        semanticAuthority: "AUDIT_PAIR_FIRST_THEN_SOURCE",
        dxfUse: "GROUND_TRUTH_AUDIT"
      };
  }
}

function dxfRoleForMode(mode: JobMode): DxfRole | undefined {
  if (mode === "PDF_DATA_RAW") return "DATA_DXF";
  if (mode === "TRAIN_REFERENCE") return "TRAIN_REFERENCE";
  if (mode === "DIRECT_EXISTING_DXF_AUDIT") return "APPROVED_REFERENCE";
  return undefined;
}

/**
 * Source-mode invariant: a bound DXF source must be reflected by the job mode,
 * and `PDF_ONLY` may never coexist with a bound DXF. Returns the mode after the
 * binding (unchanged when the binding needs no reclassification) or throws.
 * Mode is reclassifiable only while the job is still SOURCE_READY; after
 * evidence is submitted the mode is locked and a mode-changing binding is
 * rejected instead.
 */
export function modeAfterBinding(mode: JobMode, state: JobState, role: SourceRole): JobMode {
  if (role === "DRAWING") return mode;

  let next: JobMode;
  if (role === "DATA_DXF") {
    if (mode === "PDF_ONLY") next = "PDF_DATA_RAW";
    else if (mode === "PDF_DATA_RAW") return mode;
    else throw new Error(`SOURCE_CONFLICT: DATA_DXF cannot bind to ${mode}`);
  } else if (role === "REFERENCE_DXF") {
    if (mode === "PDF_ONLY") next = "TRAIN_REFERENCE";
    else if (mode === "TRAIN_REFERENCE" || mode === "DIRECT_EXISTING_DXF_AUDIT") return mode;
    else throw new Error(`SOURCE_CONFLICT: REFERENCE_DXF cannot bind to ${mode}`);
  } else {
    // AI_DXF: fail-closed, only the direct audit mode accepts an AI-exported DXF
    if (mode === "DIRECT_EXISTING_DXF_AUDIT") return mode;
    throw new Error(`AI_DXF_NOT_ALLOWED_IN_${mode}`);
  }

  if (state !== "SOURCE_READY") throw new Error(`SOURCE_MODE_LOCKED: ${state}`);
  return next;
}

class JobStore {
  private jobs = new Map<string, CadJob>();

  private file(jobId: string): string {
    return join(dataRoot(), "jobs", `${jobId}.json`);
  }

  private persist(job: CadJob): void {
    mkdirSync(join(dataRoot(), "jobs"), { recursive: true });
    writeFileSync(this.file(job.jobId), JSON.stringify(job, null, 2));
  }

  private normalizePersisted(raw: unknown): CadJob {
    const legacy = raw as Omit<CadJob, "mode"> & {
      mode: JobMode | "NEW_PDF_TO_DXF";
      referenceDxf?: SourceDescriptor;
      sourcePolicy?: SourcePolicy;
    };

    if (legacy.mode === "NEW_PDF_TO_DXF") {
      const oldReference = legacy.referenceDxf;
      legacy.mode = oldReference ? "TRAIN_REFERENCE" : "PDF_ONLY";
      legacy.dxf = legacy.dxf ?? oldReference;
      legacy.dxfRole = oldReference ? "TRAIN_REFERENCE" : undefined;
      delete legacy.referenceDxf;
    }

    legacy.sourcePolicy = legacy.sourcePolicy ?? sourcePolicyForMode(legacy.mode as JobMode);
    return legacy as CadJob;
  }

  create(
    source: SourceDescriptor,
    dxf: SourceDescriptor | undefined,
    requested: JobModeRequested,
    declaredReference = false
  ): CadJob {
    const now = new Date().toISOString();
    const mode = resolveJobMode(requested, Boolean(dxf), declaredReference);
    const job: CadJob = {
      jobId: `cad_${randomUUID().replaceAll("-", "").slice(0, 16)}`,
      mode,
      sourcePolicy: sourcePolicyForMode(mode),
      state: "CREATED",
      production: readReleasePin(),
      source,
      dxf,
      dxfRole: dxfRoleForMode(mode),
      evidence: [],
      routes: [],
      flags: [],
      createdAt: now,
      updatedAt: now
    };
    this.jobs.set(job.jobId, job);
    this.persist(job);
    return this.transition(job.jobId, "SOURCE_READY");
  }

  get(jobId: string): CadJob {
    let job = this.jobs.get(jobId);
    if (!job) {
      const file = this.file(jobId);
      if (existsSync(file)) {
        job = this.normalizePersisted(JSON.parse(readFileSync(file, "utf8")));
        this.jobs.set(jobId, job);
        this.persist(job);
      }
    }
    if (!job) throw new Error(`JOB_NOT_FOUND: ${jobId}`);
    return job;
  }

  transition(jobId: string, next: JobState): CadJob {
    const job = this.get(jobId);
    assertTransition(job.state, next);
    job.state = next;
    job.updatedAt = new Date().toISOString();
    this.persist(job);
    return job;
  }

  submitEvidence(jobId: string, raw: unknown[]): CadJob {
    const job = this.get(jobId);
    if (!["SOURCE_READY", "ROUTED", "REVIEW_REQUIRED"].includes(job.state)) {
      throw new Error(`EVIDENCE_NOT_ACCEPTED_IN_STATE: ${job.state}`);
    }
    const parsed = raw.map((item) => CadEvidenceV1.parse(item));
    for (const item of parsed) {
      if (item.jobId !== jobId) throw new Error(`EVIDENCE_JOB_MISMATCH: ${item.jobId}`);
      if (item.source.sourceId !== (job.source.sourceId ?? job.source.sha256)) {
        throw new Error(`EVIDENCE_SOURCE_MISMATCH: ${item.code}`);
      }
    }
    const seen = new Set<string>();
    for (const item of parsed) {
      if (seen.has(item.code)) throw new Error(`DUPLICATE_CODE: ${item.code}`);
      seen.add(item.code);
    }
    job.evidence = parsed;
    job.routes = [];
    job.flags = [];
    if (job.state === "SOURCE_READY") return this.transition(jobId, "EVIDENCE_READY");
    job.state = "EVIDENCE_READY";
    job.updatedAt = new Date().toISOString();
    this.persist(job);
    return job;
  }

  setRoutes(jobId: string, routes: RouteResult[]): CadJob {
    const job = this.get(jobId);
    if (job.state !== "EVIDENCE_READY") {
      throw new Error(`ROUTING_NOT_ALLOWED_IN_STATE: ${job.state}`);
    }
    job.routes = routes;
    job.flags = routes
      .filter((r) => r.status === "REVIEW_REQUIRED")
      .map((r) => `${r.code}:ROUTING_REVIEW_REQUIRED`);
    return this.transition(jobId, job.flags.length ? "REVIEW_REQUIRED" : "ROUTED");
  }

  /**
   * Bind an ingested source and keep the source-mode invariant: the job mode,
   * source policy and dxf descriptor are reclassified (or the binding is
   * rejected) so `PDF_ONLY` can never carry a DXF source. Rejects before any
   * write, so a refused binding leaves both the job and the binding file alone.
   */
  bindSource(jobId: string, role: SourceRole, source: IngestResult): { job: CadJob; bound: Record<string, IngestResult> } {
    const job = this.get(jobId);
    const next = modeAfterBinding(job.mode, job.state, role);
    const bound = bindSourceToJob(jobId, role, source);
    if (next !== job.mode) {
      job.mode = next;
      job.sourcePolicy = sourcePolicyForMode(next);
      job.dxf = {
        fileName: source.fileName,
        sha256: source.sha256,
        mimeType: source.mimeType
      };
      job.dxfRole = dxfRoleForMode(next);
      job.updatedAt = new Date().toISOString();
      this.persist(job);
    }
    return { job, bound };
  }
}

export const jobStore = new JobStore();

const topologyModule: Partial<Record<Evidence["contour"]["topology"], string>> = {
  L_PROFILE: "skills/lispcad/topology/L_PROFILE.md",
  U_PROFILE: "skills/lispcad/topology/U_PROFILE.md",
  MULTI_FACE: "skills/lispcad/topology/MULTI_FACE_PROFILE.md",
  STEPPED_PROFILE: "skills/lispcad/topology/STEPPED_PROFILE.md"
};

const featureModules: Partial<Record<Evidence["features"][number]["family"], readonly string[]>> = {
  SLOT: ["skills/lispcad/features/SLOTS.md"],
  CURVED_SLOT: ["skills/lispcad/features/CURVED_SLOT.md"],
  HOLE: ["skills/lispcad/features/HOLES_TAPS.md"],
  TAP: ["skills/lispcad/features/HOLES_TAPS.md"],
  CHAMFER: ["skills/lispcad/features/CHAMFER_RADIUS.md"],
  RADIUS: ["skills/lispcad/features/CHAMFER_RADIUS.md"],
  FORMING: ["skills/lispcad/features/FORMING_FEATURES.md"],
  PIASU: [
    "skills/lispcad/features/HOLES_TAPS.md",
    "skills/lispcad/features/FORMING_FEATURES.md"
  ],
  SLIT_RELIEF: ["skills/lispcad/features/SLIT_RELIEF.md"],
  RIB: ["skills/lispcad/features/RIB.md"]
};

const structurallyBentTopologies = new Set<Evidence["contour"]["topology"]>([
  "L_PROFILE",
  "U_PROFILE",
  "MULTI_FACE",
  "STEPPED_PROFILE",
  "BOXMET"
]);

function unique(values: string[]): string[] {
  return [...new Set(values)];
}

function inferredFaceCount(evidence: Evidence): number | null {
  if (evidence.faceCount) return evidence.faceCount;
  switch (evidence.contour.topology) {
    case "PLATE": return 1;
    case "L_PROFILE": return 2;
    case "U_PROFILE": return 3;
    case "BOXMET": return 5;
    default: return null;
  }
}

function minimumBends(evidence: Evidence): number {
  switch (evidence.contour.topology) {
    case "L_PROFILE": return 1;
    case "U_PROFILE": return 2;
    case "BOXMET": return 4;
    case "MULTI_FACE":
    case "STEPPED_PROFILE":
      return 1;
    default:
      return 0;
  }
}

function classifyPart(evidence: Evidence, structurallyBent: boolean): PartClass {
  if (evidence.partClassHint) return evidence.partClassHint;
  if (!structurallyBent) return "FLAT_NO_BEND";
  switch (evidence.contour.topology) {
    case "L_PROFILE": return "SINGLE_BEND_L";
    case "U_PROFILE": return "DOUBLE_BEND_U";
    case "MULTI_FACE": return "MULTI_FACE_ORTHOGONAL";
    case "STEPPED_PROFILE": return "STEPPED_BENT";
    case "BOXMET": return "BOX_4_FLANGE";
    default: return "OTHER_PROVED_TOPOLOGY";
  }
}

function inventory(evidence: Evidence, structurallyBent: boolean): string[] {
  const values = ["CUT"];
  if (structurallyBent) values.push("BEND");
  for (const feature of evidence.features) {
    switch (feature.family) {
      case "HOLE":
      case "TAP":
        values.push("HOLE_TAP");
        break;
      case "SLOT":
        values.push("STRAIGHT_SLOT");
        break;
      case "CURVED_SLOT":
        values.push("CURVED_SLOT");
        break;
      case "PIASU":
        values.push("PIASU_PIERCING");
        break;
      case "SLIT_RELIEF":
        values.push("SLIT_RELIEF");
        break;
      case "RIB":
        values.push("RIB");
        break;
      case "CHAMFER":
      case "RADIUS":
        values.push("R_C_CHAMFER");
        break;
      case "FORMING":
        values.push("FORMING");
        break;
      case "CUTOUT":
        values.push("INNER_CUT");
        break;
      default:
        values.push("OTHER");
    }
  }
  for (const marking of evidence.markings) {
    if (marking.family === "KEGAKI") values.push("KEGAKI");
    if (marking.family === "RIB") values.push("RIB");
  }
  return unique(values);
}

export function routeEvidence(evidence: Evidence, sourceMode: JobMode = "PDF_ONLY"): RouteResult {
  const structurallyBent =
    evidence.bends.length > 0 ||
    structurallyBentTopologies.has(evidence.contour.topology);

  const faceCount = inferredFaceCount(evidence);
  const requiredBends = minimumBends(evidence);
  const missingFaceCount =
    ["MULTI_FACE", "STEPPED_PROFILE"].includes(evidence.contour.topology) &&
    faceCount === null;
  const missingBendProof =
    structurallyBent && (
      evidence.bends.length < requiredBends ||
      evidence.bends.some((bend) =>
        !bend.axis || !bend.sign || bend.sign === "UNKNOWN"
      )
    );

  const blocked =
    evidence.contour.status === "UNCERTAIN" ||
    evidence.features.some((f) => f.status === "UNCERTAIN") ||
    evidence.bends.some((b) => b.status === "UNCERTAIN") ||
    evidence.markings.some((m) => m.status === "UNCERTAIN") ||
    evidence.uncertainties.some((u) => u.blocking) ||
    missingFaceCount ||
    missingBendProof;

  const mode: RouteResult["mode"] = blocked
    ? "UNRESOLVED"
    : structurallyBent
      ? "BEND_UNFOLD"
      : "FLAT_NO_BEND";

  const modules = [
    "references/SOURCE_DATA_CLASSIFICATION.md",
    "references/MECHANICAL_CLASSIFIER.md",
    "skills/lispcad/core/DRAWING_READING.md",
    "skills/lispcad/core/DATUM_DIMENSION.md",
    "skills/lispcad/core/VALIDATION.md",
    "skills/lispcad/core/CAD_OUTPUT.md",
    structurallyBent
      ? "skills/lispcad/modes/BEND_UNFOLD.md"
      : "skills/lispcad/modes/FLAT_NO_BEND.md"
  ];

  const topology = topologyModule[evidence.contour.topology];
  if (topology) modules.push(topology);

  for (const feature of evidence.features) {
    const selected = featureModules[feature.family];
    if (selected) modules.push(...selected);
  }
  for (const marking of evidence.markings) {
    if (marking.family === "KEGAKI") modules.push("skills/lispcad/features/KEGAKI.md");
    if (marking.family === "RIB") modules.push("skills/lispcad/features/RIB.md");
  }

  const specialRules: string[] = [];
  if (structurallyBent) {
    specialRules.push("references/FACE_GRAPH_UNFOLD_PROTOCOL.md");
  }
  const acute = evidence.bends.some(
    (bend) => bend.status === "PROVED" && bend.angle.value < 85
  );
  if (acute) {
    specialRules.push(
      "references/ACUTE_BEND_LT85_METHOD.md",
      "references/ACUTE_BEND_LT85_FROM_SOURCE.md"
    );
  }
  if (evidence.contour.topology === "BOXMET") {
    specialRules.push("references/BOXMET_SLIT_RELIEF.md");
  }

  const loadedModules = unique([...modules, ...specialRules]);
  const partClass = classifyPart(evidence, structurallyBent);

  return {
    code: evidence.code,
    mode,
    topology: evidence.contour.topology,
    modules: unique(modules),
    specialRules: unique(specialRules),
    status: blocked ? "REVIEW_REQUIRED" : "ROUTED",
    mechanical: {
      sourceMode,
      partClass,
      faceCount,
      bendAxes: evidence.bends.map((bend) => ({
        bendId: bend.id,
        axis: bend.axis ?? "UNPROVED"
      })),
      bendAnglesAndSigns: evidence.bends.map((bend) => ({
        bendId: bend.id,
        angleDeg: bend.angle.value,
        sign: bend.sign ?? "UNPROVED"
      })),
      featureInventory: inventory(evidence, structurallyBent),
      evidenceStatus: blocked ? "REVIEW_REQUIRED" : "PROVED",
      loadedModules
    },
    jev: jevStatus()
  };
}

export function routeJob(jobId: string): CadJob {
  const job = jobStore.get(jobId);
  if (job.state !== "EVIDENCE_READY") {
    throw new Error(`ROUTING_NOT_ALLOWED_IN_STATE: ${job.state}`);
  }
  if (!job.evidence.length) throw new Error("NO_EVIDENCE");
  return jobStore.setRoutes(
    jobId,
    job.evidence.map((evidence) => routeEvidence(evidence, job.mode))
  );
}

export function publicJob(job: CadJob): Omit<CadJob, "evidence"> & { evidenceCount: number } {
  const { evidence, ...rest } = job;
  return { ...rest, evidenceCount: evidence.length };
}
