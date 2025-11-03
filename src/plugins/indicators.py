"""
Technical Indicators Module

Provides technical analysis indicators for trading strategies.
Uses the 'ta' library for calculations.

All indicators accept pandas DataFrame with OHLCV data and return boolean signals
or numeric values that can be used for trading decisions.
"""

import pandas as pd
import ta
from typing import Dict, Any, Optional, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class TechnicalIndicators:
    """
    Technical indicators for trading strategies.
    
    All methods accept a DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
    """
    
    @staticmethod
    def get_rsi(df: pd.DataFrame, period: int = 14) -> Tuple[float, bool]:
        """
        Get RSI (Relative Strength Index) value and rising status.

        Args:
            df: OHLCV DataFrame
            period: RSI period (default: 14)

        Returns:
            Tuple of (current_rsi, is_rising)
        """
        if len(df) < period + 2:
            return 50.0, False

        rsi_ind = ta.momentum.rsi(close=df['close'], window=period)
        rsi = rsi_ind.values[-1]
        rsi_prev = rsi_ind.values[-2]
        rising = rsi > rsi_prev

        return rsi, rising

    @staticmethod
    def is_rsi_rising(df: pd.DataFrame, period: int = 14, lookback: int = 3) -> bool:
        """
        Check if RSI is in an upward trend over multiple periods.
        This helps identify if momentum is building (price might continue rising).

        Args:
            df: OHLCV DataFrame
            period: RSI period (default: 14)
            lookback: Number of periods to check for rising trend (default: 3)

        Returns:
            True if RSI has been rising for 'lookback' periods
        """
        if len(df) < period + lookback:
            return False

        rsi_ind = ta.momentum.rsi(close=df['close'], window=period)
        rsi_values = rsi_ind.values[-lookback:]

        # Check if each RSI value is higher than the previous
        for i in range(1, len(rsi_values)):
            if rsi_values[i] <= rsi_values[i-1]:
                return False

        return True
    
    @staticmethod
    def is_rsi_oversold(df: pd.DataFrame, period: int = 14, oversold_level: float = 30) -> bool:
        """
        Check if RSI indicates oversold condition.
        
        Args:
            df: OHLCV DataFrame
            period: RSI period (default: 14)
            oversold_level: Oversold threshold (default: 30)
            
        Returns:
            True if oversold
        """
        rsi, _ = TechnicalIndicators.get_rsi(df, period)
        return rsi <= oversold_level
    
    @staticmethod
    def is_rsi_overbought(df: pd.DataFrame, period: int = 14, overbought_level: float = 70) -> bool:
        """
        Check if RSI indicates overbought condition.
        
        Args:
            df: OHLCV DataFrame
            period: RSI period (default: 14)
            overbought_level: Overbought threshold (default: 70)
            
        Returns:
            True if overbought
        """
        rsi, _ = TechnicalIndicators.get_rsi(df, period)
        return rsi >= overbought_level
    
    @staticmethod
    def get_stoch_rsi(df: pd.DataFrame, period: int = 14, smooth: int = 3) -> float:
        """
        Get Stochastic RSI value.
        
        Args:
            df: OHLCV DataFrame
            period: Stochastic period (default: 14)
            smooth: Smoothing period (default: 3)
            
        Returns:
            Current Stochastic RSI value
        """
        stoch_ind = ta.momentum.stoch(
            high=df['high'], 
            low=df['low'], 
            close=df['close'], 
            window=period,
            smooth_window=smooth
        )
        return stoch_ind.values[-1]
    
    @staticmethod
    def is_stoch_oversold(df: pd.DataFrame, period: int = 14, smooth: int = 3, oversold_level: float = 20) -> bool:
        """
        Check if Stochastic RSI indicates oversold condition.
        
        Args:
            df: OHLCV DataFrame
            period: Stochastic period (default: 14)
            smooth: Smoothing period (default: 3)
            oversold_level: Oversold threshold (default: 20)
            
        Returns:
            True if oversold
        """
        stoch = TechnicalIndicators.get_stoch_rsi(df, period, smooth)
        return stoch <= oversold_level
    
    @staticmethod
    def get_ema(df: pd.DataFrame, length: int = 25) -> float:
        """
        Get EMA (Exponential Moving Average) value.
        
        Args:
            df: OHLCV DataFrame
            length: EMA period (default: 25)
            
        Returns:
            Current EMA value
        """
        ema_ind = ta.trend.ema_indicator(close=df['close'], window=length)
        return ema_ind.values[-1]
    
    @staticmethod
    def is_price_below_ema(df: pd.DataFrame, length: int = 25) -> bool:
        """
        Check if current price is below EMA.
        
        Args:
            df: OHLCV DataFrame
            length: EMA period (default: 25)
            
        Returns:
            True if price is below EMA
        """
        ema = TechnicalIndicators.get_ema(df, length)
        current_price = df['close'].values[-1]
        return current_price < ema
    
    @staticmethod
    def get_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """
        Get MACD (Moving Average Convergence Divergence) values.
        
        Args:
            df: OHLCV DataFrame
            fast: Fast period (default: 12)
            slow: Slow period (default: 26)
            signal: Signal period (default: 9)
            
        Returns:
            Tuple of (macd, signal, histogram)
        """
        macd_ind = ta.trend.macd(close=df['close'], window_slow=slow, window_fast=fast, window_sign=signal)
        macd_signal = ta.trend.macd_signal(close=df['close'], window_slow=slow, window_fast=fast, window_sign=signal)
        macd_diff = ta.trend.macd_diff(close=df['close'], window_slow=slow, window_fast=fast, window_sign=signal)
        
        return macd_ind.values[-1], macd_signal.values[-1], macd_diff.values[-1]
    
    @staticmethod
    def is_macd_rising(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> bool:
        """
        Check if MACD histogram is rising (bullish).
        
        Args:
            df: OHLCV DataFrame
            fast: Fast period (default: 12)
            slow: Slow period (default: 26)
            signal: Signal period (default: 9)
            
        Returns:
            True if MACD is rising
        """
        macd_diff = ta.trend.macd_diff(close=df['close'], window_slow=slow, window_fast=fast, window_sign=signal)
        current = macd_diff.values[-1]
        previous = macd_diff.values[-2]
        return current > previous
    
    @staticmethod
    def is_macd_positive(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> bool:
        """
        Check if MACD histogram is positive (bullish).
        
        Args:
            df: OHLCV DataFrame
            fast: Fast period (default: 12)
            slow: Slow period (default: 26)
            signal: Signal period (default: 9)
            
        Returns:
            True if MACD is positive
        """
        _, _, histogram = TechnicalIndicators.get_macd(df, fast, slow, signal)
        return histogram > 0
    
    @staticmethod
    def get_mfi(df: pd.DataFrame, period: int = 14) -> float:
        """
        Get MFI (Money Flow Index) value.
        
        Args:
            df: OHLCV DataFrame
            period: MFI period (default: 14)
            
        Returns:
            Current MFI value
        """
        mfi_ind = ta.volume.money_flow_index(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume'],
            window=period
        )
        return mfi_ind.values[-1]
    
    @staticmethod
    def is_mfi_oversold(df: pd.DataFrame, period: int = 14, oversold_level: float = 20) -> bool:
        """
        Check if MFI indicates oversold condition.
        
        Args:
            df: OHLCV DataFrame
            period: MFI period (default: 14)
            oversold_level: Oversold threshold (default: 20)
            
        Returns:
            True if oversold
        """
        mfi = TechnicalIndicators.get_mfi(df, period)
        return mfi <= oversold_level
    
    @staticmethod
    def has_price_dropped(df: pd.DataFrame, lookback: int = 24, drop_percent: float = 1.0) -> bool:
        """
        Check if price has dropped by a certain percentage over lookback period.
        
        Args:
            df: OHLCV DataFrame
            lookback: Number of candles to look back (default: 24)
            drop_percent: Minimum drop percentage (default: 1.0%)
            
        Returns:
            True if price has dropped by drop_percent or more
        """
        if len(df) < lookback:
            return False
        
        current_price = df['close'].values[-1]
        past_price = df['close'].values[-lookback]
        
        percent_change = ((current_price - past_price) / past_price) * 100
        
        return percent_change <= -drop_percent
    
    @staticmethod
    def is_price_rising(df: pd.DataFrame, lookback: int = 3) -> bool:
        """
        Check if price is rising over recent candles.

        Args:
            df: OHLCV DataFrame
            lookback: Number of candles to check (default: 3)

        Returns:
            True if price is rising
        """
        if len(df) < lookback:
            return False

        prices = df['close'].values[-lookback:]

        # Check if each price is higher than the previous
        for i in range(1, len(prices)):
            if prices[i] <= prices[i-1]:
                return False

        return True

    @staticmethod
    def calculate_sell_price_with_fees(
        buy_price: float,
        buy_fee_percent: float,
        sell_fee_percent: float,
        profit_target_percent: float
    ) -> float:
        """
        Calculate the sell price needed to achieve target profit after all fees.

        Formula:
        1. Total cost = buy_price + (buy_price × buy_fee%)
        2. Target with profit = total_cost × (1 + profit_target%)
        3. Sell price = target_with_profit / (1 - sell_fee%)

        Args:
            buy_price: Price at which asset was bought
            buy_fee_percent: Buy fee as percentage (e.g., 0.1 for 0.1%)
            sell_fee_percent: Sell fee as percentage (e.g., 0.1 for 0.1%)
            profit_target_percent: Desired profit as percentage (e.g., 1.0 for 1%)

        Returns:
            Sell price that achieves target profit after all fees

        Example:
            >>> calculate_sell_price_with_fees(50000, 0.1, 0.1, 1.0)
            50601.05
            # Buy at $50,000, pay 0.1% fee = $50
            # Total cost = $50,050
            # Want 1% profit = $500.50
            # Target = $50,550.50
            # Need to account for 0.1% sell fee
            # Sell price = $50,601.05
        """
        # Convert percentages to decimals
        buy_fee = buy_fee_percent / 100.0
        sell_fee = sell_fee_percent / 100.0
        profit_target = profit_target_percent / 100.0

        # Calculate total cost including buy fee
        total_cost = buy_price * (1 + buy_fee)

        # Calculate target price with desired profit
        target_with_profit = total_cost * (1 + profit_target)

        # Calculate sell price accounting for sell fee
        # sell_price * (1 - sell_fee) = target_with_profit
        # sell_price = target_with_profit / (1 - sell_fee)
        sell_price = target_with_profit / (1 - sell_fee)

        return sell_price

    @staticmethod
    def calculate_actual_profit_percent(
        buy_price: float,
        sell_price: float,
        buy_fee_percent: float,
        sell_fee_percent: float
    ) -> float:
        """
        Calculate actual profit percentage after all fees.

        Args:
            buy_price: Price at which asset was bought
            sell_price: Price at which asset was sold
            buy_fee_percent: Buy fee as percentage (e.g., 0.1 for 0.1%)
            sell_fee_percent: Sell fee as percentage (e.g., 0.1 for 0.1%)

        Returns:
            Actual profit percentage after fees
        """
        # Convert percentages to decimals
        buy_fee = buy_fee_percent / 100.0
        sell_fee = sell_fee_percent / 100.0

        # Calculate total cost including buy fee
        total_cost = buy_price * (1 + buy_fee)

        # Calculate proceeds after sell fee
        proceeds = sell_price * (1 - sell_fee)

        # Calculate profit percentage
        profit_percent = ((proceeds - total_cost) / total_cost) * 100.0

        return profit_percent

