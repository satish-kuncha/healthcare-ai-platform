import asyncio
import sys
import os

# Ensure the app module can be imported from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.context import PatientContext
from agents.unified_agent import healthcare_agent

async def run_evaluation():
    print("Phase 6: Running Deterministic Workflow Evaluations...\n")
    
    # ---------------------------------------------------------
    # TEST 1: Tool Extraction Accuracy
    # ---------------------------------------------------------
    print("Running Test 1: Context Extraction...")
    test_context = PatientContext()
    history = []
    
    input_text = "Hi, my name is Alex and my member ID is INS-12345."
    
    await healthcare_agent.run(
        input_text,
        deps=test_context,
        message_history=history
    )
    
    # Assert the LLM mapped the unstructured text into our Pydantic state correctly
    assert test_context.patient_name == "Alex", f"Failed: Expected 'Alex', got {test_context.patient_name}"
    assert test_context.member_id == "INS-12345", f"Failed: Expected 'INS-12345', got {test_context.member_id}"
    print("✅ Test 1 Passed: The agent successfully called the state tool and mapped the variables.")

    # ---------------------------------------------------------
    # TEST 2: Business Rule Guardrails
    # ---------------------------------------------------------
    print("\nRunning Test 2: Business Rule Interception...")
    
    input_text = "My birthday is 2045-10-10."
    
    await healthcare_agent.run(
        input_text,
        deps=test_context,
        message_history=history
    )
    
    # Assert that the Pydantic field_validator blocked the future date from hitting the state
    assert test_context.dob is None, f"Failed: The future DOB was accepted into state: {test_context.dob}"
    print("✅ Test 2 Passed: Pydantic rules successfully intercepted and blocked the bad data.")
    
    print("\n🎉 All regression evaluations passed successfully. System is stable.")

if __name__ == "__main__":
    asyncio.run(run_evaluation())