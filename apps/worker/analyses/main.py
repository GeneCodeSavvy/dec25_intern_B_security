from __future__ import annotations

import asyncio
import random
import os
import uuid
import logging
from typing import Optional
from datetime import datetime, timezone
import json

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from pythonjsonlogger import json as jsonlogger

from packages.shared.database import get_session, init_db
from packages.shared.constants import EmailStatus
from packages.shared.models import EmailEvent
from packages.shared.queue import get_redis_client, EMAIL_ANALYSIS_QUEUE
from packages.shared.types import AttachmentMetadata

# --- Logging ---
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt='%(asctime)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


async def process_email_analysis(
    session: AsyncSession,
    email: EmailEvent,
    payload: dict,
) -> bool:
    """Process a single email event through the analysis agent."""
    try:
        # NOTE: This is where the actual sandboxing logic would go.
        # For now, we'll just simulate a result.
        logger.info(f'Starting sandbox analysis for email {email.id}')
        await asyncio.sleep(5)  # Simulate network latency

        # Reconstruct attachment metadata for logging/display if needed
        attachments = [AttachmentMetadata.model_validate_json(att) for att in payload.get('attachment_metadata', [])]

        sandbox_result = {
            'verdict': 'clean',
            'score': 10,
            'details': 'Simulated scan found no threats.',
            'urls_scanned': payload.get('extracted_urls', []),
            'attachments_scanned': [att.filename for att in attachments],
        }

        email.sandbox_result = sandbox_result
        email.status = EmailStatus.COMPLETED
        email.updated_at = datetime.now(timezone.utc)

        session.add(email)
        await session.commit()
        await session.refresh(email)
        logger.info(f'Sandbox analysis completed for email {email.id}')
        return True

    except Exception as e:
        logger.error(f'Error in process_email_analysis: {e}')
        try:
            email.status = EmailStatus.FAILED
            session.add(email)
            await session.commit()
        except Exception as commit_err:
            logger.error(f'Failed to persist FAILED status: {commit_err}')
        return False


async def run_loop() -> None:
    """Main worker loop using Redis Streams Consumer Groups."""
    await init_db()
    redis = await get_redis_client()

    group_name = 'analysis_workers'
    consumer_name = f'worker-{random.randint(1000, 9999)}'

    try:
        await redis.xgroup_create(EMAIL_ANALYSIS_QUEUE, group_name, id='0', mkstream=True)
        logger.info(f'Consumer group {group_name} created.')
    except Exception as e:
        if 'BUSYGROUP' not in str(e):
            logger.warning(f'Error creating consumer group: {e}')

    logger.info(f'Worker {consumer_name} started. Listening on {EMAIL_ANALYSIS_QUEUE}...')

    while True:
        try:
            streams = await redis.xreadgroup(
                group_name,
                consumer_name,
                {EMAIL_ANALYSIS_QUEUE: '>'},
                count=1,
                block=5000,
            )

            if not streams:
                continue

            for stream_name, messages in streams:
                for message_id, payload in messages:
                    email_id_str = payload.get('email_id')

                    if not email_id_str:
                        logger.warning(f'Invalid payload in message {message_id}')
                        await redis.xack(EMAIL_ANALYSIS_QUEUE, group_name, message_id)
                        continue

                    try:
                        email_id = uuid.UUID(email_id_str)
                    except (ValueError, TypeError):
                        logger.error(f"Malformed email ID '{email_id_str}' in message {message_id}")
                        await redis.xack(EMAIL_ANALYSIS_QUEUE, group_name, message_id)
                        continue

                    logger.info(f'Processing message {message_id} (Email ID: {email_id})')

                    processed_successfully = False
                    from contextlib import asynccontextmanager

                    @asynccontextmanager
                    async def session_scope():
                        async for s in get_session():
                            yield s
                            break

                    async with session_scope() as session:
                        try:
                            query = select(EmailEvent).where(EmailEvent.id == email_id)
                            result = await session.exec(query)
                            email = result.first()

                            if not email:
                                logger.warning(f'Email {email_id} not found.')
                                await redis.xack(EMAIL_ANALYSIS_QUEUE, group_name, message_id)
                                continue

                            processed_successfully = await process_email_analysis(session, email, payload)
                        except Exception as inner_e:
                            logger.error(f'Error processing {email_id}: {inner_e}')

                    if processed_successfully:
                        await redis.xack(EMAIL_ANALYSIS_QUEUE, group_name, message_id)
                        logger.info(f'Acknowledged message {message_id}')

        except Exception as e:
            logger.error(f'Worker loop error: {e}')
            await asyncio.sleep(1)


def main() -> None:
    """Entry point for the worker service."""
    logger.info('Starting analysis worker...')
    asyncio.run(run_loop())


if __name__ == '__main__':
    main()
