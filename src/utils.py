"""Utility functions for fraud detection system"""

import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid


def generate_transaction_id() -> str:
    """Generate a unique transaction ID"""
    return f"TXN_{uuid.uuid4().hex[:12].upper()}"


def generate_alert_id() -> str:
    """Generate a unique alert ID"""
    return f"ALERT_{uuid.uuid4().hex[:12].upper()}"


def generate_job_id() -> str:
    """Generate a unique job ID"""
    return f"JOB_{uuid.uuid4().hex[:12].upper()}"


def hash_account_id(account_id: str, salt: str = "") -> str:
    """Hash account ID for privacy"""
    hash_input = f"{account_id}{salt}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


def verify_signature(data: str, signature: str, secret_key: str) -> bool:
    """Verify HMAC signature"""
    expected_sig = hmac.new(
        secret_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_sig)


def create_signature(data: str, secret_key: str) -> str:
    """Create HMAC signature"""
    return hmac.new(
        secret_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()


def parse_iso_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO 8601 timestamp"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}")


def get_time_window(days: int = 30) -> tuple:
    """Get time window for the last N days"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    return start_time, end_time


def categorize_risk_level(fraud_score: float) -> str:
    """Categorize fraud risk level"""
    if fraud_score >= 0.7:
        return 'CRITICAL'
    elif fraud_score >= 0.5:
        return 'HIGH'
    elif fraud_score >= 0.3:
        return 'MEDIUM'
    elif fraud_score >= 0.1:
        return 'LOW'
    else:
        return 'MINIMAL'


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format amount as currency"""
    return f"{currency} {amount:,.2f}"


def batch_data(data: List[Dict], batch_size: int = 100) -> List[List[Dict]]:
    """Split data into batches"""
    batches = []
    for i in range(0, len(data), batch_size):
        batches.append(data[i:i + batch_size])
    return batches


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def sanitize_log_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict:
    """Sanitize sensitive data for logging"""
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'card_number']
    
    sanitized = data.copy()
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'
    
    return sanitized


def exponential_backoff(attempt: int, base: float = 1.0, max_wait: float = 60.0) -> float:
    """Calculate exponential backoff duration"""
    wait_time = min(base * (2 ** attempt), max_wait)
    return wait_time


def retry_with_backoff(func, max_retries: int = 3, base_wait: float = 1.0):
    """Retry function with exponential backoff"""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = exponential_backoff(attempt, base_wait)
                time.sleep(wait_time)
            else:
                raise


def calculate_metrics(predictions: List[int], actuals: List[int]) -> Dict[str, float]:
    """Calculate performance metrics"""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    
    metrics = {
        'accuracy': accuracy_score(actuals, predictions),
        'precision': precision_score(actuals, predictions, zero_division=0),
        'recall': recall_score(actuals, predictions, zero_division=0),
        'f1_score': f1_score(actuals, predictions, zero_division=0)
    }
    
    # Try to calculate AUC if predictions are probabilities
    try:
        metrics['auc'] = roc_auc_score(actuals, predictions)
    except:
        pass
    
    return metrics
