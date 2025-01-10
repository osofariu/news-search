from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
from nyt_api import NYTNewsApi, ArchiveResponse
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
nyt_news = NYTNewsApi(os.getenv("NYT_API_KEY"))

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
def nyt_archive_search(topic: str, start_date: str, end_date: str) -> ArchiveResponse:
    """Call the NYT Archive API with topic, start_date, end_date to search the NYT archive on a topic for a date range.
    
    Args:
        topic: a search query for in the NYT archive.
        start_date: the beginning of the date range with format YYYY.MM.
        end_date: the beginning of the date range with format YYYY.MM.
    """
    print(f"Searching for {topic} from {start_date} to {end_date}")
    response = nyt_news.get_archives(topic, start_date, end_date)
    return {"messages": [AIMessage(content=str(response))]}

class NewsSearch:
    def __init__(self):
        tools = [nyt_archive_search]
        self.tool_node = ToolNode(tools)
        self.nyt_news = NYTNewsApi(os.getenv("NYT_API_KEY"))
        self.model = (
            ChatOpenAI(model="gpt-4o-mini", temperature=0)
            .bind_tools(tools)
        )

    def call_model(self, state: MessagesState):
        logger.debug("Calling model")
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}


    def should_continue(self, state: MessagesState):
        last_message = state["messages"][-1]
        args = last_message.additional_kwargs
        if args.get("tool_calls"):
            return "tools"
        return END

    @traceable
    def invoke_workflow(self, user_input):
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)

        workflow.add_edge(START, "agent")
        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges("agent", self.should_continue)

        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer=checkpointer)

        final_state = app.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": 1}, "recursion_limit": 25},
        )

        messages = final_state.get("messages", [])
        if messages:
            return messages[-1].content
        return "No response"
    

def main(): 
    logging.basicConfig(filename="logs/news_search.log", level=logging.INFO)
    query = "I want to know about the news from NYT archive about Romania from September 2024 through December 2024"
    if sys.argv[1:]:
        query = " ".join(sys.argv[1:])
        
    print(f"Running the NYT API search with query: {query}\n")
    news_search = NewsSearch()
    response = news_search.invoke_workflow(query)
    print(f"# Response:\n{response}")

if __name__ == "__main__":
    main()