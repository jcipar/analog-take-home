import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
import random

from broker import MessageBroker
from sms_message import SmsMessage
from stats_collector import StatsCollector

log = logging.getLogger(__name__)


class SendResult(Enum):
    SUCCESS = (0,)
    FAILURE = (1,)


@dataclass
class SendConfig:
    failure_rate: float = 0.1
    mean_send_time: float = 1.0
    std_send_time: float = 0.1


class Sender:
    def __init__(self, broker: MessageBroker, collector: StatsCollector, config: SendConfig | None = None) -> None:
        if config is None:
            self.config = SendConfig()
        else:
            self.config = config
        self.broker = broker
        self.collector = collector

    async def consume_messages(self) -> None:
        while True:
            maybe_batch = await self.broker.get_batch()
            if maybe_batch is None:
                break
            await self.collector.log_dqueued(len(maybe_batch.messages))
            for msg in maybe_batch.messages:
                await self.send_message(msg)

    async def send_message(self, msg: SmsMessage) -> SendResult:
        # Sleep first: assume even a failed send takes time
        send_time = max(
            random.normalvariate(self.config.mean_send_time, self.config.std_send_time),
            0,
        )
        await asyncio.sleep(send_time)
        if random.random() < self.config.failure_rate:
            await self.collector.log_failed(send_time)
            log.debug("Send failed")
            return SendResult.FAILURE
        await self.collector.log_sent(send_time)
        return SendResult.SUCCESS
