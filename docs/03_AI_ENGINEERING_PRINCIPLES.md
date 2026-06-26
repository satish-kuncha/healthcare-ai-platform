# AI Engineering Principles

## 1. Simplicity Before Complexity

Prefer one agent before many agents.

---

## 2. Structured Outputs Over Free Text

Typed models are preferred.

---

## 3. Deterministic Rules Over Prompt Logic

Business rules belong in code.

---

## 4. Explicit State Over Hidden State

State must be observable.

---

## 5. Workflow Controls AI

LangGraph owns orchestration.

---

## 6. Evaluation Before Optimization

Measure first.

Optimize later.

---

## 7. Observability Is Mandatory

Every workflow must be traceable.

---

## 8. Async By Default

Prefer asynchronous architecture.

---

## 9. Production Readiness Is Incremental

Build layers gradually.

---

## 10. Enterprise Patterns Over Demos

Favor production concepts whenever practical.

---

## 11. Agents Reason. Workflows Execute.

Agents are responsible for reasoning.

Workflow engines are responsible for execution,
coordination and process control.

Do not embed business workflows inside prompts.

---

## 12. Every Layer Has One Owner

Each architectural concern must have exactly one owner.

Avoid duplicated responsibilities across layers.

When responsibilities overlap,
refactor the architecture instead of adding exceptions.

---

## 13. Capabilities Are Separate From Decisions

External systems expose capabilities.

Business decisions remain inside the application.

Never delegate business policy to external tools.

---

## 14. Prefer the Simplest Architecture That Solves the Problem

Small, self-contained reasoning tasks may be implemented
entirely within a PydanticAI agent.

Introduce LangGraph workflows only when business
processes require branching, checkpoints,
human approval, retries or long-running state.

Do not introduce orchestration before it provides
clear architectural value.