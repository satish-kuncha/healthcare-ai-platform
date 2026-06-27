# Autonomous AI Voice Receptionist & Healthcare Platform

An enterprise-grade, asynchronous AI voice receptionist and clinical operations platform. This application leverages a finite state machine orchestrator to handle patient queries, manage appointment lifecycles with Human-in-the-Loop (HITL) guardrails, and interface safely with medical data via Advanced RAG and the Model Context Protocol (MCP).

## ✨ Core Features
* **Voice-Enabled React Interface:** Native browser speech-to-text and text-to-speech integration.
* **State Machine Orchestration:** LangGraph checkpointer ensures session memory and pauses execution for administrative override (HITL) before high-risk actions (e.g., booking slots).
* **Advanced RAG Pipeline:** Pinecone Serverless integration with Two-Stage Retrieval (Bi-Encoder Dense Search + Cross-Encoder Re-Ranking) for zero-hallucination policy answers.
* **Model Context Protocol (MCP):** A self-hosted FastMCP server acts as a secure Electronic Health Records (EHR) gateway, decoupling sensitive data from the main reasoning engine.
* **Type-Safe AI Tools:** PydanticAI rules layer ensures all LLM tool executions match precise backend schemas.

---

## 🚀 Technology Stack

* **Backend Framework:** FastAPI (Python 3.13)
* **Frontend UI:** React (Vite, TailwindCSS)
* **Orchestration & Agent:** PydanticAI (Google Gemini 2.5 Flash-Lite) & LangGraph
* **Vector Database:** Pinecone Serverless
* **Embedding & Re-ranking:** Pinecone Integrated Inference (`llama-text-embed-v2` & `bge-reranker-v2-m3`)
* **Integrations Protocol:** Anthropic FastMCP 
* **Database (State):** SQLite (Local Thread Checkpointer)
* **Containerization:** Docker & Docker Compose

---

## 🏗️ System Architecture

The architecture decouples the reasoning engine (PydanticAI) from state memory (LangGraph/SQLite) and domain data (Pinecone RAG / FastMCP), allowing the system to scale securely.

```text
+-----------------------------------------------------------------------+
|                             USER BROWSER                              |
|                                                                       |
|       [ React Web UI ] <-----------> [ Web Speech API (Voice) ]       |
+---------------------------+-------------------------------------------+
                            | 
                            | HTTP POST /chat (JSON)
                            v
+-----------------------------------------------------------------------+
|                         DOCKER: BACKEND APP                           |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  |                       FastAPI (Port 8000)                       |  |
|  +--------------------------------+--------------------------------+  |
|                                   |                                   |
|  +--------------------------------v--------------------------------+  |
|  |                     LangGraph Orchestrator                      |  |
|  |       (Manages State, HITL Breakpoints, Thread Memory)          |  |
|  +--------+-----------------------+-----------------------+--------+  |
|           |                       |                       |           |
|  +--------v-------+               |               +-------v-------+   |
|  |   SQLite DB    |               |               |  PydanticAI   |   |
|  | (Checkpointer) |               |               | (Gemini Flash)|   |
|  +----------------+               |               +-------+-------+   |
|                                   v                       |           |
|                         [ TOOL EXECUTION ] <--------------+           |
+-----------------------------------+-----------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
+---------v---------+     +---------v---------+     +---------v---------+
|     Local DB      |     |  Pinecone Cloud   |     | Self-Hosted MCP   |
|   (SQLite Appt.   |     |  (Vector RAG +    |     | Server (FastMCP)  |
|    Management)    |     |   Re-Ranker)      |     | via stdio routing |
+-------------------+     +-------------------+     +-------------------+


---------------------------------------------------------------------------------------------

├── app/
│   ├── api/
│   │   └── server.py             # FastAPI routing and HITL HTTP endpoints
│   ├── agents/
│   │   └── healthcare_agent.py   # PydanticAI Agent definition & Tool bindings
│   ├── workflows/
│   │   └── graph.py              # LangGraph state machine layout
│   └── db/
│       └── store.py              # SQLite checkpointer & memory management
├── frontend/                     # React Single Page App (Voice UI)
├── mcp_server/
│   ├── server.py                 # FastMCP secure EHR Gateway
│   └── ehr_db.json               # Mock patient record database
├── knowledge/
│   └── extended_clinic_manual.txt# Dense clinical operations corpus for RAG
├── ingest.py                     # Pinecone ingestion & chunking script
├── docker-compose.yml            # Multi-container orchestration config
├── requirements.txt              # Frozen Python dependencies
└── .env                          # Runtime configuration keys (git-ignored)