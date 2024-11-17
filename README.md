# SMS Alert Simulation
This simulates a system for sending many SMS alerts. It must include producer processes that create SMS messages and sender processes that send them. For the purposes of this simulation, "sending" a message simply means sleeping for some amount of time. The project requirements specified that the system must be scalable, but left the precise target for scaling open-ended.

## Overall Design
![System diagram showing the 5 components described below](figures/system-diagram.png)

The system consists of 5 components, shown in the diagram above and documented in detail in their own sections below.
1. **Message Broker**: Responsible for moving messages between producers and senders.
2. **Producer**: Generates random messages and sends them to the broker.
3. **Sender**: Polls the broker for new messages and sends them one-by-one.
4. **Stats Collector**: Service that receives statistics from the other components, such as the number of messages sent.
5. **Monitor**: Periodically requests the most recent system statistics and logs them.


## Asyncio and Scalability tests
Because I expect most of the work for this system to involve waiting on blocking IO rather than computation (`sleep` in this case), my initial thought was to use Python asyncio with coroutines. I expected this to allow the system to initiate many simulataneous `send` requests with minimal overhead.

To validate this approach before designing the whole system around it, I first created a very crude version of the proposed system to run a quick-and-dirty scalability test. This code is entirely contained in `quick_test.py`. This experiment used an `asyncio.Queue` as the message broker, and `asyncio.Task`s for the producer and senders. I configured the mean send time to be 1 second with a standard deviation of 0.1 seconds.

In the experiment I varied the number of concurrent senders and measured the overall throughput. The number of messages sent was 10 times the number of senders. The figures below show the results of this experiment.

![Throughput scaling as the number of senders is increased](figures/throughput.png)
*The overall throughput as the number of senders is increased. Note the log-log scale. Throughput increases linearly until about 50e3 senders, at which point it levels off. The results show that there is no throughput collapse through abotu 2e6 senders, suggesting that it will not be necessary to carefully tune that parameter: just set it to something reasonably large and forget about it.*

![Efficiency scaling as the number of senders is increased](figures/throughput-per.png)
*Per-sender throughput as the number of senders is increased. Note the log-log scale. Per-sender throughput is constant, and just barely below 1 msg per second from 1 sender through about 50e3 senders. After that it drops off quickly. The fact that it is just barely below 1 (the configured mean send time) inidcates that the system is getting good efficiency for all of these parameter settings: almost all of a sender's time is spent sending messages, and not doing other things.*

![Time to send a message to everyone in the US](figures/us-pop-send.png)
*This chart shows the time to send a message to everyone in the United States. The US population is abotu 340 million, so this is really just another way of presenting the data from the first chart, however, it gives some understanding of what kind of scale we're talking about with this design: With 50 thousand senders it would take about 2 hours to message everyone in the US. That's probably good enough for many applications, but maybe not for something like an emergency alert system. For reference, at this throughput it would take about 2 minutes to message everyone in the state of Massachusetts.*
