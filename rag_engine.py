import os
import io
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


# Strictly grounded system prompt constraint
STRICT_RAG_PROMPT_TEMPLATE = """You are a civic legal assistant. Answer solely using the retrieved context. If the answer is not present in the context, clearly state that the provided information does not contain the answer.

Explain statutory clauses, legal procedures, or civic rights in simple, plain English that an ordinary citizen can easily understand, without omitting key legal caveats.

Retrieved Context:
{context}

Citizen's Question:
{question}

Provide a structured, clear, and grounded answer:"""


def query_rag_engine(vectorstore: FAISS, question: str, k: int = 4) -> dict:
    """
    Retrieve top-k chunks from FAISS vectorstore and generate grounded answer with Mistral 7B.
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)

    if not docs:
        return {
            "answer": "The provided information does not contain the answer.",
            "source_documents": [],
        }

    formatted_context = "\n\n---\n\n".join(
        [
            f"[Source: {doc.metadata.get('source', 'Doc')} | Page: {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
            for doc in docs
        ]
    )

    llm = get_llm(temperature=0.1)
    prompt = ChatPromptTemplate.from_template(STRICT_RAG_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"context": formatted_context, "question": question})

    return {
        "answer": response,
        "source_documents": docs,
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
