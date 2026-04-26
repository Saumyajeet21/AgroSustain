import asyncio
from main import chat_with_gemini
from pydantic import BaseModel
class ChatRequest(BaseModel):
    message: str
    session_id: str = 'default'
    history: list = []

req = ChatRequest(message="Tell me about farming.", history=[{'role': 'assistant', 'parts': [{'text': 'Hello'}]}])
res = asyncio.run(chat_with_gemini(req))
