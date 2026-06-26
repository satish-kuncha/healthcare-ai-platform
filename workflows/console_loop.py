# app/workflows/console_loop.py
from typing import TypedDict
import uuid
from db.store import init_db, load_session, save_session
from workflows.graph import healthcare_graph


async def run_console():
    await init_db()

    print("Phase 10: Human-in-the-Loop Orchestration Active")
    
    session_id = input("Enter a Patient Session ID (or press Enter for a new one): ").strip()
    if not session_id:
        session_id = str(uuid.uuid4())[:8]
        print(f"Assigned new Session ID: {session_id}")

    patient_context, message_history = await load_session(session_id)
    
    # LangGraph threads require a configuration dict passing the unique thread identifier
    config = {"configurable": {"thread_id": session_id}}
    
    print(f"\n[LOADED STATE] Patient: {patient_context.patient_name or 'Unknown'}")
    print("Type 'exit' to quit")

    while True:
        # Check if the graph is currently paused at a breakpoint
        graph_state = await healthcare_graph.aget_state(config)
        
        if graph_state.next:
            print(f"\n🛑 [HITL BREAKPOINT] Transaction paused before node: {graph_state.next[0]}")
            print(f"Pending action verification for patient: {patient_context.patient_name}")
            
            choice = input("Admin Action Required - Approve slot booking? (yes/no): ").strip().lower()
            
            if choice == "yes":
                # PRODUCTION FIX 2: Remove as_node="reason". 
                # We want to patch the frozen state directly waiting at the 'human_approval' gate.
                await healthcare_graph.aupdate_state(
                    config, 
                    {"approval_granted": True}
                )
                print("✅ Approval injected. Resuming execution thread...")
                final_state = await healthcare_graph.ainvoke(None, config)
            else:
                await healthcare_graph.aupdate_state(
                    config, 
                    {"approval_granted": False}
                )
                print("❌ Rejection injected. Routing back to remediation loop...")
                final_state = await healthcare_graph.ainvoke(None, config)
                
            patient_context = final_state["context"]
            message_history = final_state["messages"]
            assistant_response = message_history[-1].parts[0].content
            print(f"\nAssistant: {assistant_response}")
            await save_session(session_id, patient_context, message_history)
            continue

        # Standard non-interrupted entry loop
        user_input = input(f"\n[{session_id}] User: ")
        if user_input.lower() == "exit":
            break

        try:
            current_state = {
                "context": patient_context,
                "messages": message_history,
                "user_input": user_input,
                "approval_granted": None
            }

            # Run graph with configuration settings to attach thread persistence
            final_state = await healthcare_graph.ainvoke(current_state, config)
            
            patient_context = final_state["context"]
            message_history = final_state["messages"]
            
            assistant_response = message_history[-1].parts[0].content
            print(f"\nAssistant: {assistant_response}")
            
            await save_session(session_id, patient_context, message_history)
            
        except Exception as e:
            print(f"\n[SYSTEM ERROR]\n{e}")