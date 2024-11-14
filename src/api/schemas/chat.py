from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

class SuggestedQuestionsResponse(BaseModel):
    questions: List[str]
