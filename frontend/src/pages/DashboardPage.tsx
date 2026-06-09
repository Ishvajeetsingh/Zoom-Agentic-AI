import { useEffect, useState } from "react";
import { Video, Upload } from "lucide-react";
import { AppShell } from "../components/layout/AppShell";
import { MetricsSummary } from "../components/metrics/MetricsSummary";
import { TranscriptList } from "../components/transcripts/TranscriptList";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { getTranscripts } from "../api/transcripts";
import type { TranscriptListItem } from "../types/api";

export function DashboardPage() {
  const [transcripts, setTranscripts] = useState<TranscriptListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getTranscripts({ limit: 10, order_by: "created_at", order: "desc" })
      .then((res) => {
        if (!cancelled) {
          setTranscripts(res.items);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load dashboard data");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const totalQuestions = transcripts.reduce((sum, t) => sum + (t.question_count ?? 0), 0);
  const completedTranscripts = transcripts.filter((t) => t.status === "completed").length;
  const failedTranscripts = transcripts.filter(
    (t) => t.status.endsWith("_failed") || t.status === "failed"
  ).length;

  return (
    <AppShell>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p className="page-header-subtitle">Overview of transcript processing and question generation</p>
      </div>

      {loading && <LoadingState message="Loading dashboard..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && (
        <>
          <div className="quick-action-grid">
            <a href="#/process-meeting" className="quick-action-card">
              <div className="quick-action-card-icon" style={{ background: "var(--c-primary-light)", color: "var(--c-primary)" }}>
                <Video size={22} />
              </div>
              <h3 className="quick-action-card-title">Process Zoom Meeting</h3>
              <p className="quick-action-card-desc">Ingest a Zoom recording by UUID and run the full processing pipeline</p>
            </a>
            <a href="#/upload-transcript" className="quick-action-card">
              <div className="quick-action-card-icon" style={{ background: "var(--c-success-light)", color: "var(--c-success)" }}>
                <Upload size={22} />
              </div>
              <h3 className="quick-action-card-title">Upload Transcript</h3>
              <p className="quick-action-card-desc">Upload a VTT, JSON, or TXT transcript file and generate questions</p>
            </a>
          </div>

          <MetricsSummary
            totalTranscripts={transcripts.length}
            totalQuestions={totalQuestions}
            completedTranscripts={completedTranscripts}
            failedTranscripts={failedTranscripts}
          />
          <section className="panel section-transcripts">
            <div className="panel-header">
              <h2 className="panel-title">Recent Transcripts</h2>
              <a href="#/transcripts" className="link-view">View all</a>
            </div>
            {transcripts.length > 0 ? (
              <TranscriptList transcripts={transcripts} />
            ) : (
              <EmptyState message="No transcripts yet. Use the actions above to get started." title="No Transcripts" />
            )}
          </section>
        </>
      )}
    </AppShell>
  );
}
