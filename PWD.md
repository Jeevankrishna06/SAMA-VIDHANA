# SAMA-VIDHANA — Project Workflow Document

## 1. Project Overview

**Project Name:** SAMA-VIDHANA

**Hackathon:** OOSC — IIIT Allahabad

**Project Type:** AI-powered Civic and Legal Rights Assistant

SAMA-VIDHANA is an AI-based system designed to help citizens understand their civic and legal rights without requiring them to navigate complicated legal documents, government portals, notices, PDFs, or bureaucratic terminology on their own.

The system provides a simple, minimalistic web interface where citizens can communicate their problems, ask questions, and upload supporting documents.

SAMA-VIDHANA processes this information using NLP, Retrieval-Augmented Generation (RAG), LangChain, embeddings, and a Mistral 7B language model to generate a structured response.

The final response is organized into four primary categories:

* **Rights**
* **Eligibility**
* **Benefits**
* **Risks & Limitations**

---

# 2. Problem Being Addressed

Citizens often have legitimate rights and government entitlements but may not use them because:

* Legal and bureaucratic language is difficult to understand.
* Relevant information is scattered across multiple websites and documents.
* Government PDFs and notices can be lengthy and difficult to interpret.
* Citizens may not know which law, scheme, department, or authority applies to their situation.
* Existing portals generally provide information rather than solving an individual's specific problem.
* Understanding legal and bureaucratic documents can require significant time and expertise.

SAMA-VIDHANA aims to reduce this complexity by acting as an intelligent bridge between citizens and bureaucratic information.

---

# 3. Core Objective

The central objective of SAMA-VIDHANA is:

> **Convert complex civic and legal information into a clear, understandable, and actionable path for a citizen.**

Instead of requiring a citizen to understand legal terminology first, the system allows the citizen to explain the problem naturally.

For example:

```text
"My landlord hasn't returned my deposit.
What can I do?"
```

SAMA-VIDHANA processes the query and identifies the relevant information before presenting it in a structured format.

---

# 4. User Interface

SAMA-VIDHANA will use a **Minimalism UI** approach.

The interface will avoid unnecessary visual elements and focus on the user's problem and the resulting information.

The primary interface will consist of:

```text
┌───────────────────────────────────────────────────┐
│                  SAMA-VIDHANA                     │
│                                                   │
│  ┌──────────────────────┐  ┌───────────────────┐ │
│  │                      │  │                   │ │
│  │   CHAT / INPUT       │  │     RESPONSE      │ │
│  │                      │  │                   │ │
│  │   Ask a question     │  │     Rights        │ │
│  │   Upload a file      │  │     Eligibility   │ │
│  │                      │  │     Benefits      │ │
│  │                      │  │     Risks         │ │
│  └──────────────────────┘  └───────────────────┘ │
│                                                   │
└───────────────────────────────────────────────────┘
```

The design will prioritize:

* Minimal visual clutter
* Clear typography
* Simple navigation
* Strong information hierarchy
* Easy document upload
* Clear separation between user input and AI output
* Readability of legal/civic information

The interface should make complex information feel simple rather than visually overwhelming.

---

# 5. User Input

The user can interact with SAMA-VIDHANA through two primary input methods.

## 5.1 Chat Input

Users can describe their situation using natural language.

Examples:

```text
"Can I apply for this government scheme?"

"What rights do I have as a tenant?"

"I received this notice. What does it mean?"

"Can I file an RTI for this information?"
```

---

## 5.2 File Upload

Users can upload relevant documents along with their queries.

The planned maximum file size is:

**200 MB**

Potential documents include:

* Government notices
* Legal notices
* Government forms
* Scheme documents
* Official letters
* PDFs
* Other relevant civic/legal documents

The uploaded document becomes additional context for the AI system.

---

# 6. Natural Language Processing

NLP is an important component of SAMA-VIDHANA.

The system should understand a citizen's problem even when the citizen does not use formal legal terminology.

For example:

```text
User:
"My landlord is keeping my deposit and won't respond."

              ↓

NLP Processing

Domain:
Housing / Tenancy

Issue:
Security Deposit

Intent:
Understand Rights / Possible Action
```

The NLP layer can identify:

* User intent
* Entities
* Problem category
* Important facts
* Relevant concepts
* Dates
* Conditions
* Context from the user's query

The processed information is then used by the retrieval pipeline.

---

# 7. Knowledge Sources

SAMA-VIDHANA will use information from multiple Indian civic, legal, and government sources.

The planned sources are:

1. **India Code**
2. **eGazette**
3. **Indian Kanoon**
4. **India.gov.in**
5. **MyScheme**
6. **Vikaspedia**

These sources provide information related to:

* Indian laws
* Government notifications
* Government schemes
* Citizen services
* Eligibility requirements
* Legal information
* Government benefits
* Civic procedures

The information collected from these sources forms the foundation of the SAMA-VIDHANA knowledge base.

---

# 8. Knowledge Processing

Information collected from the sources will be processed before being used by the RAG system.

The pipeline is:

```text
Source Websites
      ↓
Data Collection
      ↓
Data Cleaning
      ↓
Text Extraction
      ↓
Document Chunking
      ↓
Metadata
      ↓
Embeddings
      ↓
Vector Database
```

The information is divided into smaller meaningful chunks so that the retrieval system can identify relevant sections for individual queries.

---

# 9. Document Processing

Uploaded documents will go through a separate processing pipeline.

```text
User Upload
     ↓
File Validation
     ↓
Document Extraction
     ↓
Text Extraction
     ↓
Cleaning
     ↓
Chunking
     ↓
Embedding
     ↓
Retrieval
```

The system can then combine:

```text
User Query
+
Uploaded Document
+
Legal / Government Knowledge
```

This allows SAMA-VIDHANA to answer questions about specific documents rather than relying only on generic information.

---

# 10. RAG Pipeline

Retrieval-Augmented Generation forms the core of the SAMA-VIDHANA AI architecture.

The system retrieves relevant information from the knowledge base before generating a response.

```text
User Query
     ↓
NLP Processing
     ↓
Query Embedding
     ↓
Vector Search
     ↓
Relevant Legal / Civic Information
     ↓
Context Assembly
     ↓
Mistral 7B
     ↓
Structured Response
```

This allows the generated response to be grounded in information retrieved from the project's selected sources.

---

# 11. Language Model

The planned language model is:

**Mistral 7B**

Mistral is used as the primary language generation and reasoning component.

The model receives:

* User query
* NLP-derived context
* Retrieved information
* Uploaded document information when applicable
* System instructions

It then generates the final structured response.

---

# 12. Four-Part Output

SAMA-VIDHANA provides four primary outputs.

## 12.1 Rights

Identifies the rights that may apply to the user's situation.

The information is explained in simple language rather than presenting only raw legal terminology.

---

## 12.2 Eligibility

Explains the requirements or conditions that determine whether the user qualifies.

Possible conditions include:

* Age
* Income
* Residency
* Employment status
* Documentation
* Scheme-specific requirements
* Jurisdiction

---

## 12.3 Benefits

Explains what the citizen may receive, claim, request, or do.

Depending on the situation, this may include:

* Government benefits
* Legal remedies
* Applications
* Complaints
* Appeals
* Available services
* Recommended actions

---

## 12.4 Risks & Limitations

Explains what the citizen should consider before taking action.

This can include:

* Exceptions
* Missing information
* Documentation requirements
* Deadlines
* Jurisdictional differences
* Possible consequences
* Uncertainty in interpretation

This section ensures that the system does not present its output as an absolute legal determination.

---

# 13. Source Transparency

SAMA-VIDHANA should associate important claims with their underlying sources wherever possible.

The user should be able to understand:

```text
AI Explanation
      ↓
Supporting Evidence
      ↓
Original Source
```

This provides transparency and allows citizens to verify the information.

---

# 14. Example User Journey

### Step 1 — User enters a problem

```text
"I received this government notice.
I don't understand what it means
or what I should do."
```

### Step 2 — User uploads the notice

The document is processed and converted into usable text.

### Step 3 — NLP understands the query

The system identifies the problem type and important information.

### Step 4 — RAG retrieves relevant information

The system searches the knowledge base for applicable laws, government information, schemes, or procedures.

### Step 5 — Mistral processes the context

Mistral generates an explanation based on the retrieved information and uploaded document.

### Step 6 — Minimal UI displays the result

```text
RIGHTS

What rights may apply?


ELIGIBILITY

What requirements apply?


BENEFITS / ACTIONS

What can you do?


RISKS & LIMITATIONS

What should you consider?


SOURCES

Where did this information come from?
```

---

# 15. Technology Components

The planned technology ecosystem includes:

* Web frontend
* Minimalism UI
* NLP
* LangChain
* Retrieval-Augmented Generation
* Embedding API
* Vector Database
* Mistral 7B
* Document processing
* Government/legal datasets
* Multiple government and legal information sources

Reinforcement Learning remains a potential future component and is not finalized for the initial implementation.

---

# 16. Product Philosophy

SAMA-VIDHANA follows three core principles:

### Simplicity

The citizen should not need legal expertise to understand the answer.

### Relevance

The system should focus on the user's specific situation rather than returning generic information.

### Actionability

The output should help the citizen understand what they can do next.

The Minimalism UI supports these principles by reducing unnecessary interface complexity and keeping attention focused on the user's problem and the resulting guidance.
