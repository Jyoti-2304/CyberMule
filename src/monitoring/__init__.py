"""
Monitoring and metrics collection for fraud detection system.
Uses Prometheus for metrics and Sentry for error tracking.
"""

import logging
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from datetime import datetime
import sentry_sdk

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Prometheus metrics for fraud detection"""
    
    def __init__(self, namespace: str = "fraud_detection"):
        self.namespace = namespace
        
        # Counters
        self.transactions_processed = Counter(
            f'{namespace}_transactions_processed_total',
            'Total number of transactions processed',
            ['channel']
        )
        
        self.transactions_flagged = Counter(
            f'{namespace}_transactions_flagged_total',
            'Total number of flagged transactions',
            ['risk_level']
        )
        
        self.mule_accounts_detected = Counter(
            f'{namespace}_mule_accounts_detected_total',
            'Total number of detected mule accounts'
        )
        
        self.fraud_alerts_received = Counter(
            f'{namespace}_fraud_alerts_received_total',
            'Total number of fraud alerts received',
            ['source']
        )
        
        self.processing_errors = Counter(
            f'{namespace}_processing_errors_total',
            'Total number of processing errors',
            ['error_type']
        )
        
        # Histograms
        self.transaction_processing_time = Histogram(
            f'{namespace}_transaction_processing_seconds',
            'Transaction processing time in seconds',
            ['processor_type']
        )
        
        self.fraud_score_distribution = Histogram(
            f'{namespace}_fraud_score_distribution',
            'Distribution of fraud scores',
            buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        self.mule_score_distribution = Histogram(
            f'{namespace}_mule_score_distribution',
            'Distribution of mule account scores',
            buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        # Gauges
        self.active_alerts = Gauge(
            f'{namespace}_active_alerts',
            'Number of active fraud alerts'
        )
        
        self.model_accuracy = Gauge(
            f'{namespace}_model_accuracy',
            'Current model accuracy',
            ['model_name']
        )
        
        self.database_connection_pool = Gauge(
            f'{namespace}_database_connections',
            'Number of active database connections'
        )
    
    def record_transaction_processed(self, channel: str) -> None:
        """Record transaction processed"""
        self.transactions_processed.labels(channel=channel).inc()
    
    def record_transaction_flagged(self, risk_level: str) -> None:
        """Record flagged transaction"""
        self.transactions_flagged.labels(risk_level=risk_level).inc()
    
    def record_mule_account_detected(self) -> None:
        """Record detected mule account"""
        self.mule_accounts_detected.inc()
    
    def record_fraud_alert(self, source: str) -> None:
        """Record received fraud alert"""
        self.fraud_alerts_received.labels(source=source).inc()
    
    def record_processing_error(self, error_type: str) -> None:
        """Record processing error"""
        self.processing_errors.labels(error_type=error_type).inc()
    
    def record_processing_time(self, processor_type: str, duration_seconds: float) -> None:
        """Record processing time"""
        self.transaction_processing_time.labels(processor_type=processor_type).observe(duration_seconds)
    
    def record_fraud_score(self, score: float) -> None:
        """Record fraud score"""
        self.fraud_score_distribution.observe(score)
    
    def record_mule_score(self, score: float) -> None:
        """Record mule score"""
        self.mule_score_distribution.observe(score)
    
    def update_active_alerts(self, count: int) -> None:
        """Update active alerts count"""
        self.active_alerts.set(count)
    
    def update_model_accuracy(self, model_name: str, accuracy: float) -> None:
        """Update model accuracy"""
        self.model_accuracy.labels(model_name=model_name).set(accuracy)
    
    def update_database_connections(self, count: int) -> None:
        """Update database connection count"""
        self.database_connection_pool.set(count)
    
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics in text format"""
        return generate_latest()


class AlertManager:
    """Manage system alerts and notifications"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.active_alerts: Dict[str, Dict] = {}
    
    def create_alert(self, alert_type: str, severity: str, message: str, 
                     details: Dict = None) -> str:
        """Create a new alert"""
        alert_id = f"{alert_type}_{datetime.utcnow().timestamp()}"
        
        alert = {
            'alert_id': alert_id,
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': details or {},
            'created_at': datetime.utcnow().isoformat(),
            'status': 'ACTIVE'
        }
        
        self.active_alerts[alert_id] = alert
        
        logger.warning(f"Alert created: {alert_id} - {message}")
        
        # Send notification if configured
        if self.config.get('send_notifications'):
            self._send_notification(alert)
        
        return alert_id
    
    def resolve_alert(self, alert_id: str) -> None:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]['status'] = 'RESOLVED'
            self.active_alerts[alert_id]['resolved_at'] = datetime.utcnow().isoformat()
            logger.info(f"Alert resolved: {alert_id}")
    
    def get_active_alerts(self) -> Dict[str, Dict]:
        """Get all active alerts"""
        return {k: v for k, v in self.active_alerts.items() if v['status'] == 'ACTIVE'}
    
    def _send_notification(self, alert: Dict) -> None:
        """Send alert notification"""
        # Placeholder for notification logic (email, Slack, etc.)
        logger.info(f"Sending notification for alert: {alert['alert_id']}")


class HealthMonitor:
    """Monitor system health"""
    
    def __init__(self):
        self.health_status = {
            'database': 'unknown',
            'kafka': 'unknown',
            'ml_models': 'unknown',
            'api': 'unknown'
        }
    
    def check_database_health(self, db_manager=None) -> bool:
        """Check database connectivity"""
        try:
            if db_manager:
                session = db_manager.get_session()
                session.execute("SELECT 1")
                session.close()
            self.health_status['database'] = 'healthy'
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            self.health_status['database'] = 'unhealthy'
            return False
    
    def check_kafka_health(self, kafka_config=None) -> bool:
        """Check Kafka connectivity"""
        try:
            # Placeholder for Kafka health check
            self.health_status['kafka'] = 'healthy'
            return True
        except Exception as e:
            logger.error(f"Kafka health check failed: {str(e)}")
            self.health_status['kafka'] = 'unhealthy'
            return False
    
    def check_models_health(self, models=None) -> bool:
        """Check ML models availability"""
        try:
            if models:
                for model_name, model in models.items():
                    if not hasattr(model, 'is_trained') or not model.is_trained:
                        raise ValueError(f"Model {model_name} not trained")
            self.health_status['ml_models'] = 'healthy'
            return True
        except Exception as e:
            logger.error(f"ML models health check failed: {str(e)}")
            self.health_status['ml_models'] = 'unhealthy'
            return False
    
    def get_health_status(self) -> Dict[str, str]:
        """Get overall system health status"""
        return self.health_status
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return all(status == 'healthy' for status in self.health_status.values())


def initialize_sentry(dsn: str, environment: str = 'development') -> None:
    """Initialize Sentry for error tracking"""
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=0.1
    )
    logger.info(f"Sentry initialized for environment: {environment}")


class MonitoringService:
    """Main monitoring service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics = PrometheusMetrics(config.get('namespace', 'fraud_detection'))
        self.alerts = AlertManager(config.get('alerts', {}))
        self.health = HealthMonitor()
        
        # Initialize Sentry if configured
        if config.get('sentry_dsn'):
            initialize_sentry(
                config['sentry_dsn'],
                config.get('environment', 'development')
            )
    
    def get_metrics(self) -> bytes:
        """Get current metrics"""
        return self.metrics.get_metrics()
    
    def create_alert(self, alert_type: str, severity: str, message: str, 
                     details: Dict = None) -> str:
        """Create system alert"""
        return self.alerts.create_alert(alert_type, severity, message, details)
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'health_status': self.health.get_health_status(),
            'is_healthy': self.health.is_healthy(),
            'active_alerts': len(self.alerts.get_active_alerts())
        }
