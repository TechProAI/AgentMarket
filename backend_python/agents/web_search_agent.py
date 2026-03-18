from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from langchain_tavily import TavilySearch
from services.llm_service import get_llm


class AgentState(TypedDict):
    question: str
    search_queries: List[str]
    search_results: List[str]
    notes: str
    answer: str
    iterations: int

# ----------------------------
# LLM
# ----------------------------

llm = get_llm()

tavily_tool = TavilySearch(
    max_results=3,
    topic="general",
    include_answer=False,
    # include_raw_content=True,
    include_images=True,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)

#Planner Agent
def planner_agent(state: AgentState):

    question = state["question"]

    prompt = f"""
    Generate exactly 2 concise web search queries for this question.

    Return ONLY the queries, one per line.

    Question: {question}
    """

    response = llm.invoke(prompt)

    # queries = response.content.split("\n")
    queries = [
        q.strip().replace("1.", "").replace("2.", "").replace("3.", "")
        for q in response.content.split("\n") if q.strip()
    ]

    return {
        "search_queries": queries
    }

#Search Agent
def search_agent(state: AgentState):

    queries = state["search_queries"]

    results = []

    for query in queries:
        if not query:
            continue

        search = tavily_tool.invoke({
            "query": query
        })

        results.append(str(search))

    return {
        "search_results": results,
        "iterations": state["iterations"] + 1
    }

#Research Agent
def research_agent(state: AgentState):

    results = "\n".join(state["search_results"])

    prompt = f"""
    Extract key insights from the web search results.

    Results:
    {results}
    """

    response = llm.invoke(prompt)

    return {
        "notes": response.content
    }

#Answer Agent
def answer_agent(state: AgentState):

    question = state["question"]
    notes = state["notes"]

    prompt = f"""
    Answer the question in **clean Markdown format**.

    Structure:

    ## Title

    ### Definition

    ### Key Features
    - bullet points

    ### Why it matters

    ### Summary

    Question:
    {question}

    Notes:
    {notes}
    """

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }

#Critic Agent
def critic_agent(state: AgentState):

    question = state["question"]
    answer = state["answer"]
    iterations = state["iterations"]

    # Stop after 2 loops
    if iterations >= 2:
        return "end"

    prompt = f"""
    Check if the answer fully answers the question.

    Question:
    {question}

    Answer:
    {answer}

    Reply only:
    APPROVED
    or
    SEARCH_MORE
    """

    response = llm.invoke(prompt)

    if "APPROVED" in response.content:
        return "end"

    return "search"

#Graph
builder = StateGraph(AgentState)

builder.add_node("planner", planner_agent)
builder.add_node("search", search_agent)
builder.add_node("research", research_agent)
builder.add_node("answer", answer_agent)

builder.set_entry_point("planner")

builder.add_edge("planner", "search")
builder.add_edge("search", "research")
builder.add_edge("research", "answer")

builder.add_conditional_edges(
    "answer",
    critic_agent,
    {
        "search": "search",
        "end": END
    }
)

# checkpointer = InMemorySaver()

graph = builder.compile()

# config = {"configurable": {"thread_id": "1"}}

# ----------------------------
# Public Function
# ----------------------------

def run_web_search_agent(text: str):

    response = graph.invoke({
        "question": text,
        "search_queries": [],
        "search_results": [],
        "notes": "",
        "answer": "",
        "iterations": 0
    })

    return response["answer"]