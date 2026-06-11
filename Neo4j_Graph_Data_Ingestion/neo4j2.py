import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# -----------------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------------
load_dotenv("../.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# -----------------------------------------------------------
# LLM
# -----------------------------------------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0,
)

# -----------------------------------------------------------
# Neo4j Graph
# -----------------------------------------------------------
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

print("\n========== SCHEMA ==========")
print(graph.schema)
print("============================\n")

# -----------------------------------------------------------
# Cypher Prompt
# -----------------------------------------------------------
CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Cypher developer.

Schema:
{schema}

Rules:
- Generate exactly ONE Cypher query.
- Never generate multiple statements.
- Never use CALL gds.*
- Never use CALL apoc.*
- Never use CREATE.
- Never use MERGE.
- Never use DELETE.
- Never use SET.
- Only generate READ-ONLY Cypher.
- Use only labels, relationships and properties present in the schema.
- Never assume a property called name exists.
- Use COUNT {{ (n)--() }} instead of SIZE().
- Return ONLY Cypher.

Question:
{question}
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE,
)

# -----------------------------------------------------------
# GraphCypherQAChain
# -----------------------------------------------------------
cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    cypher_prompt=cypher_prompt,
    verbose=True,
    allow_dangerous_requests=True,
    return_intermediate_steps=True,
)

# -----------------------------------------------------------
# Interactive Loop
# -----------------------------------------------------------
if __name__ == "__main__":

    while True:
        user_query = input("\nAsk a Neo4j Question (or 'exit'): ")

        if user_query.lower() == "exit":
            break

        try:
            response = cypher_chain.invoke(
                {"query": user_query}
            )

            print("\n==============================")
            print("ANSWER")
            print("==============================")
            print(response["result"])

            print("\n==============================")
            print("INTERMEDIATE STEPS")
            print("==============================")

            for step in response["intermediate_steps"]:
                print(step)

        except Exception as e:
            print(f"\nERROR:\n{e}")