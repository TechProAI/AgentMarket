import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from typing import TypedDict, Annotated, List, Union, Optional, Literal
from langchain_tavily import TavilySearch
from serpapi import GoogleSearch
from langchain_core.output_parsers import StrOutputParser
from langgraph.checkpoint.memory import InMemorySaver
import json
import operator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    password = password[:72]   # bcrypt limit
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    plain = plain[:72]
    return pwd_context.verify(plain, hashed)

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

users_db = {}
class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/signup")
def signup(data: SignupRequest):

    if data.email in users_db:
        return {"message": "User already exists"}

    hashed = hash_password(data.password)

    users_db[data.email] = hashed

    return {"message": "User created successfully"}

@app.post("/login")
def login(data: LoginRequest):

    user = users_db.get(data.email)
    print("Users DB:", users_db)
    print("Login email:", data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.password, user):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": data.email})

    return {"access_token": token}

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@app.get("/api/hello")
def hello():
    return {"message": "Hello from Python"}

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

tavily_tool = TavilySearch(max_results=2)
tools = [tavily_tool]

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert travel itinerary planner. ONLY respond to travel planning and itinerary-related questions.

IMPORTANT RULES:
- If asked about non-travel topics (weather, math, general questions), politely decline and redirect to travel planning
- Always provide complete, well-formatted itineraries with specific details
- Include timing, locations, transportation, and practical tips

Use the ReAct approach:
1. THOUGHT: Analyze what travel information is needed
2. ACTION: Search for current information about destinations, attractions, prices, hours
3. OBSERVATION: Process the search results
4. Provide a comprehensive, formatted response

Available tools:
- TavilySearch: Search for current travel information

Format your itineraries with:
- Clear day-by-day breakdown
- Specific times and locations
- Transportation between locations
- Estimated costs when possible
- Practical tips and recommendations"""),
    MessagesPlaceholder(variable_name="messages"),
])

llm_with_tools = llm.bind_tools(tools)
itinerary_agent = itinerary_prompt | llm_with_tools

# Build flight search tool
def search_flights(departure_airport: str, arrival_airport: str, outbound_date: str, return_date: str = None, adults: int = 1, children: int = 0) -> str:
    """
    Search for flights using Google Flights engine.

    Args:
        departure_airport: Departure airport code (e.g., 'NYC', 'LAX')
        arrival_airport: Arrival airport code (e.g., 'LON', 'NRT')
        outbound_date: Departure date (YYYY-MM-DD format)
        return_date: Return date (YYYY-MM-DD format, optional for one-way)
        adults: Number of adult passengers (default: 1)
        children: Number of child passengers (default: 0)
    """

    # Ensure proper integer types
    adults = int(float(adults)) if adults else 1
    children = int(float(children)) if children else 0

    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_flights',
        'hl': 'en',
        'gl': 'us',
        'departure_id': departure_airport,
        'arrival_id': arrival_airport,
        'outbound_date': outbound_date,
        'currency': 'USD',
        'adults': adults,
        'children': children,
        'type': '2' if not return_date else '1'  # FIX #1: Added type parameter (2=one-way)
        # REMOVED: 'stops': '1'  # FIX #2: This parameter doesn't exist!
    }


    if return_date:
        params['return_date'] = return_date

    try:
        search = GoogleSearch(params)
        results = search.get_dict().get('best_flights', [])

        # Fallback to other_flights if no best_flights
        if not results:
            results = search.get_dict().get('other_flights', [])

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Flight search failed: {str(e)}"


# flight agent prompt
flight_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a flight booking expert. ONLY respond to flight-related queries.

IMPORTANT RULES:
- If asked about non-flight topics, politely decline and redirect to flight booking
- Always use the search_flights tool to find current flight information
- You CAN search for flights and analyze the results for:
  * Direct flights vs connecting flights
  * Different airlines and flight classes
  * Various price ranges and timing options
  * Flight duration and layover information
- When users ask for specific preferences (direct flights, specific class, etc.), search first then filter/analyze the results
- Present results clearly organized by outbound and return flights

Available tools:
- search_flights: Search for comprehensive flight data that includes all airlines, classes, and connection types

Process:
1. ALWAYS search for flights first using the tool
2. Analyze the results to find flights matching user preferences
3. Present organized results with clear recommendations

Airport code mapping:
- Delhi: DEL
- London Heathrow: LHR
- New York: JFK/LGA/EWR
- etc."""),
    MessagesPlaceholder(variable_name="messages"),
])

llm_with_flight_tools = llm.bind_tools([search_flights])
flight_agent = flight_prompt | llm_with_flight_tools

# hotel search tool
def search_hotels(location: str, check_in_date: str, check_out_date: str, adults: int = 1, children: int = 0, rooms: int = 1, hotel_class: str = None, sort_by: int = 8) -> str:
    """
    Search for hotels using Google Hotels engine.

    Args:
        location: Location to search for hotels (e.g., 'New York', 'Paris', 'Tokyo')
        check_in_date: Check-in date (YYYY-MM-DD format)
        check_out_date: Check-out date (YYYY-MM-DD format)
        adults: Number of adults (default: 1)
        children: Number of children (default: 0)
        rooms: Number of rooms (default: 1)
        hotel_class: Hotel class filter (e.g., '2,3,4' for 2-4 star hotels)
        sort_by: Sort parameter (default: 8 for highest rating)
    """

    # Ensure proper integer types
    adults = int(float(adults)) if adults else 1
    children = int(float(children)) if children else 0
    rooms = int(float(rooms)) if rooms else 1
    sort_by = int(float(sort_by)) if sort_by else 8

    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_hotels',
        'hl': 'en',
        'gl': 'us',
        'q': location,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'currency': 'USD',
        'adults': adults,
        'children': children,
        'rooms': rooms,
        'sort_by': sort_by
    }

    # Only add hotel_class if provided
    if hotel_class:
        params['hotel_class'] = hotel_class

    try:
        search = GoogleSearch(params)
        properties = search.get_dict().get('properties', [])

        if not properties:
            return f"No hotels found. Available data keys: {list(search.data.keys())}"

        # Return top 5 results
        return json.dumps(properties[:5], indent=2)

    except Exception as e:
        return f"Hotel search failed: {str(e)}"


# Hotel agent prompt
hotel_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a hotel booking expert. ONLY respond to hotel and accommodation-related queries.

IMPORTANT RULES:
- If asked about non-hotel topics, politely decline and redirect to hotel booking
- Always use the search_hotels tool to find current hotel information
- Provide detailed hotel options with prices, ratings, amenities, and location details
- Include practical booking advice and tips
- You CAN search and analyze results for different criteria like star ratings, price ranges, amenities

Available tools:
- search_hotels: Search for hotels using Google Hotels engine

When searching hotels, extract or ask for:
- Location/destination
- Check-in and check-out dates (YYYY-MM-DD format)
- Number of guests (adults, children)
- Number of rooms
- Hotel preferences (star rating, amenities, etc.)

Present results with:
- Hotel name and star rating
- Price per night and total cost
- Key amenities and features
- Location and nearby attractions
- Booking recommendations"""),
    MessagesPlaceholder(variable_name="messages"),
])

# Bind tools and create hotel agent
llm_with_hotel_tools = llm.bind_tools([search_hotels])
hotel_agent = hotel_prompt | llm_with_hotel_tools


#Create Router
def create_router():
    """Creates a router for the three travel agents using LangGraph patterns"""

    router_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a routing expert for a travel planning system.

        Analyze the user's query and decide which specialist agent should handle it:

        - FLIGHT: Flight bookings, airlines, air travel, flight search, tickets, airports, departures, arrivals, airline prices
        - HOTEL: Hotels, accommodations, stays, rooms, hotel bookings, lodging, resorts, hotel search, hotel prices
        - ITINERARY: Travel itineraries, trip planning, destinations, activities, attractions, sightseeing, travel advice, weather, culture, food, general travel questions

        Respond with ONLY one word: FLIGHT, HOTEL, or ITINERARY

        Examples:
        "Book me a flight to Paris" → FLIGHT
        "Find hotels in Tokyo" → HOTEL
        "Plan my 5-day trip to Italy" → ITINERARY
        "Search flights from NYC to London" → FLIGHT
        "Where should I stay in Bali?" → HOTEL
        "What are the best attractions in Rome?" → ITINERARY
        "I need airline tickets" → FLIGHT
        "Show me hotel options" → HOTEL
        "Create an itinerary for Japan" → ITINERARY"""),

        ("user", "Query: {query}")
    ])

    router_chain = router_prompt | llm | StrOutputParser()
    def route_query(state):
        """Router function for LangGraph - decides which agent to call next"""

        # Get the latest user message
        user_message = state["messages"][-1].content

        print(f"🧭 Router analyzing: '{user_message[:50]}...'")

        try:
            # Get LLM routing decision
            decision = router_chain.invoke({"query": user_message}).strip().upper()
            print(f"🎯 Router decision: {decision}")

            # post process decision to make sure it's accurate
            if decision not in ["FLIGHT", "HOTEL", "ITINERARY"]:
                decision = "ITINERARY"

            # Map to our agent node names
            agent_mapping = {
                "FLIGHT": "flight_agent",
                "HOTEL": "hotel_agent",
                "ITINERARY": "itinerary_agent"
            }

            next_agent = agent_mapping.get(decision, "itinerary_agent")
            print(f"🎯 Router decision: {decision} → {next_agent}")

            return next_agent

        except Exception as e:
            print(f"⚠️ Router error, defaulting to itinerary_agent: {e}")
            return "itinerary_agent"

    return route_query

router = create_router()    #Travel Router created for LangGraph!

#Define state schema
class TravelPlannerState(TypedDict):
    """Simple state schema for travel multiagent system"""

    # Conversation history - persisted with checkpoint memory
    messages: Annotated[List[BaseMessage], operator.add]

    # Agent routing
    next_agent: Optional[str]

    # Current user query
    user_query: Optional[str]


#IMPORTANT THING -> CREATE AGENT NODES---------------------------------------------------------

#Itinerary Agent Node
def itinerary_agent_node(state: TravelPlannerState):
    """Itinerary planning agent node"""
    local_messages = list(state["messages"])
    node_generated_messages = []

    while True:
        response = itinerary_agent.invoke({"messages": local_messages})
        node_generated_messages.append(response)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_messages = []
            for tool_call in response.tool_calls:
                tool_result = None
                if tool_call['name'] == 'tavily_search_results_json':
                    try:
                        # Use tool.invoke for consistent tool execution pattern
                        tool_result = tool.invoke({"query": tool_call['args']['query'], "max_results": 2})
                        tool_result = json.dumps(tool_result, indent=2)
                    except Exception as e:
                        tool_result = f"Search failed: {str(e)}"
                else:
                    tool_result = f"Unrecognized tool call: {tool_call['name']}"

                tm = ToolMessage(content=tool_result, tool_call_id=tool_call['id'])
                tool_messages.append(tm)
                node_generated_messages.append(tm)

            local_messages.append(response)
            local_messages.extend(tool_messages)
        else:
            break

    return {"messages": node_generated_messages}

#Flight Agent Node
def flight_agent_node(state: TravelPlannerState):
    """Flight booking agent node"""
    local_messages = list(state["messages"])
    node_generated_messages = []

    while True:
        response = flight_agent.invoke({"messages": local_messages})
        node_generated_messages.append(response)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_messages = []
            for tool_call in response.tool_calls:
                tool_result = None
                if tool_call['name'] == 'search_flights':
                    try:
                        tool_result = search_flights(**tool_call['args'])
                    except Exception as e:
                        tool_result = f"Flight search failed: {str(e)}"
                else:
                    tool_result = f"Unrecognized tool call: {tool_call['name']}"

                tm = ToolMessage(content=tool_result, tool_call_id=tool_call['id'])
                tool_messages.append(tm)
                node_generated_messages.append(tm)

            local_messages.append(response)
            local_messages.extend(tool_messages)
        else:
            break

    return {"messages": node_generated_messages}

#Hotel Agent Node
def hotel_agent_node(state: TravelPlannerState):
    """Hotel booking agent node"""
    local_messages = list(state["messages"])
    node_generated_messages = []

    while True:
        response = hotel_agent.invoke({"messages": local_messages})
        node_generated_messages.append(response)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_messages = []
            for tool_call in response.tool_calls:
                tool_result = None
                if tool_call['name'] == 'search_hotels':
                    try:
                        tool_result = search_hotels(**tool_call['args'])
                    except Exception as e:
                        tool_result = f"Hotel search failed: {str(e)}"
                else:
                    tool_result = f"Unrecognized tool call: {tool_call['name']}"

                tm = ToolMessage(content=tool_result, tool_call_id=tool_call['id'])
                tool_messages.append(tm)
                node_generated_messages.append(tm)

            local_messages.append(response)
            local_messages.extend(tool_messages)
        else:
            break

    return {"messages": node_generated_messages}

#Router Node
def router_node(state: TravelPlannerState):
    """Router node - determines which agent should handle the query"""
    user_message = state["messages"][-1].content
    next_agent = router(state)

    return {
        "next_agent": next_agent,
        "user_query": user_message
    }

# Conditional routing function
def route_to_agent(state: TravelPlannerState):
    """Conditional edge function - routes to appropriate agent based on router decision"""

    next_agent = state.get("next_agent")

    if next_agent == "flight_agent":
        return "flight_agent"
    elif next_agent == "hotel_agent":
        return "hotel_agent"
    elif next_agent == "itinerary_agent":
        return "itinerary_agent"
    else:
        # Default fallback
        return "itinerary_agent"

# Build the complete travel planning graph
workflow = StateGraph(TravelPlannerState)

# Add all nodes to the graph
workflow.add_node("router", router_node)
workflow.add_node("flight_agent", flight_agent_node)
workflow.add_node("hotel_agent", hotel_agent_node)
workflow.add_node("itinerary_agent", itinerary_agent_node)

# Set entry point - always start with router
workflow.set_entry_point("router")

# Add conditional edge from router to appropriate agent
workflow.add_conditional_edges(
    "router",
    route_to_agent,
    {
        "flight_agent": "flight_agent",
        "hotel_agent": "hotel_agent",
        "itinerary_agent": "itinerary_agent"
    }
)

# Add edges from each agent back to END
workflow.add_edge("flight_agent", END)
workflow.add_edge("hotel_agent", END)
workflow.add_edge("itinerary_agent", END)

checkpointer = InMemorySaver()

# Compile the graph
travel_planner = workflow.compile(checkpointer=checkpointer)   #Travel Planning Graph built successfully!

#Interactive Agent like ChatGPT
config = {"configurable": {"thread_id": "1"}}
class ChatRequest(BaseModel):
    text: str

@app.post("/api/travel-agent")
def display_result(data: ChatRequest, user=Depends(verify_token)):

    print("Processing query.....")

    result = travel_planner.invoke(
        {"messages": [HumanMessage(content=data.text)]},
        config
    )

    response = result["messages"][-1].content

    return {"message": response}