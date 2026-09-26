# route_demo.py - the routing idea as a plain script, before it becomes a tool
import json
import math

with open("clinics.json") as f:
    CLINICS = json.load(f)["clinics"]

def distance_km(a: dict, b: dict) -> float:
    """Rough distance between two clinics in kilometres."""
    dx = (a["lon"] - b["lon"]) * 111.32 * math.cos(math.radians((a["lat"] + b["lat"]) / 2))
    dy = (a["lat"] - b["lat"]) * 110.57
    return round(math.sqrt(dx * dx + dy * dy), 1)

start = CLINICS[0]                                     # Kisumu Central
route = [start]
remaining = [c for c in CLINICS if c is not start]
total = 0.0
while remaining:
    here = route[-1]
    nearest = min(remaining, key=lambda c: distance_km(here, c))
    leg = distance_km(here, nearest)
    print(f"{here['name']}  ->  {nearest['name']}  ({leg} km)")
    total += leg
    route.append(nearest)
    remaining.remove(nearest)

print(f"Total: {round(total, 1)} km by the nearest-neighbour rule")