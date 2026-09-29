import { createHash } from "node:crypto";
import { lookup } from "node:dns/promises";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { isIP } from "node:net";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

export type SourceKind = "PDF" | "IMAGE" | "DXF";
export type SourceRole = "DRAWING" | "DATA_DXF" | "REFERENCE_DXF" | "AI_DXF";

const PACKAGE_ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

/** Local data root (jobs + immutable sources). Override with TRAINAICAD_MCP_DATA. */
export function dataRoot(): string {
  return process.env.TRAINAICAD_MCP_DATA ?? join(PACKAGE_ROOT, "data");
}

export function maxSourceBytes(): number {
  const raw = Number.parseInt(process.env.TRAINAICAD_MAX_SOURCE_BYTES ?? "", 10);
  return Number.isInteger(raw) && raw > 0 ? raw : 25 * 1024 * 1024;
}

const ALLOWED_EXT: Record<string, SourceKind> = {
  ".pdf": "PDF",
  ".png": "IMAGE",
  ".jpg": "IMAGE",
  ".jpeg": "IMAGE",
  ".tif": "IMAGE",
  ".tiff": "IMAGE",
  ".bmp": "IMAGE",
  ".webp": "IMAGE",
  ".dxf": "DXF"
};

const KIND_MIME: Record<SourceKind, readonly string[]> = {
  PDF: ["application/pdf"],
  IMAGE: ["image/png", "image/jpeg", "image/tiff", "image/bmp", "image/webp"],
  DXF: ["image/vnd.dxf", "application/dxf", "application/x-dxf", "application/octet-stream"]
};

/** Strip any path, control/illegal characters and reserved leading dots. */
export function sanitizeFileName(raw: string): string {
  const base = raw.split(/[\\/]/).pop() ?? "";
  const cleaned = base
    .replace(/[\u0000-\u001f\u007f<>:"|?*]/g, "")
    .replace(/^[.\s]+/, "")
    .trim()
    .slice(0, 120);
  if (!cleaned || !/^[\p{L}\p{N} ._()-]+$/u.test(cleaned) || cleaned.includes("..")) {
    throw new Error(`INVALID_FILE_NAME: ${JSON.stringify(raw)}`);
  }
  const ext = extname(cleaned).toLowerCase();
  if (!ALLOWED_EXT[ext]) throw new Error(`UNSUPPORTED_FILE_TYPE: ${ext || "(none)"}`);
  return cleaned;
}

function startsWith(bytes: Uint8Array, sig: number[], at = 0): boolean {
  if (bytes.length < at + sig.length) return false;
  return sig.every((b, i) => bytes[at + i] === b);
}

function ascii(bytes: Uint8Array, from = 0, to = bytes.length): string {
  return Buffer.from(bytes.subarray(from, to)).toString("latin1");
}

/** Magic-byte sniffing; declared MIME never decides the kind. */
export function sniffKind(bytes: Uint8Array): SourceKind | null {
  if (startsWith(bytes, [0x25, 0x50, 0x44, 0x46, 0x2d])) return "PDF";
  if (startsWith(bytes, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])) return "IMAGE";
  if (startsWith(bytes, [0xff, 0xd8, 0xff])) return "IMAGE";
  if (ascii(bytes, 0, 4) === "II*\u0000" || ascii(bytes, 0, 4) === "MM\u0000*") return "IMAGE";
  if (ascii(bytes, 0, 2) === "BM") return "IMAGE";
  if (ascii(bytes, 0, 4) === "RIFF" && ascii(bytes, 8, 12) === "WEBP") return "IMAGE";
  if (ascii(bytes, 0, 17) === "AutoCAD Binary DXF") return "DXF";

  const head = ascii(bytes, 0, Math.min(bytes.length, 2048)).replace(/^\uFEFF/, "");
  if (/^\s*(0|999)\s*\r?\n/.test(head) && /(SECTION|ENDSEC|ENTITIES|HEADER|TABLES)/.test(head)) {
    return "DXF";
  }
  return null;
}

export type IngestResult = {
  kind: SourceKind;
  bytes: number;
  fileName: string;
  mimeType: string;
  sha256: string;
  storedPath: string;
};

/**
 * Validate bytes, hash them and store immutably under data/sources/<role>/.
 * Same content is idempotent; content is never rewritten.
 */
export function storeSource(
  raw: { fileName: string; bytes: Buffer; mimeType?: string },
  role: SourceRole
): IngestResult {
  const fileName = sanitizeFileName(raw.fileName);
  if (raw.bytes.length === 0) throw new Error("EMPTY_SOURCE_FILE");
  if (raw.bytes.length > maxSourceBytes()) {
    throw new Error(`SOURCE_TOO_LARGE: ${raw.bytes.length} > ${maxSourceBytes()}`);
  }

  const kind = sniffKind(raw.bytes);
  if (!kind) throw new Error("UNKNOWN_FILE_SIGNATURE");

  const ext = extname(fileName).toLowerCase();
  if (ALLOWED_EXT[ext] !== kind) throw new Error(`EXTENSION_SIGNATURE_MISMATCH: ${ext} is not ${kind}`);
  if (role !== "DRAWING" && kind !== "DXF") {
    throw new Error(`ROLE_KIND_MISMATCH: ${role} requires DXF`);
  }

  const declared = raw.mimeType?.split(";")[0]?.trim().toLowerCase();
  if (declared && declared !== "application/octet-stream" && !KIND_MIME[kind].includes(declared)) {
    throw new Error(`MIME_SIGNATURE_MISMATCH: declared ${declared}, signature ${kind}`);
  }

  const sha256 = createHash("sha256").update(raw.bytes).digest("hex");
  const dir = join(dataRoot(), "sources", role, sha256.slice(0, 2));
  const storedPath = join(dir, `${sha256}${ext}`);
  mkdirSync(dir, { recursive: true });
  try {
    writeFileSync(storedPath, raw.bytes, { flag: "wx" });
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code !== "EEXIST") throw error;
    if (!existsSync(storedPath)) throw error; // content-addressed: same path => same bytes
  }

  return {
    kind,
    bytes: raw.bytes.length,
    fileName,
    mimeType: KIND_MIME[kind][0] ?? declared ?? "application/octet-stream",
    sha256,
    storedPath
  };
}

function isPrivateAddress(address: string): boolean {
  if (isIP(address) === 4) {
    const [a = 0, b = 0] = address.split(".").map(Number);
    return (
      a === 0 || a === 10 || a === 127 ||
      (a === 169 && b === 254) ||
      (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && b === 168) ||
      (a === 100 && b >= 64 && b <= 127)
    );
  }
  const lower = address.toLowerCase();
  return (
    lower === "::" || lower === "::1" || lower.startsWith("fc") || lower.startsWith("fd") ||
    lower.startsWith("fe80") || lower.startsWith("::ffff:127.") || lower.startsWith("::ffff:10.") ||
    lower.startsWith("::ffff:192.168.")
  );
}

async function assertPublicHost(hostname: string, allowPrivate: boolean): Promise<void> {
  if (allowPrivate) return;
  const literal = isIP(hostname);
  const addresses = literal ? [hostname] : (await lookup(hostname, { all: true })).map((r) => r.address);
  if (!addresses.length) throw new Error(`DNS_FAILED: ${hostname}`);
  if (addresses.some(isPrivateAddress)) throw new Error(`PRIVATE_ADDRESS_BLOCKED: ${hostname}`);
}

export type DownloadOptions = {
  allowPrivate?: boolean;
  maxRedirects?: number;
  timeoutMs?: number;
};

/** SSRF-guarded fetch: http(s) only, bounded redirects, bounded size and time. */
export async function downloadUri(uri: string, options: DownloadOptions = {}): Promise<Buffer> {
  const allowPrivate = options.allowPrivate ?? process.env.TRAINAICAD_ALLOW_PRIVATE_URL === "1";
  const maxRedirects = options.maxRedirects ?? 3;
  const timeoutMs = options.timeoutMs ?? 15_000;
  const limit = maxSourceBytes();

  let current = uri;
  for (let hop = 0; hop <= maxRedirects; hop += 1) {
    const url = new URL(current);
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      throw new Error(`UNSUPPORTED_URI_SCHEME: ${url.protocol}`);
    }
    await assertPublicHost(url.hostname, allowPrivate);

    const response = await fetch(url, {
      redirect: "manual",
      signal: AbortSignal.timeout(timeoutMs),
      headers: { accept: "application/pdf,image/*,application/dxf,text/plain,*/*" }
    });
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (!location) throw new Error(`REDIRECT_WITHOUT_LOCATION: ${response.status}`);
      current = new URL(location, url).toString();
      continue;
    }
    if (!response.ok) throw new Error(`DOWNLOAD_FAILED: ${response.status} ${url.host}`);

    const declared = Number(response.headers.get("content-length") ?? "0");
    if (Number.isFinite(declared) && declared > limit) {
      throw new Error(`SOURCE_TOO_LARGE: content-length ${declared} > ${limit}`);
    }

    const chunks: Buffer[] = [];
    let total = 0;
    for await (const chunk of response.body as unknown as AsyncIterable<Uint8Array>) {
      total += chunk.byteLength;
      if (total > limit) throw new Error(`SOURCE_TOO_LARGE: streamed ${total} > ${limit}`);
      chunks.push(Buffer.from(chunk));
    }
    return Buffer.concat(chunks);
  }
  throw new Error(`TOO_MANY_REDIRECTS: > ${maxRedirects}`);
}

/** Bind an ingested source to a job, immutably, per role. */
export function bindSourceToJob(
  jobId: string,
  role: SourceRole,
  source: IngestResult
): Record<string, IngestResult> {
  if (!/^cad_[a-f0-9]{16}$/.test(jobId)) throw new Error(`INVALID_JOB_ID: ${jobId}`);
  const dir = join(dataRoot(), "jobs");
  const file = join(dir, `${jobId}.sources.json`);
  if (!existsSync(join(dir, `${jobId}.json`))) throw new Error(`JOB_NOT_FOUND: ${jobId}`);
  mkdirSync(dir, { recursive: true });
  const current: Record<string, IngestResult> = existsSync(file)
    ? (JSON.parse(readFileSync(file, "utf8")) as Record<string, IngestResult>)
    : {};
  const bound = current[role];
  if (bound && bound.sha256 !== source.sha256) {
    throw new Error(`SOURCE_ALREADY_BOUND: ${role} is immutable for ${jobId}`);
  }
  current[role] = source;
  writeFileSync(file, JSON.stringify(current, null, 2));
  return current;
}
