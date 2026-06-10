"""
ML Models for fraud detection.
Includes transaction anomaly detection and mule account identification models.
"""

import logging
import pickle
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime

logger = logging.getLogger(__name__)


class FraudDetectionModel(ABC):
    """Abstract base class for fraud detection models"""
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: List[int] = None) -> None:
        """Train the model"""
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        pass
    
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities"""
        pass
    
    @abstractmethod
    def save(self, filepath: str) -> None:
        """Save model to disk"""
        pass
    
    @abstractmethod
    def load(self, filepath: str) -> None:
        """Load model from disk"""
        pass


class TransactionAnomalyDetector(FraudDetectionModel):
    """Unsupervised anomaly detection for transaction fraud"""
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X: pd.DataFrame, y: List[int] = None) -> None:
        """Train anomaly detection model"""
        logger.info(f"Training transaction anomaly detector with {len(X)} samples")
        
        self.feature_names = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        logger.info("Transaction anomaly detector training completed")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict anomalies: -1 for anomaly, 1 for normal"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # Convert to binary (0 for normal, 1 for anomaly)
        return (predictions == -1).astype(int)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get anomaly scores"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        scores = -self.model.score_samples(X_scaled)
        
        # Normalize scores to 0-1
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        
        return np.column_stack([1 - scores, scores])
    
    def save(self, filepath: str) -> None:
        """Save model to disk"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'contamination': self.contamination,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.contamination = model_data['contamination']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")


class MuleAccountDetector(FraudDetectionModel):
    """Supervised learning model for mule account identification"""
    
    def __init__(self, random_state: int = 42, n_estimators: int = 100):
        self.random_state = random_state
        self.n_estimators = n_estimators
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=15,
            min_samples_split=10,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        self.feature_importance = {}
    
    def train(self, X: pd.DataFrame, y: List[int]) -> None:
        """Train mule account detection model"""
        if y is None or len(y) == 0:
            raise ValueError("Labels (y) are required for supervised training")
        
        logger.info(f"Training mule account detector with {len(X)} samples")
        
        self.feature_names = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Calculate feature importance
        self.feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        self.is_trained = True
        
        logger.info("Mule account detector training completed")
        logger.info(f"Top features: {sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict mule accounts: 0 for normal, 1 for mule"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get mule account probability"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)
    
    def save(self, filepath: str) -> None:
        """Save model to disk"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.feature_importance = model_data['feature_importance']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")


class EnsembleAnomalyDetector:
    """Ensemble of multiple anomaly detection models"""
    
    def __init__(self, contamination: float = 0.1):
        self.models = {}
        self.contamination = contamination
        self.weights = {}
    
    def add_model(self, name: str, model: FraudDetectionModel, weight: float = 1.0) -> None:
        """Add a model to the ensemble"""
        self.models[name] = model
        self.weights[name] = weight
        logger.info(f"Added model '{name}' with weight {weight}")
    
    def train(self, X: pd.DataFrame, y: List[int] = None) -> None:
        """Train all models in the ensemble"""
        logger.info(f"Training ensemble with {len(self.models)} models")
        
        for name, model in self.models.items():
            logger.info(f"Training model: {name}")
            model.train(X, y)
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """Ensemble prediction using weighted voting"""
        predictions = []
        total_weight = 0
        
        for name, model in self.models.items():
            proba = model.predict_proba(X)
            # Get probability of fraud class
            fraud_proba = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
            weight = self.weights.get(name, 1.0)
            
            predictions.append(fraud_proba * weight)
            total_weight += weight
        
        # Average weighted probabilities
        ensemble_scores = np.mean(predictions, axis=0)
        
        return (ensemble_scores >= threshold).astype(int)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get ensemble fraud probabilities"""
        predictions = []
        total_weight = 0
        
        for name, model in self.models.items():
            proba = model.predict_proba(X)
            fraud_proba = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
            weight = self.weights.get(name, 1.0)
            
            predictions.append(fraud_proba * weight)
            total_weight += weight
        
        ensemble_scores = np.mean(predictions, axis=0)
        return np.column_stack([1 - ensemble_scores, ensemble_scores])


class ModelRegistry:
    """Registry for managing trained models"""
    
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}
        self.model_versions: Dict[str, int] = {}
    
    def register_model(self, name: str, model: FraudDetectionModel, metadata: Dict = None) -> None:
        """Register a trained model"""
        version = self.model_versions.get(name, 0) + 1
        self.model_versions[name] = version
        
        self.models[name] = {
            'model': model,
            'version': version,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        logger.info(f"Registered model '{name}' version {version}")
    
    def get_model(self, name: str) -> FraudDetectionModel:
        """Retrieve a registered model"""
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found in registry")
        
        return self.models[name]['model']
    
    def get_model_info(self, name: str) -> Dict[str, Any]:
        """Get model metadata"""
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found in registry")
        
        return self.models[name]
    
    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.models.keys())
