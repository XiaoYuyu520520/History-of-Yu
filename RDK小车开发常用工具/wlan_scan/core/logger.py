"""Logger module for consistent logging across the application."""

import logging
import sys
from typing import Optional

try:
    from colorama import init, Fore, Style
    COLORAMA_AVAILABLE = True
    init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False
    Fore = None
    Style = None


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for terminal output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN if COLORAMA_AVAILABLE else '',
        'INFO': Fore.GREEN if COLORAMA_AVAILABLE else '',
        'WARNING': Fore.YELLOW if COLORAMA_AVAILABLE else '',
        'ERROR': Fore.RED if COLORAMA_AVAILABLE else '',
        'CRITICAL': Fore.RED + Style.BRIGHT if COLORAMA_AVAILABLE else '',
    }
    RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else ''
    
    def format(self, record):
        if COLORAMA_AVAILABLE:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str = 'wlan_scan', level: int = logging.INFO, 
                 use_colors: bool = True) -> logging.Logger:
    """Setup and return a configured logger.
    
    Args:
        name: Logger name
        level: Logging level
        use_colors: Whether to use colored output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    if use_colors and COLORAMA_AVAILABLE:
        formatter = ColoredFormatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a logger.
    
    Args:
        name: Logger name, defaults to 'wlan_scan'
        
    Returns:
        Logger instance
    """
    if name is None:
        name = 'wlan_scan'
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
