from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SmsMessage:
    destination: str
    message: str


@dataclass(frozen=True)
class MessageBatch:
    messages: List[SmsMessage]
