"""
MT5 Pure Technical Scalping Bot
================================

High-frequency scalping with fixed lot sizing based on balance.
No LLM - Pure technical analysis only.
"""

import MetaTrader5 as mt5
import logging
import time
import json
from datetime import datetime
from typing import Dict
from scalping_engine import ScalpingEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scalping_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScalpingBot:
    """Pure technical scalping bot"""
    
    TIMEFRAME_MAP = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
    }
    
    def __init__(self, config: Dict):
        self.config = config
        self.start_balance = 0
        self.daily_trades = 0
        self.trade_history = []
        
        # Initialize scalping engine
        self.engine = ScalpingEngine()
        
        # Initialize MT5
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        if not mt5.login(config['mt5_login'], password=config['mt5_password'], server=config['mt5_server']):
            raise Exception(f"MT5 login failed: {mt5.last_error()}")
        
        account_info = mt5.account_info()
        self.start_balance = account_info.balance
        
        logger.info("=" * 80)
        logger.info("MT5 PURE TECHNICAL SCALPING BOT")
        logger.info("=" * 80)
        logger.info(f"Account: {account_info.login}")
        logger.info(f"Balance: ${account_info.balance:,.2f}")
        logger.info(f"Leverage: 1:{account_info.leverage}")
        logger.info(f"Symbols: {len(config['symbols'])}")
        logger.info(f"Timeframe: {config.get('timeframe', 'M5')}")
        logger.info(f"Min Margin Level: {config.get('min_margin_level', 800)}%")
        logger.info(f"Lot Sizing: Balance-based (100k=$20, 1M=$80)")
        logger.info(f"Max TP: 120 pips")
        logger.info("=" * 80)
    
    def calculate_lot_size(self, balance: float) -> float:
        """
        Calculate lot size based on balance
        100k USD = 20 lots
        1M USD = 80 lots
        Linear scaling
        """
        # Base calculation: $100k = 20 lots
        # So: lots = (balance / 100000) * 20
        # Simplified: lots = balance / 5000
        
        lots = balance / 5000
        
        # Round to 2 decimal places
        lots = round(lots, 2)
        
        # Minimum 0.01 lot
        lots = max(0.01, lots)
        
        # Maximum 100 lots (safety limit)
        lots = min(100.0, lots)
        
        return lots
    
    def scan_markets(self):
        """Scan all symbols for scalping opportunities"""
        account_info = mt5.account_info()
        positions = mt5.positions_get()
        open_positions_count = len(positions) if positions else 0
        
        margin_level = account_info.margin_level if account_info.margin > 0 else float('inf')
        margin_display = f"{margin_level:.2f}%" if margin_level != float('inf') else "N/A (no positions)"
        
        logger.info("\n" + "=" * 80)
        logger.info(f"SCANNING MARKETS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Balance: ${account_info.balance:,.2f} | Equity: ${account_info.equity:,.2f}")
        logger.info(f"Margin Level: {margin_display} | Open Positions: {open_positions_count} | Daily Trades: {self.daily_trades}")
        logger.info("=" * 80)
        
        # Safety checks - Margin level
        min_margin_level = self.config.get('min_margin_level', 800)
        
        if margin_level < min_margin_level and account_info.margin > 0:
            logger.info(f"Margin level too low ({margin_level:.2f}% < {min_margin_level}%)")
            logger.info(f"Current: Equity ${account_info.equity:,.2f} | Margin ${account_info.margin:,.2f}")
            return
        
        # Daily loss limit
        daily_pnl_pct = ((account_info.balance - self.start_balance) / self.start_balance) * 100
        if daily_pnl_pct <= -self.config['max_daily_loss'] * 100:
            logger.info(f"Daily loss limit reached ({daily_pnl_pct:.2f}%)")
            return
        
        # Get timeframe
        timeframe_str = self.config.get('timeframe', 'M5')
        timeframe = self.TIMEFRAME_MAP.get(timeframe_str, mt5.TIMEFRAME_M5)
        
        # Scan each symbol
        signals_found = 0
        trades_executed = 0
        
        for symbol in self.config['symbols']:
            # Skip if already have position on this symbol
            if positions and any(pos.symbol == symbol for pos in positions):
                continue
            
            # Analyze with pure technical indicators
            action, confidence, details = self.engine.analyze(symbol, timeframe)
            
            # Log analysis in debug mode
            if self.config.get('debug_mode') and details:
                logger.info(f"\n[{details.get('strategy', 'UNKNOWN')}] {symbol}:")
                if action:
                    logger.info(f"  Signal: {action} ({confidence:.1f}%)")
                    if 'signals' in details:
                        for reason, score in details['signals']:
                            logger.info(f"    - {reason} ({score} points)")
                    
                    # Log key indicators
                    for key, value in details.items():
                        if key not in ['strategy', 'signals', 'tp_pips', 'sl_pips']:
                            if isinstance(value, float):
                                logger.info(f"  {key}: {value:.5f}")
                            else:
                                logger.info(f"  {key}: {value}")
                else:
                    logger.info(f"  No signal")
            
            # Check if signal meets threshold
            if action and confidence >= self.config.get('min_confidence', 50):
                signals_found += 1
                
                logger.info(f"\n>>> {symbol}: {action} signal ({confidence:.1f}%)")
                logger.info(f"    Strategy: {details.get('strategy', 'UNKNOWN')}")
                logger.info(f"    TP: {details['tp_pips']} pips | SL: {details['sl_pips']} pips")
                
                # Execute trade
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    self.execute_trade(symbol, action, tick, confidence, details)
                    trades_executed += 1
        
        logger.info("\n" + "=" * 80)
        logger.info(f"SCAN COMPLETE: Signals {signals_found} | Trades Executed {trades_executed}")
        logger.info("=" * 80)
    
    def execute_trade(self, symbol: str, action: str, tick, confidence: float, details: Dict):
        """Execute scalping trade with fixed lot sizing"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Cannot get symbol info for {symbol}")
            return
        
        price = tick.ask if action == 'BUY' else tick.bid
        
        # Get TP/SL from strategy
        tp_pips = min(details['tp_pips'], 120)  # Max 120 pips
        sl_pips = details['sl_pips']
        
        # Calculate pip size based on symbol type
        if 'JPY' in symbol:
            pip_size = 0.01
        elif 'XAU' in symbol or 'GOLD' in symbol:
            pip_size = 0.10
        elif 'XTI' in symbol or 'XBR' in symbol or 'OIL' in symbol:
            pip_size = 0.01
        else:
            pip_size = 0.0001
        
        # Calculate SL/TP
        if action == 'BUY':
            sl = price - (sl_pips * pip_size)
            tp = price + (tp_pips * pip_size)
            order_type = mt5.ORDER_TYPE_BUY
        else:
            sl = price + (sl_pips * pip_size)
            tp = price - (tp_pips * pip_size)
            order_type = mt5.ORDER_TYPE_SELL
        
        # Calculate lot size based on balance
        lots = self.calculate_lot_size(mt5.account_info().balance)
        
        # Prepare order
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lots,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": f"Scalp_{details.get('strategy', 'TECH')}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.retcode} - {result.comment}")
            return
        
        self.daily_trades += 1
        
        logger.info("\n" + "=" * 80)
        logger.info("[TRADE EXECUTED]")
        logger.info(f"Symbol: {symbol} | Action: {action}")
        logger.info(f"Strategy: {details.get('strategy', 'UNKNOWN')}")
        logger.info(f"Lots: {lots} | Price: {price}")
        logger.info(f"SL: {sl} ({sl_pips} pips) | TP: {tp} ({tp_pips} pips)")
        logger.info(f"Confidence: {confidence:.1f}%")
        logger.info("=" * 80)
        
        # Save trade history
        trade_record = {
            'time': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'lots': lots,
            'price': price,
            'sl': sl,
            'tp': tp,
            'confidence': confidence,
            'strategy': details.get('strategy', 'UNKNOWN')
        }
        self.trade_history.append(trade_record)
        
        # Save to file
        with open('trade_history.json', 'w') as f:
            json.dump(self.trade_history, f, indent=2)
    
    def run(self):
        """Main bot loop"""
        logger.info("\n>>> Bot started - Pure technical scalping active\n")
        logger.info(f"Scan interval: {self.config.get('check_interval', 60)} seconds")
        
        try:
            while True:
                self.scan_markets()
                time.sleep(self.config.get('check_interval', 60))
        except KeyboardInterrupt:
            logger.info("\n>>> Bot stopped by user")
        finally:
            mt5.shutdown()


if __name__ == "__main__":
    # Import config
    try:
        from config import CONFIG
    except ImportError:
        logger.error("config.py not found! Copy config_template.py to config.py and configure it.")
        exit(1)
    
    # Run bot
    bot = ScalpingBot(CONFIG)
    bot.run()

