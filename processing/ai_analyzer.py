import os
import json
import ollama
from groq import Groq
from typing import List, Dict, Optional

# --- Configuration ---
# Set USE_GROQ to True for deployment, False for local Ollama development.
# This is determined by the presence of the GROQ_API_KEY environment variable.
USE_GROQ = os.getenv("GROQ_API_KEY") is not None and len(os.getenv("GROQ_API_KEY")) > 0

if USE_GROQ:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    LLM_MODEL = "llama3-8b-8192"
    print("AI Analyzer configured to use Groq Cloud API.")
else:
    try:
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_client = ollama.Client(host=ollama_host)
        # Verify connection
        ollama_client.list()
        LLM_MODEL = "llama3:8b"
        print(f"AI Analyzer configured to use local Ollama at {ollama_host}.")
    except Exception as e:
        print(f"FATAL: Could not connect to Ollama at {ollama_host}. Please ensure Ollama is running. Error: {e}")
        ollama_client = None


# --- Prompt Engineering ---
ANALYSIS_SYSTEM_PROMPT = """
You are an expert business analyst AI. Your task is to analyze the text content from a company's homepage and extract key business information.
Respond ONLY with a single, valid JSON object. Do not include any text, explanations, or markdown formatting before or after the JSON.
The JSON object must strictly follow this structure:
{
  "industry": "A specific industry category (e.g., 'Financial Technology', 'E-commerce', 'Healthcare SaaS')",
  "company_size": "An estimated size (e.g., 'Startup (1-10 employees)', 'Medium (50-200 employees)', 'Large Enterprise (>1000 employees)') or 'N/A' if not found.",
  "location": "The primary headquarters or location (e.g., 'San Francisco, CA, USA') or 'N/A' if not found.",
  "core_products_services": ["A list of the main products or services offered."],
  "unique_selling_proposition": "A concise, one-sentence summary of what makes the company unique.",
  "target_audience": "A description of the primary customer demographic (e.g., 'Small to Medium Businesses (SMBs)', 'Individual Consumers', 'Large Enterprises').",
  "contact_info": {
    "email": "The primary contact email or 'N/A'.",
    "phone": "The primary phone number or 'N/A'.",
    "social_media": { "linkedin": "URL", "twitter": "URL", ... }
  }
}
If information for a field is not available in the provided text, use "N/A" for strings, an empty list for arrays, or an empty object for the social_media map.
"""

def _generate_llm_response(messages: List[Dict[str, str]]) -> str:
    """Internal function to call the configured LLM."""
    if USE_GROQ:
        response = groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=2048,
            response_format={"type": "json_object"} if "json" in messages[0]["content"].lower() else None
        )
        return response.choices[0].message.content
    else:
        if not ollama_client:
            raise Exception("Ollama client is not initialized. Is Ollama running?")
        
        # Ollama API call
        response = ollama_client.chat(
            model=LLM_MODEL,
            messages=messages,
            format='json' if "json" in messages[0]["content"].lower() else ''
        )
        return response['message']['content']


async def analyze_content_with_llm(content: str, custom_questions: Optional[List[str]]) -> Dict:
    """
    Analyzes website content to extract core business details and answer specific questions.
    """
    analysis_messages = [
        {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": f"Here is the website content:\n\n---\n\n{content}\n\n---\n\nExtract the business information based on your instructions."}
    ]
    
    try:
        raw_response = _generate_llm_response(analysis_messages)
        company_info = json.loads(raw_response)
    except json.JSONDecodeError:
        raise Exception("LLM returned malformed JSON for company info.")
    except Exception as e:
        raise Exception(f"An error occurred during LLM company info analysis: {e}")

    extracted_answers = []
    if custom_questions:
        for question in custom_questions:
            qa_messages = [
                {"role": "system", "content": "You are a helpful question-answering assistant. Use the provided context to answer the user's question concisely and accurately. If the answer is not in the context, state that the information is not available on the homepage."},
                {"role": "user", "content": f"Context:\n\n---\n\n{content}\n\n---\n\nQuestion: {question}"}
            ]
            try:
                answer = _generate_llm_response(qa_messages)
                extracted_answers.append({"question": question, "answer": answer})
            except Exception as e:
                extracted_answers.append({"question": question, "answer": f"Error answering question: {e}"})

    return {"company_info": company_info, "extracted_answers": extracted_answers}

async def answer_follow_up_question(content: str, query: str, history: List[Dict[str, str]]) -> str:
    """
    Answers a follow-up question using the website content and conversation history as context.
    """
    system_prompt = "You are a conversational AI agent. You are having a conversation about a specific website. Use the provided website content and conversation history to answer the user's latest query. Be helpful, conversational, and base your answers on the provided text. If you don't know the answer, say so."
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "system", "content": f"Website Content Context:\n\n---\n{content}\n---"})
    
    for turn in history:
        messages.append({"role": "user", "content": turn.get("user_query", "")})
        messages.append({"role": "assistant", "content": turn.get("agent_response", "")})

    messages.append({"role": "user", "content": query})

    try:
        response = _generate_llm_response(messages)
        return response
    except Exception as e:
        raise Exception(f"An error occurred during conversational LLM call: {e}")
