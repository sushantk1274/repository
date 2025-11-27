import unittest
import threading
import time
from producer_consumer import SharedQueue, Producer, Consumer, ProducerConsumerSystem


class TestSharedQueue(unittest.TestCase):
    # Tests for the SharedQueue class

    def test_basic_put_get(self):
        # Test basic put and get operations
        sq = SharedQueue(max_size=5)
        sq.put("item1")
        sq.put("item2")
        self.assertEqual(sq.get(), "item1")
        self.assertEqual(sq.get(), "item2")

    def test_queue_size(self):
        # Test queue size tracking
        sq = SharedQueue(max_size=10)
        self.assertEqual(sq.size(), 0)
        sq.put("a")
        sq.put("b")
        self.assertEqual(sq.size(), 2)
        sq.get()
        self.assertEqual(sq.size(), 1)

    def test_is_empty(self):
        # Test empty check
        sq = SharedQueue(max_size=5)
        self.assertTrue(sq.is_empty())
        sq.put("item")
        self.assertFalse(sq.is_empty())
        sq.get()
        self.assertTrue(sq.is_empty())

    def test_blocking_on_full(self):
        # Test that put blocks when queue is full
        sq = SharedQueue(max_size=2)
        sq.put("a")
        sq.put("b")

        result = []
        def delayed_get():
            time.sleep(0.1)
            result.append(sq.get())

        getter = threading.Thread(target=delayed_get)
        getter.start()

        start = time.time()
        sq.put("c")
        elapsed = time.time() - start

        getter.join()
        self.assertGreater(elapsed, 0.05)
        self.assertEqual(len(result), 1)

    def test_get_timeout(self):
        # Test get with timeout on empty queue
        sq = SharedQueue(max_size=5)
        start = time.time()
        result = sq.get(timeout=0.1)
        elapsed = time.time() - start
        self.assertIsNone(result)
        self.assertGreater(elapsed, 0.05)

    def test_close_queue(self):
        # Test closing the queue
        sq = SharedQueue(max_size=5)
        sq.put("item")
        sq.close()
        self.assertTrue(sq.closed)
        self.assertEqual(sq.get(), "item")

    def test_fifo_order(self):
        # Test that queue maintains FIFO order
        sq = SharedQueue(max_size=10)
        items = [1, 2, 3, 4, 5]
        for item in items:
            sq.put(item)
        for expected in items:
            self.assertEqual(sq.get(), expected)


class TestProducer(unittest.TestCase):
    # Tests for the Producer class

    def test_producer_produces_all_items(self):
        # Test that producer puts all items into queue
        source = ["a", "b", "c", "d", "e"]
        sq = SharedQueue(max_size=10)
        producer = Producer(source, sq, "TestProducer")
        producer.start()
        producer.join()
        self.assertEqual(producer.items_produced, len(source))
        self.assertEqual(sq.size(), len(source))

    def test_producer_with_small_queue(self):
        # Test producer with queue smaller than source
        source = list(range(10))
        sq = SharedQueue(max_size=3)
        destination = []

        producer = Producer(source, sq, "TestProducer")
        consumer = Consumer(sq, destination, "TestConsumer")

        consumer.start()
        producer.start()
        producer.join()
        sq.close()
        consumer.join()

        self.assertEqual(producer.items_produced, len(source))


class TestConsumer(unittest.TestCase):
    # Tests for the Consumer class

    def test_consumer_consumes_all_items(self):
        # Test that consumer gets all items from queue
        sq = SharedQueue(max_size=10)
        destination = []
        items = ["x", "y", "z"]

        for item in items:
            sq.put(item)
        sq.close()

        consumer = Consumer(sq, destination, "TestConsumer")
        consumer.start()
        consumer.join()

        self.assertEqual(consumer.items_consumed, len(items))
        self.assertEqual(destination, items)

    def test_consumer_stops_on_close(self):
        # Test that consumer stops when queue is closed
        sq = SharedQueue(max_size=5)
        destination = []
        consumer = Consumer(sq, destination, "TestConsumer")
        consumer.start()

        time.sleep(0.1)
        sq.close()
        consumer.join(timeout=2)

        self.assertFalse(consumer.is_alive())


class TestProducerConsumerSystem(unittest.TestCase):
    # Tests for the ProducerConsumerSystem class

    def test_single_producer_single_consumer(self):
        # Test basic system with one producer and one consumer
        source = list(range(1, 21))
        system = ProducerConsumerSystem(queue_size=5)
        system.add_producer(source)
        system.add_consumer()
        system.start()
        system.wait_for_completion()

        results = system.get_results()
        self.assertEqual(len(results), len(source))
        self.assertEqual(sorted(results), sorted(source))

    def test_multiple_producers_single_consumer(self):
        # Test system with multiple producers
        source1 = [f"A{i}" for i in range(5)]
        source2 = [f"B{i}" for i in range(5)]

        system = ProducerConsumerSystem(queue_size=3)
        system.add_producer(source1, "Producer-A")
        system.add_producer(source2, "Producer-B")
        system.add_consumer()
        system.start()
        system.wait_for_completion()

        results = system.get_results()
        self.assertEqual(len(results), len(source1) + len(source2))

    def test_single_producer_multiple_consumers(self):
        # Test system with multiple consumers
        source = list(range(20))

        system = ProducerConsumerSystem(queue_size=5)
        system.add_producer(source)
        system.add_consumer("Consumer-1")
        system.add_consumer("Consumer-2")
        system.start()
        system.wait_for_completion()

        results = system.get_results()
        self.assertEqual(len(results), len(source))

    def test_multiple_producers_multiple_consumers(self):
        # Test system with multiple producers and consumers
        source1 = list(range(10))
        source2 = list(range(10, 20))

        system = ProducerConsumerSystem(queue_size=4)
        system.add_producer(source1, "P1")
        system.add_producer(source2, "P2")
        system.add_consumer("C1")
        system.add_consumer("C2")
        system.start()
        system.wait_for_completion()

        results = system.get_results()
        self.assertEqual(len(results), len(source1) + len(source2))

    def test_empty_source(self):
        # Test with empty source
        system = ProducerConsumerSystem(queue_size=5)
        system.add_producer([])
        system.add_consumer()
        system.start()
        system.wait_for_completion()

        self.assertEqual(len(system.get_results()), 0)

    def test_data_integrity(self):
        # Test that all data is transferred correctly
        source = [{"id": i, "value": f"data-{i}"} for i in range(15)]

        system = ProducerConsumerSystem(queue_size=5)
        system.add_producer(source)
        system.add_consumer()
        system.start()
        system.wait_for_completion()

        results = system.get_results()
        self.assertEqual(len(results), len(source))
        for item in source:
            self.assertIn(item, results)


class TestConcurrency(unittest.TestCase):
    # Tests for thread synchronization correctness

    def test_no_data_loss(self):
        # Verify no items are lost during concurrent access
        source = list(range(100))
        system = ProducerConsumerSystem(queue_size=10)
        system.add_producer(source)
        system.add_consumer()
        system.add_consumer()
        system.start()
        system.wait_for_completion()

        results = system.get_results()
        self.assertEqual(sorted(results), sorted(source))

    def test_no_duplicates(self):
        # Verify no duplicate items appear
        source = list(range(50))
        system = ProducerConsumerSystem(queue_size=5)
        system.add_producer(source)
        system.add_consumer()
        system.add_consumer()
        system.start()
        system.wait_for_completion()

        results = system.get_results()
        self.assertEqual(len(results), len(set(results)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
