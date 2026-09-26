# agent_loop.py - what an agent does, in plain Python (fully self-contained)
import json

STOCK = {"amoxicillin": {"Kisumu Central": 40, "Vihiga": 8},
         "malaria_kits": {"Kisumu Central": 55, "Vihiga": 6}}

def check_stock(item: str) -> str:
    """Toy stock lookup: how many units of an item each clinic holds."""
    if item not in STOCK:
        return json.dumps({"error": f"Unknown item '{item}'. Valid: {list(STOCK)}"})
    return json.dumps({"item": item, "stock": STOCK[item]})

def clinic_count() -> str:
    """Toy directory lookup: how many clinics we serve."""
    return json.dumps({"clinics": 2})

TOOLS = {"check_stock": check_stock, "clinic_count": clinic_count}

def pick_tool(question: str, already_called: list):
    """One extra input: the tools already called this run, so the stand-in
    'thinking' step can pick the NEXT useful tool instead of repeating itself."""
    q = question.lower()
    for item in STOCK:
        if (item.replace("_", " ") in q or item in q) and "check_stock" not in already_called:
            return ("check_stock", [item])
    if "how many clinics" in q and "clinic_count" not in already_called:
        return ("clinic_count", [])
    return None

def run_agent(question: str, max_steps: int = 3) -> str:
    observations = []
    already_called = []
    ran_out = False

    for _ in range(max_steps):
        choice = pick_tool(question, already_called)         # THINK
        if choice is None:
            break                                             # nothing more to do
        tool_name, args = choice
        print(f"  calling {tool_name}({', '.join(repr(a) for a in args)})")
        observation = json.loads(TOOLS[tool_name](*args))     # ACT + OBSERVE
        observations.append(observation)
        already_called.append(tool_name)
    else:
        # the for-loop finished all max_steps without ever hitting 'break'
        if pick_tool(question, already_called) is not None:
            ran_out = True

    if ran_out:
        partial = "; ".join(json.dumps(o) for o in observations)
        return f"I ran out of steps before finishing. Partial findings: {partial}"
    if not observations:
        return "I do not have a tool that can answer that question."
    joined = "; ".join(json.dumps(o) for o in observations)
    return f"Answer based on {len(observations)} tool call(s): {joined}"

if __name__ == "__main__":
    print(run_agent("How much amoxicillin do we have, and how many clinics do we serve?"))
    print(run_agent("How much amoxicillin do we have, and how many clinics do we serve?",
                    max_steps=1))