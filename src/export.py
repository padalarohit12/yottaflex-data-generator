"""
Export functions for CSV, JSON, SQL
"""
import os
import json
import csv
import hashlib
from pathlib import Path
from datetime import datetime

def export_all(data, ground_truth, state_events, config):
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export CSV
    csv_dir = output_dir / 'csv'
    csv_dir.mkdir(exist_ok=True)
    for name, records in data.items():
        if name.startswith('_'):
            continue
        if not records:
            continue
        filepath = csv_dir / f'{name}.csv'
        keys = list(records[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)
        print(f"Wrote {filepath} ({len(records)} rows)")
    
    # Export JSON
    json_dir = output_dir / 'json'
    json_dir.mkdir(exist_ok=True)
    for name, records in data.items():
        if name.startswith('_'):
            continue
        filepath = json_dir / f'{name}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2)
        print(f"Wrote {filepath} ({len(records)} rows)")
    
    # Export ground truth
    gt_dir = Path(config.ground_truth_dir)
    gt_dir.mkdir(parents=True, exist_ok=True)
    with open(gt_dir / 'ground_truth.csv', 'w', newline='', encoding='utf-8') as f:
        if ground_truth:
            writer = csv.DictWriter(f, fieldnames=ground_truth[0].keys())
            writer.writeheader()
            writer.writerows(ground_truth)
    with open(gt_dir / 'ground_truth.json', 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=2)
    print(f"Wrote ground truth ({len(ground_truth)} entries)")
    
    # Export state events
    with open(csv_dir / 'StateChangeEvent.csv', 'w', newline='', encoding='utf-8') as f:
        if state_events:
            keys = list(state_events[0].keys())
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(state_events)
    
    # Export SQL
    export_sql(data, ground_truth, config)
    
    # Create manifest with checksums
    create_manifest(output_dir, gt_dir, config)
    
    print("Export complete")

def export_sql(data, ground_truth, config):
    sql_dir = Path('sql')
    sql_dir.mkdir(exist_ok=True)
    
    schema_sql = sql_dir / 'schema.sql'
    with open(schema_sql, 'w', encoding='utf-8') as f:
        f.write("-- YottaFlex Schema\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n\n")
        # Basic schema
        f.write("CREATE TABLE IF NOT EXISTS Customer (customer_id VARCHAR PRIMARY KEY, first_name VARCHAR, last_name VARCHAR, email VARCHAR, phone VARCHAR, city VARCHAR, country VARCHAR, created_at TIMESTAMP, status VARCHAR);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS Seller (seller_id VARCHAR PRIMARY KEY, business_name VARCHAR, email VARCHAR, status VARCHAR, effective_from TIMESTAMP, effective_to TIMESTAMP, rating DECIMAL, created_at TIMESTAMP);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS CommissionRule (commission_rule_id VARCHAR PRIMARY KEY, category VARCHAR, commission_rate DECIMAL, reserve_rate DECIMAL, effective_from TIMESTAMP, effective_to TIMESTAMP, is_active BOOLEAN);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS ProductListing (listing_id VARCHAR PRIMARY KEY, seller_id VARCHAR REFERENCES Seller(seller_id), commission_rule_id VARCHAR REFERENCES CommissionRule(commission_rule_id), title VARCHAR, category VARCHAR, price DECIMAL, status VARCHAR, created_at TIMESTAMP);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS \"Order\" (order_id VARCHAR PRIMARY KEY, customer_id VARCHAR REFERENCES Customer(customer_id), status VARCHAR, created_at TIMESTAMP, confirmed_at TIMESTAMP, completed_at TIMESTAMP, currency VARCHAR, subtotal DECIMAL);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS OrderLine (order_line_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES \"Order\"(order_id), listing_id VARCHAR REFERENCES ProductListing(listing_id), seller_id VARCHAR REFERENCES Seller(seller_id), quantity INTEGER, unit_price DECIMAL, line_total DECIMAL);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS Fulfillment (fulfillment_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES \"Order\"(order_id), seller_id VARCHAR REFERENCES Seller(seller_id), status VARCHAR, created_at TIMESTAMP, promised_ship_by TIMESTAMP, shipped_at TIMESTAMP, delivered_at TIMESTAMP, returned_at TIMESTAMP, is_late_shipment BOOLEAN);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS FulfillmentLine (fulfillment_line_id VARCHAR PRIMARY KEY, fulfillment_id VARCHAR REFERENCES Fulfillment(fulfillment_id), order_line_id VARCHAR REFERENCES OrderLine(order_line_id), quantity INTEGER);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS CustomerReview (review_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES \"Order\"(order_id), order_line_id VARCHAR REFERENCES OrderLine(order_line_id), customer_id VARCHAR REFERENCES Customer(customer_id), seller_id VARCHAR REFERENCES Seller(seller_id), rating INTEGER, comment VARCHAR, created_at TIMESTAMP);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS Dispute (dispute_id VARCHAR PRIMARY KEY, order_id VARCHAR REFERENCES \"Order\"(order_id), fulfillment_id VARCHAR REFERENCES Fulfillment(fulfillment_id), seller_id VARCHAR REFERENCES Seller(seller_id), customer_id VARCHAR REFERENCES Customer(customer_id), reason VARCHAR, amount DECIMAL, status VARCHAR, created_at TIMESTAMP, resolved_at TIMESTAMP);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS Payout (payout_id VARCHAR PRIMARY KEY, seller_id VARCHAR REFERENCES Seller(seller_id), period_start DATE, period_end DATE, payout_date DATE, status VARCHAR, total_amount DECIMAL, currency VARCHAR);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS PayoutLine (payout_line_id VARCHAR PRIMARY KEY, payout_id VARCHAR REFERENCES Payout(payout_id), order_id VARCHAR REFERENCES \"Order\"(order_id), order_line_id VARCHAR REFERENCES OrderLine(order_line_id), fulfillment_id VARCHAR REFERENCES Fulfillment(fulfillment_id), seller_id VARCHAR REFERENCES Seller(seller_id), gross_amount DECIMAL, commission_amount DECIMAL, reserve_amount DECIMAL, refund_amount DECIMAL, adjustment_amount DECIMAL, net_amount DECIMAL, status VARCHAR, eligible_at TIMESTAMP);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS StateChangeEvent (event_id SERIAL PRIMARY KEY, entity_type VARCHAR, entity_id VARCHAR, from_state VARCHAR, to_state VARCHAR, reason VARCHAR, occurred_at TIMESTAMP);\n\n")
        f.write("CREATE TABLE IF NOT EXISTS GroundTruth (ground_truth_id VARCHAR PRIMARY KEY, entity_type VARCHAR, entity_id VARCHAR, issue_type VARCHAR, expected_decision VARCHAR, rule_ref VARCHAR, explanation VARCHAR, severity VARCHAR);\n\n")
    
    # Data inserts (sample - full inserts would be large, but include structure)
    seeds_sql = sql_dir / 'seeds.sql'
    with open(seeds_sql, 'w', encoding='utf-8') as f:
        f.write("-- YottaFlex Seeds\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n\n")
        f.write("-- See data/generated/*/csv for full data\n")
    
    print(f"Wrote {schema_sql} and {seeds_sql}")

def create_manifest(output_dir, gt_dir, config):
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'seed': config.seed,
        'scale': config.scale,
        'volumes': {
            'sellers': config.sellers,
            'listings': config.listings,
            'orders': config.orders,
            'disputes': config.disputes
        },
        'files': []
    }
    
    # Walk all files
    for root, dirs, files in os.walk(output_dir):
        for fname in files:
            fpath = Path(root) / fname
            rel_path = str(fpath.relative_to(Path('.')))
            # Compute checksum
            sha256_hash = hashlib.sha256()
            with open(fpath, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            manifest['files'].append({
                'path': rel_path,
                'size_bytes': fpath.stat().st_size,
                'sha256': sha256_hash.hexdigest()
            })
    
    for root, dirs, files in os.walk(gt_dir):
        for fname in files:
            fpath = Path(root) / fname
            rel_path = str(fpath.relative_to(Path('.')))
            sha256_hash = hashlib.sha256()
            with open(fpath, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            manifest['files'].append({
                'path': rel_path,
                'size_bytes': fpath.stat().st_size,
                'sha256': sha256_hash.hexdigest()
            })
    
    manifest_path = output_dir / 'manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote {manifest_path} with {len(manifest['files'])} files")
