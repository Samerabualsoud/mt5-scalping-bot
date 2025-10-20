"""
MT5 Pure Technical Analysis Scalping Engine
============================================

High-frequency scalping bot using only technical indicators.
No LLM, pure price action and indicators.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime


class ScalpingEngine:
    """Pure technical analysis engine for scalping"""
    
    def __init__(self):
        self.pair_strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict:
        """Define optimal indicator combinations for each pair type"""
        return {
            # Major Forex Pairs - Fast RSI + EMA + Stochastic
            'EURUSD': {'strategy': 'fast_rsi_ema', 'tp_pips': 15, 'sl_pips': 8},
            'GBPUSD': {'strategy': 'fast_rsi_ema', 'tp_pips': 18, 'sl_pips': 9},
            'USDJPY': {'strategy': 'fast_rsi_ema', 'tp_pips': 15, 'sl_pips': 8},
            'AUDUSD': {'strategy': 'fast_rsi_ema', 'tp_pips': 15, 'sl_pips': 8},
            'USDCAD': {'strategy': 'fast_rsi_ema', 'tp_pips': 15, 'sl_pips': 8},
            'USDCHF': {'strategy': 'fast_rsi_ema', 'tp_pips': 15, 'sl_pips': 8},
            'NZDUSD': {'strategy': 'fast_rsi_ema', 'tp_pips': 15, 'sl_pips': 8},
            
            # Cross Pairs - Bollinger + CCI + RSI
            'EURGBP': {'strategy': 'bollinger_cci', 'tp_pips': 20, 'sl_pips': 10},
            'EURJPY': {'strategy': 'bollinger_cci', 'tp_pips': 25, 'sl_pips': 12},
            'GBPJPY': {'strategy': 'bollinger_cci', 'tp_pips': 30, 'sl_pips': 15},
            'AUDJPY': {'strategy': 'bollinger_cci', 'tp_pips': 25, 'sl_pips': 12},
            'EURAUD': {'strategy': 'bollinger_cci', 'tp_pips': 20, 'sl_pips': 10},
            'GBPAUD': {'strategy': 'bollinger_cci', 'tp_pips': 25, 'sl_pips': 12},
            'EURCHF': {'strategy': 'bollinger_cci', 'tp_pips': 18, 'sl_pips': 9},
            
            # Gold - MACD + RSI + ATR
            'XAUUSD': {'strategy': 'macd_rsi_atr', 'tp_pips': 40, 'sl_pips': 20},
            'GOLD': {'strategy': 'macd_rsi_atr', 'tp_pips': 40, 'sl_pips': 20},
            
            # Oil - MACD + Momentum + Bollinger
            'XTIUSD': {'strategy': 'macd_momentum', 'tp_pips': 50, 'sl_pips': 25},
            'XBRUSD': {'strategy': 'macd_momentum', 'tp_pips': 50, 'sl_pips': 25},
            'USOIL': {'strategy': 'macd_momentum', 'tp_pips': 50, 'sl_pips': 25},
            'UKOIL': {'strategy': 'macd_momentum', 'tp_pips': 50, 'sl_pips': 25},
        }
    
    def analyze(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """
        Analyze symbol and return trading signal
        
        Returns:
            action: 'BUY', 'SELL', or None
            confidence: 0-100
            details: Analysis details
        """
        # Get strategy for symbol
        if symbol not in self.pair_strategies:
            # Default strategy for unknown pairs
            strategy_config = {'strategy': 'fast_rsi_ema', 'tp_pips': 15, 'sl_pips': 8}
        else:
            strategy_config = self.pair_strategies[symbol]
        
        strategy_name = strategy_config['strategy']
        
        # Execute strategy
        if strategy_name == 'fast_rsi_ema':
            return self._fast_rsi_ema_strategy(symbol, timeframe, strategy_config)
        elif strategy_name == 'bollinger_cci':
            return self._bollinger_cci_strategy(symbol, timeframe, strategy_config)
        elif strategy_name == 'macd_rsi_atr':
            return self._macd_rsi_atr_strategy(symbol, timeframe, strategy_config)
        elif strategy_name == 'macd_momentum':
            return self._macd_momentum_strategy(symbol, timeframe, strategy_config)
        else:
            return None, 0, {}
    
    def _fast_rsi_ema_strategy(self, symbol: str, timeframe, config: Dict) -> Tuple[Optional[str], float, Dict]:
        """
        Fast RSI + EMA + Stochastic for major pairs
        Best for liquid, trending pairs
        """
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate indicators
        # Fast RSI (9 period for scalping)
        rsi_9 = self._calculate_rsi(df['close'], 9)
        
        # EMAs for trend
        ema_8 = df['close'].ewm(span=8, adjust=False).mean()
        ema_21 = df['close'].ewm(span=21, adjust=False).mean()
        
        # Stochastic for momentum
        stoch_k, stoch_d = self._calculate_stochastic(df, 14, 3)
        
        # Current values
        current_price = df['close'].iloc[-1]
        current_rsi = rsi_9.iloc[-1]
        current_ema8 = ema_8.iloc[-1]
        current_ema21 = ema_21.iloc[-1]
        current_stoch_k = stoch_k.iloc[-1]
        current_stoch_d = stoch_d.iloc[-1]
        
        # Signal logic
        signals = []
        score = 0
        action = None
        
        # BUY conditions
        if current_rsi < 35:  # Oversold
            signals.append(("RSI oversold", 30))
            score += 30
        
        if current_ema8 > current_ema21:  # Uptrend
            signals.append(("EMA uptrend", 25))
            score += 25
        
        if current_stoch_k < 20 and current_stoch_k > current_stoch_d:  # Stoch turning up
            signals.append(("Stochastic bullish", 25))
            score += 25
        
        if current_price < current_ema8 < current_ema21:  # Price below EMAs in uptrend
            signals.append(("Price pullback in uptrend", 20))
            score += 20
        
        if score >= 50:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        sell_signals = []
        
        if current_rsi > 65:  # Overbought
            sell_signals.append(("RSI overbought", 30))
            sell_score += 30
        
        if current_ema8 < current_ema21:  # Downtrend
            sell_signals.append(("EMA downtrend", 25))
            sell_score += 25
        
        if current_stoch_k > 80 and current_stoch_k < current_stoch_d:  # Stoch turning down
            sell_signals.append(("Stochastic bearish", 25))
            sell_score += 25
        
        if current_price > current_ema8 > current_ema21:  # Price above EMAs in downtrend
            sell_signals.append(("Price pullback in downtrend", 20))
            sell_score += 20
        
        if sell_score > score and sell_score >= 50:
            action = 'SELL'
            score = sell_score
            signals = sell_signals
        
        details = {
            'strategy': 'FAST_RSI_EMA',
            'rsi_9': current_rsi,
            'ema_8': current_ema8,
            'ema_21': current_ema21,
            'stoch_k': current_stoch_k,
            'stoch_d': current_stoch_d,
            'signals': signals,
            'tp_pips': config['tp_pips'],
            'sl_pips': config['sl_pips']
        }
        
        return action, score, details
    
    def _bollinger_cci_strategy(self, symbol: str, timeframe, config: Dict) -> Tuple[Optional[str], float, Dict]:
        """
        Bollinger Bands + CCI + RSI for cross pairs
        Best for volatile, range-bound pairs
        """
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate indicators
        # Bollinger Bands (20, 2)
        bb_middle = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # CCI (14)
        cci = self._calculate_cci(df, 14)
        
        # RSI (14)
        rsi = self._calculate_rsi(df['close'], 14)
        
        # Current values
        current_price = df['close'].iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        current_bb_middle = bb_middle.iloc[-1]
        current_cci = cci.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Distance to bands
        dist_to_lower = ((current_price - current_bb_lower) / current_bb_lower) * 100
        dist_to_upper = ((current_bb_upper - current_price) / current_price) * 100
        
        # Signal logic
        signals = []
        score = 0
        action = None
        
        # BUY conditions (bounce from lower band)
        if dist_to_lower < 0.15:  # Very close to lower band
            signals.append(("Price at lower Bollinger", 35))
            score += 35
        
        if current_cci < -100:  # CCI oversold
            signals.append(("CCI oversold", 30))
            score += 30
        
        if current_rsi < 40:  # RSI oversold
            signals.append(("RSI oversold", 20))
            score += 20
        
        if current_price < current_bb_middle:  # Below middle band
            signals.append(("Below BB middle", 15))
            score += 15
        
        if score >= 50:
            action = 'BUY'
        
        # SELL conditions (bounce from upper band)
        sell_score = 0
        sell_signals = []
        
        if dist_to_upper < 0.15:  # Very close to upper band
            sell_signals.append(("Price at upper Bollinger", 35))
            sell_score += 35
        
        if current_cci > 100:  # CCI overbought
            sell_signals.append(("CCI overbought", 30))
            sell_score += 30
        
        if current_rsi > 60:  # RSI overbought
            sell_signals.append(("RSI overbought", 20))
            sell_score += 20
        
        if current_price > current_bb_middle:  # Above middle band
            sell_signals.append(("Above BB middle", 15))
            sell_score += 15
        
        if sell_score > score and sell_score >= 50:
            action = 'SELL'
            score = sell_score
            signals = sell_signals
        
        details = {
            'strategy': 'BOLLINGER_CCI',
            'bb_upper': current_bb_upper,
            'bb_lower': current_bb_lower,
            'bb_middle': current_bb_middle,
            'cci': current_cci,
            'rsi': current_rsi,
            'dist_to_lower': dist_to_lower,
            'dist_to_upper': dist_to_upper,
            'signals': signals,
            'tp_pips': config['tp_pips'],
            'sl_pips': config['sl_pips']
        }
        
        return action, score, details
    
    def _macd_rsi_atr_strategy(self, symbol: str, timeframe, config: Dict) -> Tuple[Optional[str], float, Dict]:
        """
        MACD + RSI + ATR for Gold
        Best for trending, volatile instruments
        """
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate indicators
        # MACD (12, 26, 9)
        macd_line, signal_line, macd_hist = self._calculate_macd(df['close'], 12, 26, 9)
        
        # RSI (14)
        rsi = self._calculate_rsi(df['close'], 14)
        
        # ATR (14) for volatility
        atr = self._calculate_atr(df, 14)
        atr_avg = atr.rolling(window=20).mean()
        
        # Current values
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_macd_hist = macd_hist.iloc[-1]
        prev_macd_hist = macd_hist.iloc[-2]
        current_rsi = rsi.iloc[-1]
        current_atr = atr.iloc[-1]
        current_atr_avg = atr_avg.iloc[-1]
        
        # Signal logic
        signals = []
        score = 0
        action = None
        
        # BUY conditions
        if current_macd > current_signal:  # MACD bullish
            signals.append(("MACD bullish", 30))
            score += 30
        
        if current_macd_hist > 0 and current_macd_hist > prev_macd_hist:  # MACD histogram growing
            signals.append(("MACD momentum increasing", 25))
            score += 25
        
        if current_rsi < 50 and current_rsi > 30:  # RSI in buy zone
            signals.append(("RSI in buy zone", 25))
            score += 25
        
        if current_atr < current_atr_avg * 1.5:  # Normal volatility
            signals.append(("Normal volatility", 20))
            score += 20
        
        if score >= 50:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        sell_signals = []
        
        if current_macd < current_signal:  # MACD bearish
            sell_signals.append(("MACD bearish", 30))
            sell_score += 30
        
        if current_macd_hist < 0 and current_macd_hist < prev_macd_hist:  # MACD histogram declining
            sell_signals.append(("MACD momentum decreasing", 25))
            sell_score += 25
        
        if current_rsi > 50 and current_rsi < 70:  # RSI in sell zone
            sell_signals.append(("RSI in sell zone", 25))
            sell_score += 25
        
        if current_atr < current_atr_avg * 1.5:  # Normal volatility
            sell_signals.append(("Normal volatility", 20))
            sell_score += 20
        
        if sell_score > score and sell_score >= 50:
            action = 'SELL'
            score = sell_score
            signals = sell_signals
        
        details = {
            'strategy': 'MACD_RSI_ATR',
            'macd': current_macd,
            'signal': current_signal,
            'macd_hist': current_macd_hist,
            'rsi': current_rsi,
            'atr': current_atr,
            'signals': signals,
            'tp_pips': config['tp_pips'],
            'sl_pips': config['sl_pips']
        }
        
        return action, score, details
    
    def _macd_momentum_strategy(self, symbol: str, timeframe, config: Dict) -> Tuple[Optional[str], float, Dict]:
        """
        MACD + Momentum + Bollinger for Oil
        Best for commodity trading
        """
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate indicators
        # MACD (12, 26, 9)
        macd_line, signal_line, macd_hist = self._calculate_macd(df['close'], 12, 26, 9)
        
        # Momentum (10)
        momentum = df['close'].diff(10)
        
        # Bollinger Bands (20, 2)
        bb_middle = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # Current values
        current_price = df['close'].iloc[-1]
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_momentum = momentum.iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        
        # Signal logic
        signals = []
        score = 0
        action = None
        
        # BUY conditions
        if current_macd > current_signal:  # MACD bullish
            signals.append(("MACD bullish", 35))
            score += 35
        
        if current_momentum > 0:  # Positive momentum
            signals.append(("Positive momentum", 30))
            score += 30
        
        if current_price < current_bb_lower * 1.005:  # Near lower band
            signals.append(("Near lower Bollinger", 25))
            score += 25
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        sell_signals = []
        
        if current_macd < current_signal:  # MACD bearish
            sell_signals.append(("MACD bearish", 35))
            sell_score += 35
        
        if current_momentum < 0:  # Negative momentum
            sell_signals.append(("Negative momentum", 30))
            sell_score += 30
        
        if current_price > current_bb_upper * 0.995:  # Near upper band
            sell_signals.append(("Near upper Bollinger", 25))
            sell_score += 25
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
            signals = sell_signals
        
        details = {
            'strategy': 'MACD_MOMENTUM',
            'macd': current_macd,
            'signal': current_signal,
            'momentum': current_momentum,
            'bb_upper': current_bb_upper,
            'bb_lower': current_bb_lower,
            'signals': signals,
            'tp_pips': config['tp_pips'],
            'sl_pips': config['sl_pips']
        }
        
        return action, score, details
    
    # Indicator calculation methods
    
    def _calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int, d_period: int) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        k = 100 * (df['close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=d_period).mean()
        return k, d
    
    def _calculate_macd(self, series: pd.Series, fast: int, slow: int, signal: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        macd_hist = macd_line - signal_line
        return macd_line, signal_line, macd_hist
    
    def _calculate_cci(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Commodity Channel Index"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (tp - sma) / (0.015 * mad)
        return cci
    
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

