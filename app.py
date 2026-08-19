import streamlit as st
import os
import json
from dotenv import load_dotenv

# Load local environment
load_dotenv()

# Import RAG and data modules (Dependency Injection)
from rag_engine import (
    get_global_vectorstore,
    query_rag_engine,
    parse_json_response,
    get_mistral_api_key,
    extract_text_from_pdf,
    build_faiss_index_from_documents,
    generate_plaintext_application,
    triage_citizen_dispute,
)
import schemes_data
from langchain_core.documents import Document

# Streamlit Page Setup
st.set_page_config(
    page_title="SAMA-VIDHANA | Civic & Legal Empowerment Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# State Management: Initialise Global FAISS Index using @st.cache_resource
@st.cache_resource(show_spinner="Indexing Global Civic & Legal Knowledge Base...")
def load_global_vectorstore():
    """Initializes and caches the global FAISS index across user interactions."""
    return get_global_vectorstore()

if "global_vectorstore" not in st.session_state:
    st.session_state.global_vectorstore = load_global_vectorstore()

# Custom CSS for rich aesthetics and clean typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: #F8FAFC;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    
    .subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 500;
    }
    
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 6px;
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    .stat-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        transition: all 0.2s ease;
    }
    
    .stat-card:hover {
        border-color: #38BDF8;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.08);
    }
    
    .scheme-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        border-left: 5px solid #6366F1;
    }
    
    .scheme-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 4px;
    }
    
    .scheme-meta {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 12px;
    }
    
    .plaintext-box {
        font-family: 'JetBrains Mono', monospace;
        background: #0F172A;
        color: #E2E8F0;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #334155;
        white-space: pre-wrap;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .warning-alert {
        background: #FEF3C7;
        color: #92400E;
        padding: 14px 18px;
        border-radius: 10px;
        border: 1px solid #FDE68A;
        margin-bottom: 16px;
    }
    
    .success-alert {
        background: #ECFDF5;
        color: #065F46;
        padding: 14px 18px;
        border-radius: 10px;
        border: 1px solid #A7F3D0;
        margin-bottom: 16px;
    }

    /* 3D Flipping Logo Styles */
    .logo-container {
        perspective: 1000px;
        width: 100%;
        display: flex;
        justify-content: center;
        margin-bottom: 25px;
        margin-top: 10px;
    }
    
    .logo-3d-scene {
        width: 260px;
        height: 55px;
        perspective: 1000px;
    }
    
    .logo-3d-prism {
        width: 100%;
        height: 100%;
        position: relative;
        transform-style: preserve-3d;
        transform: translateZ(-75px);
        animation: rotatePrismY 12s infinite ease-in-out;
    }
    
    .logo-face {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 1.15rem;
        letter-spacing: 0.5px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-sizing: border-box;
    }
    
    .logo-face-en {
        color: #38BDF8;
        border-color: rgba(56, 189, 248, 0.3);
        transform: rotateY(0deg) translateZ(75px);
    }
    
    .logo-face-hi {
        color: #818CF8;
        border-color: rgba(129, 140, 248, 0.3);
        transform: rotateY(120deg) translateZ(75px);
    }
    
    .logo-face-kn {
        color: #C084FC;
        border-color: rgba(192, 132, 252, 0.3);
        transform: rotateY(240deg) translateZ(75px);
    }
    
    @keyframes rotatePrismY {
        0%, 25% {
            transform: translateZ(-75px) rotateY(0deg);
        }
        30%, 55% {
            transform: translateZ(-75px) rotateY(-120deg);
        }
        60%, 85% {
            transform: translateZ(-75px) rotateY(-240deg);
        }
        90%, 100% {
            transform: translateZ(-75px) rotateY(-360deg);
        }
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div class="main-title">🏛️ SAMA-VIDHANA</div>
            <div class="subtitle">Civic & Legal Empowerment AI Assistant • Powered by Mistral 7B & FAISS RAG</div>
        </div>
        <div style="margin-top: 10px;">
            <span class="badge-pill">open-mistral-7b</span>
            <span class="badge-pill">all-MiniLM-L6-v2</span>
            <span class="badge-pill">Grounded RAG</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with status and project info
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-3d-scene">
            <div class="logo-3d-prism">
                <div class="logo-face logo-face-en">🏛️ SAMA-VIDHANA</div>
                <div class="logo-face logo-face-hi">⚖️ सम-विधान</div>
                <div class="logo-face logo-face-kn">🏛️ ಸಮ-ವಿಧಾನ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### ⚖️ **About SAMA-VIDHANA**")
    st.info(
        "**SAMA-VIDHANA** (सम-विधान) bridges the gap between complex statutory legal codes and ordinary citizens. "
        "It provides grounded statutory explanations, step-by-step form drafting, welfare scheme matching, and legal dispute triage."
    )
    
    # Check API key status
    api_key = get_mistral_api_key()
    if api_key:
        st.success("✅ **Mistral API Key Active** (Loaded from configuration)")
    else:
        st.warning("⚠️ **Mistral API Key Missing**\nPlease configure `MISTRAL_API_KEY` in your `.env` file or Streamlit secrets.")

    st.markdown("---")
    st.markdown("#### 🛠️ **System Architecture**")
    st.markdown("""
    - **LLM**: Mistral 7B (`open-mistral-7b`)
    - **Embeddings**: `all-MiniLM-L6-v2`
    - **Vector Store**: FAISS
    - **Chunking**: Recursive (600 chars, 100 overlap)
    - **Grounding**: Strict context-bounded answers
    """)
    st.markdown("---")
    st.caption("Developed for Civic Empowerment & Open Justice.")

# Tab definitions
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Law Explainer", 
    "📝 Plaintext Form-Filler", 
    "🎯 Scheme Eligibility", 
    "🧭 Situational Triage"
])


# ==============================================================================
# TAB 1: LAW EXPLAINER (PDF Upload + Grounded RAG Chat Interface)
# ==============================================================================
with tab1:
    st.markdown("### 📖 Law Explainer — Statutory Clause Simplifier")
    st.write(
        "Upload any legal act, gazette notification, contract, or government order (PDF), "
        "or load our built-in sample legal act to query and simplify statutory clauses in plain English. "
        "SAMA-VIDHANA will search both the global legal base and your uploaded documents."
    )

    # State management for vector store
    if "tab1_vectorstore" not in st.session_state:
        st.session_state.tab1_vectorstore = None
    if "tab1_doc_name" not in st.session_state:
        st.session_state.tab1_doc_name = None
    if "tab1_messages" not in st.session_state:
        st.session_state.tab1_messages = []

    # Two column layout: left for interaction, right for structured output
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### 📥 Document Knowledge Source")
        col_up1, col_up2 = st.columns([3, 2])
        
        with col_up1:
            uploaded_pdf = st.file_uploader(
                "Upload Legal Document / Act (PDF)",
                type=["pdf"],
                help="Upload an official act, legal notice, tenancy agreement, or government gazette."
            )

        with col_up2:
            st.markdown("**Or Use Test Document:**")
            sample_btn = st.button("📄 Load Sample RTI Act", help="Load pre-configured Right to Information Act sample for instant testing.")

        # Handle Uploaded PDF
        if uploaded_pdf is not None:
            if st.session_state.tab1_doc_name != uploaded_pdf.name:
                with st.spinner(f"Indexing '{uploaded_pdf.name}' into FAISS vector database..."):
                    try:
                        docs = extract_text_from_pdf(uploaded_pdf)
                        st.session_state.tab1_vectorstore = build_faiss_index_from_documents(docs)
                        st.session_state.tab1_doc_name = uploaded_pdf.name
                        st.session_state.tab1_messages = []
                        st.success(f"✅ Indexed **{uploaded_pdf.name}** ({len(docs)} pages).")
                    except Exception as e:
                        st.error(f"Error processing PDF: {e}")

        # Handle Sample Document Load
        elif sample_btn:
            sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_rti_act.txt")
            if os.path.exists(sample_path):
                with open(sample_path, "r", encoding="utf-8") as f:
                    sample_text = f.read()
                with st.spinner("Indexing Sample RTI Act (2005)..."):
                    try:
                        sample_doc = Document(page_content=sample_text, metadata={"source": "RTI_Act_2005.pdf", "page": 1})
                        st.session_state.tab1_vectorstore = build_faiss_index_from_documents([sample_doc])
                        st.session_state.tab1_doc_name = "RTI_Act_2005.pdf (Built-in Sample)"
                        st.session_state.tab1_messages = []
                        st.success("✅ Loaded & Indexed **Right to Information Act, 2005**!")
                    except Exception as e:
                        st.error(f"Error indexing sample document: {e}")

        # Active Document Status
        db_status = "📌 **Active Base**: Global Civic & Legal Database (Default)"
        if st.session_state.tab1_vectorstore is not None:
            db_status = f"📌 **Active Base**: Global Database + `{st.session_state.tab1_doc_name}`"
        st.markdown(db_status)

        # Example prompt suggestions
        st.markdown("##### 💡 Suggested Questions:")
        sugg_cols = st.columns(3)
        if sugg_cols[0].button("⏱️ 48-Hour Liberty Rule"):
            st.session_state.tab1_preset_query = "What is the time limit if the requested information concerns the life or liberty of a person?"
        if sugg_cols[1].button("🚫 Section 8 Exemptions"):
            st.session_state.tab1_preset_query = "What categories of information are exempt from disclosure under Section 8?"
        if sugg_cols[2].button("📝 Applicant Reasons"):
            st.session_state.tab1_preset_query = "Is an applicant required to give reasons for requesting information under the Act?"

        st.markdown("---")
        st.markdown("#### 💬 Conversation History")

        # Display Chat History (Simple lightweight cards/bubbles)
        for msg in st.session_state.tab1_messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.markdown(msg["content"])
                else:
                    if msg.get("error"):
                        st.markdown(f"⚠️ *Query encountered an issue: {msg['error']}*")
                    else:
                        rights_summary = msg["content"].get("rights", "") if isinstance(msg.get("content"), dict) else str(msg.get("content", ""))
                        if len(rights_summary) > 180:
                            rights_summary = rights_summary[:180] + "..."
                        st.markdown(f"**Rights summary:** {rights_summary}")
                    st.caption("*(Detailed structured response is visible in the right dashboard panel)*")

        # Chat Input
        preset_val = st.session_state.pop("tab1_preset_query", None)
        user_query = st.chat_input("Ask any question about legal codes or uploaded files...")
        if preset_val:
            user_query = preset_val

        if user_query:
            # Append user message
            st.session_state.tab1_messages.append({"role": "user", "content": user_query})
            st.rerun()

    # RAG Execution when query is submitted (UI Synchronisation & Robust Error Boundaries)
    if st.session_state.tab1_messages and st.session_state.tab1_messages[-1]["role"] == "user":
        last_query = st.session_state.tab1_messages[-1]["content"]
        
        with col_left:
            with st.spinner("Analyzing legal context and generating structured response..."):
                try:
                    result = query_rag_engine(
                        global_vs=st.session_state.global_vectorstore,
                        user_vs=st.session_state.tab1_vectorstore,
                        question=last_query
                    )
                    answer_data = result.get("answer", {})
                    # Ensure answer data is a properly parsed dictionary
                    if isinstance(answer_data, str):
                        answer_data = parse_json_response(answer_data)
                    
                    st.session_state.tab1_messages.append({
                        "role": "assistant",
                        "content": answer_data,
                        "sources": result.get("source_documents", []),
                        "error": None
                    })
                except Exception as e:
                    # Graceful Error Boundary - capture error without crashing the Streamlit app
                    error_text = str(e)
                    st.session_state.tab1_messages.append({
                        "role": "assistant",
                        "content": {
                            "rights": "Unable to process query due to an engine error.",
                            "eligibility": [{"condition": "Engine Execution / LLM Invocation", "status": "Failed"}],
                            "benefits": "Please check your network connection, API key, or query and try again.",
                            "risks": f"System Alert: {error_text}"
                        },
                        "sources": [],
                        "error": error_text
                    })
                st.rerun()

    # Determine latest assistant message to render on the right panel
    latest_assistant_msg = None
    for msg in reversed(st.session_state.tab1_messages):
        if msg["role"] == "assistant":
            latest_assistant_msg = msg
            break

    with col_right:
        st.markdown("#### 📊 Civic & Legal Response Dashboard")
        if latest_assistant_msg is not None:
            # Display Error Alert if error boundary caught an exception
            if latest_assistant_msg.get("error"):
                st.markdown(f"""
                <div class="warning-alert" style="border-left: 5px solid #EF4444; background: #FEF2F2; color: #991B1B; margin-bottom: 18px;">
                    <b style="font-size: 1rem;">⚠️ Engine Processing Notice</b><br>
                    <span style="font-size: 0.92rem; line-height: 1.5;">{latest_assistant_msg['error']}</span>
                    <div style="margin-top: 8px; font-size: 0.82rem; color: #7F1D1D;">
                        Please verify your <code>MISTRAL_API_KEY</code> configuration or ensure the document vectorstore is active.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Extract and validate content keys
            raw_content = latest_assistant_msg.get("content", {})
            if isinstance(raw_content, str):
                content = parse_json_response(raw_content)
            elif isinstance(raw_content, dict):
                content = raw_content
            else:
                content = {
                    "rights": str(raw_content),
                    "eligibility": [],
                    "benefits": "",
                    "risks": ""
                }
            
            # 1. Display Rights Cards
            st.markdown("### 📜 Applicable Civic & Legal Rights")
            rights_text = content.get("rights", "") or "No specific rights identified in the current context."
            st.markdown(f'<div class="scheme-card" style="border-left-color: #38BDF8; margin-top: 10px;">'
                        f'<div style="font-size: 1rem; color: #1E293B; line-height: 1.6;">{rights_text}</div>'
                        f'</div>', unsafe_allow_html=True)
            
            # 2. Display Eligibility Tables
            st.markdown("### 🎯 Eligibility & Statutory Conditions")
            elig_data = content.get("eligibility", [])
            if elig_data and isinstance(elig_data, list):
                rows_html = ""
                for item in elig_data:
                    if isinstance(item, dict):
                        cond = item.get("condition", "Verify requirement")
                        status = item.get("status", "Information Needed")
                    else:
                        cond = str(item)
                        status = "Information Needed"
                    
                    # Compute color styles
                    badge_color = "#E2E8F0"
                    text_color = "#475569"
                    status_text = str(status)
                    
                    status_lower = status_text.lower()
                    if any(x in status_lower for x in ["satisfied", "yes", "pass", "eligible"]):
                        badge_color = "#D1FAE5"
                        text_color = "#065F46"
                        status_text = "✓ " + status_text
                    elif any(x in status_lower for x in ["needed", "unknown", "missing"]):
                        badge_color = "#FEF3C7"
                        text_color = "#92400E"
                        status_text = "? " + status_text
                    elif any(x in status_lower for x in ["required", "fail", "no", "alert", "warning", "failed"]):
                        badge_color = "#FEE2E2"
                        text_color = "#991B1B"
                        status_text = "⚠ " + status_text
                        
                    rows_html += f"""
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 12px 14px; font-size: 0.92rem; color: #334155; font-weight: 500;">{cond}</td>
                        <td style="padding: 12px 14px; text-align: right;">
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; background-color: {badge_color}; color: {text_color};">
                                {status_text}
                            </span>
                        </td>
                    </tr>
                    """
                
                st.markdown(f"""
                <div style="margin-top: 10px; margin-bottom: 20px;">
                    <table style="width: 100%; border-collapse: collapse; background: white; border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                        <thead>
                            <tr style="background: #F8FAFC; border-bottom: 1px solid #E2E8F0; text-align: left;">
                                <th style="padding: 12px 14px; font-size: 0.85rem; font-weight: 700; color: #475569; letter-spacing: 0.05em; text-transform: uppercase;">STATUTORY REQUIREMENT</th>
                                <th style="padding: 12px 14px; font-size: 0.85rem; font-weight: 700; color: #475569; letter-spacing: 0.05em; text-transform: uppercase; text-align: right;">STATUS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No explicit eligibility conditions identified in the retrieved context.")
                
            # 3. Display Benefits Lists
            st.markdown("### 🚀 Actionable Benefits & Next Steps")
            benefits_text = content.get("benefits", "") or "No specific actionable benefits listed."
            st.markdown(f'<div class="scheme-card" style="border-left-color: #818CF8; margin-top: 10px;">'
                        f'<div style="font-size: 1rem; color: #1E293B; line-height: 1.6;">{benefits_text}</div>'
                        f'</div>', unsafe_allow_html=True)
            
            # 4. Display Risks Alerts
            st.markdown("### ⚠️ Critical Risks & Limitations")
            risks_text = content.get("risks", "") or "Ensure all claims and procedures are verified against official records."
            st.markdown(f'<div class="warning-alert" style="margin-top: 10px; border-left: 5px solid #F59E0B;">'
                        f'<b>Please Note:</b><br>{risks_text}'
                        f'</div>', unsafe_allow_html=True)
            
            # 5. Display Sources
            if latest_assistant_msg.get("sources"):
                st.markdown("### 🔍 Verified Citations & References")
                for i, doc in enumerate(latest_assistant_msg["sources"]):
                    with st.expander(f"Reference {i+1}: {doc.metadata.get('source', 'Doc')} (Page {doc.metadata.get('page', 1)})"):
                        st.caption(doc.page_content)
        else:
            # Welcome State
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.03); border: 2px dashed #E2E8F0; padding: 40px 30px; border-radius: 16px; min-height: 480px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
                <div style="font-size: 3.5rem; margin-bottom: 20px;">⚖️</div>
                <h3 style="color: #1E293B; font-weight: 800; font-size: 1.4rem; margin-bottom: 10px;">Civic & Legal Response Dashboard</h3>
                <p style="color: #64748B; font-size: 0.95rem; max-width: 380px; line-height: 1.5;">
                    Ask a civic or legal question in the chat panel, or upload a document to get a structured 4-part legal analysis here.
                </p>
                <div style="margin-top: 20px; font-size: 0.8rem; color: #94A3B8; font-weight: 500;">
                    SAMA-VIDHANA indexes official acts like RTI 2005, Wages Code, Consumer Protection, Civil Rights, and more.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: PLAINTEXT FORM-FILLER (Interactive Interview & Standardized Drafting)
# ==============================================================================
with tab2:
    st.markdown("### 📝 Plaintext Form-Filler — Conversational Legal Drafter")
    st.write(
        "Draft clean, standardized, ready-to-submit plaintext legal notices and civic applications step-by-step. "
        "The generated application adheres to official statutory standards and can be directly copied or downloaded."
    )

    form_type = st.selectbox(
        "Select Application / Notice Type",
        [
            "Right to Information (RTI) Application [Sec 6(1) RTI Act 2005]",
            "Consumer Grievance Legal Demand Notice [Consumer Protection Act 2019]",
            "Tenant Security Deposit Refund Demand Notice",
            "Public Grievance & Municipal Complaint (Civic Negligence)",
            "Formal Representation to Government Department / Public Authority"
        ]
    )

    st.markdown("#### 📋 Applicant & Dispute Details")
    
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        app_name = st.text_input("Applicant Full Name", placeholder="e.g. Rajesh Kumar")
        app_address = st.text_area("Applicant Full Address & Contact", placeholder="e.g. Flat 402, Green Valley Apartments, Bengaluru, Karnataka - 560001\nPhone: +91 9876543210\nEmail: rajesh@example.com")
        target_authority = st.text_input("Target Department / Opposite Party Name", placeholder="e.g. Public Information Officer, Bengaluru Development Authority (BDA)")

    with fcol2:
        incident_date = st.text_input("Relevant Date(s) / Timeline", placeholder="e.g. 15th January 2024 to 10th February 2024")
        relief_sought = st.text_area("Specific Information / Remedy / Action Demanded", placeholder="e.g. Certified copies of road inspection reports and sanctioned budget for 100 Feet Ring Road.")
        additional_notes = st.text_area("Key Facts / Previous Communications", placeholder="e.g. Complaint token #8392 filed on municipal portal with no response for 45 days.")

    generate_form_btn = st.button("⚡ Generate Formatted Plaintext Application", type="primary")

    if generate_form_btn:
        if not app_name or not target_authority or not relief_sought:
            st.warning("Please provide at least the **Applicant Name**, **Target Department / Opposite Party**, and **Specific Information/Remedy**.")
        else:
            with st.spinner("Drafting standardized legal application via Mistral 7B..."):
                details = {
                    "Applicant Name": app_name,
                    "Applicant Address & Contact": app_address,
                    "Target Department / Opposite Party": target_authority,
                    "Relevant Dates": incident_date,
                    "Information / Remedy / Relief Demanded": relief_sought,
                    "Additional Context & Reference Numbers": additional_notes
                }
                try:
                    generated_text = generate_plaintext_application(form_type, details)
                    st.session_state.generated_application = generated_text
                    st.success("✅ Application drafted successfully!")
                except Exception as e:
                    st.error(f"Failed to generate application: {e}")

    if "generated_application" in st.session_state and st.session_state.generated_application:
        st.markdown("#### 📄 Generated Application (Plaintext Ready for Copy/Print):")
        st.text_area("Plaintext Output", value=st.session_state.generated_application, height=380)
        
        dcol1, dcol2 = st.columns([1, 4])
        with dcol1:
            st.download_button(
                label="📥 Download as .txt",
                data=st.session_state.generated_application,
                file_name=f"{form_type[:20].strip().replace(' ', '_')}_Application.txt",
                mime="text/plain"
            )


# ==============================================================================
# TAB 3: SCHEME ELIGIBILITY (Searchable Vector Lookup for Welfare Schemes)
# ==============================================================================
with tab3:
    st.markdown("### 🎯 Scheme Eligibility — Citizen Welfare Intelligence")
    st.write(
        "Semantic search and vector-based matching for Central and State government welfare schemes, subsidies, and social security programs."
    )

    sc_col1, sc_col2 = st.columns([1, 2])
    
    with sc_col1:
        st.markdown("#### 👤 Citizen Profile Filter")
        target_category = st.selectbox(
            "Target Category",
            ["All Categories", "Agriculture & Farmers", "Healthcare & Social Security", "Women & Child Development", "Housing & Urban Affairs", "Micro-Enterprise & Self Employment", "Senior Citizens & Social Welfare", "Artisans & Traditional Craftspeople"]
        )
        citizen_age = st.number_input("Citizen Age", min_value=1, max_value=110, value=35)
        annual_income = st.selectbox(
            "Annual Household Income",
            ["< ₹1,00,000 (BPL / Deprived)", "₹1,00,000 - ₹3,00,000 (EWS)", "₹3,00,000 - ₹6,00,000 (LIG)", "> ₹6,00,000 (MIG/General)"]
        )
        employment = st.selectbox(
            "Occupation / Status",
            ["Small / Marginal Farmer", "Daily Wage / Unorganized Worker", "Street Vendor / Hawker", "Traditional Artisan / Craftsperson", "Self-Employed / Small Business", "Senior Citizen", "Homemaker / Mother", "Salaried / Other"]
        )

    with sc_col2:
        st.markdown("#### 🔍 Natural Language Query")
        scheme_search_query = st.text_input(
            "Search schemes by citizen situation or need:",
            placeholder="e.g. Free health insurance coverage for elderly parents above 70 years"
        )
        
        # Example search chips
        st.markdown("##### 💡 Popular Searches:")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        if chip_col1.button("🌾 ₹6000 Farmer Income Support"):
            scheme_search_query = "Direct cash transfer income support for farmers"
        if chip_col2.button("🏥 ₹5 Lakh Free Hospitalization"):
            scheme_search_query = "Ayushman Bharat cashless health insurance coverage"
        if chip_col3.button("🔨 Collateral-Free Loans for Artisans"):
            scheme_search_query = "PM Vishwakarma toolkits and collateral free loan for artisans"

    # Search Execution
    schemes_vectorstore = schemes_data.get_schemes_vectorstore()
    
    # Query assembly
    query_to_run = scheme_search_query.strip()
    if not query_to_run:
        query_to_run = f"Welfare schemes for {employment} in category {target_category} with income {annual_income} and age {citizen_age}"

    if st.button("🔎 Find Matching Welfare Schemes", type="primary"):
        with st.spinner("Searching welfare schemes knowledgebase..."):
            retriever = schemes_vectorstore.as_retriever(search_kwargs={"k": 5})
            matched_docs = retriever.invoke(query_to_run)

            # Filter by category if selected
            if target_category != "All Categories":
                filtered = [d for d in matched_docs if target_category.lower() in d.metadata.get("category", "").lower()]
                matched_docs = filtered if filtered else matched_docs

            st.markdown(f"#### 🎯 Found {len(matched_docs)} Relevant Scheme(s):")
            
            for doc in matched_docs:
                meta = doc.metadata
                st.markdown(f"""
                <div class="scheme-card">
                    <div class="scheme-title">🏛️ {meta.get('name', 'Welfare Scheme')}</div>
                    <div class="scheme-meta"><b>Category:</b> {meta.get('category')} | <b>Ministry:</b> {meta.get('ministry')}</div>
                    <div style="font-size: 0.95rem; color: #334155; line-height: 1.6; white-space: pre-line;">{doc.page_content}</div>
                </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# TAB 4: SITUATIONAL TRIAGE (Dispute Intake & Procedural Routing)
# ==============================================================================
with tab4:
    st.markdown("### 🧭 Situational Triage — Dispute Intake & Legal Routing")
    st.write(
        "Evaluate a legal dispute or civic grievance, verify procedural admissibility and statutory deadlines, "
        "and get routed to the correct government department, commission, ombudsman, or court."
    )

    with st.form("triage_intake_form"):
        t_col1, t_col2 = st.columns(2)
        
        with t_col1:
            dispute_category = st.selectbox(
                "Dispute Category",
                [
                    "Consumer Defect & Service Deficiency (E-commerce, Electronics, Airlines, Banking)",
                    "Real Estate & Builder Delay (RERA, Possession, Undisclosed Charges)",
                    "Tenant & Landlord Dispute (Deposit Retention, Eviction, Maintenance)",
                    "Labor & Employment (Unpaid Wages, Wrongful Termination, Gratuity)",
                    "Cyber Crime & Financial Fraud (UPI Fraud, Phishing, Identity Theft)",
                    "Civic Negligence & Municipal Failure (Sanitation, Illegal Encroachment, Potholes)"
                ]
            )
            jurisdiction_state = st.text_input("State / City / District", placeholder="e.g. Pune, Maharashtra")
            opposing_party = st.text_input("Opposing Entity Name", placeholder="e.g. XYZ E-Commerce Pvt Ltd / ABC Builder")

        with t_col2:
            current_status = st.selectbox(
                "Current Stage of Grievance",
                [
                    "No action taken yet (Initial occurrence)",
                    "Verbal or informal request made, but ignored",
                    "Formal written email / grievance ticket submitted (No resolution)",
                    "Opposing party explicitly rejected claim or issued counter-notice",
                    "Police / Local authority complaint filed (Awaiting follow-up)"
                ]
            )
            supporting_documents = st.text_input(
                "Available Evidence in Hand",
                placeholder="e.g. Invoice, payment receipts, email trail, WhatsApp chats, photo proof"
            )

        incident_description = st.text_area(
            "Detailed Incident Narrative (What happened? When? Financial or physical loss incurred?)",
            placeholder="e.g. Ordered a laptop worth ₹65,000 on 12th Jan 2024. Received damaged unit. Requested replacement within 7-day window. Customer support closed ticket citing policy without replacement or refund.",
            height=120
        )

        submit_triage = st.form_submit_button("🧭 Analyze & Generate Legal Triage Roadmap", type="primary")

    if submit_triage:
        if not incident_description or len(incident_description.strip()) < 15:
            st.warning("Please provide a more detailed description of the incident for an accurate triage assessment.")
        else:
            with st.spinner("Conducting statutory procedural analysis via Mistral 7B..."):
                triage_payload = {
                    "category": dispute_category,
                    "jurisdiction": jurisdiction_state,
                    "description": incident_description,
                    "opposing_party": opposing_party,
                    "status": current_status,
                    "documents": supporting_documents
                }
                try:
                    triage_result = triage_citizen_dispute(triage_payload)
                    st.session_state.triage_report = triage_result
                except Exception as e:
                    st.error(f"Error executing legal triage: {e}")

    if "triage_report" in st.session_state and st.session_state.triage_report:
        st.markdown("---")
        st.markdown("### 📊 Procedural Triage & Action Roadmap")
        st.markdown(st.session_state.triage_report)
        
        st.download_button(
            label="📥 Download Triage Report (.txt)",
            data=st.session_state.triage_report,
            file_name="SAMA_VIDHANA_Legal_Triage_Roadmap.txt",
            mime="text/plain"
        )
        