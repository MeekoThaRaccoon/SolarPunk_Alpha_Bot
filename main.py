#!/usr/bin/env python3
"""
SolarPunk Alpha Bot - Main Entry Point
"""

import sys
import time
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml
import schedule
from loguru import logger
from datetime import datetime

class SolarAlphaBot:
    def __init__(self, config_path="config.yaml"):
        self.load_config(config_path)
        self.setup_logging()
        self.running = False
        
        logger.info("🤖 SolarPunk Alpha Bot initialized")
        logger.info(f"Mode: {self.config['bot']['mode'].upper()}")
        logger.info(f"Redistribution: {self.config['redistribution']['split']['crisis']}% to crisis orgs")
    
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def setup_logging(self):
        logger.remove()
        logger.add(sys.stdout, level=self.config['logging']['level'])
        if self.config['logging']['file']:
            logger.add(self.config['logging']['file_path'], rotation="1 day")
    
    def scan_markets(self):
        """Scan markets for opportunities"""
        logger.info("📡 Scanning markets...")
        
        # Simulated scanning
        opportunities = [
            {"symbol": "BTC-USD", "price": 42000, "change": 2.5, "potential": 0.7},
            {"symbol": "ETH-USD", "price": 2500, "change": 1.8, "potential": 0.5}
        ]
        
        for opp in opportunities:
            logger.info(f"Found: {opp['symbol']} at ${opp['price']} ({opp['change']}% change)")
        
        return opportunities
    
    def analyze_opportunity(self, opportunity):
        """Analyze opportunity with AI"""
        logger.info(f"🤖 Analyzing {opportunity['symbol']}...")
        
        # Simulated AI analysis
        analysis = {
            "confidence": opportunity['potential'] * 10,
            "recommendation": "BUY" if opportunity['potential'] > 0.6 else "HOLD",
            "reason": "Strong momentum detected" if opportunity['change'] > 2 else "Neutral trend"
        }
        
        return analysis
    
    def execute_trade(self, opportunity, analysis):
        """Execute trade based on analysis"""
        if analysis['recommendation'] != 'BUY':
            return None
        
        trade = {
            "id": f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "symbol": opportunity['symbol'],
            "price": opportunity['price'],
            "quantity": 0.01,  # Small position
            "timestamp": datetime.now().isoformat(),
            "profit": opportunity['price'] * 0.01  # Simulated 1% profit
        }
        
        logger.info(f"💼 Executed trade: {trade['symbol']} at ${trade['price']}")
        return trade
    
    def redistribute_profits(self, profit):
        """Redistribute profits according to config"""
        split = self.config['redistribution']['split']
        
        crisis_amount = profit * (split['crisis'] / 100)
        your_amount = profit * (split['you'] / 100)
        network_amount = profit * (split['network'] / 100)
        
        logger.info(f"🌍 Redistributing ${profit:.2f}:")
        logger.info(f"  - Crisis orgs: ${crisis_amount:.2f}")
        logger.info(f"  - Your wallet: ${your_amount:.2f}")
        logger.info(f"  - Network: ${network_amount:.2f}")
        
        return {
            "crisis": crisis_amount,
            "you": your_amount,
            "network": network_amount
        }
    
    def run_cycle(self):
        """Run one complete cycle"""
        logger.info("🔄 Starting trading cycle...")
        
        # 1. Scan markets
        opportunities = self.scan_markets()
        
        # 2. Analyze and execute
        total_profit = 0
        for opp in opportunities[:2]:  # Limit to 2 trades per cycle
            analysis = self.analyze_opportunity(opp)
            trade = self.execute_trade(opp, analysis)
            
            if trade:
                total_profit += trade['profit']
        
        # 3. Redistribute if there's profit
        if total_profit > 0:
            self.redistribute_profits(total_profit)
        
        logger.info(f"✅ Cycle complete. Total profit: ${total_profit:.2f}")
    
    def start(self):
        """Start the bot"""
        self.running = True
        
        # Set up schedule
        interval = self.config['bot']['scan_interval_hours']
        schedule.every(interval).hours.do(self.run_cycle)
        
        # Run immediately
        self.run_cycle()
        
        logger.info(f"🚀 Bot started. Will run every {interval} hours.")
        
        # Keep running
        while self.running:
            schedule.run_pending()
            time.sleep(60)
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        logger.info("🛑 Bot stopped")

def signal_handler(signum, frame):
    logger.info("Received shutdown signal")
    raise KeyboardInterrupt

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    bot = SolarAlphaBot()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        bot.stop()
