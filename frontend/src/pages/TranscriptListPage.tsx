import { useEffect, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { TranscriptList } from "../components/transcripts/TranscriptList";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { getTranscripts } from "../api/transcripts";
import type { TranscriptListItem, PaginatedListResponse } from "../types/api";

const PAGE_SIZE = 20;

export function TranscriptListPage() {
  const [data, setData] = useState<PaginatedListResponse<TranscriptListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    let cancelled = false;
    getTranscripts({ offset, limit: PAGE_SIZE })
      .then((res) => {
        if (!cancelled) {
          setData(res);
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
  }, [offset]);

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;
  const currentPage = data ? Math.floor(data.offset / PAGE_SIZE) + 1 : 1;

  return (
    <AppShell>
      <div className="page-header">
        <h1>Transcripts</h1>
        <p className="page-header-subtitle">All processed meeting transcripts and their status</p>
      </div>

      {loading && <LoadingState message="Loading transcripts..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && (
        data && data.items.length > 0 ? (
          <div className="panel">
            <TranscriptList transcripts={data.items} />
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="pagination-btn"
                  disabled={currentPage <= 1}
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                >
                  Previous
                </button>
                <span className="pagination-info">
                  Page {currentPage} of {totalPages} ({data.total} transcripts)
                </span>
                <button
                  className="pagination-btn"
                  disabled={currentPage >= totalPages}
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                >
                  Next
                </button>
              </div>
            )}
          </div>
        ) : (
          <EmptyState message="No transcripts found. They will appear after Zoom meetings are processed." title="No Transcripts" />
        )
      )}
    </AppShell>
  );
}
