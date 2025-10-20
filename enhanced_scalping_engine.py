"""
Enhanced MT5 Multi-Strategy Scalping Engine
============================================

Multiple research-backed strategies per pair with consensus voting.
Only executes when 2+ strategies agree for maximum reliability.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from datetime import datetime


class EnhancedScalpingEngine:
    """Multi-strategy scalping engine with consensus voting"""
    
    def __init__(self):
        self.pair_strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict:
        """Define multiple strategies for each pair type"""
        return {
            # Major Forex Pairs - 3 strategies each
            'EURUSD': {
                'strategies': ['ema_rsi_adx', 'macd_stochastic', 'price_action_volume'],
                'tp_pips': 18,
                'sl_pips': 9,
                'min_consensus': 2  # Need 2/3 strategies to agree
            },
            'GBPUSD': {
                'strategies': ['ema_rsi_adx', 'macd_stochastic', 'price_action_volume'],
                'tp_pips': 20,
                'sl_pips': 10,
                'min_consensus': 2
            },
            'USDJPY': {
                'strategies': ['ema_rsi_adx', 'macd_stochastic', 'price_action_volume'],
                'tp_pips': 18,
                'sl_pips': 9,
                'min_consensus': 2
            },
            'AUDUSD': {
                'strategies': ['ema_rsi_adx', 'macd_stochastic', 'price_action_volume'],
                'tp_pips': 18,
                'sl_pips': 9,
                'min_consensus': 2
            },
            'USDCAD': {
                'strategies': ['ema_rsi_adx', 'macd_stochastic', 'price_action_volume'],
                'tp_pips': 18,
                'sl_pips': 9,
                'min_consensus': 2
            },
            'USDCHF': {
                'strategies': ['ema_rsi_adx', 'macd_stochastic', 'price_action_volume'],
                'tp_pips': 18,
                'sl_pips': 9,
                'min_consensus': 2
            },
            'NZDUSD': {
                'strategies': ['ema_rsi_adx', 'macd_stochastic', 'price_action_volume'],
                'tp_pips': 18,
                'sl_pips': 9,
                'min_consensus': 2
            },
            
            # Cross Pairs - 3 strategies each
            'EURGBP': {
                'strategies': ['bollinger_stochastic', 'rsi_cci_atr', 'mean_reversion'],
                'tp_pips': 22,
                'sl_pips': 11,
                'min_consensus': 2
            },
            'EURJPY': {
                'strategies': ['bollinger_stochastic', 'rsi_cci_atr', 'mean_reversion'],
                'tp_pips': 28,
                'sl_pips': 14,
                'min_consensus': 2
            },
            'GBPJPY': {
                'strategies': ['bollinger_stochastic', 'rsi_cci_atr', 'mean_reversion'],
                'tp_pips': 35,
                'sl_pips': 17,
                'min_consensus': 2
            },
            'AUDJPY': {
                'strategies': ['bollinger_stochastic', 'rsi_cci_atr', 'mean_reversion'],
                'tp_pips': 28,
                'sl_pips': 14,
                'min_consensus': 2
            },
            'EURAUD': {
                'strategies': ['bollinger_stochastic', 'rsi_cci_atr', 'mean_reversion'],
                'tp_pips': 22,
                'sl_pips': 11,
                'min_consensus': 2
            },
            'GBPAUD': {
                'strategies': ['bollinger_stochastic', 'rsi_cci_atr', 'mean_reversion'],
                'tp_pips': 28,
                'sl_pips': 14,
                'min_consensus': 2
            },
            'EURCHF': {
                'strategies': ['bollinger_stochastic', 'rsi_cci_atr', 'mean_reversion'],
                'tp_pips': 20,
                'sl_pips': 10,
                'min_consensus': 2
            },
            
            # Gold - 3 strategies
            'XAUUSD': {
                'strategies': ['ema_macd_atr', 'trend_momentum', 'breakout_system'],
                'tp_pips': 45,
                'sl_pips': 22,
                'min_consensus': 2
            },
            'GOLD': {
                'strategies': ['ema_macd_atr', 'trend_momentum', 'breakout_system'],
                'tp_pips': 45,
                'sl_pips': 22,
                'min_consensus': 2
            },
            
            # Oil - 3 strategies
            'XTIUSD': {
                'strategies': ['price_action_rsi', 'momentum_volatility', 'support_resistance'],
                'tp_pips': 55,
                'sl_pips': 27,
                'min_consensus': 2
            },
            'XBRUSD': {
                'strategies': ['price_action_rsi', 'momentum_volatility', 'support_resistance'],
                'tp_pips': 55,
                'sl_pips': 27,
                'min_consensus': 2
            },
            'USOIL': {
                'strategies': ['price_action_rsi', 'momentum_volatility', 'support_resistance'],
                'tp_pips': 55,
                'sl_pips': 27,
                'min_consensus': 2
            },
            'UKOIL': {
                'strategies': ['price_action_rsi', 'momentum_volatility', 'support_resistance'],
                'tp_pips': 55,
                'sl_pips': 27,
                'min_consensus': 2
            },
        }
    
    def analyze(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """
        Analyze symbol using multiple strategies with consensus voting
        
        Returns:
            action: 'BUY', 'SELL', or None
            confidence: 0-100
            details: Analysis details including all strategy votes
        """
        # Get strategies for symbol
        if symbol not in self.pair_strategies:
            # Default for unknown pairs
            config = {
                'strategies': ['ema_rsi_adx', 'macd_stochastic'],
                'tp_pips': 18,
                'sl_pips': 9,
                'min_consensus': 2
            }
        else:
            config = self.pair_strategies[symbol]
        
        # Run all strategies
        strategy_votes = []
        for strategy_name in config['strategies']:
            action, confidence, details = self._run_strategy(symbol, timeframe, strategy_name)
            strategy_votes.append({
                'strategy': strategy_name,
                'action': action,
                'confidence': confidence,
                'details': details
            })
        
        # Calculate consensus
        buy_votes = [v for v in strategy_votes if v['action'] == 'BUY']
        sell_votes = [v for v in strategy_votes if v['action'] == 'SELL']
        
        min_consensus = config['min_consensus']
        
        # Determine final action
        final_action = None
        final_confidence = 0
        consensus_details = {
            'total_strategies': len(strategy_votes),
            'min_consensus': min_consensus,
            'buy_votes': len(buy_votes),
            'sell_votes': len(sell_votes),
            'strategy_votes': strategy_votes,
            'tp_pips': config['tp_pips'],
            'sl_pips': config['sl_pips']
        }
        
        if len(buy_votes) >= min_consensus:
            final_action = 'BUY'
            # Average confidence of agreeing strategies
            final_confidence = sum(v['confidence'] for v in buy_votes) / len(buy_votes)
            consensus_details['consensus'] = f"{len(buy_votes)}/{len(strategy_votes)} strategies agree on BUY"
        elif len(sell_votes) >= min_consensus:
            final_action = 'SELL'
            final_confidence = sum(v['confidence'] for v in sell_votes) / len(sell_votes)
            consensus_details['consensus'] = f"{len(sell_votes)}/{len(strategy_votes)} strategies agree on SELL"
        else:
            consensus_details['consensus'] = "No consensus reached"
        
        return final_action, final_confidence, consensus_details
    
    def _run_strategy(self, symbol: str, timeframe, strategy_name: str) -> Tuple[Optional[str], float, Dict]:
        """Run a specific strategy"""
        if strategy_name == 'ema_rsi_adx':
            return self._ema_rsi_adx_strategy(symbol, timeframe)
        elif strategy_name == 'macd_stochastic':
            return self._macd_stochastic_strategy(symbol, timeframe)
        elif strategy_name == 'price_action_volume':
            return self._price_action_volume_strategy(symbol, timeframe)
        elif strategy_name == 'bollinger_stochastic':
            return self._bollinger_stochastic_strategy(symbol, timeframe)
        elif strategy_name == 'rsi_cci_atr':
            return self._rsi_cci_atr_strategy(symbol, timeframe)
        elif strategy_name == 'mean_reversion':
            return self._mean_reversion_strategy(symbol, timeframe)
        elif strategy_name == 'ema_macd_atr':
            return self._ema_macd_atr_strategy(symbol, timeframe)
        elif strategy_name == 'trend_momentum':
            return self._trend_momentum_strategy(symbol, timeframe)
        elif strategy_name == 'breakout_system':
            return self._breakout_system_strategy(symbol, timeframe)
        elif strategy_name == 'price_action_rsi':
            return self._price_action_rsi_strategy(symbol, timeframe)
        elif strategy_name == 'momentum_volatility':
            return self._momentum_volatility_strategy(symbol, timeframe)
        elif strategy_name == 'support_resistance':
            return self._support_resistance_strategy(symbol, timeframe)
        else:
            return None, 0, {}
    
    # ==================== MAJOR PAIR STRATEGIES ====================
    
    def _ema_rsi_adx_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """EMA + RSI + ADX - Research-backed trend following"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # EMAs (20, 50)
        ema_20 = df['close'].ewm(span=20, adjust=False).mean()
        ema_50 = df['close'].ewm(span=50, adjust=False).mean()
        
        # RSI (14)
        rsi = self._calculate_rsi(df['close'], 14)
        
        # ADX (14)
        adx = self._calculate_adx(df, 14)
        
        current_price = df['close'].iloc[-1]
        current_ema20 = ema_20.iloc[-1]
        current_ema50 = ema_50.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_adx = adx.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions
        if current_ema20 > current_ema50:  # Uptrend
            score += 35
            if current_rsi < 50 and current_rsi > 30:  # RSI in buy zone
                score += 30
            if current_adx > 20:  # Strong trend
                score += 25
            if current_price < current_ema20:  # Pullback
                score += 10
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_ema20 < current_ema50:  # Downtrend
            sell_score += 35
            if current_rsi > 50 and current_rsi < 70:  # RSI in sell zone
                sell_score += 30
            if current_adx > 20:  # Strong trend
                sell_score += 25
            if current_price > current_ema20:  # Pullback
                sell_score += 10
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'rsi': current_rsi, 'adx': current_adx, 'ema_trend': 'UP' if current_ema20 > current_ema50 else 'DOWN'}
    
    def _macd_stochastic_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """MACD + Stochastic - Momentum confirmation"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # MACD
        macd_line, signal_line, macd_hist = self._calculate_macd(df['close'], 12, 26, 9)
        
        # Stochastic
        stoch_k, stoch_d = self._calculate_stochastic(df, 14, 3)
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_stoch_k = stoch_k.iloc[-1]
        current_stoch_d = stoch_d.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions
        if current_macd > current_signal:  # MACD bullish
            score += 40
        if current_stoch_k < 30 and current_stoch_k > current_stoch_d:  # Stoch turning up
            score += 40
        if current_stoch_k < 20:  # Oversold
            score += 20
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_macd < current_signal:  # MACD bearish
            sell_score += 40
        if current_stoch_k > 70 and current_stoch_k < current_stoch_d:  # Stoch turning down
            sell_score += 40
        if current_stoch_k > 80:  # Overbought
            sell_score += 20
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'macd': current_macd, 'signal': current_signal, 'stoch': current_stoch_k}
    
    def _price_action_volume_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Price Action + Volume - Pure price movement"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 50:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # Calculate price action signals
        # Higher highs / Lower lows
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        current_close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        
        # Volume trend
        avg_volume = df['tick_volume'].tail(20).mean()
        current_volume = df['tick_volume'].iloc[-1]
        
        # Candle patterns
        body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        candle_range = df['high'].iloc[-1] - df['low'].iloc[-1]
        body_ratio = body / candle_range if candle_range > 0 else 0
        
        score = 0
        action = None
        
        # BUY conditions
        if current_close > prev_close:  # Bullish candle
            score += 25
        if current_close > recent_high * 0.995:  # Near recent high
            score += 25
        if current_volume > avg_volume * 1.2:  # High volume
            score += 25
        if body_ratio > 0.6:  # Strong body
            score += 25
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_close < prev_close:  # Bearish candle
            sell_score += 25
        if current_close < recent_low * 1.005:  # Near recent low
            sell_score += 25
        if current_volume > avg_volume * 1.2:  # High volume
            sell_score += 25
        if body_ratio > 0.6:  # Strong body
            sell_score += 25
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'volume_ratio': current_volume / avg_volume, 'body_ratio': body_ratio}
    
    # ==================== CROSS PAIR STRATEGIES ====================
    
    def _bollinger_stochastic_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Bollinger Bands + Stochastic - Mean reversion"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # Bollinger Bands
        bb_middle = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # Stochastic
        stoch_k, stoch_d = self._calculate_stochastic(df, 14, 3)
        
        current_price = df['close'].iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        current_stoch_k = stoch_k.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions (bounce from lower band)
        dist_to_lower = ((current_price - current_bb_lower) / current_bb_lower) * 100
        if dist_to_lower < 0.2:  # Very close to lower band
            score += 40
        if current_stoch_k < 25:  # Oversold
            score += 40
        if current_stoch_k < 20:  # Very oversold
            score += 20
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions (bounce from upper band)
        sell_score = 0
        dist_to_upper = ((current_bb_upper - current_price) / current_price) * 100
        if dist_to_upper < 0.2:  # Very close to upper band
            sell_score += 40
        if current_stoch_k > 75:  # Overbought
            sell_score += 40
        if current_stoch_k > 80:  # Very overbought
            sell_score += 20
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'bb_position': 'LOWER' if dist_to_lower < dist_to_upper else 'UPPER', 'stoch': current_stoch_k}
    
    def _rsi_cci_atr_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """RSI + CCI + ATR - Volatility-aware oscillator"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # RSI
        rsi = self._calculate_rsi(df['close'], 14)
        
        # CCI
        cci = self._calculate_cci(df, 14)
        
        # ATR
        atr = self._calculate_atr(df, 14)
        atr_avg = atr.rolling(window=20).mean()
        
        current_rsi = rsi.iloc[-1]
        current_cci = cci.iloc[-1]
        current_atr = atr.iloc[-1]
        current_atr_avg = atr_avg.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions
        if current_rsi < 35:  # Oversold
            score += 35
        if current_cci < -100:  # CCI oversold
            score += 35
        if current_atr < current_atr_avg * 1.3:  # Normal volatility
            score += 30
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_rsi > 65:  # Overbought
            sell_score += 35
        if current_cci > 100:  # CCI overbought
            sell_score += 35
        if current_atr < current_atr_avg * 1.3:  # Normal volatility
            sell_score += 30
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'rsi': current_rsi, 'cci': current_cci, 'atr_ratio': current_atr / current_atr_avg}
    
    def _mean_reversion_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Mean Reversion - Statistical approach"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # Calculate mean and standard deviation
        sma_50 = df['close'].rolling(window=50).mean()
        std_50 = df['close'].rolling(window=50).std()
        
        current_price = df['close'].iloc[-1]
        current_sma = sma_50.iloc[-1]
        current_std = std_50.iloc[-1]
        
        # Z-score
        z_score = (current_price - current_sma) / current_std if current_std > 0 else 0
        
        score = 0
        action = None
        
        # BUY conditions (price below mean)
        if z_score < -1.5:  # 1.5 std below mean
            score += 50
        elif z_score < -1.0:  # 1 std below mean
            score += 35
        
        if current_price < current_sma:  # Below mean
            score += 30
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions (price above mean)
        sell_score = 0
        if z_score > 1.5:  # 1.5 std above mean
            sell_score += 50
        elif z_score > 1.0:  # 1 std above mean
            sell_score += 35
        
        if current_price > current_sma:  # Above mean
            sell_score += 30
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'z_score': z_score, 'price_vs_mean': 'ABOVE' if current_price > current_sma else 'BELOW'}
    
    # ==================== GOLD STRATEGIES ====================
    
    def _ema_macd_atr_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """EMA + MACD + ATR - Trend following for gold"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # EMAs
        ema_50 = df['close'].ewm(span=50, adjust=False).mean()
        ema_200 = df['close'].ewm(span=200, adjust=False).mean()
        
        # MACD
        macd_line, signal_line, macd_hist = self._calculate_macd(df['close'], 12, 26, 9)
        
        # ATR
        atr = self._calculate_atr(df, 14)
        atr_avg = atr.rolling(window=20).mean()
        
        current_price = df['close'].iloc[-1]
        current_ema50 = ema_50.iloc[-1]
        current_ema200 = ema_200.iloc[-1]
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_atr = atr.iloc[-1]
        current_atr_avg = atr_avg.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions
        if current_ema50 > current_ema200:  # Long-term uptrend
            score += 35
        if current_macd > current_signal:  # MACD bullish
            score += 35
        if current_price > current_ema50:  # Price above 50 EMA
            score += 20
        if current_atr < current_atr_avg * 1.5:  # Normal volatility
            score += 10
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_ema50 < current_ema200:  # Long-term downtrend
            sell_score += 35
        if current_macd < current_signal:  # MACD bearish
            sell_score += 35
        if current_price < current_ema50:  # Price below 50 EMA
            sell_score += 20
        if current_atr < current_atr_avg * 1.5:  # Normal volatility
            sell_score += 10
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'ema_trend': 'UP' if current_ema50 > current_ema200 else 'DOWN', 'macd_signal': 'BULL' if current_macd > current_signal else 'BEAR'}
    
    def _trend_momentum_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Trend + Momentum - Combined approach"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # ADX for trend strength
        adx = self._calculate_adx(df, 14)
        
        # RSI for momentum
        rsi = self._calculate_rsi(df['close'], 14)
        
        # Momentum
        momentum = df['close'].diff(10)
        
        current_adx = adx.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_momentum = momentum.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions
        if current_adx > 25:  # Strong trend
            score += 35
        if current_momentum > 0:  # Positive momentum
            score += 35
        if current_rsi < 60 and current_rsi > 40:  # RSI in neutral-bullish zone
            score += 30
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_adx > 25:  # Strong trend
            sell_score += 35
        if current_momentum < 0:  # Negative momentum
            sell_score += 35
        if current_rsi > 40 and current_rsi < 60:  # RSI in neutral-bearish zone
            sell_score += 30
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'adx': current_adx, 'momentum': 'POSITIVE' if current_momentum > 0 else 'NEGATIVE'}
    
    def _breakout_system_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Breakout System - Donchian channels"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 50:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # Donchian Channels (20 period)
        upper_channel = df['high'].rolling(window=20).max()
        lower_channel = df['low'].rolling(window=20).min()
        
        # Volume
        avg_volume = df['tick_volume'].tail(20).mean()
        current_volume = df['tick_volume'].iloc[-1]
        
        current_price = df['close'].iloc[-1]
        current_upper = upper_channel.iloc[-1]
        current_lower = lower_channel.iloc[-1]
        prev_high = df['high'].iloc[-2]
        prev_low = df['low'].iloc[-2]
        
        score = 0
        action = None
        
        # BUY conditions (breakout above)
        if current_price > current_upper and prev_high <= current_upper:  # Fresh breakout
            score += 50
        if current_volume > avg_volume * 1.3:  # High volume
            score += 30
        if current_price > current_upper * 0.999:  # Near upper channel
            score += 20
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions (breakout below)
        sell_score = 0
        if current_price < current_lower and prev_low >= current_lower:  # Fresh breakout
            sell_score += 50
        if current_volume > avg_volume * 1.3:  # High volume
            sell_score += 30
        if current_price < current_lower * 1.001:  # Near lower channel
            sell_score += 20
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'breakout': 'YES' if score >= 50 or sell_score >= 50 else 'NO', 'volume_ratio': current_volume / avg_volume}
    
    # ==================== OIL STRATEGIES ====================
    
    def _price_action_rsi_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Price Action + RSI - For news-driven instruments"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # RSI
        rsi = self._calculate_rsi(df['close'], 14)
        
        # Price action
        current_close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
        
        # Candle strength
        body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        candle_range = df['high'].iloc[-1] - df['low'].iloc[-1]
        body_ratio = body / candle_range if candle_range > 0 else 0
        
        current_rsi = rsi.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions
        if current_rsi < 40:  # Oversold
            score += 40
        if current_close > prev_close:  # Bullish candle
            score += 30
        if body_ratio > 0.6:  # Strong candle
            score += 20
        if current_close > sma_20:  # Above SMA
            score += 10
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_rsi > 60:  # Overbought
            sell_score += 40
        if current_close < prev_close:  # Bearish candle
            sell_score += 30
        if body_ratio > 0.6:  # Strong candle
            sell_score += 20
        if current_close < sma_20:  # Below SMA
            sell_score += 10
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'rsi': current_rsi, 'candle_strength': body_ratio}
    
    def _momentum_volatility_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Momentum + Volatility - Adaptive to market conditions"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # Momentum
        momentum = df['close'].diff(10)
        
        # ATR
        atr = self._calculate_atr(df, 14)
        atr_avg = atr.rolling(window=20).mean()
        
        # Rate of change
        roc = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
        
        current_momentum = momentum.iloc[-1]
        current_atr = atr.iloc[-1]
        current_atr_avg = atr_avg.iloc[-1]
        current_roc = roc.iloc[-1]
        
        score = 0
        action = None
        
        # BUY conditions
        if current_momentum > 0:  # Positive momentum
            score += 40
        if current_roc > 0.5:  # Strong rate of change
            score += 30
        if current_atr > current_atr_avg:  # Increasing volatility
            score += 30
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions
        sell_score = 0
        if current_momentum < 0:  # Negative momentum
            sell_score += 40
        if current_roc < -0.5:  # Strong rate of change down
            sell_score += 30
        if current_atr > current_atr_avg:  # Increasing volatility
            sell_score += 30
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'momentum': 'POSITIVE' if current_momentum > 0 else 'NEGATIVE', 'volatility': 'HIGH' if current_atr > current_atr_avg else 'NORMAL'}
    
    def _support_resistance_strategy(self, symbol: str, timeframe) -> Tuple[Optional[str], float, Dict]:
        """Support/Resistance - Key levels"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) < 100:
            return None, 0, {}
        
        df = pd.DataFrame(rates)
        
        # Find recent highs and lows (pivot points)
        recent_highs = df['high'].tail(50).nlargest(5).mean()
        recent_lows = df['low'].tail(50).nsmallest(5).mean()
        
        current_price = df['close'].iloc[-1]
        current_volume = df['tick_volume'].iloc[-1]
        avg_volume = df['tick_volume'].tail(20).mean()
        
        # Distance to support/resistance
        dist_to_support = ((current_price - recent_lows) / recent_lows) * 100
        dist_to_resistance = ((recent_highs - current_price) / current_price) * 100
        
        score = 0
        action = None
        
        # BUY conditions (near support)
        if dist_to_support < 0.3:  # Very close to support
            score += 50
        if current_volume > avg_volume * 1.2:  # High volume
            score += 30
        if dist_to_support < dist_to_resistance:  # Closer to support
            score += 20
        
        if score >= 60:
            action = 'BUY'
        
        # SELL conditions (near resistance)
        sell_score = 0
        if dist_to_resistance < 0.3:  # Very close to resistance
            sell_score += 50
        if current_volume > avg_volume * 1.2:  # High volume
            sell_score += 30
        if dist_to_resistance < dist_to_support:  # Closer to resistance
            sell_score += 20
        
        if sell_score > score and sell_score >= 60:
            action = 'SELL'
            score = sell_score
        
        return action, score, {'near_level': 'SUPPORT' if dist_to_support < dist_to_resistance else 'RESISTANCE', 'distance': min(dist_to_support, dist_to_resistance)}
    
    # ==================== INDICATOR CALCULATIONS ====================
    
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
    
    def _calculate_adx(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average Directional Index"""
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()
        
        pos_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        neg_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        atr = self._calculate_atr(df, period)
        
        pos_di = 100 * (pos_dm.rolling(window=period).mean() / atr)
        neg_di = 100 * (neg_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * np.abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(window=period).mean()
        
        return adx

