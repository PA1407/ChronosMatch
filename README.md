# ChronosMatch – Exchange Matching Engine and Trading Dashboard

## 1. Project Overview

ChronosMatch is a Python-based exchange simulation system designed to demonstrate how trading platforms manage buy and sell orders, maintain an order book, execute trades, and preserve transaction data.

The application uses a matching engine based on price-time priority. It provides REST APIs through FastAPI, persistent storage using SQLite, and a Streamlit dashboard for interacting with the trading system.

The project focuses on modular architecture, matching correctness, order lifecycle management, database persistence, API integration, and automated testing.

**Project Status:** Core matching engine, REST API integration, database persistence, recovery functionality, and Streamlit dashboard have been implemented and tested.

## 2. Key Features

- **Order and Trade Management:** Structured models for orders, trade records, order sides, and order statuses.
- **Order Book:** Maintains separate buy and sell orders using price-time priority.
- **Matching Engine:** Automatically matches compatible buy and sell orders.
- **Partial and Complete Fills:** Updates filled and remaining quantities during trade execution.
- **Order Cancellation:** Supports cancellation of active orders while preserving previously executed trades.
- **Trade Records:** Stores execution price, quantity, timestamp, and associated buy and sell order IDs.
- **REST API Integration:** FastAPI endpoints allow users to submit, retrieve, and manage orders and trades.
- **Database Persistence:** SQLite stores order and trade information.
- **Recovery Mechanism:** Restores the matching engine's state from persisted data when the application restarts.
- **Interactive Dashboard:** Streamlit provides a user interface for placing orders, viewing the order book, managing orders, and viewing trade history.
- **Automated Testing:** Pytest validates matching logic, API behavior, persistence, recovery, and other system functionality.

## 3. Matching Engine Rules

The matching engine follows price-time priority:

1. Buy orders are prioritized by highest price first.
2. Sell orders are prioritized by lowest price first.
3. When prices are equal, the earlier order receives priority.
4. A trade executes when the best buy price is equal to or higher than the best sell price.
5. The resting order's price is used as the execution price.
6. Filled and remaining quantities are updated after every execution.
7. Fully filled orders are removed from the active order book.
8. Partially filled orders remain active with their remaining quantity.
9. Active resting orders can be cancelled.
10. Previously executed trade records are preserved when an order is cancelled.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | SQLite |
| Frontend | Streamlit |
| Data Handling | Pandas |
| API Communication | REST API, Requests |
| Testing | Pytest |
| Version Control | Git and GitHub |

## 5. System Architecture

ChronosMatch follows a modular architecture with the following major components:

- **Frontend Layer:** Streamlit dashboard provides the user interface.
- **API Layer:** FastAPI exposes endpoints for order submission, order management, order-book retrieval, and trade history.
- **Matching Engine Layer:** Processes incoming orders and applies price-time priority.
- **Order Book Layer:** Maintains active buy and sell orders.
- **Persistence Layer:** SQLite stores order and trade records.
- **Recovery Mechanism:** Reloads persisted state during application startup.

### Order Processing Flow

1. A user submits an order through the Streamlit dashboard.
2. The frontend sends the request to the FastAPI backend.
3. The API validates and processes the order.
4. The matching engine checks the order against the existing order book.
5. Compatible orders are matched and trade records are generated.
6. Updated order and trade information is persisted in SQLite.
7. The dashboard retrieves and displays the latest order-book and trade information.

## 6. Project Structure

```text
ChronosMatch/
│
├── app/
│   ├── api/
│   ├── engine/
│   │   ├── models.py
│   │   ├── order_book.py
│   │   └── matching_engine.py
│   ├── database/
│   └── main.py
│
├── frontend/
│   ├── api_client.py
│   ├── dashboard.py
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   ├── requirements.md
│   └── team-responsibilities.md
│
├── tests/
│
├── ChronosMatch_Modules_Guide.pdf
├── .gitignore
├── README.md
└── requirements.txt
```

*The structure above highlights the main project components; individual modules and test files may contain additional files.*

## 7. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/PA1407/ChronosMatch.git
cd ChronosMatch
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install Backend Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5: Install Frontend Dependencies

```bash
python -m pip install -r frontend/requirements.txt
```

## 8. Running the Application

The backend and frontend should run in separate terminals.

### Start the Backend

From the project root, activate the virtual environment and run:

```bash
uvicorn app.main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### Start the Frontend

Open another terminal, navigate to the project root, activate the virtual environment, and run:

```bash
streamlit run frontend/dashboard.py
```

The dashboard is generally available at:

`http://localhost:8501`

## 9. Running Automated Tests

Run the complete test suite from the project root:

```bash
python -m pytest -v
```

**Latest verified result:** 45 tests passed successfully.

The test suite covers matching behavior, order-book priority, order validation, partial fills, cancellation, API functionality, persistence, and recovery scenarios.

Run the test command again after making changes to verify that existing functionality remains intact.

## 10. Current Limitations and Future Improvements

Although the core application is implemented, further improvements can include:

- Expanding edge-case and regression test coverage.
- Improving API error handling and validation.
- Enhancing dashboard usability and visualization.
- Adding concurrent request handling and more advanced order types.
- Profiling matching-engine performance under larger workloads.
- Evaluating data structures and optimization techniques for improved throughput.
- Adding deployment configuration and production-grade monitoring.

Zero-copy behavior and high-frequency performance improvements should only be claimed after implementation, profiling, and benchmark validation.

## 11. Project Objective

The objective of ChronosMatch is to build a modular, testable exchange simulation that demonstrates order-book management, matching algorithms, REST API integration, database persistence, recovery mechanisms, and frontend-backend communication.

This project is intended for educational and simulation purposes. It is not connected to a real trading exchange and is not designed for actual financial transactions.