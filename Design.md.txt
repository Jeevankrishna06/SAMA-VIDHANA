# SAMA-VIDHANA — Design System

## 1. Design Philosophy

SAMA-VIDHANA follows a **Minimalism UI** philosophy.

The project deals with complex civic and legal information. Therefore, the interface should not add another layer of complexity.

The design principle is:

> **Complexity belongs in the system, not in the interface.**

The user should see a simple interface while the underlying system handles:

* NLP
* RAG
* Document processing
* Retrieval
* Embeddings
* Legal information
* AI reasoning

---

# 2. Design Goals

The interface should prioritize:

1. **Simplicity**
2. **Readability**
3. **Clarity**
4. **Trust**
5. **Accessibility**
6. **Focused interaction**
7. **Minimal cognitive load**

The citizen should immediately understand:

* Where to ask a question
* Where to upload a document
* What the AI is doing
* What the result means
* Where the information came from

---

# 3. Overall Layout

The primary interface will use a two-part layout.

```text id="k3n7v2"
┌──────────────────────────────────────────────────────────┐
│                    SAMA-VIDHANA                          │
├────────────────────────┬─────────────────────────────────┤
│                        │                                 │
│                        │                                 │
│    INPUT / CHAT        │       AI RESPONSE               │
│                        │                                 │
│  Ask your question     │       RIGHTS                    │
│                        │                                 │
│  + Upload document     │       ELIGIBILITY               │
│                        │                                 │
│                        │       BENEFITS                  │
│                        │                                 │
│                        │       RISKS & LIMITATIONS       │
│                        │                                 │
│                        │       SOURCES                   │
│                        │                                 │
└────────────────────────┴─────────────────────────────────┘
```

The left side is focused on **interaction**.

The right side is focused on **understanding the result**.

---

# 4. Minimalism UI

The interface should avoid unnecessary visual complexity.

### Avoid

* Excessive gradients
* Excessive animations
* Too many buttons
* Dense navigation bars
* Decorative elements without purpose
* Large numbers of colors
* Unnecessary popups
* Overloaded dashboards

### Prefer

* Generous whitespace
* Clear typography
* Simple cards
* Consistent spacing
* Subtle borders
* Clear hierarchy
* Limited color usage
* Simple icons
* Focused interactions

---

# 5. Visual Hierarchy

The interface should make the most important information visually obvious.

Priority order:

```text id="d9w5e1"
1. User Question
        ↓
2. Main Answer
        ↓
3. Rights
        ↓
4. Eligibility
        ↓
5. Benefits / Actions
        ↓
6. Risks & Limitations
        ↓
7. Sources
```

The design should prevent secondary information from competing visually with the primary answer.

---

# 6. Typography

Typography should prioritize readability because the system will display potentially long explanations.

Recommended principles:

* Use a clean sans-serif font.
* Maintain clear heading hierarchy.
* Keep body text comfortable to read.
* Avoid excessively small text.
* Use bold text selectively.
* Keep line lengths reasonable.
* Maintain consistent spacing between sections.

Example hierarchy:

```text id="n2h6a3"
SAMA-VIDHANA

Your Civic Rights

Rights
What rights may apply...

Eligibility
What requirements apply...

Benefits
What can you do...

Risks & Limitations
What should you consider...
```

---

# 7. Color Philosophy

The color system should remain restrained.

The interface should primarily use:

* Neutral background
* Neutral text
* One primary accent
* Limited semantic colors

Semantic colors may be used where necessary to distinguish information types.

For example:

```text id="c1j4r8"
Rights
→ Primary / neutral emphasis

Eligibility
→ Positive or neutral emphasis

Benefits
→ Positive emphasis

Risks & Limitations
→ Warning emphasis

Sources
→ Secondary / muted emphasis
```

Color should support information hierarchy rather than become the main visual feature.

---

# 8. Chat Interface

The chat interface should feel simple and familiar.

The input area should provide:

```text id="j6q9s2"
┌───────────────────────────────────────────────┐
│ Ask SAMA-VIDHANA anything...                  │
│                                               │
│                                   📎    ↑     │
└───────────────────────────────────────────────┘
```

The user should be able to:

* Type a question
* Attach a document
* Submit the query
* Continue the conversation

The input area should remain visually unobtrusive until needed.

---

# 9. File Upload

The file-upload interaction should be integrated into the chat interface instead of creating a separate complicated page.

Example:

```text id="x5k2r9"
┌──────────────────────────────────┐
│  Upload a document               │
│                                  │
│  Drag & drop or choose a file    │
│                                  │
│  Maximum size: 200 MB            │
└──────────────────────────────────┘
```

After upload:

```text id="m8q4c1"
✓ document.pdf

Ready to analyze
```

The interface should clearly indicate:

* Upload status
* Processing status
* Completion
* Errors

---

# 10. AI Processing State

Because document processing and RAG may take time, the interface should communicate what the system is doing.

Possible states:

```text id="v7p3d2"
Analyzing your question...
       ↓
Searching relevant sources...
       ↓
Reviewing the information...
       ↓
Preparing your answer...
```

The UI should remain minimal rather than showing technical logs.

The user does not need to see:

```text
Embedding generated
Vector similarity = 0.83
Retriever returned 5 chunks
```

Instead, they should see understandable progress information.

---

# 11. Response Design

The generated answer should not appear as one large block of text.

It should be divided into clearly identifiable sections.

```text id="e3k7p1"
┌───────────────────────────────────────────┐
│ RIGHTS                                    │
│                                           │
│ You may have the right to...              │
│                                           │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│ ELIGIBILITY                               │
│                                           │
│ The following conditions may apply...     │
│                                           │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│ BENEFITS / ACTIONS                        │
│                                           │
│ You may be able to...                     │
│                                           │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│ RISKS & LIMITATIONS                       │
│                                           │
│ Consider the following before acting...   │
│                                           │
└───────────────────────────────────────────┘
```

---

# 12. Rights Section

The Rights section should answer:

> **What rights may apply to me?**

The section should prioritize:

* Clear language
* Short explanations
* Relevant legal context
* Supporting sources

Legal terminology can be included when necessary, but should be explained in plain language.

---

# 13. Eligibility Section

The Eligibility section should make requirements easy to scan.

Instead of presenting a long paragraph, information can be structured as:

```text id="r4s7v2"
Requirement          Status

Age                  ✓ Satisfied

Income               ? Information needed

Residency             ✓ Satisfied

Documents             ⚠ Required
```

This makes eligibility easier to understand at a glance.

---

# 14. Benefits / Actions Section

The Benefits section should be action-oriented.

Instead of only explaining what a scheme or right is, the interface should help the user understand what they can do.

Example:

```text id="p8w3m6"
NEXT STEPS

1. Gather the required documents.
2. Submit the application.
3. Contact the relevant authority.
4. Keep the acknowledgement/reference number.
```

Where applicable, the system can provide relevant official sources.

---

# 15. Risks & Limitations Section

This section should be visually distinguishable without becoming visually aggressive.

It should communicate:

* Potential risks
* Exceptions
* Missing information
* Deadlines
* Jurisdiction-specific limitations
* Possible consequences
* AI limitations

The purpose is to encourage informed action rather than blind reliance.

---

# 16. Sources

Sources should be visible but should not dominate the main answer.

Example:

```text id="f2r8w1"
Sources

India Code
Section / Document Reference

MyScheme
Scheme Information

eGazette
Notification Reference
```

The source area should allow users to understand where the information came from.

---

# 17. Document Analysis View

When analyzing a document, the interface can display the uploaded document alongside the generated interpretation.

```text id="z5c9n4"
┌──────────────────────┬─────────────────────────────┐
│                      │                             │
│   DOCUMENT           │   SAMA-VIDHANA ANALYSIS     │
│                      │                             │
│   Page 1             │   What is this document?    │
│   Page 2             │                             │
│   Page 3             │   Rights                    │
│                      │   Eligibility               │
│                      │   Benefits                  │
│                      │   Risks                     │
│                      │                             │
└──────────────────────┴─────────────────────────────┘
```

This allows the citizen to keep the original document in context while reading the explanation.

---

# 18. Responsive Design

The interface should work across:

* Desktop
* Laptop
* Tablet
* Mobile

On smaller screens, the two-column layout can transition into a stacked layout:

```text id="b1v5x7"
INPUT
  ↓
RESPONSE
  ↓
SOURCES
```

The core functionality should remain accessible regardless of screen size.

---

# 19. Interaction Principles

Interactions should follow predictable patterns.

### Input

User enters a problem.

### Upload

User attaches supporting information.

### Process

System analyzes the information.

### Understand

System presents the four-part result.

### Verify

User can inspect the sources.

The design should make this flow intuitive without requiring instructions.

---

# 20. Trust & Transparency

Because SAMA-VIDHANA deals with civic and legal information, trust is an important part of the design.

The interface should communicate:

* Where information came from.
* Which information is uncertain.
* When user information is missing.
* That AI-generated guidance should not automatically be treated as a final legal determination.

Trust should be communicated through the interface itself rather than through excessive warnings.

---

# 21. Design Principle

The final design philosophy can be summarized as:

```text id="s6q2n8"
             COMPLEX SYSTEM
                  │
                  ▼
          ┌───────────────┐
          │ SAMA-VIDHANA  │
          │               │
          │ NLP           │
          │ RAG           │
          │ Mistral       │
          │ Retrieval     │
          │ Documents     │
          └───────┬───────┘
                  │
                  ▼
             SIMPLE UI
                  │
                  ▼
             CLEAR ANSWER
                  │
                  ▼
                CITIZEN
```

> **The interface should be simple enough for anyone to use, while the system behind it handles the complexity.**
