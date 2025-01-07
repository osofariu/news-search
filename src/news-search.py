from langchain_core.tools import tool
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from langchain.tools import Tool
from langchain.prompts import PromptTemplate

from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

from langsmith import wrappers, traceable

from nyt_api import (
    nyt_archive_wrapper,
)  # Import nyt_archive_api from the appropriate module
from dotenv import load_dotenv

load_dotenv()


class ArchiveQuery(BaseModel):
    """Inputs to the nyt_archive tool."""

    topic: str = Field(
        description="Something that happened in the past that you want to know about"
    )
    start_date: str = Field(
        description="The beginning of time period you want to know about. This must be in this format: YYYY-MM"
    )
    end_date: str = Field(
        description="The end of the time period you want to know about. This must be in this format: YYYY-MM"
    )


@tool()
def nyt_archive_api(state: MessagesState):
    """Call the NYT Archive API with the given parameters when someone wants to know about a topic in the past."""
    print(f"* tool: state before calling -> {state}") 
    last_message = state["messages"][-1]
    args = last_message.additional_kwargs
    response = nyt_archive_wrapper(args)
    return {"messages": [AIMessage(content=response)]}

tools = [
    Tool(
        name="New York Times Archive API",
        func=nyt_archive_api,
        description="Use this tool when someone wants to know about a topic in the past.",
    )
]
# tools = [nyt_archive_api]
tool_node = ToolNode(tools)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools).with_structured_output(ArchiveQuery)

def call_model(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    last_message = messages[-1]
    last_message.additional_kwargs = {
        "topic": response.topic,
        "start_date": response.start_date,
        "end_date": response.end_date,
    }
    print(f"* call_model: LL respose  -> {response}")
    return {
        "messages": [
            AIMessage(
                content="I will look up news on the topic of climate change from 2020 through 2021.",
                additional_kwargs={
                    "tool_name": "nyt_archive_api",
                    "topic": response.topic,
                    "start_date": response.start_date,
                    "end_date": response.end_date,
                },
            )
        ]
    }


def should_continue(state: MessagesState):
    print(f"*continue: state['messages'] before deciding ->{state}")
    last_message = state["messages"][-1]
    args = last_message.additional_kwargs
    if args["topic"]:
        return "tools"
    return END


@traceable
def invoke_workflow(user_input):
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_edge("tools", END)
    workflow.add_conditional_edges("agent", should_continue)

    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    
    final_state = app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": 1},  "recursion_limit": 5}
    )

    print(f'* Final message: {final_state["messages"][-1].content}')
    print(f'* Final state: {final_state}')
    
invoke_workflow(
    "I want to know about the news on the topic of climate change from 2020 through 2021"
)
