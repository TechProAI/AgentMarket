from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth.security import verify_token
from agents.travel_agent import run_travel_agent, travel_planner, config

router = APIRouter(prefix="/api", tags=["agents"])


class ChatRequest(BaseModel):
    text: str


@router.post("/travel-agent")
def display_result(data: ChatRequest, user=Depends(verify_token)):

    print("Processing query.....")

    response = run_travel_agent(data.text)

    return {"message": response}