import redis
from core.config import settings
from typing import Callable, Any, Dict
import json

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, password=settings.REDIS_PASSWORD)

    def ensure_group(self):
        try:
            self.client.xgroup_create(name=settings.REDIS_STREAM_KEY, groupname=settings.REDIS_CONSUMER_GROUP, id='0', mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                pass  # Group already exists
            else:
                raise e
    
    def produce_message(self, payload: dict):
        payload_json = json.dumps(payload)
        self.client.xadd(name=settings.REDIS_STREAM_KEY, fields={"data": payload_json}, maxlen=1000, approximate=True)

    def consume_messages(self, consumername: str, count: int = 1, block: int = 5000):
        self.ensure_group()

        while True:
            messages = self.client.xreadgroup(groupname=settings.REDIS_CONSUMER_GROUP, consumername=consumername, count=count, block=block, streams={settings.REDIS_STREAM_KEY: '>'})
            if not messages:
                continue

            for stream, msgs in messages:
                for msg_id, msg_data in msgs:
                    print(f"redis process {msg_id}")
                    data = json.loads(msg_data[b'data'])

                    self.client.xack(settings.REDIS_STREAM_KEY, settings.REDIS_CONSUMER_GROUP, msg_id)

    def run(
        self,
        handler: Callable[[str, Dict[str, Any]], bool],
    ) -> None:
        self.ensure_group()

        while True:
            messages = self.client.xreadgroup(groupname=settings.REDIS_CONSUMER_GROUP, consumername="consumer-1", count=1, block=5000, streams={settings.REDIS_STREAM_KEY: '>'})
            if not messages:
                continue

            for stream, msgs in messages:
                for msg_id, msg_data in msgs:
                    data = json.loads(msg_data[b'data'])
                    print(f"Consumed {msg_id}")

                    success = handler(msg_id, data)
                    if success:
                        self.client.xack(settings.REDIS_STREAM_KEY, settings.REDIS_CONSUMER_GROUP, msg_id)
                    else:
                        print(f"Handler failed for message {msg_id}, not acknowledging.")
