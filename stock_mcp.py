# stock_mcp.py - the logistics server, stage 1: one real tool
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("afyaplus-logistics")

with open("clinics.json") as f:
    CLINICS = json.load(f)["clinics"]

VALID_ITEMS = ["amoxicillin", "ors_sachets", "malaria_kits"]

@mcp.tool()
def check_stock(item: str) -> str:
    """Check how many units of a medical item each clinic holds.
    Valid items: amoxicillin, ors_sachets, malaria_kits."""
    if item not in VALID_ITEMS:
        return json.dumps({"error": f"Unknown item '{item}'. Valid items: {VALID_ITEMS}"})
    rows = [
        {"clinic": c["name"], "county": c["county"], "units": c["stock"][item],
         "reorder_needed": c["stock"][item] < 10}
        for c in CLINICS
    ]
    return json.dumps({"item": item, "stock": rows})

if __name__ == "__main__":
    mcp.run()