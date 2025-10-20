"""
Configuration Template for MT5 Scalping Bot
============================================

Copy this file to config.py and fill in your credentials.
"""

CONFIG = {
    # MT5 Connection
    'mt5_login': 12345,  # Your MT5 account number
    'mt5_password': 'YOUR_PASSWORD_HERE',
    'mt5_server': 'YOUR_SERVER_NAME',  # e.g., 'ACYSecurities-Demo'
    
    # Trading Symbols - Forex, Gold, Oil
    'symbols': [
        # Major Forex Pairs
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD',
        'USDCAD', 'USDCHF', 'NZDUSD',
        
        # Cross Pairs
        'EURGBP', 'EURJPY', 'GBPJPY', 'AUDJPY',
        
        # Gold
        'XAUUSD',
        
        # Oil
        # 'XTIUSD',  # WTI Crude Oil
        # 'XBRUSD',  # Brent Crude Oil
    ],
    
    # Signal threshold
    'min_confidence': 50,  # Minimum confidence to execute trade (0-100)
    
    # Timeframe - M1 or M5 for scalping
    'timeframe': 'M5',  # M1, M5
    
    # Lot Sizing - Fixed based on balance
    # 100k USD = 20 lots
    # 1M USD = 80 lots
    # Automatically calculated: lots = balance / 5000
    
    # Position Limits - Margin-based (unlimited trades)
    'min_margin_level': 800,  # Stop trading if margin level < 800%
    
    # Safety Limits
    'max_daily_loss': 0.05,  # -5% stop trading for the day
    'check_interval': 60,  # Scan every 60 seconds (M1/M5 scalping)
    
    # Debug
    'debug_mode': True,  # Show detailed analysis
}

