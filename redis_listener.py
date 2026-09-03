import json
import redis.asyncio as redis
from websocket import manager
from config import settings

r = redis.Redis.from_url(settings.REDIS_URL)

async def listener():
    pubsub = r.pubsub()
    await pubsub.subscribe("task_update")
    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                await manager.broadcast(data["project_id"], data["message"])
            except (json.JSONDecodeError, KeyError):
                continue  