#!/usr/bin/env python3
"""
SolarPunk Alpha Bot - Main Entry Point
Autonomous trading agent with 50% auto-redistribution
"""

import sys
import time
import signal
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import load_config
from core.logger import setup_logger
from core.state import BotState
from scanner.market_scanner import MarketScanner
from analyzer.ai_analyzer import AIAnalyzer
from trader.trade_executor import TradeExecutor
from redistributor.donation_engine import DonationEngine
from ledger.public_ledger import PublicLedger
from dashboard.server import DashboardServer

class SolarAlphaBot:
    """Main bot controller"""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize the bot with configuration"""
        self.config = load_config(config_path)
        self.logger = setup_logger(__name__, self.config.logging.level)
        
        # Initialize components
        self.state = BotState()
        self.scanner = MarketScanner(self.config)
        self.analyzer = AIAnalyzer(self.config)
        self.trader = TradeExecutor(self.config, self.state)
        self.redistributor = DonationEngine(self.config)
        self.ledger = PublicLedger(self.config)
        self.dashboard = DashboardServer(self.config, self.state) if self.config.dashboard.enabled else None
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        self.running = False
        self.cycle_count = 0
        
        self.logger.info("🤖 SolarPunk Alpha Bot initialized")
        self.logger.info(f"Mode: {self.config.bot.mode.upper()}")
        self.logger.info(f"Redistribution: {self.config.redistribution.split.crisis}% to crisis orgs")
        
    def run(self):
        """Main execution loop"""
        self.running = True
        
        # Start dashboard if enabled
        if self.dashboard:
            self.dashboard.start()
            self.logger.info(f"📊 Dashboard running on http://localhost:{self.config.dashboard.port}")
        
        # Initial scan
        self.run_cycle()
        
        # Main loop
        while self.running:
            try:
                # Calculate sleep time until next cycle
                next_cycle = self.get_next_cycle_time()
                sleep_time = (next_cycle - datetime.now()).total_seconds()
                
                if sleep_time > 0:
                    self.logger.info(f"⏳ Next scan in {sleep_time/60:.1f} minutes")
                    time.sleep(min(sleep_time, 300))  # Check every 5 minutes max
                else:
                    # Time for next cycle
                    self.run_cycle()
                    
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(60)  # Wait a minute before retrying
        
        self.shutdown()
    
    def run_cycle(self):
        """Execute one complete scan/analyze/trade cycle"""
        self.cycle_count += 1
        cycle_id = f"cycle-{self.cycle_count}-{datetime.now().strftime('%Y%m%d-%H%M')}"
        
        self.logger.info(f"🔄 Starting cycle {self.cycle_count} ({cycle_id})")
        
        try:
            # 1. Scan markets
            self.logger.info("📡 Scanning markets...")
            opportunities = self.scanner.scan()
            
            if not opportunities:
                self.logger.info("📭 No opportunities found")
                return
            
            # 2. Analyze with AI
            self.logger.info("🤖 Analyzing opportunities...")
            analyzed_opportunities = []
            
            for opp in opportunities[:3]:  # Limit to top 3
                analysis = self.analyzer.analyze(opp)
                if analysis and analysis.get('confidence', 0) > self.config.bot.risk_tolerance:
                    opp['analysis'] = analysis
                    analyzed_opportunities.append(opp)
            
            if not analyzed_opportunities:
                self.logger.info("🎯 No opportunities passed analysis")
                return
            
            # 3. Execute trades
            self.logger.info("💼 Executing trades...")
            trades = []
            
            for opp in analyzed_opportunities:
                if self.state.can_trade(opp, self.config):
                    trade = self.trader.execute(opp)
                    if trade:
                        trades.append(trade)
                        self.logger.info(f"✅ Trade executed: {trade['symbol']} at ${trade['price']}")
            
            if not trades:
                self.logger.info("📊 No trades executed (limits/constraints)")
                return
            
            # 4. Process completed trades (check periodically)
            self.process_completed_trades()
            
            # 5. Log everything
            self.ledger.log_cycle({
                'cycle_id': cycle_id,
                'opportunities_found': len(opportunities),
                'opportunities_analyzed': len(analyzed_opportunities),
                'trades_executed': len(trades),
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"✅ Cycle {self.cycle_count} completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error in cycle {self.cycle_count}: {e}", exc_info=True)
            self.ledger.log_error(cycle_id, str(e))
    
    def process_completed_trades(self):
        """Check for completed trades and handle redistribution"""
        completed = self.trader.get_completed_trades()
        
        for trade in completed:
            if not trade.get('processed'):
                # Calculate profits
                profit = trade.get('profit', 0)
                
                if profit > 0:
                    # Redistribute
                    redistribution = self.redistributor.distribute(profit)
                    
                    # Log to ledger
                    self.ledger.log_trade(trade)
                    self.ledger.log_redistribution(redistribution)
                    
                    self.logger.info(f"🌍 Redistributed ${profit:.2f}: {redistribution}")
                    
                    # Mark as processed
                    trade['processed'] = True
                    self.trader.update_trade(trade)
    
    def get_next_cycle_time(self):
        """Calculate when next cycle should run"""
        interval = self.config.bot.scan_interval_hours
        last_cycle = self.state.last_cycle_time or datetime.now() - timedelta(hours=interval)
        next_cycle = last_cycle + timedelta(hours=interval)
        return next_cycle
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received shutdown signal {signum}")
        self.running = False
    
    def shutdown(self):
        """Clean shutdown procedure"""
        self.logger.info("🛑 Shutting down SolarPunk Alpha Bot...")
        
        # Process any remaining trades
        self.process_completed_trades()
        
        # Stop dashboard
        if self.dashboard:
            self.dashboard.stop()
        
        # Final ledger update
        self.ledger.log_shutdown()
        
        self.logger.info("👋 Shutdown complete. Goodbye!")
        
        # Print summary
        print("\n" + "="*50)
        print("SOLARPUNK ALPHA BOT - FINAL REPORT")
        print("="*50)
        print(f"Cycles completed: {self.cycle_count}")
        print(f"Total trades: {self.state.total_trades}")
        print(f"Total profit: ${self.state.total_profit:.2f}")
        print(f"Total redistributed: ${self.state.total_redistributed:.2f}")
        print("="*50)
        print("Thank you for trading ethically 🌱")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='SolarPunk Alpha Bot')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--once', action='store_true', help='Run one cycle and exit')
    args = parser.parse_args()
    
    # Create and run bot
    bot = SolarAlphaBot(args.config)
    
    if args.once:
        bot.run_cycle()
        bot.shutdown()
    else:
        bot.run()
