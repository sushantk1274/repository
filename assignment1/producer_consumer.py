import threading
import time
import random
from typing import List, Any


class SharedQueue:
    # Thread-safe bounded queue with wait/notify mechanism
    def __init__(self, max_size: int = 10):
        self.queue = []
        self.max_size = max_size
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        self.closed = False

    # Add item to queue, blocks if full
    def put(self, item: Any) -> bool:
        with self.not_full:
            while len(self.queue) >= self.max_size and not self.closed:
                self.not_full.wait()
            if self.closed:
                return False
            self.queue.append(item)
            self.not_empty.notify()
            return True

    # Remove and return item from queue, blocks if empty
    def get(self, timeout: float = None) -> Any:
        with self.not_empty:
            start_time = time.time()
            while len(self.queue) == 0 and not self.closed:
                if timeout is not None:
                    remaining = timeout - (time.time() - start_time)
                    if remaining <= 0:
                        return None
                    self.not_empty.wait(timeout=remaining)
                else:
                    self.not_empty.wait()
            if len(self.queue) == 0:
                return None
            item = self.queue.pop(0)
            self.not_full.notify()
            return item

    # Signal that no more items will be added
    def close(self):
        with self.lock:
            self.closed = True
            self.not_empty.notify_all()
            self.not_full.notify_all()

    # Check if queue is empty
    def is_empty(self) -> bool:
        with self.lock:
            return len(self.queue) == 0

    # Get current queue size
    def size(self) -> int:
        with self.lock:
            return len(self.queue)


class Producer(threading.Thread):
    # Producer thread that reads from source and puts items into shared queue
    def __init__(self, source: List[Any], shared_queue: SharedQueue, name: str = "Producer"):
        super().__init__(name=name)
        self.source = source
        self.shared_queue = shared_queue
        self.items_produced = 0

    # Main producer loop
    def run(self):
        for item in self.source:
            if self.shared_queue.closed:
                break
            success = self.shared_queue.put(item)
            if success:
                self.items_produced += 1
                print(f"[{self.name}] Produced: {item} (Queue size: {self.shared_queue.size()})")
                time.sleep(random.uniform(0.01, 0.05))
        print(f"[{self.name}] Finished. Total items produced: {self.items_produced}")


class Consumer(threading.Thread):
    # Consumer thread that reads from shared queue and stores in destination
    def __init__(self, shared_queue: SharedQueue, destination: List[Any], name: str = "Consumer"):
        super().__init__(name=name)
        self.shared_queue = shared_queue
        self.destination = destination
        self.items_consumed = 0
        self.running = True

    # Main consumer loop
    def run(self):
        while self.running:
            item = self.shared_queue.get(timeout=0.5)
            if item is not None:
                self.destination.append(item)
                self.items_consumed += 1
                print(f"[{self.name}] Consumed: {item} (Queue size: {self.shared_queue.size()})")
                time.sleep(random.uniform(0.02, 0.08))
            elif self.shared_queue.closed and self.shared_queue.is_empty():
                break
        print(f"[{self.name}] Finished. Total items consumed: {self.items_consumed}")

    # Stop the consumer thread
    def stop(self):
        self.running = False


class ProducerConsumerSystem:
    # Orchestrates multiple producers and consumers with shared queue
    def __init__(self, queue_size: int = 10):
        self.shared_queue = SharedQueue(max_size=queue_size)
        self.producers = []
        self.consumers = []
        self.destination = []
        self.lock = threading.Lock()

    # Create and add a producer thread
    def add_producer(self, source: List[Any], name: str = None) -> Producer:
        if name is None:
            name = f"Producer-{len(self.producers) + 1}"
        producer = Producer(source, self.shared_queue, name)
        self.producers.append(producer)
        return producer

    # Create and add a consumer thread
    def add_consumer(self, name: str = None) -> Consumer:
        if name is None:
            name = f"Consumer-{len(self.consumers) + 1}"
        with self.lock:
            consumer = Consumer(self.shared_queue, self.destination, name)
        self.consumers.append(consumer)
        return consumer

    # Start all producer and consumer threads
    def start(self):
        print("=" * 50)
        print("Starting Producer-Consumer System")
        print("=" * 50)
        for consumer in self.consumers:
            consumer.start()
        for producer in self.producers:
            producer.start()

    # Wait for all producers to finish and then shutdown consumers
    def wait_for_completion(self):
        for producer in self.producers:
            producer.join()
        self.shared_queue.close()
        for consumer in self.consumers:
            consumer.join()
        print("=" * 50)
        print("System Complete")
        print(f"Total items in destination: {len(self.destination)}")
        print("=" * 50)

    # Get the collected items from destination
    def get_results(self) -> List[Any]:
        return self.destination.copy()


def demo_single_producer_consumer():
    # Demo with single producer and single consumer
    print("\n" + "=" * 60)
    print("DEMO 1: Single Producer - Single Consumer")
    print("=" * 60)

    source_data = [f"Item-{i}" for i in range(1, 11)]

    system = ProducerConsumerSystem(queue_size=5)
    system.add_producer(source_data, "Producer")
    system.add_consumer("Consumer")

    system.start()
    system.wait_for_completion()

    print(f"\nSource items: {len(source_data)}")
    print(f"Destination items: {len(system.get_results())}")
    return system.get_results()


def demo_multiple_producers_consumers():
    # Demo with multiple producers and multiple consumers
    print("\n" + "=" * 60)
    print("DEMO 2: Multiple Producers - Multiple Consumers")
    print("=" * 60)

    source1 = [f"A-{i}" for i in range(1, 8)]
    source2 = [f"B-{i}" for i in range(1, 8)]

    system = ProducerConsumerSystem(queue_size=5)
    system.add_producer(source1, "Producer-A")
    system.add_producer(source2, "Producer-B")
    system.add_consumer("Consumer-1")
    system.add_consumer("Consumer-2")

    system.start()
    system.wait_for_completion()

    print(f"\nTotal source items: {len(source1) + len(source2)}")
    print(f"Destination items: {len(system.get_results())}")
    return system.get_results()


if __name__ == "__main__":
    demo_single_producer_consumer()
    demo_multiple_producers_consumers()
