from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langsmith import traceable
from nyt_api import NYTApi, ArchiveResponse
import os
import sys
import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from datetime import datetime
from dotenv import load_dotenv

from helpers import (
    get_last_content,
    last_message_has_tool_calls,
    last_message_is_ask_for_human_input,
    next_node_is_human,
)

load_dotenv()
logger = logging.getLogger(__name__)
nyt_news = NYTApi(os.getenv("NYT_API_KEY"), max_range=6)
today = datetime.today().strftime("%Y-%m-%d")
console = Console()


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


def fancy_print(text: str, style=""):
    text = Text(text=text, style=style)
    console.print(text)


@tool(
    "nyt_archive_search",
    args_schema=ArchiveQuery,
    return_direct=True,
    parse_docstring=True,
)
def nyt_archive_search(topic: str, start_date: str, end_date: str) -> ArchiveResponse:
    """Call the NYT Archive API with topic, start_date, end_date to search the NYT archive on a topic for a date range.

    Args:
        topic: a search query for in the NYT archive.
        start_date: the beginning of the date range with format YYYY.MM.
        end_date: the beginning of the date range with format YYYY.MM.
    """
    fancy_print(f"Searching for {topic} from {start_date} to {end_date}", "bright_cyan")
    response = nyt_news.get_archives(topic, start_date, end_date)
    return {"messages": [AIMessage(content=str(response))]}


SYSTEM_MESSAGE = f"""
You are a helpful librarian who helps people use the New York Times Archive to find
interesting stories about topics they are interested in.  You need to find out what the
topic is and the date range they are interested in. 

Today is: {today} The start date must be after 1852, and the end date can be as late as today.
When computing relative dates use the today's date that I have passed in.

If you cannot determine the topic, start date, and end date from the question you must ask 
for clarification. You must use the nyt_archive_search tool and cannot answer the question 
using general knowledge.

Afer the tool was called and we have some articles to review you should include a wide
selection of articles, and can omit those that seem to be duplicates.
"""


class NewsSearch:
    def __init__(self):
        tools = [nyt_archive_search]
        self.tool_node = ToolNode(tools)
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(
            tools, parallel_tool_calls=False
        )

    def call_model(self, state: MessagesState):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def should_continue(self, state: MessagesState):
        if last_message_has_tool_calls(state):
            return "tools"
        elif last_message_is_ask_for_human_input(state):
            return "human_input"
        else:
            return END

    def human_input(self, state: MessagesState):
        human_message = interrupt("human_input")
        return {
            "messages": [HumanMessage(content=human_message)],
        }

    @traceable
    def build_graph(self):
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("agent", self.call_model)
        graph_builder.add_node("tools", self.tool_node)
        graph_builder.add_node("human_input", self.human_input)

        graph_builder.add_edge(START, "agent")
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge("human_input", "agent")
        graph_builder.add_conditional_edges("agent", self.should_continue)

        checkpointer = MemorySaver()
        graph = graph_builder.compile(checkpointer=checkpointer)
        graph.get_graph(xray=1).draw_mermaid_png(output_file_path="graph.png")
        return graph

    def run_graph(self, question, config):
        graph = self.build_graph()
        config = {"configurable": {"thread_id": 1}, "recursion_limit": 25}
        state = graph.invoke(
            {
                "messages": [
                    SystemMessage(content=SYSTEM_MESSAGE),
                    HumanMessage(content=question),
                ]
            },
            config=config,
        )

        content = get_last_content(state)
        while next_node_is_human(graph, config):
            console.print(Text(f"{content}\n =>", style="bold bright_cyan"), end=" ")
            improved_question = console.input()
            final_state = graph.invoke(Command(resume=improved_question), config=config)
            content = get_last_content(final_state)
        return content


def main():
    logging.basicConfig(
        filename="logs/news_search.log",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    if sys.argv[1:]:
        query = " ".join(sys.argv[1:])
    else:
        query = "I want to know about the news from NYT archive about COVID from September 2024 through the end of the year"

    config = {"configurable": {"thread_id": 1}, "recursion_limit": 4}
    news_search = NewsSearch()
    response = news_search.run_graph(question=query, config=config)
    md = Markdown(response)
    console.print(md)


if __name__ == "__main__":
    main()
