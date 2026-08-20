# 🏛️ SAMA-VIDHANA (सम-विधान)
### Civic & Legal Empowerment AI Assistant • Powered by Mistral 7B & FAISS RAG

**SAMA-VIDHANA** is a premium, full-stack civic and legal empowerment application designed to make legal knowledge, statutory rights, welfare programs, and dispute resolution accessible to every citizen — presented in a sleek **dark-mode-only** interface.

---

## 🌟 Key Features & Interface Tabs

The application is structured into four core civic intelligence modules:

1. **📖 Law Explainer**
   - Upload any official PDF (acts, gazettes, notices, contracts) or load the built-in sample legal act (RTI Act 2005).
   - Answer query inputs in plain language supported by exact chunk-level citations.
   - Active Sources Sidebar: Visual documents list is hidden from the UI to declutter the workspace, while the file upload functionality remains accessible via the tray button.

2. **📝 Plaintext Form-Filler**
   - Guided conversational legal drafter for standard civic applications (RTI, Consumer Grievances, Tenant Demand Notices, Municipal Representations).
   - **Ruled Paper Layout**: Replaces basic textarea previews with an elegant, paper-sheet simulation styled in alabaster (`#faf9f6`), featuring a double red margin line, book-bound double border, and CSS gradient ruled notebook lines aligned with the Georgia typography baseline.
   - One-click copy-to-clipboard and `.txt` download capabilities.

3. **🎯 Scheme Eligibility**
   - Semantic natural language matching and multi-attribute citizen profile filtering for Indian welfare schemes (Ayushman Bharat, PM-KISAN, PM Vishwakarma, etc.).
   - **Flexible Age Selector**: Custom text inputs allowing users to clear the field, backspace, and type any age, or adjust it with control arrows.

4. **🧭 Situational Triage**
   - Intake form evaluating legal disputes (Consumer, Labor, Tenancy, Cyber Crime, RERA).
   - Generates an actionable roadmap presented strictly as structured Markdown bullet points — no conversational filler or sign-offs.

---

## ⚙️ Technical Enhancements & Performance

- **FAISS Disk Cache Optimization**: Rather than rebuilding the vector indexes from source files on every backend start (taking up to 5 minutes), SAMA-VIDHANA implements a local disk-based FAISS index caching system. Startup database load times are reduced to **~0.1 seconds**.
- **Robust JSON Parser**: Regex-based JSON extraction in `rag_engine.py` securely parses RAG responses, preventing raw arrays or malformed JSON from leaking into the user interface.
- **Structured Triage Output**: Prompt-level enforcements in `rag_engine.py` ensure every Situational Triage report is formatted as a clean, professional structured document using Markdown headings and bullet points.

---

## 🎨 Premium Dark-Mode Design System

SAMA-VIDHANA runs exclusively in a sleek **dark mode** built around:

| Token | Value | Usage |
|---|---|---|
| Main Background | `#191414` | Full-page sleek black |
| Prism Face Background | `#1C1C1C` | Soft black on 3D logo faces |
| Accent Blue | `#38bdf8` | Interactive elements, active tabs |
| Accent Purple | `#818cf8` | Secondary badges, highlights |
| Text Primary | `#f8fafc` | All body text |
| Text Muted | `#94a3b8` | Subtitles, captions |

### Branding & Logo
- **Header Logo**: The custom gavel logo image (`/sama-vidhana.png`) is displayed in the top left at `68px` height for high visibility, with `filter: invert(1)` and `mix-blend-mode: screen` applied for seamless rendering on the dark background.
- **3D Rotating Prism Logo**: A `250×200px` rotating prism in the sidebar shows the multilingual brand images (English, Hindi, Kannada) with no text overlays. Faces have a soft black `#1C1C1C` background. Images use `filter: invert(1)` + `mix-blend-mode: screen` to blend white borders into the background while keeping logo text readable in white.
- **Spring Easing Animation**: The prism rotates with a custom `cubic-bezier(0.68, -0.6, 0.32, 1.6)` spring curve over a faint pulsating background aura.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend / Web UI** | React.js (Vite, Lucide Icons, Glassmorphism, 3D CSS animations) |
| **API Layer / Backend** | FastAPI (uvicorn) |
| **Large Language Model** | Mistral 7B (`open-mistral-7b`) via official `langchain-mistralai` |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Indexing** | FAISS (`faiss-cpu`) with local disk caching |
| **Document Processing** | `pypdf` + LangChain Recursive Text Splitter |

---

## 🚀 Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<TEAMMATE_USERNAME>/SAMA-VIDHANA.git
cd SAMA-VIDHANA
```

### 2. Create and Activate a Virtual Environment
**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Add your Mistral API Key:
```ini
MISTRAL_API_KEY=your_actual_mistral_api_key_here
```

### 5. Launch the FastAPI Backend
```bash
python -u -m uvicorn main:app --host 127.0.0.1 --port 8000
```
The backend API server runs at `http://127.0.0.1:8000`.

### 6. Launch the React Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
The client dashboard opens at `http://localhost:5173`.

---

## ⚖️ Disclaimer
*SAMA-VIDHANA is an AI-powered civic empowerment tool designed for informational and procedural guidance. It does not constitute formal legal representation or an attorney-client relationship. For formal litigation, consult an advocate registered with the State Bar Council.*
