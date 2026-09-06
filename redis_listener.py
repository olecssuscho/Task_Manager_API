import json
import redis.asyncio as redis
from websocket import manager
from config import settings
import logging

logger = logging.getLogger(__name__)
r = redis.Redis.from_url(settings.REDIS_URL)

async def listener():
    pubsub = r.pubsub()
    await pubsub.subscribe("task_update")
    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                await manager.broadcast(data["project_id"], data["message"])
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Skipping malformed pubsub message: {e}, raw data {message["data"]}")
                continue  