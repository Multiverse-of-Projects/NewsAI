
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth
app = FastAPI() 
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)