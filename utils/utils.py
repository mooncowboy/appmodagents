import os

def get_instructions(name):
    """
    Returns the instructions for the specified agent.
    """
    # Locate the instructions file for the agent
    instructions_file = f"instructions/{name}.hbs"
    if not os.path.exists(instructions_file):
        return "No instructions found for this agent."

    with open(instructions_file, "r") as f:
        return f.read()