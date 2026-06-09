export function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="loading-state">
      <div className="loading-spinner" />
      <span className="loading-state-text">{message}</span>
    </div>
  );
}
