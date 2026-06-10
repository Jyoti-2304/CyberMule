"""Unit tests for ML models"""

import pytest
import numpy as np
import pandas as pd
from src.ml_models import (
    TransactionAnomalyDetector,
    MuleAccountDetector,
    EnsembleAnomalyDetector,
    ModelRegistry
)


class TestTransactionAnomalyDetector:
    """Test transaction anomaly detection model"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample transaction data"""
        return pd.DataFrame({
            'amount': np.random.randn(100),
            'hour': np.random.randint(0, 24, 100),
            'is_weekend': np.random.randint(0, 2, 100)
        })
    
    def test_initialization(self):
        """Test model initialization"""
        model = TransactionAnomalyDetector(contamination=0.1)
        assert model.contamination == 0.1
        assert not model.is_trained
    
    def test_training(self, sample_data):
        """Test model training"""
        model = TransactionAnomalyDetector()
        model.train(sample_data)
        assert model.is_trained
        assert model.feature_names is not None
    
    def test_prediction_before_training(self, sample_data):
        """Test prediction fails before training"""
        model = TransactionAnomalyDetector()
        with pytest.raises(ValueError):
            model.predict(sample_data)
    
    def test_prediction_after_training(self, sample_data):
        """Test prediction after training"""
        model = TransactionAnomalyDetector()
        model.train(sample_data)
        predictions = model.predict(sample_data)
        assert predictions.shape[0] == len(sample_data)
        assert np.all((predictions == 0) | (predictions == 1))


class TestMuleAccountDetector:
    """Test mule account detection model"""
    
    @pytest.fixture
    def sample_training_data(self):
        """Create sample training data"""
        X = pd.DataFrame({
            'transaction_frequency': np.random.rand(100) * 100,
            'unique_counterparties': np.random.rand(100) * 50,
            'small_amount_ratio': np.random.rand(100),
            'transaction_velocity': np.random.rand(100) * 10
        })
        y = np.random.randint(0, 2, 100)
        return X, y
    
    def test_initialization(self):
        """Test model initialization"""
        model = MuleAccountDetector()
        assert not model.is_trained
    
    def test_training_without_labels(self, sample_training_data):
        """Test training fails without labels"""
        X, _ = sample_training_data
        model = MuleAccountDetector()
        with pytest.raises(ValueError):
            model.train(X, None)
    
    def test_training_with_labels(self, sample_training_data):
        """Test successful training"""
        X, y = sample_training_data
        model = MuleAccountDetector()
        model.train(X, y)
        assert model.is_trained
        assert len(model.feature_importance) > 0
    
    def test_prediction_after_training(self, sample_training_data):
        """Test predictions after training"""
        X, y = sample_training_data
        model = MuleAccountDetector()
        model.train(X, y)
        predictions = model.predict(X)
        assert predictions.shape[0] == len(X)


class TestEnsembleAnomalyDetector:
    """Test ensemble anomaly detector"""
    
    def test_ensemble_initialization(self):
        """Test ensemble initialization"""
        ensemble = EnsembleAnomalyDetector()
        assert len(ensemble.models) == 0
    
    def test_add_model_to_ensemble(self):
        """Test adding models to ensemble"""
        ensemble = EnsembleAnomalyDetector()
        model1 = TransactionAnomalyDetector()
        model2 = TransactionAnomalyDetector()
        
        ensemble.add_model('model1', model1, weight=0.6)
        ensemble.add_model('model2', model2, weight=0.4)
        
        assert len(ensemble.models) == 2
        assert ensemble.weights['model1'] == 0.6


class TestModelRegistry:
    """Test model registry"""
    
    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = ModelRegistry()
        assert len(registry.models) == 0
    
    def test_register_model(self):
        """Test registering a model"""
        registry = ModelRegistry()
        model = TransactionAnomalyDetector()
        
        registry.register_model('anomaly_detector', model, {'version': '1.0'})
        
        assert 'anomaly_detector' in registry.models
        assert registry.model_versions['anomaly_detector'] == 1
    
    def test_retrieve_registered_model(self):
        """Test retrieving registered model"""
        registry = ModelRegistry()
        model = TransactionAnomalyDetector()
        registry.register_model('detector', model)
        
        retrieved = registry.get_model('detector')
        assert retrieved == model
    
    def test_list_models(self):
        """Test listing all models"""
        registry = ModelRegistry()
        registry.register_model('model1', TransactionAnomalyDetector())
        registry.register_model('model2', MuleAccountDetector())
        
        models = registry.list_models()
        assert len(models) == 2
        assert 'model1' in models
        assert 'model2' in models
