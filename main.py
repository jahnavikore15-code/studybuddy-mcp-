"""StudyBuddy web API. It calls tools on the separate MCP server via MCP client."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.getenv("STUDYBUDDY_MCP_URL", "http://127.0.0.1:8000/mcp")

@asynccontextmanager
async def mcp_session():
    try:
        async with streamablehttp_client(MCP_URL) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot reach MCP server at {MCP_URL}. Start server.py first. Details: {exc}",
        ) from exc

async def call_tool(name: str, arguments: dict):
    async with mcp_session() as session:
        result = await session.call_tool(name, arguments=arguments)
        parts = [item.text for item in result.content if getattr(item, "text", None)]
        output_text = "\n".join(parts) or "The tool returned no text."
        if result.isError:
            raise HTTPException(status_code=400, detail=output_text)
        return output_text

app = FastAPI(title="StudyBuddy API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "StudyBuddy API",
        "docs": "/docs",
        "health": "/api/health",
        "frontend": "http://127.0.0.1:5500",
        "mcp_url": MCP_URL,
    }

class NoteInput(BaseModel):
    topic: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=10000)

class QuizInput(BaseModel):
    topic: str = Field(min_length=1, max_length=100)
    num_questions: int = Field(default=5, ge=1, le=10)

class PlanInput(BaseModel):
    exam_date: str
    topics: list[str] = Field(min_length=1, max_length=30)

@app.get("/api/health")
async def health():
    return {"status": "ok", "mcp_url": MCP_URL}

@app.get("/api/topics")
async def topics():
    result = await call_tool("list_study_topics", {})
    return {"result": result}

@app.get("/api/notes")
async def notes(topic: str):
    clean_topic = topic.strip()
    if not clean_topic:
        raise HTTPException(status_code=400, detail="Topic parameter cannot be empty.")
    result = await call_tool("get_study_notes", {"topic": clean_topic})
    return {"result": result}

@app.post("/api/notes")
async def add_note(payload: NoteInput):
    result = await call_tool("add_note", {"topic": payload.topic, "text": payload.text})
    return {"result": result}

@app.post("/api/quiz")
async def quiz(payload: QuizInput):
    result = await call_tool(
        "quiz_me",
        {"topic": payload.topic, "num_questions": payload.num_questions},
    )
    return {"result": result}

@app.post("/api/plan")
async def plan(payload: PlanInput):
    result = await call_tool(
        "revision_plan",
        {"exam_date": payload.exam_date, "topics": payload.topics},
    )
    return {"result": result}
