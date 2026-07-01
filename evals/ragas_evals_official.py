import asyncio
import sys
import os
import types
from dotenv import load_dotenv


load_dotenv()

# --- 1. QUICK FIX FOR RAGAS/LANGCHAIN VERSION CLASH ---
# Dynamically register a dummy module so Ragas can load cleanly without VertexAI
try:
    import langchain_community.chat_models.vertexai
except ModuleNotFoundError:
    dummy_vertex = types.ModuleType("langchain_community.chat_models.vertexai")
    dummy_vertex.ChatVertexAI = type("ChatVertexAI", (object,), {})
    sys.modules["langchain_community.chat_models.vertexai"] = dummy_vertex

    import langchain_community.llms
    langchain_community.llms.VertexAI = type("VertexAI", (object,), {})
# ------------------------------------------------------

# Ensure the app module can be imported from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import official RAGAS 0.4.x components
from ragas import aevaluate
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision
from ragas.run_config import RunConfig

# Import wrappers to bridge Gemini to RAGAS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

# Import your application tools
from tools.insurance_tools import search_knowledge_base
from agents.healthcare_agent import healthcare_agent
from models.context import PatientContext

async def run_official_ragas():
    print("⚖️ Phase 7: Running Official RAGAS 0.4.x Evaluation...\n")

    # 2. Initialize the Evaluator LLM and Embeddings (Gemini)
    print("Initializing Gemini Judge Models...")
    judge_llm = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
    )
    judge_embeddings = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    )

    # 3. Define the Test Suite with Ground-Truth References
    test_suite = [
        {
            "question": "What happens if I arrive 20 minutes late to my appointment?",
            "reference": (
                "Patients arriving more than 15 minutes late may need to "
                "reschedule their appointment."
            )
        },
        {
            "question": "Does the Tier A insurance cover holistic acupuncture?",
            "reference":"Tier A insurance does not cover holistic acupuncture."
        }
    ]

    samples = []

    # 4. Generate the execution data from your RAG pipeline
    for i, case in enumerate(test_suite):
        question = case["question"]
        reference_answer = case["reference"]
        print(f"\nProcessing Test Case {i+1}: '{question}'")
        
        # Step A: Fetch from Pinecone (Our Retrieval Pipeline)
        raw_context = await search_knowledge_base(question)
        retrieved_contexts = [raw_context] 
        
        # Step B: Generate Answer (Our PydanticAI Agent)
        test_context = PatientContext()
        agent_result = await healthcare_agent.run(
            f"Use this context to answer the user: {raw_context}\n\nUser: {question}",
            deps=test_context
        )
        generated_answer = agent_result.output
        
        # Step C: Construct the RAGAS 0.4.x SingleTurnSample with reference
        sample = SingleTurnSample(
            user_input=question,
            retrieved_contexts=retrieved_contexts,
            response=generated_answer,
            reference=reference_answer
        )
        samples.append(sample)

    # 5. Package into an EvaluationDataset
    dataset = EvaluationDataset(samples)

    # 6. Execute the RAGAS Evaluation Framework
    print("\n🚀 Handing off to RAGAS for evaluation (this may take a moment)...")
    
    metrics_to_run = [
        Faithfulness(),
        AnswerRelevancy(),
        ContextPrecision()
    ]
    
    results = await aevaluate(
        dataset=dataset,
        metrics=metrics_to_run,
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=RunConfig(max_workers=2, timeout=120)
    )

    # 7. Output the official scorecard
    print("\n==================================================")
    print("🏆 OFFICIAL RAGAS SCORECARD (0.0 to 1.0)")
    print("==================================================")
    
    summary_scores = results.to_pandas()
    
    for index, row in summary_scores.iterrows():
        print(f"\nQuestion: {row['user_input']}")
        print(f" - Faithfulness:      {row['faithfulness']:.2f}")
        print(f" - Answer Relevancy:  {row['answer_relevancy']:.2f}")
        print(f" - Context Precision: {row['context_precision']:.2f}")
        print(f" -> Generated Answer: {row['response']}")

if __name__ == "__main__":
    # Ensure you have installed: pip install ragas langchain-google-genai pandas
    asyncio.run(run_official_ragas())
