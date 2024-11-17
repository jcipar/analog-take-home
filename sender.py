import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
import random

from broker import MessageBroker
from config import Config
from sms_message import SmsMessage
from stats_collector import StatsCollector

log = logging.getLogger(__name__)


class SendResult(Enum):
    SUCCESS = (0,)
    FAILURE = (1,)


class Sender:
    def __init__(
        self,
        conf: Config,
        broker: MessageBroker,
        collector: StatsCollector,
    ) -> None:
        self.config = conf
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
            random.normalvariate(
                self.config.send_time_mean, self.config.send_time_stddev
            ),
            0,
        )
        await asyncio.sleep(send_time)
        if random.random() < self.config.send_failure_rate:
            await self.collector.log_failed(send_time)
            log.debug("Send failed")
            return SendResult.FAILURE
        await self.collector.log_sent(send_time)
        return SendResult.SUCCESS
