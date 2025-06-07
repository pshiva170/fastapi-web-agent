import pydantic
from typing import List, Optional, Dict

class ContactInfo(pydantic.BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None

class CompanyInfo(pydantic.BaseModel):
    industry: Optional[str] = "N/A"
    company_size: Optional[str] = "N/A"
    location: Optional[str] = "N/A"
    core_products_services: Optional[List[str]] = []
    unique_selling_proposition: Optional[str] = "N/A"
    target_audience: Optional[str] = "N/A"
    contact_info: Optional[ContactInfo] = ContactInfo()

class ExtractedAnswer(pydantic.BaseModel):
    question: str
    answer: str

class AnalysisRequest(pydantic.BaseModel):
    url: pydantic.HttpUrl
    questions: Optional[List[str]] = None

class AnalysisResponse(pydantic.BaseModel):
    url: str
    analysis_timestamp: str
    company_info: CompanyInfo
    extracted_answers: List[ExtractedAnswer] = []

class ChatRequest(pydantic.BaseModel):
    url: pydantic.HttpUrl
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(pydantic.BaseModel):
    url: str
    user_query: str
    agent_response: str
    context_sources: Optional[List[str]] = None
