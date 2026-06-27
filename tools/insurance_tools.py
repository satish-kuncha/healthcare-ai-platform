import os
from pinecone import Pinecone

# Initialize Pinecone connection globally so it doesn't reconnect on every message
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index("healthcare-platform")

# Replace hardcoded values inside search_knowledge_base with these dynamic calls:
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default-namespace")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "llama-text-embed-v2")
RERANK_MODEL = os.getenv("RERANK_MODEL", "bge-reranker-v2-m3")

# insurance_tools.py
from pydantic_ai import RunContext
from models.context import PatientContext




async def verify_coverage(ctx: RunContext[PatientContext]):
    """Verify insurance coverage details using the context member ID."""
    patient = ctx.deps
    if not patient.member_id:
        return {"error": "No member ID found in context to verify."}
    
    print(f"\n[TOOL RUNNING] verify_coverage for member_id: {patient.member_id}")
    return {"covered": True, "copay": 25}

async def check_eligibility(ctx: RunContext[PatientContext]):
    """Check general healthcare program eligibility for the context member ID."""
    patient = ctx.deps
    if not patient.member_id:
        return {"error": "No member ID found in context to check eligibility."}
        
    print(f"\n[TOOL RUNNING] check_eligibility for member_id: {patient.member_id}")
    return {"eligible": True}


async def search_knowledge_base_old(query: str) -> str:
    """
    Search the clinic's internal knowledge base for insurance policies, scheduling rules, and coverage details.
    Call this tool whenever a patient asks a general question about what is covered or clinic rules.
    """
    print(f"\n[TOOL CALLED] Searching Knowledge Base for: '{query}'")
    
    try:
        # 1. Convert the user's question into a vector using Pinecone's Inference API
        # We use input_type="query" to optimize the embedding for searching
        embedding_response = pc.inference.embed(
            model="llama-text-embed-v2",
            inputs=[query],
            parameters={"input_type": "query"}
        )
        
        # Extract the raw floating-point array
        query_vector = embedding_response[0].values

        # 2. Search the database for the top 2 most relevant chunks
        results = pinecone_index.query(
            namespace="namespace-1",
            vector=query_vector,
            top_k=2,
            include_metadata=True
        )

        # 3. Format the results for the LLM
        if not results.matches:
            return "No specific policy information found for that query."

        # Extract the 'text' field from the metadata of our top matches
        retrieved_chunks = [match.metadata['text'] for match in results.matches]
        
        # Combine them into a single string for the AI to read
        combined_context = "\n\n---\n\n".join(retrieved_chunks)
        print(f"[RAG SUCCESS] Retrieved {len(results.matches)} chunks of policy data.")
        
        return combined_context

    except Exception as e:
        print(f"[RAG ERROR] {str(e)}")
        return "The knowledge base is currently unavailable. Please ask a human manager."


async def search_knowledge_base(query: str) -> str:
    """
    Search the clinic's internal knowledge base for insurance policies, scheduling rules, and coverage details.
    """
    print(f"\n[TOOL CALLED] Searching Knowledge Base for: '{query}'")
    
    try:
        # STAGE 1: Fast Vector Search (The Wide Net)
        embedding_response = pc.inference.embed(
            model=EMBED_MODEL,
            inputs=[query],
            parameters={"input_type": "query"}
        )
        query_vector = embedding_response[0].values

        # Fetch 10 candidates instead of 2
        initial_results = pinecone_index.query(
            namespace=NAMESPACE,
            vector=query_vector,
            top_k=10, 
            include_metadata=True
        )

        if not initial_results.matches:
            return "No specific policy information found for that query."

        # Format candidates for the Re-Ranker
        # Pinecone's reranker expects a list of dictionaries with a 'text' key by default
        candidate_docs = [{"id": match.id, "text": match.metadata['text']} for match in initial_results.matches]

        print(f"[RAG] Fast search found {len(candidate_docs)} candidates. Re-ranking now...")

        # STAGE 2: Cross-Encoder Re-Ranking (The Precision Scalpel)
        rerank_response = pc.inference.rerank(
            model=RERANK_MODEL,
            query=query,
            documents=candidate_docs,
            top_n=2, # Narrow it down to the absolute best 2 for the LLM
            return_documents=True
        )

        # Extract the text from the top 2 re-ranked documents
        final_chunks = [doc.document["text"] for doc in rerank_response.data]
        
        combined_context = "\n\n---\n\n".join(final_chunks)
        print(f"[RAG SUCCESS] Returned top {len(final_chunks)} highly relevant chunks.")
        
        return combined_context

    except Exception as e:
        print(f"[RAG ERROR] {str(e)}")
        return "The knowledge base is currently unavailable. Please ask a human manager."