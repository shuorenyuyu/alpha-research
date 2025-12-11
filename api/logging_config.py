"""
Centralized logging configuration for Alpha Research API

Provides:
- File-based logging with rotation
- Structured log formatting
- Different log levels for different components
- Console and file handlers
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
API_LOG_FILE = LOGS_DIR / "api.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"
RESEARCH_LOG_FILE = LOGS_DIR / "research.log"

# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

def setup_logger(
    name: str,
    log_file: Path = API_LOG_FILE,
    level: int = logging.INFO,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup a logger with file and console handlers
    
    Args:
        name: Logger name (usually module name)
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to output to console as well
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with colors
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

def setup_error_logger() -> logging.Logger:
    """Setup dedicated error logger for critical issues"""
    error_logger = logging.getLogger("alpha_research.errors")
    error_logger.setLevel(logging.ERROR)
    
    if error_logger.handlers:
        return error_logger
    
    # Error file handler - only logs ERROR and CRITICAL
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(pathname)s:%(lineno)d\n"
        "Message: %(message)s\n"
        "%(exc_info)s\n",
        DATE_FORMAT
    )
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    
    return error_logger

def setup_research_logger() -> logging.Logger:
    """Setup dedicated logger for research paper operations"""
    return setup_logger(
        "alpha_research.research",
        log_file=RESEARCH_LOG_FILE,
        level=logging.DEBUG,  # More detailed logging for research operations
        console_output=True
    )

def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with standard configuration
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Starting process...")
    """
    return setup_logger(name)

# Initialize default loggers on import
api_logger = setup_logger("alpha_research.api", level=logging.INFO)
error_logger = setup_error_logger()
research_logger = setup_research_logger()

# Log startup
api_logger.info("=" * 80)
api_logger.info(f"Alpha Research API logging initialized - {datetime.now()}")
api_logger.info(f"Logs directory: {LOGS_DIR}")
api_logger.info("=" * 80)
