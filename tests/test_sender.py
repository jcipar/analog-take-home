import broker
import producer
import sender
import stats_collector

async def test_sends_messages() -> None:
    collector = stats_collector.StatsCollector()
    br = broker.MessageBroker(10)
    conf = sender.SendConfig(mean_send_time = 0.01)
    send = sender.Sender(br, collector, conf)
    prod = producer.SmsMessageProducer(br, collector)
    msg = prod.generate_random_message()
    await send.send_message(msg)
    stats = await collector.get_stats()
    assert 1 == stats.failed + stats.sent

async def test_stops_when_empty() -> None:
    collector = stats_collector.StatsCollector()
    br = broker.MessageBroker(10)
    conf = sender.SendConfig(mean_send_time = 0.01)
    send = sender.Sender(br, collector, conf)
    prod = producer.SmsMessageProducer(br, collector)

    await prod.send_multiple_batches(10, 10)
    br.shutdown()
    await send.consume_messages()
    stats = await collector.get_stats()
    assert stats.produced == 10 * 10
    assert stats.sent + stats.failed == 10 * 10
    
