import os
import redis.asyncio as redis
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware # 🎯 IMPORT THE FIX
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from dotenv import load_dotenv

from schemas.api_models import AnalysisRequest, AnalysisResponse, ChatRequest, ChatResponse, CompanyInfo
from utils.security import get_api_key
from processing.web_scraper import scrape_homepage_content
from processing.ai_analyzer import analyze_content_with_llm, answer_follow_up_question

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_connection = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_connection)
        print("Successfully connected to Redis.")
    except Exception as e:
        print(f"Could not connect to Redis. Rate limiting will not work. Error: {e}")
    yield
    print("Shutting down.")


app = FastAPI(
    title="AI Business Insights Agent",
    description="An API for extracting and interpreting business insights from websites.",
    version="1.0.0",
    lifespan=lifespan
)

# 🎯🎯🎯 THIS IS THE FIX 🎯🎯🎯
# This is the "Guest List" for the security guard. We are telling the API
# to accept requests from ANY website. For a public portfolio project, this is perfect.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# --- END OF THE FIX ---

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return HTTPException(status_code=500, detail=f"An internal server error occurred: {exc}")

@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze a Website Homepage",
    dependencies=[Depends(get_api_key), Depends(RateLimiter(times=5, minutes=1))]
)
async def analyze_website(request: AnalysisRequest):
    try:
        content = await scrape_homepage_content(str(request.url))
        if not content.strip():
            raise HTTPException(status_code=404, detail="Could not find any meaningful text content on the homepage.")
        analysis_result = await analyze_content_with_llm(content, request.questions)
        response = AnalysisResponse(
            url=str(request.url),
            analysis_timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            company_info=CompanyInfo(**analysis_result.get("company_info", {})),
            extracted_answers=analysis_result.get("extracted_answers", [])
        )
        return response
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

@app.post(
    "/chat",
    response_model=ChatResponse,
    summary="Conversational Follow-up",
    dependencies=[Depends(get_api_key), Depends(RateLimiter(times=15, minutes=1))]
)
async def conversational_chat(request: ChatRequest):
    try:
        content = await scrape_homepage_content(str(request.url))
        if not content.strip():
            raise HTTPException(status_code=404, detail="Could not find any meaningful text content on the homepage.")
        agent_response = await answer_follow_up_question(
            content=content,
            query=request.query,
            history=request.conversation_history
        )
        response = ChatResponse(
            url=str(request.url),
            user_query=request.query,
            agent_response=agent_response,
            context_sources=["Homepage text content."]
        )
        return response
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

@app.get("/", summary="Health Check")
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}
