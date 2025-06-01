import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

def setup_logging():
    # Create logs directory
    LOG_DIR = Path("/app/logs")
    LOG_DIR.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=1024*1024,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Set root logger to WARNING to hide most technical logs
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Configure specific loggers
    loggers_to_silence = [
        'kafka',
        'kafka.conn',
        'kafka.producer',
        'kafka.client',
        'kafka.cluster',
        'kafka.coordinator',
        'kafka.consumer',
        'urllib3',
        'requests',
        'streamlit',
        'uvicorn',
        'fastapi'
    ]
    
    for logger_name in loggers_to_silence:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Configure our application logger
    logger = logging.getLogger('kafka_logger')
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent propagation to root logger
    
    # Add handlers only to our logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logging
logger = setup_logging() 