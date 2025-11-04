"""
Backtest Engine - Test Trading Strategies on Historical Data

Allows testing strategies on historical data before risking real money.

Features:
- Historical data replay
- Simulated order execution
- Performance metrics
- Trade analysis
- Strategy optimization

This is CRITICAL for validating strategies before live trading.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)


class BacktestEngine:
    """
    Backtest engine for testing strategies on historical data.
    
    Simulates trading by replaying historical price data and
    executing strategy logic as if it were live.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize backtest engine.

        Args:
            config: Backtest configuration
        """
        self.config = config
        self.symbol = config.get('symbol', 'BTC/USD')
        self.start_date = config.get('start_date')
        self.end_date = config.get('end_date')
        self.initial_balance = config.get('initial_balance', 10000.0)

        # State
        self.balance = self.initial_balance
        self.position = 0.0  # Current position size
        self.position_cost = 0.0  # Total cost of current position
        self.trades = []
        self.equity_curve = []

        # Strategy
        self.strategy = None

        # Backtest mode flag (reduces logging noise)
        self.is_backtest = True

        logger.info(f"Backtest engine initialized")
        logger.info(f"  Symbol: {self.symbol}")
        logger.info(f"  Period: {self.start_date} to {self.end_date}")
        logger.info(f"  Initial balance: ${self.initial_balance:,.2f}")
    
    def load_historical_data(self, data_source: str) -> pd.DataFrame:
        """
        Load historical price data.
        
        Args:
            data_source: Path to CSV file or exchange API
            
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Loading historical data from {data_source}")
        
        # TODO: Implement data loading from:
        # 1. CSV files
        # 2. Exchange API (ccxt)
        # 3. Database
        
        # For now, return empty DataFrame
        # This will be implemented based on user's data source
        df = pd.DataFrame()
        
        logger.info(f"Loaded {len(df)} candles")
        return df
    
    def set_strategy(self, strategy):
        """
        Set the trading strategy to backtest.

        Args:
            strategy: Strategy instance
        """
        self.strategy = strategy
        # Set backtest mode on strategy to reduce logging
        if hasattr(strategy, 'is_backtest'):
            strategy.is_backtest = True
        logger.info(f"Strategy set: {strategy.config.get('name')}")
    
    def run(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run backtest on historical data.

        Args:
            historical_data: DataFrame with OHLCV data

        Returns:
            Backtest results dictionary
        """
        logger.info("=" * 60)
        logger.info("Starting backtest...")
        logger.info("=" * 60)

        if self.strategy is None:
            raise ValueError("No strategy set. Call set_strategy() first.")

        if historical_data.empty:
            raise ValueError("No historical data provided")

        # Store full historical data
        self.historical_data = historical_data

        # Initialize strategy
        self.strategy.initialize(self)

        # Minimum lookback period for indicators (need enough data to calculate)
        # Most indicators need at least 50 candles (e.g., RSI 14, EMA 26, MACD 26+9)
        min_lookback = 100

        logger.info(f"Processing {len(historical_data)} candles...")
        logger.info(f"Using {min_lookback} candle lookback for indicator calculations")

        # Iterate through historical data (starting after min_lookback)
        for i in range(min_lookback, len(historical_data)):
            # Get current candle
            current_candle = historical_data.iloc[i]

            # Get lookback window for indicator calculations
            lookback_window = historical_data.iloc[max(0, i-200):i+1]  # Last 200 candles + current

            self._process_candle(current_candle, lookback_window, i, len(historical_data))

        # Calculate final results
        results = self._calculate_results()

        # Display final summary
        from colorama import Fore, Style

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"{Fore.CYAN}{'BACKTEST RESULTS':^70}{Style.RESET_ALL}")
        logger.info("=" * 70)

        # Financial metrics
        final_equity = results['final_equity']
        profit_loss = results['total_profit']
        profit_loss_pct = results['return_pct']

        pl_color = Fore.GREEN if profit_loss >= 0 else Fore.RED
        pl_sign = "+" if profit_loss >= 0 else ""

        logger.info(f"Initial Balance:      ${self.initial_balance:,.2f}")
        logger.info(f"Final Balance:        ${self.balance:,.2f}")
        logger.info(f"Final Position:       {self.position:.8f}")
        logger.info(f"Final Equity:         ${final_equity:,.2f}")
        logger.info(f"Total Profit/Loss:    {pl_color}{pl_sign}${profit_loss:,.2f} ({pl_sign}{profit_loss_pct:.2f}%){Style.RESET_ALL}")
        logger.info("")

        # Trading metrics
        logger.info(f"Total Trades:         {results['total_trades']}")
        logger.info(f"Winning Trades:       {Fore.GREEN}{results['winning_trades']}{Style.RESET_ALL}")
        logger.info(f"Losing Trades:        {Fore.RED}{results['losing_trades']}{Style.RESET_ALL}")

        if results['total_trades'] > 0:
            win_rate = (results['winning_trades'] / results['total_trades']) * 100
            win_color = Fore.GREEN if win_rate >= 50 else Fore.YELLOW if win_rate >= 30 else Fore.RED
            logger.info(f"Win Rate:             {win_color}{win_rate:.1f}%{Style.RESET_ALL}")

        logger.info("")
        logger.info(f"Max Drawdown:         {Fore.RED}{results['max_drawdown']:.2f}%{Style.RESET_ALL}")
        logger.info(f"Sharpe Ratio:         {results['sharpe_ratio']:.2f}")
        logger.info("=" * 70)

        return results
    
    def _process_candle(self, candle: pd.Series, lookback_df: pd.DataFrame, current_index: int, total_candles: int):
        """
        Process a single candle (bar) of historical data.

        Args:
            candle: Series with OHLCV data for current candle
            lookback_df: DataFrame with historical lookback window for indicator calculations
            current_index: Current position in the historical data
            total_candles: Total number of candles being processed
        """
        # Progress logging (every 1000 candles)
        if current_index % 1000 == 0:
            progress = (current_index / total_candles) * 100

            # Calculate current equity (balance + position value)
            current_price = candle.get('close')
            position_value = self.position * current_price
            equity = self.balance + position_value

            # Calculate profit/loss
            profit_loss = equity - self.initial_balance
            profit_loss_pct = (profit_loss / self.initial_balance) * 100

            # Format profit/loss with color
            from colorama import Fore, Style
            if profit_loss >= 0:
                pl_color = Fore.GREEN
                pl_sign = "+"
            else:
                pl_color = Fore.RED
                pl_sign = ""

            logger.info(f"Progress: {progress:.1f}% ({current_index}/{total_candles} candles) | "
                       f"Balance: ${self.balance:,.2f} | "
                       f"Position: {self.position:.8f} | "
                       f"Equity: ${equity:,.2f} | "
                       f"P/L: {pl_color}{pl_sign}${profit_loss:,.2f} ({pl_sign}{profit_loss_pct:.2f}%){Style.RESET_ALL}")

        # Create market data dict for strategy
        market_data = {
            'timestamp': candle.get('timestamp'),
            'open': candle.get('open'),
            'high': candle.get('high'),
            'low': candle.get('low'),
            'close': candle.get('close'),
            'volume': candle.get('volume'),
            'last': candle.get('close'),  # Use close as last price
            'ohlcv': lookback_df  # CRITICAL: Pass the lookback window for indicator calculations
        }

        # Run strategy analysis
        signal = self.strategy.analyze(market_data)

        # Execute signal
        if signal['action'] == 'buy':
            self._execute_buy(signal, market_data)
        elif signal['action'] == 'sell':
            self._execute_sell(signal, market_data)

        # Record equity
        current_price = market_data['close']
        equity = self.balance + (self.position * current_price)

        self.equity_curve.append({
            'timestamp': market_data['timestamp'],
            'equity': equity,
            'balance': self.balance,
            'position': self.position,
            'price': current_price
        })
    
    def _execute_buy(self, signal: Dict[str, Any], market_data: Dict[str, Any]):
        """
        Execute simulated buy order.
        
        Args:
            signal: Buy signal from strategy
            market_data: Current market data
        """
        metadata = signal.get('metadata', {})
        price = metadata.get('price', market_data['close'])
        amount = metadata.get('amount', 0)
        
        if amount <= 0:
            return
        
        # Calculate cost
        cost = amount * price

        # Check if we have enough balance
        if cost > self.balance:
            logger.debug(f"Insufficient balance for buy: ${cost:.2f} > ${self.balance:.2f}")
            return
        
        # Execute buy
        self.balance -= cost
        self.position += amount
        self.position_cost += cost
        
        # Record trade
        trade = {
            'timestamp': market_data['timestamp'],
            'type': 'buy',
            'price': price,
            'amount': amount,
            'cost': cost,
            'balance': self.balance,
            'position': self.position
        }
        self.trades.append(trade)
        
        logger.debug(f"BUY: {amount:.8f} @ ${price:.2f} = ${cost:.2f}")
    
    def _execute_sell(self, signal: Dict[str, Any], market_data: Dict[str, Any]):
        """
        Execute simulated sell order.
        
        Args:
            signal: Sell signal from strategy
            market_data: Current market data
        """
        metadata = signal.get('metadata', {})
        price = metadata.get('price', market_data['close'])
        amount = metadata.get('amount', 0)
        
        if amount <= 0:
            return
        
        # Check if we have enough position
        if amount > self.position:
            logger.warning(f"Insufficient position for sell: {amount:.8f} > {self.position:.8f}")
            return
        
        # Execute sell
        proceeds = amount * price
        self.balance += proceeds
        
        # Calculate profit for this portion
        avg_cost = self.position_cost / self.position if self.position > 0 else 0
        cost_of_sold = amount * avg_cost
        profit = proceeds - cost_of_sold
        
        self.position -= amount
        self.position_cost -= cost_of_sold
        
        # Record trade
        trade = {
            'timestamp': market_data['timestamp'],
            'type': 'sell',
            'price': price,
            'amount': amount,
            'proceeds': proceeds,
            'profit': profit,
            'balance': self.balance,
            'position': self.position
        }
        self.trades.append(trade)
        
        logger.debug(f"SELL: {amount:.8f} @ ${price:.2f} = ${proceeds:.2f} (P&L: ${profit:.2f})")
    
    def _calculate_results(self) -> Dict[str, Any]:
        """
        Calculate backtest results and performance metrics.
        
        Returns:
            Results dictionary with performance metrics
        """
        # Final equity
        final_equity = self.equity_curve[-1]['equity'] if self.equity_curve else self.initial_balance
        
        # Total return
        total_return = final_equity - self.initial_balance
        total_return_pct = (total_return / self.initial_balance) * 100
        
        # Trade statistics
        total_trades = len(self.trades)
        buy_trades = [t for t in self.trades if t['type'] == 'buy']
        sell_trades = [t for t in self.trades if t['type'] == 'sell']
        
        # Profit/loss from completed trades
        winning_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in sell_trades if t.get('profit', 0) < 0]
        
        win_rate = (len(winning_trades) / len(sell_trades) * 100) if sell_trades else 0
        
        # Average profit/loss
        avg_win = sum(t['profit'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['profit'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Max drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        results = {
            'initial_balance': self.initial_balance,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': total_trades,
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        return results
    
    def _calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Returns:
            Maximum drawdown as percentage
        """
        if not self.equity_curve:
            return 0.0
        
        equity_values = [e['equity'] for e in self.equity_curve]
        
        max_equity = equity_values[0]
        max_drawdown = 0.0
        
        for equity in equity_values:
            if equity > max_equity:
                max_equity = equity
            
            drawdown = ((max_equity - equity) / max_equity) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def place_order(self, symbol: str, side: str, amount: float, price: float, order_type: str = 'limit') -> Dict[str, Any]:
        """
        Simulated order placement (called by strategy).
        
        This mimics the exchange API but executes immediately in backtest.
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            amount: Order amount
            price: Order price
            order_type: Order type
            
        Returns:
            Simulated order result
        """
        # In backtest, orders execute immediately at specified price
        order = {
            'id': f"backtest_{len(self.trades)}",
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'type': order_type,
            'status': 'closed',  # Immediately filled in backtest
            'filled': amount
        }
        
        return order

