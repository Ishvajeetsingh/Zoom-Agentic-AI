interface CompletionStat {
  label: string;
  value: string;
}

interface CompletionCardProps {
  title?: string;
  stats: CompletionStat[];
  actions?: React.ReactNode;
}

export function CompletionCard({ title = "Processing Complete", stats, actions }: CompletionCardProps) {
  return (
    <div className="completion-card">
      <h3 className="completion-card-title">
        <span style={{ fontSize: "1.3rem" }}>&#10003;</span> {title}
      </h3>
      <div className="completion-stats">
        {stats.map((s) => (
          <div key={s.label} className="completion-stat">
            <span className="completion-stat-label">{s.label}</span>
            <span className="completion-stat-value">{s.value}</span>
          </div>
        ))}
      </div>
      {actions && <div className="completion-actions">{actions}</div>}
    </div>
  );
}
