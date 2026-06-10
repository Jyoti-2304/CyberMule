"""
Database schema and ORM models for fraud detection system.
Supports PostgreSQL for transactional data and MongoDB for alerts/logs.
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


# PostgreSQL Models

class Transaction(Base):
    """Transaction model"""
    __tablename__ = 'transactions'
    
    transaction_id = Column(String(50), primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    sender = Column(String(100), nullable=False, index=True)
    receiver = Column(String(100), nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False)
    channel = Column(String(50))
    timestamp = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default='PENDING')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_sender_timestamp', 'sender', 'timestamp'),
        Index('idx_receiver_timestamp', 'receiver', 'timestamp'),
    )


class FraudScore(Base):
    """Fraud detection score model"""
    __tablename__ = 'fraud_scores'
    
    score_id = Column(String(50), primary_key=True, index=True)
    transaction_id = Column(String(50), nullable=False, index=True)
    fraud_probability = Column(Float, nullable=False)
    is_fraud = Column(Boolean, default=False, index=True)
    risk_level = Column(String(20))
    confidence = Column(Float)
    model_version = Column(String(50))
    flagged_features = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_transaction_fraud', 'transaction_id', 'is_fraud'),
    )


class Account(Base):
    """Account model"""
    __tablename__ = 'accounts'
    
    account_id = Column(String(50), primary_key=True, index=True)
    account_name = Column(String(200))
    account_type = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MuleAccountScore(Base):
    """Mule account detection score model"""
    __tablename__ = 'mule_account_scores'
    
    score_id = Column(String(50), primary_key=True, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    mule_probability = Column(Float, nullable=False)
    is_mule = Column(Boolean, default=False, index=True)
    indicators = Column(JSON)
    model_version = Column(String(50))
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_account_mule', 'account_id', 'is_mule'),
    )


class FraudAlert(Base):
    """Fraud alert model"""
    __tablename__ = 'fraud_alerts'
    
    alert_id = Column(String(50), primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    source = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    affected_entities = Column(JSON)
    details = Column(Text)
    status = Column(String(20), default='OPEN', index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_alert_type_status', 'alert_type', 'status'),
        Index('idx_alert_created', 'created_at'),
    )


class UserAction(Base):
    """User action audit trail"""
    __tablename__ = 'user_actions'
    
    action_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(50), index=True)
    old_value = Column(JSON)
    new_value = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )


class RegulatoryReport(Base):
    """Regulatory report model"""
    __tablename__ = 'regulatory_reports'
    
    report_id = Column(String(50), primary_key=True, index=True)
    report_type = Column(String(50), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    total_transactions = Column(Integer)
    fraudulent_transactions = Column(Integer)
    fraud_rate = Column(Float)
    mule_accounts_detected = Column(Integer)
    alerts_generated = Column(Integer)
    report_data = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)


class NotebookLog(Base):
    """ML model training/evaluation log"""
    __tablename__ = 'notebook_logs'
    
    log_id = Column(String(50), primary_key=True, index=True)
    notebook_name = Column(String(100), nullable=False)
    model_name = Column(String(50), nullable=False)
    experiment_name = Column(String(100))
    training_samples = Column(Integer)
    test_samples = Column(Integer)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_score = Column(Float)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# MongoDB Models (Document schemas)

class MongoDBModels:
    """MongoDB document schemas for alerts and logs"""
    
    @staticmethod
    def fraud_alert_schema():
        """Schema for fraud alerts in MongoDB"""
        return {
            'alert_id': str,
            'alert_type': str,
            'source': str,
            'severity': str,
            'affected_entities': list,
            'details': dict,
            'status': str,
            'created_at': datetime,
            'resolved_at': datetime,
        }
    
    @staticmethod
    def transaction_log_schema():
        """Schema for transaction logs in MongoDB"""
        return {
            'transaction_id': str,
            'fraud_score': float,
            'model_version': str,
            'processing_time_ms': float,
            'timestamp': datetime,
        }
    
    @staticmethod
    def model_performance_log_schema():
        """Schema for model performance logs in MongoDB"""
        return {
            'model_name': str,
            'evaluation_date': datetime,
            'metrics': dict,
            'predictions': dict,
            'performance_summary': str,
        }


class DatabaseManager:
    """Manage database connections and sessions"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self):
        """Initialize database connection"""
        from sqlalchemy import create_engine
        
        logger.info(f"Initializing database: {self.database_url}")
        
        self.engine = create_engine(
            self.database_url,
            pool_size=20,
            max_overflow=40,
            echo=False
        )
        
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        
        logger.info("Database initialized successfully")
    
    def get_session(self):
        """Get a database session"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized")
        
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


def create_database_manager(database_url: str) -> DatabaseManager:
    """Factory function to create database manager"""
    manager = DatabaseManager(database_url)
    manager.initialize()
    return manager
