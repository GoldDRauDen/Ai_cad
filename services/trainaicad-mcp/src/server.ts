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
import { bindSourceToJob, downloadUri, storeSource } from "./ingest.js";

const BASE64 = /^[A-Za-z0-9+/\s]*={0,2}$/;

function json(value: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }]
  };
}

export function buildServer(): McpServer {
  const server = new McpServer(
    { name: "TrainAiCad", version: "0.1.0" },
    { capabilities: { tools: {} } }
  );

  server.registerTool(
    "open_cad_job",
    {
      description:
        "Open an experimental TrainAiCad job from immutable source descriptors. AUTO remains NEW_PDF_TO_DXF even when a DATA/reference DXF is present.",
      inputSchema: z.object({
        drawing: SourceDescriptor,
        referenceDxf: SourceDescriptor.optional(),
        mode: JobModeRequested.default("AUTO")
      })
    },
    async ({ drawing, referenceDxf, mode }) => {
      const job = jobStore.create(drawing, referenceDxf, mode);
      return json(publicJob(job));
    }
  );

  server.registerTool(
    "submit_cad_evidence",
    {
      description:
        "Validate and store CAD_EVIDENCE_V1 produced from direct source inspection. DERIVED values require derivation provenance.",
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
        "Run deterministic V0.1 routing first, with optional non-authoritative Jev shadow status. Does not build geometry.",
      inputSchema: z.object({ jobId: z.string().min(1) })
    },
    async ({ jobId }) => json(publicJob(routeJob(jobId)))
  );

  server.registerTool(
    "get_cad_job",
    {
      description:
        "Read the current experimental job state, release pin, routes and flags. V0.1 never returns production PASS.",
      inputSchema: z.object({ jobId: z.string().min(1) })
    },
    async ({ jobId }) => json(publicJob(jobStore.get(jobId)))
  );

  server.registerTool(
    "ingest_cad_file",
    {
      description:
        "Ingest one PDF/image/DXF source file for ChatGPT/OpenAI MCP callers: inline base64 `data` or a downloadable `uri`. Signature/MIME/extension/size validation, SHA256, filename sanitization, immutable content-addressed storage. Role REFERENCE_DXF is stored separately and is never a hidden ruler for NEW_PDF_TO_DXF.",
      inputSchema: z.object({
        fileName: z.string().min(1),
        role: z.enum(["DRAWING", "REFERENCE_DXF"]).default("DRAWING"),
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
      if (jobId) {
        const job = jobStore.get(jobId); // unknown job fails closed before any binding
        bound = bindSourceToJob(job.jobId, role, stored);
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
        boundSources: bound
      });
    }
  );

  return server;
}
