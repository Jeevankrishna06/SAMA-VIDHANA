import React, { useState, useEffect, useRef } from "react";
import { 
  Plus, 
  Send, 
  Paperclip, 
  Scale, 
  ClipboardList, 
  Rocket, 
  AlertTriangle, 
  BookOpen, 
  Loader2, 
  FileText,
  CheckSquare,
  Square,
  HelpCircle
} from "lucide-react";

export default function App() {
  // State
  const [sources, setSources] = useState({ global_sources: [], user_sources: [] });
  const [selectedSources, setSelectedSources] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeMsgId, setActiveMsgId] = useState(null);

  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Fetch Sources on load
  useEffect(() => {
    fetchSources();
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSources = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/sources");
      if (res.ok) {
        const data = await res.json();
        setSources(data);
      }
    } catch (err) {
      console.error("Error fetching sources:", err);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        // Add to selected sources by default
        setSelectedSources(prev => [...prev, data.filename]);
        await fetchSources();
      } else {
        const errData = await res.json();
        alert(`Upload failed: ${errData.detail || "Unknown error"}`);
      }
    } catch (err) {
      console.error("Error uploading file:", err);
      alert("Error uploading file.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const toggleSourceSelection = (srcName) => {
    setSelectedSources(prev => 
      prev.includes(srcName) 
        ? prev.filter(s => s !== srcName) 
        : [...prev, srcName]
    );
  };

  const handleSend = async (presetText = null) => {
    const queryText = presetText || input.trim();
    if (!queryText || loading) return;

    // Add user message to history
    const userMsg = { role: "user", text: queryText };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: queryText,
          selected_sources: selectedSources,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMsg = {
          role: "assistant",
          answer: data.answer,
          sources: data.sources,
          id: Date.now(),
        };
        setMessages(prev => [...prev, assistantMsg]);
        setActiveMsgId(assistantMsg.id); // Show this structured response on the right
      } else {
        const errData = await res.json();
        const errorMsg = {
          role: "assistant",
          error: true,
          answer: {
            rights: "Failed to generate structured response from backend.",
            eligibility: [],
            benefits: errData.detail || "API server error",
            risks: "Please verify uvicorn backend logs and your MISTRAL_API_KEY.",
          },
          sources: [],
          id: Date.now(),
        };
        setMessages(prev => [...prev, errorMsg]);
        setActiveMsgId(errorMsg.id);
      }
    } catch (err) {
      console.error("Error chatting:", err);
      const networkErrorMsg = {
        role: "assistant",
        error: true,
        answer: {
          rights: "Connection to API server failed.",
          eligibility: [],
          benefits: "Is the FastAPI server running on http://localhost:8000?",
          risks: "Please ensure uvicorn is running.",
        },
        sources: [],
        id: Date.now(),
      };
      setMessages(prev => [...prev, networkErrorMsg]);
      setActiveMsgId(networkErrorMsg.id);
    } finally {
      setLoading(false);
    }
  };

  // Get active structured response details to display on the right panel
  const getActiveResponse = () => {
    if (!activeMsgId) return null;
    return messages.find(m => m.id === activeMsgId && m.role === "assistant");
  };

  const activeResponse = getActiveResponse();

  return (
    <div className="app-container">
      {/* LEFT PANE: Sources & Chat */}
      <div className="left-pane">
        
        {/* Source Documents Panel */}
        <div className="sources-panel">
          <div className="sources-header">
            <span className="sources-title">
              <BookOpen size={16} /> Active Sources
            </span>
            <button 
              className="add-source-btn" 
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? (
                <Loader2 size={12} className="animate-spin" />
              ) : (
                <Plus size={12} />
              )}
              {uploading ? "Uploading..." : "Add Source"}
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: "none" }} 
              accept=".pdf"
              onChange={handleFileUpload} 
            />
          </div>

          <div className="sources-grid">
            {/* Global statutory PDF sources */}
            {sources.global_sources.map(src => {
              const isSelected = selectedSources.includes(src);
              return (
                <div 
                  key={src} 
                  className={`source-card ${isSelected ? "selected" : ""}`}
                  onClick={() => toggleSourceSelection(src)}
                >
                  {isSelected ? <CheckSquare size={13} style={{ color: "#38bdf8" }} /> : <Square size={13} style={{ color: "#94a3b8" }} />}
                  <span className="source-name" title={src}>{src}</span>
                </div>
              );
            })}
            
            {/* User-uploaded PDF sources */}
            {sources.user_sources.map(src => {
              const isSelected = selectedSources.includes(src);
              return (
                <div 
                  key={src} 
                  className={`source-card ${isSelected ? "selected" : ""}`}
                  onClick={() => toggleSourceSelection(src)}
                  style={{ borderStyle: "dashed" }}
                >
                  {isSelected ? <CheckSquare size={13} style={{ color: "#38bdf8" }} /> : <Square size={13} style={{ color: "#94a3b8" }} />}
                  <span className="source-name" title={src}>{src}</span>
                </div>
              );
            })}

            {sources.global_sources.length === 0 && sources.user_sources.length === 0 && (
              <div style={{ fontSize: "0.75rem", color: "#64748b", padding: "4px" }}>
                Loading source documents...
              </div>
            )}
          </div>
        </div>

        {/* Chat Timeline Panel */}
        <div className="chat-panel">
          <div className="chat-history">
            {messages.length === 0 ? (
              <div className="chat-welcome">
                <HelpCircle size={40} style={{ color: "#475569", marginBottom: 15 }} />
                <h4 style={{ color: "#cbd5e1", margin: "0 0 8px 0" }}>What is SAMA-VIDHANA?</h4>
                <p style={{ fontSize: "0.85rem", color: "#64748b", margin: 0, maxWidth: "300px", lineHeight: 1.5 }}>
                  Ask questions about Indian civic laws, acts, or upload your own legal notice to get a structured 4-part legal translation.
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message-wrapper ${msg.role}`}>
                  <div 
                    className={`message-bubble ${msg.role} ${activeMsgId === msg.id ? "active-response" : ""}`}
                    onClick={() => msg.role === "assistant" && setActiveMsgId(msg.id)}
                  >
                    {msg.role === "user" ? (
                      msg.text
                    ) : (
                      <div>
                        <strong>Summary of Rights:</strong> {msg.answer.rights.substring(0, 150)}...
                        <div style={{ fontSize: "0.72rem", color: "#38bdf8", marginTop: 4 }}>
                          Click to display detailed dashboard response
                        </div>
                      </div>
                    )}
                  </div>
                  <span className="message-time">
                    {msg.role === "user" ? "Citizen" : "SAMA-VIDHANA Assistant"}
                  </span>
                </div>
              ))
            )}
            {loading && (
              <div className="message-wrapper assistant">
                <div className="message-bubble assistant" style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <Loader2 size={16} className="animate-spin" />
                  Thinking and simplifying statutory clauses...
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Preset Suggestions */}
          <div className="suggestions-box">
            <button 
              className="suggestion-chip" 
              onClick={() => handleSend("What is the time limit if the requested information concerns the life or liberty of a person?")}
            >
              ⏱️ 48-Hour Liberty Rule
            </button>
            <button 
              className="suggestion-chip" 
              onClick={() => handleSend("What categories of information are exempt from disclosure under Section 8 of RTI?")}
            >
              🚫 Section 8 Exemptions
            </button>
            <button 
              className="suggestion-chip" 
              onClick={() => handleSend("What are the core tenant rights when a landlord keeps the security deposit?")}
            >
              🏠 Tenant Deposit Rights
            </button>
          </div>

          {/* User Input controls */}
          <div className="input-panel">
            <button 
              className="btn-icon" 
              title="Upload Document"
              onClick={() => fileInputRef.current?.click()}
            >
              <Paperclip size={18} />
            </button>
            
            <input 
              type="text" 
              className="chat-input" 
              placeholder={selectedSources.length > 0 
                ? `Querying ${selectedSources.length} selected source(s)...` 
                : "Ask SAMA-VIDHANA a civic / legal question..."}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSend()}
              disabled={loading}
            />

            <button 
              className="btn-icon send" 
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
            >
              <Send size={18} />
            </button>
          </div>
        </div>

      </div>

      {/* RIGHT PANE: Grounded Response Dashboard */}
      <div className="right-pane">
        
        {/* Horizontal Spatial 3D Logo */}
        <div className="logo-container">
          <div className="logo-3d-scene">
            <div className="logo-3d-prism">
              <div className="logo-face logo-face-en">🏛️ SAMA-VIDHANA</div>
              <div className="logo-face logo-face-hi">⚖️ सम-विधान</div>
              <div className="logo-face logo-face-kn">🏛️ ಸಮ-ವಿಧಾನ</div>
            </div>
          </div>
        </div>

        {activeResponse ? (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <h2 style={{ margin: 0, fontSize: "1.35rem", fontWeight: 800, color: "#f8fafc" }}>
                Statutory Civic Analysis
              </h2>
              {activeResponse.error && (
                <span className="badge required">API Connection Error</span>
              )}
            </div>

            {/* 1. RIGHTS */}
            <div className="dashboard-card">
              <div className="card-title-rights">
                <Scale size={18} /> 📜 Applicable Civic & Legal Rights
              </div>
              <div className="markdown-content">
                <p>{activeResponse.answer.rights}</p>
              </div>
            </div>

            {/* 2. ELIGIBILITY */}
            <div className="dashboard-card">
              <div className="card-title-eligibility">
                <ClipboardList size={18} /> 🎯 Eligibility & Statutory Conditions
              </div>
              {activeResponse.answer.eligibility && activeResponse.answer.eligibility.length > 0 ? (
                <table className="eligibility-table">
                  <thead>
                    <tr>
                      <th>Requirement / Condition</th>
                      <th style={{ textAlign: "right" }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeResponse.answer.eligibility.map((item, idx) => {
                      const stat = item.status || "Needed";
                      const statLower = stat.toLowerCase();
                      let badgeClass = "needed";
                      if (statLower.includes("satisfied") || statLower.includes("yes") || statLower.includes("pass") || statLower.includes("eligible")) {
                        badgeClass = "satisfied";
                      } else if (statLower.includes("required") || statLower.includes("fail") || statLower.includes("no") || statLower.includes("alert")) {
                        badgeClass = "required";
                      }
                      return (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{item.condition}</td>
                          <td style={{ textAlign: "right" }}>
                            <span className={`badge ${badgeClass}`}>{stat}</span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              ) : (
                <div style={{ fontSize: "0.85rem", color: "#64748b", fontStyle: "italic" }}>
                  No explicit eligibility criteria found in context.
                </div>
              )}
            </div>

            {/* 3. BENEFITS & ACTIONS */}
            <div className="dashboard-card">
              <div className="card-title-benefits">
                <Rocket size={18} /> 🚀 Actionable Benefits & Next Steps
              </div>
              <div className="markdown-content">
                <p>{activeResponse.answer.benefits}</p>
              </div>
            </div>

            {/* 4. RISKS & LIMITATIONS */}
            <div className="dashboard-card">
              <div className="card-title-risks">
                <AlertTriangle size={18} /> ⚠️ Critical Risks & Limitations
              </div>
              <div className="markdown-content" style={{ color: "#d97706" }}>
                <p>{activeResponse.answer.risks}</p>
              </div>
            </div>

            {/* 5. CITATIONS / REFERENCES */}
            {activeResponse.sources && activeResponse.sources.length > 0 && (
              <div>
                <div className="sources-title-container">
                  <FileText size={18} /> Verified Citations ({activeResponse.sources.length})
                </div>
                <div className="citation-list">
                  {activeResponse.sources.map((src, idx) => (
                    <div key={idx} className="citation-card">
                      <div className="citation-header">
                        <span>Citation {idx + 1}: {src.source}</span>
                        <span>Page {src.page}</span>
                      </div>
                      <div className="citation-snippet">
                        "{src.content}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Welcome State */
          <div style={{
            background: "rgba(30, 41, 59, 0.05)",
            border: "2px dashed rgba(255, 255, 255, 0.08)",
            padding: "50px 30px",
            borderRadius: "16px",
            minHeight: "450px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            textAlign: "center",
            marginTop: "10px"
          }}>
            <div style={{ fontSize: "4rem", marginBottom: 20 }}>⚖️</div>
            <h3 style={{ color: "#f8fafc", fontWeight: 800, fontSize: "1.5rem", margin: "0 0 10px 0" }}>
              Civic & Legal Response Dashboard
            </h3>
            <p style={{ color: "#94a3b8", fontSize: "0.95rem", maxWidth: "400px", lineHeight: 1.6, margin: "0 0 20px 0" }}>
              Select your source documents on the left panel, and ask SAMA-VIDHANA a query. The structured rights, eligibility checklist, benefits roadmap, and warning alerts will generate here in real-time.
            </p>
            <div style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 500 }}>
              Retrieves from global statutory codes (rti.pdf, wages.pdf, consumer.pdf, civil.pdf) and your own documents.
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
