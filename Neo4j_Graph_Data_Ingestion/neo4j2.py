import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

# FIX: Use standard, updated LangChain import paths
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv("../.env")

# 1. Configuration & Initializations
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
# Best practice: Explicitly define your database target (defaults to "neo4j")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


print("=== DEBUG: ENVIRONMENT VARIABLES ===")
print(f"GROQ_API_KEY: {GROQ_API_KEY}")
print(f"NEO4J_URI: {NEO4J_URI}")
print(f"NEO4J_USERNAME: {NEO4J_USERNAME}")
print(f"NEO4J_PASSWORD: {NEO4J_PASSWORD}")  # Avoid printing sensitive info in real applications    )
print(f"NEO4J_DATABASE: {NEO4J_DATABASE}")
print("=====================================\n")

# Initialize Groq Chat Model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0,  # Strict compliance for deterministic Cypher generation
)

# Connect to the Neo4j Graph Database
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
)

# Deepening: Force a schema refresh and print it to verify data presence right away
graph.refresh_schema()
print("\n=== DEBUG: VERIFYING DATABASE SCHEMA ===")
if graph.schema:
    print(graph.schema)
else:
    print(
        "WARNING: Graph schema is empty! Check database connection, data presence, or user permissions."
    )
print("========================================\n")


# FIX: Convert the legacy string PromptTemplate into a ChatPromptTemplate
# This ensures ChatGroq cleanly separates instruction routing from database inputs.
cypher_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a Neo4j Cypher expert tasked with generating clean, efficient Cypher queries.\n\n"
                "IMPORTANT RULES:\n"
                "- Neo4j version is 5.x\n"
                "- Never use SIZE((n)--())\n"
                "- Never use SIZE((n)-[]->())\n"
                "- Use COUNT {{ (n)--() }} or COUNT {{ (n)-[]->() }} instead.\n\n"
                "Database Schema:\n"
                "{schema}"
            ),
        ),
        ("human", "Generate a Cypher query to answer this question: {question}"),
    ]
)

# 2. Build the Cypher Generation Chain
cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    cypher_prompt=cypher_prompt,
    verbose=True,
    allow_dangerous_requests=True,
)


# 3. Deepened Native Agent Tool with Self-Correction Capabilities
@tool
def query_graph_database(question: str) -> str:
    """
    Useful for answering questions about connected data, tracking paths,
    identifying relationships, or looking up structural nodes within the database.
    Input should be a standalone natural language question.
    """
    try:
        # GraphCypherQAChain expects "query" as its input key
        response = cypher_chain.invoke({"query": question})
        return response.get("result", "No relevant data found in the graph database.")

    except Exception as e:
        # CRITICAL DEPTH ADDITION: Instead of crashing the script, passing the
        # database/syntax error back to the Agent allows it to self-correct and retry.
        return (
            f"Error executing graph query: {str(e)}. "
            f"Please adjust your natural language query or fix the Cypher generation rules to avoid this error."
        )


# Add it to the tool list
tools = [query_graph_database]


# 4. Create the Tool-Calling AI Agent
agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert AI assistant. Answer user questions accurately.\n"
            "Whenever a question requires analyzing structured connections, patterns, "
            "or specific graph entities, always leverage the `query_graph_database` tool.\n"
            "If the tool returns an error execution message, read the error carefully, "
            "reformulate your query logic, and try again.",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create and execute agent
agent = create_tool_calling_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# 5. Run a Sample Query
if __name__ == "__main__":
    user_query = "Who are the top 3 most influential nodes in the graph based on their connections? Give the node names as well."

    print(f"User Question: {user_query}\n")
    response = agent_executor.invoke({"input": user_query})
    print("\nFinal Agent Answer:")
    print(response["output"])
