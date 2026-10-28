# Plan: YottaFlex AI Candidate Project (Seller Marketplace Ops)

This is a **synthetic data generator + schema/project** for seller service levels, fulfillment, disputes, commissions, payout eligibility. Must follow all points strictly.

## Goal
Build a working, reproducible solution that generates realistic e-commerce marketplace ops data (sellers/listings/orders/fulfillments/reviews/disputes/commissions/payouts) with all relationships, rules, edge cases, ground truth, validation, docs, and full transparency artifacts (prompt history).

## Entities & Required IDs
Core: `Seller`, `ProductListing`, `Order`, `OrderLine`, `Fulfillment`, `CustomerReview`, `Dispute`, `CommissionRule`, `Payout`, `PayoutLine`  
IDs: `SELL-000001`, `LIST-<seller-id>-000001`, `ORD-2026-000001`, `FUL-<order-line-id>`, `DSP-2026-000001`, `PAYOUT-2026-000001`  
Must have PK for every entity, FK for every relationship, cardinality, optional, effective dates, lifecycle states, bridge tables for M:N, event history for state changes, `issue_type`/`ground_truth` labels for anomalies.

## Required Scale
- 2000 sellers
- 20000 listings  
- 100000 orders
- 10000 disputes  
Must include split orders, late shipment, returns, reserve holds, seller suspension.

## Required Edge Cases
- Payout before delivery/hold release
- Commission applied twice
- Suspended seller continues listing
- Dispute not deducted
- Payout total does not equal lines

## 10-Step Generation Plan (from requirements)
1. **Data dictionary** - For each entity: type, required/optional, allowed values, units, uniqueness, validation
2. **Parents first** - Seller, CommissionRule etc before children/events. Apply domain logic (create sellers/listings, orders across sellers, split multi-seller orders into fulfillments, shipment/delivery/reviews, commission/reserve rules, disputes/chargebacks, payout lines after delivery/hold windows)
3. **Deterministic IDs** - Fixed pattern with zero-padding, immutable, consistent across files
4. **Baseline volume** - With fixed seed (20261022), parameterizable scale, reproducible generator
5. **Labelled edge cases** - Inject after valid baseline; use ground truth labels (issue_type/ground_truth), don't corrupt unrelated rows
6. **Derived values** - Compute from sources (totals/balances/scores/statuses/dates)
7. **Ground truth separation** - Separate `ground_truth.csv/json` for anomalies/expected decisions/labels; never leak to input features
8. **Validation** - PK uniqueness, FK integrity, enums, date ordering, arithmetic reconciliation, lifecycle transitions, duplicate checks
9. **Export** - CSV/JSON/SQL seeds, README, schema/data dictionary, generator command, fixed seed, source manifest, validation summary
10. **Reproducibility** - Regenerate twice with same seed, compare row counts/checksums

## Phased Implementation Plan

### Phase 0: Setup & Project Structure (Day1 start)
- [ ] Create public GitHub repo structure
- [ ] Choose stack (recommend Python + pandas/pyarrow + pydantic/jsonschema + sqlalchemy + click/typer; or pure scripts). Must be free/local runnable
- [ ] Setup: `src/`, `data/` (raw/generated), `schema/`, `docs/`, `prompts/`, `tests/` (optional), `sql/`, `scripts/`
- [ ] Create initial commit

### Phase 1: Schema & Data Dictionary (Critical)
- [ ] Design full ERD with PK/FK, cardinality, optional, effective dates, lifecycle states
- [ ] Write detailed data dictionary for all 10 entities (field-level: type, req/opt, allowed values, units, uniqueness, validation)
- [ ] Define enums/states (Seller status, Order status, Fulfillment status, Dispute status, Payout status etc)
- [ ] Design bridge tables if any M:N (e.g. maybe not obvious, but must use if exists)
- [ ] Plan event history tables for state changes
- [ ] Document in `schema/erd.md`, `schema/data_dictionary.csv/md`, `schema/schema.json`

### Phase 2: Generator Design (Core)
- [ ] Config: seed=20261022, scales parameterized (starter/full), output formats
- [ ] ID generator with counters, deterministic
- [ ] Topological generation order (parents->children->events)
- [ ] Logic for splits (multi-seller orders -> multiple fulfillments), late shipment, returns, holds, suspensions
- [ ] CommissionRule logic, reserves/hold windows
- [ ] Disputes/chargebacks
- [ ] Payout calculation after delivery + hold windows
- [ ] Derived values computed from sources
- [ ] Ground truth tracking separate from features

### Phase 3: Baseline Data Generation
- [ ] Generate 2000 sellers, 20000 listings
- [ ] Generate 100000 orders across sellers (with splits)
- [ ] Generate fulfillments per order-line/split
- [ ] Generate customer reviews
- [ ] Generate commission rules
- [ ] Generate 10000 disputes (baseline)
- [ ] Compute derived fields

### Phase 4: Edge Cases Injection (Labelled)
- [ ] Inject each required edge case with `issue_type`/ground truth labels
- [ ] Ensure unrelated rows untouched, traceable
- [ ] Write to separate ground_truth store

### Phase 5: Validation & Reconciliation
- [ ] PK uniqueness checks
- [ ] FK integrity (all refs exist)
- [ ] Enum validation
- [ ] Date ordering (e.g. order created < fulfillment shipped/delivered < payout eligible)
- [ ] Arithmetic reconciliation (payout lines sum vs payout total; fees/refunds/holds)
- [ ] Lifecycle transitions valid
- [ ] Duplicates
- [ ] Generate validation summary report

### Phase 6: Export & Documentation
- [ ] Export CSV, JSON, SQL seeds (CREATE TABLE + INSERTs or just data)
- [ ] Write README with setup/run/verify
- [ ] Include generator command, fixed seed, source manifest
- [ ] Include validation summary
- [ ] Ensure reproducibility test (regen twice, compare counts/checksums)

### Phase 7: Transparency Artifacts (Must)
- [ ] **Prompt history** - Save ALL prompts to every AI tool used (full history). If tool can't export, document limitation + manual record
- [ ] Document where AI helped/reviewed/changed/validated
- [ ] Prepare explanation of decisions/tradeoffs/assumptions/limitations
- [ ] List dependencies, licenses
- [ ] No secrets

## Key Design Decisions to Make
- **Stack**: Python (easiest for deterministic data gen, pandas/json/csv, hashing/checksums). Determinism via `random.Random(seed)`, avoid `np.random` global state issues or seed properly.
- **Storage formats**: All three (CSV/JSON/SQL). SQL as .sql with schema + inserts or separate schema.sql + data.sql.
- **Reproducibility**: Single generator entrypoint `python -m src.generate --seed 20261022 --scale full`, log params, output manifest with checksums (sha256) of all files.
- **Ground truth**: `ground_truth/ground_truth.json` and/or `ground_truth.csv` with keys (entity, id, issue_type, expected_decision, rule_ref, explanation). Never mixed into feature inputs.
- **Event history**: Consider `state_change_events` table capturing transitions with timestamps/reasons.
- **Bridge tables**: Only if true M:N; need to check - OrderLine links Order and ProductListing? Or Order has OrderLines each tied to Listing/Seller. Fulfillment may relate to OrderLine(s). Might not need explicit bridge if modeled properly, but must use if exists.
- **Anomalies**: Explicitly mark with labels; don't "fix" them.

## Implementation Checklist (Verification)
- [ ] All 10 entities present with PK/FK
- [ ] ID patterns match exactly
- [ ] 2000/20000/100000/10000 volumes (or parameterized; document if using starter but must support full; better generate full or clearly explain)
- [ ] All 5 edge cases present and labeled
- [ ] Payouts reconcile (sum of PayoutLine amounts = Payout.total_amount considering fees/refunds/holds)
- [ ] Date ordering valid
- [ ] Ground truth separate
- [ ] Seed 20261022 fixed
- [ ] Reproducibility demonstrated (checksums)
- [ ] Prompt history included
- [ ] README complete
- [ ] Validation summary present

## Risks & Mitigations
- **Volume generation performance**: Use efficient pandas operations, vectorize where possible, chunked writes. 10^5 orders manageable in Python.
- **Referential integrity**: Build in topological order, use ID sets/lookups.
- **Reproducibility**: Central RNG, no time-based randomness, deterministic ordering.
- **Data leakage**: Strict separation - ground truth dir only, never imported by "feature" generation code paths.
- **Anomaly labeling**: Create ground truth entries at injection time.

## Next Steps (When Ready to Implement)
1. Initialize repo structure and git
2. Write detailed schema + data dictionary
3. Implement ID generator + config + RNG
4. Build generator in phases
5. Add validation + reconciliation
6. Export all formats + docs
7. Collect prompt history throughout
8. Run validation twice for reproducibility

**Ready to start implementation when you say go.** This plan covers all stated requirements with no obvious gaps.
