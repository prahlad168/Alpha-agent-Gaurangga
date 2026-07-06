"""
GAURANGA Logger
Simple logging utility
"""

import os
import sys
from datetime import datetime
from typing import Optional

class Logger:
    """Simple logger for GAURANGA"""
    
    def __init__(self, name: str = "GAURANGA", log_file: str = None):
        self.name = name
        self.log_file = log_file or f"./data/gauranga_{datetime.now().strftime('%Y%m%d')}.log"
        self._ensure_log_dir()
    
    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists"""
        os.makedirs(os.path.dirname(self.log_file) or ".", exist_ok=True)
    
    def _log(self, level: str, message: str, *args) -> None:
        """Internal log method"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = message % args if args else message
        line = f"[{timestamp}] [{self.name}] [{level}] {formatted}"
        
        # Print to console
        print(line)
        
        # Write to file
        try:
            with open(self.log_file, 'a') as f:
                f.write(line + "\n")
        except:
            pass
    
    def debug(self, message: str, *args) -> None:
        self._log("DEBUG", message, *args)
    
    def info(self, message: str, *args) -> None:
        self._log("INFO", message, *args)
    
    def warning(self, message: str, *args) -> None:
        self._log("WARNING", message, *args)
    
    def error(self, message: str, *args) -> None:
        self._log("ERROR", message, *args)
    
    def critical(self, message: str, *args) -> None:
        self._log("CRITICAL", message, *args)