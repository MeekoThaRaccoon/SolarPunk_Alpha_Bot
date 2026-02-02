"""
Donation Engine - Handles automatic redistribution of profits
"""

from datetime import datetime

class DonationEngine:
    def __init__(self, config):
        self.config = config
        self.donation_history = []
    
    def distribute(self, profit):
        """Distribute profits according to configured splits"""
        if profit <= 0:
            return None
        
        split = self.config['redistribution']['split']
        
        distribution = {
            'id': f"dist_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'total_profit': profit,
            'breakdown': {
                'crisis': profit * (split['crisis'] / 100),
                'you': profit * (split['you'] / 100),
                'network': profit * (split['network'] / 100)
            },
            'crisis_details': []
        }
        
        # Distribute to crisis organizations
        for org in self.config['redistribution']['crisis_orgs']:
            amount = distribution['breakdown']['crisis'] * (org['percentage'] / 100)
            
            org_distribution = {
                'organization': org['name'],
                'amount': amount,
                'wallet': org['wallet'],
                'chain': org['chain'],
                'status': 'PENDING'
            }
            
            distribution['crisis_details'].append(org_distribution)
        
        self.donation_history.append(distribution)
        
        return distribution
    
    def get_donation_history(self):
        """Get donation history"""
        return self.donation_history
    
    def get_total_donated(self):
        """Get total donated amount"""
        total = 0
        for donation in self.donation_history:
            total += donation['breakdown']['crisis']
        
        return total
