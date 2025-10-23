from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode

def check_tyre_wear(lap_number: int) -> str:
    """Checks the estimated tyre wear based on the current lap number."""
    if lap_number < 15:
        return f"Lap {lap_number}: Tyre wear is low. Estimated 85% life remaining."
    elif lap_number < 30:
        return f"Lap {lap_number}: Tyre wear is medium. Estimated 50% life remaining."
    else:
        return f"Lap {lap_number}: Tyre wear is high. Estimated 20% life remaining. Consider pitting."

def get_weather_forecast(sector: int) -> str:
    """Gets the weather forecast for a specific sector of the track."""
    if sector == 1:
        return f"Sector {sector}: Forecast is clear, track temperature stable."
    elif sector == 2:
        return f"Sector {sector}: Slight chance of light drizzle in the next 10 laps."
    else:
        return f"Sector {sector}: Track remains dry for now."

def suggest_pit_strategy(current_lap: int, laps_remaining: int) -> str:
    """Suggests a pit stop strategy based on current lap and laps remaining."""
    optimal_pit_window_start = 20
    optimal_pit_window_end = 35
    if optimal_pit_window_start <= current_lap <= optimal_pit_window_end:
        return f"Lap {current_lap}/{laps_remaining} laps remaining: Currently within the optimal pit window. Evaluate traffic."
    elif current_lap < optimal_pit_window_start:
        return f"Lap {current_lap}/{laps_remaining} laps remaining: Too early for optimal one-stop. Hold position."
    else:
        return f"Lap {current_lap}/{laps_remaining} laps remaining: Past optimal window. Consider Plan B if tyres degrade rapidly."

tools = [check_tyre_wear, get_weather_forecast, suggest_pit_strategy]

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

sys_msg = SystemMessage(content="You are a helpful F1 race engineer providing concise updates and strategy advice to the driver based on available tools.")

def race_engineer_assistant(state: MessagesState):
   """Invokes the LLM with the current message state and system prompt."""
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

builder = StateGraph(MessagesState)

builder.add_node("assistant", race_engineer_assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

graph = builder.compile()