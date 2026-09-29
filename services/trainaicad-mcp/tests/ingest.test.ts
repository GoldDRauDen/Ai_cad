import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { createServer, type Server } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  bindSourceToJob,
  downloadUri,
  sanitizeFileName,
  sniffKind,
  storeSource
} from "../src/ingest.js";
import { jevStatus } from "../src/jev.js";
import { jobStore, readReleasePin } from "../src/core.js";

const dataDir = mkdtempSync(join(tmpdir(), "trainaicad-mcp-"));
process.env.TRAINAICAD_MCP_DATA = dataDir;

const PDF = Buffer.from("%PDF-1.7\n1 0 obj\n<< >>\nendobj\ntrailer\n%%EOF\n");
const PNG = Buffer.concat([
  Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
  Buffer.alloc(64, 1)
]);
const DXF = Buffer.from("0\nSECTION\n2\nENTITIES\n0\nENDSEC\n0\nEOF\n");

test("release pin fails closed when entrypoint and CURRENT disagree", () => {
  const root = mkdtempSync(join(tmpdir(), "trainaicad-root-"));
  mkdirSync(join(root, "skills/lispcad/portable"), { recursive: true });
  writeFileSync(join(root, "AI_ENTRYPOINT.md"), "Current production release is **V4.17**.\n");
  writeFileSync(
    join(root, "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"),
    "# SKILL_LISPCAD V4.18 PORTABLE\n"
  );
  assert.throws(() => readReleasePin(root), /SKILL_FRESHNESS_UNVERIFIED/);
});

test("sanitizeFileName strips traversal and enforces extension whitelist", () => {
  assert.equal(sanitizeFileName("../../etc/passwd.pdf"), "passwd.pdf");
  assert.equal(sanitizeFileName("C:\\temp\\drawing_056648.DXF"), "drawing_056648.DXF");
  assert.throws(() => sanitizeFileName("payload.exe"), /UNSUPPORTED_FILE_TYPE/);
  assert.throws(() => sanitizeFileName(".."), /INVALID_FILE_NAME/);
});

test("signature sniffing decides the kind, not the declared MIME", () => {
  assert.equal(sniffKind(PDF), "PDF");
  assert.equal(sniffKind(PNG), "IMAGE");
  assert.equal(sniffKind(DXF), "DXF");
  assert.equal(sniffKind(Buffer.from("plain text")), null);

  const ok = storeSource({ fileName: "drawing.pdf", bytes: PDF }, "DRAWING");
  assert.equal(ok.kind, "PDF");
  assert.equal(ok.sha256.length, 64);
  assert.ok(existsSync(ok.storedPath));
  // content-addressed write is idempotent, never rewritten
  assert.equal(storeSource({ fileName: "drawing.pdf", bytes: PDF }, "DRAWING").sha256, ok.sha256);

  assert.throws(
    () => storeSource({ fileName: "drawing.pdf", bytes: PDF, mimeType: "image/png" }, "DRAWING"),
    /MIME_SIGNATURE_MISMATCH/
  );
  assert.throws(() => storeSource({ fileName: "drawing.dxf", bytes: PDF }, "DRAWING"), /EXTENSION_SIGNATURE_MISMATCH/);
  assert.throws(() => storeSource({ fileName: "drawing.pdf", bytes: Buffer.alloc(0) }, "DRAWING"), /EMPTY_SOURCE_FILE/);
  assert.throws(() => storeSource({ fileName: "drawing.pdf", bytes: Buffer.from("nope") }, "DRAWING"), /UNKNOWN_FILE_SIGNATURE/);

  const previous = process.env.TRAINAICAD_MAX_SOURCE_BYTES;
  process.env.TRAINAICAD_MAX_SOURCE_BYTES = "8";
  try {
    assert.throws(() => storeSource({ fileName: "drawing.pdf", bytes: PDF }, "DRAWING"), /SOURCE_TOO_LARGE/);
  } finally {
    if (previous === undefined) delete process.env.TRAINAICAD_MAX_SOURCE_BYTES;
    else process.env.TRAINAICAD_MAX_SOURCE_BYTES = previous;
  }
});

test("reference DXF binds separately from the drawing and is immutable per job", () => {
  const job = jobStore.create({ fileName: "a.pdf", sha256: "b".repeat(64) }, undefined, "AUTO");
  const drawing = storeSource({ fileName: "a.pdf", bytes: PDF }, "DRAWING");
  const reference = storeSource({ fileName: "ref.dxf", bytes: DXF }, "REFERENCE_DXF");

  const bound = bindSourceToJob(job.jobId, "DRAWING", drawing);
  bindSourceToJob(job.jobId, "REFERENCE_DXF", reference);
  assert.equal(bound.DRAWING?.sha256, drawing.sha256);
  assert.notEqual(
    join(dataDir, "sources", "DRAWING", drawing.sha256.slice(0, 2), `${drawing.sha256}.pdf`),
    join(dataDir, "sources", "REFERENCE_DXF", reference.sha256.slice(0, 2), `${reference.sha256}.dxf`)
  );

  assert.throws(
    () => bindSourceToJob(job.jobId, "DRAWING", reference),
    /SOURCE_ALREADY_BOUND/
  );
  assert.throws(
    () => bindSourceToJob("cad_0000000000000000", "DRAWING", drawing),
    /INVALID_JOB_ID|JOB_NOT_FOUND/
  );
});

test("jobs persist to the filesystem independent of the chat session", () => {
  const job = jobStore.create({ fileName: "p.pdf", sha256: "c".repeat(64) }, undefined, "AUTO");
  const file = join(dataDir, "jobs", `${job.jobId}.json`);
  assert.ok(existsSync(file));
  const onDisk = JSON.parse(readFileSync(file, "utf8"));
  assert.equal(onDisk.jobId, job.jobId);
  assert.equal(onDisk.state, "SOURCE_READY");
  assert.equal(onDisk.mode, "NEW_PDF_TO_DXF");
});

test("Jev stays advisory: missing key never blocks routing status", () => {
  const previousKey = process.env.TYPESAFE_API_KEY;
  const previousMode = process.env.JEV_MODE;
  delete process.env.TYPESAFE_API_KEY;
  try {
    process.env.JEV_MODE = "disabled";
    const off = jevStatus();
    assert.equal(off.configured, false);
    assert.equal(off.verdict, "UNAVAILABLE");

    process.env.JEV_MODE = "shadow";
    const shadow = jevStatus();
    assert.equal(shadow.verdict, "UNAVAILABLE");
    assert.match(shadow.detail, /TYPESAFE_API_KEY/);

    process.env.TYPESAFE_API_KEY = "test-key";
    process.env.JEV_MODE = "shadow";
    const keyed = jevStatus();
    assert.equal(keyed.configured, true);
    assert.equal(keyed.verdict, "UNAVAILABLE"); // V0.1 never calls Jev
  } finally {
    if (previousKey === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previousKey;
    if (previousMode === undefined) delete process.env.JEV_MODE;
    else process.env.JEV_MODE = previousMode;
  }
});

test("download guards scheme, private addresses and size", async () => {
  await assert.rejects(() => downloadUri("file:///etc/passwd"), /UNSUPPORTED_URI_SCHEME/);
  await assert.rejects(() => downloadUri("http://127.0.0.1:9/a.pdf"), /PRIVATE_ADDRESS_BLOCKED/);

  const server: Server = createServer((req, res) => {
    if (req.url === "/big") {
      res.writeHead(200, { "content-type": "application/pdf" });
      res.end(Buffer.alloc(4096, 0x25));
      return;
    }
    res.writeHead(200, { "content-type": "application/pdf" });
    res.end(PDF);
  });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  const port = typeof address === "object" && address ? address.port : 0;
  try {
    const bytes = await downloadUri(`http://127.0.0.1:${port}/a.pdf`, { allowPrivate: true });
    assert.equal(bytes.equals(PDF), true);

    const previous = process.env.TRAINAICAD_MAX_SOURCE_BYTES;
    process.env.TRAINAICAD_MAX_SOURCE_BYTES = "64";
    try {
      await assert.rejects(
        () => downloadUri(`http://127.0.0.1:${port}/big`, { allowPrivate: true }),
        /SOURCE_TOO_LARGE/
      );
    } finally {
      if (previous === undefined) delete process.env.TRAINAICAD_MAX_SOURCE_BYTES;
      else process.env.TRAINAICAD_MAX_SOURCE_BYTES = previous;
    }
  } finally {
    await new Promise<void>((resolve, reject) => server.close((error) => (error ? reject(error) : resolve())));
  }
});
