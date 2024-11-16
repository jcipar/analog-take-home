import asyncio
import math
from typing import List

from stats_collector import StatsCollector
from broker import MessageBroker
from sender import Sender
from producer import SmsMessageProducer
import time
import gc
from typing import Dict, Any


async def main() -> None:
    collector = StatsCollector()
    # producer = SmsMessageProducer(broker, collector)
    # prod_task = asyncio.create_task(produce_then_stop(broker, producer, 1_000_000, 1))
    num_messages = 7_000_000
    num_producers = 1
    batch_size = 10
    num_batches = math.ceil(num_messages / num_producers / batch_size)
    num_consumers = 50_000
    broker = MessageBroker(num_consumers)  # FIXME: config for this
    print(f"Producing {num_messages} messaging in {num_producers} producers.")
    print(f"Batch size is {batch_size}, batch count {num_batches}")
    prod_task = parallel_producers(
        num_producers, collector, broker, num_batches, batch_size
    )
    print("Started producers")
    print_task = asyncio.create_task(print_stats(collector, 2))
    print("Started monitor")
    consume_task = asyncio.create_task(
        parallel_senders(num_consumers, collector, broker)
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

async def print_stats(collector: StatsCollector, sleep_time: float) -> None:
    last_done = 0
    last_time = time.time()
    while True:
        try:
            await asyncio.sleep(sleep_time)
            stats = await collector.get_stats()
            print(f"\nProduced: {stats.produced}")
            print(f"Error: {stats.failed}")
            print(f"Success: {stats.sent}")
            print(f"Avg time: {stats.average_time:.3f}")
            print(f"Processing: {stats.dequeued - stats.sent - stats.failed}")
            print(f"Pending: {stats.produced - stats.dequeued}")
            done = stats.failed + stats.sent
            now = time.time()
            print(f"Throughtput: {(done - last_done) / (now - last_time):.1f} msgs/s")
            last_done = done
            last_time = now
        except asyncio.CancelledError:
            break


async def produce_then_stop(
    broker: MessageBroker,
    producer: SmsMessageProducer,
    batch_count: int,
    batch_size: int,
) -> None:
    await producer.send_multiple_batches(batch_count, batch_size)


if __name__ == "__main__":
    asyncio.run(main())
