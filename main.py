import asyncio
import math
from typing import List

import config
from stats_collector import StatsCollector
from broker import MessageBroker
from sender import Sender
from producer import SmsMessageProducer
from monitor import Monitor
import time


async def main() -> None:
    conf = config.read_config()
    num_batches = math.ceil(conf.message_count / conf.batch_size / conf.producer_count)
    collector = StatsCollector()
    # producer = SmsMessageProducer(broker, collector)
    # prod_task = asyncio.create_task(produce_then_stop(broker, producer, 1_000_000, 1))
    broker = MessageBroker(conf.sender_count)
    monitor = Monitor(conf, collector)
    print(
        f"Producing {conf.message_count} messaging in {conf.producer_count} producers."
    )
    print(f"Batch size is {conf.batch_size}, batch count {num_batches}")
    prod_task = parallel_producers(
        conf.producer_count, collector, broker, num_batches, conf.batch_size
    )
    print("Started producers")
    print_task = monitor.run()
    print("Started monitor")
    consume_task = asyncio.create_task(
        parallel_senders(conf.sender_count, collector, broker)
    )
    print("Started consumers")
    await asyncio.gather(prod_task, consume_task, return_exceptions=True)
    print_task.cancel()
    print("DONE!")


async def parallel_senders(
    num_senders: int, collector: StatsCollector, broker: MessageBroker
) -> None:
    tasks: List[asyncio.Task[None]] = []
    for i in range(num_senders):
        sender = Sender(broker, collector)
        task = asyncio.create_task(sender.consume_messages())
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)


async def parallel_producers(
    num_producers: int,
    collector: StatsCollector,
    broker: MessageBroker,
    batch_count: int,
    batch_size: int,
) -> None:
    tasks: List[asyncio.Task[None]] = []
    for i in range(num_producers):
        producer = SmsMessageProducer(broker, collector)
        task = asyncio.create_task(
            produce_then_stop(broker, producer, batch_count, batch_size)
        )
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)
    broker.shutdown()


async def produce_then_stop(
    broker: MessageBroker,
    producer: SmsMessageProducer,
    batch_count: int,
    batch_size: int,
) -> None:
    await producer.send_multiple_batches(batch_count, batch_size)


if __name__ == "__main__":
    asyncio.run(main())
