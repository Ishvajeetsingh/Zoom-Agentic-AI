import { apiGet } from "./client";

export function getMetrics() {
  return apiGet<{ items: unknown[] }>("/metrics");
}

