# API Documentation

## Overview

The Bank Fraud Detection API provides real-time endpoints for:
- Transaction fraud scoring
- Mule account detection
- Batch processing
- Fraud alert management
- System health monitoring

## Base URL

```
http://localhost:8000
```

## Authentication

API endpoints require JWT token or API key in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Health Check

**GET** `/health`

Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-05T10:30:00Z",
  "version": "1.0.0"
}
```

---

### Score Transactions

**POST** `/api/v1/score-transaction`

Score one or more transactions for fraud risk.

**Request:**
```json
{
  "transactions": [
    {
      "transaction_id": "TXN001",
      "amount": 1500.50,
      "sender": "ACC001",
      "receiver": "ACC002",
      "transaction_type": "transfer",
      "timestamp": "2024-06-05T10:30:00Z",
      "channel": "online"
    }
  ],
  "include_details": true
}
```

**Response:**
```json
[
  {
    "transaction_id": "TXN001",
    "is_fraud": false,
    "fraud_score": 0.35,
    "fraud_probability": 0.35,
    "risk_level": "MEDIUM",
    "confidence": 0.92,
    "flagged_features": ["high_amount"],
    "recommendations": ["Monitor account", "Check sender history"]
  }
]
```

**Status Codes:**
- `200 OK` - Successful scoring
- `400 Bad Request` - Invalid request format
- `503 Service Unavailable` - Model not loaded

---

### Detect Mule Account

**POST** `/api/v1/detect-mule-account`

Detect if an account exhibits mule account characteristics.

**Request:**
```json
{
  "account_id": "ACC123",
  "time_window_days": 30
}
```

**Response:**
```json
{
  "account_id": "ACC123",
  "is_mule_account": true,
  "mule_score": 0.78,
  "indicators": {
    "transaction_frequency": "high",
    "unique_counterparties": 45,
    "small_transaction_ratio": 0.85,
    "money_flow_direction": "predominantly_outbound",
    "transactions_in_window": 156,
    "average_transaction_time": "4.2 hours"
  },
  "recommendation": "High risk - Recommend investigation"
}
```

**Status Codes:**
- `200 OK` - Successfully analyzed
- `404 Not Found` - Account not found
- `503 Service Unavailable` - Model not loaded

---

### Batch Score

**POST** `/api/v1/batch-score`

Submit a batch of transactions for asynchronous scoring.

**Request:**
```json
{
  "transactions": [
    {
      "transaction_id": "TXN001",
      "amount": 1500,
      "sender": "ACC001",
      "receiver": "ACC002",
      "transaction_type": "transfer",
      "timestamp": "2024-06-05T10:30:00Z"
    },
    {
      "transaction_id": "TXN002",
      "amount": 50000,
      "sender": "ACC003",
      "receiver": "ACC004",
      "transaction_type": "transfer",
      "timestamp": "2024-06-05T10:31:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "job_id": "batch_1717584600000",
  "status": "queued",
  "created_at": "2024-06-05T10:30:00Z"
}
```

---

### Get Batch Result

**GET** `/api/v1/batch-score/{job_id}`

Retrieve results of a batch scoring job.

**Response (Processing):**
```json
{
  "job_id": "batch_1717584600000",
  "status": "processing",
  "progress": 45,
  "processed": 45,
  "total": 100
}
```

**Response (Completed):**
```json
{
  "job_id": "batch_1717584600000",
  "status": "completed",
  "results": [
    {
      "transaction_id": "TXN001",
      "is_fraud": false,
      "fraud_score": 0.35,
      "risk_level": "MEDIUM"
    },
    {
      "transaction_id": "TXN002",
      "is_fraud": true,
      "fraud_score": 0.82,
      "risk_level": "CRITICAL"
    }
  ],
  "completed_at": "2024-06-05T10:35:00Z"
}
```

---

### Receive Fraud Alert

**POST** `/api/v1/alert`

Receive and process fraud alerts from monitoring systems.

**Request:**
```json
{
  "alert_id": "ALERT_ABC123",
  "alert_type": "unusual_pattern",
  "source": "fraud_monitoring_system",
  "severity": "HIGH",
  "affected_entities": ["ACC001", "ACC002"],
  "details": {
    "pattern": "Rapid sequence of large transfers",
    "threshold_exceeded": true
  }
}
```

**Response:**
```json
{
  "alert_id": "ALERT_ABC123",
  "status": "received",
  "received_at": "2024-06-05T10:30:00Z"
}
```

---

## Response Models

### FraudScoreResponse

```
transaction_id: string        - Unique transaction identifier
is_fraud: boolean             - Fraud determination
fraud_score: float (0.0-1.0)  - Raw fraud score
fraud_probability: float      - Fraud probability
risk_level: string            - LOW, MEDIUM, HIGH, CRITICAL
confidence: float (0.0-1.0)   - Model confidence
flagged_features: array       - Features triggering fraud flag
recommendations: array        - Recommended actions
```

### MuleAccountResponse

```
account_id: string            - Account identifier
is_mule_account: boolean      - Mule account determination
mule_score: float (0.0-1.0)   - Mule probability score
indicators: object            - Mule behavior indicators
recommendation: string        - Analyst recommendation
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request format"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds"
}
```

### 503 Service Unavailable

```json
{
  "detail": "Model not loaded or database unavailable"
}
```

## Rate Limiting

- Per-user limit: 1000 requests/hour
- Batch endpoint: 100 jobs/hour
- Burst allowance: 10 requests/second

## Examples

### Python

```python
import requests
import json

# Score a transaction
url = "http://localhost:8000/api/v1/score-transaction"
payload = {
    "transactions": [{
        "transaction_id": "TXN001",
        "amount": 1500.00,
        "sender": "ACC001",
        "receiver": "ACC002",
        "transaction_type": "transfer",
        "timestamp": "2024-06-05T10:30:00Z"
    }]
}

headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### cURL

```bash
curl -X POST http://localhost:8000/api/v1/score-transaction \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [{
      "transaction_id": "TXN001",
      "amount": 1500.00,
      "sender": "ACC001",
      "receiver": "ACC002",
      "transaction_type": "transfer",
      "timestamp": "2024-06-05T10:30:00Z"
    }]
  }'
```

## Webhooks

Configure webhooks for:
- Fraud detection alerts
- Batch job completion
- System health alerts

## Versioning

Current API version: **v1**

APIs follow semantic versioning:
- `v1` - Current production API
- Breaking changes increment major version
- New features use minor version bump

## Pagination

For list endpoints, use query parameters:

```
GET /api/v1/transactions?page=1&per_page=50&sort=-created_at
```

## Monitoring

- API metrics at: `http://localhost:8001/metrics`
- System health: `http://localhost:8000/health`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc docs: `http://localhost:8000/redoc`
