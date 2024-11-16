from dataclasses import dataclass


@dataclass(frozen=True)
class MessagingStats:
    produced: int
    dequeued: int
    sent: int
    failed: int
    average_time: float


class StatsCollector:
    def __init__(self) -> None:
        self.produced: int = 0
        self.dequeued = 0
        self.sent: int = 0
        self.failed: int = 0
        self.time: float = 0.0

    # These methods don't really need to be async in this
    # toy implementation, but I'm imagining a distributed
    # implementation where the stats collector may be logging
    # to a database or some other external service. In that
    # case they should be async.
    async def log_produced(self, batch_size: int) -> None:
        self.produced += batch_size

    async def log_dqueued(self, batch_size: int) -> None:
        self.dequeued += batch_size

    async def log_sent(self, send_time: float) -> None:
        self.sent += 1
        self.time += send_time

    async def log_failed(self, send_time: float) -> None:
        self.failed += 1
        self.time += send_time

    async def get_stats(self) -> MessagingStats:
        total_count = self.sent + self.failed
        if total_count > 0:
            avg = self.time / total_count
        else:
            avg = 0
        return MessagingStats(
            produced=self.produced,
            dequeued=self.dequeued,
            sent=self.sent,
            failed=self.failed,
            average_time=avg,
        )
