🤖 SolarPunk Alpha Bot

*Autonomous trading agent that redistributes 50% of gains to crisis response*

## ✨ What It Is
An open-source, zero-cost trading/research agent that:
- Scans markets for opportunities
- Uses local LLM analysis (no API fees)
- Executes with transparent paper trading
- **Auto-redistributes 50%** of gains to verified crisis organizations
- Logs everything to a public ledger

## 🎯 Core Principles
1. **Sovereignty**: Runs entirely on your hardware, no third-party dependencies
2. **Transparency**: Every trade, every analysis, every donation is public
3. **Redistribution**: 50% minimum to crisis response (non-negotiable)
4. **Open Source**: MIT licensed, fork it, modify it, make it yours

## 🚀 Quick Start

### Install (2 minutes):
```bash
# Clone and setup
git clone https://github.com/SolarPunk-Infra/Alpha-Bot.git
cd Alpha-Bot
chmod +x install.sh && ./install.sh
Configure (1 minute):
bash
cp config.yaml.example config.yaml
# Edit with your preferences (see below)
Run (0 minutes - runs automatically):
bash
# The bot auto-runs every 6 hours via systemd
# Check status:
systemctl status solar-alpha
🛠️ How It Works
Data Flow:
text
1. Scanner → Collects market data (crypto, prediction markets, etc.)
2. Analyzer → Local LLM analyzes opportunities
3. Trader → Executes paper trades (optionally real)
4. Redistributor → Sends 50% to crisis orgs, 30% to you, 20% to network
5. Ledger → Logs everything to public Google Sheet/local file
Current Capabilities:
Crypto Markets: BTC, ETH, SOL, ADA via Yahoo Finance

Prediction Markets: PredictIt (US politics), Polymarket (crypto)

Analysis: Local Llama 3.2 7B (runs on CPU)

Execution: Paper trading with optional real execution

Redistribution: Auto-donations via crypto or direct ACH

📊 Live Dashboard
Once running, view your:

Live Trades (public)

Redistribution Tracker (blockchain)

Bot Status (local web UI)

⚙️ Configuration
config.yaml Options:
yaml
bot:
  mode: "paper"  # paper, real, or simulation
  scan_interval_hours: 6
  risk_tolerance: "medium"  # low, medium, high
  
redistribution:
  crisis_orgs:
    - name: "World Central Kitchen"
      percentage: 25
      address: "0x..."
    - name: "Doctors Without Borders"
      percentage: 25
      address: "0x..."
  your_wallet: "0xYOUR_ADDRESS"
  network_fund: "0xNETWORK_ADDRESS"  # For growing SolarPunk
  
trading:
  max_position_size: 100  # USD
  allowed_markets: ["crypto", "prediction"]
  stop_loss_percent: 10
🧠 Local AI Setup
The bot uses a quantized 7B parameter model that runs on CPU:

bash
# Download model (4GB, runs on Raspberry Pi)
./scripts/download_model.sh

# Or use your own model
echo "MODEL_PATH=/path/to/your/model.gguf" >> .env
📈 Example Trade
text
[2026-02-01 14:30:00] 📈 SCANNER: BTC dropped 5.2% in 1h
[2026-02-01 14:31:00] 🤖 ANALYZER: "Likely temporary correction. News shows..."
[2026-02-01 14:32:00] 💼 TRADER: Buying $50 BTC at $41,200
[2026-02-01 16:00:00] 📈 TRADER: BTC up 3.1%, selling for $51.55 profit
[2026-02-01 16:01:00] 🌍 REDISTRIBUTOR: $25.78 to WCK, $15.47 to you, $10.30 to network
[2026-02-01 16:02:00] 📖 LEDGER: Trade logged to sheet, receipt stored on IPFS
🔧 Development
Project Structure:
text
alpha-bot/
├── scanner/          # Market data collection
├── analyzer/         # Local LLM analysis
├── trader/           # Trade execution
├── redistributor/    # Auto-donation system
├── ledger/          # Public transparency
├── web/             # Local dashboard
└── scripts/         # Setup and maintenance
Adding a New Market:
Create scanner/new_market.py

Add to config allowed_markets

Submit PR to main repo

Creating a Custom Analysis:
Modify analyzer/prompts/

Test with python -m analyzer.test_new_prompt

The bot will learn from successful trades

🌐 Network Features
Join the Alpha Bot Collective:
bash
# Share your successful strategies
./scripts/share_strategy.py "My volatility play"

# Learn from others
./scripts/download_strategies.py

# All strategies are open-source, forkable, improvable
Transparency Verification:
Public Ledger: All trades on Google Sheets

Blockchain Proof: Redistributions on Ethereum/Polygon

Receipt Storage: IPFS hashes for all donations

Live Dashboard: Real-time monitoring

⚠️ Important Notes
Risk Disclosure:
This is experimental software

Start with paper trading only

Never risk more than you can lose

The 50% redistribution is non-negotiable

Legal:
Check your local trading regulations

Report taxes appropriately

The software is MIT licensed - you are responsible for its use

Ethical Framework:
No exploitation: Never profit from crisis or suffering

Maximum transparency: Everything public by default

Network growth: Help others deploy their own bots

Continuous redistribution: Even in loss, donate time/skills

🚨 Emergency Stop
bash
# Immediately halt all trading
./scripts/emergency_stop.sh

# Will complete current trades and donations
# Then shut down cleanly
🤝 Contributing
We need:

Market scanners for new opportunities

Risk models for different strategies

Redistribution channels to verified orgs

Dashboard developers for better visualization

Documentation writers to help newcomers

See CONTRIBUTING.md for details.

📚 Learn More
SolarPunk Manifesto

Local LLM Guide

Crypto Donation Infrastructure

Transparent Ledger Design

📄 License
MIT - see LICENSE for details.

"We don't build bots to escape the system. We build bots that change what the system rewards."

Start small. Trade ethically. Redistribute radically.
