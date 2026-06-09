import type { MeetingDetail as MeetingDetailType } from "../../types/api";
import { Calendar, Clock, Users, Mail, Globe, FileText, HelpCircle, Hash } from "lucide-react";

interface MeetingDetailProps {
  meeting: MeetingDetailType;
}

function formatDate(iso: string | null): string {
  if (!iso) return "\u2014";
  return new Date(iso).toLocaleString();
}

export function MeetingDetail({ meeting }: MeetingDetailProps) {
  return (
    <section className="panel meeting-detail">
      <div className="panel-header">
        <h2 className="panel-title">{meeting.topic ?? "Untitled Meeting"}</h2>
      </div>
      <div className="transcript-info-grid">
        <div className="info-item">
          <span className="info-label"><Hash size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Zoom Meeting ID</span>
          <span className="info-value">{meeting.zoom_meeting_id ?? "\u2014"}</span>
        </div>
        <div className="info-item">
          <span className="info-label"><Calendar size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Start Time</span>
          <span className="info-value">{formatDate(meeting.start_time)}</span>
        </div>
        <div className="info-item">
          <span className="info-label"><Clock size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Duration</span>
          <span className="info-value">{meeting.duration_minutes != null ? `${meeting.duration_minutes} min` : "\u2014"}</span>
        </div>
        <div className="info-item">
          <span className="info-label"><Users size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Participants</span>
          <span className="info-value">{meeting.participant_count ?? "\u2014"}</span>
        </div>
        <div className="info-item">
          <span className="info-label"><Mail size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Host</span>
          <span className="info-value">{meeting.host_email ?? "\u2014"}</span>
        </div>
        <div className="info-item">
          <span className="info-label"><Globe size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Timezone</span>
          <span className="info-value">{meeting.timezone ?? "\u2014"}</span>
        </div>
        <div className="info-item">
          <span className="info-label"><FileText size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Transcripts</span>
          <span className="info-value">{meeting.transcript_count}</span>
        </div>
        <div className="info-item">
          <span className="info-label"><HelpCircle size={12} style={{ verticalAlign: "middle", marginRight: 4 }} />Questions</span>
          <span className="info-value">{meeting.question_count}</span>
        </div>
      </div>
    </section>
  );
}
