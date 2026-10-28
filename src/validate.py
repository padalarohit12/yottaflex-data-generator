"""
CLI entrypoint for validation
"""
import sys
from pathlib import Path
import csv

def main():
    data_dir = "data/generated/full"
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--data-dir' and i+1 < len(args):
            data_dir = args[i+1]
    
    print(f"Validating data in {data_dir}")
    data_path = Path(data_dir) / 'csv'
    if not data_path.exists():
        print(f"Error: {data_path} does not exist")
        return
    
    required = ['Customer.csv', 'Seller.csv', 'ProductListing.csv', 'Order.csv', 
                'OrderLine.csv', 'Fulfillment.csv', 'FulfillmentLine.csv',
                'CustomerReview.csv', 'Dispute.csv', 'CommissionRule.csv',
                'Payout.csv', 'PayoutLine.csv']
    
    for r in required:
        if (data_path / r).exists():
            with open(data_path / r) as f:
                rows = sum(1 for _ in csv.DictReader(f))
            print(f"OK {r}: {rows} rows")
        else:
            print(f"MISSING {r}")
    
    print("\nValidation complete")

if __name__ == "__main__":
    main()
