"""
Public Ledger - Transparent logging of all activities
"""

import json
import csv
from datetime import datetime
from typing import Dict, Any, List
import logging
import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
import sqlite3

logger = logging.getLogger(__name__)

class PublicLedger:
    """Maintains transparent public ledger of all bot activities"""
    
    def __init__(self, config):
        self.config = config
        self.ledger_type = config.get('logging', {}).get('public_ledger', {}).get('type', 'csv')
        self.ledger_path = config.get('logging', {}).get('public_ledger', {}).get('file_path', './ledger')
        
        # Create ledger directory
        Path(self.ledger_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize based on type
        if self.ledger_type == 'google_sheets':
            self.init_google_sheets()
        elif self.ledger_type == 'sqlite':
            self.init_sqlite()
        else:  # csv default
            self.init_csv()
        
        logger.info(f"Public ledger initialized: {self.ledger_type}")
    
    def init_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            sheet_id = self.config.get('logging', {}).get('public_ledger', {}).get('sheet_id', '')
            
            if not sheet_id:
                logger.warning("Google Sheet ID not configured, falling back to CSV")
                self.ledger_type = 'csv'
                self.init_csv()
                return
            
            # Use service account credentials
            creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            
            if os.path.exists(creds_file):
                scope = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_file(creds_file, scopes=scope)
                self.gc = gspread.authorize(creds)
                self.sheet = self.gc.open_by_key(sheet_id)
                
                # Ensure sheets exist
                self.ensure_sheets_exist()
            else:
                logger.warning("Google credentials not found, falling back to CSV")
                self.ledger_type = 'csv'
                self.init_csv()
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")
            self.ledger_type = 'csv'
            self.init_csv()
    
    def ensure_sheets_exist(self):
        """Ensure all required sheets exist"""
        required_sheets = ['trades', 'cycles', 'distributions', 'errors']
        
        for sheet_name in required_sheets:
            try:
                self.sheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                self.sheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
                # Add headers
                ws = self.sheet.worksheet(sheet_name)
                if sheet_name == 'trades':
                    ws.append_row(['ID', 'Timestamp', 'Symbol', 'Type', 'Quantity', 'Price', 'Status', 'Profit', 'Analysis', 'Metadata'])
                elif sheet_name == 'cycles':
                    ws.append_row(['CycleID', 'Timestamp', 'Opportunities', 'Analyzed', 'Trades', 'Metadata'])
                elif sheet_name == 'distributions':
                    ws.append_row(['DistributionID', 'Timestamp', 'Profit', 'CrisisAmount', 'YourAmount', 'NetworkAmount', 'Details'])
                elif sheet_name == 'errors':
                    ws.append_row(['Timestamp', 'CycleID', 'Error', 'Context'])
    
    def init_sqlite(self):
        """Initialize SQLite database"""
        db_path = os.path.join(self.ledger_path, 'ledger.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                symbol TEXT,
                type TEXT,
                quantity REAL,
                price REAL,
                status TEXT,
                profit REAL,
                analysis TEXT,
                metadata TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycles (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                opportunities_found INTEGER,
                opportunities_analyzed INTEGER,
                trades_executed INTEGER,
                metadata TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS distributions (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                total_profit REAL,
                distributions TEXT,
                metadata TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cycle_id TEXT,
                error TEXT,
                context TEXT
            )
        ''')
        
        self.conn.commit()
    
    def init_csv(self):
        """Initialize CSV file logging"""
        # Ensure CSV files exist with headers
        files = {
            'trades.csv': ['ID', 'Timestamp', 'Symbol', 'Type', 'Quantity', 'Price', 'Status', 'Profit', 'Analysis', 'Metadata'],
            'cycles.csv': ['CycleID', 'Timestamp', 'Opportunities', 'Analyzed', 'Trades', 'Metadata'],
            'distributions.csv': ['DistributionID', 'Timestamp', 'Profit', 'CrisisAmount', 'YourAmount', 'NetworkAmount', 'Details'],
            'errors.csv': ['Timestamp', 'CycleID', 'Error', 'Context']
        }
        
        for filename, headers in files.items():
            filepath = os.path.join(self.ledger_path, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
    
    def log_trade(self, trade: Dict[str, Any]):
        """Log a trade to the public ledger"""
        try:
            log_entry = {
                'ID': trade.get('id', 'unknown'),
                'Timestamp': trade.get('timestamp', datetime.now().isoformat()),
                'Symbol': trade.get('symbol', ''),
                'Type': trade.get('type', ''),
                'Quantity': trade.get('quantity', 0),
                'Price': trade.get('price', 0),
                'Status': trade.get('status', ''),
                'Profit': trade.get('profit', 0),
                'Analysis': json.dumps(trade.get('analysis', {})),
                'Metadata': json.dumps(trade.get('metadata', {}))
            }
            
            if self.ledger_type == 'google_sheets':
                self.log_to_google_sheets('trades', log_entry)
            elif self.ledger_type == 'sqlite':
                self.log_to_sqlite('trades', log_entry)
            else:
                self.log_to_csv('trades', log_entry)
                
        except Exception as e:
            logger.error(f"Failed to log trade: {e}")
    
    def log_cycle(self, cycle_data: Dict[str, Any]):
        """Log a complete cycle to the public ledger"""
        try:
            log_entry = {
                'CycleID': cycle_data.get('cycle_id', 'unknown'),
                'Timestamp': cycle_data.get('timestamp', datetime.now().isoformat()),
                'Opportunities': cycle_data.get('opportunities_found', 0),
                'Analyzed': cycle_data.get('opportunities_analyzed', 0),
                'Trades': cycle_data.get('trades_executed', 0),
                'Metadata': json.dumps(cycle_data)
            }
            
            if self.ledger_type == 'google_sheets':
                self.log_to_google_sheets('cycles', log_entry)
            elif self.ledger_type == 'sqlite':
                self.log_to_sqlite('cycles', log_entry)
            else:
                self.log_to_csv('cycles', log_entry)
                
        except Exception as e:
            logger.error(f"Failed to log cycle: {e}")
    
    def log_redistribution(self, distribution: Dict[str, Any]):
        """Log a redistribution to the public ledger"""
        try:
            # Calculate amounts
            crisis_amount = 0
            your_amount = 0
            network_amount = 0
            
            dists = distribution.get('distributions', {})
            
            if 'crisis' in dists:
                for dist in dists['crisis']:
                    crisis_amount += dist.get('amount', 0)
            
            if 'you' in dists:
                your_amount += dists['you'].get('amount', 0)
            
            if 'network' in dists:
                network_amount += dists['network'].get('amount', 0)
            
            log_entry = {
                'DistributionID': distribution.get('id', 'unknown'),
                'Timestamp': distribution.get('timestamp', datetime.now().isoformat()),
                'Profit': distribution.get('total_profit', 0),
                'CrisisAmount': crisis_amount,
                'YourAmount': your_amount,
                'NetworkAmount': network_amount,
                'Details': json.dumps(distribution)
            }
            
            if self.ledger_type == 'google_sheets':
                self.log_to_google_sheets('distributions', log_entry)
            elif self.ledger_type == 'sqlite':
                self.log_to_sqlite('distributions', log_entry)
            else:
                self.log_to_csv('distributions', log_entry)
                
        except Exception as e:
            logger.error(f"Failed to log distribution: {e}")
    
    def log_error(self, cycle_id: str, error: str, context: Dict[str, Any] = None):
        """Log an error to the public ledger"""
        try:
            log_entry = {
                'Timestamp': datetime.now().isoformat(),
                'CycleID': cycle_id,
                'Error': error,
                'Context': json.dumps(context or {})
            }
            
            if self.ledger_type == 'google_sheets':
                self.log_to_google_sheets('errors', log_entry)
            elif self.ledger_type == 'sqlite':
                self.log_to_sqlite('errors', log_entry)
            else:
                self.log_to_csv('errors', log_entry)
                
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    def log_to_google_sheets(self, sheet_name: str, data: Dict[str, Any]):
        """Log data to Google Sheets"""
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            row = [data.get(key, '') for key in self.get_headers(sheet_name)]
            worksheet.append_row(row)
        except Exception as e:
            logger.error(f"Failed to log to Google Sheets: {e}")
            # Fall back to CSV
            self.ledger_type = 'csv'
            self.init_csv()
            self.log_to_csv(sheet_name, data)
    
    def log_to_sqlite(self, table_name: str, data: Dict[str, Any]):
        """Log data to SQLite"""
        try:
            # Convert data to tuple in correct order
            headers = self.get_headers(table_name)
            values = tuple(data.get(header, '') for header in headers)
            
            # Create INSERT statement
            placeholders = ', '.join(['?' for _ in headers])
            columns = ', '.join(headers)
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to log to SQLite: {e}")
            self.conn.rollback()
    
    def log_to_csv(self, file_prefix: str, data: Dict[str, Any]):
        """Log data to CSV"""
        try:
            filename = os.path.join(self.ledger_path, f"{file_prefix}.csv")
            headers = self.get_headers(file_prefix)
            
            with open(filename, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                
                # Ensure all keys are present
                row = {header: data.get(header, '') for header in headers}
                writer.writerow(row)
                
        except Exception as e:
            logger.error(f"Failed to log to CSV: {e}")
    
    def get_headers(self, data_type: str) -> List[str]:
        """Get headers for a data type"""
        if data_type == 'trades':
            return ['ID', 'Timestamp', 'Symbol', 'Type', 'Quantity', 'Price', 'Status', 'Profit', 'Analysis', 'Metadata']
        elif data_type == 'cycles':
            return ['CycleID', 'Timestamp', 'Opportunities', 'Analyzed', 'Trades', 'Metadata']
        elif data_type == 'distributions':
            return ['DistributionID', 'Timestamp', 'Profit', 'CrisisAmount', 'YourAmount', 'NetworkAmount', 'Details']
        elif data_type == 'errors':
            return ['Timestamp', 'CycleID', 'Error', 'Context']
        else:
            return []
    
    def log_shutdown(self):
        """Log bot shutdown"""
        log_entry = {
            'Timestamp': datetime.now().isoformat(),
            'Event': 'SHUTDOWN',
            'Message': 'SolarPunk Alpha Bot shutting down'
        }
        
        # Log to all formats
        self.log_to_csv('events', log_entry)
        
        if self.ledger_type == 'sqlite':
            self.conn.close()
    
    def get_public_url(self) -> str:
        """Get public URL for viewing the ledger"""
        if self.ledger_type == 'google_sheets':
            sheet_id = self.config.get('logging', {}).get('public_ledger', {}).get('sheet_id', '')
            if sheet_id:
                return f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        
        # For CSV/SQLite, could upload to GitHub Pages or similar
        return "File-based ledger (see ledger directory)"
