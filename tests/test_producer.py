import producer
import re
from sms_message import SmsMessage
import stats_collector


def validate_message(msg: SmsMessage) -> None:
    assert len(msg.message) == 100
    assert len(msg.destination) == 12

    # We don't need to match any valid phone number format,
    # only the one that we expect from the producer.
    phone_number_re = re.compile(r"\d{3}-\d{3}-\d{4}")
    assert phone_number_re.fullmatch(msg.destination)


def test_random_message() -> None:
    collector = stats_collector.StatsCollector()
    prod = producer.SmsMessageProducer(collector)
    msg = prod.generate_random_message()
    validate_message(msg)



def test_message_batch() -> None:
    collector = stats_collector.StatsCollector()
    prod = producer.SmsMessageProducer(collector)
    batch = prod.generate_message_batch(25)
    assert len(batch.messages) == 25
    for msg in batch.messages:
        validate_message(msg)
