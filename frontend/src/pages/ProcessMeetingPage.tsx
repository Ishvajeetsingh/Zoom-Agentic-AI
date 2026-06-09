import { useEffect, useState } from "react";
import { Video, RotateCcw } from "lucide-react";
import { AppShell } from "../components/layout/AppShell";
import { ProcessingTimeline, type TimelineStep } from "../components/common/ProcessingTimeline";
import { CompletionCard } from "../components/common/CompletionCard";
import { ingestZoomMeeting } from "../api/zoom";
import { runPipeline } from "../api/transcripts";
import type { ZoomIngestResponse } from "../types/api";

type Phase = "form" | "ingesting" | "pipeline" | "done" | "error";

const INGEST_STEPS: TimelineStep[] = [
  { key: "auth", label: "Authenticate with Zoom", description: "Obtain OAuth access token", status: "waiting" },
  { key: "fetch", label: "Fetch Recording Metadata", description: "Retrieve meeting and recording details", status: "waiting" },
  { key: "meeting", label: "Save Meeting Record", description: "Upsert meeting into database", status: "waiting" },
  { key: "transcript", label: "Find Transcript File", description: "Locate VTT/CC transcript in recording files", status: "waiting" },
];

const PIPELINE_STEPS: TimelineStep[] = [
  { key: "download", label: "Download Transcript", description: "Download VTT file from Zoom cloud", status: "waiting" },
  { key: "parse", label: "Parse Transcript", description: "Extract speaker segments and timestamps", status: "waiting" },
  { key: "clean", label: "Clean Transcript", description: "Normalize speakers, remove fillers and artifacts", status: "waiting" },
  { key: "chunk", label: "Semantic Chunking", description: "Split transcript into topic-coherent chunks", status: "waiting" },
  { key: "generate", label: "Generate Questions", description: "Create quiz questions using LLM", status: "waiting" },
];

function setStep(steps: TimelineStep[], key: string, status: TimelineStep["status"], desc?: string): TimelineStep[] {
  return steps.map((s) =>
    s.key === key ? { ...s, status, description: desc ?? s.description } : s
  );
}

function markPreviousCompleted(steps: TimelineStep[], upToKey: string): TimelineStep[] {
  let found = false;
  return steps.map((s) => {
    if (s.key === upToKey) found = true;
    return !found && s.status !== "failed" ? { ...s, status: "completed" as const } : s;
  });
}

export function ProcessMeetingPage() {
  const [meetingUuid, setMeetingUuid] = useState("");
  const [phase, setPhase] = useState<Phase>("form");
  const [ingestSteps, setIngestSteps] = useState<TimelineStep[]>(INGEST_STEPS);
  const [pipelineSteps, setPipelineSteps] = useState<TimelineStep[]>(PIPELINE_STEPS);
  const [ingestResult, setIngestResult] = useState<ZoomIngestResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [completionStats, setCompletionStats] = useState<{ label: string; value: string }[]>([]);

  const reset = () => {
    setPhase("form");
    setMeetingUuid("");
    setIngestSteps(INGEST_STEPS.map((s) => ({ ...s })));
    setPipelineSteps(PIPELINE_STEPS.map((s) => ({ ...s })));
    setIngestResult(null);
    setErrorMsg(null);
    setCompletionStats([]);
  };

  const handleIngest = async () => {
    if (!meetingUuid.trim()) return;
    setPhase("ingesting");
    setErrorMsg(null);
    let steps = INGEST_STEPS.map((s) => ({ ...s }));

    steps = setStep(steps, "auth", "running", "Requesting OAuth token...");
    setIngestSteps([...steps]);

    try {
      await new Promise((r) => setTimeout(r, 600));
      steps = markPreviousCompleted(setStep(steps, "auth", "completed"), "auth");
      steps = setStep(steps, "fetch", "running", "Calling Zoom Recording API...");
      setIngestSteps([...steps]);

      const result = await ingestZoomMeeting({ meeting_uuid: meetingUuid.trim() });

      steps = markPreviousCompleted(setStep(steps, "fetch", "completed"), "fetch");
      steps = setStep(steps, "meeting", "completed", "Meeting record saved");
      if (result.recording_found) {
        steps = setStep(steps, "transcript", "completed", "Transcript file found");
      } else {
        steps = setStep(steps, "transcript", "failed", "No transcript file found in recording");
      }
      setIngestSteps([...steps]);
      setIngestResult(result);

      if (result.transcript_id && result.recording_found) {
        setPhase("pipeline");
        runPipelineSteps(result.transcript_id);
      } else if (!result.recording_found) {
        setPhase("error");
        setErrorMsg("No transcript recording found for this meeting. The meeting may not have had cloud transcription enabled.");
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Ingestion failed";
      steps = setStep(
        steps,
        steps.find((s) => s.status === "running")?.key ?? "fetch",
        "failed",
        msg
      );
      setIngestSteps([...steps]);
      setPhase("error");
      setErrorMsg(msg);
    }
  };

  const runPipelineSteps = async (transcriptId: string) => {
    let steps = PIPELINE_STEPS.map((s) => ({ ...s }));
    const stepKeys = ["download", "parse", "clean", "chunk", "generate"];
    const stepLabels: Record<string, string> = {
      download: "Downloading VTT from Zoom...",
      parse: "Extracting speaker segments...",
      clean: "Normalizing and cleaning...",
      chunk: "Building semantic chunks...",
      generate: "Running LLM question generation...",
    };

    try {
      for (const key of stepKeys) {
        steps = setStep(steps, key, "running", stepLabels[key]);
        setPipelineSteps([...steps]);

        const res = await fetch(
          `${import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1"}/transcripts/${transcriptId}/${key}`,
          { method: "POST", headers: { "Content-Type": "application/json" } }
        );

        if (!res.ok) {
          const detail = await res.text().catch(() => "");
          throw new Error(detail || `Step ${key} failed: ${res.status}`);
        }

        steps = markPreviousCompleted(setStep(steps, key, "completed"), key);
        setPipelineSteps([...steps]);
      }

      setPhase("done");
      setCompletionStats([
        { label: "Meeting ID", value: ingestResult?.meeting_id ?? "" },
        { label: "Transcript ID", value: transcriptId },
        { label: "Topic", value: ingestResult?.topic ?? "N/A" },
        { label: "Zoom UUID", value: ingestResult?.zoom_uuid ?? meetingUuid },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Pipeline failed";
      const failedStep = steps.find((s) => s.status === "running");
      if (failedStep) {
        steps = setStep(steps, failedStep.key, "failed", msg);
        setPipelineSteps([...steps]);
      }
      setPhase("error");
      setErrorMsg(msg);
    }
  };

  return (
    <AppShell>
      <div className="process-page">
        <div className="page-header">
          <h1>Process Zoom Meeting</h1>
          <p className="page-header-subtitle">
            Ingest a Zoom meeting recording and run the full transcript processing pipeline
          </p>
        </div>

        {phase === "form" && (
          <div className="process-form">
            <div className="form-group">
              <label className="form-label">Meeting UUID</label>
              <input
                className="form-input"
                type="text"
                placeholder="e.g. /Mv5TxyCQVM8wOQ=="
                value={meetingUuid}
                onChange={(e) => setMeetingUuid(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleIngest()}
              />
              <p className="form-hint">
                Find this in the Zoom portal under Past Meetings, or from the recording URL.
              </p>
            </div>
            <button className="btn-primary" onClick={handleIngest} disabled={!meetingUuid.trim()}>
              <Video size={18} /> Ingest &amp; Process
            </button>
          </div>
        )}

        {(phase === "ingesting" || phase === "pipeline" || phase === "error" || phase === "done") && (
          <>
            <div className="panel" style={{ marginBottom: 24 }}>
              <div className="panel-header">
                <h2 className="panel-title">Ingestion</h2>
              </div>
              <ProcessingTimeline steps={ingestSteps} />
            </div>

            {ingestResult?.transcript_id && (
              <div className="panel" style={{ marginBottom: 24 }}>
                <div className="panel-header">
                  <h2 className="panel-title">Processing Pipeline</h2>
                </div>
                <ProcessingTimeline steps={pipelineSteps} />
              </div>
            )}

            {phase === "error" && errorMsg && (
              <div className="process-error-box">
                <span>&#9888;</span>
                <p>{errorMsg}</p>
              </div>
            )}

            {phase === "done" && (
              <CompletionCard
                stats={completionStats}
                actions={
                  <>
                    <a href={`#/transcripts/${ingestResult?.transcript_id}`} className="btn-primary">
                      View Transcript
                    </a>
                    <button className="btn-secondary" onClick={reset}>
                      <RotateCcw size={16} /> Process Another
                    </button>
                  </>
                }
              />
            )}

            {(phase === "error") && (
              <div style={{ marginTop: 16 }}>
                <button className="btn-secondary" onClick={reset}>
                  <RotateCcw size={16} /> Start Over
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
