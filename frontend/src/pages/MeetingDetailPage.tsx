import { useEffect, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { MeetingDetail } from "../components/meetings/MeetingDetail";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { getMeeting } from "../api/meetings";
import type { MeetingDetail as MeetingDetailType } from "../types/api";
import { ArrowLeft } from "lucide-react";

interface MeetingDetailPageProps {
  meetingId?: string;
}

export function MeetingDetailPage({ meetingId }: MeetingDetailPageProps) {
  const [meeting, setMeeting] = useState<MeetingDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!meetingId) {
      setError("No meeting ID provided");
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    getMeeting(meetingId)
      .then((res) => {
        if (!cancelled) {
          setMeeting(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load meeting");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [meetingId]);

  return (
    <AppShell>
      <div className="page-header">
        <a href="#/meetings" className="back-link">
          <ArrowLeft size={14} />
          Back to Meetings
        </a>
        <h1>Meeting Detail</h1>
      </div>
      {loading && <LoadingState message="Loading meeting..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && meeting && <MeetingDetail meeting={meeting} />}
    </AppShell>
  );
}
