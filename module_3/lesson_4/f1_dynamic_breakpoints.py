from typing_extensions import TypedDict
from typing import Literal
from langgraph.errors import NodeInterrupt
from langgraph.graph import START, END, StateGraph
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver


class RaceState(TypedDict):
    driver_message: str
    engineer_response: str


def check_conditions(state: RaceState) -> RaceState:
    """Checks track conditions based on driver message."""
    print("---Checking Track Conditions---")
    return {"engineer_response": f"Copy that: '{state['driver_message']}'"}


def strategy_check(state: RaceState) -> RaceState:
    """Checks strategy implications and interrupts if urgent."""
    print("---Checking Strategy Implications---")
    message_lower = state['driver_message'].lower()
    if "pit now" in message_lower or "box box" in message_lower:
        raise NodeInterrupt(f"Urgent Pit Request Detected: '{state['driver_message']}'. Requires confirmation.")

    print("---Strategy Check Passed---")
    return {"engineer_response": state['engineer_response'] + " | Strategy check OK."}


def confirm_action(state: RaceState) -> RaceState:
    """Confirms the final action with the team."""
    print("---Confirming Action with Team---")
    return {"engineer_response": state['engineer_response'] + " | Action confirmed."}


builder = StateGraph(RaceState)
builder.add_node("check_conditions", check_conditions)
builder.add_node("strategy_check", strategy_check)
builder.add_node("confirm_action", confirm_action)
builder.add_edge(START, "check_conditions")
builder.add_edge("check_conditions", "strategy_check")
builder.add_edge("strategy_check", "confirm_action")
builder.add_edge("confirm_action", END)

graph = builder.compile()