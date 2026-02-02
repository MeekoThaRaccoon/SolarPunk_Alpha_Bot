```bash
#!/bin/bash

# SolarPunk Alpha Bot Installer
# Run with: curl -s https://raw.githubusercontent.com/SolarPunk-Infra/Alpha-Bot/main/install.sh | bash

set -e

echo "🌱 Installing SolarPunk Alpha Bot..."
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python3
    else
        echo "⚠️ Please install Python3 manually: https://www.python.org/"
        exit 1
    fi
fi

# Create directory
INSTALL_DIR="$HOME/solar-alpha"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "📦 Cloning repository..."
if [ -d ".git" ]; then
    echo "✅ Already installed, updating..."
    git pull
else
    git clone https://github.com/SolarPunk-Infra/Alpha-Bot.git .
fi

echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt --user

echo "🔧 Setting up configuration..."
if [ ! -f "config.yaml" ]; then
    cp config.yaml.example config.yaml
    echo "📝 Please edit config.yaml with your settings"
fi

echo "🧠 Downloading AI model (this may take a while)..."
mkdir -p models
cd models
if [ ! -f "llama-3.2-7b-q4_k_m.gguf" ]; then
    echo "Downloading 4GB model... Go grab a coffee ☕"
    wget -q --show-progress https://huggingface.co/QuantFactory/Meta-Llama-3.2-7B-Instruct-GGUF/resolve/main/Meta-Llama-3.2-7B-Instruct-Q4_K_M.gguf -O llama-3.2-7b-q4_k_m.gguf
fi
cd ..

echo "📊 Setting up public ledger..."
python3 -c "from ledger.setup import setup_public_ledger; setup_public_ledger()"

echo "⚙️ Creating system service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cat > solar-alpha.service << EOF
[Unit]
Description=SolarPunk Alpha Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo mv solar-alpha.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable solar-alpha
    echo "✅ Service installed. Start with: sudo systemctl start solar-alpha"
fi

echo "🌐 Setting up local dashboard..."
python3 -m web.setup_dashboard &

echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml: nano $INSTALL_DIR/config.yaml"
echo "2. Start the bot: sudo systemctl start solar-alpha"
echo "3. Check status: sudo systemctl status solar-alpha"
echo "4. View dashboard: http://localhost:8080"
echo ""
echo "Remember: Start with PAPER trading first!"
echo "The bot will auto-run every 6 hours."
echo ""
echo "🌍 Happy ethical trading!"
