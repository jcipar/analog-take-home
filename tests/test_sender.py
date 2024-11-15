import producer
import sender
import stats_collector

async def test_sends_messages() -> None:
    collector = stats_collector.StatsCollector()
    conf = sender.SendConfig(mean_send_time = 0.01)
    send = sender.Sender(collector, conf)
    prod = producer.SmsMessageProducer(collector)
    msg = prod.generate_random_message()
    await send.send_message(msg)
    stats = await collector.get_stats()
    assert 1 == stats.failed + stats.sent
    
