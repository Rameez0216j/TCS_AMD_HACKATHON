import os
from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../.env")  # Adjust the path as needed to locate your .env file

# -----------------------------------------------------------
# 1. Configuration & Initializations
# -----------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize the Groq LLM (Llama 3.1 or 3.3 models excel at tool calling)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0,  # Keeping temperature at 0 ensures stable Cypher generation
)

# Connect to the Neo4j Graph Database
# This automatically fetches your database schema behind the scenes
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)


CYPHER_GENERATION_TEMPLATE = """
You are a Neo4j Cypher expert.

IMPORTANT:
- Neo4j version is 5.x
- Never use SIZE((n)--())
- Never use SIZE((n)-[]->())
- Use COUNT {{ (n)--() }} instead.

Schema:
{schema}

Question:
{question}
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE,
)

# -----------------------------------------------------------
# 2. Build the Cypher Generation Chain
# -----------------------------------------------------------
# The allow_dangerous_requests=True flag is required by LangChain
# to explicitly authorize the code to run LLM-generated DB queries.
# cypher_chain = GraphCypherQAChain.from_llm(
#    llm=llm, graph=graph, verbose=True, allow_dangerous_requests=True
# )

cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    cypher_prompt=cypher_prompt,
    verbose=True,
    allow_dangerous_requests=True,
)


# -----------------------------------------------------------
# 3. Wrap the Chain into a Native Agent Tool
# -----------------------------------------------------------
@tool
def query_graph_database(question: str) -> str:
    """
    Useful for answering questions about connected data, tracking paths,
    identifying relationships, or looking up structural nodes within the database.
    Input should be a standalone natural language question.
    """
    response = cypher_chain.invoke({"query": question})
    return response.get("result", "No relevant data found in the graph database.")


# Add it to the agent's toolbelt
tools = [query_graph_database]

# -----------------------------------------------------------
# 4. Create the Tool-Calling AI Agent
# -----------------------------------------------------------
# Define the agent's system instructions and conversation layout
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert AI assistant. Answer user questions accurately. "
            "Whenever a question requires analyzing structured connections, patterns, "
            "or specific entities, always leverage the `query_graph_database` tool.",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create the agent using modern tool calling (highly optimized on Groq)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# -----------------------------------------------------------
# 5. Run a Sample Query
# -----------------------------------------------------------
if __name__ == "__main__":
    # Replace this query with one relevant to your actual database schema!
    # user_query = "Who are the top 3 most influential nodes in the graph based on their connections?"
    user_query = "Who are the top 3 most influential nodes in the graph based on their connections? Give the node names as well"

    print(f"User Question: {user_query}\n")
    response = agent_executor.invoke({"input": user_query})
    print("\nFinal Agent Answer:")
    print(response["output"])


# NEED TO TUNE LLM FOR CYPHER QUERIES
