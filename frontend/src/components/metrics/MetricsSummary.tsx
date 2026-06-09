import { FileText, HelpCircle, CheckCircle, XCircle } from "lucide-react";

interface MetricsSummaryProps {
  totalTranscripts: number;
  totalQuestions: number;
  completedTranscripts: number;
  failedTranscripts: number;
}

export function MetricsSummary({ totalTranscripts, totalQuestions, completedTranscripts, failedTranscripts }: MetricsSummaryProps) {
  return (
    <div className="metrics-summary">
      <div className="metric-card">
        <div className="metric-icon-wrap metric-icon-primary">
          <FileText />
        </div>
        <div className="metric-body">
          <span className="metric-value">{totalTranscripts}</span>
          <span className="metric-label">Transcripts</span>
        </div>
      </div>
      <div className="metric-card">
        <div className="metric-icon-wrap metric-icon-primary">
          <HelpCircle />
        </div>
        <div className="metric-body">
          <span className="metric-value">{totalQuestions}</span>
          <span className="metric-label">Questions</span>
        </div>
      </div>
      <div className="metric-card metric-card-success">
        <div className="metric-icon-wrap metric-icon-success">
          <CheckCircle />
        </div>
        <div className="metric-body">
          <span className="metric-value">{completedTranscripts}</span>
          <span className="metric-label">Completed</span>
        </div>
      </div>
      <div className="metric-card metric-card-error">
        <div className="metric-icon-wrap metric-icon-error">
          <XCircle />
        </div>
        <div className="metric-body">
          <span className="metric-value">{failedTranscripts}</span>
          <span className="metric-label">Failed</span>
        </div>
      </div>
    </div>
  );
}
