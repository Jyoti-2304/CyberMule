"""
Data processing pipeline for fraud detection.
Handles data cleaning, transformation, feature engineering, and normalization.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Transaction type enumeration"""
    TRANSFER = "transfer"
    PAYMENT = "payment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    UNKNOWN = "unknown"


class DataProcessor:
    """Main data processing pipeline"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.processed_cache = {}
    
    def clean_transaction_data(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Clean and normalize transaction data"""
        logger.info(f"Cleaning {len(raw_data)} transaction records")
        
        df = pd.DataFrame(raw_data)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['transaction_id'])
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Standardize data types
        df = self._standardize_types(df)
        
        # Remove outliers
        df = self._remove_outliers(df)
        
        logger.info(f"Cleaned data contains {len(df)} records")
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        # For amount fields, fill with 0
        amount_cols = df.columns[df.columns.str.contains('amount', case=False)]
        df[amount_cols] = df[amount_cols].fillna(0)
        
        # For categorical fields, fill with 'UNKNOWN'
        categorical_cols = df.select_dtypes(include=['object']).columns
        df[categorical_cols] = df[categorical_cols].fillna('UNKNOWN')
        
        return df
    
    def _standardize_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize data types"""
        # Convert timestamp columns to datetime
        time_cols = df.columns[df.columns.str.contains('time|date', case=False)]
        for col in time_cols:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                logger.warning(f"Could not convert {col} to datetime")
        
        # Convert amount columns to float
        amount_cols = df.columns[df.columns.str.contains('amount', case=False)]
        for col in amount_cols:
            try:
                df[col] = df[col].astype(float)
            except:
                logger.warning(f"Could not convert {col} to float")
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove statistical outliers"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            # Mark outliers but keep them for now (model will handle)
            df[f'{col}_is_outlier'] = (df[col] < lower_bound) | (df[col] > upper_bound)
        
        return df
    
    def engineer_transaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features from transaction data"""
        logger.info("Engineering transaction features")
        
        # Time-based features
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            df['is_night'] = df['hour'].isin([22, 23, 0, 1, 2, 3, 4, 5]).astype(int)
        
        # Transaction type features
        if 'transaction_type' in df.columns:
            transaction_dummies = pd.get_dummies(df['transaction_type'], prefix='tx_type')
            df = pd.concat([df, transaction_dummies], axis=1)
        
        # Amount-based features
        if 'amount' in df.columns:
            df['amount_log'] = np.log1p(df['amount'])
            df['amount_is_round'] = (df['amount'] % 100 == 0).astype(int)
        
        # Sender/Receiver features
        if 'sender' in df.columns and 'receiver' in df.columns:
            df['same_entity'] = (df['sender'] == df['receiver']).astype(int)
        
        return df
    
    def engineer_alert_features(self, alerts: List[Dict]) -> pd.DataFrame:
        """Engineer features from fraud alerts"""
        logger.info(f"Engineering features for {len(alerts)} alerts")
        
        if not alerts:
            return pd.DataFrame()
        
        df = pd.DataFrame(alerts)
        
        # Alert frequency features
        if 'entity_id' in df.columns:
            df['alert_count_by_entity'] = df.groupby('entity_id')['entity_id'].transform('count')
        
        # Severity features
        if 'severity' in df.columns:
            severity_map = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            df['severity_score'] = df['severity'].map(severity_map)
        
        # Time-based alert features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['alert_hour'] = df['timestamp'].dt.hour
        
        return df
    
    def identify_mule_account_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify potential mule account characteristics"""
        logger.info("Identifying mule account indicators")
        
        # High transaction frequency
        if 'sender' in df.columns:
            df['transactions_as_sender'] = df.groupby('sender')['sender'].transform('count')
        
        if 'receiver' in df.columns:
            df['transactions_as_receiver'] = df.groupby('receiver')['receiver'].transform('count')
        
        # High transaction velocity
        if 'sender' in df.columns and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['transaction_velocity'] = df.groupby('sender')['timestamp'].transform(
                lambda x: (x.max() - x.min()).total_seconds() / max(len(x), 1)
            )
        
        # Multiple counterparties
        if 'sender' in df.columns and 'receiver' in df.columns:
            df['unique_counterparties_as_sender'] = df.groupby('sender')['receiver'].transform('nunique')
            df['unique_counterparties_as_receiver'] = df.groupby('receiver')['sender'].transform('nunique')
        
        # Low value high frequency pattern (typical mule behavior)
        if 'amount' in df.columns:
            df['is_small_amount'] = (df['amount'] < df['amount'].quantile(0.25)).astype(int)
            df['small_amount_frequency'] = df.groupby('sender')['is_small_amount'].transform('sum')
        
        return df
    
    def normalize_features(self, df: pd.DataFrame, scaler_config: Dict = None) -> Tuple[pd.DataFrame, Dict]:
        """Normalize feature values"""
        logger.info("Normalizing features")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        normalization_params = {}
        
        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()
            
            if std > 0:
                df[f'{col}_normalized'] = (df[col] - mean) / std
                normalization_params[col] = {'mean': mean, 'std': std}
            else:
                df[f'{col}_normalized'] = 0
                normalization_params[col] = {'mean': mean, 'std': 1}
        
        return df, normalization_params
    
    def create_training_dataset(self, transactions: List[Dict], labels: List[int]) -> Tuple[pd.DataFrame, List[int]]:
        """Create a training dataset with features and labels"""
        logger.info(f"Creating training dataset with {len(transactions)} samples")
        
        # Process raw data
        df = self.clean_transaction_data(transactions)
        
        # Engineer features
        df = self.engineer_transaction_features(df)
        df = self.identify_mule_account_indicators(df)
        
        # Normalize
        df, norm_params = self.normalize_features(df)
        
        self.processed_cache['normalization_params'] = norm_params
        
        return df, labels
