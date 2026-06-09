export type QuestionType = "mcq" | "short_answer" | "true_false" | "fill_blank";
export type Difficulty = "easy" | "medium" | "hard";
export type TranscriptStatus =
  | "metadata_received"
  | "download_started"
  | "downloaded"
  | "parsing_started"
  | "parsed"
  | "parsing_failed"
  | "cleaning_started"
  | "cleaned"
  | "cleaning_failed"
  | "chunking_started"
  | "chunked"
  | "chunking_failed"
  | "generating"
  | "completed"
  | "generation_failed"
  | "failed";

export interface PaginatedListResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface MeetingListItem {
  id: string;
  source: string;
  zoom_meeting_id: string | null;
  zoom_uuid: string | null;
  topic: string | null;
  start_time: string | null;
  timezone: string | null;
  duration_minutes: number | null;
  participant_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface MeetingDetail {
  id: string;
  source: string;
  zoom_meeting_id: string | null;
  zoom_uuid: string | null;
  account_id: string | null;
  host_id: string | null;
  host_email: string | null;
  topic: string | null;
  start_time: string | null;
  timezone: string | null;
  duration_minutes: number | null;
  participant_count: number | null;
  transcript_count: number;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface TranscriptListItem {
  id: string;
  meeting_id: string;
  source_format: string | null;
  status: TranscriptStatus;
  transcript_filename: string | null;
  file_type: string | null;
  file_size_bytes: number | null;
  segment_count: number | null;
  chunk_count: number | null;
  question_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface TranscriptDetail {
  id: string;
  meeting_id: string;
  source_format: string | null;
  status: TranscriptStatus;
  transcript_filename: string | null;
  raw_file_path: string | null;
  processed_file_path: string | null;
  zoom_file_id: string | null;
  zoom_recording_type: string | null;
  file_type: string | null;
  file_extension: string | null;
  file_size_bytes: number | null;
  recording_start: string | null;
  recording_end: string | null;
  language: string | null;
  segment_count: number;
  word_count: number | null;
  cleaned_segment_count: number | null;
  cleaned_word_count: number | null;
  chunk_count: number;
  question_count: number;
  generation_model: string | null;
  checksum_sha256: string | null;
  created_at: string;
  updated_at: string;
}

export interface Question {
  id: string;
  transcript_id: string;
  meeting_id: string;
  chunk_id: string | null;
  chunk_index: number | null;
  question_text: string;
  question_type: QuestionType;
  options: string[];
  correct_answer: string;
  explanation: string;
  difficulty: Difficulty;
  is_valid: boolean;
  is_duplicate: boolean;
  duplicate_of: string | null;
  created_at: string;
}

export interface QuestionListResponse {
  items: Question[];
  total: number;
  offset: number;
  limit: number;
}

export interface ZoomIngestResponse {
  meeting_id: string;
  transcript_id: string | null;
  recording_found: boolean;
  zoom_meeting_id: string | null;
  zoom_uuid: string;
  topic: string | null;
}

export interface TranscriptUploadResponse {
  transcript_id: string;
  meeting_id: string;
  transcript_filename: string;
  file_size_bytes: number;
  source_format: string;
  status: string;
}

export interface PipelineStepResult {
  step: string;
  status: string;
  [key: string]: unknown;
}

export interface PipelineResponse {
  transcript_id: string;
  status: string;
  steps: PipelineStepResult[];
}
