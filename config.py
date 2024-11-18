from dataclasses import dataclass
import tomllib
from typing import Dict, Any


@dataclass(frozen=True)
class Config:
    # TODO: This is enough for a demo, but we would probably
    # want something with a bit of namespacing for a real
    # application.
    message_count: int = 1000
    min_message_length: int = 100
    max_message_length: int = 100
    producer_count: int = 1
    batch_size: int = 1
    sender_count: int = 1
    send_time_mean: float = 1.0
    send_time_stddev: float = 0.1
    send_failure_rate: float = 0.1
    print_frequency: int = 2
    max_queued_batches: int = 1


def read_config(filename: str = "config.toml") -> Config:
    with open(filename, "rb") as fp:
        data = tomllib.load(fp)
        return _parse_config(data)


def _read_config_from_string(config_str: str) -> Config:
    # This method only exists to make testing _parse_config easier.
    data = tomllib.loads(config_str)
    return _parse_config(data)


def _parse_config(raw_config: Dict[str, Any]) -> Config:
    def get_int(section: str, name: str, default: int) -> int:
        return int(raw_config.get(section, {}).get(name, default))

    def get_float(section: str, name: str, default: float) -> float:
        return float(raw_config.get(section, {}).get(name, default))

    return Config(
        message_count=get_int("messages", "message_count", 1_000),
        min_message_length=get_int("messages", "min_message_length", 100),
        max_message_length=get_int("messages", "max_message_length", 100),
        producer_count=get_int("producer", "producer_count", 1),
        batch_size=get_int("producer", "batch_size", 1),
        sender_count=get_int("sender", "sender_count", 50_000),
        send_time_mean=get_float("sender", "send_time_mean", 1.0),
        send_time_stddev=get_float("sender", "send_time_stddev", 0.1),
        send_failure_rate=get_float("sender", "send_failure_rate", 0.1),
        print_frequency=get_int("monitor", "print_frequency", 2),
        max_queued_batches=get_int("broker", "max_queued_batches", 10_000)
    )
