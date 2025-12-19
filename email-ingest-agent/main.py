import os
import base64
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from pythonjsonlogger import jsonlogger

# --- Configuration ---
# In production, these would be loaded from Secret Manager or Env Vars
DECISION_AGENT_URL = os.getenv("DECISION_AGENT_URL", "http://localhost:9000") # Default for local testing
PORT = int(os.getenv("PORT", "8080"))

# --- Logging Setup ---
# Structured JSON logging for Cloud Logging compatibility
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# --- FastAPI App ---
app = FastAPI(title="Email Ingest Agent")

# --- Models ---
class PubSubMessage(BaseModel):
    data: str
    messageId: str
    publishTime: str
    attributes: Optional[Dict[str, str]] = None

class PubSubBody(BaseModel):
    message: PubSubMessage
    subscription: str

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

# --- Helpers ---
def decode_pubsub_data(data_base64: str) -> Dict[str, Any]:
    """Decodes the Base64 encoded Pub/Sub message data."""
    try:
        decoded_bytes = base64.b64decode(data_base64)
        decoded_str = decoded_bytes.decode("utf-8")
        return json.loads(decoded_str)
    except Exception as e:
        logger.error(f"Failed to decode Pub/Sub data: {e}", extra={"error": str(e)})
        # We raise here because if we can't read the message, we can't process it.
        # However, for Pub/Sub, we might still want to ACK to prevent infinite retries of bad data.
        # But for now, we'll let the handler catch it.
        raise ValueError(f"Invalid Pub/Sub data: {e}")

def mock_gmail_processing(email_address: str, history_id: int) -> StructuredEmailPayload:
    """
    Phase 1A Mock: Simulate Gmail API fetching and extraction.
    In Phase 1B, this will be replaced with real Gmail API calls.
    """
    logger.info(f"Mock processing for {email_address} with historyId {history_id}")
    
    return StructuredEmailPayload(
        message_id=f"mock-msg-{history_id}",
        sender="sender@example.com",
        subject="Mock Suspicious Email",
        extracted_urls=["http://malware-example.com/login", "https://fishing-site.com"],
        attachment_metadata=[
            AttachmentMetadata(filename="invoice.pdf", mime_type="application/pdf", size=10240),
            AttachmentMetadata(filename="evil.exe", mime_type="application/x-msdownload", size=512)
        ]
    )

def forward_to_decision_agent(payload: StructuredEmailPayload):
    """
    Forwards the structured payload to the Decision Agent.
    Catches all exceptions to ensure we return 200 to Pub/Sub.
    """
    try:
        logger.info("Forwarding payload to Decision Agent", extra={"url": DECISION_AGENT_URL, "payload": payload.model_dump()})
        response = requests.post(
            DECISION_AGENT_URL,
            json=payload.model_dump(),
            timeout=5 # Short timeout for "fire-and-forget" feel
        )
        response.raise_for_status()
        logger.info("Successfully forwarded to Decision Agent", extra={"status_code": response.status_code})
    except requests.exceptions.RequestException as e:
        # CRITICAL: We log the error but do NOT raise. 
        # We must ACK the Pub/Sub message so it doesn't redeliver indefinitely.
        logger.error(f"Failed to forward to Decision Agent: {e}", extra={"error": str(e)})


# --- Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "ok"}

@app.post("/")
async def receive_pubsub_push(body: PubSubBody):
    """
    Handle incoming Pub/Sub push messages.
    Returns 200 OK to acknowledge receipt, even if downstream fails.
    """
    try:
        # 1. Log receipt
        logger.info("Received Pub/Sub message", extra={"messageId": body.message.messageId})

        # 2. Decode the inner data
        # Expecting: {"emailAddress": "...", "historyId": ...}
        # Note: Actual Pub/Sub for Gmail push might just have historyId, but we'll stick to our plan's contract for now.
        decoded_data = decode_pubsub_data(body.message.data)
        
        email_address = decoded_data.get("emailAddress", "unknown@example.com")
        history_id = decoded_data.get("historyId", 0)

        if not history_id:
            logger.warning("No historyId found in message", extra={"data": decoded_data})
            # Still ACK
            return {"status": "acked", "reason": "missing_history_id"}

        # 3. Process (Mock for now)
        structured_payload = mock_gmail_processing(email_address, history_id)

        # 4. Forward (Fire-and-forget semantics)
        forward_to_decision_agent(structured_payload)

        # 5. ACK
        return {"status": "success"}

    except Exception as e:
        # Catch-all to ensure we don't return 500 to Pub/Sub unless it's a transient issue we WANT to retry.
        # For malformed data, we should ACK (return 200) to stop retries.
        # For this design, we'll log exception and return 200 to be safe/stable in Cloud Run.
        logger.exception("Unexpected error processing message")
        return {"status": "error_handled"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
