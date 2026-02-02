"""
Trade Executor - Handles trade execution (paper and real)
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging
from dataclasses import dataclass
import hashlib
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Represents a trade"""
    id: str
    symbol: str
    type: str  # BUY, SELL
    quantity: float
    price: float
    timestamp: datetime
    status: str  # PENDING, EXECUTED, CANCELLED, CLOSED
    profit: float = 0.0
    metadata: Dict[str, Any] = None

class TradeExecutor:
    """Executes trades and manages positions"""
    
    def __init__(self, config, state):
        self.config = config
        self.state = state
        self.mode = config.get('bot', {}).get('mode', 'paper')
        self.positions = {}
        self.trade_history = []
        
        # Initialize exchange connections if in real mode
        if self.mode == 'real':
            self.init_exchanges()
    
    def init_exchanges(self):
        """Initialize exchange connections for real trading"""
        self.exchanges = {}
        
        exchange_configs = self.config.get('trading', {}).get('exchanges', {})
        
        if exchange_configs.get('binance', {}).get('enabled', False):
            try:
                import ccxt
                config = exchange_configs['binance']
                self.exchanges['binance'] = ccxt.binance({
                    'apiKey': config.get('api_key', ''),
                    'secret': config.get('api_secret', ''),
                    'enableRateLimit': True
                })
                logger.info("Binance exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Binance: {e}")
        
        if exchange_configs.get('alpaca', {}).get('enabled', False):
            try:
                import alpaca_trade_api as tradeapi
                config = exchange_configs['alpaca']
                self.exchanges['alpaca'] = tradeapi.REST(
                    config.get('api_key', ''),
                    config.get('api_secret', ''),
                    base_url='https://paper-api.alpaca.markets' if config.get('paper', True) else 'https://api.alpaca.markets'
                )
                logger.info("Alpaca exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Alpaca: {e}")
    
    def execute(self, opportunity: Dict[str, Any], analysis: Dict[str, Any]) -> Trade:
        """Execute a trade based on opportunity and analysis"""
        try:
            # Check if we can trade
            if not self.can_trade(opportunity, analysis):
                logger.warning(f"Cannot trade {opportunity.get('symbol')}: constraints not met")
                return None
            
            # Generate trade ID
            trade_id = self.generate_trade_id(opportunity)
            
            # Determine trade parameters
            trade_params = self.calculate_trade_parameters(opportunity, analysis)
            
            # Create trade object
            trade = Trade(
                id=trade_id,
                symbol=opportunity.get('symbol'),
                type=analysis.get('recommendation', 'HOLD'),
                quantity=trade_params['quantity'],
                price=opportunity.get('current_price', 0),
                timestamp=datetime.now(),
                status='PENDING',
                metadata={
                    'opportunity': opportunity,
                    'analysis': analysis,
                    'trade_params': trade_params
                }
            )
            
            # Execute based on mode
            if self.mode == 'paper':
                executed_trade = self.execute_paper_trade(trade)
            elif self.mode == 'real':
                executed_trade = self.execute_real_trade(trade)
            else:  # simulation
                executed_trade = self.execute_simulation_trade(trade)
            
            if executed_trade:
                # Update state
                self.state.add_trade(executed_trade)
                self.trade_history.append(executed_trade)
                
                # Update position
                self.update_position(executed_trade)
                
                logger.info(f"Trade executed: {executed_trade}")
                return executed_trade
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
        
        return None
    
    def can_trade(self, opportunity: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Check if trade meets all constraints"""
        # Check recommendation
        if analysis.get('recommendation', 'HOLD') == 'HOLD':
            return False
        
        # Check confidence
        if analysis.get('confidence', 0) < 5:
            return False
        
        # Check ethical override
        if analysis.get('ethical_override', False):
            return False
        
        # Check position limits
        symbol = opportunity.get('symbol')
        current_position = self.positions.get(symbol, 0)
        
        max_position = self.config.get('trading', {}).get('max_position_size', 100)
        if abs(current_position) >= max_position:
            return False
        
        # Check daily trade limit
        today = datetime.now().date()
        today_trades = [t for t in self.trade_history 
                       if t.timestamp.date() == today and t.status == 'EXECUTED']
        
        max_daily = self.config.get('bot', {}).get('max_daily_trades', 3)
        if len(today_trades) >= max_daily:
            return False
        
        # Check total exposure
        total_exposure = sum(abs(p) for p in self.positions.values())
        max_exposure = self.config.get('trading', {}).get('max_total_exposure', 300)
        if total_exposure >= max_exposure:
            return False
        
        return True
    
    def calculate_trade_parameters(self, opportunity: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate trade size and parameters"""
        # Get suggested position size from analysis
        suggested_size = analysis.get('position_size', 0.05)  # Default 5%
        confidence = analysis.get('confidence', 5) / 10  # Normalize to 0-1
        
        # Adjust based on confidence
        adjusted_size = suggested_size * confidence
        
        # Cap at max position size
        max_position = self.config.get('trading', {}).get('max_position_size', 100)
        portfolio_value = self.state.get_portfolio_value()
        
        position_value = min(
            portfolio_value * adjusted_size,
            max_position
        )
        
        # Calculate quantity
        price = opportunity.get('current_price', 1)
        quantity = position_value / price if price > 0 else 0
        
        # Round based on market
        if opportunity.get('market_type') == 'crypto':
            quantity = Decimal(str(quantity)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
        else:
            quantity = Decimal(str(quantity)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        
        return {
            'position_value': float(position_value),
            'quantity': float(quantity),
            'percentage_of_portfolio': adjusted_size,
            'confidence_multiplier': confidence
        }
    
    def execute_paper_trade(self, trade: Trade) -> Trade:
        """Execute a paper trade (simulated)"""
        # Simulate execution with slight price variation
        import random
        price_variation = random.uniform(-0.001, 0.001)  # 0.1% variation
        executed_price = trade.price * (1 + price_variation)
        
        trade.price = executed_price
        trade.status = 'EXECUTED'
        
        # Simulate order fill
        time.sleep(0.1)
        
        logger.info(f"Paper trade executed: {trade.symbol} {trade.type} {trade.quantity} @ ${trade.price}")
        return trade
    
    def execute_real_trade(self, trade: Trade) -> Trade:
        """Execute a real trade on an exchange"""
        try:
            # Determine which exchange to use based on symbol
            exchange = self.get_exchange_for_symbol(trade.symbol)
            
            if not exchange:
                logger.error(f"No exchange configured for {trade.symbol}")
                trade.status = 'CANCELLED'
                return trade
            
            # Execute trade
            if trade.type == 'BUY':
                order = exchange.create_market_buy_order(
                    symbol=trade.symbol,
                    amount=trade.quantity
                )
            else:  # SELL
                order = exchange.create_market_sell_order(
                    symbol=trade.symbol,
                    amount=trade.quantity
                )
            
            # Update trade with execution details
            trade.price = order.get('price', trade.price)
            trade.quantity = order.get('filled', trade.quantity)
            trade.status = 'EXECUTED'
            trade.metadata['order_id'] = order.get('id')
            trade.metadata['exchange'] = exchange.id
            
            logger.info(f"Real trade executed: {order}")
            return trade
            
        except Exception as e:
            logger.error(f"Failed to execute real trade: {e}")
            trade.status = 'CANCELLED'
            trade.metadata['error'] = str(e)
            return trade
    
    def execute_simulation_trade(self, trade: Trade) -> Trade:
        """Execute a simulation trade (for backtesting)"""
        trade.status = 'EXECUTED'
        trade.metadata['simulation'] = True
        return trade
    
    def get_exchange_for_symbol(self, symbol: str):
        """Get appropriate exchange for a symbol"""
        if 'PI:' in symbol:  # PredictIt
            return None  # Would need PredictIt API
        elif 'PM:' in symbol:  # Polymarket
            return None  # Would need Polymarket API
        else:  # Assume crypto
            return self.exchanges.get('binance')
    
    def generate_trade_id(self, opportunity: Dict[str, Any]) -> str:
        """Generate unique trade ID"""
        base = f"{opportunity.get('symbol')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return hashlib.md5(base.encode()).hexdigest()[:8]
    
    def update_position(self, trade: Trade):
        """Update position tracking"""
        symbol = trade.symbol
        
        if symbol not in self.positions:
            self.positions[symbol] = 0
        
        if trade.type == 'BUY':
            self.positions[symbol] += trade.quantity
        else:  # SELL
            self.positions[symbol] -= trade.quantity
    
    def close_position(self, symbol: str, reason: str = "manual"):
        """Close an open position"""
        if symbol not in self.positions or self.positions[symbol] == 0:
            return None
        
        quantity = abs(self.positions[symbol])
        position_type = 'SELL' if self.positions[symbol] > 0 else 'BUY'
        
        # Create closing trade
        closing_trade = Trade(
            id=self.generate_trade_id({'symbol': symbol}),
            symbol=symbol,
            type=position_type,
            quantity=quantity,
            price=self.get_current_price(symbol),
            timestamp=datetime.now(),
            status='PENDING',
            metadata={'close_reason': reason}
        )
        
        # Execute close
        if self.mode == 'paper':
            return self.execute_paper_trade(closing_trade)
        elif self.mode == 'real':
            return self.execute_real_trade(closing_trade)
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol (placeholder)"""
        # In real implementation, fetch from exchange or data source
        return 0.0
    
    def get_completed_trades(self) -> List[Trade]:
        """Get trades that have been executed but not yet processed"""
        return [t for t in self.trade_history 
                if t.status == 'EXECUTED' 
                and not t.metadata.get('processed', False)]
    
    def update_trade(self, trade: Trade):
        """Update a trade in history"""
        for i, t in enumerate(self.trade_history):
            if t.id == trade.id:
                self.trade_history[i] = trade
                break
