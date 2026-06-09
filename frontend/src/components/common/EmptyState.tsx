import { Inbox } from "lucide-react";

export function EmptyState({ message = "No data available.", title }: { message?: string; title?: string }) {
  return (
    <div className="empty-state">
      <Inbox className="empty-state-icon" />
      {title && <p className="empty-state-title">{title}</p>}
      <p className="empty-state-msg">{message}</p>
    </div>
  );
}
