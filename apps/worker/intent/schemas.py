from typing import Optional
from pydantic import BaseModel, Field
from .taxonomy import Intent

class IntentAnalysis(BaseModel):
    """Result of an intent analysis on subject or body."""
    intent: Intent = Field(description="The primary intent of the email text.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    reasoning: str = Field(description="Brief explanation for the chosen intent.")

class EmailIntentState(BaseModel):
    """LangGraph state for email intent analysis."""
    subject: str
    body: str
    
    subject_intent: Optional[Intent] = None
    subject_confidence: Optional[float] = None
    
    body_intent: Optional[Intent] = None
    body_confidence: Optional[float] = None
    
    final_intent: Optional[Intent] = None
    final_confidence: Optional[float] = None
