import random
import string
from typing import List

from sms_message import SmsMessage, MessageBatch
from stats_collector import StatsCollector


class SmsMessageProducer:
    def __init__(self, stats_collector: StatsCollector, message_length:int =100) -> None:
        self.message_length = 100
        self.stats_collector = stats_collector

    def generate_message_batch(self, batch_size: int) -> MessageBatch:
        messages: List[SmsMessage] = []
        for i in range(batch_size):
            messages.append(self.generate_random_message())
        return MessageBatch(messages)

    def generate_random_message(self) -> SmsMessage:
        dest = self._rand_phone_number()
        msg = self._rand_string(self.message_length)
        return SmsMessage(destination=dest, message=msg)

    def _rand_phone_number(self) -> str:
        # Assume a US phone number without country code
        return f"{self._rand_digits(3)}-{self._rand_digits(3)}-{self._rand_digits(4)}"

    def _rand_digits(self, k: int) -> str:
        return self._rand_string(k, string.digits)

    def _rand_string(self, k: int, charset: str = string.printable) -> str:
        return "".join(random.choices(charset, k=k))
