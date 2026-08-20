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

# Enable CORS for local Vite React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
GLOBAL_VS = None
USER_VECTORSTORES = {}  # filename -> FAISS index
UPLOAD_DIR = "./uploads"

import logging
import uuid

# Configure secure minimal logging (without logging sensitive user PII)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sama_vidhana")

# Max upload limit (200 MB)
MAX_UPLOAD_SIZE = 200 * 1024 * 1024

def log_request_response(endpoint: str, payload: dict, response: dict):
    """Safe audit logging without persisting unencrypted citizen PII or dispute text to disk."""
    logger.info(f"Handled request to {endpoint}")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

import threading

@app.on_event("startup")
async def startup_event():
    def index_background():
        global GLOBAL_VS
        logger.info("Starting global legal database indexing in background thread...")
        GLOBAL_VS = rag_engine.get_global_vectorstore()
        logger.info("Global legal database indexing completed successfully.")
        
    threading.Thread(target=index_background, daemon=True).start()

@app.get("/api/sources")
async def get_sources():
    """
    Returns list of active global acts and user uploaded PDFs.
    """
    data_dir = "./data"
    global_acts = []
    if os.path.exists(data_dir):
        global_acts = [os.path.basename(f) for f in os.listdir(data_dir) if f.endswith(".pdf")]
    
    uploaded_files = list(USER_VECTORSTORES.keys())
    
    return {
        "global_sources": global_acts,
        "user_sources": uploaded_files
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts PDF with strict validation, extracts text, indexes to FAISS in memory.
    """
    # 1. Sanitize filename to prevent path traversal
    original_filename = os.path.basename(file.filename or "uploaded_document.pdf")
    if not original_filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents (.pdf) are supported.")
        
    # 2. Verify PDF Magic Bytes (%PDF-)
    magic_header = await file.read(5)
    await file.seek(0)
    if magic_header != b"%PDF-":
        raise HTTPException(status_code=400, detail="Invalid PDF header. File is not a valid PDF.")

    # 3. Stream and enforce 200MB size limit
    safe_disk_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_disk_filename)
    total_size = 0
    
    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=413, detail="File size exceeds maximum allowed limit (200MB).")
                buffer.write(chunk)
            
        # Parse and Index PDF safely
        docs = rag_engine.extract_text_from_pdf(file_path)
        vs = rag_engine.build_faiss_index_from_documents(docs)
        USER_VECTORSTORES[original_filename] = vs
        
        return {
            "filename": original_filename,
            "status": "success",
            "page_count": len(docs)
        }
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded PDF {original_filename}: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to process and index document. Please ensure it is a valid PDF.")


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
    
    # 1. Query global acts
    if use_global:
        if GLOBAL_VS is None:
            # Check if there are acts to index
            data_dir = "./data"
            global_acts = []
            if os.path.exists(data_dir):
                global_acts = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
            if global_acts:
                res = {
                    "answer": {
                        "rights": "SAMA-VIDHANA global legal database is currently indexing its documents in the background. Please wait about 15-20 seconds and try your question again.",
                        "eligibility": [{"condition": "Database indexing in progress", "status": "Information Needed"}],
                        "benefits": "Service is initializing. You can also upload a PDF document on the left and query it immediately.",
                        "risks": "Database starting up."
                    },
                    "sources": []
                }
                log_request_response("/api/chat", payload, res)
                return res
        else:
            try:
                global_retriever = GLOBAL_VS.as_retriever(search_kwargs={"k": 4})
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
        
    # Compile context with explicit XML document tags
    formatted_context = "\n\n".join(
        [
            f"<document source='{doc.metadata.get('source', 'Doc')}' page='{doc.metadata.get('page', 'N/A')}'>\n{doc.page_content}\n</document>"
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
        logger.error(f"Error executing chat RAG pipeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to process question with AI legal assistant.")

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
        logger.error(f"Error generating legal application: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate legal application.")

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
        logger.error(f"Error generating legal triage: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dispute triage report.")

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
        logger.error(f"Error fetching matching schemes: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve welfare schemes.")


