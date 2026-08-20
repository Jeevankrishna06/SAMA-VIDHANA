import os
import io
import json
import re
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# Load local environment variables from .env if present
load_dotenv()


def get_mistral_api_key() -> str:
    """
    Retrieve the Mistral API Key securely from .env, environment variable,
    or Streamlit secrets (for cloud deployment).
    """
    # 1. Check local environment variable / .env
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key and api_key.strip() and api_key != "your_mistral_api_key_here":
        return api_key.strip()

    # 2. Check Streamlit secrets (Streamlit Community Cloud)
    try:
        if "MISTRAL_API_KEY" in st.secrets:
            secret_key = st.secrets["MISTRAL_API_KEY"]
            if secret_key and secret_key.strip():
                return secret_key.strip()
    except Exception:
        pass

    return ""


_GLOBAL_EMBEDDINGS = None
_GLOBAL_VECTORSTORE = None


def get_embeddings():
    """
    Load and cache sentence-transformers/all-MiniLM-L6-v2 embeddings.
    """
    global _GLOBAL_EMBEDDINGS
    if _GLOBAL_EMBEDDINGS is None:
        _GLOBAL_EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _GLOBAL_EMBEDDINGS


def get_llm(temperature: float = 0.2):
    """
    Initialize Mistral 7B via official langchain-mistralai ChatMistralAI.
    """
    api_key = get_mistral_api_key()
    if not api_key:
        raise ValueError(
            "Mistral API Key not found. Please add MISTRAL_API_KEY in your .env file or Streamlit secrets."
        )
    return ChatMistralAI(
        model="open-mistral-7b",
        api_key=api_key,
        temperature=temperature,
    )


def extract_text_from_pdf(uploaded_file) -> list[Document]:
    """
    Extract text per page from an uploaded PDF or file path using pypdf.
    """
    if isinstance(uploaded_file, (str, os.PathLike)):
        reader = PdfReader(uploaded_file)
        file_name = os.path.basename(uploaded_file)
    else:
        # Streamlit UploadedFile or file-like object (BytesIO)
        pdf_bytes = io.BytesIO(uploaded_file.read())
        reader = PdfReader(pdf_bytes)
        file_name = getattr(uploaded_file, "name", "uploaded_document.pdf")

    documents = []
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": file_name, "page": page_idx + 1},
                )
            )
    return documents


def build_faiss_index_from_documents(documents: list[Document]) -> FAISS:
    """
    Split documents with chunk_size=600, chunk_overlap=100 and create FAISS vectorstore.
    """
    if not documents:
        raise ValueError("No text content could be extracted from the document.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", "Section ", "Article ", ". ", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


def build_faiss_index_from_texts(texts: list[str], metadatas: list[dict] = None) -> FAISS:
    """
    Build FAISS index directly from raw text strings and metadata.
    """
    embeddings = get_embeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    
    docs = []
    for i, t in enumerate(texts):
        meta = metadatas[i] if metadatas and i < len(metadatas) else {}
        sub_docs = text_splitter.create_documents([t], metadatas=[meta])
        docs.extend(sub_docs)
        
    return FAISS.from_documents(docs, embeddings)


def get_global_vectorstore() -> FAISS:
    """
    Load pre-built FAISS index from 'faiss_index/' if available,
    otherwise read all PDF files in 'data/', chunk them, and build index.
    Caches the FAISS index locally to speed up startup.
    """
    global _GLOBAL_VECTORSTORE
    if _GLOBAL_VECTORSTORE is not None:
        return _GLOBAL_VECTORSTORE

    base_dir = os.path.dirname(__file__)
    faiss_dir = os.path.join(base_dir, "faiss_index")
    embeddings = get_embeddings()

    # 1. Try loading from saved faiss_index directory
    if os.path.exists(faiss_dir) and (
        os.path.exists(os.path.join(faiss_dir, "index.faiss")) or
        os.path.exists(os.path.join(faiss_dir, "index.pkl"))
    ):
        try:
            print(f"Loading pre-indexed FAISS knowledge base from {faiss_dir}...")
            _GLOBAL_VECTORSTORE = FAISS.load_local(faiss_dir, embeddings, allow_dangerous_deserialization=True)
            print(f"Global FAISS index loaded with {_GLOBAL_VECTORSTORE.index.ntotal} vectors.")
            return _GLOBAL_VECTORSTORE
        except Exception as e:
            print(f"Error loading local faiss_index: {e}. Falling back to parsing data/ PDFs...")

    # 2. Build index from data/ PDFs
    data_dir = os.path.join(base_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        return None

    pdf_files = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    if not pdf_files:
        return None

    all_docs = []
    for pdf_file in pdf_files:
        path = os.path.join(data_dir, pdf_file)
        try:
            docs = extract_text_from_pdf(path)
            all_docs.extend(docs)
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")

    if not all_docs:
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", "Section ", "Article ", ". ", " ", ""],
    )
    chunks = text_splitter.split_documents(all_docs)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Cache to disk for instant future boots
    try:
        vectorstore.save_local(faiss_dir)
    except Exception as e:
        print(f"Warning: Could not save FAISS index to disk: {e}")

    _GLOBAL_VECTORSTORE = vectorstore
    return _GLOBAL_VECTORSTORE


# Structured prompt for generating Rights, Eligibility, Benefits, and Risks
STRUCTURED_RAG_PROMPT_TEMPLATE = """You are SAMA-VIDHANA, a civic and legal empowerment assistant. Answer solely using the retrieved context. If the answer is not present in the context, clearly state that the provided information does not contain the answer.

Explain statutory clauses, legal procedures, or civic rights in simple, plain English that an ordinary citizen can easily understand, without omitting key legal caveats.

Retrieved Context:
{context}

Citizen's Question:
{question}

Instructions:
1. Do NOT format your response as JSON. Do NOT output JSON objects, arrays, keys, or curly braces ({{}}).
2. Structure your response in plain text using EXACTLY these four sections in order:

Rights:
Provide a structured list of bullet points using standard hyphens (-) for each right (e.g., "- Right Title: Explanation of right"). Output plain text only without asterisks or bolding.

Eligibility:
Provide a structured list of statutory conditions or criteria mentioned in the context, along with status (Satisfied, Required, or Information Needed). Format each condition as a bullet point using standard hyphens (-) (e.g., "- Must be an Indian citizen (Satisfied)").

Benefits:
Provide a structured list of bullet points using standard hyphens (-) explaining remedies, reliefs, schemes, compensations, or actions the citizen can take based on the context.

Risks:
Provide a structured list of bullet points using standard hyphens (-) explaining limitations, exceptions, statutory deadlines, risks, or caveats the citizen should consider.

CRITICAL: Do not use any markdown formatting. Do not use asterisks, bolding, italics, or headers (e.g., ###). Output plain text only. You may use standard hyphens (-) for lists at maximum.
"""


def _normalize_parsed_response(data: dict) -> dict:
    """
    Guarantees strict schema adherence for the React frontend:
    - rights: str (markdown bullet points)
    - eligibility: list[dict] where each item is {"condition": str, "status": str}
    - benefits: str (markdown bullet points)
    - risks: str (markdown bullet points)
    Coerces capitalised keys (e.g., "Rights", "ELIGIBILITY") and converts lists into a single newline-separated markdown string.
    """
    normalized = {
        "rights": "",
        "eligibility": [],
        "benefits": "",
        "risks": ""
    }
    
    if not isinstance(data, dict):
        return normalized

    for raw_key, value in data.items():
        key = str(raw_key).strip().lower()
        
        if key in ["rights", "benefits", "risks"]:
            if isinstance(value, list):
                items = []
                for item in value:
                    if isinstance(item, dict):
                        item_str = " - ".join(f"**{k}**: {v}" for k, v in item.items())
                        items.append(f"- {item_str}")
                    else:
                        item_s = str(item).strip()
                        if item_s and not (item_s.startswith("-") or item_s.startswith("*")):
                            item_s = f"- {item_s}"
                        if item_s:
                            items.append(item_s)
                normalized[key] = "\n".join(items)
            elif isinstance(value, dict):
                items = [f"- **{k}**: {v}" for k, v in value.items()]
                normalized[key] = "\n".join(items)
            else:
                normalized[key] = str(value or "").strip()
                
        elif key == "eligibility":
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        # Normalise capitalised or alternative keys
                        cond = (
                            item.get("condition")
                            or item.get("Condition")
                            or item.get("requirement")
                            or item.get("Requirement")
                            or item.get("criteria")
                            or item.get("Criteria")
                            or ""
                        )
                        stat = (
                            item.get("status")
                            or item.get("Status")
                            or "Information Needed"
                        )
                        normalized["eligibility"].append({
                            "condition": str(cond).strip(),
                            "status": str(stat).strip()
                        })
                    elif isinstance(item, str):
                        item_s = item.strip().lstrip("-* ").strip()
                        if not item_s:
                            continue
                        status_found = "Information Needed"
                        clean_cond = item_s
                        for possible_status in ["Satisfied", "Required", "Information Needed", "Eligible", "Not Satisfied"]:
                            if re.search(rf"\b{re.escape(possible_status)}\b", item_s, re.IGNORECASE):
                                status_found = possible_status.title()
                                clean_cond = re.sub(rf"[\(\|\[\-–:]*\s*{re.escape(possible_status)}\s*[\)\]]*", "", clean_cond, flags=re.IGNORECASE).strip(" |:-")
                                break
                        normalized["eligibility"].append({
                            "condition": clean_cond or item_s,
                            "status": status_found
                        })
            elif isinstance(value, dict):
                for k, v in value.items():
                    normalized["eligibility"].append({
                        "condition": str(k).strip(),
                        "status": str(v).strip()
                    })
            elif isinstance(value, str):
                lines = [l.strip().lstrip("-* ") for l in value.split("\n") if l.strip()]
                for l in lines:
                    normalized["eligibility"].append({
                        "condition": l,
                        "status": "Information Needed"
                    })
                    
    return normalized


def parse_json_response(response_text: str) -> dict:
    """
    Parses model response into structured dictionary:
    - rights: str (bullet points or plain text)
    - eligibility: list[dict] where each item is {"condition": str, "status": str}
    - benefits: str (bullet points or plain text)
    - risks: str (bullet points or plain text)
    Supports plain text section headers (e.g. 'Rights:', 'Rights', '1. Rights'),
    markdown headers ('### Rights', '**Rights**'), direct JSON, and resilient fallbacks.
    """
    import json
    import re
    import ast

    if not response_text:
        return _normalize_parsed_response({})

    cleaned = response_text.strip()

    # 1. Primary Strategy: Match Section Headers (plain text or markdown: Rights, Eligibility, Benefits, Risks)
    # Matches patterns like: '### Rights', 'Rights:', 'Rights', '1. Rights', '**Rights**', etc.
    header_pattern = r'(?:^|\n)[ \t]*(?:#{1,6}[ \t]*|\*{1,2}|\d+[\.\)][ \t]*|\[)?[ \t]*(Rights|Eligibility|Benefits|Risks)[ \t]*[\*\]:]*[ \t]*(?:\n|(?=[ \t]+[^\n]))'
    matches = list(re.finditer(header_pattern, cleaned, flags=re.IGNORECASE))
    if matches:
        parsed_sections = {"rights": "", "eligibility": [], "benefits": "", "risks": ""}
        for idx, match in enumerate(matches):
            header = match.group(1).lower()
            start_pos = match.end()
            end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(cleaned)
            content = cleaned[start_pos:end_pos].strip()
            # Clean optional leading colon or stray symbols on same line
            content = re.sub(r'^[ \t]*:?[ \t]*', '', content).strip()
            if header in ["rights", "benefits", "risks"]:
                parsed_sections[header] = content
            elif header == "eligibility":
                lines = [line.strip().lstrip("-*• ") for line in content.split("\n") if line.strip()]
                parsed_sections["eligibility"] = lines

        if parsed_sections["rights"] or parsed_sections["eligibility"] or parsed_sections["benefits"] or parsed_sections["risks"]:
            return _normalize_parsed_response(parsed_sections)

    # 2. Secondary Strategy: Direct JSON parsing
    unwrapped = cleaned
    if unwrapped.startswith("```"):
        unwrapped = re.sub(r"^```[a-zA-Z]*\n", "", unwrapped)
        unwrapped = re.sub(r"\n```$", "", unwrapped)
        unwrapped = unwrapped.strip()

    try:
        data = json.loads(unwrapped, strict=False)
        if isinstance(data, dict):
            return _normalize_parsed_response(data)
    except Exception:
        pass

    # 3. Tertiary Strategy: Extract JSON object via regex match
    json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if json_match:
        json_candidate = json_match.group(1).strip()
        try:
            data = json.loads(json_candidate, strict=False)
            if isinstance(data, dict):
                return _normalize_parsed_response(data)
        except Exception:
            pass

        try:
            data = ast.literal_eval(json_candidate)
            if isinstance(data, dict):
                return _normalize_parsed_response(data)
        except Exception:
            pass

    # 4. Field-level Regex Fallback for individual JSON-like keys
    def extract_field_value(field_name, next_field_name, text):
        pattern = rf'"{field_name}"\s*:\s*(.*?)\s*,\s*"{next_field_name}"' if next_field_name else rf'"{field_name}"\s*:\s*(.*?)\s*}}\s*$'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if not match and not next_field_name:
            match = re.search(rf'"{field_name}"\s*:\s*(.*?)\s*[^"]*$', text, re.DOTALL | re.IGNORECASE)
        if match:
            val_str = match.group(1).strip()
            try:
                return json.loads(val_str, strict=False)
            except Exception:
                pass
            try:
                return ast.literal_eval(val_str)
            except Exception:
                pass
            if val_str.startswith('"') and val_str.endswith('"'):
                return val_str[1:-1].replace('\\"', '"').replace('\\n', '\n')
            return val_str
        return None

    try:
        parsed_data = {}
        for f_name, n_name in [("rights", "eligibility"), ("eligibility", "benefits"), ("benefits", "risks"), ("risks", None)]:
            val = extract_field_value(f_name, n_name, cleaned) or extract_field_value(f_name.capitalize(), n_name.capitalize() if n_name else None, cleaned)
            if val is not None:
                parsed_data[f_name] = val
        if parsed_data:
            return _normalize_parsed_response(parsed_data)
    except Exception as e:
        print(f"Field regex parser error: {e}")

    # 5. Final fallback structure
    return _normalize_parsed_response({
        "rights": cleaned,
        "eligibility": [{"condition": "Verify requirements in reference sources", "status": "Information Needed"}],
        "benefits": "- Please review retrieved context and reference materials for actionable steps.",
        "risks": "- Verify timelines, limitations, and statutory exceptions."
    })


def query_rag_engine(global_vs: FAISS, user_vs: FAISS, question: str, k: int = 4) -> dict:
    """
    Retrieve top-k chunks from global and/or user vectorstores,
    and generate a structured answer with Mistral 7B.
    """
    retrieved_docs = []
    
    # Retrieve from global database
    if global_vs is not None:
        try:
            global_retriever = global_vs.as_retriever(search_kwargs={"k": k})
            global_docs = global_retriever.invoke(question)
            retrieved_docs.extend(global_docs)
        except Exception as e:
            print(f"Error querying global vector store: {e}")
        
    # Retrieve from user uploaded PDF
    if user_vs is not None:
        try:
            user_retriever = user_vs.as_retriever(search_kwargs={"k": k})
            user_docs = user_retriever.invoke(question)
            retrieved_docs.extend(user_docs)
        except Exception as e:
            print(f"Error querying user vector store: {e}")

    if not retrieved_docs:
        return {
            "answer": {
                "rights": "The provided information does not contain the answer.",
                "eligibility": [],
                "benefits": "No relevant documents found.",
                "risks": "Please verify your question or upload a document."
            },
            "source_documents": [],
        }

    formatted_context = "\n\n---\n\n".join(
        [
            f"[Source: {doc.metadata.get('source', 'Doc')} | Page: {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
            for doc in retrieved_docs
        ]
    )

    llm = get_llm(temperature=0.1)
    prompt = ChatPromptTemplate.from_template(STRUCTURED_RAG_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"context": formatted_context, "question": question})
    parsed_answer = parse_json_response(response)

    return {
        "answer": parsed_answer,
        "source_documents": retrieved_docs,
    }


def generate_plaintext_application(form_type: str, details: dict) -> str:
    """
    Generate a clean, standardized plaintext legal or civic application (e.g., RTI request, consumer notice).
    """
    llm = get_llm(temperature=0.2)

    prompt_text = """You are an expert civic legal document drafter. Your task is to generate a comprehensive, professional, ready-to-submit plaintext legal/civic application based ONLY on the details provided by the citizen.

Application Type: {form_type}
Applicant & Dispute Details:
{details}

Requirements:
1. Format as clean, properly aligned plain text suitable for direct copying, printing, or submitting to government offices/portals.
2. Include standard legal headings (e.g., To Public Information Officer / Consumer Grievance Redressal Authority, Subject, Applicant Information, Specific Information/Grievance Requested, List of Enclosures, Declaration, and Signature line).
3. Insert appropriate statutory references (e.g., Section 6(1) of RTI Act 2005 for RTI requests; Consumer Protection Act 2019 for consumer claims).
4. Clearly mark placeholders like [Date], [Fee Details / Postal Order No.] if not provided.
5. Do not include markdown code block markers in the final plain text output. Return pure, clean text.

CRITICAL: Do not use any markdown formatting. Do not use asterisks, bolding, italics, or headers (e.g., ###). Output plain text only. You may use standard hyphens (-) for lists at maximum.
CRITICAL: Do not wrap your output in backticks or markdown code blocks (```). Return raw text only.
"""
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()

    formatted_details = "\n".join([f"- {k}: {v}" for k, v in details.items() if v])
    raw_output = chain.invoke({"form_type": form_type, "details": formatted_details})
    return raw_output.replace("```markdown", "").replace("```", "").strip()


def triage_citizen_dispute(dispute_info: dict) -> str:
    """
    Evaluate citizen's legal situation, procedural validity, limitation periods,
    appropriate authority/forum, and step-by-step sequential action plan.
    """
    llm = get_llm(temperature=0.2)

    prompt_text = """You are a senior civic legal triage expert. Analyze the citizen's legal issue and generate a clear, actionable triage assessment.

Citizen's Issue Profile:
- Category: {category}
- Jurisdiction / State: {jurisdiction}
- Nature of Dispute / Incident: {description}
- Opposing Party: {opposing_party}
- Current Status / Previous Actions Taken: {status}
- Available Supporting Documents: {documents}

Produce a structured legal triage response with these exact sections:
1. ⚖️ **Procedural Validity & Legal Grounding**: Identify relevant statutory acts, consumer rights, labor codes, or constitutional protections. Use bullet points.
2. 🏛️ **Designated Authority / Forum**: State the exact government department, ombudsman, tribunal, regulatory body, or court with jurisdiction. Use bullet points.
3. ⏱️ **Limitation Period & Urgency**: Mention statutory filing deadlines and urgency level. Use bullet points.
4. 📋 **Mandatory Checklist of Evidentiary Documents**: What proofs the citizen must collect before filing. Use bullet points.
5. 🚀 **Step-by-Step Action Roadmap**: Chronological, sequential action steps the citizen should take. Use bullet points.

Formatting Rules:
- The entire output MUST be structured systematically and logically using clean Markdown bullet points.
- Do NOT include any conversational filler, follow-up offers, sign-offs, or chat-like endings (e.g. do NOT say "Let me know if you need help...", "I can help you draft...", "You've got this", or ask any questions at the end).
- Stop writing immediately after the final bullet point of the "Step-by-Step Action Roadmap". The response must end strictly with that bullet point.
- CRITICAL: Do not wrap your output in backticks or markdown code blocks (```). Return raw text only.
"""
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()

    raw_output = chain.invoke({
        "category": dispute_info.get("category", "General"),
        "jurisdiction": dispute_info.get("jurisdiction", "India"),
        "description": dispute_info.get("description", "Not provided"),
        "opposing_party": dispute_info.get("opposing_party", "Not specified"),
        "status": dispute_info.get("status", "Initial stage"),
        "documents": dispute_info.get("documents", "None mentioned"),
    })
    return raw_output.replace("```markdown", "").replace("```", "").strip()
