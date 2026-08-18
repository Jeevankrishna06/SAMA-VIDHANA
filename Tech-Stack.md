# SAMA-VIDHANA — Technology Stack

## 1. Overview

SAMA-VIDHANA uses an AI-first technology stack designed around Natural Language Processing, Retrieval-Augmented Generation, document understanding, semantic search, and a minimalistic web interface.

The stack is intentionally modular so that the AI pipeline, knowledge base, and frontend can be developed independently and integrated into a single system.

---

# 2. Technology Stack Overview

| Layer                  | Technology                                                              | Purpose                                          |
| ---------------------- | ----------------------------------------------------------------------- | ------------------------------------------------ |
| Frontend               | React.js                                                                | Web application interface                        |
| UI                     | Minimalism UI                                                           | Clean and focused user experience                |
| Styling                | CSS / Tailwind CSS                                                      | Interface styling and responsive design          |
| Backend                | Python                                                                  | AI and application backend                       |
| API Layer              | FastAPI                                                                 | Communication between frontend and AI pipeline   |
| NLP                    | Python NLP libraries / processing                                       | Query and context understanding                  |
| AI Orchestration       | LangChain                                                               | Connecting retrieval, prompts, documents and LLM |
| RAG                    | Retrieval-Augmented Generation                                          | Grounding responses using external knowledge     |
| LLM                    | Mistral 7B                                                              | Natural-language generation and reasoning        |
| Embeddings             | Embedding API                                                           | Converting text into vector representations      |
| Vector Database        | Vector Store                                                            | Semantic document retrieval                      |
| Document Processing    | PDF/document extraction libraries                                       | Processing uploaded files                        |
| Knowledge Base         | Curated civic/legal datasets                                            | Source of legal and government information       |
| Data Sources           | India Code, eGazette, Indian Kanoon, India.gov.in, MyScheme, Vikaspedia | Knowledge acquisition                            |
| Version Control        | Git + GitHub                                                            | Source-code management                           |
| Future Experimentation | Reinforcement Learning                                                  | Potential future optimization                    |

---

# 3. Frontend

## React.js

React.js will be used to build the SAMA-VIDHANA web application.

Responsibilities include:

* Chat interface
* File upload interface
* Conversation display
* Response rendering
* Rights section
* Eligibility section
* Benefits section
* Risks & Limitations section
* Source references
* Loading and processing states

The frontend will communicate with the backend through API requests.

---

# 4. UI Technology

The frontend will follow a **Minimalism UI** design philosophy.

The interface will use:

* Clean layouts
* Limited visual elements
* Clear typography
* Consistent spacing
* Simple interactions
* Minimal navigation
* Focused content presentation

The UI should make the complexity of the underlying AI system invisible to the citizen.

---

# 5. Styling

CSS or Tailwind CSS can be used for implementing the visual system.

The styling layer will control:

* Typography
* Spacing
* Cards
* Buttons
* Input fields
* Upload components
* Response sections
* Responsive layouts
* Animations and transitions where required

The visual design should remain restrained rather than becoming overly decorative.

---

# 6. Backend

## Python

Python will act as the primary backend and AI development language.

Python is suitable for SAMA-VIDHANA because the major AI components are built around the Python ecosystem.

It will handle:

* NLP
* Document processing
* RAG
* LangChain
* Embeddings
* Retrieval
* Mistral integration
* Response generation
* AI pipeline orchestration

---

# 7. API Layer

## FastAPI

FastAPI can be used to expose the AI functionality to the frontend.

The backend can provide endpoints such as:

```text id="a3qj9v"
POST /chat
POST /upload
POST /analyze
GET  /sources
```

Example workflow:

```text id="t4f6r8"
React Frontend
      ↓
FastAPI
      ↓
AI Pipeline
      ↓
Response
      ↓
React Frontend
```

---

# 8. Natural Language Processing

NLP will be used to understand the user's natural-language problem before retrieval.

The NLP layer can perform:

* Intent identification
* Entity extraction
* Query processing
* Context extraction
* Problem classification
* Important information identification

Example:

```text id="q6v4r1"
"My landlord hasn't returned my deposit."

             ↓ NLP

Domain → Housing / Tenancy
Issue → Security Deposit
Intent → Rights / Remedy
```

The resulting information can improve the quality of retrieval.

---

# 9. LangChain

LangChain will be used as the orchestration layer for the AI pipeline.

It will connect:

```text id="f8d1w2"
User Query
    ↓
NLP
    ↓
Retriever
    ↓
Relevant Documents
    ↓
Context
    ↓
Prompt
    ↓
Mistral 7B
    ↓
Response
```

LangChain will also assist with document loaders, retrieval chains, prompt management, and LLM integration.

---

# 10. Retrieval-Augmented Generation

RAG is one of the primary technologies used by SAMA-VIDHANA.

The system will retrieve relevant information from the project's knowledge base before generating an answer.

```text id="m2p6s9"
User Query
    ↓
Embedding
    ↓
Vector Search
    ↓
Relevant Knowledge
    ↓
Context
    ↓
Mistral 7B
    ↓
Answer
```

This allows the system to ground its responses in the collected legal and government information.

---

# 11. Embeddings

An embedding API will be used to convert text into vector representations.

The embedding pipeline will process:

* Government documents
* Legal documents
* Scheme information
* User documents
* User queries

Example:

```text id="u4s2a8"
"Eligibility for government scheme X"
                  ↓
            Embedding API
                  ↓
             Vector [ ... ]
```

The vector is then used for semantic retrieval.

---

# 12. Vector Database

A vector database/vector store will store the embeddings generated from the knowledge base.

Its primary function is semantic search.

```text id="d7q2x5"
Knowledge Documents
       ↓
   Embeddings
       ↓
 Vector Database
       ↓
Similarity Search
       ↓
Relevant Chunks
```

The vector store should also retain metadata associated with each document chunk.

Potential metadata:

* Source
* Document title
* Section
* Date
* Category
* Scheme
* Law
* Source reference

---

# 13. Mistral 7B

Mistral 7B will serve as the primary language model.

Its responsibilities include:

* Understanding retrieved context
* Reasoning over the user's situation
* Explaining legal/civic information
* Generating natural-language responses
* Structuring the response
* Producing the four primary outputs

The model receives:

```text id="c8w3n4"
System Prompt
+
User Query
+
NLP Context
+
Retrieved Information
+
Uploaded Document Context
```

---

# 14. Document Processing

SAMA-VIDHANA will support document uploads of up to approximately **200 MB**.

The document processing stack will be responsible for extracting usable information from uploaded files.

Pipeline:

```text id="s7m1p3"
File
 ↓
Validation
 ↓
Document Parser
 ↓
Text Extraction
 ↓
Cleaning
 ↓
Chunking
 ↓
Embedding
 ↓
Vector Retrieval
```

The extracted information can be combined with external legal and government information during RAG.

---

# 15. Knowledge Sources

The initial knowledge base will use the following sources:

### 1. India Code

Indian laws and legal provisions.

### 2. eGazette

Official government notifications and gazette information.

### 3. Indian Kanoon

Indian legal documents and case-law information.

### 4. India.gov.in

Government information and citizen services.

### 5. MyScheme

Government schemes and eligibility information.

### 6. Vikaspedia

Citizen-oriented government and welfare information.

---

# 16. Data Pipeline

The knowledge acquisition pipeline will be:

```text id="r8c3z1"
Source Websites
      ↓
Data Collection
      ↓
Cleaning
      ↓
Text Extraction
      ↓
Chunking
      ↓
Metadata
      ↓
Embeddings
      ↓
Vector Database
```

The processed knowledge can then be accessed by the RAG system.

---

# 17. Reinforcement Learning

Reinforcement Learning is currently an **optional/future component**.

It is not required for the initial MVP.

If implemented, potential applications include:

* Improving retrieval
* Ranking retrieved information
* Optimizing responses
* Learning from user feedback
* Improving system efficiency

The architecture should therefore remain modular enough to allow RL experimentation later.

---

# 18. Development Tools

The development environment will include:

* VS Code
* Git
* GitHub
* Python
* Node.js
* Package managers appropriate to the selected frontend/backend libraries

Git will be used for version control and collaborative development.

---

# 19. Overall Stack

```text id="z2y7p6"
                   SAMA-VIDHANA
                        │
              ┌─────────┴─────────┐
              │                   │
           FRONTEND            BACKEND
              │                   │
          React.js              Python
              │                   │
       Minimalism UI           FastAPI
                                  │
                     ┌────────────┼────────────┐
                     │            │            │
                    NLP       LangChain    Documents
                     │            │            │
                     └────────────┼────────────┘
                                  │
                                 RAG
                                  │
                             Embeddings
                                  │
                           Vector Database
                                  │
                              Mistral 7B
                                  │
                              Response
                                  │
                                  ▼
                              Frontend
```

---

# 20. Technology Objective

The technology stack is designed to support one primary objective:

> **Retrieve reliable civic/legal information, understand the citizen's situation, and convert that information into a simple actionable response.**
