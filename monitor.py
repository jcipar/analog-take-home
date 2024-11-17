import asyncio
import time
from typing import Dict

from config import Config
from stats_collector import MessagingStats, StatsCollector


class Monitor:
    def __init__(
        self, conf: Config, stats_collector: StatsCollector, now: float = time.time()
    ) -> None:
        self.config = conf
        self.stats_collector = stats_collector
        self.start_time = now
        self.last_finished = 0
        self.last_time = now

    def run(self) -> asyncio.Task[None]:
        return asyncio.create_task(self._run())

    async def _run(self) -> None:
        while True:
            try:
                await asyncio.sleep(self.config.print_frequency)
                stats = await self.stats_collector.get_stats()
                now = time.time()

                msg = self._stats_to_string(stats, now)
                print(msg)
            
                finished = stats.sent + stats.failed
                self.last_time = now
                self.last_finished = finished
            except asyncio.CancelledError:
                break


    def _stats_to_string(self, stats: MessagingStats, now: float) -> str:
        detailed_monitor_format = """
Total Produced: {produced}
Enqueued: {enqueued}
Processing: {processing}
Finished: {finished}
Failures: {sent} sent, {failed} failed. {f_rate_pct:.1f}% failure rate.
Throughput: {overall_tput:.1f} msgs/s overall, {recent_tput:.1f} msgs/s recently.
Latency: {latency} s/msg.
Elapsed: {elapsed:.1f} s total run time.
"""
        finished = stats.sent + stats.failed
        failure_rate_percent = stats.failed * 100.0 / finished

        total_elapsed = now - self.start_time
        recent_elapsed = now - self.last_time

        recent_finished = finished - self.last_finished
        throughput = finished / total_elapsed
        recent_throughput = recent_finished / recent_elapsed


        stats_dict: Dict[str, int | float] = {
            "produced": stats.produced,
            "finished": stats.sent + stats.failed,
            "sent": stats.sent,
            "failed": stats.failed,
            "f_rate_pct": failure_rate_percent,
            "overall_tput": throughput,
            "recent_tput": recent_throughput,
            "elapsed": total_elapsed,
            "enqueued": stats.produced - stats.dequeued,
            "processing": stats.dequeued - finished,
            "latency": stats.average_time,
        }
        return detailed_monitor_format.format(**stats_dict)
