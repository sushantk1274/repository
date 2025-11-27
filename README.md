# Assignments

This repository contains two Python assignments demonstrating thread synchronization and data analysis using functional programming.

## Project Structure

```
├── assignment1/
│   ├── producer_consumer.py      # Producer-Consumer pattern implementation
│   └── test_producer_consumer.py # Unit tests for Assignment 1
├── assignment2/
│   ├── sales_analysis.py         # Sales data analysis implementation
│   ├── sales_data.csv            # Sample sales data (50 records)
│   └── test_sales_analysis.py    # Unit tests for Assignment 2
└── README.md
```

## Requirements

- Python 3.8+
- No external dependencies required (uses standard library only)

## Setup Instructions

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

2. No additional installation needed - both assignments use Python standard library.

---

## Assignment 1: Producer-Consumer Pattern

Demonstrates thread synchronization using blocking queues and wait/notify mechanism.

### Features

- Custom SharedQueue with thread-safe operations
- Producer thread that reads from source and adds to queue
- Consumer thread that reads from queue and stores in destination
- ProducerConsumerSystem for orchestrating multiple producers/consumers

### Run Demo

```bash
cd assignment1
python producer_consumer.py
```

### Run Tests

```bash
cd assignment1
python -m unittest test_producer_consumer -v
```

### Sample Output

```
DEMO 1: Single Producer - Single Consumer

[Producer] Produced: Item-1 (Queue size: 1)
[Consumer] Consumed: Item-1 (Queue size: 0)
...
System Complete
Total items in destination: 10

DEMO 2: Multiple Producers - Multiple Consumers

[Producer-A] Produced: A-1 (Queue size: 1)
[Producer-B] Produced: B-1 (Queue size: 2)
[Consumer-1] Consumed: A-1 (Queue size: 1)
...
System Complete
Total items in destination: 14
```

---

## Assignment 2: Sales Data Analysis

Demonstrates functional programming with stream operations, data aggregation, and lambda expressions.

### Features

- CSV data parsing and loading
- Revenue calculations (total, average, by category, by region)
- Top products and customers analysis
- Monthly revenue trends
- Filtering with custom predicates
- Mapping transformations
- Category and regional breakdowns

### Run Analysis

```bash
cd assignment2
python sales_analysis.py
```

### Run Tests

```bash
cd assignment2
python -m unittest test_sales_analysis -v
```

### Sample Output

```
SALES DATA ANALYSIS REPORT

Data source: sales_data.csv
Total records loaded: 50

1. OVERALL STATISTICS

Total Orders: 50
Total Revenue: $41,359.46
Average Order Value: $827.19
...

2. REVENUE BY CATEGORY

Electronics: $24,536.61 (59.3%)
Furniture: $16,822.85 (40.7%)

3. REVENUE BY REGION

North: $11,538.08 (27.9%)
South: $10,998.54 (26.6%)
East: $10,258.30 (24.8%)
West: $8,564.54 (20.7%)
...
```

---

## Key Concepts Demonstrated

### Assignment 1

- Thread synchronization using `threading.Lock` and `threading.Condition`
- Blocking queues with wait/notify mechanism
- Producer-consumer pattern
- Concurrent programming with multiple threads
- Thread-safe data structures

### Assignment 2

- Functional programming paradigms
- Lambda expressions
- Map, filter, reduce operations
- Data aggregation and grouping
- CSV file processing
- Statistical analysis
