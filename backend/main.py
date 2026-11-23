from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import games

app = FastAPI()
app.include_router(games.router)
app.state.sessions = {}

origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}