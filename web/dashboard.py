"""
Web Dashboard - Simple Flask dashboard for monitoring
"""

from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

class Dashboard:
    def __init__(self, config, bot_state):
        self.config = config
        self.bot_state = bot_state
        self.port = config['dashboard']['port']
        self.host = config['dashboard']['host']
    
    def start(self):
        """Start the dashboard server"""
        if not self.config['dashboard']['enabled']:
            return
        
        # Create templates directory if it doesn't exist
        os.makedirs('templates', exist_ok=True)
        
        # Create basic HTML template
        self.create_template()
        
        app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
    
    def create_template(self):
        """Create HTML template for dashboard"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SolarPunk Alpha Bot Dashboard</title>
            <style>
                body {
                    font-family: 'Courier New', monospace;
                    background: #0a0f1e;
                    color: #00ff9d;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                h1 {
                    color: #00ff9d;
                    border-bottom: 2px solid #00ff9d;
                    padding-bottom: 10px;
                }
                .status-card {
                    background: rgba(0, 255, 157, 0.1);
                    border: 1px solid #00ff9d;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                }
                .metric {
                    display: inline-block;
                    margin: 10px 20px 10px 0;
                    padding: 10px 20px;
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 5px;
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #00ff9d;
                }
                .metric-label {
                    font-size: 12px;
                    color: #88a;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                th, td {
                    border: 1px solid #00ff9d;
                    padding: 10px;
                    text-align: left;
                }
                th {
                    background: rgba(0, 255, 157, 0.2);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 SolarPunk Alpha Bot Dashboard</h1>
                
                <div class="status-card">
                    <h2>📊 Current Status</h2>
                    <div class="metric">
                        <div class="metric-value" id="total-profit">$0.00</div>
                        <div class="metric-label">Total Profit</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="total-donated">$0.00</div>
                        <div class="metric-label">Crisis Donations</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="total-trades">0</div>
                        <div class="metric-label">Trades Executed</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="bot-mode">PAPER</div>
                        <div class="metric-label">Trading Mode</div>
                    </div>
                </div>
                
                <h2>📈 Recent Trades</h2>
                <table id="trades-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Quantity</th>
                            <th>Profit</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Filled by JavaScript -->
                    </tbody>
                </table>
                
                <h2>🌍 Recent Donations</h2>
                <table id="donations-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Organization</th>
                            <th>Amount</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Filled by JavaScript -->
                    </tbody>
                </table>
                
                <div style="margin-top: 40px; color: #88a; font-size: 12px;">
                    <p>SolarPunk Alpha Bot v0.1 | All trades logged transparently | 50% auto-redistribution</p>
                </div>
            </div>
            
            <script>
                async function updateData() {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        
                        // Update metrics
                        document.getElementById('total-profit').textContent = '$' + data.total_profit.toFixed(2);
                        document.getElementById('total-donated').textContent = '$' + data.total_donated.toFixed(2);
                        document.getElementById('total-trades').textContent = data.total_trades;
                        document.getElementById('bot-mode').textContent = data.bot_mode;
                        
                        // Update trades table
                        const tradesTable = document.getElementById('trades-table').getElementsByTagName('tbody')[0];
                        tradesTable.innerHTML = '';
                        data.recent_trades.forEach(trade => {
                            const row = tradesTable.insertRow();
                            row.innerHTML = `
                                <td>${new Date(trade.timestamp).toLocaleTimeString()}</td>
                                <td>${trade.symbol}</td>
                                <td>$${trade.price.toFixed(2)}</td>
                                <td>${trade.quantity.toFixed(4)}</td>
                                <td>$${trade.profit.toFixed(2)}</td>
                            `;
                        });
                        
                        // Update donations table
                        const donationsTable = document.getElementById('donations-table').getElementsByTagName('tbody')[0];
                        donationsTable.innerHTML = '';
                        data.recent_donations.forEach(donation => {
                            const row = donationsTable.insertRow();
                            row.innerHTML = `
                                <td>${new Date(donation.timestamp).toLocaleTimeString()}</td>
                                <td>${donation.organization}</td>
                                <td>$${donation.amount.toFixed(2)}</td>
                                <td>${donation.status}</td>
                            `;
                        });
                        
                    } catch (error) {
                        console.error('Error updating dashboard:', error);
                    }
                }
                
                // Update every 10 seconds
                setInterval(updateData, 10000);
                updateData(); // Initial update
            </script>
        </body>
        </html>
        '''
        
        with open('templates/index.html', 'w') as f:
            f.write(html)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    # This would connect to the actual bot state
    return jsonify({
        'total_profit': 0.0,
        'total_donated': 0.0,
        'total_trades': 0,
        'bot_mode': 'PAPER',
        'recent_trades': [],
        'recent_donations': []
    })

if __name__ == '__main__':
    dashboard = Dashboard({'dashboard': {'enabled': True, 'port': 8080, 'host': '0.0.0.0'}}, None)
    dashboard.start()
