# YottaFlex AI Candidate Project - Seller Marketplace Ops Data Generator

## Objective
Deterministic synthetic data generator for seller service levels, order fulfillment, disputes, commissions and payout eligibility. All data is generated locally with fixed seed for reproducibility.

## Quick Start

### Setup
```bash
pip install -r requirements.txt
```

### Generate Data (Full Scale)
```bash
python -m src.generate --seed 20261022 --scale full
```

### Generate Data (Starter Scale for testing)
```bash
python -m src.generate --seed 20261022 --scale starter
```

### Validate Existing Data
```bash
python -m src.validate --data-dir data/generated/full
```

## Scale
- Full: 2000 sellers, 20000 listings, 100000 orders, 10000 disputes
- Starter: 200 sellers, 2000 listings, 10000 orders, 1000 disputes (for dev/testing)

## Key Features
- Deterministic generation with fixed seed (20261022)
- All entities with proper PK/FK relationships
- Split orders (multi-seller) modeled via FulfillmentLine bridge table
- All 5 required edge cases injected as labelled anomalies
- Ground truth strictly separated (never leaked to feature tables)
- Full reconciliation and validation
- Exports: CSV, JSON, SQL
- Reproducible with checksums

## Project Structure
```
├── src/           # Generator source code
├── schema/        # ERD, data dictionary, schema.json
├── data/          # Generated data
├── sql/           # SQL schema and seeds
├── ground_truth/  # Anomaly labels (separate from features)
├── prompts/       # AI prompt history (transparency)
├── docs/          # Documentation
└── tests/         # Validation tests
```

## Transparency
All AI prompts used are recorded in `prompts/` directory. See `docs/AI_USAGE.md` for details on where AI helped, was reviewed, modified, or validated.

## License
This is synthetic data generated for evaluation purposes only. No real PII.
