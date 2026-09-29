import { McpServer } from "@modelcontextprotocol/server";
import * as z from "zod/v4";
import {
  CadEvidenceV1,
  JobModeRequested,
  SourceDescriptor
} from "./model.js";
import {
  jobStore,
  publicJob,
  routeJob
} from "./core.js";
import { downloadUri, storeSource } from "./ingest.js";
import { GeometrySourceV1 } from "./geometry.js";

const BASE64 = /^[A-Za-z0-9+/\s]*={0,2}$/;

function json(value: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }]
  };
}

export function buildServer(): McpServer {
  const server = new McpServer(
    { name: "TrainAiCad", version: "0.2.0" },
    { capabilities: { tools: {} } }
  );

  server.registerTool(
    "open_cad_job",
    {
      description:
        "Open a TrainAiCad V0.1.1 job with V4.20 source classification. AUTO+generic dxf => PDF_DATA_RAW; AUTO+explicit referenceDxf => TRAIN_REFERENCE; no DXF => PDF_ONLY.",
      inputSchema: z.object({
        drawing: SourceDescriptor,
        dxf: SourceDescriptor.optional(),
        referenceDxf: SourceDescriptor.optional(),
        mode: JobModeRequested.default("AUTO")
      })
    },
    async ({ drawing, dxf, referenceDxf, mode }) => {
      if (dxf && referenceDxf) throw new Error("PROVIDE_ONLY_ONE_OF_DXF_OR_REFERENCEDXF");
      const attachedDxf = dxf ?? referenceDxf;
      const job = jobStore.create(drawing, attachedDxf, mode, Boolean(referenceDxf));
      return json(publicJob(job));
    }
  );

  server.registerTool(
    "submit_cad_evidence",
    {
      description:
        "Validate and store CAD_EVIDENCE_V1 produced from source inspection. DERIVED values require derivedFrom[] and rule; bent evidence may include faceCount, bend axis and signed fold direction.",
      inputSchema: z.object({
        jobId: z.string().min(1),
        evidence: z.array(CadEvidenceV1).min(1)
      })
    },
    async ({ jobId, evidence }) => {
      const job = jobStore.submitEvidence(jobId, evidence);
      return json(publicJob(job));
    }
  );

  server.registerTool(
    "route_cad_parts",
    {
      description:
        "Run V4.20 source/mechanical routing. Loads source classification, mechanical classifier, feature modules and FACE_GRAPH for bent/multi-face parts. Jev remains advisory.",
      inputSchema: z.object({ jobId: z.string().min(1) })
    },
    async ({ jobId }) => json(publicJob(routeJob(jobId)))
  );

  server.registerTool(
    "build_canonical_geometry",
    {
      description:
        "Build deterministic CANONICAL_GEOMETRY_V1 from source-authorized GEOMETRY_SOURCE_V1. V0.2 supports proved flat single-face geometry and proved constant-width linear bend chains; unsupported/missing constraints fail to REVIEW_REQUIRED.",
      inputSchema: z.object({
        jobId: z.string().min(1),
        geometrySources: z.array(GeometrySourceV1).min(1)
      })
    },
    async ({ jobId, geometrySources }) =>
      json(publicJob(jobStore.buildGeometry(jobId, geometrySources)))
  );

  server.registerTool(
    "get_cad_job",
    {
      description:
        "Read current experimental job state, release pin, source policy, routes, canonical geometry and flags. V0.2 still has no DXF/production PASS path.",
      inputSchema: z.object({ jobId: z.string().min(1) })
    },
    async ({ jobId }) => json(publicJob(jobStore.get(jobId)))
  );

  server.registerTool(
    "ingest_cad_file",
    {
      description:
        "Ingest one PDF/image/DXF source: inline base64 data or downloadable http(s) URI. Supports DRAWING, DATA_DXF, REFERENCE_DXF and AI_DXF roles with immutable content-addressed storage.",
      inputSchema: z.object({
        fileName: z.string().min(1),
        role: z.enum(["DRAWING", "DATA_DXF", "REFERENCE_DXF", "AI_DXF"]).default("DRAWING"),
        data: z.string().min(1).optional(),
        uri: z.string().min(1).optional(),
        mimeType: z.string().min(1).optional(),
        jobId: z.string().min(1).optional()
      })
    },
    async ({ fileName, role, data, uri, mimeType, jobId }) => {
      if (Boolean(data) === Boolean(uri)) {
        throw new Error("PROVIDE_EXACTLY_ONE_OF_DATA_OR_URI");
      }
      let bytes: Buffer;
      if (data) {
        if (!BASE64.test(data)) throw new Error("INVALID_BASE64");
        bytes = Buffer.from(data.replace(/\s+/g, ""), "base64");
      } else {
        bytes = await downloadUri(uri as string);
      }

      const stored = storeSource({ fileName, bytes, mimeType }, role);
      let bound: Record<string, unknown> | null = null;
      let jobMode: string | null = null;
      if (jobId) {
        const result = jobStore.bindSource(jobId, role, stored); // reclassifies or rejects before writing
        bound = result.bound;
        jobMode = result.job.mode;
      }
      return json({
        role,
        kind: stored.kind,
        bytes: stored.bytes,
        source: {
          fileName: stored.fileName,
          sha256: stored.sha256,
          mimeType: stored.mimeType
        },
        storedPath: `sources/${role}/${stored.sha256.slice(0, 2)}/${stored.sha256}${stored.fileName.match(/\.[^.]+$/)?.[0] ?? ""}`,
        boundToJob: jobId ?? null,
        jobMode,
        boundSources: bound
      });
    }
  );

  return server;
}
