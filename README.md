Autonomous AI Voice Receptionist & Healthcare Platform
An enterprise-grade, asynchronous AI voice receptionist and clinical operations platform. This application leverages a finite state machine orchestrator to handle patient queries, manage appointment lifecycles with Human-in-the-Loop (HITL) guardrails, and interface safely with medical data via Advanced Two-Stage RAG and the Model Context Protocol (MCP).

✨ Core Features
Voice-Enabled React Interface: Native browser speech-to-text and text-to-speech integration.

State Machine Orchestration: LangGraph checkpointer ensures session memory and pauses execution for administrative override (HITL) before high-risk actions (e.g., booking slots).

Advanced RAG Pipeline: Pinecone Serverless integration with Two-Stage Retrieval (Bi-Encoder Dense Search + Cross-Encoder Re-Ranking) for zero-hallucination policy answers.

Model Context Protocol (MCP): A self-hosted FastMCP server acts as a secure Electronic Health Records (EHR) gateway, routing logs via stderr to decouple sensitive data from the main reasoning engine.

Type-Safe AI Tools: PydanticAI rules layer ensures all LLM tool executions match precise backend schemas.

Production Observability: Full application lifecycle tracing and telemetry using Langfuse, nested automatically from top-level API traces down to tool-level generations.

🚀 Technology Stack
Backend Framework: FastAPI (Python 3.13)

Frontend UI: React (Vite, TailwindCSS)

Orchestration & Agent: PydanticAI (Google Gemini 2.5 Flash) & LangGraph

Vector Database: Pinecone Serverless

Embedding & Re-ranking: Pinecone Integrated Inference (llama-text-embed-v2 & bge-reranker-v2-m3)

Integrations Protocol: Anthropic FastMCP

Observability: Langfuse SDK

Database (State): SQLite (Local Thread Checkpointer)

Containerization: Docker & Docker Compose

🏗️ System Architecture
The architecture decouples the reasoning engine (PydanticAI) from state memory (LangGraph/SQLite) and domain data (Pinecone RAG / FastMCP), allowing the system to scale securely.

Plaintext
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
|                          [ TOOL EXECUTION ] <--------------+           |
+-----------------------------------+-----------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
+---------v---------+     +---------v---------+     +---------v---------+
|     Local DB      |     |   Pinecone Cloud  |     |  Self-Hosted MCP  |
|   (SQLite Appt.   |     |   (Vector RAG +   |     |  Server (FastMCP) |
|    Management)    |     |    Re-Ranker)     |     | via stdio routing |
+-------------------+     +-------------------+     +-------------------+
📁 Repository Structure
Plaintext
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
├── mcpserver/
│   ├── server.py                 # FastMCP secure EHR Gateway (Stdio routed via stderr)
│   └── ehr_db.json               # Mock patient record database
├── knowledge/
│   └── extended_clinic_manual.txt# Dense clinical operations corpus for RAG
├── ingest.py                     # Pinecone ingestion & chunking script
├── docker-compose.yml            # Multi-container orchestration config
├── requirements.txt              # Frozen Python backend dependencies
└── .env                          # Runtime configuration keys (git-ignored)
⚙️ Setup & Installation
1. Environment Configuration
Create a .env file in the root directory and populate your credentials:

Plaintext
# Core API Keys
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key

# Langfuse Observability
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# RAG Engine Deployments
KNOWLEDGE_FILE_PATH=knowledge/extended_clinic_manual.txt
PINECONE_INDEX_NAME=healthcare-platform
PINECONE_NAMESPACE=clinic-ops-v3
EMBEDDING_MODEL=llama-text-embed-v2
RERANK_MODEL=bge-reranker-v2-m3

# Model Context Protocol Configuration
# For Docker: /code/mcpserver/server.py
# For Local: mcpserver/server.py
EHR_SERVER_PATH=/code/mcpserver/server.py
2. Ingesting the Clinical Knowledge Base
To chunk, process, and push clinical manuals to your Pinecone cloud index using Integrated Inference, run the standalone ingestion engine locally before spinning up your endpoints:

Bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\Activate.ps1

# Install requirements and execute
pip install -r requirements.txt
python ingest.py
🏃‍♂️ Running the Platform
Option A: Running via Docker Compose (Recommended)
This option packages the environment layers cleanly. Containers use /code as their working directory root. Ensure your .env lists EHR_SERVER_PATH=/code/mcpserver/server.py.

Bash
# Build and run the local cluster
docker-compose up --build

# To stop the cluster and tear down networks
docker-compose down
Backend REST API: http://localhost:8000

Frontend Voice UI: http://localhost:5173

Option B: Running Locally (Bare-Metal Development)
If you want to run the layers directly on your host machine for active debugging, open your .env and switch your path to EHR_SERVER_PATH=mcpserver/server.py.

Bash
# 1. Start the FastAPI Orchestration Server
uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload

# 2. In a separate terminal, start the React Web Frontend
cd frontend
npm install
npm run dev
🧪 Operational Testing Playbook
Once both layers are active, open http://localhost:5173 inside your browser to execute the clinical validation tests below.

🧪 Test 1: Basic State Memory Verification
Voice / Text Prompt: "Hi, my name is Jane Doe, and my insurance policy ID is INS-491."

Expected System Behavior: The backend logs will trigger the update_patient_record tool execution. PydanticAI populates the PatientContext dependency. The agent will reply conversationally, confirming it has updated your session file.

🧪 Test 2: Advanced Two-Stage RAG Execution
Voice / Text Prompt: "What is the penalty fee if I arrive late versus cancelling late?"

Expected System Behavior: The agent detects a policy question and calls the search_knowledge_base tool. PydanticAI vectors the prompt using Pinecone Integrated Inference, fetches candidate chunks from extended_clinic_manual.txt, passes them to the bge-reranker-v2-m3 Cross-Encoder, and synthesizes an authoritative answer. Check your Langfuse dashboard to review the re-ranking scores.

🧪 Test 3: Self-Hosted MCP EHR Data Connection
Voice / Text Prompt: "My patient ID is PT-8831. Can you look up my profile and tell me what medications I am currently taking?"

Expected System Behavior: The agent invokes the fetch_ehr_medical_history tool. The FastAPI orchestrator opens a background pipe connection to the subprocess script designated by EHR_SERVER_PATH. The tool parses the local ehr-db.json database file, pipes human logs safely out via stderr, and outputs data back to the LLM via stdout. The agent responds detailing your prescriptions for Lisinopril and Metformin.

🧪 Test 4: Human-in-the-Loop (HITL) Gate Override
Voice / Text Prompt: "I need to book an open slot for an appointment on Monday at 2 PM."

Expected System Behavior: The agent stages the reservation inside the context memory using stage_appointment_booking and yields control. LangGraph intercepts the workflow execution state before reaching the database booking node, freezes the thread, and returns an HTTP status code 423 Locked. The React UI displays the Administrative Override interface. Once an administrator approves or denies the endpoint request via /admin/approve, the state machine resumes execution to close out the interaction loop.