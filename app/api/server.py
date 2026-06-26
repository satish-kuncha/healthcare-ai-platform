from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import warnings
import traceback
from fastapi.middleware.cors import CORSMiddleware  # <-- ADD THIS

# Suppress LangGraph msgpack warnings
warnings.filterwarnings("ignore", message="Deserializing unregistered type")

from db.store import init_db, load_session, save_session
from workflows.graph import healthcare_graph

# 1. Define the API Application
app = FastAPI(
    title="Healthcare AI Platform",
    description="Production API for LangGraph Orchestration",
    version="1.0.0"
)

# --- ADD THIS CORS BLOCK ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your React app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------


# 2. Define Request Schemas (The expected incoming JSON structure)
class ChatRequest(BaseModel):
    session_id: str
    user_input: str

class ApprovalRequest(BaseModel):
    session_id: str
    approved: bool

# 3. Bootstrapping
@app.on_event("startup")
async def startup_event():
    print("[SYSTEM] Booting FastAPI Server and Initializing Database...")
    await init_db()

# 4. The Core Chat Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    patient_context, message_history = await load_session(request.session_id)
    config = {"configurable": {"thread_id": request.session_id}}

    # Pre-check: Is this thread currently frozen waiting for a manager?
    graph_state = await healthcare_graph.aget_state(config)
    if graph_state.next:
        raise HTTPException(
            status_code=423, 
            detail="This session is locked pending administrative approval."
        )

    try:
        current_state = {
            "context": patient_context,
            "messages": message_history,
            "user_input": request.user_input,
            "approval_granted": None
        }

        # Invoke the graph
        final_state = await healthcare_graph.ainvoke(current_state, config)
        
        # Post-check: Did this interaction trigger a new HITL breakpoint?
        graph_state = await healthcare_graph.aget_state(config)
        
        if graph_state.next:
            # Save state and return a special status code to the frontend
            await save_session(request.session_id, final_state["context"], final_state["messages"])
            return {
                "status": "pending_approval",
                "message": "Action staged. Waiting for manager approval.",
                "context": final_state["context"].model_dump()
            }

        # Normal execution finished
        patient_context = final_state["context"]
        message_history = final_state["messages"]
        assistant_response = message_history[-1].parts[0].content

        await save_session(request.session_id, patient_context, message_history)

        return {
            "status": "success",
            "response": assistant_response,
            "context": patient_context.model_dump()
        }

    except Exception as e:
        # 1. Print a massive, unmissable error block in your Python terminal
        print("\n" + "!" * 50)
        print("[CRITICAL ENDPOINT CRASH]")
        traceback.print_exc()
        print("!" * 50 + "\n")
        
        # 2. Pass the stringified error back to the frontend
        raise HTTPException(status_code=500, detail=f"Server crashed: {str(e)}")

# 5. The Admin Approval Endpoint
@app.post("/admin/approve")
async def admin_approve_endpoint(request: ApprovalRequest):
    config = {"configurable": {"thread_id": request.session_id}}
    graph_state = await healthcare_graph.aget_state(config)

    # Validate that there is actually a breakpoint to approve
    if not graph_state.next:
        raise HTTPException(status_code=400, detail="No pending actions require approval for this session.")

    try:
        # Inject the admin's decision and resume the graph
        await healthcare_graph.aupdate_state(config, {"approval_granted": request.approved})
        final_state = await healthcare_graph.ainvoke(None, config)

        # Extract the final response after the API tool fires (or rejects)
        patient_context = final_state["context"]
        message_history = final_state["messages"]
        assistant_response = message_history[-1].parts[0].content

        await save_session(request.session_id, patient_context, message_history)

        return {
            "status": "success",
            "response": assistant_response,
            "context": patient_context.model_dump()
        }
        
    except Exception as e:
        # 1. Print a massive, unmissable error block in your Python terminal
        print("\n" + "!" * 50)
        print("[CRITICAL ENDPOINT CRASH]")
        traceback.print_exc()
        print("!" * 50 + "\n")
        
        # 2. Pass the stringified error back to the frontend
        raise HTTPException(status_code=500, detail=f"Server crashed: {str(e)}")