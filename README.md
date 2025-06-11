# Advanced FastAPI AI Agent for Website Intelligence

This project is a high-performance FastAPI application that acts as an AI-powered agent. It extracts, synthesizes, and interprets key business insights from any given website homepage, providing both structured data and a conversational interface for follow-up questions.

---

## Architecture Diagram

The diagram below illustrates the flow of data from the user request to the final AI-powered response.

```mermaid
graph TD
    A[User] -- API Request (URL, Questions) --> B{FastAPI Server};
    B -- Auth Middleware --> C[Secret Key Check];
    C -- Valid --> D[Rate Limiter];
    D -- Allowed --> E[Endpoint Logic];
    E -- Scrape URL --> F["Web Scraper (httpx + BeautifulSoup)"];
    F -- Homepage Text & Data --> G[AI Analyzer];
    G -- Formatted Prompt --> H["LLM (Groq / Ollama)"];
    H -- Structured JSON / Text --> G;
    G -- Parsed Data --> E;
    E -- Formatted Response --> A;

    subgraph "AI Core"
        G
        H
    end


Flow Description:

A User sends a request to the FastAPI server containing a URL and optional questions.

The Auth Middleware first validates the secret key from the Authorization header.

The Rate Limiter checks if the user has exceeded their request limit.

If authorized and allowed, the request is passed to the specific Endpoint Logic (/analyze or /chat).

The Web Scraper, using httpx for requests and BeautifulSoup for parsing, extracts the text content and contact info from the website's homepage.

The extracted data is sent to the AI Analyzer core.

The analyzer constructs a detailed, engineered prompt and sends it to the Large Language Model (LLM).

The LLM processes the text and returns structured data or a natural language answer.

The analyzer parses the LLM response, combines it with the scraped contact info, and sends the clean, structured data back to the endpoint.

Finally, a Pydantic-validated JSON response is sent back to the user.

Technology Justification

FastAPI:

High Performance: Chosen for its asynchronous capabilities (built on Starlette and ASGI), which are essential for handling network-bound operations like web scraping and AI API calls efficiently without blocking the server.

Data Validation: FastAPI's native integration with Pydantic ensures robust, type-hinted data validation for all incoming requests and outgoing responses, reducing errors and making the API reliable.

Automatic Documentation: It automatically generates interactive API documentation (Swagger UI and ReDoc), which is crucial for demonstrating and testing the endpoints.

Scraping Tools (httpx + BeautifulSoup):

httpx: A modern, async-first HTTP client. It was selected to work seamlessly with FastAPI's async environment, allowing for non-blocking web page requests.

BeautifulSoup: A powerful and forgiving Python library for parsing HTML. It excels at navigating and extracting specific information from a website's DOM tree, even if the HTML is not perfectly structured. We use the lxml parser for its speed and robustness.

AI Model Used & Rationale

LLMs Used: This project is designed to be flexible, supporting both cloud-based and local models.

Cloud: Groq with the llama3-8b-8192 model.

Local: Ollama with the tinyllama model.

Rationale:

Groq: Chosen for its exceptional inference speed, which is critical for providing real-time analysis and conversational responses. Its API-based access simplifies integration for production-level performance.

Ollama with tinyllama: Provides a powerful alternative for local development. tinyllama was specifically chosen because its small footprint ensures compatibility with a wide range of hardware, running effectively on a CPU without requiring a dedicated GPU. This avoids common infrastructure issues (like CUDA errors) and allows for cost-free, private, and offline-capable development.

Dual-Approach: This setup offers the best of both worlds: high-performance for a cloud deployment and easy, accessible, and private local development.

Local Setup & Running Instructions
1. Prerequisites

You must have the following installed and running on your system:

Python 3.10+

Ollama (for local AI model development)

Redis (for API rate limiting)

2. Installation & Setup
# Clone the repository (example command)
git clone https://github.com/your-username/fastapi-web-agent-main.git
cd fastapi-web-agent-main

# Create and activate a Python virtual environment
# On Windows:
python -m venv venv
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all required dependencies
pip install -r requirements.txt```

### 3. Configure Environment Variables
Create a file named `.env` in the root of the project folder. Copy the template below into the file and add your secret key.

```env
# .env
# Invent your own secret password. This will be used in the "Authorization: Bearer <key>" header.
APP_SECRET_KEY="your_super_secret_password_here"

# OPTIONAL: To use the high-speed Groq service, add your key here.
# If left blank, the application will default to using local Ollama.
GROQ_API_KEY=

# OPTIONAL: Only change these if your local services are not running on default ports.
OLLAMA_HOST="http://localhost:11434"
REDIS_URL="redis://localhost:6379"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END
4. Prepare Local AI Model

If you are using Ollama, you must pull the tinyllama model.

ollama pull tinyllama```

### 5. Run the Application
Start the FastAPI server using `uvicorn`. The application's main file is `agent_server.py`.

```bash
uvicorn agent_server:app --reload
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

The API is now running at http://127.0.0.1:8000. The interactive documentation is available at http://127.0.0.1:8000/docs.

API Usage Examples

The following examples use PowerShell on Windows. Replace your_super_secret_password_here with the secret key you set in your .env file.

Endpoint 1: /analyze

This endpoint performs the primary analysis of a website.

Example PowerShell Command:

# 1. Define headers and body
$headers = @{
    "Content-Type"  = "application/json";
    "Authorization" = "Bearer your_super_secret_password_here"
}

$body = @'
{
    "url": "https://www.mongodb.com/",
    "questions": [
        "What kind of database is this?",
        "What is the main benefit of using this product?"
    ]
}
'@

# 2. Make the API call and view the clean JSON response
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/analyze" -Method POST -Headers $headers -Body $body).Content | ConvertFrom-Json
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Powershell
IGNORE_WHEN_COPYING_END
Endpoint 2: /chat

This endpoint handles conversational follow-up questions.

Example PowerShell Command:

# 1. Define headers and body
$headers = @{
    "Content-Type"  = "application/json";
    "Authorization" = "Bearer your_super_secret_password_here"
}

$body = @'
{
    "url": "https://www.mongodb.com/",
    "query": "Tell me more about their Atlas product in simple terms."
}
'@

# 2. Make the API call and view the clean JSON response
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/chat" -Method POST -Headers $headers -Body $body).Content | ConvertFrom-Json
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Powershell
IGNORE_WHEN_COPYING_END
IDE Used

IDE: Visual Studio Code

Key Extensions for this Project:

Python (Microsoft): Core Python language support, debugging, and linting.

Pylance (Microsoft): Provides high-performance type checking and smart code completions.

Thunder Client: An in-editor REST client useful for quickly testing API endpoints without leaving the IDE.

IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
