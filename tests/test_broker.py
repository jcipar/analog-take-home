import broker
import config
import producer
import stats_collector


async def test_round_trip() -> None:
    conf = config.Config(max_queued_batches=10)
    collector = stats_collector.StatsCollector()
    br = broker.MessageBroker(conf)
    prod = producer.SmsMessageProducer(conf, br, collector)
    batch1 = await prod.generate_message_batch(25)
    batch2 = await prod.generate_message_batch(25)

    await br.put_batch(batch1)
    await br.put_batch(batch2)
    res = await br.get_batch()
    assert res == batch1
    res = await br.get_batch()
    assert res == batch2
