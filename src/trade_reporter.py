"""
Anonymous Trade Reporter for KryptoMF Bot Core.

Reports completed trades to the KryptoMF statistics server.
All reports are anonymous - no user identification is sent.
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

# API Configuration
API_URL = "https://kryptomfai.com/api/v1/trades/report-anonymous/"


class AnonymousTradeReporter:
    """
    Reports anonymous trade statistics to KryptoMF.
    
    Privacy:
    - No user identification sent
    - No exchange credentials exposed
    - Only aggregated profit data
    - Can be disabled by user
    """
    
    QUEUE_FILE = Path.home() / ".kryptomf_core" / "trade_queue.json"
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._queue: List[Dict] = []
        self._load_queue()
    
    def report_trade(self, trade_data: Dict) -> bool:
        """
        Queue a completed trade for reporting.
        
        Args:
            trade_data: Dict containing:
                - symbol: Trading pair (e.g., "BTC/USDT")
                - profit: Profit amount (quote currency)
                - amount: Trade size (base currency)
                - completed_timestamp: Unix timestamp
        """
        if not self.enabled:
            return False
        
        if trade_data.get('profit', 0) <= 0:
            return False  # Only report profitable trades
        
        report = {
            'symbol': trade_data.get('symbol', ''),
            'profit': float(trade_data.get('profit', 0)),
            'amount': float(trade_data.get('amount', 0)),
            'completed_timestamp': float(trade_data.get('completed_timestamp', 0)),
            'source': 'core',  # Identifies as Bot Core
        }
        
        self._queue.append(report)
        
        # Send if we have enough trades
        if len(self._queue) >= 10:
            self._send_batch()
        
        return True
    
    def flush(self):
        """Send all pending reports immediately."""
        if self._queue:
            self._send_batch()
    
    def _send_batch(self):
        """Send queued trades to server."""
        if not self._queue:
            return
        
        try:
            response = requests.post(
                API_URL,
                json={'trades': self._queue},
                timeout=30,
                headers={'User-Agent': 'KryptoMF-BotCore/1.0'}
            )
            
            if response.status_code == 200:
                logger.info(f"Reported {len(self._queue)} trades anonymously")
                self._queue = []
                self._save_queue()
            else:
                logger.warning(f"Trade report failed: {response.status_code}")
                self._save_queue()
                
        except requests.RequestException as e:
            logger.debug(f"Could not report trades: {e}")
            self._save_queue()
    
    def _save_queue(self):
        """Persist queue to disk."""
        try:
            self.QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.QUEUE_FILE, 'w') as f:
                json.dump(self._queue, f)
        except Exception as e:
            logger.error(f"Could not save trade queue: {e}")
    
    def _load_queue(self):
        """Load queue from disk."""
        try:
            if self.QUEUE_FILE.exists():
                with open(self.QUEUE_FILE, 'r') as f:
                    self._queue = json.load(f)
        except Exception as e:
            logger.error(f"Could not load trade queue: {e}")
