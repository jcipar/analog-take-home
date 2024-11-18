import asyncio
import math
from typing import List

import broker
import config
import monitor
import producer
import sender
import stats_collector


class Application:
    def __init__(self, config_file_name: str) -> None:
        self.config_file_name = config_file_name
        self.config: None | config.Config = None

    async def run(self) -> None:
        self.config = config.read_config(self.config_file_name)
        self.stats_collector = stats_collector.StatsCollector()
        # TODO: add a separate config for message broker queue size
        self.broker = broker.MessageBroker(self.config)
        self.monitor = monitor.Monitor(self.config, self.stats_collector)

        self.monitor_task = self.monitor.run()
        self.produce_task = self._start_producers()
        self.send_task = self._start_senders()

        await asyncio.gather(self.produce_task, self.send_task, return_exceptions=True)
        self.monitor_task.cancel()
        

    async def _start_producers(self) -> None:
        # Start parallel producers. When all producers have finished,
        # shut down the broker to signal that no more
        assert self.config is not None
        tasks: List[asyncio.Task[None]] = []
        batch_count = math.ceil(
            self.config.message_count
            / self.config.batch_size
            / self.config.producer_count
        )
        for i in range(self.config.producer_count):
            prod = producer.SmsMessageProducer(
                self.config, self.broker, self.stats_collector
            )
            task = asyncio.create_task(prod.send_multiple_batches(batch_count, self.config.batch_size))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
        self.broker.shutdown()

    async def _start_senders(self) -> None:
        assert self.config is not None
        tasks: List[asyncio.Task[None]] = []
        for i in range(self.config.sender_count):
            send = sender.Sender(self.config, self.broker, self.stats_collector)
            task = asyncio.create_task(send.consume_messages())
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
        
