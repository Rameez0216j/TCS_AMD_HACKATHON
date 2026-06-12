import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    FewShotPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env file
load_dotenv("../.env")

# -----------------------------------------------------------
# 1. Configuration & Initializations
# -----------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize Groq LLM (optimized for tool-calling & reasoning)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0,  # 0 ensures deterministic Cypher generation and analytical stability
)

# Connect to the Neo4j Graph Database
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

# -----------------------------------------------------------
# 2. Few-Shot Cypher Generation Strategy (FIXED BRACES)
# -----------------------------------------------------------
few_shot_examples = [
    {
        "question": "Identify the customer who did the most transactions.",
        "cypher": "MATCH (c:Customer)-[:MADE_TRANSACTION]->(t:Transaction) RETURN c.customer_id AS customer_id, c.customer_name AS customer_name, count(t) AS transaction_count ORDER BY transaction_count DESC LIMIT 1",
    },
    {
        "question": "Find high-risk customers who have made international transactions over 10000.",
        "cypher": "MATCH (c:Customer)-[:MADE_TRANSACTION]->(t:Transaction) WHERE c.customer_risk_rating = 'HIGH' AND t.transaction_amount > 10000 AND t.is_international = true RETURN c.customer_id AS customer_id, t.transaction_id AS transaction_id, t.transaction_amount AS amount, t.origin_country AS origin, t.destination_country AS destination",
    },
    {
        "question": "Check if any customer has sent money to a beneficiary matched with a Sanction Entity.",
        "cypher": "MATCH (c:Customer)-[:MADE_TRANSACTION]->(t:Transaction)-[:TO_BENEFICIARY]->(b:Beneficiary)-[:SANCTION_MATCH]->(s:SanctionEntity) RETURN c.customer_id AS customer_id, c.customer_name AS customer_name, b.receiver_name AS beneficiary_name, s.entity_name AS sanction_entity, s.sanction_category AS reason",
    },
    {
        "question": "Identify devices that are being shared by more than one customer account.",
        "cypher": "MATCH (c:Customer)-[:HAS_DEVICE]->(d:Device) WITH d, count(c) AS customer_count WHERE customer_count > 1 MATCH (c2:Customer)-[:HAS_DEVICE]->(d) RETURN d.device_id AS device_id, d.device_type AS device_type, collect(distinct c2.customer_id) AS shared_by_customers, customer_count",
    },
    {
        "question": "Find transactions processed at a merchant with a high fraud history count.",
        "cypher": "MATCH (t:Transaction)-[:AT_MERCHANT]->(m:Merchant) WHERE m.fraud_transaction_count > 5 RETURN t.transaction_id AS transaction_id, m.merchant_name AS merchant_name, m.merchant_risk_rating AS merchant_risk, t.transaction_amount AS amount",
    },
    {
        "question": "Get the structural profile and total connection count for a specific customer ID C1001.",
        "cypher": "MATCH (c:Customer {{customer_id: 'C1001'}}) RETURN c.customer_name AS name, c.customer_risk_rating AS risk, count{{(c)--()}} AS total_graph_connections",
    },
    {
        "question": "Look for transactions where account takeover is suspected and flag high risk scores.",
        "cypher": "MATCH (c:Customer)-[:MADE_TRANSACTION]->(t:Transaction) WHERE t.account_takeover_suspected = true OR t.overall_risk_score > 0.8 RETURN c.customer_id AS customer_id, t.transaction_id AS transaction_id, t.overall_risk_score AS risk_score, t.recommended_action AS action",
    },
]

example_formatter_template = """
Question: {question}
Cypher Query: {cypher}
"""
example_prompt = PromptTemplate(
    input_variables=["question", "cypher"],
    template=example_formatter_template,
)

prefix = """You are a Neo4j Cypher expert. Given an input question, your job is to write a valid, read-only Neo4j 5.x Cypher query.

Schema:
{schema}

Rules:
- Generate exactly ONE Cypher query statement.
- Never use CREATE, MERGE, DELETE, SET, or CALL (apoc/gds).
- Return ONLY the executable Cypher query string. Do NOT wrap it in backticks, markdown, or add conversational filler.
- Always prefer modern element-count syntax: Use `COUNT {{ (n)--() }}` instead of `SIZE((n)--())`.

Here are examples of correct conversions:"""

suffix = """
Question: {question}
Cypher Query:"""

cypher_prompt = FewShotPromptTemplate(
    examples=few_shot_examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["schema", "question"],
)

# Robust Generation Chain using LCEL (LangChain Expression Language)
# This generates a raw string instead of a volatile internal Chain object
cypher_generation_chain = cypher_prompt | llm | StrOutputParser()


# -----------------------------------------------------------
# 3. Wrap Pure Query Execution into an Agent Tool
# -----------------------------------------------------------
@tool
def query_graph_database(question: str) -> str:
    """
    Executes a read-only natural language query against the graph database.
    Use this to look up specific entities, trace paths, inspect transaction details,
    count relationships, or fetch sequential steps for an ongoing investigation.
    Input must be a highly specific standalone question.
    """
    # Defensive programming: prevent rapid hitting of Groq rate-limits
    time.sleep(0.5)

    try:
        # 1. Fetch the actual database schema dynamically
        current_schema = graph.schema

        # 2. Ask the LLM to generate just the Cypher statement
        generated_cypher = cypher_generation_chain.invoke(
            {"schema": current_schema, "question": question}
        )

        # Clean up any potential markdown code blocks the LLM might have returned
        clean_cypher = (
            generated_cypher.replace("```cypher", "").replace("```", "").strip()
        )

        # Print for visible tracking in terminal debugging
        print(f"\n[Generated Cypher]: {clean_cypher}")

        # 3. Directly hit the Neo4j database using the raw client driver
        db_result = graph.query(clean_cypher)

        if not db_result:
            return "Investigation Note: No data found in the database for this specific query configuration."

        return str(db_result)

    except Exception as e:
        return f"Investigation Note: Query failed to execute. Error: {str(e)}. Try refining target properties."


tools = [query_graph_database]

# -----------------------------------------------------------
# 4. Build an Investigative Agent (Multi-Step Logic)
# -----------------------------------------------------------
investigator_system_prompt = (
    "You are an expert forensic data analyst and investigator. "
    "Your objective is to deep-dive into graph and transaction data to uncover truths, anomalies, or complete answers.\n\n"
    "CRITICAL WORKING METHODOLOGY:\n"
    "1. Do not guess. Always gather facts via `query_graph_database`.\n"
    "2. Be methodical. If a user asks a complex question (e.g., tracing paths or investigating high-influence nodes), "
    "break it down into step-by-step tool queries.\n"
    "3. ALWAYS examine the output of your previous tool calls before formulating your next steps. "
    "If Tool Call 1 reveals an interesting entity ID, use Tool Call 2 to investigate that specific ID deeper.\n"
    "4. Keep calling your tools until you have completely mapped out the solution and have no lingering blind spots.\n"
    "5. Synthesize all your findings into a comprehensive final summary for the user."
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", investigator_system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create the Agent and AgentExecutor
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=6,  # Safe loop limit for nested checks
    early_stopping_method="force",  # Fixed the classic LangChain compatibility issue
)

# -----------------------------------------------------------
# 5. Run Deep Investigation Query
# -----------------------------------------------------------
if __name__ == "__main__":
    user_query = "Identify the customer who did most transactions"

    print(f"User Question: {user_query}\n")
    response = agent_executor.invoke({"input": user_query})
    print("\nFinal Agent Answer:")
    print(response["output"])
