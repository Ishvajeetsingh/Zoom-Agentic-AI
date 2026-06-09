import { useEffect, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { TranscriptDetail } from "../components/transcripts/TranscriptDetail";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { getTranscript } from "../api/transcripts";
import type { TranscriptDetail as TranscriptDetailType } from "../types/api";
import { ArrowLeft } from "lucide-react";

interface TranscriptDetailPageProps {
  transcriptId: string;
}

export function TranscriptDetailPage({ transcriptId }: TranscriptDetailPageProps) {
  const [transcript, setTranscript] = useState<TranscriptDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getTranscript(transcriptId)
      .then((res) => {
        if (!cancelled) {
          setTranscript(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load transcript");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [transcriptId]);

  return (
    <AppShell>
      <div className="page-header">
        <a href="#/transcripts" className="back-link">
          <ArrowLeft size={14} />
          Back to Transcripts
        </a>
        <h1>Transcript Detail</h1>
      </div>

      {loading && <LoadingState message="Loading transcript..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && transcript && <TranscriptDetail transcript={transcript} />}
    </AppShell>
  );
}
