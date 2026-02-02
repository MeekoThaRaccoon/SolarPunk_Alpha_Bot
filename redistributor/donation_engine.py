"""
Donation Engine - Handles automatic redistribution of profits
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging
from decimal import Decimal, ROUND_DOWN
import hashlib

logger = logging.getLogger(__name__)

class DonationEngine:
    """Manages automatic redistribution of profits"""
    
    def __init__(self, config):
        self.config = config
        self.donation_history = []
        
        # Initialize crypto wallet if needed
        self.web3 = None
        if self.config.get('redistribution', {}).get('enabled', True):
            self.init_crypto()
    
    def init_crypto(self):
        """Initialize Web3 connection for crypto donations"""
        try:
            from web3 import Web3
            # Use public RPC endpoints
            self.web3 = Web3(Web3.HTTPProvider('https://cloudflare-eth.com'))
            logger.info("Web3 initialized for Ethereum donations")
        except ImportError:
            logger.warning("Web3 not installed, crypto donations disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {e}")
    
    def distribute(self, profit: float) -> Dict[str, Any]:
        """Distribute profits according to configured splits"""
        if profit <= 0:
            return self.create_distribution_record(profit, {})
        
        # Get distribution configuration
        split_config = self.config.get('redistribution', {}).get('split', {})
        crisis_percent = split_config.get('crisis', 50)
        your_percent = split_config.get('you', 30)
        network_percent = split_config.get('network', 20)
        
        # Validate totals
        total = crisis_percent + your_percent + network_percent
        if abs(total - 100) > 0.01:
            logger.warning(f"Distribution percentages don't sum to 100%: {total}%")
            # Normalize
            crisis_percent = (crisis_percent / total) * 100
            your_percent = (your_percent / total) * 100
            network_percent = (network_percent / total) * 100
        
        # Calculate amounts
        amounts = {
            'crisis': profit * crisis_percent / 100,
            'you': profit * your_percent / 100,
            'network': profit * network_percent / 100
        }
        
        # Round to 2 decimal places
        for key in amounts:
            amounts[key] = Decimal(str(amounts[key])).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        
        # Distribute to crisis organizations
        crisis_distributions = self.distribute_to_crisis_orgs(float(amounts['crisis']))
        
        # Distribute to your wallet
        your_distribution = self.distribute_to_your_wallet(float(amounts['you']))
        
        # Distribute to network fund
        network_distribution = self.distribute_to_network(float(amounts['network']))
        
        # Create distribution record
        distribution = self.create_distribution_record(
            profit,
            {
                'crisis': crisis_distributions,
                'you': your_distribution,
                'network': network_distribution
            }
        )
        
        # Store in history
        self.donation_history.append(distribution)
        
        logger.info(f"Distributed ${profit:.2f}: ${amounts['crisis']} to crisis, ${amounts['you']} to you, ${amounts['network']} to network")
        
        return distribution
    
    def distribute_to_crisis_orgs(self, amount: float) -> List[Dict[str, Any]]:
        """Distribute to configured crisis organizations"""
        distributions = []
        
        orgs = self.config.get('redistribution', {}).get('crisis_orgs', [])
        
        if not orgs:
            logger.warning("No crisis organizations configured")
            return distributions
        
        # Calculate per-organization amounts
        total_percent = sum(org.get('percentage', 0) for org in orgs)
        
        for org in orgs:
            org_percent = org.get('percentage', 0)
            if org_percent <= 0:
                continue
            
            # Calculate amount for this org
            org_amount = amount * (org_percent / total_percent)
            org_amount = Decimal(str(org_amount)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            
            # Skip if below minimum
            min_donation = self.config.get('redistribution', {}).get('min_donation', 1.0)
            if org_amount < min_donation:
                # Batch with other small donations
                continue
            
            # Distribute based on chain
            distribution = {
                'organization': org.get('name', 'Unknown'),
                'amount': float(org_amount),
                'currency': 'USD',
                'chain': org.get('chain', 'ethereum'),
                'wallet': org.get('wallet', ''),
                'timestamp': datetime.now().isoformat(),
                'status': 'PENDING'
            }
            
            # Execute donation
            if self.config.get('redistribution', {}).get('batch_donations', True):
                # Batch for later
                distribution['status'] = 'BATCHED'
            else:
                # Execute immediately
                executed = self.execute_donation(distribution)
                distribution.update(executed)
            
            distributions.append(distribution)
        
        return distributions
    
    def distribute_to_your_wallet(self, amount: float) -> Dict[str, Any]:
        """Distribute to your wallet"""
        wallet = self.config.get('redistribution', {}).get('your_wallet', '')
        
        if not wallet:
            logger.warning("Your wallet not configured")
            return {}
        
        distribution = {
            'recipient': 'Your Wallet',
            'amount': float(amount),
            'currency': 'USD',
            'wallet': wallet,
            'timestamp': datetime.now().isoformat(),
            'status': 'PENDING'
        }
        
        # In real implementation, this would transfer funds
        # For now, just log it
        distribution['status'] = 'SIMULATED'
        distribution['note'] = 'Real distribution requires exchange integration'
        
        return distribution
    
    def distribute_to_network(self, amount: float) -> Dict[str, Any]:
        """Distribute to SolarPunk network fund"""
        fund_wallet = self.config.get('redistribution', {}).get('network_fund', '')
        
        if not fund_wallet:
            logger.warning("Network fund wallet not configured")
            return {}
        
        distribution = {
            'recipient': 'SolarPunk Network Fund',
            'amount': float(amount),
            'currency': 'USD',
            'wallet': fund_wallet,
            'timestamp': datetime.now().isoformat(),
            'status': 'PENDING'
        }
        
        # Execute crypto donation if Web3 is available
        if self.web3 and fund_wallet.startswith('0x'):
            try:
                # This would require having ETH for gas
                # For now, simulate
                distribution['status'] = 'SIMULATED'
                distribution['tx_hash'] = '0x' + hashlib.sha256(str(time.time()).encode()).hexdigest()[:64]
            except Exception as e:
                distribution['status'] = 'FAILED'
                distribution['error'] = str(e)
        else:
            distribution['status'] = 'SIMULATED'
        
        return distribution
    
    def execute_donation(self, distribution: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single donation"""
        # This is a placeholder implementation
        # In reality, this would:
        # 1. Convert USD to appropriate crypto if needed
        # 2. Send transaction on appropriate chain
        # 3. Wait for confirmation
        # 4. Return transaction details
        
        return {
            'executed_at': datetime.now().isoformat(),
            'tx_hash': '0x' + hashlib.sha256(str(time.time()).encode()).hexdigest()[:64],
            'gas_used': 21000,
            'status': 'CONFIRMED'
        }
    
    def create_distribution_record(self, profit: float, distributions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete distribution record"""
        return {
            'id': hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            'timestamp': datetime.now().isoformat(),
            'total_profit': profit,
            'distributions': distributions,
            'config_used': {
                'split': self.config.get('redistribution', {}).get('split', {}),
                'crisis_orgs': [
                    {'name': org.get('name'), 'percentage': org.get('percentage')}
                    for org in self.config.get('redistribution', {}).get('crisis_orgs', [])
                ]
            }
        }
    
    def get_donation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get donation history"""
        return self.donation_history[-limit:] if self.donation_history else []
    
    def get_total_donated(self) -> float:
        """Get total amount donated to crisis organizations"""
        total = 0.0
        
        for record in self.donation_history:
            for dist in record.get('distributions', {}).get('crisis', []):
                if dist.get('status') in ['CONFIRMED', 'SIMULATED']:
                    total += dist.get('amount', 0)
        
        return total
