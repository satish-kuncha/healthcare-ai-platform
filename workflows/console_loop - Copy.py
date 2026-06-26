import uuid
from dotenv import load_dotenv


# Load environment variables FIRST
load_dotenv()


from models.context import PatientContext
from agents.unified_agent import healthcare_agent
from db.store import init_db, load_session, save_session


from langfuse import observe




# The @observe decorator wraps this function in a Langfuse Trace
@observe(as_type="generation")
async def execute_agent_turn(session_id: str, user_input: str, patient_context, message_history):
    """Encapsulate the agent execution so Langfuse can track inputs and outputs natively."""
    result = await healthcare_agent.run(
        user_input,
        deps=patient_context,
        message_history=message_history
    )
    return result

async def run_console():

    # 1. Ensure DB exists
    await init_db()

    print("Phase 3: Persistent Sessions (Multi-Tenant Mode)")
    print("Phase 5: Observable Sessions (Langfuse Tracing Active)")
    
    # 2. Simulate User Authentication / Session Management
    session_id = input("Enter a Session ID (or press Enter for a new one): ").strip()
    if not session_id:
        session_id = str(uuid.uuid4())[:8]
        print(f"Assigned new Session ID: {session_id}")

    # 1. Initialize Business State
    # 3. Load State from DB
    patient_context, message_history = await load_session(session_id)
    print(f"\n[LOADED STATE] Name: {patient_context.patient_name}, ID: {patient_context.member_id}")
    

    print("Phase 1: Unified Healthcare Assistant (Harness Mode)")
    print("Type 'exit' to quit")

    while True:
        user_input = input("\nUser: ")

        if user_input.lower() == "exit":
            break

        try:
            # 3. Execute the Agent inside the Harness
            # Call our new wrapped function
            result = await execute_agent_turn(
                session_id=session_id,
                user_input=user_input, 
                patient_context=patient_context, 
                message_history=message_history
            )

            # 4. Save Conversation State for the next loop
            message_history = result.new_messages()

            # 5. Display the Agent's text response
            print(f"\nAssistant: {result.output}")

            # 6. Save Updated State to DB
            await save_session(session_id, patient_context, message_history)

            # 6. Observability: Print the live Business State
            print("\n" + "=" * 40)
            print("[STATE SAVED TO DB]")
            print(patient_context.model_dump())
            print("=" * 40)

        except Exception as e:
            print(f"\n[SYSTEM ERROR]\n{e}")