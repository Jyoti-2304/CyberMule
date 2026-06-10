"""Test configuration and fixtures"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return [
        {
            'transaction_id': 'TXN001',
            'amount': 1000.0,
            'sender': 'ACC001',
            'receiver': 'ACC002',
            'transaction_type': 'transfer',
            'timestamp': '2024-06-01T10:00:00Z',
            'channel': 'online'
        },
        {
            'transaction_id': 'TXN002',
            'amount': 50000.0,
            'sender': 'ACC003',
            'receiver': 'ACC004',
            'transaction_type': 'transfer',
            'timestamp': '2024-06-01T11:00:00Z',
            'channel': 'atm'
        }
    ]


@pytest.fixture
def sample_fraud_labels():
    """Sample fraud labels for supervised learning"""
    return [0, 1]  # 0: legitimate, 1: fraudulent


@pytest.fixture
def mock_kafka_config():
    """Mock Kafka configuration"""
    return {
        'bootstrap_servers': 'localhost:9092',
        'group_id': 'test-group',
        'transaction_topic': 'test_transactions',
        'alert_topic': 'test_alerts'
    }


@pytest.fixture
def mock_database_config():
    """Mock database configuration"""
    return {
        'url': 'postgresql://test:test@localhost/test_db',
        'echo': False
    }


@pytest.fixture
def sample_mule_account_data():
    """Sample data indicating mule account behavior"""
    return pd.DataFrame({
        'account_id': ['ACC001', 'ACC002'],
        'transaction_count': [150, 5],
        'unique_counterparties': [45, 3],
        'avg_transaction_amount': [500, 5000],
        'small_amount_ratio': [0.85, 0.2],
        'transaction_velocity': [5, 1],
        'is_mule': [1, 0]
    })
