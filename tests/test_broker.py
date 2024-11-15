import broker
import producer
import stats_collector

async def test_round_trip() -> None:
    collector = stats_collector.StatsCollector()
    prod = producer.SmsMessageProducer(collector)
    batch1 = prod.generate_message_batch(25)
    batch2 = prod.generate_message_batch(25)

    br = broker.MessageBroker(10)
    await br.put_batch(batch1)
    await br.put_batch(batch2)
    res = await br.get_batch()
    assert res == batch1
    res = await br.get_batch()
    assert res == batch2
