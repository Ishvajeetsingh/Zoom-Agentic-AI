import { AlertTriangle } from "lucide-react";

export function ErrorState({ message = "Something went wrong." }: { message?: string }) {
  return (
    <div className="error-state">
      <AlertTriangle className="error-state-icon" />
      <p className="error-state-title">Error</p>
      <p className="error-state-msg">{message}</p>
    </div>
  );
}
