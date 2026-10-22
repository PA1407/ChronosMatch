# ChronosMatch — Zero-Copy High-Frequency Trading Engine

## 1. Project Overview

ChronosMatch is a Python-based exchange simulation project designed to explore order-book management, matching algorithms, and performance considerations relevant to high-frequency trading systems.

The project focuses on implementing a matching engine that processes buy and sell orders, maintains price-time priority, handles partial and complete order fills, and records executed trades.

**Project status:** Core engine development and automated testing are in progress.

## 2. Current Features

- **Order and trade models:** Structured representations of orders, trade records, order sides, and order statuses.
- **Order book:** Separate buy and sell order collections with price-time priority.
- **Matching engine:** Matches compatible buy and sell orders based on price and available quantity.
- **Partial fills:** Updates filled and remaining quantities when an order is only partially executed.
- **Trade records:** Records execution price, quantity, and associated buy and sell order IDs.
- **Order cancellation:** Supports cancellation of orders that remain in the order book.
- **Automated testing:** Uses pytest to validate matching behavior, order priority, invalid inputs, duplicate order IDs, and cancellation scenarios.

## 3. Matching Rules

The current implementation follows these rules:

- Buy orders are prioritized by highest price first.
- Sell orders are prioritized by lowest price first.
- Earlier orders receive priority when prices are equal.
- Orders match when their prices are compatible.
- The resting order's price is used as the execution price.
- Filled and remaining quantities are updated after execution.
- Unfilled quantities remain in the order book.
- Fully filled orders are removed from the order book.
- Resting orders can be cancelled through the matching engine.

## 4. Technology Stack

- **Language:** Python
- **Testing:** pytest
- **Version control:** Git and GitHub
- **Development environment:** Visual Studio Code

FastAPI integration, database persistence, dashboard development, and performance optimization are planned or under evaluation and should not be considered complete until implemented and tested.

## 5. Project Structure

```text
ChronosMatch/
├── app/
│   └── engine/
│       ├── models.py
│       ├── order_book.py
│       └── matching_engine.py
├── docs/
│   ├── architecture.md
│   ├── requirements.md
│   └── team-responsibilities.md
├── tests/
│   └── test_matching_engine.py
├── .gitignore
├── README.md
└── requirements.txt
```

## 6. Setup and Installation

Clone the repository:

```bash
git clone https://github.com/PA1407/ChronosMatch.git
cd ChronosMatch
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

## 7. Running the Tests

Run the complete test suite from the repository root:

```bash
python -m pytest -v
```

The latest reported test run during development completed with **16 passing tests**. Run the command above to confirm the current result after pulling the latest changes.

## 8. Current Limitations

- The matching engine has initial automated test coverage, but additional edge cases and regression tests are needed.
- The current order book prioritizes correctness and simplicity rather than optimized high-frequency performance.
- API integration and persistent order and trade storage remain future development tasks.
- Zero-copy behavior and performance improvements require implementation, profiling, and benchmark evidence before they can be claimed.

## 9. Planned Development

1. Expand order lifecycle and matching-engine test coverage.
2. Review matching correctness and error handling.
3. Integrate the engine with a REST API.
4. Add persistent storage for orders and trades.
5. Develop performance benchmarks and profile bottlenecks.
6. Evaluate optimization opportunities.
7. Complete documentation and prepare the final demonstration.

## 10. Project Objective

The objective is to develop a modular and testable exchange simulation while learning about matching-engine design, order-book data structures, software testing, and performance optimization.

This project is for simulation and educational purposes; it is not connected to a real trading exchange.
