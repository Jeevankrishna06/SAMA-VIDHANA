# 🏛️ SAMA-VIDHANA (सम-विधान)
### Civic & Legal Empowerment AI Assistant • Powered by Mistral 7B & FAISS RAG

**SAMA-VIDHANA** is a full-stack civic and legal empowerment application designed to make statutory rights, legal procedures, government welfare programs, and dispute resolution accessible to every citizen in plain, understandable language.

🌐 **Live Demo**: [https://sama-vidhana.netlify.app](https://sama-vidhana.netlify.app)

---

## 🚀 Live Deployment & Infrastructure

| Layer | Platform | Status |
|---|---|---|
| **Frontend Web App** | [Netlify](https://sama-vidhana.netlify.app) | 🟢 Active |
| **Backend API Server** | [Render](https://render.com) (FastAPI) | 🟢 Active (Free Tier) |
| **Alternative Cloud App** | [Streamlit Community Cloud](https://share.streamlit.io) | 🟢 Ready (`app.py`) |

> [!NOTE]
> **Free-Tier Cold Start Notice**:
> The backend API is hosted on Render's free-tier infrastructure, which automatically spins down instances during periods of inactivity. If the service is waking up from sleep, API responses may take up to **2–5 minutes** on the initial request. Subsequent requests will be fast and responsive.
> 
> *If an API call times out or displays a connection error initially, please wait a couple of minutes and refresh the page—the service automatically recovers without any further action required.*

---

## 🌟 Key Features & Civic Modules

The application is organized into four purpose-built civic intelligence modules:

### 1. 📖 Law Explainer
- **Document Grounding**: Upload custom legal PDF documents (acts, gazettes, notices, contracts) or query pre-indexed statutory codes (RTI Act 2005, Consumer Protection Act, BNSS, etc.).
- **RAG Pipeline**: Implements PyPDF extraction, LangChain recursive text chunking (`chunk_size=600`, `chunk_overlap=100`), and local FAISS vector similarity search.
- **Structured Explanations**: Translates dense legal jargon into plain English with structured sections for **Applicable Rights**, **Eligibility & Statutory Criteria**, **Actionable Next Steps**, and **Risks & Limitations**, supported by exact chunk-level citations.

### 2. 📝 Plaintext Form-Filler
- **Conversational Legal Drafter**: Automatically formats standardized, legally coherent representations and notices:
  - **Right to Information (RTI)** Applications (*Section 6(1), RTI Act 2005*)
  - **Consumer Grievance Legal Demand Notices** (*Consumer Protection Act 2019*)
  - **Tenant-Landlord Security Deposit Demand Notices**
  - **Municipal Representations & Civic Grievance Letters**
- **Ruled Paper Simulation**: Displays drafted letters on an elegant, book-bound ruled notebook paper layout with one-click copy and `.txt` file download.

### 3. 🎯 Scheme Eligibility
- **Welfare Knowledge Base**: Pre-indexed database covering major Central and State welfare programs (PM-KISAN, Ayushman Bharat PM-JAY, PMAY, Sukanya Samriddhi, PMMY Mudra, PM SVANidhi, PM Vishwakarma, etc.).
- **Multi-Attribute Matching**: Natural language query matching paired with citizen profile filters (Occupation, Income Bracket, Category, and Age).

### 4. 🧭 Situational Triage
- **Dispute Intake**: Interactive legal dispute evaluation covering Consumer, Real Estate (RERA), Labor & Employment, Tenancy, Cyber Crime, and Municipal Negligence.
- **Actionable Roadmap**: Generates a structured roadmap detailing procedural validity, designated grievance authorities (commissions, tribunals, ombudsmen), limitation periods, and mandatory evidentiary checklists.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend / Web UI** | React 19, Vite, TailwindCSS, Lucide Icons | Responsive single-page application with modern dark-mode aesthetic |
| **Backend API** | FastAPI, Uvicorn | High-performance asynchronous REST API with sliding-window rate limiting |
| **Alternative App** | Streamlit | Standalone single-script Python interface with custom 3D CSS styling |
| **Language Model** | Mistral 7B (`open-mistral-7b`) | LLM for structured reasoning, simplification, and legal drafting |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Local on-device dense vector embeddings via HuggingFace |
| **Vector Search** | FAISS (`faiss-cpu`) | In-memory similarity search with local disk index caching |
| **Document Processing** | PyPDF & LangChain Text Splitters | PDF parsing, chunking, and semantic context compilation |
| **Security & Privacy** | Custom Middlewares, PII Redaction | Security headers, rate limiting, path traversal defenses, PII masking |

---

## 🎨 Design System

SAMA-VIDHANA features a sleek, dedicated dark-mode interface:

| Color / Token | Hex Code | Usage |
|---|---|---|
| **Background Dark** | `#191414` | Primary app canvas |
| **Surface Dark** | `#1E293B` | Interactive cards, input panels |
| **Soft Black** | `#1C1C1C` | 3D rotating prism faces |
| **Primary Accent** | `#38BDF8` | Active tabs, highlights, links |
| **Secondary Accent** | `#818CF8` | Category badges, statutory tags |
| **Text Primary** | `#F8FAFC` | High-contrast readable body text |
| **Text Muted** | `#94A3B8` | Subtitles, metadata, captions |

---

## 🚀 Local Development Setup

To run SAMA-VIDHANA locally, start the FastAPI backend and Vite frontend in two separate terminals:

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/SAMA-VIDHANA.git
cd SAMA-VIDHANA
```

### 2. Configure Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Add your Mistral API Key to `.env`:
```ini
MISTRAL_API_KEY=your_actual_mistral_api_key_here
```

### 4. Terminal 1 — Start the Backend (FastAPI)
```bash
python -u -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The API server will run at `http://127.0.0.1:8000`.

### 5. Terminal 2 — Start the Frontend (React / Vite)
In a second terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## ☁️ Streamlit Community Cloud Deployment

SAMA-VIDHANA includes complete Streamlit Cloud deployment support ([`app.py`](file:///d:/SAMA-VIDHANA/SAMA-VIDHANA/app.py)):

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: deploy to Streamlit Cloud"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **New app** and select your repository.
4. Set the **Main file path** to `app.py`.
5. Under **Advanced Settings** -> **Secrets**, add your Mistral API key:
   ```toml
   MISTRAL_API_KEY = "your_actual_mistral_api_key_here"
   ```
6. Click **Deploy!** *(Dependencies and Linux libraries are automatically configured via `requirements.txt`, `packages.txt`, and `.streamlit/config.toml`)*.

---

## 🔒 Grounding & Safety Boundary

To prevent hallucinations and guarantee factual accuracy:
> *"You are a civic legal assistant. Answer solely using the retrieved context. If the answer is not present in the context, clearly state that the provided information does not contain the answer."*

All citizen questions and document chunks are isolated within strict XML boundary tags (`<retrieved_context>` and `<citizen_question>`) with active prompt injection defenses.

---

## ⚖️ Disclaimer

*SAMA-VIDHANA is an AI-powered civic empowerment tool designed strictly for informational and procedural guidance. It does not constitute formal legal representation, legal practice, or an attorney-client relationship. For formal litigation, dispute filing, or court appearances, consult an advocate registered with the State Bar Council.*

---

***THANK YOU***  
-Team *Sama-Vidhana*
