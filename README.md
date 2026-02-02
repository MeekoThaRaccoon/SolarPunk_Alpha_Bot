# 🤖 SolarPunk Alpha Bot

*Autonomous trading agent that redistributes 50% of gains to crisis response*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SolarPunk Protocol](https://img.shields.io/badge/Protocol-SolarPunk-00ff9d)](https://github.com/SolarPunk-Infra)

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
git clone https://github.com/SolarPunk-Infra/Alpha-Bot.git
cd Alpha-Bot
chmod +x install.sh && ./install.sh
Configure (1 minute):
bash
cp config.yaml.example config.yaml
# Edit with your preferences
Run (0 minutes - runs automatically):
bash
# The bot auto-runs every 6 hours via systemd
# Check status:
systemctl status solar-alpha
🛠️ How It Works
Data Flow:
text
1. Scanner → Collects market data (crypto, prediction markets)
2. Analyzer → Local LLM analyzes opportunities
3. Trader → Executes paper trades (optionally real)
4. Redistributor → Sends 50% to crisis orgs, 30% to you, 20% to network
5. Ledger → Logs everything to public Google Sheet/local file
📊 Live Dashboard
Once running, view your:

Live trades (public)

Redistribution tracker (blockchain)

Bot status (local web UI)

🤝 Contributing
We need:

Market scanners for new opportunities

Risk models for different strategies

Redistribution channels to verified orgs

Dashboard developers for better visualization

See CONTRIBUTING.md for details.

📄 License
MIT - see LICENSE for details.

"We don't build bots to escape the system. We build bots that change what the system rewards."

Start small. Trade ethically. Redistribute radically.
