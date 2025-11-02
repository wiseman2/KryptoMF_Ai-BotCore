"""
Backtest Results Display - Format and Display Backtest Results

Provides formatted output of backtest results including:
- Performance summary
- Trade statistics
- Equity curve
- Trade log

Uses colorama for colored terminal output.
"""

from typing import Dict, Any, List
from colorama import Fore, Style
from datetime import datetime


class BacktestResults:
    """
    Format and display backtest results.
    """
    
    @staticmethod
    def display_summary(results: Dict[str, Any]):
        """
        Display backtest summary.
        
        Args:
            results: Results dictionary from BacktestEngine
        """
        print()
        print("=" * 70)
        print(f"{Fore.CYAN}{'BACKTEST RESULTS':^70}{Style.RESET_ALL}")
        print("=" * 70)
        
        # Performance
        print(f"\n{Fore.GREEN}═══ PERFORMANCE ═══{Style.RESET_ALL}")
        
        initial = results['initial_balance']
        final = results['final_equity']
        total_return = results['total_return']
        return_pct = results['total_return_pct']
        
        # Color based on performance
        if return_pct > 0:
            return_color = Fore.GREEN
            return_symbol = "+"
        elif return_pct < 0:
            return_color = Fore.RED
            return_symbol = ""
        else:
            return_color = Fore.YELLOW
            return_symbol = ""
        
        print(f"Initial Balance:  ${initial:,.2f}")
        print(f"Final Equity:     ${final:,.2f}")
        print(f"Total Return:     {return_color}{return_symbol}${total_return:,.2f} ({return_symbol}{return_pct:.2f}%){Style.RESET_ALL}")
        print(f"Max Drawdown:     {Fore.RED}{results['max_drawdown']:.2f}%{Style.RESET_ALL}")
        
        # Trade statistics
        print(f"\n{Fore.GREEN}═══ TRADE STATISTICS ═══{Style.RESET_ALL}")
        
        total_trades = results['total_trades']
        buy_trades = results['buy_trades']
        sell_trades = results['sell_trades']
        winning = results['winning_trades']
        losing = results['losing_trades']
        win_rate = results['win_rate']
        
        # Win rate color
        if win_rate >= 60:
            win_rate_color = Fore.GREEN
        elif win_rate >= 40:
            win_rate_color = Fore.YELLOW
        else:
            win_rate_color = Fore.RED
        
        print(f"Total Trades:     {total_trades}")
        print(f"  Buy Orders:     {Fore.CYAN}{buy_trades}{Style.RESET_ALL}")
        print(f"  Sell Orders:    {Fore.CYAN}{sell_trades}{Style.RESET_ALL}")
        print(f"Winning Trades:   {Fore.GREEN}{winning}{Style.RESET_ALL}")
        print(f"Losing Trades:    {Fore.RED}{losing}{Style.RESET_ALL}")
        print(f"Win Rate:         {win_rate_color}{win_rate:.1f}%{Style.RESET_ALL}")
        
        # Average profit/loss
        avg_win = results['avg_win']
        avg_loss = results['avg_loss']
        
        print(f"\nAverage Win:      {Fore.GREEN}+${avg_win:.2f}{Style.RESET_ALL}")
        print(f"Average Loss:     {Fore.RED}${avg_loss:.2f}{Style.RESET_ALL}")
        
        if avg_loss != 0:
            profit_factor = abs(avg_win / avg_loss) if avg_loss < 0 else 0
            print(f"Profit Factor:    {Fore.CYAN}{profit_factor:.2f}{Style.RESET_ALL}")
        
        print("=" * 70)
    
    @staticmethod
    def display_trade_log(results: Dict[str, Any], max_trades: int = 20):
        """
        Display trade log.
        
        Args:
            results: Results dictionary from BacktestEngine
            max_trades: Maximum number of trades to display
        """
        trades = results['trades']
        
        if not trades:
            print(f"\n{Fore.YELLOW}No trades executed{Style.RESET_ALL}")
            return
        
        print()
        print("=" * 70)
        print(f"{Fore.CYAN}{'TRADE LOG':^70}{Style.RESET_ALL}")
        print("=" * 70)
        
        # Header
        print(f"\n{Fore.YELLOW}{'Time':<20} {'Type':<6} {'Amount':<15} {'Price':<12} {'P&L':<12}{Style.RESET_ALL}")
        print("-" * 70)
        
        # Show last N trades
        display_trades = trades[-max_trades:] if len(trades) > max_trades else trades
        
        for trade in display_trades:
            timestamp = trade.get('timestamp', 'N/A')
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            trade_type = trade['type'].upper()
            amount = trade['amount']
            price = trade['price']
            
            # Type color
            type_color = Fore.GREEN if trade_type == 'BUY' else Fore.RED
            
            # P&L (only for sells)
            if trade_type == 'SELL':
                profit = trade.get('profit', 0)
                if profit > 0:
                    pnl_text = f"{Fore.GREEN}+${profit:.2f}{Style.RESET_ALL}"
                elif profit < 0:
                    pnl_text = f"{Fore.RED}${profit:.2f}{Style.RESET_ALL}"
                else:
                    pnl_text = f"{Fore.YELLOW}$0.00{Style.RESET_ALL}"
            else:
                pnl_text = "-"
            
            print(f"{timestamp:<20} {type_color}{trade_type:<6}{Style.RESET_ALL} "
                  f"{amount:<15.8f} ${price:<11,.2f} {pnl_text}")
        
        if len(trades) > max_trades:
            print(f"\n{Fore.YELLOW}... showing last {max_trades} of {len(trades)} trades{Style.RESET_ALL}")
        
        print("=" * 70)
    
    @staticmethod
    def display_equity_curve(results: Dict[str, Any], points: int = 50):
        """
        Display simple ASCII equity curve.
        
        Args:
            results: Results dictionary from BacktestEngine
            points: Number of points to display
        """
        equity_curve = results['equity_curve']
        
        if not equity_curve:
            return
        
        print()
        print("=" * 70)
        print(f"{Fore.CYAN}{'EQUITY CURVE':^70}{Style.RESET_ALL}")
        print("=" * 70)
        
        # Sample equity curve if too many points
        if len(equity_curve) > points:
            step = len(equity_curve) // points
            sampled = equity_curve[::step]
        else:
            sampled = equity_curve
        
        # Get equity values
        equity_values = [e['equity'] for e in sampled]
        
        # Calculate range
        min_equity = min(equity_values)
        max_equity = max(equity_values)
        equity_range = max_equity - min_equity
        
        if equity_range == 0:
            equity_range = 1  # Avoid division by zero
        
        # Display curve (simple ASCII)
        chart_height = 15
        chart_width = 60
        
        # Normalize values to chart height
        normalized = []
        for value in equity_values:
            norm = int(((value - min_equity) / equity_range) * (chart_height - 1))
            normalized.append(norm)
        
        # Draw chart
        for row in range(chart_height - 1, -1, -1):
            # Y-axis label
            equity_at_row = min_equity + (row / (chart_height - 1)) * equity_range
            print(f"${equity_at_row:>8,.0f} │", end="")
            
            # Plot points
            for col in range(len(normalized)):
                if normalized[col] == row:
                    print(f"{Fore.GREEN}●{Style.RESET_ALL}", end="")
                elif normalized[col] > row:
                    print(f"{Fore.GREEN}│{Style.RESET_ALL}", end="")
                else:
                    print(" ", end="")
            
            print()
        
        # X-axis
        print(" " * 10 + "└" + "─" * len(normalized))
        print(" " * 11 + "Start" + " " * (len(normalized) - 10) + "End")
        
        print("=" * 70)
    
    @staticmethod
    def save_to_file(results: Dict[str, Any], filename: str):
        """
        Save backtest results to file.
        
        Args:
            results: Results dictionary from BacktestEngine
            filename: Output filename
        """
        import json
        
        # Convert results to JSON-serializable format
        output = {
            'summary': {
                'initial_balance': results['initial_balance'],
                'final_equity': results['final_equity'],
                'total_return': results['total_return'],
                'total_return_pct': results['total_return_pct'],
                'max_drawdown': results['max_drawdown'],
                'total_trades': results['total_trades'],
                'win_rate': results['win_rate']
            },
            'trades': results['trades'],
            'equity_curve': results['equity_curve']
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n{Fore.GREEN}✓ Results saved to {filename}{Style.RESET_ALL}")

