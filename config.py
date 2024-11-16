from dataclasses import dataclass
import tomllib
from typing import Dict, Any


@dataclass(frozen=True)
class Config:
    # TODO: This is enough for a demo, but we would probably
    # want something with a bit of namespacing for a real
    # application.
    message_count: int
    message_length: int
    producer_count: int
    batch_size: int
    sender_count: int
    send_time_mean: float
    send_time_stddev: float
    print_frequency: int


def read_config(filename: str = "config.toml") -> Config:
    with open(filename, "rb") as fp:
        data = tomllib.load(fp)
        return _parse_config(data)


def _read_config_from_string(config_str: str) -> Config:
    # This method only exists to make testing _parse_config easier.
    data = tomllib.loads(config_str)
    return _parse_config(data)


def _parse_config(raw_config: Dict[str, Any]) -> Config:
    def get_int(section:str, name:str, default: int) -> int:
        return int(raw_config.get(section, {}).get(name, default))
    def get_float(section:str, name:str, default: float) -> float:
        return float(raw_config.get(section, {}).get(name, default))
    
    return Config(
        message_count=get_int("messages", "message_count", 1_000),
        message_length=get_int("messages", "message_length", 100),
        producer_count=get_int("producer", "producer_count", 1),
        batch_size=get_int("producer", "batch_size", 1),
        sender_count=get_int("sender", "sender_count", 50_000),
        send_time_mean=get_float("sender", "send_time_mean", 1.0),
        send_time_stddev=get_float("sender", "send_time_stddev", 0.1),
        print_frequency=get_int("monitor", "print_frequency", 2),
    )