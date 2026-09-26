# agent_langchain.py - the same loop, run by a real LLM through LangChain
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

load_dotenv()

async def build_agent():
    client = MultiServerMCPClient({
        "logistics": {
            "command": "python",
            "args": ["logistics_mcp.py"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return create_react_agent(model, tools)

async def main():
    agent = await build_agent()
    result = await agent.ainvoke(
        {"messages": [("user", "Which clinics need an amoxicillin reorder, and what "
                               "route should the driver take from Kisumu Central?")]},
        {"recursion_limit": 8},
    )
    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())