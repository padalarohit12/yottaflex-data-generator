# YottaFlex Schema (ERD)

## Entities

### Core Entities
- **Customer** (customer_id PK) - Marketplace customers
- **Seller** (seller_id PK) - Marketplace sellers (with status, effective dates)
- **CommissionRule** (commission_rule_id PK) - Commission/reserve rates by category
- **ProductListing** (listing_id PK, FK seller_id, FK commission_rule_id) - Seller product listings
- **Order** (order_id PK, FK customer_id) - Customer orders
- **OrderLine** (order_line_id PK, FK order_id, FK listing_id, FK seller_id) - Order line items
- **Fulfillment** (fulfillment_id PK, FK order_id, FK seller_id) - Fulfillment per (order, seller) - handles split orders
- **FulfillmentLine** (fulfillment_line_id PK, FK fulfillment_id, FK order_line_id) - Bridge between fulfillment and order lines
- **CustomerReview** (review_id PK, FK order_id, FK order_line_id, FK customer_id, FK seller_id) - Reviews
- **Dispute** (dispute_id PK, FK order_id, FK fulfillment_id, FK seller_id, FK customer_id) - Disputes/chargebacks
- **Payout** (payout_id PK, FK seller_id) - Weekly payouts per seller
- **PayoutLine** (payout_line_id PK, FK payout_id, FK order_id, FK order_line_id, FK fulfillment_id, FK seller_id) - Payout line items with fees/reserves/holds

### Supporting
- **StateChangeEvent** (event_id PK) - State change audit trail
- **GroundTruth** (ground_truth_id PK) - Anomaly labels (separate from features)

## Relationships
- Seller 1:N ProductListing
- Customer 1:N Order
- Order 1:N OrderLine
- OrderLine N:1 ProductListing, N:1 Seller
- Order N:N Seller via Fulfillment (split orders) - modeled with Fulfillment + FulfillmentLine
- Fulfillment 1:N FulfillmentLine
- Order 1:N CustomerReview, 1:N Dispute
- Seller 1:N Payout
- Payout 1:N PayoutLine

## Key Design Notes
- **Split orders**: Multi-seller orders create multiple Fulfillment records (one per seller). FulfillmentLine bridges fulfillments to order lines.
- **Payout holds**: PayoutLine has `eligible_at` (delivery + hold window). Eligibility enforced by business rules.
- **Ground truth separation**: All anomaly labels in `ground_truth/` directory, never mixed into feature tables.
- **Deterministic IDs**: Following patterns like SELL-000001, LIST-<seller>-000001, ORD-2026-000001, FUL-<order-line-id>, DSP-2026-000001, PAYOUT-2026-000001, PLN-2026-000001
