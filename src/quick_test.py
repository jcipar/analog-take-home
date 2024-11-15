import asyncio
import logging
import numpy as np
from matplotlib import pyplot as plt
import random
import sys
import time

from typing import List, Tuple

# This script is a quick-and-dirty scalability test.
# It is meant to evaluate what kind of performance we can expect from a
# relatively naive solution using Python ascynio.

FAILURE_RATE: float = 0.0
MEAN_SEND_TIME: float = 1.0
STD_SEND_TIME: float = 0.1
LOG_LEVEL = logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(levelname)s: %(filename)s:%(lineno)d %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


async def send_message(msg: str) -> bool:
    if random.random() < FAILURE_RATE:
        log.debug("Send failed")
        return False
    send_time = max(random.normalvariate(MEAN_SEND_TIME, STD_SEND_TIME), 0)
    await asyncio.sleep(send_time)
    log.debug(f"Sent {msg}")
    return True


async def sender_process(msg_queue: asyncio.Queue[str]) -> None:
    while True:
        try:
            msg = await msg_queue.get()
        except Exception as e:
            log.debug(f"get returned {e}")
            break
        await send_message(msg)


async def do_test(num_senders: int) -> Tuple[int, int, float]:
    msg_count = num_senders * 10
    max_pending = num_senders

    queue: asyncio.Queue[str] = asyncio.Queue(max_pending)

    tasks: List[asyncio.Task[None]] = []
    for i in range(num_senders):
        task = asyncio.create_task(sender_process(queue))
        tasks.append(task)

    start_time = time.time()
    for i in range(msg_count):
        await queue.put("Hello")
    queue.shutdown()
    await asyncio.gather(*tasks, return_exceptions=True)
    elapsed_time = time.time() - start_time

    log.info(
        f"Sending {msg_count} message with {num_senders} senders took {elapsed_time:.3f} seconds."
    )
    log.info(
        f"{(msg_count/elapsed_time):.3f} msgs/s. {(msg_count / num_senders / elapsed_time):.3f} msgs/s/sender."
    )
    return (msg_count, num_senders, elapsed_time)


async def main() -> None:
    log.info("Starting main()")

    US_POPULATION: int = 337_421_200
    results: List[Tuple[int, int, float]] = []
    num_senders = 1
    while num_senders < 3e6:
        res = await do_test(num_senders)
        results.append(res)
        num_senders *= 2

    res_array = np.array(results)
    senders = res_array[:, 1]
    throughput = res_array[:, 0] / res_array[:, 2]
    throughput_per = throughput / res_array[:, 1]
    us_pop_send = US_POPULATION / throughput / 3600

    plt.figure()
    plt.xscale("log")
    plt.yscale("log")
    plt.grid()
    plt.plot(senders, throughput, ".-")
    plt.title("Throughput scaling")
    plt.xlabel("Number of senders (log scale)")
    plt.ylabel("Total throughput (msgs/s)")
    plt.savefig("throughput.png")

    plt.figure()
    plt.xscale("log")
    plt.yscale("log")
    plt.grid()
    plt.title("Efficiency scaling")
    plt.plot(senders, throughput_per, ".-")
    plt.xlabel("Number of senders (log scale)")
    plt.ylabel("Throughput per sender (msgs/s/sender)")
    plt.savefig("throughput-per.png")

    plt.figure()
    plt.xscale("log")
    plt.yscale("log")
    plt.grid()
    plt.title("Large scale cost")
    plt.plot(senders, us_pop_send, ".-")
    plt.xlabel("Number of senders (log scale)")
    plt.ylabel("Time to message everyone in the US (hours)")
    plt.savefig("us-pop-send.png")


if __name__ == "__main__":
    asyncio.run(main())
