"""Bank Fraud Detection Solution Package"""

__version__ = "1.0.0"
__author__ = "Bank Fraud Detection Team"
__email__ = "fraud-detection@bank.com"

# Import main components
from src.api import create_api_server, APIServer
from src.data_ingestion import MultiSourceDataIngestor, create_ingestor
from src.data_processing import DataProcessor
from src.ml_models import (
    TransactionAnomalyDetector,
    MuleAccountDetector,
    ModelRegistry,
    EnsembleAnomalyDetector
)
from src.real_time_processing import RealTimeAnomalyDetectionPipeline
from src.database import create_database_manager
from src.monitoring import MonitoringService
from src.logging_config import configure_logging, get_logger

__all__ = [
    'create_api_server',
    'APIServer',
    'MultiSourceDataIngestor',
    'create_ingestor',
    'DataProcessor',
    'TransactionAnomalyDetector',
    'MuleAccountDetector',
    'ModelRegistry',
    'EnsembleAnomalyDetector',
    'RealTimeAnomalyDetectionPipeline',
    'create_database_manager',
    'MonitoringService',
    'configure_logging',
    'get_logger'
]
