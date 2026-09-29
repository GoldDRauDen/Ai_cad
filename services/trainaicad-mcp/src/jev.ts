import type { RouteResult } from "./model.js";

export type JevMode = "disabled" | "mock" | "shadow";

/**
 * Jev adapter boundary. V0.1 makes no Jev network call in any mode and never
 * blocks the MCP: a missing TYPESAFE_API_KEY only changes the reported status.
 * Adding the key later flips `configured` without touching routing code.
 */
export function jevMode(): JevMode {
  const raw = process.env.JEV_MODE ?? "disabled";
  return raw === "mock" || raw === "shadow" ? raw : "disabled";
}

export function jevConfigured(): boolean {
  return Boolean(process.env.TYPESAFE_API_KEY?.trim());
}

export function jevStatus(): RouteResult["jev"] {
  const mode = jevMode();
  const configured = jevConfigured();

  if (mode === "mock") {
    return {
      mode,
      configured,
      verdict: "MOCK_MATCH",
      detail: "V0.1 mock only; hard router remains authoritative"
    };
  }
  if (mode === "shadow") {
    return {
      mode,
      configured,
      verdict: "UNAVAILABLE",
      detail: configured
        ? "shadow contract present and TYPESAFE_API_KEY set; network client lands in V0.2 (no call in V0.1)"
        : "shadow contract present; set TYPESAFE_API_KEY to configure the Jev client"
    };
  }
  return { mode, configured, verdict: "UNAVAILABLE", detail: "Jev disabled" };
}
