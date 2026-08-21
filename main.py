from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import shutil
import rag_engine
from langchain_core.documents import Document

# Load environment variables (.env)
load_dotenv()

app = FastAPI(title="SAMA-VIDHANA API")

# Enable CORS for local Vite React, Netlify, Vercel, and custom preview domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "https://sama-vidhana.netlify.app",
    ],
    allow_origin_regex=r"https://.*\.netlify\.app|https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global variables
GLOBAL_VS = None
USER_VECTORSTORES = {}  # filename -> FAISS index
UPLOAD_DIR = "./uploads"

def get_global_vs():
    """
    Lazy-load the global legal FAISS index on demand.
    Avoids loading PyTorch embedding models or vectorstores at application boot.
    """
    global GLOBAL_VS
    if GLOBAL_VS is None:
        GLOBAL_VS = rag_engine.get_global_vectorstore()
    return GLOBAL_VS

def log_request_response(endpoint: str, payload: dict, response: dict):
    log_path = "../.log"
    try:
        import json
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"=== [{endpoint}] ===\n")
            f.write(f"Input: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")
            f.write(f"Output: {json.dumps(response, ensure_ascii=False, indent=2)}\n")
            f.write("-" * 40 + "\n\n")
    except Exception as e:
        print(f"Logging error: {e}")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    print("FastAPI: SAMA-VIDHANA API initialized in lightweight mode (Lazy loading enabled).")

@app.get("/health")
async def health_check():
    """
    Lightweight health check endpoint for Render / cloud monitoring.
    Returns immediately without loading ML models, vectorstores, or PDFs.
    """
    return {"status": "ok"}

@app.get("/api/sources")
async def get_sources():
    """
    Returns list of active global acts and user uploaded PDFs.
    """
    data_dir = "./data"
    global_acts = []
    if os.path.exists(data_dir):
        global_acts = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    
    uploaded_files = list(USER_VECTORSTORES.keys())
    
    return {
        "global_sources": global_acts,
        "user_sources": uploaded_files
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts PDF, extracts text, index to FAISS in memory, and cache.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse and Index PDF
        docs = rag_engine.extract_text_from_pdf(file_path)
        vs = rag_engine.build_faiss_index_from_documents(docs)
        USER_VECTORSTORES[file.filename] = vs
        
        return {
            "filename": file.filename,
            "status": "success",
            "page_count": len(docs)
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(payload: dict):
    """
    Accepts question and optional selected sources, retrieves context, and runs Mistral structured RAG.
    """
    question = payload.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    selected_sources = payload.get("selected_sources", [])
    
    # Retrieve active vector stores
    active_user_vs = []
    if selected_sources:
        for src in selected_sources:
            if src in USER_VECTORSTORES:
                active_user_vs.append(USER_VECTORSTORES[src])
    else:
        active_user_vs = list(USER_VECTORSTORES.values())
        
    # Decide if we query global acts
    use_global = True
    if selected_sources:
        use_global = False
        data_dir = "./data"
        global_acts = []
        if os.path.exists(data_dir):
            global_acts = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
        for src in selected_sources:
            if src in global_acts:
                use_global = True
                break
                
    retrieved_docs = []
    
    # 1. Query global acts (Lazy-loaded)
    if use_global:
        global_vs = get_global_vs()
        if global_vs is not None:
            try:
                global_retriever = global_vs.as_retriever(search_kwargs={"k": 4})
                global_docs = global_retriever.invoke(question)
                retrieved_docs.extend(global_docs)
            except Exception as e:
                print(f"Error querying global VS: {e}")
            
    # 2. Query user uploaded documents
    for vs in active_user_vs:
        try:
            user_retriever = vs.as_retriever(search_kwargs={"k": 3})
            user_docs = user_retriever.invoke(question)
            retrieved_docs.extend(user_docs)
        except Exception as e:
            print(f"Error querying user VS: {e}")
            
    if not retrieved_docs:
        res = {
            "answer": {
                "rights": "The provided information does not contain the answer.",
                "eligibility": [],
                "benefits": "No relevant documents found in selected sources.",
                "risks": "Please verify your question or upload a document."
            },
            "sources": []
        }
        log_request_response("/api/chat", payload, res)
        return res
        
    # Compile context
    formatted_context = "\n\n---\n\n".join(
        [
            f"[Source: {doc.metadata.get('source', 'Doc')} | Page: {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
            for doc in retrieved_docs
        ]
    )
    
    try:
        llm = rag_engine.get_llm(temperature=0.1)
        prompt = rag_engine.ChatPromptTemplate.from_template(rag_engine.STRUCTURED_RAG_PROMPT_TEMPLATE)
        chain = prompt | llm | rag_engine.StrOutputParser()
        
        response = chain.invoke({"context": formatted_context, "question": question})
        parsed_answer = rag_engine.parse_json_response(response)
        
        # Serialize sources for frontend
        sources_list = []
        for doc in retrieved_docs:
            sources_list.append({
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", 1),
                "content": doc.page_content
            })
            
        res = {
            "answer": parsed_answer,
            "sources": sources_list
        }
        log_request_response("/api/chat", payload, res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import schemes_data

@app.post("/api/generate-form")
async def generate_form(payload: dict):
    form_type = payload.get("form_type", "")
    details = payload.get("details", {})
    if not form_type or not details:
        raise HTTPException(status_code=400, detail="Form type and details are required.")
    try:
        generated_text = rag_engine.generate_plaintext_application(form_type, details)
        res = {"generated_text": generated_text}
        log_request_response("/api/generate-form", payload, res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/triage")
async def triage(payload: dict):
    if not payload.get("description"):
        raise HTTPException(status_code=400, detail="Incident narrative description is required.")
    try:
        triage_report = rag_engine.triage_citizen_dispute(payload)
        res = {"triage_report": triage_report}
        log_request_response("/api/triage", payload, res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schemes")
async def get_matching_schemes(payload: dict):
    query = payload.get("query", "").strip()
    category = payload.get("category", "All Categories")
    age = payload.get("age", 35)
    income = payload.get("income", "")
    occupation = payload.get("occupation", "")
    
    if not query:
        age_str = f" and age {age}" if age not in [None, ""] else ""
        query = f"Welfare schemes for {occupation} in category {category} with income {income}{age_str}"
        
    try:
        schemes_vectorstore = schemes_data.get_schemes_vectorstore()
        retriever = schemes_vectorstore.as_retriever(search_kwargs={"k": 5})
        matched_docs = retriever.invoke(query)
        
        # Filter by category if selected
        if category != "All Categories":
            filtered = [d for d in matched_docs if category.lower() in d.metadata.get("category", "").lower()]
            if filtered:
                matched_docs = filtered
                
        schemes_list = []
        for doc in matched_docs:
            meta = doc.metadata
            schemes_list.append({
                "name": meta.get("name", "Welfare Scheme"),
                "category": meta.get("category", "General"),
                "ministry": meta.get("ministry", "Government of India"),
                "content": doc.page_content
            })
            
        res = {"schemes": schemes_list}
        log_request_response("/api/schemes", payload, res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

