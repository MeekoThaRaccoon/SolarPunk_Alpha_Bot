#!/bin/bash

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
        echo "⚠️ Please install Python3 manually"
        exit 1
    fi
fi

# Create directory
INSTALL_DIR="$HOME/solar-alpha"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --user

echo "🔧 Setting up configuration..."
if [ ! -f "config.yaml" ]; then
    cp config.yaml.example config.yaml
    echo "📝 Please edit config.yaml with your settings"
fi

echo "🧠 Downloading AI model..."
mkdir -p models
cd models
if [ ! -f "llama-3.2-7b-q4_k_m.gguf" ]; then
    echo "Downloading model (4GB)..."
    wget -q --show-progress https://huggingface.co/QuantFactory/Meta-Llama-3.2-7B-Instruct-GGUF/resolve/main/Meta-Llama-3.2-7B-Instruct-Q4_K_M.gguf
    mv Meta-Llama-3.2-7B-Instruct-Q4_K_M.gguf llama-3.2-7b-q4_k_m.gguf
fi
cd ..

echo "📊 Setting up logs..."
mkdir -p logs

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

echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml: nano $INSTALL_DIR/config.yaml"
echo "2. Start the bot: sudo systemctl start solar-alpha"
echo "3. Check dashboard: http://localhost:8080"
