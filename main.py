from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os
from groq import Groq 
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio


load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)


class Promt(BaseModel) :
    query : str


async def groq_response(query : str):
    stream = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "",
            },
             {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-8b-8192",
        stream=True,
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
            await asyncio.sleep(0.05)


@app.get('/')
async def index():
    return "Hello World"


@app.post('/chatbot')
async def chatbot(promt : Promt):  
    return StreamingResponse(groq_response(promt.query), media_type="text/plain")

