import { AppShell } from "../components/layout/AppShell";
import { RunTimeline } from "../components/metrics/RunTimeline";

export function RunsPage() {
  return (
    <AppShell>
      <div className="page-header">
        <h1>Processing Runs</h1>
        <p className="page-header-subtitle">Track the status of transcript processing pipelines</p>
      </div>
      <RunTimeline />
    </AppShell>
  );
}
