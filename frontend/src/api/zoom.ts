import { apiPost } from "./client";
import type { ZoomIngestResponse } from "../types/api";

export interface ZoomIngestRequest {
  meeting_uuid: string;
}

export function ingestZoomMeeting(request: ZoomIngestRequest) {
  return apiPost<ZoomIngestResponse>("/zoom/ingest", request);
}
