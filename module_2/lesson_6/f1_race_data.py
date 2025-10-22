from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class RaceSessionState(MessagesState):
    race_summary: str


def call_race_control(state: RaceSessionState):
    summary = state.get("race_summary", "")
    if summary:
        system_message = f"Summary of the race session so far: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]

    response = model.invoke(messages)
    return {"messages": response}


def should_generate_report(state: RaceSessionState) -> Literal["generate_race_report", END]:
    messages = state["messages"]
    if len(messages) > 6:
        return "generate_race_report"
    return END


def generate_race_report(state: RaceSessionState):
    summary = state.get("race_summary", "")
    if summary:
        summary_message = (
            f"This is the race report so far: {summary}\n\n"
            "Update the report based on the new radio messages above:"
        )
    else:
        summary_message = "Generate a brief race report based on the radio messages above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"race_summary": response.content, "messages": delete_messages}


workflow = StateGraph(RaceSessionState)
workflow.add_node("radio_comms", call_race_control)
workflow.add_node(generate_race_report)

workflow.add_edge(START, "radio_comms")
workflow.add_conditional_edges("radio_comms", should_generate_report)
workflow.add_edge("generate_race_report", END)

graph = workflow.compile()