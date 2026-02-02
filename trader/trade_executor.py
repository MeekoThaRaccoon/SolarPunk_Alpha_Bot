"""
Trade Executor - Handles trade execution
"""

import time
from datetime import datetime

class TradeExecutor:
    def __init__(self, config):
        self.config = config
        self.positions = {}
        self.trade_history = []
    
    def execute(self, opportunity, analysis):
        """Execute a trade"""
        if analysis['recommendation'] != 'BUY':
            return None
        
        # Check position limits
        if not self.can_trade(opportunity['symbol']):
            return None
        
        trade = {
            'id': f"trade_{int(time.time())}",
            'symbol': opportunity['symbol'],
            'price': opportunity['price'],
            'quantity': self.calculate_position_size(opportunity),
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'status': 'EXECUTED' if self.config['bot']['mode'] == 'paper' else 'PENDING'
        }
        
        # Update position
        self.positions[opportunity['symbol']] = trade['quantity']
        self.trade_history.append(trade)
        
        return trade
    
    def can_trade(self, symbol):
        """Check if we can take a new position"""
        max_exposure = self.config['trading']['max_total_exposure']
        max_position = self.config['trading']['max_position_size']
        
        # Check total exposure
        total_exposure = sum(self.positions.values())
        if total_exposure >= max_exposure:
            return False
        
        # Check individual position
        current_position = self.positions.get(symbol, 0)
        if current_position >= max_position:
            return False
        
        return True
    
    def calculate_position_size(self, opportunity):
        """Calculate position size based on risk"""
        max_position = self.config['trading']['max_position_size']
        
        # Simple calculation: use 10% of max position for now
        position_value = max_position * 0.1
        quantity = position_value / opportunity['price']
        
        return round(quantity, 6)
    
    def get_open_positions(self):
        """Get all open positions"""
        return self.positions
    
    def get_trade_history(self):
        """Get trade history"""
        return self.trade_history
