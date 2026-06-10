# agent_graph.py
import os
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"🔑 Loaded GROQ API Key: {api_key}")


async def main():
    # 1. Initialize the Groq LLM
    model = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile", temperature=0)

    # 2. Configure the Multi-Server MCP client using stdio transport
    # Note: Make sure the paths to your server scripts are accessible from your directory
    client = MultiServerMCPClient(
        {
            "math_service": {
                "transport": "stdio",
                "command": "python",
                "args": ["math_server.py"],
            },
            "weather_service": {
                "transport": "stdio",
                "command": "python",
                "args": ["weather_server.py"],
            },
        }
    )

    print("🔄 Connecting to FastMCP servers and discovering tool schemas...")
    # This automatically discovers all tools exposed by both running processes
    mcp_tools = await client.get_tools()

    # 3. Create the standard LangGraph ReAct Agent compiled with your tools
    agent_graph = create_agent(model, tools=mcp_tools)

    # --- Test Case 1: Triggering the Math Server ---
    print("\n🚀 Querying Agent for a math problem...")
    math_query = {
        "messages": [
            ("user", "What is 452 multiplied by 12, then add 1500 to the result?")
        ]
    }

    async for chunk in agent_graph.astream(math_query):
        if "agent" in chunk:
            print("🤖 Agent:", chunk["agent"]["messages"][-1].content)
        elif "tools" in chunk:
            print("🔧 Tool Output:", chunk["tools"]["messages"][-1].content)

    # --- Test Case 2: Triggering the Weather Server ---
    print("\n🚀 Querying Agent for a weather report...")
    weather_query = {
        "messages": [("user", "What is the weather like in London right now?")]
    }

    async for chunk in agent_graph.astream(weather_query):
        if "agent" in chunk:
            print("🤖 Agent:", chunk["agent"]["messages"][-1].content)
        elif "tools" in chunk:
            print("🔧 Tool Output:", chunk["tools"]["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
