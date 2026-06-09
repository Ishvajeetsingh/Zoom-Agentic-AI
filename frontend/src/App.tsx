import { useEffect, useState } from "react";
import { DashboardPage } from "./pages/DashboardPage";
import { TranscriptListPage } from "./pages/TranscriptListPage";
import { TranscriptDetailPage } from "./pages/TranscriptDetailPage";
import { QuestionsPage } from "./pages/QuestionsPage";
import { RunsPage } from "./pages/RunsPage";
import { MeetingsPage } from "./pages/MeetingsPage";
import { MeetingDetailPage } from "./pages/MeetingDetailPage";
import { ProcessMeetingPage } from "./pages/ProcessMeetingPage";
import { UploadTranscriptPage } from "./pages/UploadTranscriptPage";

type Route =
  | { page: "dashboard" }
  | { page: "transcripts" }
  | { page: "transcript-detail"; transcriptId: string }
  | { page: "questions" }
  | { page: "runs" }
  | { page: "meetings" }
  | { page: "meeting-detail"; meetingId: string }
  | { page: "process-meeting" }
  | { page: "upload-transcript" }
  | { page: "not-found" };

function parseHash(hash: string): Route {
  if (!hash || hash === "#/" || hash === "#") return { page: "dashboard" };

  const transcriptDetailMatch = hash.match(/^#\/transcripts\/([^/]+)$/);
  if (transcriptDetailMatch) return { page: "transcript-detail", transcriptId: transcriptDetailMatch[1] };
  if (hash === "#/transcripts") return { page: "transcripts" };
  if (hash === "#/questions") return { page: "questions" };
  if (hash === "#/runs") return { page: "runs" };
  if (hash === "#/meetings") return { page: "meetings" };
  if (hash === "#/process-meeting") return { page: "process-meeting" };
  if (hash === "#/upload-transcript") return { page: "upload-transcript" };

  const meetingDetailMatch = hash.match(/^#\/meetings\/([^/]+)$/);
  if (meetingDetailMatch) return { page: "meeting-detail", meetingId: meetingDetailMatch[1] };

  return { page: "not-found" };
}

export default function App() {
  const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash));

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(parseHash(window.location.hash));
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  switch (route.page) {
    case "dashboard":
      return <DashboardPage />;
    case "transcripts":
      return <TranscriptListPage />;
    case "transcript-detail":
      return <TranscriptDetailPage transcriptId={route.transcriptId} />;
    case "questions":
      return <QuestionsPage />;
    case "runs":
      return <RunsPage />;
    case "meetings":
      return <MeetingsPage />;
    case "meeting-detail":
      return <MeetingDetailPage meetingId={route.meetingId} />;
    case "process-meeting":
      return <ProcessMeetingPage />;
    case "upload-transcript":
      return <UploadTranscriptPage />;
    default:
      return <DashboardPage />;
  }
}
