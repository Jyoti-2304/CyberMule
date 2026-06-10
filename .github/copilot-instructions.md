# Bank Fraud Detection Solution - Copilot Instructions

## Project Overview
AI/ML solution for detecting suspicious transactions and mule accounts by ingesting real-time financial data, fraud monitoring alerts, transaction monitoring system alerts, and government cyber fraud alerts.

## Key Components
- **Data Ingestion**: Multi-source data consumption (transactions, fraud alerts, TMS alerts, govt alerts)
- **ML Models**: Transaction anomaly detection, mule account identification
- **Real-time Processing**: Kafka-based stream processing
- **API Layer**: FastAPI for fraud detection endpoints
- **Database**: PostgreSQL for transactional data, MongoDB for alerts/logs
- **Monitoring**: Prometheus metrics and alerts

## Development Guidelines
- Use Python 3.9+
- Follow PEP 8 coding standards
- Write unit tests for all features
- Use logging for debugging and monitoring
- Follow security best practices for sensitive financial data
- Implement data validation at all ingestion points
