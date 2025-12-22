import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .schemas import EmailIntentState, IntentAnalysis
from .prompts import SYSTEM_PROMPT, SUBJECT_PROMPT, BODY_PROMPT
from .taxonomy import Intent

def get_model():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def analyze_subject(state: EmailIntentState) -> dict:
    model = get_model().with_structured_output(IntentAnalysis)
    
    intents_list = "\n".join([f"- {i.value}" for i in Intent])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", SUBJECT_PROMPT)
    ])
    
    chain = prompt | model
    result = await chain.ainvoke({
        "intents_list": intents_list,
        "subject": state.subject
    })
    
    return {
        "subject_intent": result.intent,
        "subject_confidence": result.confidence
    }

async def analyze_body(state: EmailIntentState) -> dict:
    model = get_model().with_structured_output(IntentAnalysis)
    
    # Truncate body if too long
    body = state.body[:2000]
    
    intents_list = "\n".join([f"- {i.value}" for i in Intent])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", BODY_PROMPT)
    ])
    
    chain = prompt | model
    result = await chain.ainvoke({
        "intents_list": intents_list,
        "body": body
    })
    
    return {
        "body_intent": result.intent,
        "body_confidence": result.confidence
    }

def resolve_intent(state: EmailIntentState) -> dict:
    # Logic for merging subject and body intent
    if state.subject_intent == state.body_intent:
        return {
            "final_intent": state.subject_intent,
            "final_confidence": max(state.subject_confidence or 0, state.body_confidence or 0)
        }
    
    # If different, prioritize higher confidence
    if (state.subject_confidence or 0) >= (state.body_confidence or 0):
        return {
            "final_intent": state.subject_intent,
            "final_confidence": state.subject_confidence
        }
    else:
        return {
            "final_intent": state.body_intent,
            "final_confidence": state.body_confidence
        }
