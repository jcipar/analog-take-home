import pytest
import tempfile

import config

cfg_str = """
[messages]
message_count = 12
message_length = 10

[producer]
producer_count = 2
batch_size = 11

[sender]
sender_count = 400
send_time_mean = 0.1
send_time_stddev = 0.01
send_failure_rate = 0.5

[monitor]
print_frequency = 2
"""


def test_config() -> None:
    with tempfile.NamedTemporaryFile(delete_on_close=False) as fp:
        fp.write(cfg_str.encode("utf-8"))
        fp.close()
        cfg = config.read_config(fp.name)
        assert cfg.message_count == 12
        assert cfg.message_length == 10
        assert cfg.producer_count == 2
        assert cfg.batch_size == 11
        assert cfg.sender_count == 400
        assert cfg.send_time_mean == pytest.approx(0.1)
        assert cfg.send_time_stddev == pytest.approx(0.01)
        assert cfg.send_failure_rate == pytest.approx(0.5)
        assert cfg.print_frequency == 2
