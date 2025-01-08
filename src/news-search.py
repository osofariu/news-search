from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langsmith import wrappers, traceable
from nyt_api import nyt_archive_wrapper
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

@tool("nyt_archive_search", args_schema=ArchiveQuery, return_direct=True, parse_docstring=True)
def nyt_archive_search(topic: str, start_date: str, end_date: str) -> str:
    """Call the NYT Archive API with topic, start_date, end_date to search the NYT archive on a topic for a date range.
    
    Args:
        topic: a search query for in the NYT archive.
        start_date: the beginning of the date range with format YYYY.MM.
        end_date: the beginning of the date range with format YYYY.MM.
        """
    print(f"********** tool")
    response = nyt_archive_wrapper(topic, start_date, end_date)
    return {"messages": [AIMessage(content=response)]}


def should_continue(state: MessagesState):
    print(f"*continue: state['messages'] before deciding ->{state}")
    last_message = state["messages"][-1]
    args = last_message.additional_kwargs
    if args["tool_calls"]:
        return "tools"
    return END


class NewsSearch:
    
    def __init__(self):
        tools = [nyt_archive_search]
        self.tool_node = ToolNode(tools)

        self.model = (
            ChatOpenAI(model="gpt-4o-mini", temperature=0)
            .bind_tools(tools)
            #.with_structured_output(ArchiveQuery)
        )

    def call_model(self, state: MessagesState):
        messages = state["messages"]
        response = self.model.invoke(messages)
        last_message = messages[-1]
        print(f"* call_model: LL respose  -> {response}")
        return {"messages": [response]}
        return response

    @traceable
    def invoke_workflow(self, user_input):
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)

        workflow.add_edge(START, "agent")
        workflow.add_edge("tools", END)
        workflow.add_conditional_edges("agent", should_continue)

        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer=checkpointer)

        final_state = app.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": 1}, "recursion_limit": 5},
        )

        print(f'* Final message: {final_state["messages"][-1].content}')
        print(f"* Final state: {final_state}")

        return final_state
    
news_search = NewsSearch()
news_search.invoke_workflow(
    "I want to know about the news from NYT archive about climate change from 2020 through 2021"
)
