import { useEffect, useState } from "react";
import { LayoutDashboard, FileText, HelpCircle, Activity, Cpu, Video, Upload, Zap } from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "#/", icon: <LayoutDashboard size={20} /> },
  { label: "Meetings", href: "#/meetings", icon: <Video size={20} /> },
  { label: "Transcripts", href: "#/transcripts", icon: <FileText size={20} /> },
  { label: "Questions", href: "#/questions", icon: <HelpCircle size={20} /> },
  { label: "Runs", href: "#/runs", icon: <Activity size={20} /> },
];

const ACTION_ITEMS: NavItem[] = [
  { label: "Process Meeting", href: "#/process-meeting", icon: <Zap size={20} /> },
  { label: "Upload Transcript", href: "#/upload-transcript", icon: <Upload size={20} /> },
];

export function Sidebar() {
  const [currentHash, setCurrentHash] = useState(window.location.hash || "#/");
  const [ollamaOnline, setOllamaOnline] = useState(false);
  const [primaryModel, setPrimaryModel] = useState("qwen3:8b");

  useEffect(() => {
    const handleHashChange = () => setCurrentHash(window.location.hash || "#/");
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch("http://localhost:11434/api/tags");
        const data = await res.json();
        setOllamaOnline(true);
        const qwen = data.models?.find((m: { name: string }) => m.name.startsWith("qwen3"));
        setPrimaryModel(qwen ? qwen.name : data.models?.[0]?.name ?? "N/A");
      } catch {
        setOllamaOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleClick = (href: string) => {
    setCurrentHash(href);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-section-label">Navigation</div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className={`sidebar-link ${currentHash === item.href ? "active" : ""}`}
            onClick={() => handleClick(item.href)}
          >
            <span className="sidebar-link-icon">{item.icon}</span>
            {item.label}
          </a>
        ))}
      </nav>
      <div className="sidebar-section-label" style={{ marginTop: 28 }}>Actions</div>
      <nav className="sidebar-nav">
        {ACTION_ITEMS.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className={`sidebar-link ${currentHash === item.href ? "active" : ""}`}
            onClick={() => handleClick(item.href)}
          >
            <span className="sidebar-link-icon">{item.icon}</span>
            {item.label}
          </a>
        ))}
      </nav>
      <div className="sidebar-spacer" />
      <div className="sidebar-footer">
        <div className="sidebar-model-info">
          <span className={`sidebar-model-dot ${ollamaOnline ? "" : "offline"}`} />
          <div>
            <div className="sidebar-model-label">LLM Engine</div>
            <div className="sidebar-model-name">{primaryModel}</div>
          </div>
          <Cpu size={16} style={{ marginLeft: "auto", opacity: 0.4 }} />
        </div>
        <div className="sidebar-version">Zoom Agentic AI v0.1.0</div>
      </div>
    </aside>
  );
}
