"""
Real-time stream processing using Kafka for fraud detection.
Processes incoming transactions and alerts in real-time.
"""

import logging
import json
from typing import Dict, Any, Callable, List
from datetime import datetime
from abc import ABC, abstractmethod
from confluent_kafka import Consumer, Producer, KafkaError
import time

logger = logging.getLogger(__name__)


class StreamProcessor(ABC):
    """Abstract base class for stream processing"""
    
    @abstractmethod
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single message"""
        pass


class TransactionStreamProcessor(StreamProcessor):
    """Process transaction stream for fraud detection"""
    
    def __init__(self, ml_model, config: Dict[str, Any] = None):
        self.ml_model = ml_model
        self.config = config or {}
        self.fraud_threshold = config.get('fraud_threshold', 0.5)
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction and return fraud score"""
        try:
            transaction_id = message.get('transaction_id')
            
            # Extract features from transaction
            features = self._extract_features(message)
            
            # Get fraud probability from model
            fraud_proba = self.ml_model.predict_proba(features)
            fraud_score = fraud_proba[0][1] if fraud_proba.shape[1] > 1 else fraud_proba[0]
            
            # Determine if fraudulent
            is_fraud = fraud_score >= self.fraud_threshold
            
            result = {
                'transaction_id': transaction_id,
                'is_fraud': bool(is_fraud),
                'fraud_score': float(fraud_score),
                'threshold': self.fraud_threshold,
                'processed_at': datetime.utcnow().isoformat(),
                'action': 'block' if is_fraud else 'allow'
            }
            
            if is_fraud:
                logger.warning(f"Fraudulent transaction detected: {transaction_id}, Score: {fraud_score:.3f}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")
            return {
                'transaction_id': message.get('transaction_id'),
                'is_fraud': None,
                'error': str(e),
                'action': 'review'
            }
    
    def _extract_features(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from transaction"""
        import pandas as pd
        
        # Build feature row
        features = pd.DataFrame([{
            'amount': transaction.get('amount', 0),
            'sender': transaction.get('sender'),
            'receiver': transaction.get('receiver'),
            'transaction_type': transaction.get('type', 'UNKNOWN'),
            'timestamp': transaction.get('timestamp'),
        }])
        
        return features


class AlertStreamProcessor(StreamProcessor):
    """Process fraud alert stream"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process fraud alert"""
        try:
            alert_id = message.get('alert_id')
            alert_type = message.get('alert_type')
            
            # Enrich alert with metadata
            enriched_alert = {
                'alert_id': alert_id,
                'alert_type': alert_type,
                'source': message.get('source', 'UNKNOWN'),
                'severity': message.get('severity', 'MEDIUM'),
                'affected_entities': message.get('affected_entities', []),
                'received_at': datetime.utcnow().isoformat(),
                'status': 'RECEIVED'
            }
            
            logger.info(f"Alert processed: {alert_id} - Type: {alert_type}")
            
            return enriched_alert
        
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
            return {
                'alert_id': message.get('alert_id'),
                'error': str(e),
                'status': 'ERROR'
            }


class KafkaStreamConsumer:
    """Kafka consumer for fraud detection stream"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.consumer = None
        self.processors: Dict[str, StreamProcessor] = {}
        self.message_handlers: Dict[str, Callable] = {}
    
    def connect(self) -> None:
        """Connect to Kafka broker"""
        logger.info(f"Connecting to Kafka broker: {self.config['bootstrap_servers']}")
        
        consumer_config = {
            'bootstrap.servers': self.config['bootstrap_servers'],
            'group.id': self.config.get('group_id', 'fraud-detection'),
            'auto.offset.reset': 'earliest'
        }
        
        self.consumer = Consumer(consumer_config)
        logger.info("Connected to Kafka broker")
    
    def disconnect(self) -> None:
        """Disconnect from Kafka broker"""
        if self.consumer:
            self.consumer.close()
            logger.info("Disconnected from Kafka broker")
    
    def register_processor(self, topic: str, processor: StreamProcessor) -> None:
        """Register a stream processor for a topic"""
        self.processors[topic] = processor
        logger.info(f"Registered processor for topic: {topic}")
    
    def register_handler(self, result_topic: str, handler: Callable) -> None:
        """Register a handler to process results"""
        self.message_handlers[result_topic] = handler
        logger.info(f"Registered handler for result topic: {result_topic}")
    
    def start_consuming(self, topics: List[str], timeout: int = 1) -> None:
        """Start consuming messages from topics"""
        logger.info(f"Starting to consume from topics: {topics}")
        
        self.consumer.subscribe(topics)
        
        try:
            while True:
                message = self.consumer.poll(timeout)
                
                if message is None:
                    continue
                
                if message.error():
                    logger.error(f"Consumer error: {message.error()}")
                    continue
                
                # Process message
                topic = message.topic()
                payload = json.loads(message.value().decode('utf-8'))
                
                if topic in self.processors:
                    processor = self.processors[topic]
                    result = processor.process(payload)
                    
                    # Handle result
                    if topic in self.message_handlers:
                        handler = self.message_handlers[topic]
                        handler(result)
        
        except KeyboardInterrupt:
            logger.info("Stopping consumer")
        
        finally:
            self.disconnect()


class KafkaStreamProducer:
    """Kafka producer for sending fraud detection results"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.producer = None
    
    def connect(self) -> None:
        """Connect to Kafka broker"""
        logger.info(f"Connecting producer to Kafka broker: {self.config['bootstrap_servers']}")
        
        producer_config = {
            'bootstrap.servers': self.config['bootstrap_servers']
        }
        
        self.producer = Producer(producer_config)
        logger.info("Producer connected to Kafka broker")
    
    def disconnect(self) -> None:
        """Disconnect from Kafka broker"""
        if self.producer:
            self.producer.flush()
            logger.info("Producer disconnected from Kafka broker")
    
    def send_result(self, topic: str, message: Dict[str, Any]) -> None:
        """Send fraud detection result"""
        try:
            payload = json.dumps(message).encode('utf-8')
            self.producer.produce(topic, value=payload)
            logger.debug(f"Sent result to topic {topic}")
        
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {str(e)}")


class RealTimeAnomalyDetectionPipeline:
    """End-to-end real-time anomaly detection pipeline"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.consumer = None
        self.producer = None
        self.ml_model = None
    
    def initialize(self, ml_model) -> None:
        """Initialize the pipeline"""
        logger.info("Initializing real-time anomaly detection pipeline")
        
        self.ml_model = ml_model
        
        # Initialize consumer
        self.consumer = KafkaStreamConsumer(self.config['kafka'])
        self.consumer.connect()
        
        # Initialize producer
        self.producer = KafkaStreamProducer(self.config['kafka'])
        self.producer.connect()
        
        # Register processors
        transaction_processor = TransactionStreamProcessor(ml_model, self.config.get('transaction', {}))
        self.consumer.register_processor('transactions', transaction_processor)
        
        alert_processor = AlertStreamProcessor(self.config.get('alerts', {}))
        self.consumer.register_processor('fraud_alerts', alert_processor)
        
        # Register handlers
        self.consumer.register_handler('transactions', lambda r: self._handle_transaction_result(r))
        self.consumer.register_handler('fraud_alerts', lambda r: self._handle_alert_result(r))
    
    def _handle_transaction_result(self, result: Dict[str, Any]) -> None:
        """Handle transaction processing result"""
        logger.info(f"Transaction result: {result}")
        self.producer.send_result('fraud_detection_results', result)
    
    def _handle_alert_result(self, result: Dict[str, Any]) -> None:
        """Handle alert processing result"""
        logger.info(f"Alert result: {result}")
        self.producer.send_result('alert_processing_results', result)
    
    def run(self) -> None:
        """Run the pipeline"""
        try:
            self.consumer.start_consuming(
                topics=['transactions', 'fraud_alerts'],
                timeout=1
            )
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Shutdown the pipeline"""
        logger.info("Shutting down pipeline")
        if self.consumer:
            self.consumer.disconnect()
        if self.producer:
            self.producer.disconnect()
