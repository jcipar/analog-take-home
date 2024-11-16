import numpy as np
import random
from typing import List
import pytest

import stats_collector


async def test_stats_collector() -> None:
    collector = stats_collector.StatsCollector()

    num_produced = random.randint(2, 20)
    num_sent = random.randint(2, 20)
    num_failed = random.randint(2, 20)
    times: List[float] = []

    await collector.log_produced(num_produced)
    for i in range(num_sent):
        t = max(0, random.normalvariate(1, 0.1))
        await collector.log_sent(t)
        times.append(t)
    for i in range(num_failed):
        t = max(0, random.normalvariate(1, 0.1))
        await collector.log_failed(t)
        times.append(t)

    stats = await collector.get_stats()
    assert stats.produced == num_produced
    assert stats.sent == num_sent
    assert stats.failed == num_failed
    assert stats.average_time == pytest.approx(np.mean(times))
