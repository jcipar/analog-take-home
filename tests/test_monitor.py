from monitor import Monitor
from config import Config
from stats_collector import MessagingStats, StatsCollector


def test_stats_to_string() -> None:
    conf = Config()
    collector = StatsCollector()
    monitor = Monitor(conf, collector, now=10)

    stats = MessagingStats(
        produced=100, dequeued=25, sent=10, failed=1, average_time=1.2
    )

    expected = """
Total Produced: 100
Enqueued: 75
Processing: 14
Finished: 11
Failures: 10 sent, 1 failed. 9.1% failure rate.
Throughput: 5.5 msgs/s overall, 5.5 msgs/s recently.
Latency: 1.2 s/msg.
Elapsed: 2.0 s total run time.
"""

    res = monitor._stats_to_string(stats, now=12)
    assert res == expected
