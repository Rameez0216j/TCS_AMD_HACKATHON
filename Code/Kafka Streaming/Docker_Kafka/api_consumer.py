agent = create_tool_calling_agent(llm_with_tools, network_tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=network_tools,
    verbose=True,
    max_iterations=5,  # Safe loop limit for nested investigations [make it 5 in prod]
    early_stopping_method="force",  # Ensures stability within your state graph runtime
)