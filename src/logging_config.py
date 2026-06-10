"""Logging configuration for fraud detection system"""

import logging
import logging.config
import json
from pathlib import Path

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/fraud_detection.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/fraud_detection_errors.log',
            'maxBytes': 10485760,
            'backupCount': 10
        }
    },
    'loggers': {
        'src': {
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'error_file'],
            'propagate': False
        },
        'src.api': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'src.ml_models': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'src.real_time_processing': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'sqlalchemy.engine': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}


def configure_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(LOG_CONFIG)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
