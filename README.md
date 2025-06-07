# AI Business Insights Agent

This is a high-performance FastAPI application that acts as an AI-powered agent for extracting, synthesizing, and interpreting key business insights from any website homepage.

**Deployed URL**: [https://fastapi-web-agent.onrender.com]

## Architecture Diagram

```mermaid
graph TD
    A[User] -- API Request (URL, Questions) --> B{FastAPI Server};
    B -- Auth Middleware --> C[Secret Key Check];
    C -- Valid --> D[Rate Limiter (Redis)];
    D -- Allowed --> E[Endpoint Logic];
    E -- Scrape URL --> F[Web Scraper (httpx + BeautifulSoup)];
    F -- Homepage Text --> G[AI Analyzer];
    G -- Formatted Prompt --> H[LLM (Ollama/Groq)];
    H -- Structured JSON / Text --> G;
    G -- Parsed Data --> E;
    E -- Formatted Response --> A;

    subgraph "AI Core"
        G
        H
    end
