# 🏛️ SAMA-VIDHANA (सम-विधान)
### Civic & Legal Empowerment AI Assistant • Powered by Mistral 7B & FAISS RAG

**SAMA-VIDHANA** is a full-stack civic and legal empowerment application designed to make legal knowledge, statutory rights, welfare programs, and dispute resolution accessible to every citizen in plain English.

**Link** :- https://sama-vidhana.netlify.app

---

## 🌟 Key Features & Architecture

The application is structured into four core civic intelligence tabs:

1. **📖 Law Explainer**
   - Upload any official PDF (acts, gazettes, notices, contracts) or load the built-in sample legal act (RTI Act 2005).
   - RAG pipeline with `pypdf` text extraction, `RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)`, and `FAISS` vector database.
   - Grounded statutory simplification answering questions in plain English with exact chunk-level citations.

2. **📝 Plaintext Form-Filler**
   - Guided conversational legal drafter for standard civic applications:
     - Right to Information (RTI) Applications (Section 6(1), RTI Act 2005)
     - Consumer Grievance Legal Demand Notices (Consumer Protection Act 2019)
     - Tenant-Landlord Security Deposit Demand Notices
     - Municipal Grievances and Public Representations
   - Generates clean, copyable plaintext documents with one-click `.txt` download.

3. **🎯 Scheme Eligibility**
   - Pre-indexed FAISS vector knowledge base containing Central and State government welfare schemes (PM-KISAN, Ayushman Bharat PM-JAY, PMAY, Sukanya Samriddhi, PMMY Mudra, PM SVANidhi, PM Vishwakarma, etc.).
   - Semantic natural language matching and multi-attribute citizen profile filtering.

4. **🧭 Situational Triage**
   - Interactive intake form evaluating legal disputes (Consumer, RERA/Real Estate, Labor, Tenancy, Cyber Crime, Civic Negligence).
   - Generates an actionable roadmap covering procedural validity, designated authorities (tribunals, commissions, ombudsmen), limitation periods, and mandatory evidentiary checklists.

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend / Web UI** | React.js (Vite, Lucide Icons, Glassmorphism, 3D CSS animations) |
| **API Layer / Backend** | FastAPI (uvicorn) |
| **Large Language Model** | Mistral 7B (`open-mistral-7b`) via official `langchain-mistralai` |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Indexing** | FAISS (`faiss-cpu`) |
| **Document Processing** | `pypdf` + LangChain Recursive Text Splitter |
| **Configuration** | `python-dotenv` & `.env` file |

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

### 4. Configure Your Mistral API Key
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Open `.env` and add your Mistral API Key:
```ini
MISTRAL_API_KEY=your_actual_mistral_api_key_here
```

### 5. Launch the FastAPI Backend
```bash
python -u -m uvicorn main:app --host 127.0.0.1 --port 8000
```
The backend API server will run at `http://127.0.0.1:8000`.

### 6. Launch the React Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
The client dashboard will open automatically in your browser at `http://localhost:5173`.


---

## ☁️ Deployment on Streamlit Community Cloud

1. Push your repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "feat: Initial commit for SAMA-VIDHANA"
   git branch -M main
   git remote add origin https://github.com/<TEAMMATE_USERNAME>/SAMA-VIDHANA.git
   git push -u origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account and select the `SAMA-VIDHANA` repository.
4. Set the main file path to `app.py`.
5. Under **Advanced Settings** -> **Secrets**, add your Mistral API key:
   ```toml
   MISTRAL_API_KEY = "your_actual_mistral_api_key_here"
   ```
6. Click **Deploy**.

---

## 🔒 System Prompt & Strict Grounding Boundary

To ensure complete legal safety and factual integrity:
> *"You are a civic legal assistant. Answer solely using the retrieved context. If the answer is not present in the context, clearly state that the provided information does not contain the answer."*

---

## ⚖️ Disclaimer
*SAMA-VIDHANA is an AI-powered civic empowerment tool designed for informational and procedural guidance. It does not constitute formal legal representation or attorney-client relationship. For formal litigation, consult an advocate registered with the State Bar Council.*
