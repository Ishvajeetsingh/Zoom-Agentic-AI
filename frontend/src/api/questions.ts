import { apiGet } from "./client";
import type { Question, PaginatedListResponse } from "../types/api";

export interface QuestionFilters {
  offset?: number;
  limit?: number;
  difficulty?: string;
  question_type?: string;
  order?: "asc" | "desc";
}

export function getTranscriptQuestions(transcriptId: string, filters?: QuestionFilters) {
  return apiGet<PaginatedListResponse<Question>>(
    `/transcripts/${transcriptId}/questions`,
    filters as Record<string, string | number>
  );
}

export function getQuestion(questionId: string) {
  return apiGet<Question>(`/questions/${questionId}`);
}
