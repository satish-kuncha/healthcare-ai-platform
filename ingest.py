import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment configuration
load_dotenv()

# Extract variables with fail-safe fallbacks
API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "healthcare-platform")
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "namespace-1")
FILE_PATH = os.getenv("KNOWLEDGE_FILE_PATH")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "llama-text-embed-v2")

if not FILE_PATH or not os.path.exists(FILE_PATH):
    raise FileNotFoundError(f"Target knowledge file not found at: {FILE_PATH}")

# 1. Initialize Pinecone
pc = Pinecone(api_key=API_KEY)
index = pc.Index(INDEX_NAME)

# 2. Read the Document (Handles text files natively)
print(f"Reading target file from: {FILE_PATH}")
with open(FILE_PATH, "r", encoding="utf-8") as file:
    raw_text = file.read()

# 3. Slidng Window Chunking Function
def chunk_text(text, chunk_size=100, overlap=20):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += (chunk_size - overlap)
    return chunks

text_chunks = chunk_text(raw_text, chunk_size=100, overlap=20)
print(f"Divided document into {len(text_chunks)} chunks.")

# 4. Construct Payload
records = []
# Create unique IDs tied specifically to the file name to prevent messy cross-file overwrites
file_slug = os.path.basename(FILE_PATH).replace(".", "-")

for i, chunk in enumerate(text_chunks):
    records.append({
        "id": f"{file_slug}-chunk-{i}",
        "text": chunk
    })

print(f"Upserting to Pinecone namespace '{NAMESPACE}' via Integrated Inference...")

# 5. Push Execution
index.upsert_records(namespace=NAMESPACE, records=records)

print("✅ Environment-driven ingestion complete!")