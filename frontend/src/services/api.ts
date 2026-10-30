import type { SimulationInput, Parameters } from "../types";
const env = import.meta.env;
const base = (env.VITE_API_URL || "").replace(/\/$/, "");
export const assetUrl = (url: string) => base + url;
async function request(url: string, init: RequestInit = {}) {
  let response: Response;
  try { response = await fetch(url, {...init, signal: AbortSignal.timeout(20000)}); }
  catch { throw new Error("A API está indisponível ou demorou para responder. Tente novamente."); }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === "string" ? data.detail : "Não foi possível concluir a operação.");
  }
  return response;
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await request(base + "/api" + path, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  return response.status === 204 ? (undefined as T) : response.json();
}
export function downloadConfig(input: SimulationInput, parameters: Parameters, version: string, hash: string) {
  const data = { model_version: version, model_hash: hash, strategy: input.strategy, scenario: input.scenario, name: input.name || "Minha simulação", overrides: parameters };
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
  const link = document.createElement("a"); link.href = url; link.download = "datavoxen-hipoteses.json"; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export async function download(
  input: SimulationInput,
  format: "csv" | "pdf",
  dataset = "months",
) {
  const response = await request(
    base + `/api/export?format=${format}&dataset=${dataset}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    },
  );
  const url = URL.createObjectURL(await response.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = `datavoxen-${dataset}.${format}`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
