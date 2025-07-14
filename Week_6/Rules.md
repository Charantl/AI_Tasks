## Backend
## General Principles

- Prioritize **clarity**, **readability**, and **minimal disruption** to existing code and workflows.
- Use the documentation in `@/docs` and its subdirectories as the **source of truth** for product behavior, architecture, data models, and user flows.
- **When in doubt, ask**—never assume requirements or intent.
- Adhere to best practices for **Python**, **FastAPI**, **Pydantic**, and established **project conventions** in both code and documentation.

---

## Step 1: Requirement Understanding & Clarification

### 1. Knowledge Gathering
- Thoroughly review relevant files and notes in `@/docs` and its subdirectories.
- Extract product requirements, API behaviors, data schemas, models, and service responsibilities.

### 2. User Query Analysis
- Interpret the user's prompt as a **product owner** would—understand whether it's a new feature, API refactor, enhancement, or fix.
- If anything is unclear, ambiguous, or incomplete, **ask specific clarifying questions**.
- Avoid assumptions about business logic, request parameters, data flows, or validation rules.

### 3. Confirmation
- Summarize your understanding of the user’s request clearly.
- Wait for **explicit user approval** before continuing.

---

## Step 2: Tasklist Creation & User Approval

### 1. Tasklist Preparation
- Break down the confirmed requirements into a structured, actionable checklist.
- Each task must:
  - Follow Pythonic design and FastAPI best practices.
  - Call out any **breaking changes**, side effects, or **workflow impacts**.
  - Consider **backward compatibility**, security, and validation risks.
  - Include implementation notes for testing or edge cases, if needed.

### 2. User Approval
- Present the tasklist to the user.
- Wait for explicit **user sign-off** before starting any implementation work.

---

## Step 3: Implementation, Tracking, and Documentation

### 1. Implementation
- Act as an expert **Python FastAPI developer**:
  - Use `@/docs` to guide your logic and modeling choices.
  - For each task:
    - **Done** — Fully implemented and tested.
    - **Partially Completed** — Needs follow-up (e.g., external dependency).
    - **Skipped** — Cannot proceed (explain why).
  - If unsure about data contracts, external API behavior, or domain logic, ask the user.

### 2. Knowledge Base Update
- Update related files in `@/docs`:
  - API specs
  - Request/response schemas
  - Authentication/authorization flows
  - Domain models or service responsibilities
- Ensure your updates are **clear**, **complete**, and follow existing formatting and language style.

---

## Additional Guidelines

- **Testing**  
  Write appropriate **unit**, **integration**, and **FastAPI test client**-based tests for all changes.

- **Code Quality**  
  - Follow **PEP8** and use tools like **Black**, **isort**, and **mypy** (if type hints are enforced).
  - Use **Pydantic** for input validation.
  - Leverage dependency injection and modular design for maintainability.

- **Communication**  
  Always keep responses **concise**, **professional**, and **context-aware**.

- **Backward Compatibility**  
  Favor **non-breaking changes** unless explicitly cleared by the user.

- **Logging & Error Handling**  
  Ensure graceful exception handling and logging using project-approved libraries (e.g., `structlog`, `loguru`, etc.)

---

**Note**: All prompts related to feature development, API refactor, bug fixing, or internal improvements in the Python Spotify API must follow these guidelines.
