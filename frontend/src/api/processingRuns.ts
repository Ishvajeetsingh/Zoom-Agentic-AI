import { apiGet } from "./client";

export function getProcessingRuns() {
  return apiGet<{ items: unknown[] }>("/processing-runs");
}

