# Architectural Boundaries

## Philosophy

Every layer owns exactly one responsibility.

Avoid overlapping responsibilities.

If two layers own the same responsibility,
the architecture should be redesigned.

---

# UI Layer

Owns

- User interaction
- Forms
- Voice
- Display

Must Never Own

- Business rules
- AI reasoning
- Database logic

---

# FastAPI Layer

Owns

- HTTP
- Authentication
- Request lifecycle
- Dependency injection

Must Never Own

- AI reasoning
- Workflow logic

---

# LangGraph

Owns

- Workflow execution
- Branching
- Retries
- Checkpoints
- Human approvals
- State transitions

Must Never Own

- Business policies
- LLM prompts
- Domain rules

---

# PydanticAI

Owns

- Intent detection
- Entity extraction
- Tool selection
- Planning
- Explanation
- Structured outputs

Must Never Own

- Workflow execution
- Database writes
- Business rules
- Long-running process control

---

# Business Rules Layer

Owns

- Policies
- Validation
- Eligibility
- Deterministic decisions

Must Never Own

- AI prompting
- Workflow orchestration

---

# MCP Layer

Owns

- External capabilities
- Tool interfaces
- Service communication

Must Never Own

- Business decisions
- Workflow logic

---

# RAG Layer

Owns

- Retrieval
- Ranking
- Context assembly

Must Never Own

- Response generation
- Workflow execution

---

# Database

Owns

- Facts
- Persistence
- Audit data

Must Never Own

- Reasoning
- Workflow

---

# Agent Memory

Owns

- Temporary reasoning context

Must Never Own

- Long-term business data

---

# Key Principle

Agents reason.

Workflows execute.

Rules decide.

Databases remember.

MCP connects.

RAG retrieves.

Users approve.

Everything has exactly one owner.