"""
Market Scanner - Collects data from various sources
"""

import yfinance as yf
import requests
from datetime import datetime
import time

class MarketScanner:
    def __init__(self, config):
        self.config = config
    
    def scan_crypto(self):
        """Scan cryptocurrency markets"""
        opportunities = []
        
        for symbol in self.config['data_sources']['crypto']:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d", interval="1h")
                
                if len(data) > 0:
                    current = data['Close'].iloc[-1]
                    prev = data['Close'].iloc[-2] if len(data) > 1 else current
                    change = ((current - prev) / prev) * 100
                    
                    opportunities.append({
                        'symbol': symbol,
                        'price': current,
                        'change': change,
                        'type': 'crypto',
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        return opportunities
    
    def scan_prediction_markets(self):
        """Scan prediction markets"""
        opportunities = []
        
        # PredictIt
        if self.config['data_sources']['prediction_markets']['predictit']:
            try:
                response = requests.get('https://www.predictit.org/api/marketdata/all/', timeout=10)
                if response.status_code == 200:
                    markets = response.json().get('markets', [])
                    
                    for market in markets[:5]:  # Top 5 markets
                        if market.get('status') == 'Open':
                            opportunities.append({
                                'symbol': f"PI:{market['id']}",
                                'price': market.get('volume', 0),
                                'change': 0,
                                'type': 'prediction',
                                'name': market.get('shortName', 'Unknown'),
                                'timestamp': datetime.now().isoformat()
                            })
                            
            except Exception as e:
                print(f"Error scanning PredictIt: {e}")
        
        return opportunities
    
    def scan(self):
        """Run all scans"""
        opportunities = []
        opportunities.extend(self.scan_crypto())
        opportunities.extend(self.scan_prediction_markets())
        
        return opportunities
