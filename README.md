# AgroChain

AgroChain is a Flask-based demo application that tracks agricultural products on a simple blockchain.  
It includes a hacker-style light UI, product timelines, a blockchain explorer, and chain integrity checks.

## Features

- Product lifecycle tracking with event history
- In-memory blockchain with SHA-256 hashing
- PoA-style validator simulation
- Chain validation and tamper simulation
- REST API + web dashboard

## Tech Stack

- Python
- Flask
- HTML/CSS/JavaScript (single template UI)

## Project Structure

```text
.
├── app.py
├── templates/
│   └── index.html
└── README.md
```

## Getting Started

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install Flask:

```powershell
pip install Flask
```

3. Run the app:

```powershell
python app.py
```

4. Open in your browser:

```text
http://127.0.0.1:5050
```

## API Endpoints

- `GET /api/stats` — chain and validator statistics
- `GET /api/chain` — full blockchain
- `GET /api/products` — product summary list
- `GET /api/product/<product_id>` — full event chain for one product
- `POST /api/add_event` — add event to a product
- `POST /api/new_product` — create a new product with initial production event
- `GET /api/validate` — validate blockchain integrity
- `POST /api/tamper/<index>` — tamper with a block (demo only)

## Notes

- Data is stored in memory (no database). Restarting the app resets blockchain state to seeded sample data.
- This project is for demonstration/learning purposes and not production-ready.
