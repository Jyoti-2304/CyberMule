"""
Data ingestion module for consuming multiple fraud data sources.
Handles ingestion from:
- Financial transaction feeds
- Fraud monitoring system alerts
- Transaction monitoring system (TMS) alerts
- Government cyber fraud alerts/tickets
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DataSourceConnector(ABC):
    """Abstract base class for data source connectors"""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to data source"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to data source"""
        pass
    
    @abstractmethod
    def fetch_data(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """Fetch data from source"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """Validate data before ingestion"""
        pass


class TransactionFeedConnector(DataSourceConnector):
    """Connector for real-time transaction feeds"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        
    def connect(self) -> None:
        """Connect to transaction feed source"""
        logger.info("Connecting to transaction feed source")
        # Implementation for connecting to transaction data source
        pass
    
    def disconnect(self) -> None:
        """Disconnect from transaction feed source"""
        logger.info("Disconnecting from transaction feed source")
        pass
    
    def fetch_data(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """Fetch transaction data"""
        logger.info(f"Fetching transaction data with filters: {filters}")
        # Implementation for fetching transactions
        return []
    
    def validate_data(self, data: Dict) -> bool:
        """Validate transaction data"""
        required_fields = ['transaction_id', 'amount', 'sender', 'receiver', 'timestamp']
        return all(field in data for field in required_fields)


class FraudMonitoringAlertConnector(DataSourceConnector):
    """Connector for fraud monitoring system alerts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    def connect(self) -> None:
        """Connect to fraud monitoring system"""
        logger.info("Connecting to fraud monitoring system")
        pass
    
    def disconnect(self) -> None:
        """Disconnect from fraud monitoring system"""
        logger.info("Disconnecting from fraud monitoring system")
        pass
    
    def fetch_data(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """Fetch fraud alerts"""
        logger.info("Fetching fraud monitoring alerts")
        return []
    
    def validate_data(self, data: Dict) -> bool:
        """Validate fraud alert data"""
        required_fields = ['alert_id', 'alert_type', 'severity', 'timestamp', 'details']
        return all(field in data for field in required_fields)


class TMSAlertConnector(DataSourceConnector):
    """Connector for Transaction Monitoring System (TMS) alerts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    def connect(self) -> None:
        """Connect to TMS"""
        logger.info("Connecting to TMS system")
        pass
    
    def disconnect(self) -> None:
        """Disconnect from TMS"""
        logger.info("Disconnecting from TMS system")
        pass
    
    def fetch_data(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """Fetch TMS alerts"""
        logger.info("Fetching TMS alerts")
        return []
    
    def validate_data(self, data: Dict) -> bool:
        """Validate TMS alert data"""
        required_fields = ['rule_id', 'entity_id', 'rule_name', 'hit_timestamp']
        return all(field in data for field in required_fields)


class GovernmentFraudAlertConnector(DataSourceConnector):
    """Connector for Government Cyber Fraud alerts/tickets"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    def connect(self) -> None:
        """Connect to government fraud alert system"""
        logger.info("Connecting to government fraud alert system")
        pass
    
    def disconnect(self) -> None:
        """Disconnect from government fraud alert system"""
        logger.info("Disconnecting from government fraud alert system")
        pass
    
    def fetch_data(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """Fetch government fraud alerts"""
        logger.info("Fetching government cyber fraud alerts")
        return []
    
    def validate_data(self, data: Dict) -> bool:
        """Validate government fraud alert data"""
        required_fields = ['ticket_id', 'fraud_type', 'affected_entities', 'report_date']
        return all(field in data for field in required_fields)


class MultiSourceDataIngestor:
    """Orchestrates data ingestion from multiple sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connectors: List[DataSourceConnector] = []
        self.ingestion_log = []
    
    def add_connector(self, connector: DataSourceConnector) -> None:
        """Register a data source connector"""
        self.connectors.append(connector)
        logger.info(f"Added connector: {connector.__class__.__name__}")
    
    def initialize_all(self) -> None:
        """Initialize all connectors"""
        for connector in self.connectors:
            try:
                connector.connect()
                logger.info(f"Successfully initialized {connector.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to initialize {connector.__class__.__name__}: {str(e)}")
    
    def shutdown_all(self) -> None:
        """Shutdown all connectors"""
        for connector in self.connectors:
            try:
                connector.disconnect()
                logger.info(f"Successfully shutdown {connector.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to shutdown {connector.__class__.__name__}: {str(e)}")
    
    def ingest_from_all_sources(self, filters: Dict[str, Any] = None) -> Dict[str, List[Dict]]:
        """Ingest data from all sources"""
        ingested_data = {}
        
        for connector in self.connectors:
            try:
                connector_name = connector.__class__.__name__
                data = connector.fetch_data(filters)
                
                # Validate each record
                valid_data = [record for record in data if connector.validate_data(record)]
                
                ingested_data[connector_name] = valid_data
                
                # Log ingestion metrics
                self.ingestion_log.append({
                    'source': connector_name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'records_fetched': len(data),
                    'records_valid': len(valid_data),
                    'records_invalid': len(data) - len(valid_data)
                })
                
                logger.info(f"Ingested {len(valid_data)} valid records from {connector_name}")
            
            except Exception as e:
                logger.error(f"Error ingesting from {connector.__class__.__name__}: {str(e)}")
                ingested_data[connector.__class__.__name__] = []
        
        return ingested_data


def create_ingestor(config_path: str) -> MultiSourceDataIngestor:
    """Factory function to create configured ingestor"""
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    ingestor = MultiSourceDataIngestor(config)
    
    # Add all connectors
    ingestor.add_connector(TransactionFeedConnector(config.get('transaction_feed', {})))
    ingestor.add_connector(FraudMonitoringAlertConnector(config.get('fraud_monitoring', {})))
    ingestor.add_connector(TMSAlertConnector(config.get('tms', {})))
    ingestor.add_connector(GovernmentFraudAlertConnector(config.get('govt_fraud_alerts', {})))
    
    return ingestor
