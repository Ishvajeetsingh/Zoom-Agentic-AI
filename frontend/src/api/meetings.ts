import { apiGet } from "./client";
import type { MeetingListItem, MeetingDetail, PaginatedListResponse } from "../types/api";

export interface MeetingListParams {
  offset?: number;
  limit?: number;
  order_by?: string;
  order?: "asc" | "desc";
}

export function getMeetings(params?: MeetingListParams) {
  return apiGet<PaginatedListResponse<MeetingListItem>>(
    "/meetings",
    params as Record<string, string | number>
  );
}

export function getMeeting(meetingId: string) {
  return apiGet<MeetingDetail>(`/meetings/${meetingId}`);
}
