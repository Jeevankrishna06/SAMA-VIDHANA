import os
import shutil
import time
import uuid
import logging
import threading
from collections import defaultdict
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import rag_engine
import schemes_data
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sama_vidhana_api")

# Load environment variables (.env)
load_dotenv()

# Startup Environment Validation
MISTRAL_API_KEY = rag_engine.get_mistral_api_key()
if not MISTRAL_API_KEY or MISTRAL_API_KEY in ["your_mistral_api_key_here", "your_actual_mistral_api_key_here", "YOUR_MISTRAL_API_KEY"]:
    logger.warning("CRITICAL: Valid MISTRAL_API_KEY environment variable is not configured. LLM-dependent features will fail.")

# Production Environment & CORS Configuration
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if origin.strip()
]

enable_docs = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"
app = FastAPI(
    title="SAMA-VIDHANA API",
    docs_url="/docs" if enable_docs else None,
    redoc_url=None,
    openapi_url="/openapi.json" if enable_docs else None,
)

# CORS Middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Vector Store & Upload Directory
GLOBAL_VS = None
USER_VECTORSTORES = {}  # filename -> FAISS index
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_TOTAL_UPLOAD_STORAGE = 100 * 1024 * 1024  # 100 MB total directory quota
MAX_STORED_FILES = 20  # Maximum user files stored simultaneously

def _enforce_storage_quota():
    """
    Prevents storage fill attacks by enforcing file count and total size quotas in UPLOAD_DIR.
    Prunes oldest uploaded files if quota is exceeded.
    """
    if not os.path.exists(UPLOAD_DIR):
        return

    files = []
    total_bytes = 0
    for fname in os.listdir(UPLOAD_DIR):
        fpath = os.path.join(UPLOAD_DIR, fname)
        if os.path.isfile(fpath):
            try:
                stat = os.stat(fpath)
                files.append((stat.st_mtime, fpath, fname, stat.st_size))
                total_bytes += stat.st_size
            except OSError:
                pass

    # Sort files by modification time (oldest first)
    files.sort(key=lambda x: x[0])

    while len(files) >= MAX_STORED_FILES or total_bytes > MAX_TOTAL_UPLOAD_STORAGE:
        if not files:
            break
        _, oldest_path, oldest_name, fsize = files.pop(0)
        try:
            os.remove(oldest_path)
            total_bytes -= fsize
            if oldest_name in USER_VECTORSTORES:
                del USER_VECTORSTORES[oldest_name]
            logger.info(f"Pruned oldest file {oldest_name} to maintain storage quota.")
        except OSError as e:
            logger.error(f"Failed to prune file {oldest_name}: {e}")

# In-Memory Sliding-Window Rate Limiter
_RATE_LIMIT_BUCKETS = defaultdict(list)
_RATE_LIMIT_LOCK = threading.Lock()

RATE_LIMITS = {
    "/api/upload": {"max_requests": 15, "window_seconds": 60},
    "/api/chat": {"max_requests": 30, "window_seconds": 60},
    "/api/generate-form": {"max_requests": 30, "window_seconds": 60},
    "/api/triage": {"max_requests": 30, "window_seconds": 60},
    "/api/schemes": {"max_requests": 40, "window_seconds": 60},
    "default": {"max_requests": 100, "window_seconds": 60},
}


def _check_rate_limit(client_ip: str, path: str) -> bool:
    config = RATE_LIMITS.get(path, RATE_LIMITS["default"])
    max_reqs = config["max_requests"]
    window = config["window_seconds"]
    now = time.time()
    key = f"{client_ip}:{path}"

    with _RATE_LIMIT_LOCK:
        timestamps = _RATE_LIMIT_BUCKETS[key]
        # Retain only timestamps within the active sliding window
        valid_timestamps = [t for t in timestamps if now - t < window]
        if len(valid_timestamps) >= max_reqs:
            _RATE_LIMIT_BUCKETS[key] = valid_timestamps
            return False
        valid_timestamps.append(now)
        _RATE_LIMIT_BUCKETS[key] = valid_timestamps
        return True


# Security Headers & Rate Limiting Middleware
@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path

    # Apply Rate Limiting
    if not _check_rate_limit(client_ip, path):
        logger.warning(f"Rate limit exceeded for IP {client_ip} on path {path}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down and try again later."},
            headers={"Retry-After": "60"},
        )

    # Process Request
    response = await call_next(request)

    # Inject Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' http://localhost:* http://127.0.0.1:*"
    )
    return response


# Global Exception Handler (Correlation ID & Safe Client Messages)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.error(f"[Error ID: {error_id}] Unhandled server exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred while processing your request.",
            "error_id": error_id,
        },
    )


# PII & Secret Redaction Helper
def _sanitize_log_data(data):
    if isinstance(data, dict):
        sanitized = {}
        secret_keywords = {"key", "secret", "token", "password", "auth", "bearer", "authorization"}
        pii_keywords = {
            "name", "applicant", "address", "phone", "email", "income", "age",
            "occupation", "description", "notes", "details", "relief", "opposing",
            "jurisdiction", "documents", "generated_text", "triage_report",
            "narrative", "incident", "authority"
        }
        for k, v in data.items():
            k_lower = k.lower()
            if any(kw in k_lower for kw in secret_keywords):
                sanitized[k] = "[REDACTED_SECRET]"
            elif any(kw in k_lower for kw in pii_keywords):
                sanitized[k] = "[REDACTED_PII]"
            else:
                sanitized[k] = _sanitize_log_data(v)
        return sanitized
    elif isinstance(data, list):
        return [_sanitize_log_data(item) for item in data]
    return data


def log_request_response(endpoint: str, payload: dict, response: dict):
    log_path = "../.log"
    try:
        import json
        safe_payload = _sanitize_log_data(payload)
        safe_response = _sanitize_log_data(response)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"=== [{endpoint}] ===\n")
            f.write(f"Input: {json.dumps(safe_payload, ensure_ascii=False, indent=2)}\n")
            f.write(f"Output: {json.dumps(safe_response, ensure_ascii=False, indent=2)}\n")
            f.write("-" * 40 + "\n\n")
    except Exception as e:
        logger.error(f"Logging error: {e}")


@app.on_event("startup")
async def startup_event():
    def index_background():
        global GLOBAL_VS
        logger.info("FastAPI: Starting global legal database indexing in background thread...")
        GLOBAL_VS = rag_engine.get_global_vectorstore()
        logger.info("FastAPI: Global legal database indexing completed successfully.")

    threading.Thread(target=index_background, daemon=True).start()


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
        "user_sources": uploaded_files,
    }


MAX_UPLOAD_SIZE = 15 * 1024 * 1024  # 15 MB limit

def _sanitize_filename(filename: str) -> str:
    """
    Prevents path traversal attacks by extracting basename and stripping illegal path characters.
    """
    import re
    base = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    if not clean.lower().endswith(".pdf"):
        clean += ".pdf"
    return clean

def _validate_safe_upload_path(filename: str) -> str:
    safe_name = _sanitize_filename(filename)
    target_path = os.path.abspath(os.path.join(UPLOAD_DIR, safe_name))
    upload_root = os.path.abspath(UPLOAD_DIR)
    if not target_path.startswith(upload_root):
        raise HTTPException(status_code=400, detail="Invalid filename or path traversal detected.")
    return target_path

@app.delete("/api/sources/{filename}")
async def delete_source(filename: str):
    """
    Data Deletion Flow: Permanently removes a user-uploaded PDF from disk and in-memory vectorstore.
    """
    safe_name = _sanitize_filename(filename)
    file_path = _validate_safe_upload_path(safe_name)

    if safe_name in USER_VECTORSTORES:
        del USER_VECTORSTORES[safe_name]

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            error_id = str(uuid.uuid4())
            logger.error(f"[Error ID: {error_id}] Error deleting file {safe_name}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete uploaded document.")

    return {"status": "success", "message": f"Source '{safe_name}' permanently deleted."}


@app.post("/api/clear-session")
async def clear_session_data():
    """
    Complete Data Deletion: Clears all user uploaded files, vectorstore indexes, and session data.
    """
    global USER_VECTORSTORES
    USER_VECTORSTORES = {}

    deleted_count = 0
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            fp = os.path.join(UPLOAD_DIR, f)
            try:
                if os.path.isfile(fp):
                    os.remove(fp)
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Error clearing upload file {f}: {e}")

    return {
        "status": "success",
        "message": "All user session data, vector stores, and uploaded files permanently erased.",
        "files_removed": deleted_count,
    }


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts PDF, validates magic bytes and file size, extracts text, indexes to FAISS in memory.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    # Enforce directory storage quota & auto-prune before saving new file
    _enforce_storage_quota()

    safe_name = _sanitize_filename(file.filename)
    file_path = _validate_safe_upload_path(safe_name)

    try:
        # Read initial chunk to validate PDF magic signature (%PDF-)
        initial_chunk = await file.read(1024)
        if not initial_chunk.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Invalid file content. Only authentic PDF files are accepted.")

        # Stream save with size limit enforcement
        total_size = len(initial_chunk)
        with open(file_path, "wb") as buffer:
            buffer.write(initial_chunk)
            while chunk := await file.read(64 * 1024):
                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=413, detail="File exceeds maximum permitted size of 15MB.")
                buffer.write(chunk)

        # Parse and Index PDF
        docs = rag_engine.extract_text_from_pdf(file_path)
        vs = rag_engine.build_faiss_index_from_documents(docs)
        USER_VECTORSTORES[safe_name] = vs

        return {
            "filename": safe_name,
            "status": "success",
            "page_count": len(docs),
        }
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        error_id = str(uuid.uuid4())
        logger.error(f"[Error ID: {error_id}] Error parsing/indexing uploaded PDF {safe_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process and index the uploaded PDF document.")


@app.post("/api/chat")
async def chat(payload: dict):
    """
    Accepts question and optional selected sources, retrieves context, and runs Mistral structured RAG.
    """
    question = payload.get("question", "").strip()
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
                        "risks": "Database starting up.",
                    },
                    "sources": [],
                }
                log_request_response("/api/chat", payload, res)
                return res
        else:
            try:
                global_retriever = GLOBAL_VS.as_retriever(search_kwargs={"k": 4})
                global_docs = global_retriever.invoke(question)
                retrieved_docs.extend(global_docs)
            except Exception as e:
                logger.error(f"Error querying global vectorstore: {e}")

    # 2. Query user uploaded documents
    for vs in active_user_vs:
        try:
            user_retriever = vs.as_retriever(search_kwargs={"k": 3})
            user_docs = user_retriever.invoke(question)
            retrieved_docs.extend(user_docs)
        except Exception as e:
            logger.error(f"Error querying user vectorstore: {e}")

    if not retrieved_docs:
        res = {
            "answer": {
                "rights": "The provided information does not contain the answer.",
                "eligibility": [],
                "benefits": "No relevant documents found in selected sources.",
                "risks": "Please verify your question or upload a document.",
            },
            "sources": [],
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
                "content": doc.page_content,
            })

        res = {
            "answer": parsed_answer,
            "sources": sources_list,
        }
        log_request_response("/api/chat", payload, res)
        return res
    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"[Error ID: {error_id}] RAG Chat invocation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate grounded legal analysis.")


@app.post("/api/generate-form")
async def generate_form(payload: dict):
    form_type = payload.get("form_type", "").strip()
    details = payload.get("details", {})
    if not form_type or not details:
        raise HTTPException(status_code=400, detail="Form type and details are required.")
    try:
        generated_text = rag_engine.generate_plaintext_application(form_type, details)
        res = {"generated_text": generated_text}
        log_request_response("/api/generate-form", payload, res)
        return res
    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"[Error ID: {error_id}] Form generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to draft legal notice.")


@app.post("/api/triage")
async def triage(payload: dict):
    if not payload.get("description", "").strip():
        raise HTTPException(status_code=400, detail="Incident narrative description is required.")
    try:
        triage_report = rag_engine.triage_citizen_dispute(payload)
        res = {"triage_report": triage_report}
        log_request_response("/api/triage", payload, res)
        return res
    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"[Error ID: {error_id}] Triage evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate situational triage report.")


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
                "content": doc.page_content,
            })

        res = {"schemes": schemes_list}
        log_request_response("/api/schemes", payload, res)
        return res
    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"[Error ID: {error_id}] Scheme search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve welfare schemes.")
