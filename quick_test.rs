//!
//! ```cargo
//! [dependencies]
//! smol = "2"
//! ```

const NUM_MESSAGES : usize = 100_000_000;
const NUM_CONSUMERS : usize = 2_000_000;
const QUEUE_SIZE : usize = 1_000_000;
const PRINT_FREQ : usize = 10_000_000;

use smol::{channel, prelude::*};

fn main() {
    let (send_ch, recv_ch) = channel::bounded::<String>(QUEUE_SIZE);

    smol::block_on( async {
        let sender_task = smol::spawn(producer(send_ch.clone(), NUM_MESSAGES/2));
        let mut consumer_tasks = Vec::<smol::Task<usize>>::new();
        for task_nr in 0..NUM_CONSUMERS {
            consumer_tasks.push(smol::spawn(consumer(recv_ch.clone())));
        }
        sender_task.await;
        send_ch.close();
        let mut total_received = 0;
        for task in consumer_tasks {
            total_received += task.await;
        }
        println!("Received a total of {total_received} messages across all consumers.");
    });
}

async fn producer(send_ch: channel::Sender::<String>, num_messages: usize) {
    for i in 0..num_messages {
        assert_eq!(send_ch.send("Hello".to_string()).await, Ok(()));
        if (i + 1) % PRINT_FREQ == 0 {
            println!("Sender sent {i} messages.");
        }
    }
}


async fn consumer(recv_ch: channel::Receiver::<String>) -> usize {
    let mut msg_count: usize = 0;
    loop {
        if let Ok(msg) = recv_ch.recv().await {
            msg_count += 1;
            smol::Timer::after(std::time::Duration::from_secs(1)).await;
            if (msg_count + 1) % PRINT_FREQ == 0 {
                println!("Consumer got {msg}.");
            }
        } else {
            break;
        }
    }
    return msg_count;
}
