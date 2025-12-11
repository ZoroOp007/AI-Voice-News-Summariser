from typing import List
import os
from utils import *
from typing import List
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from tenacity import (
    retry, 
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from aiolimiter import AsyncLimiter
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, timedelta


load_dotenv()


two_weeks_ago = datetime.today() - timedelta(days=14) 
two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d')


class MCPOverloadedError(Exception):
    pass


mcp_limiter = AsyncLimiter(1, 15)

model = ChatGroq(model="llama-3.3-70b-versatile")

# FIXED server_params
server_params = StdioServerParameters(
    command="npx",
    env={
        "API_TOKEN": os.getenv("BRIGHTDATA_API_TOKEN"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE") or "mcp_unlocker",
        "PRO_MODE": "true",  # REQUIRED for full tools
        "LOG_LEVEL": "debug"  # For troubleshooting
    },
    args=["-y", "@brightdata/mcp"],  # -y prevents prompts
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=15, max=60),
    retry=retry_if_exception_type(MCPOverloadedError),
    reraise=True
)
async def process_topic(agent, topic: str):
    async with mcp_limiter:
        messages = [
            {"role": "system", "content": f"""Reddit analysis expert. Use tools to:
1. Find top 2 posts about '{topic}' AFTER {two_weeks_ago_str} ONLY
2. Analyze content/sentiment
3. Summarize discussions with quotes (no usernames)"""},
            {"role": "user", "content": f"Analyze Reddit '{topic}': main points, opinions, trends, sentiment"}
        ]
        
        try:
            response = await agent.ainvoke({"messages": messages})
            return response["messages"][-1].content
        except Exception as e:
            if "Overloaded" in str(e) or "401" in str(e):
                raise MCPOverloadedError(f"MCP error: {str(e)}")
            raise

async def scrape_reddit_topics(topics: List[str]) -> dict[str, dict]:
    """Process topics with proper error isolation"""
    reddit_results = {}
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)  # Agent per session
            
            # Process sequentially with isolation
            for topic in topics:
                try:
                    summary = await process_topic(agent, topic)
                    reddit_results[topic] = {"summary": summary, "status": "success"}
                    await asyncio.sleep(5)  # Rate limit
                except Exception as e:
                    reddit_results[topic] = {"error": str(e), "status": "failed"}
                    print(f"Failed {topic}: {e}")
                    await asyncio.sleep(10)  # Backoff on error
    
    return {"reddit_analysis": reddit_results}