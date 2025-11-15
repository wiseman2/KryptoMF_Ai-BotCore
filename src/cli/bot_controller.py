"""
Bot Controller - Interactive Bot Control for CLI

Provides interactive commands for controlling the bot:
- Pause/Resume
- Status display
- Emergency stop
- Position management

Uses keyboard input for real-time control.
"""

import sys
import threading
import time
from typing import Optional, Callable
from colorama import Fore, Style
from utils.logger import get_logger

logger = get_logger(__name__)

# Platform-specific keyboard input
if sys.platform == 'win32':
    import msvcrt
    
    def get_key_non_blocking() -> Optional[str]:
        """Get keyboard input without blocking (Windows)."""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                return key.decode('utf-8').lower()
            except:
                return None
        return None
else:
    import select
    import tty
    import termios
    
    def get_key_non_blocking() -> Optional[str]:
        """Get keyboard input without blocking (Unix)."""
        if select.select([sys.stdin], [], [], 0)[0]:
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setcbreak(sys.stdin.fileno())
                key = sys.stdin.read(1).lower()
                return key
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return None


class BotController:
    """
    Interactive bot controller for CLI mode.
    
    Provides keyboard commands to control the bot:
    - P: Pause
    - R: Resume
    - S: Show status
    - Q: Quit
    - Ctrl+C: Emergency stop
    """
    
    def __init__(self, bot_instance, status_display):
        """
        Initialize bot controller.
        
        Args:
            bot_instance: BotInstance to control
            status_display: StatusDisplay for output
        """
        self.bot = bot_instance
        self.display = status_display
        self.running = False
        self.input_thread = None
        
        # Command handlers
        self.commands = {
            'p': self._handle_pause,
            'r': self._handle_resume,
            's': self._handle_status,
            'q': self._handle_quit,
            'h': self._handle_help,
            '?': self._handle_help,
        }
    
    def start(self):
        """Start the controller (begins listening for input)."""
        self.running = True
        
        # Start input listener thread
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
        
        logger.info("Bot controller started")
    
    def stop(self):
        """Stop the controller."""
        self.running = False
        
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
        
        logger.info("Bot controller stopped")
    
    def _input_loop(self):
        """
        Main input loop (runs in separate thread).
        Listens for keyboard input and executes commands.
        """
        while self.running:
            try:
                key = get_key_non_blocking()
                
                if key:
                    self._handle_command(key)
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"Error in input loop: {e}")
                time.sleep(1)
    
    def _handle_command(self, key: str):
        """
        Handle keyboard command.
        
        Args:
            key: Key pressed
        """
        handler = self.commands.get(key)
        
        if handler:
            try:
                handler()
            except Exception as e:
                logger.error(f"Error handling command '{key}': {e}")
                self.display.display_error(f"Command failed: {e}")
        else:
            # Unknown command - show help
            if key.isprintable():
                print(f"\n{Fore.YELLOW}Unknown command: '{key}'. Press 'h' for help.{Style.RESET_ALL}")
    
    def _handle_pause(self):
        """Handle pause command."""
        if not self.bot.running:
            self.display.display_warning("Bot is not running")
            return
        
        if self.bot.paused:
            self.display.display_warning("Bot is already paused")
            return
        
        logger.info("Pausing bot...")
        self.bot.pause()
        self.display.display_success("Bot paused")
    
    def _handle_resume(self):
        """Handle resume command."""
        if not self.bot.running:
            self.display.display_warning("Bot is not running")
            return
        
        if not self.bot.paused:
            self.display.display_warning("Bot is not paused")
            return
        
        logger.info("Resuming bot...")
        self.bot.resume()
        self.display.display_success("Bot resumed")
    
    def _handle_status(self):
        """Handle status command (refresh display)."""
        status = self.bot.get_status()
        self.display.display_full_status(status)
    
    def _handle_quit(self):
        """Handle quit command."""
        print(f"\n{Fore.YELLOW}Shutting down bot...{Style.RESET_ALL}")
        self.running = False
        self.bot.stop()
        self.display.display_success("Bot stopped successfully")
        
        # Exit the program
        sys.exit(0)
    
    def _handle_help(self):
        """Handle help command."""
        print(f"\n{Fore.CYAN}═══ AVAILABLE COMMANDS ═══{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}P{Style.RESET_ALL} - Pause bot (stop trading but keep connection)")
        print(f"  {Fore.GREEN}R{Style.RESET_ALL} - Resume bot (continue trading)")
        print(f"  {Fore.GREEN}S{Style.RESET_ALL} - Show full status (refresh display)")
        print(f"  {Fore.GREEN}Q{Style.RESET_ALL} - Quit (stop bot and exit)")
        print(f"  {Fore.GREEN}H{Style.RESET_ALL} or {Fore.GREEN}?{Style.RESET_ALL} - Show this help")
        print(f"  {Fore.RED}Ctrl+C{Style.RESET_ALL} - Emergency stop")
        print()


class StatusUpdateLoop:
    """
    Status update loop for CLI mode.
    
    Periodically updates the status display while the bot is running.
    """
    
    def __init__(self, bot_instance, status_display, update_interval: int = 5):
        """
        Initialize status update loop.
        
        Args:
            bot_instance: BotInstance to monitor
            status_display: StatusDisplay for output
            update_interval: Update interval in seconds (default: 5)
        """
        self.bot = bot_instance
        self.display = status_display
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.full_refresh_count = 0
        self.full_refresh_interval = 12  # Full refresh every 12 updates (1 minute if update_interval=5)
    
    def start(self):
        """Start the status update loop."""
        self.running = True
        
        # Start update thread
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"Status update loop started (interval: {self.update_interval}s)")
    
    def stop(self):
        """Stop the status update loop."""
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        logger.info("Status update loop stopped")
    
    def _update_loop(self):
        """
        Main update loop (runs in separate thread).
        Periodically updates the status display.
        """
        # Initial full display
        status = self.bot.get_status()
        self.display.display_full_status(status)
        
        while self.running:
            try:
                time.sleep(self.update_interval)
                
                if not self.running:
                    break
                
                # Get current status
                status = self.bot.get_status()
                
                # Decide whether to do full refresh or compact update
                self.full_refresh_count += 1
                
                if self.full_refresh_count >= self.full_refresh_interval:
                    # Full refresh
                    self.display.display_full_status(status)
                    self.full_refresh_count = 0
                else:
                    # Compact update
                    self.display.display_compact_status(status)
                
            except Exception as e:
                logger.error(f"Error in status update loop: {e}")
                time.sleep(5)


def run_interactive_mode(bot_instance, status_display):
    """
    Run bot in interactive mode with status display and keyboard controls.

    Args:
        bot_instance: BotInstance to run
        status_display: StatusDisplay for output
    """
    # Create controller and status updater
    controller = BotController(bot_instance, status_display)
    status_updater = StatusUpdateLoop(bot_instance, status_display, update_interval=30)
    
    try:
        # Start controller and status updater
        controller.start()
        status_updater.start()
        
        # Show initial help
        print(f"\n{Fore.CYAN}Press 'h' for help, 'q' to quit{Style.RESET_ALL}\n")
        
        # Keep main thread alive
        while bot_instance.running and controller.running:
            time.sleep(0.5)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Emergency stop requested!{Style.RESET_ALL}")
        logger.warning("Emergency stop via Ctrl+C")
    
    finally:
        # Clean shutdown
        controller.stop()
        status_updater.stop()
        
        if bot_instance.running:
            bot_instance.stop()

