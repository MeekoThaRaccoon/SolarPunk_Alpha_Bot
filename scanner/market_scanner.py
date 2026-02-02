"""
Market Scanner - Collects data from various sources
"""

import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Opportunity:
    """Represents a trading opportunity"""
    symbol: str
    market_type: str
    current_price: float
    change_24h: float
    volume: float
    volatility: float
    potential_score: float
    metadata: Dict[str, Any]

class MarketScanner:
    """Scans multiple markets for trading opportunities"""
    
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def scan(self) -> List[Opportunity]:
        """Scan all configured markets"""
        opportunities = []
        
        # Scan crypto markets
        if 'crypto' in self.config.get('trading', {}).get('allowed_markets', []):
            opportunities.extend(self.scan_crypto())
        
        # Scan prediction markets
        if 'prediction' in self.config.get('trading', {}).get('allowed_markets', []):
            opportunities.extend(self.scan_prediction_markets())
        
        # Sort by potential score
        opportunities.sort(key=lambda x: x.potential_score, reverse=True)
        
        logger.info(f"Found {len(opportunities)} opportunities")
        return opportunities
    
    def scan_crypto(self) -> List[Opportunity]:
        """Scan cryptocurrency markets"""
        opportunities = []
        
        for symbol in self.config.get('data_sources', {}).get('crypto', []):
            try:
                data = self.get_crypto_data(symbol)
                
                if not data or len(data) < 2:
                    continue
                
                # Calculate metrics
                current_price = data['Close'].iloc[-1]
                prev_price = data['Close'].iloc[-24] if len(data) > 24 else data['Close'].iloc[0]
                change_24h = ((current_price - prev_price) / prev_price) * 100
                
                # Volume analysis
                current_volume = data['Volume'].iloc[-1]
                avg_volume = data['Volume'].mean()
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                # Volatility (standard deviation of recent returns)
                returns = data['Close'].pct_change().dropna()
                volatility = returns.std() * 100 if len(returns) > 0 else 0
                
                # Calculate potential score
                potential_score = self.calculate_crypto_score(
                    abs(change_24h), 
                    volume_ratio, 
                    volatility
                )
                
                if potential_score > 0.3:  # Threshold for consideration
                    opp = Opportunity(
                        symbol=symbol,
                        market_type='crypto',
                        current_price=current_price,
                        change_24h=change_24h,
                        volume=current_volume,
                        volatility=volatility,
                        potential_score=potential_score,
                        metadata={
                            'timeframe': '24h',
                            'volume_ratio': volume_ratio,
                            'support': data['Close'].min(),
                            'resistance': data['Close'].max(),
                            'data_points': len(data)
                        }
                    )
                    opportunities.append(opp)
                    
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        return opportunities
    
    def get_crypto_data(self, symbol: str, period: str = '1d', interval: str = '1h'):
        """Get cryptocurrency data from Yahoo Finance"""
        cache_key = f"crypto_{symbol}_{period}_{interval}"
        
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if not data.empty:
                self.cache[cache_key] = (time.time(), data)
                return data
                
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
        
        return None
    
    def scan_prediction_markets(self) -> List[Opportunity]:
        """Scan prediction markets (PredictIt, Polymarket)"""
        opportunities = []
        
        # Scan PredictIt markets
        if self.config.get('data_sources', {}).get('prediction_markets', {}).get('predictit', {}).get('enabled', False):
            opportunities.extend(self.scan_predictit())
        
        # Scan Polymarket
        if self.config.get('data_sources', {}).get('prediction_markets', {}).get('polymarket', {}).get('enabled', False):
            opportunities.extend(self.scan_polymarket())
        
        return opportunities
    
    def scan_predictit(self) -> List[Opportunity]:
        """Scan PredictIt markets"""
        opportunities = []
        
        try:
            # PredictIt public API
            url = "https://www.predictit.org/api/marketdata/all/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                markets = response.json().get('markets', [])
                
                for market in markets:
                    if market.get('status') == 'Open':
                        # Calculate opportunity score
                        volume = market.get('volume', 0)
                        contracts = market.get('contracts', [])
                        
                        if contracts:
                            # Find contracts with high probability shifts
                            for contract in contracts:
                                prob = contract.get('lastTradePrice', 0) * 100
                                vol = contract.get('volume', 0)
                                
                                if vol > 1000 and 30 < prob < 70:  # Mid-range probabilities often have movement
                                    score = self.calculate_prediction_score(prob, vol, market.get('volume', 0))
                                    
                                    if score > 0.4:
                                        opp = Opportunity(
                                            symbol=f"PI:{market['id']}:{contract['id']}",
                                            market_type='prediction',
                                            current_price=contract.get('lastTradePrice', 0),
                                            change_24h=0,  # Would need historical data
                                            volume=vol,
                                            volatility=10,  # Approximate
                                            potential_score=score,
                                            metadata={
                                                'market_name': market.get('shortName', ''),
                                                'contract_name': contract.get('name', ''),
                                                'probability': prob,
                                                'total_volume': market.get('volume', 0),
                                                'time_to_close': market.get('timeStamp', ''),
                                                'url': f"https://www.predictit.org/markets/detail/{market['id']}"
                                            }
                                        )
                                        opportunities.append(opp)
                                        
        except Exception as e:
            logger.error(f"Error scanning PredictIt: {e}")
        
        return opportunities
    
    def scan_polymarket(self) -> List[Opportunity]:
        """Scan Polymarket markets"""
        opportunities = []
        
        try:
            # Polymarket GraphQL API endpoint
            url = "https://gamma-api.polymarket.com/graphql"
            
            query = """
            query {
                markets(first: 20, orderBy: volume, orderDirection: desc) {
                    conditionId
                    question
                    volume
                    outcomeTokenPrices
                    liquidity
                }
            }
            """
            
            response = requests.post(url, json={'query': query}, timeout=10)
            
            if response.status_code == 200:
                markets = response.json().get('data', {}).get('markets', [])
                
                for market in markets:
                    volume = float(market.get('volume', 0))
                    prices = market.get('outcomeTokenPrices', [])
                    
                    if prices and len(prices) == 2:  # Binary markets
                        prob = float(prices[0]) * 100
                        
                        if 25 < prob < 75 and volume > 1000:
                            score = self.calculate_prediction_score(prob, volume, volume)
                            
                            if score > 0.4:
                                opp = Opportunity(
                                    symbol=f"PM:{market['conditionId']}",
                                    market_type='prediction',
                                    current_price=float(prices[0]),
                                    change_24h=0,
                                    volume=volume,
                                    volatility=15,
                                    potential_score=score,
                                    metadata={
                                        'question': market.get('question', ''),
                                        'liquidity': market.get('liquidity', 0),
                                        'probability': prob,
                                        'outcome_prices': prices,
                                        'url': f"https://polymarket.com/event/{market['conditionId']}"
                                    }
                                )
                                opportunities.append(opp)
                                
        except Exception as e:
            logger.error(f"Error scanning Polymarket: {e}")
        
        return opportunities
    
    def calculate_crypto_score(self, abs_change: float, volume_ratio: float, volatility: float) -> float:
        """Calculate a score for crypto opportunities"""
        # Normalize inputs
        norm_change = min(abs_change / 10, 1.0)  # 10% change = max score
        norm_volume = min(volume_ratio, 2.0) / 2.0  # 2x volume = max score
        norm_volatility = min(volatility / 5, 1.0)  # 5% volatility = max score
        
        # Weighted score
        score = (
            norm_change * 0.4 +      # Price change weight
            norm_volume * 0.3 +      # Volume weight
            norm_volatility * 0.3    # Volatility weight
        )
        
        return round(score, 2)
    
    def calculate_prediction_score(self, probability: float, contract_volume: float, market_volume: float) -> float:
        """Calculate a score for prediction market opportunities"""
        # Score is highest when probability is near 50% (maximum uncertainty)
        prob_score = 1 - abs(probability - 50) / 50
        
        # Volume score (normalized)
        vol_score = min(contract_volume / 5000, 1.0)
        
        # Combined score
        score = (prob_score * 0.6) + (vol_score * 0.4)
        
        return round(score, 2)
    
    def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get news sentiment for a symbol (placeholder implementation)"""
        # In a real implementation, this would use news APIs
        return {
            'sentiment': 'neutral',
            'article_count': 0,
            'last_updated': datetime.now().isoformat()
        }
