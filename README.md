# YottaFlex AI Candidate Project – Seller Marketplace Ops Data Generator

⚡️ Deterministic synthetic data generator for seller service levels, order fulfillment, disputes, commissions, and payout eligibility. All data is reproducible via a fixed seed.

## 📑 Table of Contents
- [✨ Objective](#-objective)
- [🚀 Quick Start](#-quick-start)
- [⚖️ Scale Options](#-scale-options)
- [🔑 Key Features](#-key-features)
- [📁 Project Structure](#-project-structure)
- [🧪 Validation & Tests](#-validation--tests)
- [🛠️ Development](#-development)
- [🔐 Transparency](#-transparency)
- [📄 License](#-license)

## ✨ Objective
Generate deterministic synthetic data for a seller marketplace, covering:
- Sellers, listings, customers, orders, order lines
- Fulfillments (including split orders)
- Reviews, disputes, commissions, payouts
- Five labelled edge‑case anomalies (ground truth)

## 🚀 Quick Start
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install front‑end dependencies
npm install --prefix frontend

# Generate full‑scale data (shows progress bars)
python -u -m src.generate --seed 20261022 --scale full

# Validate the generated data
python -m src.validate --data-dir data/generated/full

# Run the UI locally
npm run dev --prefix frontend
```

## ⚖️ Scale Options
| Scale   | Sellers | Listings | Orders | Disputes |
|---------|--------:|----------:|-------:|---------:|
| **Full**   | 2 000 | 20 000 | 100 000 | 10 000 |
| **Starter**|   200 |  2 000 | 10 000 | 1 000 |

## 🔑 Key Features
- 🎲 Deterministic generation with fixed seed (`20261022`)
- 🔗 Full PK/FK relationship integrity
- 🔀 Split orders via fulfillment‑line bridge
- 🏷️ Five required edge‑case anomalies (ground‑truth separated)
- 📦 Export formats: CSV, JSON, SQL (with checksums)
- 🧪 Comprehensive validation suite
- 🎨 Premium front‑end built with React + Vite (dark mode, glass‑morphism, micro‑animations)

## 📁 Project Structure
```
src/            # Generator core
frontend/       # React + Vite UI
data/           # Generated data (CSV/JSON)
schema/         # ERD & data dictionary
ground_truth/   # Anomaly labels
docs/           # Documentation (including AI_USAGE.md)
tests/          # Validation tests
```

## 🧪 Validation & Tests
```bash
python -m src.validate --data-dir data/generated/full   # Validate full dataset
pytest tests/                                          # Run unit tests
```

## 🛠️ Development
- **Lint**: `ruff check src`
- **CI**: GitHub Actions automatically run lint, tests, and UI build on each push.
- **Docker**: Build with `docker build -t yottaflex .` and run `docker run yottaflex`.

## 🔐 Transparency
All AI‑assisted actions are documented in `docs/AI_USAGE.md`. The project adheres to strict reproducibility and data‑privacy standards.

## 📄 License
Synthetic data for evaluation purposes only. No real PII. See `LICENSE` for details.
