import asyncio
import sys
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent

load_dotenv()

# Ensure the app module can be imported from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your tools to simulate the RAG flow
from tools.insurance_tools import search_knowledge_base
from agents.healthcare_agent import healthcare_agent
from models.context import PatientContext

# ---------------------------------------------------------
# 1. Define the RAGAS Scorecard Schema
# ---------------------------------------------------------
# Pydantic forces the Judge LLM to output strictly formatted grades
class RagasScorecard(BaseModel):
    faithfulness_score: int = Field(..., description="Scale 1-5: Is the generated answer entirely factually supported by the provided context? 1=Hallucinated, 5=Perfectly supported.")
    answer_relevance_score: int = Field(..., description="Scale 1-5: Does the generated answer directly and concisely address the user's question? 1=Irrelevant, 5=Highly relevant.")
    context_precision_score: int = Field(..., description="Scale 1-5: Does the retrieved context actually contain the information needed to answer the question? 1=Useless context, 5=Perfect context.")
    reasoning: str = Field(..., description="A 1-2 sentence explanation justifying the scores.")

# ---------------------------------------------------------
# 2. Initialize the Judge Agent
# ---------------------------------------------------------
ragas_judge_agent = Agent(
    "google:gemini-2.5-flash",
    output_type=RagasScorecard,
    system_prompt=(
        "You are an impartial AI judge evaluating a Retrieval-Augmented Generation (RAG) pipeline for a healthcare clinic. "
        "You will be given a User Question, the Retrieved Context from the database, and the Agent's Generated Answer. "
        "Your job is to objectively score the performance based on Faithfulness, Answer Relevance, and Context Precision."
    )
)

# ---------------------------------------------------------
# 3. The Automated Evaluation Loop
# ---------------------------------------------------------
async def run_ragas_evaluation():
    print("⚖️ Phase 7: Running RAGAS Pipeline Evaluations...\n")

    # A tiny dataset of test questions to run through the system
    test_suite = [
        "What happens if I arrive 20 minutes late to my appointment?",
        "Does the Tier A insurance cover holistic acupuncture?"
    ]

    for i, question in enumerate(test_suite):
        print(f"--- Evaluating Test Case {i+1} ---")
        print(f"Question: {question}")
        
        # Step A: Simulate the Retrieval (Pinecone)
        retrieved_context = await search_knowledge_base(question)
        
        # Step B: Simulate the Generation (Healthcare Agent)
        test_context = PatientContext()
        agent_result = await healthcare_agent.run(
            f"Use this context to answer the user: {retrieved_context}\n\nUser: {question}",
            deps=test_context
        )
        generated_answer = agent_result.output

        # Step C: The RAGAS Judge Evaluation
        judge_prompt = f"""
        Evaluate the following RAG interaction:
        
        USER QUESTION: {question}
        
        RETRIEVED CONTEXT: {retrieved_context}
        
        AGENT'S GENERATED ANSWER: {generated_answer}
        """
        
        evaluation = await ragas_judge_agent.run(judge_prompt)
        scorecard = evaluation.output
        
        # Step D: Output the Results
        print(f"Faithfulness:       {scorecard.faithfulness_score}/5")
        print(f"Answer Relevance:   {scorecard.answer_relevance_score}/5")
        print(f"Context Precision:  {scorecard.context_precision_score}/5")
        print(f"Judge's Reasoning:  {scorecard.reasoning}\n")

if __name__ == "__main__":
    asyncio.run(run_ragas_evaluation())