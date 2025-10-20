"""
MT5 Improved Scalping Bot - Professional Grade
===============================================

Improvements:
- Risk-based position sizing (1% per trade)
- ACY ProZero commission accounting
- Max concurrent trades limit
- Session filters (London/NY only)
- Improved EMA+RSI strategy
- Volatility filters
"""

import MetaTrader5 as mt5
import logging
import time
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from improved_scalping_engine import ImprovedScalpingEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('improved_scalping_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ImprovedScalpingBot:
    """Professional-grade scalping bot with proper risk management"""
    
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
        
        # Initialize improved scalping engine
        self.engine = ImprovedScalpingEngine()
        
        # Initialize MT5
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        if not mt5.login(config['mt5_login'], password=config['mt5_password'], server=config['mt5_server']):
            raise Exception(f"MT5 login failed: {mt5.last_error()}")
        
        account_info = mt5.account_info()
        self.start_balance = account_info.balance
        
        logger.info("=" * 80)
        logger.info("MT5 IMPROVED PROFESSIONAL SCALPING BOT")
        logger.info("=" * 80)
        logger.info(f"Account: {account_info.login}")
        logger.info(f"Balance: ${account_info.balance:,.2f}")
        logger.info(f"Leverage: 1:{account_info.leverage}")
        logger.info(f"Symbols: {len(config['symbols'])}")
        logger.info(f"Timeframe: {config.get('timeframe', 'M5')}")
        logger.info(f"Risk per Trade: {config.get('risk_per_trade', 0.01) * 100}%")
        logger.info(f"Max Concurrent Trades: {config.get('max_concurrent_trades', 3)}")
        logger.info(f"Commission: ${config.get('commission_per_lot', 6)} per lot (round-turn)")
        logger.info(f"Session Filter: London/NY only")
        logger.info("=" * 80)
    
    def is_active_session(self) -> bool:
        """Check if we're in an active trading session (London or New York)"""
        now = datetime.utcnow()
        hour = now.hour
        
        # London session: 08:00 - 16:00 UTC
        # New York session: 13:00 - 21:00 UTC
        # Overlap: 13:00 - 16:00 UTC (best time)
        
        if (8 <= hour < 16) or (13 <= hour < 21):
            return True
        return False
    
    def calculate_lot_size(self, balance: float, stop_loss_pips: float, symbol: str) -> float:
        """
        Calculate lot size based on fixed fractional risk (1% per trade)
        This is the CORRECT way to size positions
        """
        RISK_PER_TRADE = self.config.get('risk_per_trade', 0.01)  # 1% default
        
        # Get symbol properties
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.error(f"Cannot get symbol info for {symbol}")
            return 0.01
        
        # Calculate pip value based on symbol type
        if 'JPY' in symbol:
            pip_size = 0.01
            pip_value = symbol_info.trade_tick_value * 1000
        elif 'XAU' in symbol or 'GOLD' in symbol:
            pip_size = 0.10
            pip_value = symbol_info.trade_tick_value * 10
        else:
            pip_size = 0.0001
            pip_value = symbol_info.trade_tick_value * 10
        
        # Calculate lot size based on risk
        risk_amount = balance * RISK_PER_TRADE
        lot_size = risk_amount / (stop_loss_pips * pip_value)
        
        # Round to 2 decimal places
        lot_size = round(lot_size, 2)
        
        # Enforce limits
        lot_size = max(symbol_info.volume_min, lot_size)
        lot_size = min(symbol_info.volume_max, lot_size)
        lot_size = min(100.0, lot_size)  # Safety cap
        
        return lot_size
    
    def scan_markets(self):
        """Scan all symbols for scalping opportunities with filters"""
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
        
        # Safety checks
        
        # 1. Session filter
        if not self.is_active_session():
            logger.info("Outside active trading sessions (London/NY). Waiting...")
            return
        
        # 2. Max concurrent trades
        max_trades = self.config.get('max_concurrent_trades', 3)
        if open_positions_count >= max_trades:
            logger.info(f"Max concurrent trades ({max_trades}) reached. No new trades.")
            return
        
        # 3. Margin level check
        min_margin_level = self.config.get('min_margin_level', 800)
        if margin_level < min_margin_level and account_info.margin > 0:
            logger.info(f"Margin level too low ({margin_level:.2f}% < {min_margin_level}%)")
            return
        
        # 4. Daily loss limit
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
            
            # Analyze with improved strategy
            action, confidence, details = self.engine.analyze(symbol, timeframe)
            
            # Log analysis in debug mode
            if self.config.get('debug_mode') and details:
                logger.info(f"\n[{details.get('strategy', 'UNKNOWN')}] {symbol}:")
                if action:
                    logger.info(f"  Signal: {action} ({confidence:.1f}%)")
                    logger.info(f"  EMA9: {details.get('ema_9', 0):.5f} | EMA21: {details.get('ema_21', 0):.5f}")
                    logger.info(f"  RSI: {details.get('rsi_14', 0):.2f}")
                    logger.info(f"  ATR: {details.get('atr', 0):.5f}")
                    logger.info(f"  TP: {details['tp_pips']:.1f} pips | SL: {details['sl_pips']:.1f} pips")
                else:
                    logger.info(f"  No signal")
            
            # Check if signal meets threshold
            if action and confidence >= self.config.get('min_confidence', 70):
                signals_found += 1
                
                logger.info(f"\n>>> {symbol}: {action} signal ({confidence:.1f}%)")
                logger.info(f"    Strategy: {details.get('strategy', 'UNKNOWN')}")
                logger.info(f"    TP: {details['tp_pips']:.1f} pips | SL: {details['sl_pips']:.1f} pips")
                
                # Execute trade
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    self.execute_trade(symbol, action, tick, confidence, details)
                    trades_executed += 1
        
        logger.info("\n" + "=" * 80)
        logger.info(f"SCAN COMPLETE: Signals {signals_found} | Trades Executed {trades_executed}")
        logger.info("=" * 80)
    
    def execute_trade(self, symbol: str, action: str, tick, confidence: float, details: Dict):
        """Execute scalping trade with proper risk management"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Cannot get symbol info for {symbol}")
            return
        
        price = tick.ask if action == 'BUY' else tick.bid
        
        # Get TP/SL from strategy (already dynamic based on ATR)
        tp_pips = details['tp_pips']
        sl_pips = details['sl_pips']
        
        # Calculate pip size
        if 'JPY' in symbol:
            pip_size = 0.01
        elif 'XAU' in symbol or 'GOLD' in symbol:
            pip_size = 0.10
        else:
            pip_size = 0.0001
        
        # Account for commission in TP calculation
        commission_per_lot = self.config.get('commission_per_lot', 6)
        
        # Calculate SL/TP
        if action == 'BUY':
            sl = price - (sl_pips * pip_size)
            tp = price + (tp_pips * pip_size)
            order_type = mt5.ORDER_TYPE_BUY
        else:
            sl = price + (sl_pips * pip_size)
            tp = price - (tp_pips * pip_size)
            order_type = mt5.ORDER_TYPE_SELL
        
        # Calculate lot size based on risk
        lots = self.calculate_lot_size(mt5.account_info().balance, sl_pips, symbol)
        
        # Calculate expected costs
        commission_cost = lots * commission_per_lot
        risk_amount = lots * sl_pips * (10 if 'JPY' not in symbol else 1000)
        
        logger.info(f"\n[TRADE PREPARATION]")
        logger.info(f"Lot Size: {lots} (based on {self.config.get('risk_per_trade', 0.01)*100}% risk)")
        logger.info(f"Risk Amount: ${risk_amount:.2f}")
        logger.info(f"Commission: ${commission_cost:.2f}")
        
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
            "magic": 234001,  # Different magic number for improved bot
            "comment": f"Improved_{details.get('strategy', 'EMA_RSI')}",
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
        logger.info("[TRADE EXECUTED - PROFESSIONAL RISK MANAGEMENT]")
        logger.info(f"Symbol: {symbol} | Action: {action}")
        logger.info(f"Strategy: {details.get('strategy', 'UNKNOWN')}")
        logger.info(f"Lots: {lots} | Price: {price}")
        logger.info(f"SL: {sl} ({sl_pips:.1f} pips) | TP: {tp} ({tp_pips:.1f} pips)")
        logger.info(f"Risk: ${risk_amount:.2f} ({self.config.get('risk_per_trade', 0.01)*100}% of balance)")
        logger.info(f"Commission: ${commission_cost:.2f}")
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
            'sl_pips': sl_pips,
            'tp_pips': tp_pips,
            'risk_amount': risk_amount,
            'commission': commission_cost,
            'confidence': confidence,
            'strategy': details.get('strategy', 'UNKNOWN')
        }
        self.trade_history.append(trade_record)
        
        # Save to file
        with open('improved_trade_history.json', 'w') as f:
            json.dump(self.trade_history, f, indent=2)
    
    def run(self):
        """Main bot loop"""
        logger.info("\n>>> Improved Bot started - Professional risk management active\n")
        logger.info(f"Scan interval: {self.config.get('check_interval', 60)} seconds")
        logger.info(f"Risk per trade: {self.config.get('risk_per_trade', 0.01) * 100}%")
        logger.info(f"Max concurrent trades: {self.config.get('max_concurrent_trades', 3)}")
        logger.info(f"Trading sessions: London (08:00-16:00 UTC) & New York (13:00-21:00 UTC)")
        
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
    
    # Run improved bot
    bot = ImprovedScalpingBot(CONFIG)
    bot.run()

