"""
Inject the 5 required edge cases as labelled anomalies
All anomalies go to ground_truth, never leak to feature tables
"""
from datetime import datetime, timedelta

def inject_all_anomalies(generator):
    rng = generator.rng
    data = generator.data
    ground_truth = generator.ground_truth
    
    # 1. Payout before delivery/hold release
    if data.get('PayoutLine'):
        pl = rng.choice(data['PayoutLine'])
        # Make it eligible before delivery
        pl['eligible_at'] = '2026-01-01T00:00:00'
        pl['status'] = 'ELIGIBLE'
        ground_truth.append({
            'ground_truth_id': f'GT-{len(ground_truth)+1:06d}',
            'entity_type': 'PayoutLine',
            'entity_id': pl['payout_line_id'],
            'issue_type': 'PAYOUT_BEFORE_DELIVERY_HOLD',
            'expected_decision': 'REJECT_OR_HOLD',
            'rule_ref': 'HOLD_WINDOW_7_DAYS',
            'explanation': 'Payout line marked eligible before delivery/hold release period completed',
            'severity': 'HIGH'
        })
    
    # 2. Commission applied twice
    if data.get('PayoutLine'):
        pl = rng.choice([p for p in data['PayoutLine'] if p['payout_line_id'] not in [g['entity_id'] for g in ground_truth if g['entity_type']=='PayoutLine']])
        if pl:
            # Double the commission
            pl['commission_amount'] = round(pl['commission_amount'] * 2, 2)
            pl['net_amount'] = round(pl['gross_amount'] - pl['commission_amount'] - pl['reserve_amount'] - pl['refund_amount'] + pl['adjustment_amount'], 2)
            ground_truth.append({
                'ground_truth_id': f'GT-{len(ground_truth)+1:06d}',
                'entity_type': 'PayoutLine',
                'entity_id': pl['payout_line_id'],
                'issue_type': 'COMMISSION_APPLIED_TWICE',
                'expected_decision': 'CORRECT_COMMISSION',
                'rule_ref': 'COMMISSION_RULE_SINGLE_APPLICATION',
                'explanation': 'Commission rate applied twice to same payout line',
                'severity': 'HIGH'
            })
    
    # 3. Suspended seller continues listing
    suspended = [s for s in data['Seller'] if s['status'] == 'SUSPENDED']
    if suspended:
        seller = suspended[0]
        listings = [l for l in data['ProductListing'] if l['seller_id'] == seller['seller_id']]
        if listings:
            # Ensure listing remains active (anomaly)
            for l in listings[:2]:
                l['status'] = 'ACTIVE'  # Should not be active if seller suspended
            ground_truth.append({
                'ground_truth_id': f'GT-{len(ground_truth)+1:06d}',
                'entity_type': 'Seller',
                'entity_id': seller['seller_id'],
                'issue_type': 'SUSPENDED_SELLER_CONTINUES_LISTING',
                'expected_decision': 'DEACTIVATE_LISTINGS',
                'rule_ref': 'SELLER_SUSPENSION_POLICY',
                'explanation': 'Suspended seller has active listings in violation of policy',
                'severity': 'HIGH'
            })
            for l in listings[:2]:
                ground_truth.append({
                    'ground_truth_id': f'GT-{len(ground_truth)+1:06d}',
                    'entity_type': 'ProductListing',
                    'entity_id': l['listing_id'],
                    'issue_type': 'SUSPENDED_SELLER_CONTINUES_LISTING',
                    'expected_decision': 'DEACTIVATE_LISTING',
                    'rule_ref': 'SELLER_SUSPENSION_POLICY',
                    'explanation': f'Listing from suspended seller {seller["seller_id"]} remains active',
                    'severity': 'HIGH'
                })
    
    # 4. Dispute not deducted
    if data.get('Dispute') and data.get('PayoutLine'):
        dispute = rng.choice([d for d in data['Dispute'] if d['status'] in ['RESOLVED_CUSTOMER', 'CHARGEBACK']])
        # Find related payout line
        related_pls = [pl for pl in data['PayoutLine'] if pl['order_id'] == dispute['order_id']]
        if related_pls:
            pl = related_pls[0]
            # Don't deduct dispute amount
            ground_truth.append({
                'ground_truth_id': f'GT-{len(ground_truth)+1:06d}',
                'entity_type': 'PayoutLine',
                'entity_id': pl['payout_line_id'],
                'issue_type': 'DISPUTE_NOT_DEDUCTED',
                'expected_decision': 'DEDUCT_DISPUTE_AMOUNT',
                'rule_ref': 'DISPUTE_DEDUCTION_POLICY',
                'explanation': f'Dispute {dispute["dispute_id"]} ({dispute["status"]}) not deducted from payout',
                'severity': 'HIGH'
            })
    
    # 5. Payout total does not equal lines
    if data.get('Payout') and data.get('PayoutLine'):
        payout = rng.choice([p for p in data['Payout'] if p['total_amount'] > 0])
        # Corrupt the total
        payout['total_amount'] = round(payout['total_amount'] + rng.uniform(50, 200), 2)
        ground_truth.append({
            'ground_truth_id': f'GT-{len(ground_truth)+1:06d}',
            'entity_type': 'Payout',
            'entity_id': payout['payout_id'],
            'issue_type': 'PAYOUT_TOTAL_MISMATCH',
            'expected_decision': 'RECONCILE_TO_LINES',
            'rule_ref': 'PAYOUT_RECONCILIATION',
            'explanation': 'Payout.total_amount does not equal sum of PayoutLine.net_amount',
            'severity': 'HIGH'
        })
    
    print(f"Injected {len(ground_truth)} ground truth entries for anomalies")
