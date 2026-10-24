import { useState } from "react";
import { CompressionPanel } from "./components/CompressionPanel";
import { HistoryPanel } from "./components/HistoryPanel";
import "./styles/main.css";

function App() {
  const [activeTab, setActiveTab] = useState<"compress" | "history">("compress");

  return (
    <div className="app">
      <header className="app-header">
        <h1>Sentinel Studio</h1>
        <nav className="app-nav">
          <button
            className={activeTab === "compress" ? "active" : ""}
            onClick={() => setActiveTab("compress")}
          >
            Compress
          </button>
          <button
            className={activeTab === "history" ? "active" : ""}
            onClick={() => setActiveTab("history")}
          >
            History
          </button>
        </nav>
      </header>
      <main className="app-main">
        {activeTab === "compress" && <CompressionPanel />}
        {activeTab === "history" && <HistoryPanel />}
      </main>
    </div>
  );
}

export default App;

