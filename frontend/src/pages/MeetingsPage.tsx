import { useEffect, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { MeetingList } from "../components/meetings/MeetingList";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { getMeetings } from "../api/meetings";
import type { MeetingListItem, PaginatedListResponse } from "../types/api";

const PAGE_SIZE = 20;

export function MeetingsPage() {
  const [data, setData] = useState<PaginatedListResponse<MeetingListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    let cancelled = false;
    getMeetings({ offset, limit: PAGE_SIZE })
      .then((res) => {
        if (!cancelled) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load meetings");
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
        <h1>Meetings</h1>
        <p className="page-header-subtitle">All synced Zoom meetings</p>
      </div>
      {loading && <LoadingState message="Loading meetings..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && (
        data && data.items.length > 0 ? (
          <div className="panel">
            <MeetingList meetings={data.items} />
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
                  Page {currentPage} of {totalPages} ({data.total} meetings)
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
          <EmptyState message="No meetings found." title="No Meetings" />
        )
      )}
    </AppShell>
  );
}
