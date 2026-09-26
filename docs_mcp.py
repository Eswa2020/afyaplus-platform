# docs_mcp.py - a tiny second server, to prove one agent can plug into many
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("afyaplus-docs")

POLICIES = {
    "reorder": "Reorders under 100 units: coordinator approval. Over 100: ops manager sign-off.",
    "dispatch": "Drivers are dispatched only against a confirmed reorder with an assigned route.",
}

@mcp.tool()
def get_policy(topic: str) -> str:
    """Return the short AfyaPlus operations policy for a topic.
    Valid topics: reorder, dispatch."""
    if topic not in POLICIES:
        return json.dumps({"error": f"Unknown topic '{topic}'. Valid topics: {list(POLICIES)}"})
    return json.dumps({"topic": topic, "policy": POLICIES[topic]})

if __name__ == "__main__":
    mcp.run()