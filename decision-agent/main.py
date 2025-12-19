import os
import logging
import asyncio
import json
import requests
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, BackgroundTasks, status
from pydantic import BaseModel
from pythonjsonlogger import jsonlogger

# --- Configuration ---
FINAL_AGENT_URL = os.getenv("FINAL_AGENT_URL", "http://localhost:9001")
PORT = int(os.getenv("PORT", "8080"))

# --- Logging ---
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# --- Models ---
class AttachmentMetadata(BaseModel):
    filename: str
    mime_type: str
    size: int

class StructuredEmailPayload(BaseModel):
    message_id: str
    sender: str
    subject: str
    extracted_urls: List[str]
    attachment_metadata: List[AttachmentMetadata]

class SandboxResult(BaseModel):
    verdict: str # malicious, suspicious, clean, unknown
    score: int
    family: Optional[str] = None
    confidence: float = 0.0

class DecisionMetadata(BaseModel):
    provider: str
    timed_out: bool = False
    reason: Optional[str] = None

class UnifiedDecisionPayload(BaseModel):
    message_id: str
    static_risk_score: int
    sandboxed: bool
    sandbox_result: Optional[SandboxResult] = None
    decision_metadata: DecisionMetadata

# --- Risk Gate Logic (Pure, Deterministic) ---
RISKY_EXTENSIONS = {'.exe', '.scr', '.vbs', '.js', '.bat', '.iso', '.dll', '.ps1'}

def evaluate_static_risk(payload: StructuredEmailPayload) -> tuple[bool, str, int]:
    """
    Evaluates static indicators to decide if sandboxing is needed.
    Returns: (should_sandbox, reason, static_risk_score)
    """
    score = 0
    reasons = []
    should_sandbox = False

    # 1. Attachment Check
    for att in payload.attachment_metadata:
        ext = os.path.splitext(att.filename)[1].lower()
        if ext in RISKY_EXTENSIONS:
            score += 70
            reasons.append(f"Risky extension {ext}")
            should_sandbox = True
        elif att.mime_type == "application/zip":
            score += 30
            reasons.append("Archive attachment")
            should_sandbox = True # Inspecting zips is standard

    # 2. URL Check (Basic heuristics for Phase 2A)
    if len(payload.extracted_urls) > 0:
        score += 10 # Presence of URLs
        # In Phase 2B, we might check TLDs or domains
        # For now, if we have > 3 URLs, it's slightly suspicious
        if len(payload.extracted_urls) > 3:
            score += 20
            reasons.append("Many URLs")
            should_sandbox = True # Sandbox URL scanning 

    # Normalize score
    score = min(score, 100)
    
    reason_str = "; ".join(reasons) if reasons else "Low static risk"
    
    # Fail-safe: if score is high but somehow didn't trigger sandbox, force it
    if score > 50:
        should_sandbox = True
        
    return should_sandbox, reason_str, score

# --- Mock Sandbox Logic (Phase 2A) ---
async def simulate_sandbox_scan(payload: StructuredEmailPayload) -> SandboxResult:
    """Simulates a call to Hybrid Analysis."""
    logger.info(f"Simulating sandbox scan for {payload.message_id}...")
    await asyncio.sleep(2.0) # Simulate network/processing delay
    
    # Deterministic mock result based on subject for testing
    if "urgent" in payload.subject.lower() or "invoice" in payload.subject.lower():
         return SandboxResult(verdict="malicious", score=90, family="MockTrojan", confidence=0.99)
    
    return SandboxResult(verdict="clean", score=0, confidence=1.0)

# --- Async Processing ---
async def process_analysis(payload: StructuredEmailPayload):
    """
    Orchestrates the analysis logic:
    Risk Gate -> (Optional) Sandbox -> Unified Output -> Forward
    """
    logger.info(f"Starting analysis for {payload.message_id}")
    
    # 1. Risk Gate
    should_sandbox, reason, static_score = evaluate_static_risk(payload)
    logger.info(f"Risk Gate Result: sandboxed={should_sandbox} score={static_score} reason='{reason}'")
    
    sandbox_res = None
    provider = "none"
    
    # 2. Sandbox (if needed)
    if should_sandbox:
        try:
            # Phase 2A: Mock call
            # Phase 2B: Real HA call
            provider = "mock-hybrid-analysis"
            sandbox_res = await simulate_sandbox_scan(payload)
        except Exception as e:
            logger.error(f"Sandbox failed for {payload.message_id}: {e}", exc_info=True)
            # Fail Open
            sandbox_res = SandboxResult(verdict="unknown", score=50, family="Error", confidence=0.0)
            
    # 3. Build Unified Payload
    unified = UnifiedDecisionPayload(
        message_id=payload.message_id,
        static_risk_score=static_score,
        sandboxed=should_sandbox,
        sandbox_result=sandbox_res,
        decision_metadata=DecisionMetadata(
            provider=provider,
            reason=reason
        )
    )
    
    # 4. Forward to Final Agent
    forward_to_final_agent(unified)

def forward_to_final_agent(payload: UnifiedDecisionPayload):
    try:
        logger.info("Forwarding decision to Final Agent", extra={"message_id": payload.message_id, "verdict": payload.sandbox_result.verdict if payload.sandbox_result else "skipped"})
        resp = requests.post(FINAL_AGENT_URL, json=payload.model_dump(), timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to forward decision for {payload.message_id}: {e}")

# --- FastAPI App ---
app = FastAPI(title="Decision Agent")

@app.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_email(payload: StructuredEmailPayload, background_tasks: BackgroundTasks):
    """
    Ingress endpoint.
    Returns 202 Accepted immediately.
    Schedules analysis in background.
    """
    logger.info("Received analysis request", extra={"message_id": payload.message_id})
    background_tasks.add_task(process_analysis, payload)
    return {"status": "accepted", "message_id": payload.message_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
