import { useEffect, useState } from "react";
import { Zap } from "lucide-react";

export function TopBar() {
  const [ollamaStatus, setOllamaStatus] = useState<"online" | "offline">("offline");
  const [modelInfo, setModelInfo] = useState<string>("");

  useEffect(() => {
    const checkOllama = async () => {
      try {
        const res = await fetch("http://localhost:11434/api/tags");
        const data = await res.json();
        setOllamaStatus("online");
        const qwen = data.models?.find((m: { name: string }) => m.name.startsWith("qwen3"));
        setModelInfo(qwen ? qwen.name : data.models?.[0]?.name ?? "No model");
      } catch {
        setOllamaStatus("offline");
        setModelInfo("Unavailable");
      }
    };
    checkOllama();
    const interval = setInterval(checkOllama, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="topbar">
      <div className="topbar-logo">
        <div className="topbar-logo-icon">
          <Zap size={18} />
        </div>
        <span className="topbar-title">Zoom Agentic AI</span>
      </div>
      <span className="topbar-subtitle">Intelligent Question Generation Platform</span>
      <div className="topbar-spacer" />
      <div className={`topbar-badge ${ollamaStatus === "offline" ? "offline" : ""}`}>
        <span className="topbar-badge-dot" />
        Ollama {ollamaStatus === "online" ? "Online" : "Offline"} &middot; {modelInfo}
      </div>
    </header>
  );
}
