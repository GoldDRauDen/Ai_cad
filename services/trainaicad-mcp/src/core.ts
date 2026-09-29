import { createHash, randomUUID } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import {
  CadEvidenceV1,
  type CadEvidenceV1 as Evidence,
  type CadJob,
  type JobMode,
  type JobModeRequested,
  type JobState,
  type ReleasePin,
  type RouteResult,
  type SourceDescriptor
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

const allowed: Readonly<Record<JobState, readonly JobState[]>> = {
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
  if (!allowed[from].includes(to)) {
    throw new Error(`INVALID_JOB_TRANSITION: ${from} -> ${to}`);
  }
}

export function resolveJobMode(
  requested: JobModeRequested,
  hasReference: boolean
): JobMode {
  if (requested === "DIRECT_EXISTING_DXF_AUDIT") {
    if (!hasReference) {
      throw new Error("DIRECT_EXISTING_DXF_AUDIT requires referenceDxf");
    }
    return requested;
  }
  // Critical source-authority guard: DATA/reference presence never changes AUTO
  // into direct audit. NEW drawings remain source-first.
  return "NEW_PDF_TO_DXF";
}

class JobStore {
  private jobs = new Map<string, CadJob>();

  create(source: SourceDescriptor, referenceDxf: SourceDescriptor | undefined, requested: JobModeRequested): CadJob {
    const now = new Date().toISOString();
    const job: CadJob = {
      jobId: `cad_${randomUUID().replaceAll("-", "").slice(0, 16)}`,
      mode: resolveJobMode(requested, Boolean(referenceDxf)),
      state: "CREATED",
      production: readReleasePin(),
      source,
      referenceDxf,
      evidence: [],
      routes: [],
      flags: [],
      createdAt: now,
      updatedAt: now
    };
    this.jobs.set(job.jobId, job);
    return this.transition(job.jobId, "SOURCE_READY");
  }

  get(jobId: string): CadJob {
    const job = this.jobs.get(jobId);
    if (!job) throw new Error(`JOB_NOT_FOUND: ${jobId}`);
    return job;
  }

  transition(jobId: string, next: JobState): CadJob {
    const job = this.get(jobId);
    assertTransition(job.state, next);
    job.state = next;
    job.updatedAt = new Date().toISOString();
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
}

export const jobStore = new JobStore();

const topologyModule: Partial<Record<Evidence["contour"]["topology"], string>> = {
  L_PROFILE: "skills/lispcad/topology/L_PROFILE.md",
  U_PROFILE: "skills/lispcad/topology/U_PROFILE.md",
  MULTI_FACE: "skills/lispcad/topology/MULTI_FACE_PROFILE.md",
  STEPPED_PROFILE: "skills/lispcad/topology/STEPPED_PROFILE.md"
};

const featureModules: Partial<Record<Evidence["features"][number]["family"], string>> = {
  SLOT: "skills/lispcad/features/SLOTS.md",
  HOLE: "skills/lispcad/features/HOLES_TAPS.md",
  TAP: "skills/lispcad/features/HOLES_TAPS.md",
  CHAMFER: "skills/lispcad/features/CHAMFER_RADIUS.md",
  RADIUS: "skills/lispcad/features/CHAMFER_RADIUS.md",
  FORMING: "skills/lispcad/features/FORMING_FEATURES.md"
};

function unique(values: string[]): string[] {
  return [...new Set(values)];
}

function jevShadow(_evidence: Evidence): RouteResult["jev"] {
  const mode = process.env.JEV_MODE ?? "disabled";
  if (mode === "mock") {
    return { mode, verdict: "MOCK_MATCH", detail: "V0.1 mock only; hard router remains authoritative" };
  }
  return {
    mode,
    verdict: "UNAVAILABLE",
    detail: mode === "shadow"
      ? "V0.1 shadow contract is present; network Jev client intentionally not configured"
      : "Jev disabled"
  };
}

export function routeEvidence(evidence: Evidence): RouteResult {
  const blocked =
    evidence.contour.status === "UNCERTAIN" ||
    evidence.features.some((f) => f.status === "UNCERTAIN") ||
    evidence.bends.some((b) => b.status === "UNCERTAIN") ||
    evidence.markings.some((m) => m.status === "UNCERTAIN") ||
    evidence.uncertainties.some((u) => u.blocking);

  const hasBend = evidence.bends.length > 0;
  const mode: RouteResult["mode"] = blocked
    ? "UNRESOLVED"
    : hasBend
      ? "BEND_UNFOLD"
      : "FLAT_NO_BEND";

  const modules = [
    "skills/lispcad/core/DRAWING_READING.md",
    "skills/lispcad/core/DATUM_DIMENSION.md",
    "skills/lispcad/core/VALIDATION.md",
    "skills/lispcad/core/CAD_OUTPUT.md",
    hasBend
      ? "skills/lispcad/modes/BEND_UNFOLD.md"
      : "skills/lispcad/modes/FLAT_NO_BEND.md"
  ];

  const topology = topologyModule[evidence.contour.topology];
  if (topology) modules.push(topology);

  for (const feature of evidence.features) {
    const module = featureModules[feature.family];
    if (module) modules.push(module);
  }

  const specialRules: string[] = [];
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

  return {
    code: evidence.code,
    mode,
    topology: evidence.contour.topology,
    modules: unique(modules),
    specialRules: unique(specialRules),
    status: blocked ? "REVIEW_REQUIRED" : "ROUTED",
    jev: jevShadow(evidence)
  };
}

export function routeJob(jobId: string): CadJob {
  const job = jobStore.get(jobId);
  if (job.state !== "EVIDENCE_READY") {
    throw new Error(`ROUTING_NOT_ALLOWED_IN_STATE: ${job.state}`);
  }
  if (!job.evidence.length) throw new Error("NO_EVIDENCE");
  return jobStore.setRoutes(jobId, job.evidence.map(routeEvidence));
}

export function publicJob(job: CadJob): Omit<CadJob, "evidence"> & { evidenceCount: number } {
  const { evidence, ...rest } = job;
  return { ...rest, evidenceCount: evidence.length };
}
