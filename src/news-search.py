from langchain_core.tools import tool
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

from langsmith import wrappers, traceable

from nyt_api import nyt_archive_wrapper  # Import nyt_archive_api from the appropriate module
from dotenv import load_dotenv

load_dotenv() 

class ArchiveQuery(BaseModel):
    """Inputs to the nyt_archive tool."""
    topic: str = Field(description="Something that happened in the past that you want to know about")   
    start_date: str = Field(description="The beginning of time period you want to know about. This must be in this format: YYYY-MM")
    end_date: str = Field(description="The end of the time period you want to know about. This must be in this format: YYYY-MM")


@tool #("nyt_archive")
def nyt_archive_api(request: ArchiveQuery):
    """Call the NYT Archive API with the given parameters.
    """
    print(f"** call_nyt_archive_api: request={request}")
    response = nyt_archive_wrapper(request)
    return {"response": response}
  
tools = [nyt_archive_api]
tool_node = ToolNode(tools)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

structured_model = model.with_structured_output(ArchiveQuery)

def call_model(state: MessagesState):
    messages = state['messages']
    response = structured_model.invoke(messages)
    state['topic'] = response.topic
    state['start_date'] = response.start_date
    state['end_date'] = response.end_date
    return {"messages": messages}


def should_continue(state: MessagesState):
    if state.get("topic"):
        return "tools"
    return END

@traceable
def invoke_workflow(user_input):
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_edge("tools", "agent")
    workflow.add_conditional_edges("agent", should_continue)

    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    final_state = app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": 1},  "recursion_limit": 5}
    )

    print(final_state["messages"][-1].content)

invoke_workflow("I want to know about the news on the topic of climate change from 2020 through 2021")