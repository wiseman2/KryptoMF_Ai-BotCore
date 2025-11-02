"""
Status Display - Real-time Bot Status for CLI

Displays:
- Current bot status (running, paused, stopped)
- Active positions and P&L
- Recent trades
- Performance metrics
- Market data

Uses colorama for colored terminal output.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class StatusDisplay:
    """
    Real-time status display for CLI mode.
    
    Shows bot status, positions, trades, and performance in a
    user-friendly format with colors.
    """
    
    def __init__(self):
        self.last_update = None
        self.terminal_width = self._get_terminal_width()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width for formatting."""
        try:
            return os.get_terminal_size().columns
        except:
            return 80  # Default width
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self, bot_name: str, exchange: str, symbol: str):
        """
        Display header with bot information.
        
        Args:
            bot_name: Bot name
            exchange: Exchange name
            symbol: Trading symbol
        """
        width = self.terminal_width
        
        print("=" * width)
        print(f"{Fore.CYAN}{bot_name:^{width}}{Style.RESET_ALL}")
        print("=" * width)
        print(f"Exchange: {Fore.GREEN}{exchange}{Style.RESET_ALL}  |  "
              f"Symbol: {Fore.GREEN}{symbol}{Style.RESET_ALL}  |  "
              f"Updated: {Fore.YELLOW}{datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
        print("-" * width)
    
    def display_status(self, status: Dict[str, Any]):
        """
        Display bot status.
        
        Args:
            status: Status dictionary from BotInstance.get_status()
        """
        running = status.get('running', False)
        paused = status.get('paused', False)
        paper_trading = status.get('paper_trading', False)
        
        # Status indicator
        if running and not paused:
            status_text = f"{Fore.GREEN}● RUNNING{Style.RESET_ALL}"
        elif paused:
            status_text = f"{Fore.YELLOW}⏸ PAUSED{Style.RESET_ALL}"
        else:
            status_text = f"{Fore.RED}● STOPPED{Style.RESET_ALL}"
        
        # Trading mode
        if paper_trading:
            mode_text = f"{Fore.YELLOW}📄 PAPER TRADING{Style.RESET_ALL}"
        else:
            mode_text = f"{Fore.RED}💰 LIVE TRADING{Style.RESET_ALL}"
        
        print(f"\nStatus: {status_text}  |  Mode: {mode_text}")
        
        # Uptime
        if status.get('started_at'):
            started = datetime.fromisoformat(status['started_at'])
            uptime = datetime.now() - started
            print(f"Uptime: {Fore.CYAN}{self._format_timedelta(uptime)}{Style.RESET_ALL}")
    
    def display_positions(self, stats: Dict[str, Any]):
        """
        Display current positions and P&L.
        
        Args:
            stats: Statistics dictionary from BotInstance
        """
        print(f"\n{Fore.CYAN}═══ POSITIONS ═══{Style.RESET_ALL}")
        
        current_position = stats.get('current_position', 0.0)
        last_price = stats.get('last_price', 0.0)
        total_profit = stats.get('total_profit', 0.0)
        
        # Position
        if current_position > 0:
            position_color = Fore.GREEN
            position_text = f"+{current_position:.8f}"
        elif current_position < 0:
            position_color = Fore.RED
            position_text = f"{current_position:.8f}"
        else:
            position_color = Fore.YELLOW
            position_text = "0.00000000"
        
        print(f"Current Position: {position_color}{position_text}{Style.RESET_ALL}")
        print(f"Last Price: {Fore.CYAN}${last_price:,.2f}{Style.RESET_ALL}")
        
        # P&L
        if total_profit > 0:
            profit_color = Fore.GREEN
            profit_symbol = "+"
        elif total_profit < 0:
            profit_color = Fore.RED
            profit_symbol = ""
        else:
            profit_color = Fore.YELLOW
            profit_symbol = ""
        
        print(f"Total P&L: {profit_color}{profit_symbol}${total_profit:,.2f}{Style.RESET_ALL}")
    
    def display_trades(self, stats: Dict[str, Any]):
        """
        Display trade statistics.
        
        Args:
            stats: Statistics dictionary from BotInstance
        """
        print(f"\n{Fore.CYAN}═══ TRADES ═══{Style.RESET_ALL}")
        
        total_trades = stats.get('total_trades', 0)
        winning_trades = stats.get('winning_trades', 0)
        losing_trades = stats.get('losing_trades', 0)
        
        # Win rate
        if total_trades > 0:
            win_rate = (winning_trades / total_trades) * 100
            if win_rate >= 60:
                win_rate_color = Fore.GREEN
            elif win_rate >= 40:
                win_rate_color = Fore.YELLOW
            else:
                win_rate_color = Fore.RED
        else:
            win_rate = 0
            win_rate_color = Fore.YELLOW
        
        print(f"Total Trades: {Fore.CYAN}{total_trades}{Style.RESET_ALL}")
        print(f"Winning: {Fore.GREEN}{winning_trades}{Style.RESET_ALL}  |  "
              f"Losing: {Fore.RED}{losing_trades}{Style.RESET_ALL}")
        print(f"Win Rate: {win_rate_color}{win_rate:.1f}%{Style.RESET_ALL}")
    
    def display_controls(self):
        """Display available keyboard controls."""
        width = self.terminal_width
        
        print(f"\n{'-' * width}")
        print(f"{Fore.YELLOW}Controls:{Style.RESET_ALL} "
              f"[P]ause  [R]esume  [S]tatus  [Q]uit  [Ctrl+C] Emergency Stop")
        print("=" * width)
    
    def display_full_status(self, bot_status: Dict[str, Any]):
        """
        Display complete status screen.
        
        Args:
            bot_status: Complete status from BotInstance.get_status()
        """
        self.clear_screen()
        
        # Header
        self.display_header(
            bot_status.get('name', 'KryptoMF Bot'),
            bot_status.get('exchange', 'Unknown'),
            bot_status.get('symbol', 'Unknown')
        )
        
        # Status
        self.display_status(bot_status)
        
        # Positions
        stats = bot_status.get('stats', {})
        self.display_positions(stats)
        
        # Trades
        self.display_trades(stats)
        
        # Controls
        self.display_controls()
        
        self.last_update = datetime.now()
    
    def display_compact_status(self, bot_status: Dict[str, Any]):
        """
        Display compact one-line status (for updates without clearing screen).
        
        Args:
            bot_status: Status from BotInstance.get_status()
        """
        stats = bot_status.get('stats', {})
        
        # Status indicator
        if bot_status.get('running') and not bot_status.get('paused'):
            status_icon = f"{Fore.GREEN}●{Style.RESET_ALL}"
        elif bot_status.get('paused'):
            status_icon = f"{Fore.YELLOW}⏸{Style.RESET_ALL}"
        else:
            status_icon = f"{Fore.RED}●{Style.RESET_ALL}"
        
        # Build status line
        last_price = stats.get('last_price', 0)
        total_profit = stats.get('total_profit', 0)
        total_trades = stats.get('total_trades', 0)
        
        profit_color = Fore.GREEN if total_profit > 0 else Fore.RED if total_profit < 0 else Fore.YELLOW
        
        status_line = (
            f"{status_icon} "
            f"Price: {Fore.CYAN}${last_price:,.2f}{Style.RESET_ALL} | "
            f"P&L: {profit_color}${total_profit:,.2f}{Style.RESET_ALL} | "
            f"Trades: {Fore.CYAN}{total_trades}{Style.RESET_ALL} | "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )
        
        print(status_line)
    
    def display_error(self, error_msg: str):
        """
        Display error message.
        
        Args:
            error_msg: Error message to display
        """
        print(f"\n{Fore.RED}❌ ERROR: {error_msg}{Style.RESET_ALL}")
    
    def display_success(self, success_msg: str):
        """
        Display success message.
        
        Args:
            success_msg: Success message to display
        """
        print(f"\n{Fore.GREEN}✓ {success_msg}{Style.RESET_ALL}")
    
    def display_warning(self, warning_msg: str):
        """
        Display warning message.
        
        Args:
            warning_msg: Warning message to display
        """
        print(f"\n{Fore.YELLOW}⚠️  {warning_msg}{Style.RESET_ALL}")
    
    def _format_timedelta(self, td: timedelta) -> str:
        """
        Format timedelta for display.
        
        Args:
            td: Timedelta to format
            
        Returns:
            Formatted string (e.g., "2h 15m 30s")
        """
        total_seconds = int(td.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

