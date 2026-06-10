import os

# Modernized standard packages
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv("../.env")

# Configure embeddings to match the selection choice made during ingestion step
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

print("🔍 Initializing access hook to 'behavioral_anomalies' Collection...")
behavior_store = Chroma(
    collection_name="behavioral_anomalies",
    embedding_function=embeddings,
    persist_directory="./chroma_storage",
)

# Convert database layout into standard vector retriever framework
retriever = behavior_store.as_retriever(search_kwargs={"k": 2})

# Mock query an incoming agent challenge statement
query_statement = "Account takeover patterns with extreme typing speed logs"
print(f"📡 Forwarding Query: '{query_statement}'")

retrieved_docs = retriever.invoke(query_statement)

print("\n🎯 --- RETRIEVED AGENT CONTEXT MATCHES ---")
if not retrieved_docs:
    print("❌ No matching contextual text pieces located inside database vector index.")
else:
    for idx, doc in enumerate(retrieved_docs):
        print(f"\n[Match Record #{idx+1}]")
        print(f"Source Document Reference: {doc.metadata.get('source_file')}")
        print(f"Text Content Content:\n{doc.page_content}")
print("------------------------------------------")
