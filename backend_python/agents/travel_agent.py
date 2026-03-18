import json
import operator
from typing import TypedDict, Annotated, List, Optional

from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from langchain_tavily import TavilySearch
from serpapi import GoogleSearch

from services.llm_service import get_llm


# ----------------------------
# LLM
# ----------------------------

llm = get_llm()

# ----------------------------
# Tools
# ----------------------------

tavily_tool = TavilySearch(max_results=2)


def search_flights(departure_airport, arrival_airport, outbound_date, return_date=None, adults=1, children=0):

    params = {
        "engine": "google_flights",
        "departure_id": departure_airport,
        "arrival_id": arrival_airport,
        "outbound_date": outbound_date,
        "currency": "USD",
        "adults": adults,
        "children": children
    }

    if return_date:
        params["return_date"] = return_date

    search = GoogleSearch(params)

    results = search.get_dict().get("best_flights", [])

    return json.dumps(results[:5], indent=2)


def search_hotels(location, check_in_date, check_out_date):

    params = {
        "engine": "google_hotels",
        "q": location,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }

    search = GoogleSearch(params)

    results = search.get_dict().get("properties", [])

    return json.dumps(results[:5], indent=2)


# ----------------------------
# Prompts
# ----------------------------

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a travel itinerary planner.

Create detailed travel plans including:
- attractions
- schedule
- tips
"""),
    MessagesPlaceholder(variable_name="messages")
])


flight_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a flight booking expert.

Always search flights using the tool.
"""),
    MessagesPlaceholder(variable_name="messages")
])


hotel_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a hotel booking expert.

Always search hotels using the tool.
"""),
    MessagesPlaceholder(variable_name="messages")
])


# ----------------------------
# Agents
# ----------------------------

itinerary_agent = itinerary_prompt | llm
flight_agent = flight_prompt | llm
hotel_agent = hotel_prompt | llm


# ----------------------------
# State Schema
# ----------------------------

class TravelPlannerState(TypedDict):

    messages: Annotated[List[BaseMessage], operator.add]

    next_agent: Optional[str]


# ----------------------------
# Router
# ----------------------------

router_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """Route query to:

FLIGHT
HOTEL
ITINERARY
"""),
    ("user", "{query}")
])

router_chain = router_prompt | llm | StrOutputParser()


def router_node(state):

    query = state["messages"][-1].content

    decision = router_chain.invoke({"query": query}).strip().upper()

    if decision not in ["FLIGHT", "HOTEL"]:
        return {"next_agent": "itinerary_agent"}

    if decision == "FLIGHT":
        return {"next_agent": "flight_agent"}

    if decision == "HOTEL":
        return {"next_agent": "hotel_agent"}


# ----------------------------
# Agent Nodes
# ----------------------------

def itinerary_agent_node(state):

    response = itinerary_agent.invoke({"messages": state["messages"]})

    return {"messages": [response]}


def flight_agent_node(state):

    response = flight_agent.invoke({"messages": state["messages"]})

    return {"messages": [response]}


def hotel_agent_node(state):

    response = hotel_agent.invoke({"messages": state["messages"]})

    return {"messages": [response]}


# ----------------------------
# Routing Logic
# ----------------------------

def route_to_agent(state):

    return state["next_agent"]


# ----------------------------
# Graph
# ----------------------------

workflow = StateGraph(TravelPlannerState)

workflow.add_node("router", router_node)

workflow.add_node("itinerary_agent", itinerary_agent_node)
workflow.add_node("flight_agent", flight_agent_node)
workflow.add_node("hotel_agent", hotel_agent_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_to_agent,
    {
        "flight_agent": "flight_agent",
        "hotel_agent": "hotel_agent",
        "itinerary_agent": "itinerary_agent"
    }
)

workflow.add_edge("flight_agent", END)
workflow.add_edge("hotel_agent", END)
workflow.add_edge("itinerary_agent", END)

checkpointer = InMemorySaver()

travel_planner = workflow.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}


# ----------------------------
# Public Function
# ----------------------------

def run_travel_agent(text: str):

    result = travel_planner.invoke(
        {"messages": [HumanMessage(content=text)]},
        config
    )

    return result["messages"][-1].content