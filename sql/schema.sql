-- YottaFlex Schema
-- Generated: 2026-10-28T10:33:58.492025

CREATE TABLE IF NOT EXISTS Customer (customer_id VARCHAR PRIMARY KEY, first_name VARCHAR, last_name VARCHAR, email VARCHAR, phone VARCHAR, city VARCHAR, country VARCHAR, created_at TIMESTAMP, status VARCHAR);

CREATE TABLE IF NOT EXISTS Seller (seller_id VARCHAR PRIMARY KEY, business_name VARCHAR, email VARCHAR, status VARCHAR, effective_from TIMESTAMP, effective_to TIMESTAMP, rating DECIMAL, created_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS CommissionRule (commission_rule_id VARCHAR PRIMARY KEY, category VARCHAR, commission_rate DECIMAL, reserve_rate DECIMAL, effective_from TIMESTAMP, effective_to TIMESTAMP, is_active BOOLEAN);

CREATE TABLE IF NOT EXISTS ProductListing (listing_id VARCHAR PRIMARY KEY, seller_id VARCHAR REFERENCES Seller(seller_id), commission_rule_id VARCHAR REFERENCES CommissionRule(commission_rule_id), title VARCHAR, category VARCHAR, price DECIMAL, status VARCHAR, created_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS "Order" (order_id VARCHAR PRIMARY KEY, customer_id VARCHAR REFERENCES Customer(customer_id), status VARCHAR, created_at TIMESTAMP, confirmed_at TIMESTAMP, completed_at TIMESTAMP, currency VARCHAR, subtotal DECIMAL);

CREATE TABLE IF NOT EXISTS OrderLine (order_line_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES "Order"(order_id), listing_id VARCHAR REFERENCES ProductListing(listing_id), seller_id VARCHAR REFERENCES Seller(seller_id), quantity INTEGER, unit_price DECIMAL, line_total DECIMAL);

CREATE TABLE IF NOT EXISTS Fulfillment (fulfillment_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES "Order"(order_id), seller_id VARCHAR REFERENCES Seller(seller_id), status VARCHAR, created_at TIMESTAMP, promised_ship_by TIMESTAMP, shipped_at TIMESTAMP, delivered_at TIMESTAMP, returned_at TIMESTAMP, is_late_shipment BOOLEAN);

CREATE TABLE IF NOT EXISTS FulfillmentLine (fulfillment_line_id VARCHAR PRIMARY KEY, fulfillment_id VARCHAR REFERENCES Fulfillment(fulfillment_id), order_line_id VARCHAR REFERENCES OrderLine(order_line_id), quantity INTEGER);

CREATE TABLE IF NOT EXISTS CustomerReview (review_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES "Order"(order_id), order_line_id VARCHAR REFERENCES OrderLine(order_line_id), customer_id VARCHAR REFERENCES Customer(customer_id), seller_id VARCHAR REFERENCES Seller(seller_id), rating INTEGER, comment VARCHAR, created_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS Dispute (dispute_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES "Order"(order_id), fulfillment_id VARCHAR REFERENCES Fulfillment(fulfillment_id), seller_id VARCHAR REFERENCES Seller(seller_id), customer_id VARCHAR REFERENCES Customer(customer_id), reason VARCHAR, amount DECIMAL, status VARCHAR, created_at TIMESTAMP, resolved_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS Payout (payout_id VARCHAR PRIMARY KEY, seller_id VARCHAR REFERENCES Seller(seller_id), period_start DATE, period_end DATE, payout_date DATE, status VARCHAR, total_amount DECIMAL, currency VARCHAR);

CREATE TABLE IF NOT EXISTS PayoutLine (payout_line_id VARCHAR PRIMARY KEY, payout_id VARCHAR REFERENCES Payout(payout_id), order_id VARCHAR REFERENCES "Order"(order_id), order_line_id VARCHAR REFERENCES OrderLine(order_line_id), fulfillment_id VARCHAR REFERENCES Fulfillment(fulfillment_id), seller_id VARCHAR REFERENCES Seller(seller_id), gross_amount DECIMAL, commission_amount DECIMAL, reserve_amount DECIMAL, refund_amount DECIMAL, adjustment_amount DECIMAL, net_amount DECIMAL, status VARCHAR, eligible_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS StateChangeEvent (event_id SERIAL PRIMARY KEY, entity_type VARCHAR, entity_id VARCHAR, from_state VARCHAR, to_state VARCHAR, reason VARCHAR, occurred_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS GroundTruth (ground_truth_id VARCHAR PRIMARY KEY, entity_type VARCHAR, entity_id VARCHAR, issue_type VARCHAR, expected_decision VARCHAR, rule_ref VARCHAR, explanation VARCHAR, severity VARCHAR);

