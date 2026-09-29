import { createServer } from "node:http";
import {
  localhostHostValidation,
  localhostOriginValidation,
  toNodeHandler
} from "@modelcontextprotocol/node";
import { createMcpHandler } from "@modelcontextprotocol/server";
import { buildServer } from "./server.js";
import { readReleasePin } from "./core.js";

const port = Number.parseInt(process.env.TRAINAICAD_MCP_PORT ?? "8787", 10);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("Invalid TRAINAICAD_MCP_PORT");
}

// Fail closed before listening if CURRENT cannot be proven coherent.
const release = readReleasePin();

const handler = createMcpHandler(buildServer);
const nodeHandler = toNodeHandler(handler);
const validateHost = localhostHostValidation();
const validateOrigin = localhostOriginValidation();

createServer((req, res) => {
  const url = new URL(req.url ?? "/", "http://localhost");
  if (url.pathname !== "/mcp") {
    res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    res.end("Not Found");
    return;
  }
  if (!validateHost(req, res) || !validateOrigin(req, res)) return;
  void nodeHandler(req, res);
}).listen(port, "127.0.0.1", () => {
  console.error(
    `[TrainAiCad MCP] V0.2 canonical-geometry experimental; production release pin=${release.release}; http://127.0.0.1:${port}/mcp`
  );
});
