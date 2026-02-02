"""
Configuration loader
"""

import yaml
import os

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        print("Creating default config...")
        create_default_config(config_path)
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_default_config(config_path):
    """Create default configuration file"""
    default_config = {
        'bot': {
            'name': 'solar-alpha-001',
            'mode': 'paper',
            'scan_interval_hours': 6,
            'risk_tolerance': 'medium',
            'max_daily_trades': 3
        },
        'redistribution': {
            'enabled': True,
            'split': {
                'crisis': 50,
                'you': 30,
                'network': 20
            },
            'crisis_orgs': [
                {
                    'name': 'World Central Kitchen',
                    'wallet': '0x1234567890abcdef1234567890abcdef12345678',
                    'percentage': 100,
                    'chain': 'ethereum'
                }
            ],
            'your_wallet': '0xYOUR_ADDRESS_HERE'
        },
        'trading': {
            'paper_starting_balance': 1000.0,
            'allowed_markets': ['crypto', 'prediction'],
            'max_position_size': 100.0,
            'max_total_exposure': 300.0,
            'stop_loss': 10,
            'take_profit': 25
        },
        'ai': {
            'model_path': './models/llama-3.2-7b-q4_k_m.gguf',
            'context_size': 4096,
            'temperature': 0.7,
            'max_tokens': 512
        },
        'data_sources': {
            'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
            'prediction_markets': {
                'predictit': True,
                'polymarket': False
            }
        },
        'logging': {
            'level': 'INFO',
            'console': True,
            'file': True,
            'file_path': './logs/bot.log'
        },
        'dashboard': {
            'enabled': True,
            'port': 8080,
            'host': '0.0.0.0'
        }
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    print(f"Default configuration created at: {config_path}")
    print("Please edit with your settings before running.")
