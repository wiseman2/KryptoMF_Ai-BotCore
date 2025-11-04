"""
Historical Data Fetcher - Download and Cache Historical Market Data

Fetches OHLCV (Open, High, Low, Close, Volume) data from exchanges
and caches it locally for backtesting.

Features:
- Automatic data fetching from exchanges via ccxt
- Local caching to avoid re-downloading
- Multiple timeframe support (1m, 5m, 15m, 1h, 4h, 1d)
- Data size estimation
- Progress tracking for large downloads
"""

import os
import pandas as pd
import ccxt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from colorama import Fore, Style
from utils.logger import get_logger

logger = get_logger(__name__)


class HistoricalDataFetcher:
    """
    Fetch and cache historical market data from exchanges.
    """
    
    # Timeframe configurations
    TIMEFRAMES = {
        '1m': {'seconds': 60, 'name': '1 minute'},
        '5m': {'seconds': 300, 'name': '5 minutes'},
        '15m': {'seconds': 900, 'name': '15 minutes'},
        '1h': {'seconds': 3600, 'name': '1 hour'},
        '4h': {'seconds': 14400, 'name': '4 hours'},
        '1d': {'seconds': 86400, 'name': '1 day'}
    }
    
    # Approximate bytes per candle (timestamp + OHLCV = ~100 bytes in CSV)
    BYTES_PER_CANDLE = 100
    
    def __init__(self, exchange_id: str, cache_dir: str = 'data/historical'):
        """
        Initialize historical data fetcher.
        
        Args:
            exchange_id: Exchange ID (e.g., 'binance', 'coinbasepro')
            cache_dir: Directory to cache downloaded data
        """
        self.exchange_id = exchange_id
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            logger.info(f"Initialized {exchange_id} for historical data fetching")
        except Exception as e:
            logger.error(f"Failed to initialize exchange {exchange_id}: {e}")
            raise
    
    @staticmethod
    def estimate_data_size(timeframe: str, days: int) -> Tuple[int, float]:
        """
        Estimate the number of candles and data size.

        Args:
            timeframe: Timeframe (e.g., '1h', '1d')
            days: Number of days

        Returns:
            Tuple of (num_candles, size_mb)
        """
        if timeframe not in HistoricalDataFetcher.TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        seconds_per_candle = HistoricalDataFetcher.TIMEFRAMES[timeframe]['seconds']
        total_seconds = days * 86400
        num_candles = total_seconds // seconds_per_candle

        size_bytes = num_candles * HistoricalDataFetcher.BYTES_PER_CANDLE
        size_mb = size_bytes / (1024 * 1024)

        return num_candles, size_mb
    
    def get_cache_filename(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> Path:
        """
        Get cache filename for given parameters.
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USD')
            timeframe: Timeframe (e.g., '1h')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Path to cache file
        """
        # Sanitize symbol for filename
        safe_symbol = symbol.replace('/', '-')
        filename = f"{self.exchange_id}_{safe_symbol}_{timeframe}_{start_date}_{end_date}.csv"
        return self.cache_dir / filename
    
    def load_from_cache(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Load data from cache if available.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame if cached, None otherwise
        """
        cache_file = self.get_cache_filename(symbol, timeframe, start_date, end_date)
        
        if cache_file.exists():
            logger.info(f"Loading cached data from {cache_file}")
            try:
                df = pd.read_csv(cache_file)
                logger.info(f"Loaded {len(df)} candles from cache")
                return df
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                return None
        
        return None
    
    def save_to_cache(self, df: pd.DataFrame, symbol: str, timeframe: str, start_date: str, end_date: str):
        """
        Save data to cache.
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            timeframe: Timeframe
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        cache_file = self.get_cache_filename(symbol, timeframe, start_date, end_date)
        
        try:
            df.to_csv(cache_file, index=False)
            logger.info(f"Saved {len(df)} candles to cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, start_date: str, end_date: str, 
                    use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch OHLCV data from exchange.
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USD')
            timeframe: Timeframe (e.g., '1h', '1d')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            use_cache: Whether to use cached data if available
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        # Check cache first
        if use_cache:
            cached_data = self.load_from_cache(symbol, timeframe, start_date, end_date)
            if cached_data is not None:
                return cached_data
        
        logger.info(f"Fetching {symbol} {timeframe} data from {start_date} to {end_date}")
        
        # Convert dates to timestamps
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
        
        # Fetch data in chunks (exchanges have limits)
        all_candles = []
        current_ts = start_ts
        
        # Calculate total expected candles for progress
        days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
        expected_candles, _ = self.estimate_data_size(timeframe, days)
        
        print(f"\n{Fore.CYAN}Downloading historical data...{Style.RESET_ALL}")
        
        while current_ts < end_ts:
            try:
                # Fetch batch (most exchanges limit to 500-1000 candles per request)
                candles = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=current_ts,
                    limit=1000
                )
                
                if not candles:
                    break
                
                # Filter candles within date range
                filtered_candles = [c for c in candles if c[0] <= end_ts]
                all_candles.extend(filtered_candles)
                
                # Update progress
                progress = (len(all_candles) / expected_candles * 100) if expected_candles > 0 else 0
                print(f"\r{Fore.CYAN}Progress: {len(all_candles):,} / ~{int(expected_candles):,} candles ({progress:.1f}%){Style.RESET_ALL}", end='')
                
                # Move to next batch
                current_ts = candles[-1][0] + 1
                
                # If we got fewer candles than requested, we've reached the end
                if len(candles) < 1000:
                    break
                
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                if all_candles:
                    logger.warning("Returning partial data")
                    break
                else:
                    raise
        
        print()  # New line after progress
        
        if not all_candles:
            raise ValueError(f"No data available for {symbol} on {self.exchange_id}")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert timestamp from milliseconds to seconds
        df['timestamp'] = df['timestamp'] // 1000
        
        logger.info(f"Fetched {len(df)} candles")
        
        # Save to cache
        if use_cache:
            self.save_to_cache(df, symbol, timeframe, start_date, end_date)
        
        return df
    
    @staticmethod
    def interactive_setup() -> Dict[str, Any]:
        """
        Interactive setup for backtest data parameters.
        
        Returns:
            Dictionary with symbol, timeframe, start_date, end_date
        """
        print()
        print("=" * 70)
        print(f"{Fore.CYAN}{'BACKTEST DATA SETUP':^70}{Style.RESET_ALL}")
        print("=" * 70)
        
        # Symbol
        print(f"\n{Fore.GREEN}Step 1: Select Trading Pair{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Examples: BTC/USD, ETH/USD, BTC/USDT, ETH/BTC{Style.RESET_ALL}")
        symbol = input(f"{Fore.CYAN}Enter trading pair (default: BTC/USDT):{Style.RESET_ALL} ").strip().upper() or 'BTC/USDT'
        
        # Timeframe
        print(f"\n{Fore.GREEN}Step 2: Select Timeframe{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available timeframes:{Style.RESET_ALL}")
        for tf, info in HistoricalDataFetcher.TIMEFRAMES.items():
            print(f"  {Fore.CYAN}{tf:<6}{Style.RESET_ALL} - {info['name']}")
        
        timeframe = input(f"{Fore.CYAN}Enter timeframe (default: 1h):{Style.RESET_ALL} ").strip().lower() or '1h'
        
        if timeframe not in HistoricalDataFetcher.TIMEFRAMES:
            print(f"{Fore.RED}Invalid timeframe. Using 1h{Style.RESET_ALL}")
            timeframe = '1h'
        
        # Date range
        print(f"\n{Fore.GREEN}Step 3: Select Date Range{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Quick options:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}1{Style.RESET_ALL} - Last 1 month")
        print(f"  {Fore.CYAN}2{Style.RESET_ALL} - Last 3 months")
        print(f"  {Fore.CYAN}3{Style.RESET_ALL} - Last 6 months")
        print(f"  {Fore.CYAN}4{Style.RESET_ALL} - Last 1 year")
        print(f"  {Fore.CYAN}5{Style.RESET_ALL} - Custom date range")
        
        choice = input(f"{Fore.CYAN}Select option (1-5):{Style.RESET_ALL} ").strip()
        
        end_date = datetime.now()
        
        if choice == '1':
            start_date = end_date - timedelta(days=30)
            days = 30
        elif choice == '2':
            start_date = end_date - timedelta(days=90)
            days = 90
        elif choice == '3':
            start_date = end_date - timedelta(days=180)
            days = 180
        elif choice == '4':
            start_date = end_date - timedelta(days=365)
            days = 365
        elif choice == '5':
            start_str = input(f"{Fore.CYAN}Enter start date (YYYY-MM-DD):{Style.RESET_ALL} ").strip()
            end_str = input(f"{Fore.CYAN}Enter end date (YYYY-MM-DD, or press Enter for today):{Style.RESET_ALL} ").strip()
            
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_str, '%Y-%m-%d') if end_str else datetime.now()
            days = (end_date - start_date).days
        else:
            print(f"{Fore.RED}Invalid choice. Using last 1 month{Style.RESET_ALL}")
            start_date = end_date - timedelta(days=30)
            days = 30
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Estimate data size
        num_candles, size_mb = HistoricalDataFetcher.estimate_data_size(timeframe, days)
        
        print(f"\n{Fore.GREEN}═══ DATA ESTIMATE ═══{Style.RESET_ALL}")
        print(f"Symbol:           {Fore.CYAN}{symbol}{Style.RESET_ALL}")
        print(f"Timeframe:        {Fore.CYAN}{timeframe} ({HistoricalDataFetcher.TIMEFRAMES[timeframe]['name']}){Style.RESET_ALL}")
        print(f"Date Range:       {Fore.CYAN}{start_date_str} to {end_date_str}{Style.RESET_ALL}")
        print(f"Duration:         {Fore.CYAN}{days} days{Style.RESET_ALL}")
        print(f"Expected Candles: {Fore.CYAN}~{num_candles:,}{Style.RESET_ALL}")
        print(f"Estimated Size:   {Fore.CYAN}~{size_mb:.2f} MB{Style.RESET_ALL}")
        
        # Confirm
        confirm = input(f"\n{Fore.YELLOW}Proceed with download? (y/n):{Style.RESET_ALL} ").strip().lower()
        
        if confirm != 'y':
            print(f"{Fore.RED}Cancelled{Style.RESET_ALL}")
            return None
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'start_date': start_date_str,
            'end_date': end_date_str
        }

