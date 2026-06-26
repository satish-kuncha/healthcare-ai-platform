from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from models.context import PatientContext
from agents.healthcare_agent import healthcare_agent
from langgraph.checkpoint.memory import MemorySaver
# Import the real, pure API function here in the orchestrator
from tools.scheduling_tools import book_appointment

# 1. Define the Graph State
# This replaces the variables you used to manage manually in the while loop
class WorkflowState(TypedDict):
    context: PatientContext
    messages: list
    user_input: str
    approval_granted: bool | None

async def reasoning_node(state: WorkflowState):
    """This node gives the current state to PydanticAI and waits for its actions."""
    
    result = await healthcare_agent.run(
        state["user_input"],
        deps=state["context"],
        message_history=state["messages"]
    )

    return {
        "context": state["context"], 
        "messages": result.new_messages(), 
    }

async def human_approval_node(state: WorkflowState):
    """HITL Gate."""
    if state.get("approval_granted") is False:
        # Clear the staging area on rejection
        state["context"].pending_booking_day = None
        state["context"].pending_booking_time = None
        return {"user_input": "SYSTEM OVERRIDE: The manager rejected this slot. Ask the patient for another time."}
    return {}

async def execute_booking_node(state: WorkflowState):
    """The Orchestrator executes the real API after approval."""
    ctx = state["context"]
    
    # 1. Execute the pure API
    api_result = await book_appointment(ctx.patient_name, ctx.pending_booking_day, ctx.pending_booking_time)
    
    # 2. Clear the staging area
    ctx.pending_booking_day = None
    ctx.pending_booking_time = None
    
    # 3. Tell the LLM it succeeded so it can inform the user
    return {
        "context": ctx,
        "user_input": f"SYSTEM OVERRIDE: The manager approved! The database confirms booking {api_result['confirmation']}. Tell the patient."
    }


def route_after_reasoning(state: WorkflowState):
    """If the LLM staged a booking, route to Human Approval. Otherwise, END."""
    if state["context"].pending_booking_day:
        return "human_approval"
    return END

def route_after_approval(state: WorkflowState):
    """If approved, execute. If rejected, loop back to the agent to apologize."""
    if state.get("approval_granted"):
        return "execute_booking"
    return "reason"

def build_graph():
    workflow = StateGraph(WorkflowState)
    
    # 3 Distinct Responsibilities
    workflow.add_node("reason", reasoning_node)           # Brain
    workflow.add_node("human_approval", human_approval_node) # Gate
    workflow.add_node("execute_booking", execute_booking_node) # Hand
    
    workflow.add_edge(START, "reason")

    # From reasoning, either end conversation or hit the gate
    workflow.add_conditional_edges(
        "reason", route_after_reasoning, {"human_approval": "human_approval", END: END}
    )

    # From the gate, either execute or route back to the LLM
    workflow.add_conditional_edges(
        "human_approval", route_after_approval, {"execute_booking": "execute_booking", "reason": "reason"}
    )
    
    # After executing, loop back to the LLM to give the final confirmation message
    workflow.add_edge("execute_booking", "reason")

    return workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["human_approval"]
    )

healthcare_graph = build_graph()