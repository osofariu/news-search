from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph, MessagesState
from nyt_api import nyt_archive_wrapper  # Import nyt_archive_api from the appropriate module
from dotenv import load_dotenv

# load the environment variables
load_dotenv() 

# @tool
# def extract_news_search_terms():
#   """user asks for a new archive question with a topic and date range.
  
#   The format is something like: "I want to know about the news on the topic of climate change from 2020 to 2022.",
#   where the topic is "climate change" and the date range is from 2020 to 2022, however the date range could
#   include the month of the year as well.  Also decades should be supported, like "from the 90s to the 2000s".

#   Args:
#       query (str): _description_
#   """
#   pass

class ArchiveQueryOutput(BaseModel):
    """Inputs to the wikipedia tool."""
    topic: str = Field(description="Something that happened in the past that you want to know about")   
    start_date: str = Field(description="The beginning of time period you want to know about. This must be in this format: YYYY-MM")
    end_date: str = Field(description="The end of the time period you want to know about. This must be in this format: YYYY-MM")


@tool("call_nyt_archive_api", args_schema=ArchiveQueryOutput)
def call_nyt_archive_api(state: MessagesState):
    """Call the NYT Archive API with the given parameters.
    """
    messages = state['messages']
    response = nyt_archive_wrapper.invoke(messages)
    return {"messages": [response]}
  

def call_model(state: MessagesState):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

tools = [call_nyt_archive_api]
tool_node = ToolNode(tools)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

structured_llm = model.with_structured_output(ArchiveQueryOutput)

result = structured_llm.invoke("I want to know about the news on the topic of climate change from 2020 to 2022.")

print(result)