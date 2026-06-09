import type { TranscriptStatus } from "../../types/api";

interface ProcessingTimelineProps {
  status: TranscriptStatus;
}

const PIPELINE_STEPS = [
  { key: "metadata_received", label: "Received" },
  { key: "downloaded", label: "Download" },
  { key: "parsed", label: "Parse" },
  { key: "cleaned", label: "Clean" },
  { key: "chunked", label: "Chunk" },
  { key: "completed", label: "Generate" },
] as const;

const STEP_ORDER: Record<string, number> = {
  metadata_received: 0,
  download_started: 1,
  downloaded: 1,
  parsing_started: 2,
  parsed: 2,
  cleaning_started: 3,
  cleaned: 3,
  chunking_started: 4,
  chunked: 4,
  generating: 5,
  completed: 5,
  parsing_failed: 2,
  cleaning_failed: 3,
  chunking_failed: 4,
  generation_failed: 5,
  failed: -1,
};

const FAILED_STEPS: Record<string, number> = {
  parsing_failed: 2,
  cleaning_failed: 3,
  chunking_failed: 4,
  generation_failed: 5,
};

export function ProcessingTimeline({ status }: ProcessingTimelineProps) {
  const currentStepIndex = STEP_ORDER[status] ?? -1;
  const failedStepIndex = FAILED_STEPS[status] ?? -1;
  const isFailed = status.endsWith("_failed") || status === "failed";
  const isInProgress = status.includes("_started") || status === "generating";

  return (
    <div className="processing-timeline">
      {PIPELINE_STEPS.map((step, i) => {
        const isStepCompleted = !isFailed && currentStepIndex > i;
        const isStepActive = isInProgress && currentStepIndex === i;
        const isStepFailed = isFailed && failedStepIndex === i;
        const isStepDone = status === "completed" || isStepCompleted;

        let dotClass = "";
        if (isStepFailed) dotClass = "failed";
        else if (isStepActive) dotClass = "active";
        else if (isStepDone) dotClass = "completed";

        const connectorCompleted = isStepDone;

        return (
          <div className="timeline-step" key={step.key}>
            <div className="timeline-step-wrap">
              <div className={`timeline-dot ${dotClass}`}>
                {isStepDone && !isStepFailed ? "\u2713" : i + 1}
              </div>
              <span className="timeline-label">{step.label}</span>
            </div>
            {i < PIPELINE_STEPS.length - 1 && (
              <div className={`timeline-connector ${connectorCompleted ? "completed" : ""}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
