# Technical Report: Agent Worker Refactoring & Event-Driven Architecture

## 1. Executive Summary
This report outlines the technical strategy for refactoring the MailShieldAI worker pipeline into a fully Event-Driven Architecture (EDA). The goal is to decouple the **Ingest**, **Intent**, **Analysis**, and **Action** services, replacing direct HTTP inter-service communication with reliable **Redis Streams**. This ensures scalability, fault tolerance, and a clear separation of concerns.

## 2. Architecture Overview

### Current State
- **Ingest**: Receives Gmail push notifications.
- **Intent**: Process emails via Redis Stream (`emails:intent`), uses LangGraph for classification.
- **Analysis**: Currently acts as an HTTP service ("Decision Agent"), tightly coupled or invoked manually.
- **Action**: Currently acts as an HTTP service ("Action Agent"), invoked by Analysis.

### Future State (Pipeline)
The pipeline will flow linearly using Redis Streams:

`Ingest` -> `emails:intent` -> **Intent Worker** -> (Routing) -> `emails:analysis` OR `emails:action`

- **Intent Worker**: Acts as the intelligent router.
- **Analysis Worker**: Consumes `emails:analysis` -> Deep scans -> Pushes to `emails:action`.
- **Action Worker**: Consumes `emails:action` -> Enforces decisions (Labels/Spam) -> Marks `COMPLETED`.

## 3. Detailed Refactoring Plan

### 3.1 Shared Infrastructure (`packages/shared/`)
**Objective**: Define the communication backbone.

*   **`queue.py`**:
    *   Define stream constants:
        *   `EMAIL_INTENT_QUEUE = 'emails:intent'` (Existing)
        *   `EMAIL_ANALYSIS_QUEUE = 'emails:analysis'` (New)
        *   `EMAIL_ACTION_QUEUE = 'emails:action'` (New)
    *   Ensure universal access to `get_redis_client()` for all workers.

### 3.2 Intent Worker (`apps/worker/intent/`)
**Objective**: Upgrade to "Smart Router".

*   **Refactor `process_email`**:
    *   **Current**: Classifies and marks `COMPLETED`.
    *   **New Logic**:
        1.  Perform classification (LangGraph).
        2.  Calculate `RiskTier`.
        3.  **Routing Decision**:
            *   **IF** `RiskTier` is `THREAT` / `CAUTIOUS` **OR** Intent is `UNKNOWN`:
                *   Publish to `EMAIL_ANALYSIS_QUEUE`.
                *   Update Status: `ANALYZING`.
            *   **ELSE** (`SAFE`):
                *   Publish to `EMAIL_ACTION_QUEUE`.
                *   Update Status: `ACTION_PENDING`.

### 3.3 Analysis Worker (`apps/worker/analyses/`)
**Objective**: Convert to Async Stream Consumer.

*   **Structure**:
    *   Replace `FastAPI` ingress with `run_loop()` (similar to `intent/main.py`).
    *   Consumer Group: `analysis_workers`.
*   **Logic**:
    *   Listen on `EMAIL_ANALYSIS_QUEUE`.
    *   **Static Analysis**: Port existing attachment/extension checks.
    *   **Sandbox**: Port existing Hybrid Analysis / Mock integration.
    *   **DB Updates**: Write `analysis_result` and refine `risk_score` directly to the `EmailEvent` table.
    *   **Output**: Always publish to `EMAIL_ACTION_QUEUE` after analysis is done.

### 3.4 Action Worker (`apps/worker/action/`)
**Objective**: Convert to Async Stream Consumer.

*   **Structure**:
    *   Replace `FastAPI` ingress with `run_loop()`.
    *   Consumer Group: `action_workers`.
*   **Logic**:
    *   Listen on `EMAIL_ACTION_QUEUE`.
    *   **Fetch Context**: Load the fully analyzed `EmailEvent` from DB.
    *   **Labeling**: Port `gmail_labels.py` to apply labels based on final `RiskTier`:
        *   `RiskTier.THREAT` -> `MailShield/MALICIOUS`
        *   `RiskTier.CAUTIOUS` -> `MailShield/CAUTIOUS`
        *   `RiskTier.SAFE` -> `MailShield/SAFE`
    *   **Enforcement**: Move to Spam if malicious (configurable).
    *   **Completion**: Set `EmailEvent.status = COMPLETED`.

### 3.5 Ingest Worker (`apps/worker/ingest/`)
**Objective**: Standardization.

*   **Changes**:
    *   Maintain current Cloud Pub/Sub -> API entry point.
    *   Ensure all logs use `pythonjsonlogger` for consistency with new workers.

## 4. Database Impact
*   **`EmailEvent` Table**:
    *   Already updated to support `intent`, `risk_score`, `analysis_result`.
    *   No major schema changes required for this refactor, relying on status updates (`PENDING` -> `PROCESSING` -> `ANALYZING` -> `COMPLETED`).

## 5. Benefits
1.  **Resilience**: Workers can go offline without losing messages (Redis Streams persistence).
2.  **Scalability**: Each worker stage can be scaled independently (e.g., more Analysis workers for heavy loads).
3.  **Observability**: Clear flow of an email through discrete stages, traceable via DB status and logs.
