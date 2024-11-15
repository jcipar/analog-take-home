import asyncio

from sms_message import MessageBatch


class MessageBroker:
    def __init__(self, max_pending_batches: int) -> None:
        self.queue: asyncio.Queue[MessageBatch] = asyncio.Queue(max_pending_batches)

    async def put_batch(self, batch: MessageBatch) -> None:
        await self.queue.put(batch)

    async def get_batch(self) -> MessageBatch:
        return await self.queue.get()
