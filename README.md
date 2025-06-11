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
```

**Flow Description:**
1.  A **User** sends a request to the FastAPI server containing a URL and optional questions.
2.  The **Auth Middleware** first validates the secret key.
3.  The **Rate Limiter** checks if the user has exceeded their request limit.
4.  If authorized and allowed, the request is passed to the specific **Endpoint Logic**.
5.  The **Web Scraper**, using `httpx` for requests and `BeautifulSoup` for parsing, extracts the text content from the website's homepage.
6.  The extracted text is sent to the **AI Analyzer** core.
7.  The analyzer constructs a detailed, engineered prompt and sends it to the **Large Language Model (LLM)**, such as a model served via Groq or Ollama.
8.  The LLM processes the text and returns structured data or a natural language answer.
9.  The analyzer parses this response and sends the clean, structured data back to the endpoint.
10. Finally, a Pydantic-validated JSON response is sent back to the user.

---

## Technology Justification

*   **FastAPI:**
    *   **High Performance:** Chosen for its asynchronous capabilities (built on Starlette and ASGI), which are essential for handling network-bound operations like web scraping and AI API calls efficiently without blocking the server.
    *   **Data Validation:** FastAPI's native integration with Pydantic ensures robust, type-hinted data validation for all incoming requests and outgoing responses, reducing errors and making the API reliable.
    *   **Automatic Documentation:** It automatically generates interactive API documentation (Swagger UI and ReDoc), which is crucial for demonstrating and testing the endpoints.

*   **Scraping Tools (`httpx` + `BeautifulSoup`):**
    *   **`httpx`:** A modern, async-first HTTP client. It was selected to work seamlessly with FastAPI's async environment, allowing for non-blocking web page requests.
    *   **`BeautifulSoup`:** A powerful and forgiving Python library for parsing HTML. It excels at navigating and extracting specific information from a website's DOM tree, even if the HTML is not perfectly structured.

---

## AI Model Used & Rationale

*   **LLM Used:** This project is designed to be flexible, primarily utilizing high-speed models via **Groq** (e.g., Llama 3) or locally-hosted models via **Ollama**.

*   **Rationale:**
    *   **Groq:** Chosen for its exceptional inference speed, which is critical for providing the real-time analysis and conversational responses required by the project specifications. Its API-based access simplifies integration.
    *   **Ollama:** Provides a powerful alternative for local development and deployment. Using Ollama allows for cost-free experimentation, data privacy (as data is not sent to a third-party service), and the ability to run without an internet connection once models are downloaded. This dual-approach provides a balance between performance, cost, and privacy.
    *   **Prompt Engineering:** The system relies on carefully crafted prompts to instruct the LLM to act as a business analyst. This ensures the model accurately extracts specific information (like Industry, USP, Target Audience) and returns it in a structured JSON format, fulfilling the core requirement of the task.

---

## Local Setup & Running Instructions

**1. Prerequisites:**
*   Python 3.9+
*   Git
*   Ollama (Optional, for local model usage)

**2. Clone the Repository:**
```bash
git clone <your-repository-url>
cd <repository-folder-name>
```

**3. Create and Activate a Virtual Environment:**
```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**4. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**5. Configure Environment Variables:**
*   Create a file named `.env` in the root directory.
*   Add the following variables to the `.env` file, replacing the placeholder values:
```
# .env
SECRET_KEY="your_predefined_secret_key"
GROQ_API_KEY="your_groq_api_key_if_using_groq"
```

**6. Run the Application:**
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. The interactive documentation can be accessed at `http://127.0.0.1:8000/docs`.

---

## API Usage Examples

Replace `YOUR_SECRET_KEY` with the key defined in your `.env` file.

### Endpoint 1: Website Analysis & Initial Extraction

**Request (using cURL):**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/analyze-website' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_SECRET_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.cloudflare.com/",
  "questions": [
    "What is their main mission?",
    "What year were they founded?"
  ]
}'
```

### Endpoint 2: Conversational Interaction & Follow-up Questions

**Request (using cURL):**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/chat-with-website' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_SECRET_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.cloudflare.com/",
  "query": "Can you explain their security services in simpler terms?"
}'
```

---

## IDE Used

*   **IDE:** Visual Studio Code
*   **Key Extensions for this Project:**
    *   **Python** (Microsoft): Core Python language support, debugging, and linting.
    *   **Pylance** (Microsoft): Provides high-performance type checking and smart code completions.
    *   **Thunder Client**: An in-editor REST client for quickly testing the API endpoints without leaving the IDE.
