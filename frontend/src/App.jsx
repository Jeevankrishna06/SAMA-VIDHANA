import { ScrollProgress } from "../components/motion-primitives/scroll-progress";
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
  HelpCircle,
  Download,
  Copy,
  Check,
  Compass,
  Search,
  Sun,
  Moon,
} from "lucide-react";

const disputeCategories = [
  "Consumer Defect & Service Deficiency (E-commerce, Electronics, Airlines, Banking)",
  "Real Estate & Builder Delay (RERA, Possession, Undisclosed Charges)",
  "Tenant & Landlord Dispute (Deposit Retention, Eviction, Maintenance)",
  "Labor & Employment (Unpaid Wages, Wrongful Termination, Gratuity)",
  "Cyber Crime & Financial Fraud (UPI Fraud, Phishing, Identity Theft)",
  "Civic Negligence & Municipal Failure (Sanitation, Illegal Encroachment, Potholes)",
];

const grievanceStages = [
  "No action taken yet (Initial occurrence)",
  "Verbal or informal request made, but ignored",
  "Formal written email / grievance ticket submitted (No resolution)",
  "Opposing party explicitly rejected claim or issued counter-notice",
  "Police / Local authority complaint filed (Awaiting follow-up)",
];

const parseMarkdownText = (text) => {
  if (!text) return null;
  return text.split("\n").map((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) return <div key={idx} style={{ height: 6 }} />;

    if (trimmed.startsWith("###")) {
      return (
        <h4
          key={idx}
          style={{
            color: "#38bdf8",
            marginTop: 12,
            marginBottom: 6,
            fontSize: "0.95rem",
            fontWeight: 700,
          }}
        >
          {trimmed.replace("###", "").trim()}
        </h4>
      );
    } else if (trimmed.startsWith("##")) {
      return (
        <h3
          key={idx}
          style={{
            color: "#818cf8",
            marginTop: 16,
            marginBottom: 8,
            fontSize: "1.05rem",
            fontWeight: 700,
          }}
        >
          {trimmed.replace("##", "").trim()}
        </h3>
      );
    } else if (trimmed.startsWith("#")) {
      return (
        <h2
          key={idx}
          style={{
            color: "#c084fc",
            marginTop: 20,
            marginBottom: 10,
            fontSize: "1.15rem",
            fontWeight: 700,
          }}
        >
          {trimmed.replace("#", "").trim()}
        </h2>
      );
    } else if (trimmed.startsWith("-") || trimmed.startsWith("*")) {
      const bulletText = trimmed.replace(/^[-*]\s+/, "");
      const parts = bulletText.split("**");
      return (
        <li
          key={idx}
          style={{
            marginLeft: 15,
            listStyleType: "disc",
            marginBottom: 4,
            color: "#cbd5e1",
          }}
        >
          {parts.map((part, pIdx) =>
            pIdx % 2 === 1 ? <strong key={pIdx}>{part}</strong> : part,
          )}
        </li>
      );
    } else {
      const parts = line.split("**");
      return (
        <p key={idx} style={{ margin: "0 0 8px 0" }}>
          {parts.map((part, pIdx) =>
            pIdx % 2 === 1 ? <strong key={pIdx}>{part}</strong> : part,
          )}
        </p>
      );
    }
  });
};

export default function App() {
  // State for theme: light or dark
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("theme") || "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  // State for global tab navigation
  const [activeTab, setActiveTab] = useState("law-explainer"); // law-explainer, form-filler, schemes, triage

  // Tab 1: Law Explainer State
  const [sources, setSources] = useState({
    global_sources: [],
    user_sources: [],
  });
  const [selectedSources, setSelectedSources] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeMsgId, setActiveMsgId] = useState(null);

  // Tab 2: Form Filler State
  const [formType, setFormType] = useState(
    "Right to Information (RTI) Application [Sec 6(1) RTI Act 2005]",
  );
  const [formDetails, setFormDetails] = useState({
    applicantName: "",
    applicantAddress: "",
    targetAuthority: "",
    incidentDate: "",
    reliefSought: "",
    additionalNotes: "",
  });
  const [formGenerating, setFormGenerating] = useState(false);
  const [generatedForm, setGeneratedForm] = useState("");
  const [formCopied, setFormCopied] = useState(false);

  // Tab 3: Scheme Eligibility State
  const [citizenProfile, setCitizenProfile] = useState({
    category: "All Categories",
    age: 35,
    income: "< ₹1,00,000 (BPL / Deprived)",
    occupation: "Small / Marginal Farmer",
  });
  const [schemeQuery, setSchemeQuery] = useState("");
  const [schemesLoading, setSchemesLoading] = useState(false);
  const [matchedSchemes, setMatchedSchemes] = useState([]);

  // Tab 4: Situational Triage State
  const [triageDetails, setTriageDetails] = useState({
    category:
      "Consumer Defect & Service Deficiency (E-commerce, Electronics, Airlines, Banking)",
    jurisdiction: "",
    opposingParty: "",
    status: "No action taken yet (Initial occurrence)",
    documents: "",
    description: "",
  });
  const [triageLoading, setTriageLoading] = useState(false);
  const [triageReport, setTriageReport] = useState("");
  const [triageCopied, setTriageCopied] = useState(false);

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
      const res = await fetch("/api/sources");
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
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setSelectedSources((prev) => [...prev, data.filename]);
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
    setSelectedSources((prev) =>
      prev.includes(srcName)
        ? prev.filter((s) => s !== srcName)
        : [...prev, srcName],
    );
  };

  const handleSend = async (presetText = null) => {
    const queryText = presetText || input.trim();
    if (!queryText || loading) return;

    const userMsg = { role: "user", text: queryText };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
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
        setMessages((prev) => [...prev, assistantMsg]);
        setActiveMsgId(assistantMsg.id);
      } else {
        const errData = await res.json();
        const errorMsg = {
          role: "assistant",
          error: true,
          answer: {
            rights: "Failed to generate structured response from backend.",
            eligibility: [],
            benefits: errData.detail || "API server error",
            risks:
              "Please verify uvicorn backend logs and your MISTRAL_API_KEY.",
          },
          sources: [],
          id: Date.now(),
        };
        setMessages((prev) => [...prev, errorMsg]);
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
      setMessages((prev) => [...prev, networkErrorMsg]);
      setActiveMsgId(networkErrorMsg.id);
    } finally {
      setLoading(false);
    }
  };

  const getActiveResponse = () => {
    if (!activeMsgId) return null;
    return messages.find((m) => m.id === activeMsgId && m.role === "assistant");
  };

  const activeResponse = getActiveResponse();

  // Tab 2: Form Filler Handler
  const handleGenerateForm = async (e) => {
    e.preventDefault();
    if (
      !formDetails.applicantName ||
      !formDetails.targetAuthority ||
      !formDetails.reliefSought
    ) {
      alert(
        "Please fill in Applicant Name, Target Department/Opposite Party, and Specific Information/Remedy.",
      );
      return;
    }
    setFormGenerating(true);
    try {
      const res = await fetch("/api/generate-form", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          form_type: formType,
          details: {
            "Applicant Name": formDetails.applicantName,
            "Applicant Address & Contact": formDetails.applicantAddress,
            "Target Department / Opposite Party": formDetails.targetAuthority,
            "Relevant Dates": formDetails.incidentDate,
            "Information / Remedy / Relief Demanded": formDetails.reliefSought,
            "Additional Context & Reference Numbers":
              formDetails.additionalNotes,
          },
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedForm(data.generated_text);
      } else {
        alert("Failed to generate application from backend.");
      }
    } catch (err) {
      console.error(err);
      alert("Error generating form.");
    } finally {
      setFormGenerating(false);
    }
  };

  // Tab 3: Welfare Schemes Search Handler
  const handleFindSchemes = async () => {
    setSchemesLoading(true);
    try {
      const res = await fetch("/api/schemes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: schemeQuery,
          category: citizenProfile.category,
          age: citizenProfile.age,
          income: citizenProfile.income,
          occupation: citizenProfile.occupation,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setMatchedSchemes(data.schemes || []);
      } else {
        alert("Failed to find schemes from backend.");
      }
    } catch (err) {
      console.error(err);
      alert("Error searching welfare schemes.");
    } finally {
      setSchemesLoading(false);
    }
  };

  // Tab 4: Situational Triage Handler
  const handleRunTriage = async (e) => {
    e.preventDefault();
    if (
      !triageDetails.description ||
      triageDetails.description.trim().length < 15
    ) {
      alert(
        "Please provide a narrative description of at least 15 characters.",
      );
      return;
    }
    setTriageLoading(true);
    try {
      const res = await fetch("/api/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category: triageDetails.category,
          jurisdiction: triageDetails.jurisdiction,
          description: triageDetails.description,
          opposing_party: triageDetails.opposingParty,
          status: triageDetails.status,
          documents: triageDetails.documents,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setTriageReport(data.triage_report);
      } else {
        alert("Failed to analyze dispute from backend.");
      }
    } catch (err) {
      console.error(err);
      alert("Error running dispute triage.");
    } finally {
      setTriageLoading(false);
    }
  };

  // File Download Helpers
  const handleDownloadTxt = (text, filename) => {
    const element = document.createElement("a");
    const file = new Blob([text], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleCopyText = (text, setCopiedState) => {
    navigator.clipboard.writeText(text);
    setCopiedState(true);
    setTimeout(() => setCopiedState(false), 2000);
  };

  // Render Spatial 3D Logo (reusable)
  const render3DLogo = () => (
    <div className="logo-container">
      <div className="logo-3d-scene">
        <div className="logo-3d-prism">
          <div className="logo-face logo-face-en">🏛️ SAMA-VIDHANA</div>
          <div className="logo-face logo-face-hi">⚖️ सम-विधान</div>
          <div className="logo-face logo-face-kn">🏛️ ಸಮ-ವಿಧಾನ</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app-wrapper">
      <ScrollProgress />

      {/* GLOBAL HEADER BAR */}
      <header className="app-header">
        <div className="header-info">
          <h1 className="header-title">🏛️ SAMA-VIDHANA</h1>
          <p className="header-subtitle">
            Civic & Legal Empowerment AI Assistant • Powered by Mistral 7B &
            FAISS RAG
          </p>
        </div>

        {/* Dynamic Navigation Tabs */}
        <div className="tabs-navigation">
          <button
            className={`tab-btn ${activeTab === "law-explainer" ? "active" : ""}`}
            onClick={() => setActiveTab("law-explainer")}
          >
            <BookOpen size={15} /> Law Explainer
          </button>
          <button
            className={`tab-btn ${activeTab === "form-filler" ? "active" : ""}`}
            onClick={() => setActiveTab("form-filler")}
          >
            <FileText size={15} /> Form-Filler
          </button>
          <button
            className={`tab-btn ${activeTab === "schemes" ? "active" : ""}`}
            onClick={() => setActiveTab("schemes")}
          >
            <ClipboardList size={15} /> Schemes Eligibility
          </button>
          <button
            className={`tab-btn ${activeTab === "triage" ? "active" : ""}`}
            onClick={() => setActiveTab("triage")}
          >
            <Compass size={15} /> Situational Triage
          </button>
        </div>

        <div className="header-badges">
          <button
            onClick={toggleTheme}
            className="theme-toggle-btn"
            title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              color: "var(--text-color)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "8px",
              borderRadius: "50%",
              marginRight: "8px",
              transition: "all 0.2s ease"
            }}
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <span className="badge-pill">open-mistral-7b</span>
          <span className="badge-pill">Grounded RAG</span>
        </div>
      </header>

      {/* CORE VIEWPORT */}
      <div className="app-content">
        {/* TAB 1: LAW EXPLAINER */}
        {activeTab === "law-explainer" && (
          <div
            className="app-container"
            style={{ width: "100%", height: "100%" }}
          >
            {/* LEFT PANE: Sources & Chat */}
            <div className="left-pane">
              {/* Source Documents Panel */}
              <div className="sources-panel" style={{ display: "none" }}>
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
                  {sources.global_sources.map((src) => {
                    const isSelected = selectedSources.includes(src);
                    return (
                      <div
                        key={src}
                        className={`source-card ${isSelected ? "selected" : ""}`}
                        onClick={() => toggleSourceSelection(src)}
                      >
                        {isSelected ? (
                          <CheckSquare size={13} style={{ color: "#38bdf8" }} />
                        ) : (
                          <Square size={13} style={{ color: "#94a3b8" }} />
                        )}
                        <span className="source-name" title={src}>
                          {src}
                        </span>
                      </div>
                    );
                  })}

                  {/* User-uploaded PDF sources */}
                  {sources.user_sources.map((src) => {
                    const isSelected = selectedSources.includes(src);
                    return (
                      <div
                        key={src}
                        className={`source-card ${isSelected ? "selected" : ""}`}
                        onClick={() => toggleSourceSelection(src)}
                        style={{ borderStyle: "dashed" }}
                      >
                        {isSelected ? (
                          <CheckSquare size={13} style={{ color: "#38bdf8" }} />
                        ) : (
                          <Square size={13} style={{ color: "#94a3b8" }} />
                        )}
                        <span className="source-name" title={src}>
                          {src}
                        </span>
                      </div>
                    );
                  })}

                  {sources.global_sources.length === 0 &&
                    sources.user_sources.length === 0 && (
                      <div
                        style={{
                          fontSize: "0.75rem",
                          color: "#64748b",
                          padding: "4px",
                        }}
                      >
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
                      <HelpCircle
                        size={40}
                        style={{ color: "var(--text-muted)", marginBottom: 15 }}
                      />
                      <h4 style={{ color: "var(--text-color)", margin: "0 0 8px 0" }}>
                        What is SAMA-VIDHANA?
                      </h4>
                      <p
                        style={{
                          fontSize: "0.85rem",
                          color: "var(--text-muted)",
                          margin: 0,
                          maxWidth: "300px",
                          lineHeight: 1.5,
                        }}
                      >
                        Ask questions about Indian civic laws, acts, or upload
                        your own legal notice to get a structured 4-part legal
                        translation.
                      </p>
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div key={idx} className={`message-wrapper ${msg.role}`}>
                        <div
                          className={`message-bubble ${msg.role} ${activeMsgId === msg.id ? "active-response" : ""}`}
                          onClick={() =>
                            msg.role === "assistant" && setActiveMsgId(msg.id)
                          }
                        >
                          {msg.role === "user" ? (
                            msg.text
                          ) : (
                            <div>
                              <strong>Summary of Rights:</strong>{" "}
                              {msg.answer?.rights
                                ? msg.answer.rights.substring(0, 150)
                                : ""}
                              ...
                              <div
                                style={{
                                  fontSize: "0.72rem",
                                  color: "#38bdf8",
                                  marginTop: 4,
                                }}
                              >
                                Click to display detailed dashboard response
                              </div>
                            </div>
                          )}
                        </div>
                        <span className="message-time">
                          {msg.role === "user"
                            ? "Citizen"
                            : "SAMA-VIDHANA Assistant"}
                        </span>
                      </div>
                    ))
                  )}
                  {loading && (
                    <div className="message-wrapper assistant">
                      <div
                        className="message-bubble assistant"
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                        }}
                      >
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
                    onClick={() =>
                      handleSend(
                        "What is the time limit if the requested information concerns the life or liberty of a person?",
                      )
                    }
                  >
                    ⏱️ 48-Hour Liberty Rule
                  </button>
                  <button
                    className="suggestion-chip"
                    onClick={() =>
                      handleSend(
                        "What categories of information are exempt from disclosure under Section 8 of RTI?",
                      )
                    }
                  >
                    🚫 Section 8 Exemptions
                  </button>
                  <button
                    className="suggestion-chip"
                    onClick={() =>
                      handleSend(
                        "What are the core tenant rights when a landlord keeps the security deposit?",
                      )
                    }
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
                    placeholder={
                      selectedSources.length > 0
                        ? `Querying ${selectedSources.length} selected source(s)...`
                        : "Ask SAMA-VIDHANA a civic / legal question..."
                    }
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
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
              {render3DLogo()}

              {activeResponse ? (
                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 20,
                    }}
                  >
                    <h2
                      style={{
                        margin: 0,
                        fontSize: "1.35rem",
                        fontWeight: 800,
                        color: "var(--text-color)",
                      }}
                    >
                      Statutory Civic Analysis
                    </h2>
                    {activeResponse.error && (
                      <span className="badge required">
                        API Connection Error
                      </span>
                    )}
                  </div>

                  {/* 1. RIGHTS */}
                  <div className="dashboard-card">
                    <div className="card-title-rights">
                      <Scale size={18} /> 📜 Applicable Civic & Legal Rights
                    </div>
                    <div className="markdown-content">
                      {parseMarkdownText(activeResponse.answer.rights)}
                    </div>
                  </div>

                  {/* 2. ELIGIBILITY */}
                  <div className="dashboard-card">
                    <div className="card-title-eligibility">
                      <ClipboardList size={18} /> 🎯 Eligibility & Statutory
                      Conditions
                    </div>
                    {activeResponse.answer.eligibility &&
                      activeResponse.answer.eligibility.length > 0 ? (
                      <table className="eligibility-table">
                        <thead>
                          <tr>
                            <th>Requirement / Condition</th>
                            <th style={{ textAlign: "right" }}>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {activeResponse.answer.eligibility.map(
                            (item, idx) => {
                              const stat = item.status || "Needed";
                              const statLower = stat.toLowerCase();
                              let badgeClass = "needed";
                              if (
                                statLower.includes("satisfied") ||
                                statLower.includes("yes") ||
                                statLower.includes("pass") ||
                                statLower.includes("eligible")
                              ) {
                                badgeClass = "satisfied";
                              } else if (
                                statLower.includes("required") ||
                                statLower.includes("fail") ||
                                statLower.includes("no") ||
                                statLower.includes("alert")
                              ) {
                                badgeClass = "required";
                              }
                              return (
                                <tr key={idx}>
                                  <td style={{ fontWeight: 600 }}>
                                    {item.condition}
                                  </td>
                                  <td style={{ textAlign: "right" }}>
                                    <span className={`badge ${badgeClass}`}>
                                      {stat}
                                    </span>
                                  </td>
                                </tr>
                              );
                            },
                          )}
                        </tbody>
                      </table>
                    ) : (
                      <div
                        style={{
                          fontSize: "0.85rem",
                          color: "#64748b",
                          fontStyle: "italic",
                        }}
                      >
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
                      {parseMarkdownText(activeResponse.answer.benefits)}
                    </div>
                  </div>

                  {/* 4. RISKS & LIMITATIONS */}
                  <div className="dashboard-card">
                    <div className="card-title-risks">
                      <AlertTriangle size={18} /> ⚠️ Critical Risks &
                      Limitations
                    </div>
                    <div
                      className="markdown-content"
                      style={{ color: "#d97706" }}
                    >
                      {parseMarkdownText(activeResponse.answer.risks)}
                    </div>
                  </div>

                  {/* 5. CITATIONS / REFERENCES */}
                  {activeResponse.sources &&
                    activeResponse.sources.length > 0 && (
                      <div>
                        <div className="sources-title-container">
                          <FileText size={18} /> Verified Citations (
                          {activeResponse.sources.length})
                        </div>
                        <div className="citation-list">
                          {activeResponse.sources.map((src, idx) => (
                            <div key={idx} className="citation-card">
                              <div className="citation-header">
                                <span>
                                  Citation {idx + 1}: {src.source}
                                </span>
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
                <div
                  style={{
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
                    marginTop: "10px",
                  }}
                >
                  <div style={{ fontSize: "4rem", marginBottom: 20 }}>⚖️</div>
                  <h3
                    style={{
                      color: "var(--text-color)",
                      fontWeight: 800,
                      fontSize: "1.5rem",
                      margin: "0 0 10px 0",
                    }}
                  >
                    Civic & Legal Response Dashboard
                  </h3>
                  <p
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "0.95rem",
                      maxWidth: "400px",
                      lineHeight: 1.6,
                      margin: "0 0 20px 0",
                    }}
                  >
                    Select your source documents on the left panel, and ask
                    SAMA-VIDHANA a query. The structured rights, eligibility
                    checklist, benefits roadmap, and warning alerts will
                    generate here in real-time.
                  </p>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: "#64748b",
                      fontWeight: 500,
                    }}
                  >
                    Retrieves from global statutory codes (rti.pdf, wages.pdf,
                    consumer.pdf, civil.pdf) and your own documents.
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: PLAINTEXT FORM-FILLER */}
        {activeTab === "form-filler" && (
          <div
            className="app-container"
            style={{ width: "100%", height: "100%" }}
          >
            {/* LEFT PANE: Form Inputs */}
            <div className="left-pane" style={{ overflowY: "auto" }}>
              <form className="form-container" onSubmit={handleGenerateForm}>
                <div className="form-title-bar">
                  <h3 className="form-title">
                    📝 Conversational Legal Drafter
                  </h3>
                  <p className="form-subtitle">
                    Create standardized legal notices and RTI applications. Fill
                    details below and AI will format it correctly.
                  </p>
                </div>

                <div className="form-group">
                  <label>Application / Notice Type</label>
                  <select
                    className="form-select"
                    value={formType}
                    onChange={(e) => setFormType(e.target.value)}
                  >
                    <option value="Right to Information (RTI) Application [Sec 6(1) RTI Act 2005]">
                      Right to Information (RTI) Application [Sec 6(1) RTI Act
                      2005]
                    </option>
                    <option value="Consumer Grievance Legal Demand Notice [Consumer Protection Act 2019]">
                      Consumer Grievance Legal Demand Notice [Consumer
                      Protection Act 2019]
                    </option>
                    <option value="Tenant Security Deposit Refund Demand Notice">
                      Tenant Security Deposit Refund Demand Notice
                    </option>
                    <option value="Public Grievance & Municipal Complaint (Civic Negligence)">
                      Public Grievance & Municipal Complaint (Civic Negligence)
                    </option>
                    <option value="Formal Representation to Government Department / Public Authority">
                      Formal Representation to Government Department / Public
                      Authority
                    </option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Applicant Full Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Rajesh Kumar"
                    value={formDetails.applicantName}
                    onChange={(e) =>
                      setFormDetails((prev) => ({
                        ...prev,
                        applicantName: e.target.value,
                      }))
                    }
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Applicant Full Address & Contact</label>
                  <textarea
                    className="form-textarea"
                    placeholder="e.g. Flat 402, Green Valley Apartments, Bengaluru, Karnataka - 560001&#10;Phone: +91 9876543210&#10;Email: rajesh@example.com"
                    value={formDetails.applicantAddress}
                    onChange={(e) =>
                      setFormDetails((prev) => ({
                        ...prev,
                        applicantAddress: e.target.value,
                      }))
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Target Department / Opposite Party Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Public Information Officer, Bengaluru Development Authority (BDA)"
                    value={formDetails.targetAuthority}
                    onChange={(e) =>
                      setFormDetails((prev) => ({
                        ...prev,
                        targetAuthority: e.target.value,
                      }))
                    }
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Relevant Date(s) / Timeline</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. 15th January 2024 to 10th February 2024"
                    value={formDetails.incidentDate}
                    onChange={(e) =>
                      setFormDetails((prev) => ({
                        ...prev,
                        incidentDate: e.target.value,
                      }))
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Specific Information / Remedy Demanded</label>
                  <textarea
                    className="form-textarea"
                    placeholder="e.g. Certified copies of road inspection reports and sanctioned budget for 100 Feet Ring Road."
                    value={formDetails.reliefSought}
                    onChange={(e) =>
                      setFormDetails((prev) => ({
                        ...prev,
                        reliefSought: e.target.value,
                      }))
                    }
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Key Facts / Previous Communications</label>
                  <textarea
                    className="form-textarea"
                    placeholder="e.g. Complaint token #8392 filed on municipal portal with no response for 45 days."
                    value={formDetails.additionalNotes}
                    onChange={(e) =>
                      setFormDetails((prev) => ({
                        ...prev,
                        additionalNotes: e.target.value,
                      }))
                    }
                  />
                </div>

                <button
                  type="submit"
                  className="form-submit-btn"
                  disabled={formGenerating}
                >
                  {formGenerating ? (
                    <>
                      <Loader2 size={16} className="animate-spin" /> Drafting
                      Application...
                    </>
                  ) : (
                    <>
                      <Rocket size={16} /> Draft Application / Notice
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* RIGHT PANE: Output View */}
            <div className="right-pane">
              {render3DLogo()}

              {generatedForm ? (
                <div className="plaintext-output-container">
                  <div className="plaintext-output-header">
                    <h2
                      style={{
                        margin: 0,
                        fontSize: "1.2rem",
                        fontWeight: 800,
                        color: "var(--text-color)",
                      }}
                    >
                      📄 Formatted Legal Plaintext Document
                    </h2>
                  </div>

                  <div className="paper-letter-container">
                    <div className="paper-sheet">
                      <div className="paper-red-margin" />
                      <pre className="paper-content">{generatedForm}</pre>
                    </div>
                  </div>

                  <div className="action-bar">
                    <button
                      className="btn-action primary"
                      onClick={() =>
                        handleCopyText(generatedForm, setFormCopied)
                      }
                    >
                      {formCopied ? <Check size={14} /> : <Copy size={14} />}
                      {formCopied ? "Copied!" : "Copy to Clipboard"}
                    </button>

                    <button
                      className="btn-action"
                      onClick={() =>
                        handleDownloadTxt(
                          generatedForm,
                          `${formType.slice(0, 15).replace(/\s+/g, "_")}_Application.txt`,
                        )
                      }
                    >
                      <Download size={14} /> Download as .txt
                    </button>
                  </div>
                </div>
              ) : (
                <div
                  style={{
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
                    marginTop: "10px",
                  }}
                >
                  <div style={{ fontSize: "4rem", marginBottom: 20 }}>📝</div>
                  <h3
                    style={{
                      color: "var(--text-color)",
                      fontWeight: 800,
                      fontSize: "1.5rem",
                      margin: "0 0 10px 0",
                    }}
                  >
                    Standardized Drafting Panel
                  </h3>
                  <p
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "0.95rem",
                      maxWidth: "400px",
                      lineHeight: 1.6,
                      margin: "0 0 20px 0",
                    }}
                  >
                    Fill out the applicant details, date timeline, opposing
                    party, and remedy requested in the left panel. SAMA-VIDHANA
                    will generate a formatted, ready-to-copy plaintext
                    application according to Indian statutory rules.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: SCHEME ELIGIBILITY */}
        {activeTab === "schemes" && (
          <div
            className="app-container"
            style={{ width: "100%", height: "100%" }}
          >
            {/* LEFT PANE: Profile Filter & Search */}
            <div className="left-pane" style={{ overflowY: "auto" }}>
              <div className="form-container">
                <div className="form-title-bar">
                  <h3 className="form-title">👤 Citizen Profile & Need</h3>
                  <p className="form-subtitle">
                    Search for central and state government schemes matching
                    your profile and household needs.
                  </p>
                </div>

                <div className="form-group">
                  <label>Target Category</label>
                  <select
                    className="form-select"
                    value={citizenProfile.category}
                    onChange={(e) =>
                      setCitizenProfile((prev) => ({
                        ...prev,
                        category: e.target.value,
                      }))
                    }
                  >
                    <option value="All Categories">All Categories</option>
                    <option value="Agriculture & Farmers">
                      Agriculture & Farmers
                    </option>
                    <option value="Healthcare & Social Security">
                      Healthcare & Social Security
                    </option>
                    <option value="Women & Child Development">
                      Women & Child Development
                    </option>
                    <option value="Housing & Urban Affairs">
                      Housing & Urban Affairs
                    </option>
                    <option value="Micro-Enterprise & Self Employment">
                      Micro-Enterprise & Self Employment
                    </option>
                    <option value="Senior Citizens & Social Welfare">
                      Senior Citizens & Social Welfare
                    </option>
                    <option value="Artisans & Traditional Craftspeople">
                      Artisans & Traditional Craftspeople
                    </option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Citizen Age</label>
                  <input
                    type="number"
                    className="form-input"
                    min="1"
                    max="110"
                    value={citizenProfile.age}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val === "") {
                        setCitizenProfile((prev) => ({ ...prev, age: "" }));
                      } else {
                        const parsed = parseInt(val);
                        setCitizenProfile((prev) => ({
                          ...prev,
                          age: isNaN(parsed) ? "" : parsed,
                        }));
                      }
                    }}
                  />
                </div>

                <div className="form-group">
                  <label>Annual Household Income</label>
                  <select
                    className="form-select"
                    value={citizenProfile.income}
                    onChange={(e) =>
                      setCitizenProfile((prev) => ({
                        ...prev,
                        income: e.target.value,
                      }))
                    }
                  >
                    <option value="< ₹1,00,000 (BPL / Deprived)">
                      &lt; ₹1,00,000 (BPL / Deprived)
                    </option>
                    <option value="₹1,00,000 - ₹3,00,000 (EWS)">
                      ₹1,00,000 - ₹3,00,000 (EWS)
                    </option>
                    <option value="₹3,00,000 - ₹6,00,000 (LIG)">
                      ₹3,00,000 - ₹6,00,000 (LIG)
                    </option>
                    <option value="> ₹6,00,000 (MIG/General)">
                      &gt; ₹6,00,000 (MIG/General)
                    </option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Occupation / Status</label>
                  <select
                    className="form-select"
                    value={citizenProfile.occupation}
                    onChange={(e) =>
                      setCitizenProfile((prev) => ({
                        ...prev,
                        occupation: e.target.value,
                      }))
                    }
                  >
                    <option value="Small / Marginal Farmer">
                      Small / Marginal Farmer
                    </option>
                    <option value="Daily Wage / Unorganized Worker">
                      Daily Wage / Unorganized Worker
                    </option>
                    <option value="Street Vendor / Hawker">
                      Street Vendor / Hawker
                    </option>
                    <option value="Traditional Artisan / Craftsperson">
                      Traditional Artisan / Craftsperson
                    </option>
                    <option value="Self-Employed / Small Business">
                      Self-Employed / Small Business
                    </option>
                    <option value="Senior Citizen">Senior Citizen</option>
                    <option value="Homemaker / Mother">
                      Homemaker / Mother
                    </option>
                    <option value="Salaried / Other">Salaried / Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Situation or Need (Natural Language Search)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Free health insurance coverage for elderly parents above 70 years"
                    value={schemeQuery}
                    onChange={(e) => setSchemeQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleFindSchemes()}
                  />
                </div>

                <div className="suggestions-box" style={{ padding: 0 }}>
                  <button
                    type="button"
                    className="suggestion-chip"
                    onClick={() => {
                      setSchemeQuery(
                        "Direct cash transfer income support for farmers",
                      );
                    }}
                  >
                    🌾 Farmer Income Support
                  </button>
                  <button
                    type="button"
                    className="suggestion-chip"
                    onClick={() => {
                      setSchemeQuery(
                        "Ayushman Bharat cashless health insurance coverage",
                      );
                    }}
                  >
                    🏥 ₹5 Lakh Free Hospitalization
                  </button>
                  <button
                    type="button"
                    className="suggestion-chip"
                    onClick={() => {
                      setSchemeQuery(
                        "PM Vishwakarma toolkits and collateral free loan for artisans",
                      );
                    }}
                  >
                    🔨 Collateral-Free Artisan Loans
                  </button>
                </div>

                <button
                  type="button"
                  className="form-submit-btn"
                  onClick={handleFindSchemes}
                  disabled={schemesLoading}
                >
                  {schemesLoading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" /> Searching
                      Database...
                    </>
                  ) : (
                    <>
                      <Search size={16} /> Find Matching Welfare Schemes
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* RIGHT PANE: Results cards */}
            <div className="right-pane">
              {render3DLogo()}

              {matchedSchemes.length > 0 ? (
                <div className="schemes-list-container">
                  <h2
                    style={{
                      margin: "0 0 10px 0",
                      fontSize: "1.20rem",
                      fontWeight: 800,
                      color: "var(--text-color)",
                    }}
                  >
                    🎯 Found {matchedSchemes.length} Matching Welfare Scheme(s)
                  </h2>

                  {matchedSchemes.map((sch, i) => (
                    <div key={i} className="scheme-card-item">
                      <div className="scheme-card-header">
                        <h4 className="scheme-card-title">🏛️ {sch.name}</h4>
                        <div className="scheme-card-meta">
                          Category: <strong>{sch.category}</strong> | Ministry:{" "}
                          <strong>{sch.ministry}</strong>
                        </div>
                      </div>
                      <div className="scheme-card-body">{sch.content}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div
                  style={{
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
                    marginTop: "10px",
                  }}
                >
                  <div style={{ fontSize: "4rem", marginBottom: 20 }}>🎯</div>
                  <h3
                    style={{
                      color: "var(--text-color)",
                      fontWeight: 800,
                      fontSize: "1.5rem",
                      margin: "0 0 10px 0",
                    }}
                  >
                    Citizen Welfare Scheme Matching
                  </h3>
                  <p
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "0.95rem",
                      maxWidth: "400px",
                      lineHeight: 1.6,
                      margin: "0 0 20px 0",
                    }}
                  >
                    Set up your citizen profile variables on the left, or search
                    for a specific need. SAMA-VIDHANA indexes major Indian
                    Welfare Schemes (like PM-KISAN, Ayushman Bharat, PMAY,
                    Sukanya Samriddhi) to find the best match.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: SITUATIONAL TRIAGE */}
        {activeTab === "triage" && (
          <div
            className="app-container"
            style={{ width: "100%", height: "100%" }}
          >
            {/* LEFT PANE: Dispute Form */}
            <div className="left-pane" style={{ overflowY: "auto" }}>
              <form className="form-container" onSubmit={handleRunTriage}>
                <div className="form-title-bar">
                  <h3 className="form-title">
                    🧭 Legal Routing & Dispute Intake
                  </h3>
                  <p className="form-subtitle">
                    Analyze a legal conflict, evaluate deadlines/limitations,
                    and find the appropriate ombudsman or commission.
                  </p>
                </div>

                <div className="form-group">
                  <label>Dispute Category</label>
                  <select
                    className="form-select"
                    value={triageDetails.category}
                    onChange={(e) =>
                      setTriageDetails((prev) => ({
                        ...prev,
                        category: e.target.value,
                      }))
                    }
                  >
                    {disputeCategories.map((cat, idx) => (
                      <option key={idx} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>State / City / District</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Pune, Maharashtra"
                    value={triageDetails.jurisdiction}
                    onChange={(e) =>
                      setTriageDetails((prev) => ({
                        ...prev,
                        jurisdiction: e.target.value,
                      }))
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Opposing Entity Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. XYZ E-Commerce Pvt Ltd / ABC Builder"
                    value={triageDetails.opposingParty}
                    onChange={(e) =>
                      setTriageDetails((prev) => ({
                        ...prev,
                        opposingParty: e.target.value,
                      }))
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Current Stage of Grievance</label>
                  <select
                    className="form-select"
                    value={triageDetails.status}
                    onChange={(e) =>
                      setTriageDetails((prev) => ({
                        ...prev,
                        status: e.target.value,
                      }))
                    }
                  >
                    {grievanceStages.map((stg, idx) => (
                      <option key={idx} value={stg}>
                        {stg}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Available Evidence / Proof</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Invoice, payment receipts, email trail, WhatsApp chats, photos"
                    value={triageDetails.documents}
                    onChange={(e) =>
                      setTriageDetails((prev) => ({
                        ...prev,
                        documents: e.target.value,
                      }))
                    }
                  />
                </div>

                <div className="form-group">
                  <label>
                    Detailed Incident Narrative (What happened? financial loss?)
                  </label>
                  <textarea
                    className="form-textarea"
                    placeholder="e.g. Ordered a laptop worth ₹65,000 on 12th Jan 2024. Received damaged unit. Requested replacement within 7-day window. Customer support closed ticket citing policy without replacement or refund."
                    value={triageDetails.description}
                    onChange={(e) =>
                      setTriageDetails((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                    style={{ minHeight: "110px" }}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="form-submit-btn"
                  disabled={triageLoading}
                >
                  {triageLoading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" /> Analyzing
                      Situation...
                    </>
                  ) : (
                    <>
                      <Compass size={16} /> Analyze Dispute & Create Roadmap
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* RIGHT PANE: Action Plan / Roadmap display */}
            <div className="right-pane">
              {render3DLogo()}

              {triageReport ? (
                <div className="triage-roadmap-container">
                  <div className="plaintext-output-header">
                    <h2
                      style={{
                        margin: 0,
                        fontSize: "1.2rem",
                        fontWeight: 800,
                        color: "var(--text-color)",
                      }}
                    >
                      📊 Procedural Triage & Action Roadmap
                    </h2>
                  </div>

                  <div className="triage-roadmap-content">
                    {/* Basic Markdown Parser for headings/bold/lists */}
                    {triageReport.split("\n").map((line, idx) => {
                      if (line.startsWith("###")) {
                        return (
                          <h4
                            key={idx}
                            style={{
                              color: "#38bdf8",
                              marginTop: 12,
                              marginBottom: 6,
                              fontSize: "1rem",
                            }}
                          >
                            {line.replace("###", "").trim()}
                          </h4>
                        );
                      } else if (line.startsWith("##")) {
                        return (
                          <h3
                            key={idx}
                            style={{
                              color: "#818cf8",
                              marginTop: 16,
                              marginBottom: 8,
                              fontSize: "1.1rem",
                            }}
                          >
                            {line.replace("##", "").trim()}
                          </h3>
                        );
                      } else if (line.startsWith("#")) {
                        return (
                          <h2
                            key={idx}
                            style={{
                              color: "#c084fc",
                              marginTop: 20,
                              marginBottom: 10,
                              fontSize: "1.25rem",
                            }}
                          >
                            {line.replace("#", "").trim()}
                          </h2>
                        );
                      } else if (
                        line.trim().startsWith("-") ||
                        line.trim().startsWith("*")
                      ) {
                        const text = line.trim().replace(/^[-*]\s+/, "");
                        const parts = text.split("**");
                        return (
                          <li
                            key={idx}
                            style={{ marginLeft: 15, listStyleType: "disc" }}
                          >
                            {parts.map((part, pIdx) =>
                              pIdx % 2 === 1 ? (
                                <strong key={pIdx}>{part}</strong>
                              ) : (
                                part
                              ),
                            )}
                          </li>
                        );
                      } else if (line.trim()) {
                        const parts = line.split("**");
                        return (
                          <p key={idx}>
                            {parts.map((part, pIdx) =>
                              pIdx % 2 === 1 ? (
                                <strong key={pIdx}>{part}</strong>
                              ) : (
                                part
                              ),
                            )}
                          </p>
                        );
                      }
                      return <div key={idx} style={{ height: 6 }} />;
                    })}
                  </div>

                  <div className="action-bar">
                    <button
                      className="btn-action primary"
                      onClick={() =>
                        handleCopyText(triageReport, setTriageCopied)
                      }
                    >
                      {triageCopied ? <Check size={14} /> : <Copy size={14} />}
                      {triageCopied ? "Copied!" : "Copy to Clipboard"}
                    </button>

                    <button
                      className="btn-action"
                      onClick={() =>
                        handleDownloadTxt(
                          triageReport,
                          "SAMA_VIDHANA_Legal_Triage_Roadmap.txt",
                        )
                      }
                    >
                      <Download size={14} /> Download Roadmap (.txt)
                    </button>
                  </div>
                </div>
              ) : (
                <div
                  style={{
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
                    marginTop: "10px",
                  }}
                >
                  <div style={{ fontSize: "4rem", marginBottom: 20 }}>🧭</div>
                  <h3
                    style={{
                      color: "var(--text-color)",
                      fontWeight: 800,
                      fontSize: "1.5rem",
                      margin: "0 0 10px 0",
                    }}
                  >
                    Legal Triage Routing Panel
                  </h3>
                  <p
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "0.95rem",
                      maxWidth: "400px",
                      lineHeight: 1.6,
                      margin: "0 0 20px 0",
                    }}
                  >
                    Input details of your dispute (category, location, evidence,
                    and narrative description) on the left panel. SAMA-VIDHANA
                    will analyze the situation and generate an actionable triage
                    roadmap covering statutory deadlines, forums of
                    jurisdiction, and procedural steps.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
