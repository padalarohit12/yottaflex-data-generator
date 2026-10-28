"""
Basic validation tests for YottaFlex data generator
"""
import os
import csv
import json
from pathlib import Path


def test_id_patterns():
    """Test that ID patterns match requirements"""
    # Check starter data if exists
    data_dir = Path('data/generated/starter/csv')
    if not data_dir.exists():
        return
    # Sample check
    sellers_file = data_dir / 'Seller.csv'
    if sellers_file.exists():
        with open(sellers_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row['seller_id'].startswith('SELL-'), f"Invalid seller_id: {row['seller_id']}"
                break


def test_required_files_exist():
    """Test that all required source files exist"""
    required = [
        'src/generate.py',
        'src/generator.py', 
        'src/anomalies.py',
        'src/validate.py',
        'src/export.py',
        'README.md',
        'requirements.txt'
    ]
    for r in required:
        assert os.path.exists(r), f"Missing required file: {r}"


def test_ground_truth_separation():
    """Test that ground truth is separate from feature data"""
    gt_dir = Path('ground_truth')
    assert gt_dir.exists(), "Ground truth directory must exist"
    gt_file = gt_dir / 'ground_truth.json'
    assert gt_file.exists(), "Ground truth JSON must exist"
    
    with open(gt_file) as f:
        gt = json.load(f)
    assert len(gt) >= 5, "Must have at least 5 ground truth entries for the 5 edge cases"
    
    # Check all have required fields
    for entry in gt:
        assert 'issue_type' in entry
        assert 'entity_type' in entry
        assert 'entity_id' in entry
        assert 'expected_decision' in entry


def test_schema_exists():
    """Test that schema files exist"""
    assert os.path.exists('schema/erd.md')
    assert os.path.exists('schema/data_dictionary.csv')
    assert os.path.exists('schema/schema.json')
    assert os.path.exists('sql/schema.sql')


def test_anomalies_present():
    """Test that all 5 required edge cases are present"""
    gt_file = Path('ground_truth/ground_truth.json')
    if not gt_file.exists():
        return
    with open(gt_file) as f:
        gt = json.load(f)
    
    issue_types = {entry['issue_type'] for entry in gt}
    required_issues = {
        'PAYOUT_BEFORE_DELIVERY_HOLD',
        'COMMISSION_APPLIED_TWICE',
        'SUSPENDED_SELLER_CONTINUES_LISTING',
        'DISPUTE_NOT_DEDUCTED',
        'PAYOUT_TOTAL_MISMATCH'
    }
    for req in required_issues:
        assert req in issue_types, f"Missing required edge case: {req}"
