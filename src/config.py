"""
Configuration for YottaFlex data generator
"""
import os
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 20261022
    scale: str = "full"  # "full" or "starter"
    
    # Full scale
    full_sellers: int = 2000
    full_listings: int = 20000
    full_orders: int = 100000
    full_disputes: int = 10000
    
    # Starter scale
    starter_sellers: int = 200
    starter_listings: int = 2000
    starter_orders: int = 10000
    starter_disputes: int = 1000
    
    @property
    def sellers(self):
        return self.full_sellers if self.scale == "full" else self.starter_sellers
    
    @property
    def listings(self):
        return self.full_listings if self.scale == "full" else self.starter_listings
    
    @property
    def orders(self):
        return self.full_orders if self.scale == "full" else self.starter_orders
    
    @property
    def disputes(self):
        return self.full_disputes if self.scale == "full" else self.starter_disputes
    
    @property
    def output_dir(self):
        return f"data/generated/{self.scale}"
    
    @property
    def ground_truth_dir(self):
        return "ground_truth"

config = Config()
