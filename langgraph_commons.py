### making State class using TypedDict ###########3
from typing_extensions import TypedDict
from typing import Literal

class TypedDictState(TypedDict):
    name:str
    game:Literal["cricket","badminton"]


### making State class using DataClass ###########
from dataclasses import dataclass

@dataclass
class DataClassState:
    name:str
    game:Literal["badminton","cricket"]

### making State class using Pydantic ###########
from pydantic import BaseModel
class State(BaseModel):
    name:str
    


## nodes ###

def play_game(state:DataClassState):
    print("---Play Game node has been called--")
    return {"name":state.name + " want to play "}

def cricket(state:DataClassState):
    print("--Cricket node has been called--")
    return {"name":state.name + " cricket","game":"cricket"}

def badminton(state:DataClassState):
    print("-- badminton node has been called--")
    return {"name":state.name + " badminton","game":"badminton"}

from langgraph.graph import StateGraph, START, END
builder=StateGraph(DataClassState)
builder.add_node("playgame",play_game)
builder.add_node("cricket",cricket)
builder.add_node("badminton",badminton)

builder.add_edge(START,"playgame")
builder.add_conditional_edges("playgame",decide_play)
builder.add_edge("cricket",END)
builder.add_edge("badminton",END)
# Add
graph = builder.compile()

# View
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))


########### TOOLS #############

from langchain_core.messages import HumanMessage
llm_with_tools=llm.bind_tools([add])

## chatbot node functionality
def llm_tool(state:State):
    return {"messages":[llm_with_tools.invoke(state["messages"])]}


tools=[add]

builder=StateGraph(State)

## Add nodes
from langgraph.prebuilt import ToolNode
builder.add_node("llm_tool",llm_tool)
builder.add_node("tools",ToolNode(tools))

## Add Edge
from langgraph.prebuilt import tools_condition
builder.add_edge(START,"llm_tool")
builder.add_conditional_edges(
    "llm_tool",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition
)
builder.add_edge("tools",END)


### react agent build #####

from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

def tool_condition_llm(state:State):
    return {"messages":[llm_with_tools.invoke(state["messages"])]}

builder = StateGraph(State)
builder.add_node("tool_calling_llm", tool_condition_llm)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    tools_condition
)
builder.add_edge("tools", "tool_calling_llm")

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))


###### memory saver ######
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
grapy_with_memory = builder.compile(checkpointer=memory)

config = {"configurable":{"thread_id":"1"}}
grapy_with_memory.invoke({"messages":"Add 2 + 2"}, config=config)



#### langsmith studio ######

# import langgraph-cli[inmem]
# langgraph.json:->

# {
#     "dependencies":["."]
#     "graphs":{
#         "openai_agent":"./openai_agent.py:agent"
#     },
#     "env":"../.env"
# }

# run by - langgraph dev