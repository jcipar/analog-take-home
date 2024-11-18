import asyncio

from config import Config
from sms_message import MessageBatch


class MessageBroker:
    def __init__(self, conf: Config) -> None:
        self.config = conf
        self.queue: asyncio.Queue[MessageBatch] = asyncio.Queue(self.config.max_queued_batches)

    async def put_batch(self, batch: MessageBatch) -> None:
        await self.queue.put(batch)

    def shutdown(self) -> None:
        self.queue.shutdown()

    async def get_batch(self) -> None | MessageBatch:
        try:
            return await self.queue.get()
        except asyncio.QueueShutDown:
            return None
