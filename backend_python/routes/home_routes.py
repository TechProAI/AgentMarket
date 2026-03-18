from fastapi import APIRouter, Depends

from auth.security import verify_token

router = APIRouter(prefix="/api", tags=["agents"])



@router.get("/home")
def hello(user=Depends(verify_token)):
    return {"message": "Hello from Python"}