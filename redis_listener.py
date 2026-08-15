import json
import redis.asyncio as redis
from websocket import manager

r = redis.Redis(host="localhost", port=6379)

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