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

  return server;
}
