import { useEffect, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { QuestionList } from "../components/questions/QuestionList";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { getTranscripts } from "../api/transcripts";
import type { TranscriptListItem } from "../types/api";

export function QuestionsPage() {
  const [transcripts, setTranscripts] = useState<TranscriptListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTranscriptId, setSelectedTranscriptId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getTranscripts()
      .then((res) => {
        if (!cancelled) {
          const withQuestions = res.items.filter((t) => t.question_count != null && t.question_count > 0);
          setTranscripts(withQuestions);
          if (withQuestions.length > 0) {
            setSelectedTranscriptId(withQuestions[0].id);
          }
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load transcripts");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AppShell>
      <div className="page-header">
        <h1>Generated Questions</h1>
        <p className="page-header-subtitle">AI-generated assessment questions from meeting transcripts</p>
      </div>

      {loading && <LoadingState message="Loading..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && (
        <>
          {transcripts.length > 0 && (
            <div className="panel transcript-selector">
              <label className="filter-label">
                Select Transcript
                <select
                  value={selectedTranscriptId ?? ""}
                  onChange={(e: { target: { value: string } }) => setSelectedTranscriptId(e.target.value)}
                  className="filter-select"
                >
                  {transcripts.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.transcript_filename ?? t.id} ({t.question_count} questions)
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}

          {selectedTranscriptId ? (
            <QuestionList transcriptId={selectedTranscriptId} />
          ) : (
            <EmptyState message="No transcripts with generated questions found." title="No Questions Available" />
          )}
        </>
      )}
    </AppShell>
  );
}
