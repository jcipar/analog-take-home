import asyncio
import random
import string
from typing import List

from broker import MessageBroker
from config import Config
from sms_message import SmsMessage, MessageBatch
from stats_collector import StatsCollector


class SmsMessageProducer:
    def __init__(
        self,
        conf: Config,
        broker: MessageBroker,
        stats_collector: StatsCollector,
    ) -> None:
        self.config = conf
        self.broker = broker
        self.stats_collector = stats_collector

    async def send_multiple_batches(self, batch_count: int, batch_size: int) -> None:
        for i in range(batch_count):
            batch = await self.generate_message_batch(batch_size)
            await self.broker.put_batch(batch)
            await self.stats_collector.log_produced(batch_size)
            # # TODO: tunable sleep frequency
            if (i+1) % 10 == 0:
                # Yield the processor so other coroutines can run
                await asyncio.sleep(0)

    async def generate_message_batch(self, batch_size: int) -> MessageBatch:
        messages: List[SmsMessage] = []
        for i in range(batch_size):
            messages.append(self.generate_random_message())
        return MessageBatch(messages)

    def generate_random_message(self) -> SmsMessage:
        dest = self._rand_phone_number()
        msg = self._rand_string(self.config.message_length)
        return SmsMessage(destination=dest, message=msg)

    def _rand_phone_number(self) -> str:
        # Assume a US phone number without country code
        return f"{self._rand_digits(3)}-{self._rand_digits(3)}-{self._rand_digits(4)}"

    def _rand_digits(self, k: int) -> str:
        return self._rand_string(k, string.digits)

    def _rand_string(self, k: int, charset: str = string.printable) -> str:
        return "".join(random.choices(charset, k=k))
