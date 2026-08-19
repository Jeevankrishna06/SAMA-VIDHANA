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


@st.cache_resource(show_spinner="Loading Sentence-Transformers Embeddings...")
def get_embeddings():
    """
    Load and cache sentence-transformers/all-MiniLM-L6-v2 embeddings.
    """
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


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
        # Streamlit UploadedFile (BytesIO)
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


@st.cache_resource(show_spinner="Indexing Global Civic & Legal Knowledge Base...")
def get_global_vectorstore() -> FAISS:
    """
    Read all PDF files in the 'data/' directory, chunk them, and index into FAISS.
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
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
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


# Structured prompt for generating Rights, Eligibility, Benefits, and Risks
STRUCTURED_RAG_PROMPT_TEMPLATE = """You are SAMA-VIDHANA, a civic legal assistant. Answer solely using the retrieved context. If the answer is not present in the context, clearly state that the provided information does not contain the answer.

Explain statutory clauses, legal procedures, or civic rights in simple, plain English that an ordinary citizen can easily understand, without omitting key legal caveats.

Retrieved Context:
{context}

Citizen's Question:
{question}

You MUST output your response in JSON format. The JSON object must contain the following keys:
1. "rights": Explain the civic and legal rights that apply to the citizen's situation based on the context. Keep it in plain, readable English. (string/markdown)
2. "eligibility": List the eligibility conditions or requirements mentioned in the context. For each condition, determine its status based on the user's question (e.g., "Satisfied", "Required", "Information Needed"). Format this as a JSON list of objects, each with "condition" and "status" keys.
3. "benefits": Explain what benefits, remedies, or actions the citizen can take based on the context (e.g., how to apply, who to contact, next steps). (string/markdown)
4. "risks": Explain what risks, limitations, exceptions, deadlines, or warnings the citizen should consider. (string/markdown)

Ensure the output is valid JSON and nothing else. Do not wrap in markdown code blocks.
"""


def parse_json_response(response_text: str) -> dict:
    """
    Strips markdown code block markers and parses JSON reliably.
    """
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
        cleaned = cleaned.strip()
    
    try:
        data = json.loads(cleaned)
        # Ensure all required keys exist
        for key in ["rights", "eligibility", "benefits", "risks"]:
            if key not in data:
                data[key] = ""
        return data
    except Exception as e:
        print(f"JSON parsing error: {e}")
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                for key in ["rights", "eligibility", "benefits", "risks"]:
                    if key not in data:
                        data[key] = ""
                return data
            except Exception:
                pass
        
        # Fallback structure
        return {
            "rights": response_text,
            "eligibility": [{"condition": "Verify requirements in sources", "status": "Information Needed"}],
            "benefits": "Please check reference materials for actionable steps.",
            "risks": "Verify timelines and exceptions."
        }


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
"""
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()

    formatted_details = "\n".join([f"- {k}: {v}" for k, v in details.items() if v])
    return chain.invoke({"form_type": form_type, "details": formatted_details})


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
1. ⚖️ **Procedural Validity & Legal Grounding**: Identify relevant statutory acts, consumer rights, labor codes, or constitutional protections.
2. 🏛️ **Designated Authority / Forum**: State the exact government department, ombudsman, tribunal, regulatory body, or court with jurisdiction (e.g., RERA, District Consumer Commission, Labor Officer, Lok Adalat, Police/Cyber Crime Portal).
3. ⏱️ **Limitation Period & Urgency**: Mention statutory filing deadlines (e.g., 2 years under Consumer Protection Act, 30 days under RTI).
4. 📋 **Mandatory Checklist of Evidentiary Documents**: What proofs the citizen must collect before filing.
5. 🚀 **Step-by-Step Action Roadmap**: Chronological steps (e.g., Step 1: Formal Notice / Grievance, Step 2: Escalation to Regulatory Portal, Step 3: Formal Petition).

Keep the language empowering, clear, precise, and practical for an ordinary citizen.
"""
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "category": dispute_info.get("category", "General"),
        "jurisdiction": dispute_info.get("jurisdiction", "India"),
        "description": dispute_info.get("description", "Not provided"),
        "opposing_party": dispute_info.get("opposing_party", "Not specified"),
        "status": dispute_info.get("status", "Initial stage"),
        "documents": dispute_info.get("documents", "None mentioned"),
    })
