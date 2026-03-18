from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.travel_routes import router as travel_router
from routes.auth_routes import router as auth_router
from routes.web_search_routes import router as web_search_router
from routes.home_routes import router as home_router
from routes.resume_builder_routes import router as resume_builder_router

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(travel_router)
app.include_router(web_search_router)
app.include_router(home_router)
app.include_router(resume_builder_router)