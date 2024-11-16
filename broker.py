import asyncio

from sms_message import MessageBatch


class MessageBroker:
    def __init__(self, max_pending_batches: int) -> None:
        self.max_pending_batches = max_pending_batches
        self.queue: asyncio.Queue[MessageBatch] = asyncio.Queue(max_pending_batches)

    async def put_batch(self, batch: MessageBatch) -> None:
        await self.queue.put(batch)

    def shutdown(self) -> None:
        self.queue.shutdown()

    async def get_batch(self) -> None | MessageBatch:
        try:
            return await self.queue.get()
        except asyncio.QueueShutDown:
            return None
