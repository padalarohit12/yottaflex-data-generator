"""
Main data generator for YottaFlex project
"""
import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path

from .config import Config
from .rng import get_rng, reset_rng
from .id_generator import IDGenerator
from .models import *
from . import anomalies

class DataGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.rng = reset_rng(config.seed)
        self.id_gen = IDGenerator()
        self.data = {}
        self.ground_truth = []
        self.state_events = []
        
    def generate_all(self):
        print(f"Generating data with seed={self.config.seed}, scale={self.config.scale}")
        print(f"Target: {self.config.sellers} sellers, {self.config.listings} listings, "
              f"{self.config.orders} orders, {self.config.disputes} disputes")
        
        # Phase 1: Parents/Masters
        self.generate_customers()
        self.generate_sellers()
        self.generate_commission_rules()
        self.generate_listings()
        
        # Phase 2: Orders and OrderLines
        self.generate_orders()
        self.generate_order_lines()
        
        # Phase 3: Fulfillments (handle splits via bridge)
        self.generate_fulfillments()
        self.generate_fulfillment_lines()
        
        # Phase 4: Reviews, Disputes
        self.generate_reviews()
        self.generate_disputes()
        
        # Phase 5: Payouts
        self.generate_payouts()
        self.generate_payout_lines()
        
        # Phase 6: Inject edge cases as labelled anomalies
        anomalies.inject_all_anomalies(self)
        
        print(f"Generation complete. Data shapes:")
        for k, v in self.data.items():
            print(f"  {k}: {len(v)} records")
        print(f"  ground_truth: {len(self.ground_truth)} entries")
        print(f"  state_change_events: {len(self.state_events)} events")
        
        return self.data
    
    def generate_customers(self):
        customers = []
        count = self.config.orders * 2  # Some repeat customers
        for i in range(min(count, 50000)):  # Cap reasonably
            cust_id = self.id_gen.next_customer()
            customers.append({
                'customer_id': cust_id,
                'first_name': f'First{i%1000}',
                'last_name': f'Last{i%100}',
                'email': f'cust{i}@example.com',
                'phone': f'555-{i%10000:04d}',
                'city': self.rng.choice(['NYC', 'LA', 'SF', 'CHI', 'BOS']),
                'country': 'US',
                'created_at': (datetime(2025, 1, 1) + timedelta(days=self.rng.randint(0, 365))).isoformat(),
                'status': 'ACTIVE'
            })
        self.data['Customer'] = customers
    
    def generate_sellers(self):
        sellers = []
        for i in range(self.config.sellers):
            seller_id = self.id_gen.next_seller()
            status = 'ACTIVE'
            # Some will be suspended later for anomaly
            if self.rng.random() < 0.02:
                status = 'SUSPENDED'
            sellers.append({
                'seller_id': seller_id,
                'business_name': f'SellerBusiness{i}',
                'email': f'seller{i}@example.com',
                'status': status,
                'effective_from': '2025-01-01T00:00:00',
                'effective_to': None,
                'rating': round(self.rng.uniform(3.5, 5.0), 2),
                'created_at': '2025-01-01T00:00:00'
            })
        self.data['Seller'] = sellers
    
    def generate_commission_rules(self):
        rules = []
        categories = ['ELECTRONICS', 'FASHION', 'HOME', 'BOOKS', 'TOYS']
        for i, cat in enumerate(categories):
            rule_id = self.id_gen.next_commission_rule()
            rules.append({
                'commission_rule_id': rule_id,
                'category': cat,
                'commission_rate': round(self.rng.uniform(0.08, 0.15), 4),
                'reserve_rate': round(self.rng.uniform(0.05, 0.10), 4),
                'effective_from': '2025-01-01T00:00:00',
                'effective_to': None,
                'is_active': True
            })
        self.data['CommissionRule'] = rules
    
    def generate_listings(self):
        listings = []
        sellers = self.data['Seller']
        rules = self.data['CommissionRule']
        categories = [r['category'] for r in rules]
        for i in range(self.config.listings):
            seller = self.rng.choice(sellers)
            rule = self.rng.choice(rules)
            listing_id = self.id_gen.next_listing(seller['seller_id'])
            listings.append({
                'listing_id': listing_id,
                'seller_id': seller['seller_id'],
                'commission_rule_id': rule['commission_rule_id'],
                'title': f'Product {i}',
                'category': rule['category'],
                'price': round(self.rng.uniform(10, 500), 2),
                'status': 'ACTIVE',
                'created_at': '2025-01-01T00:00:00'
            })
        self.data['ProductListing'] = listings
    
    def generate_orders(self):
        orders = []
        customers = self.data['Customer']
        for i in range(self.config.orders):
            order_id = self.id_gen.next_order()
            cust = self.rng.choice(customers)
            created = datetime(2026, 1, 1) + timedelta(days=self.rng.randint(0, 300), 
                                                       hours=self.rng.randint(0, 23))
            if self.rng.random() < 0.1:
                status = 'CONFIRMED'
            else:
                status = 'COMPLETED'
            orders.append({
                'order_id': order_id,
                'customer_id': cust['customer_id'],
                'status': status,
                'created_at': created.isoformat(),
                'confirmed_at': (created + timedelta(hours=1)).isoformat(),
                'completed_at': (created + timedelta(days=self.rng.randint(3, 14))).isoformat() if status == 'COMPLETED' else None,
                'currency': 'USD',
                'subtotal': 0.0  # Will be computed
            })
        self.data['Order'] = orders
    
    def generate_order_lines(self):
        order_lines = []
        orders = self.data['Order']
        listings = self.data['ProductListing']
        for order in orders:
            # Each order has 1-4 lines
            num_lines = self.rng.randint(1, 4)
            # 10% chance of multi-seller order (split)
            is_split = self.rng.random() < 0.10
            if is_split and num_lines >= 2:
                # Assign different sellers
                sellers_used = []
                for j in range(num_lines):
                    listing = self.rng.choice([l for l in listings if l['seller_id'] not in sellers_used or len(sellers_used) == 0])
                    sellers_used.append(listing['seller_id'])
                    line_id = self.id_gen.next_orderline()
                    qty = self.rng.randint(1, 3)
                    price = listing['price']
                    order_lines.append({
                        'order_line_id': line_id,
                        'order_id': order['order_id'],
                        'listing_id': listing['listing_id'],
                        'seller_id': listing['seller_id'],
                        'quantity': qty,
                        'unit_price': price,
                        'line_total': round(qty * price, 2)
                    })
            else:
                # Single seller order
                listing = self.rng.choice(listings)
                for j in range(num_lines):
                    line_id = self.id_gen.next_orderline()
                    qty = self.rng.randint(1, 3)
                    price = listing['price']
                    order_lines.append({
                        'order_line_id': line_id,
                        'order_id': order['order_id'],
                        'listing_id': listing['listing_id'],
                        'seller_id': listing['seller_id'],
                        'quantity': qty,
                        'unit_price': price,
                        'line_total': round(qty * price, 2)
                    })
        self.data['OrderLine'] = order_lines
        # Update order subtotals
        for order in orders:
            total = sum(ol['line_total'] for ol in order_lines if ol['order_id'] == order['order_id'])
            order['subtotal'] = round(total, 2)
    
    def generate_fulfillments(self):
        fulfillments = []
        order_lines = self.data['OrderLine']
        # Group by seller per order for split orders
        # Create fulfillment per (order, seller) combination
        seen = set()
        for ol in order_lines:
            key = (ol['order_id'], ol['seller_id'])
            if key not in seen:
                seen.add(key)
                fulfillment_id = self.id_gen.next_fulfillment_for_line(ol['order_line_id'])  # Will use pattern, but need to track properly
                # Better: create fulfillment with generated ID, store mapping
                fulfillment_id = f"FUL-{self.id_gen.counters['fulfillment'] + 1:06d}" if False else None  # placeholder
        # Simpler approach
        self.data['Fulfillment'] = []
        self.data['_fulfillment_map'] = {}  # (order_id, seller_id) -> fulfillment_id
    
    def generate_fulfillment_lines(self):
        fulfillments = []
        fulfillment_lines = []
        order_lines = self.data['OrderLine']
        orders = {o['order_id']: o for o in self.data['Order']}
        fulfillment_map = {}
        counter = 0
        
        # Group order lines by (order_id, seller_id)
        from collections import defaultdict
        groups = defaultdict(list)
        for ol in order_lines:
            groups[(ol['order_id'], ol['seller_id'])].append(ol)
        
        for (order_id, seller_id), lines in groups.items():
            counter += 1
            # FUL-<order-line-id> per requirement - use first order line's ID as base
            fulfillment_id = f"FUL-{lines[0]['order_line_id']}"
            fulfillment_map[(order_id, seller_id)] = fulfillment_id
            
            order = orders[order_id]
            created = datetime.fromisoformat(order['created_at'])
            # Ship within 1-5 days
            ship_delay = self.rng.randint(1, 5)
            promised = created + timedelta(days=ship_delay)
            shipped = created + timedelta(days=ship_delay + self.rng.randint(-1, 2))
            is_late = shipped > promised
            delivered = shipped + timedelta(days=self.rng.randint(1, 3))
            status = 'DELIVERED'
            if self.rng.random() < 0.05:  # 5% returns
                status = 'RETURNED'
            
            fulfillments.append({
                'fulfillment_id': fulfillment_id,
                'order_id': order_id,
                'seller_id': seller_id,
                'status': status,
                'created_at': (created + timedelta(hours=2)).isoformat(),
                'promised_ship_by': promised.isoformat(),
                'shipped_at': shipped.isoformat(),
                'delivered_at': delivered.isoformat(),
                'returned_at': (delivered + timedelta(days=self.rng.randint(1, 7))).isoformat() if status == 'RETURNED' else None,
                'is_late_shipment': is_late
            })
            
            for ol in lines:
                fulfillment_lines.append({
                    'fulfillment_line_id': f"FLL-{fulfillment_id}-{ol['order_line_id']}",
                    'fulfillment_id': fulfillment_id,
                    'order_line_id': ol['order_line_id'],
                    'quantity': ol['quantity']
                })
        
        self.data['Fulfillment'] = fulfillments
        self.data['FulfillmentLine'] = fulfillment_lines
        self.data['_fulfillment_map'] = fulfillment_map
    
    def generate_reviews(self):
        reviews = []
        orders = self.data['Order']
        order_lines = self.data['OrderLine']
        fulfillments = self.data['Fulfillment']
        delivered = [f for f in fulfillments if f['status'] == 'DELIVERED']
        for f in delivered[:len(delivered)//2]:  # Half get reviews
            ols = [ol for ol in order_lines if ol['order_id'] == f['order_id'] and ol['seller_id'] == f['seller_id']]
            if not ols:
                continue
            ol = ols[0]
            review_id = self.id_gen.next_review()
            delivered_at = datetime.fromisoformat(f['delivered_at'])
            reviews.append({
                'review_id': review_id,
                'order_id': f['order_id'],
                'order_line_id': ol['order_line_id'],
                'customer_id': [o['customer_id'] for o in orders if o['order_id'] == f['order_id']][0],
                'seller_id': f['seller_id'],
                'rating': self.rng.randint(1, 5),
                'comment': f'Review {review_id}',
                'created_at': (delivered_at + timedelta(days=self.rng.randint(1, 14))).isoformat()
            })
        self.data['CustomerReview'] = reviews
    
    def generate_disputes(self):
        disputes = []
        fulfillments = self.data['Fulfillment']
        orders = self.data['Order']
        delivered = [f for f in fulfillments if f['status'] in ['DELIVERED', 'RETURNED']]
        # Generate ~10000 disputes
        count = min(self.config.disputes, len(delivered))
        for i in range(count):
            f = self.rng.choice(delivered)
            dispute_id = self.id_gen.next_dispute()
            delivered_at = datetime.fromisoformat(f['delivered_at'])
            disputes.append({
                'dispute_id': dispute_id,
                'order_id': f['order_id'],
                'fulfillment_id': f['fulfillment_id'],
                'seller_id': f['seller_id'],
                'customer_id': [o['customer_id'] for o in orders if o['order_id'] == f['order_id']][0],
                'reason': self.rng.choice(['NOT_RECEIVED', 'DAMAGED', 'WRONG_ITEM', 'NOT_AS_DESCRIBED']),
                'amount': round(self.rng.uniform(20, 200), 2),
                'status': self.rng.choice(['OPEN', 'UNDER_REVIEW', 'RESOLVED_SELLER', 'RESOLVED_CUSTOMER', 'CHARGEBACK']),
                'created_at': (delivered_at + timedelta(days=self.rng.randint(1, 30))).isoformat(),
                'resolved_at': None
            })
        self.data['Dispute'] = disputes
    
    def generate_payouts(self):
        payouts = []
        sellers = self.data['Seller']
        # Weekly payouts
        start_date = datetime(2026, 1, 6)  # Monday
        for week in range(52):  # 52 weeks
            period_start = start_date + timedelta(weeks=week)
            period_end = period_start + timedelta(days=6)
            for seller in sellers:
                payout_id = self.id_gen.next_payout()
                payouts.append({
                    'payout_id': payout_id,
                    'seller_id': seller['seller_id'],
                    'period_start': period_start.date().isoformat(),
                    'period_end': period_end.date().isoformat(),
                    'payout_date': (period_end + timedelta(days=2)).date().isoformat(),
                    'status': 'PENDING',
                    'total_amount': 0.0,
                    'currency': 'USD'
                })
        self.data['Payout'] = payouts
    
    def generate_payout_lines(self):
        payout_lines = []
        payouts = self.data['Payout']
        fulfillments = self.data['Fulfillment']
        order_lines = self.data['OrderLine']
        orders = {o['order_id']: o for o in self.data['Order']}
        commission_rules = {r['commission_rule_id']: r for r in self.data['CommissionRule']}
        listings = {l['listing_id']: l for l in self.data['ProductListing']}
        
        # Group payouts by seller
        payouts_by_seller = {}
        for p in payouts:
            if p['seller_id'] not in payouts_by_seller:
                payouts_by_seller[p['seller_id']] = []
            payouts_by_seller[p['seller_id']].append(p)
        
        for f in fulfillments:
            if f['status'] != 'DELIVERED':
                continue
            delivered_at = datetime.fromisoformat(f['delivered_at'])
            # Eligible after 7 days hold
            eligible_date = delivered_at + timedelta(days=7)
            ols = [ol for ol in order_lines if ol['order_id'] == f['order_id'] and ol['seller_id'] == f['seller_id']]
            for ol in ols:
                listing = listings[ol['listing_id']]
                rule = commission_rules[listing['commission_rule_id']]
                gross = ol['line_total']
                commission = round(gross * rule['commission_rate'], 2)
                reserve = round(gross * rule['reserve_rate'], 2)
                net = round(gross - commission - reserve, 2)
                line_id = self.id_gen.next_payoutline()
                # Find appropriate payout period
                payout = None
                for p in payouts_by_seller.get(f['seller_id'], []):
                    pstart = datetime.fromisoformat(p['period_start'])
                    pend = datetime.fromisoformat(p['period_end'])
                    if pstart <= eligible_date <= pend + timedelta(days=10):
                        payout = p
                        break
                if not payout:
                    continue
                payout_lines.append({
                    'payout_line_id': line_id,
                    'payout_id': payout['payout_id'],
                    'order_id': f['order_id'],
                    'order_line_id': ol['order_line_id'],
                    'fulfillment_id': f['fulfillment_id'],
                    'seller_id': f['seller_id'],
                    'gross_amount': gross,
                    'commission_amount': commission,
                    'reserve_amount': reserve,
                    'refund_amount': 0.0,
                    'adjustment_amount': 0.0,
                    'net_amount': net,
                    'status': 'ELIGIBLE' if eligible_date <= datetime(2026, 12, 31) else 'HELD',
                    'eligible_at': eligible_date.isoformat()
                })
        self.data['PayoutLine'] = payout_lines
        # Update payout totals
        for p in payouts:
            total = sum(pl['net_amount'] for pl in payout_lines if pl['payout_id'] == p['payout_id'])
            p['total_amount'] = round(total, 2)
            p['status'] = 'ELIGIBLE' if total > 0 else 'PENDING'
        
        self.data['StateChangeEvent'] = self.state_events

def generate_data(seed=20261022, scale='full'):
    config = Config()
    config.seed = seed
    config.scale = scale
    gen = DataGenerator(config)
    return gen.generate_all()
