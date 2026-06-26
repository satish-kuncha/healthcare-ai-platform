import uuid
import asyncio
from dotenv import load_dotenv

load_dotenv()

from db.store import init_db, load_session, save_session
from workflows.graph import healthcare_graph

async def run_console():
    await init_db()

    print("Phase 7: LangGraph Orchestration Active")
    
    session_id = input("Enter a Session ID (or press Enter for a new one): ").strip()
    if not session_id:
        session_id = str(uuid.uuid4())[:8]
        print(f"Assigned new Session ID: {session_id}")

    # Load initial state from our database
    patient_context, message_history = await load_session(session_id)
    
    print(f"\n[LOADED STATE] Name: {patient_context.patient_name}, ID: {patient_context.member_id}")
    print("Type 'exit' to quit")

    while True:
        user_input = input(f"\n[{session_id}] User: ")
        if user_input.lower() == "exit":
            break

        try:
            # 1. Package the current state
            current_state = {
                "context": patient_context,
                "messages": message_history,
                "user_input": user_input
            }

            # 2. INVOKE THE GRAPH
            # The graph processes the state through its nodes and returns the final state
            final_state = await healthcare_graph.ainvoke(current_state)
            
            # 3. Extract the updated state from the graph's output
            patient_context = final_state["context"]
            message_history = final_state["messages"]
            
            # The last message in the history is the Assistant's response
            assistant_response = message_history[-1].parts[0].content
            print(f"\nAssistant: {assistant_response}")
            
            # 4. Save to Database
            await save_session(session_id, patient_context, message_history)
            
        except Exception as e:
            print(f"\n[SYSTEM ERROR]\n{e}")