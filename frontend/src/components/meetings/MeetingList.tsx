import type { MeetingListItem } from "../../types/api";

interface MeetingListProps {
  meetings: MeetingListItem[];
}

function formatDate(iso: string | null): string {
  if (!iso) return "\u2014";
  return new Date(iso).toLocaleString();
}

export function MeetingList({ meetings }: MeetingListProps) {
  if (meetings.length === 0) return null;

  return (
    <div style={{ overflowX: "auto" }}>
      <table className="meeting-table">
        <thead>
          <tr>
            <th>Topic</th>
            <th>Start Time</th>
            <th>Duration</th>
            <th>Participants</th>
          </tr>
        </thead>
        <tbody>
          {meetings.map((m) => (
            <tr key={m.id}>
              <td style={{ fontWeight: 500 }}>{m.topic ?? "\u2014"}</td>
              <td className="cell-date">{formatDate(m.start_time)}</td>
              <td className="cell-number">{m.duration_minutes != null ? `${m.duration_minutes} min` : "\u2014"}</td>
              <td className="cell-number">{m.participant_count ?? "\u2014"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
