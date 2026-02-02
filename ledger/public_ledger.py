"""
Public Ledger - Transparent logging of all activities
"""

import json
import csv
from datetime import datetime
import os

class PublicLedger:
    def __init__(self, config):
        self.config = config
        self.ledger_dir = "./ledger"
        
        # Create ledger directory
        os.makedirs(self.ledger_dir, exist_ok=True)
        
        # Initialize CSV files with headers if they don't exist
        self.init_csv('trades.csv', ['ID', 'Timestamp', 'Symbol', 'Price', 'Quantity', 'Profit', 'Analysis'])
        self.init_csv('cycles.csv', ['Timestamp', 'Opportunities', 'Trades', 'Profit', 'Redistribution'])
        self.init_csv('donations.csv', ['ID', 'Timestamp', 'Organization', 'Amount', 'Wallet', 'Status'])
    
    def init_csv(self, filename, headers):
        """Initialize CSV file with headers if it doesn't exist"""
        filepath = os.path.join(self.ledger_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def log_trade(self, trade):
        """Log a trade to the public ledger"""
        filepath = os.path.join(self.ledger_dir, 'trades.csv')
        
        with open(filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trade['id'],
                trade['timestamp'],
                trade['symbol'],
                trade['price'],
                trade.get('quantity', 0),
                trade.get('profit', 0),
                json.dumps(trade.get('analysis', {}))
            ])
    
    def log_cycle(self, cycle_data):
        """Log a complete cycle"""
        filepath = os.path.join(self.ledger_dir, 'cycles.csv')
        
        with open(filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                cycle_data.get('timestamp', datetime.now().isoformat()),
                cycle_data.get('opportunities', 0),
                cycle_data.get('trades', 0),
                cycle_data.get('profit', 0),
                json.dumps(cycle_data.get('redistribution', {}))
            ])
    
    def log_donation(self, donation):
        """Log a donation"""
        filepath = os.path.join(self.ledger_dir, 'donations.csv')
        
        for org in donation.get('crisis_details', []):
            with open(filepath, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    donation['id'],
                    donation['timestamp'],
                    org['organization'],
                    org['amount'],
                    org['wallet'],
                    org['status']
                ])
    
    def get_public_url(self):
        """Get public URL for the ledger (for future GitHub Pages integration)"""
        return "Ledger stored locally. Future: GitHub Pages integration"
