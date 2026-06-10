"""Unit tests for data ingestion module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.data_ingestion import (
    TransactionFeedConnector,
    FraudMonitoringAlertConnector,
    TMSAlertConnector,
    GovernmentFraudAlertConnector,
    MultiSourceDataIngestor
)


class TestTransactionFeedConnector:
    """Test transaction feed connector"""
    
    def test_connector_initialization(self):
        """Test connector can be initialized"""
        config = {'host': 'localhost', 'port': 5432}
        connector = TransactionFeedConnector(config)
        assert connector.config == config
    
    def test_validate_valid_transaction(self):
        """Test validation of valid transaction"""
        connector = TransactionFeedConnector({})
        
        valid_transaction = {
            'transaction_id': 'TXN001',
            'amount': 1000,
            'sender': 'ACC001',
            'receiver': 'ACC002',
            'timestamp': '2024-06-01T10:00:00Z'
        }
        
        assert connector.validate_data(valid_transaction) is True
    
    def test_validate_invalid_transaction(self):
        """Test validation of invalid transaction"""
        connector = TransactionFeedConnector({})
        
        invalid_transaction = {
            'transaction_id': 'TXN001',
            'amount': 1000
            # Missing required fields
        }
        
        assert connector.validate_data(invalid_transaction) is False


class TestFraudMonitoringAlertConnector:
    """Test fraud monitoring alert connector"""
    
    def test_validate_valid_alert(self):
        """Test validation of valid fraud alert"""
        connector = FraudMonitoringAlertConnector({})
        
        valid_alert = {
            'alert_id': 'ALERT001',
            'alert_type': 'unusual_pattern',
            'severity': 'HIGH',
            'timestamp': '2024-06-01T10:00:00Z',
            'details': {'account': 'ACC001'}
        }
        
        assert connector.validate_data(valid_alert) is True


class TestMultiSourceDataIngestor:
    """Test multi-source data ingestor"""
    
    def test_ingestor_initialization(self):
        """Test ingestor initialization"""
        config = {}
        ingestor = MultiSourceDataIngestor(config)
        assert len(ingestor.connectors) == 0
    
    def test_add_connector(self):
        """Test adding connectors"""
        ingestor = MultiSourceDataIngestor({})
        connector = TransactionFeedConnector({})
        
        ingestor.add_connector(connector)
        assert len(ingestor.connectors) == 1
    
    def test_multiple_connectors(self):
        """Test adding multiple connectors"""
        ingestor = MultiSourceDataIngestor({})
        
        ingestor.add_connector(TransactionFeedConnector({}))
        ingestor.add_connector(FraudMonitoringAlertConnector({}))
        ingestor.add_connector(TMSAlertConnector({}))
        ingestor.add_connector(GovernmentFraudAlertConnector({}))
        
        assert len(ingestor.connectors) == 4
