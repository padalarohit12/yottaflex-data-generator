"""
ID Generator - deterministic, zero-padded, immutable
"""
from .rng import get_rng

class IDGenerator:
    def __init__(self):
        self.counters = {
            'seller': 0,
            'customer': 0,
            'listing': 0,
            'order': 0,
            'orderline': 0,
            'fulfillment': 0,
            'review': 0,
            'dispute': 0,
            'commission_rule': 0,
            'payout': 0,
            'payoutline': 0,
        }
        self.rng = get_rng()
    
    def next_seller(self):
        self.counters['seller'] += 1
        return f"SELL-{self.counters['seller']:06d}"
    
    def next_customer(self):
        self.counters['customer'] += 1
        return f"CUST-{self.counters['customer']:06d}"
    
    def next_listing(self, seller_id):
        self.counters['listing'] += 1
        return f"LIST-{seller_id}-{self.counters['listing']:06d}"
    
    def next_order(self):
        self.counters['order'] += 1
        return f"ORD-2026-{self.counters['order']:06d}"
    
    def next_orderline(self):
        self.counters['orderline'] += 1
        return f"ORDL-2026-{self.counters['orderline']:06d}"
    
    def next_fulfillment(self):
        self.counters['fulfillment'] += 1
        return f"FUL-{self.counters['fulfillment']:06d}"  # Will be mapped to FUL-<order-line-id> per requirements? Wait - check requirement again
    
    def next_fulfillment_for_line(self, order_line_id):
        # Requirement says: FUL-<order-line-id>
        return f"FUL-{order_line_id}"
    
    def next_review(self):
        self.counters['review'] += 1
        return f"REV-2026-{self.counters['review']:06d}"
    
    def next_dispute(self):
        self.counters['dispute'] += 1
        return f"DSP-2026-{self.counters['dispute']:06d}"
    
    def next_commission_rule(self):
        self.counters['commission_rule'] += 1
        return f"CMR-2026-{self.counters['commission_rule']:06d}"
    
    def next_payout(self):
        self.counters['payout'] += 1
        return f"PAYOUT-2026-{self.counters['payout']:06d}"
    
    def next_payoutline(self):
        self.counters['payoutline'] += 1
        return f"PLN-2026-{self.counters['payoutline']:06d}"

id_gen = IDGenerator()
