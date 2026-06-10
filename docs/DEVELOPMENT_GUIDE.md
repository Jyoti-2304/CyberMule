# Development Guide

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- MongoDB 5.0+
- Apache Kafka 3.0+
- Docker & Docker Compose (for containerized development)

### Local Development Setup

#### 1. Clone and Setup

```bash
cd "c:\Users\Friends\Desktop\bank fraud detection"
python -m venv venv
.\venv\Scripts\activate  # On Windows
# or: source venv/bin/activate  # On Unix
pip install -r requirements.txt
```

#### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your local settings
```

#### 3. Start Services with Docker Compose

```bash
# Start all services
docker-compose -f deployment/docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### 4. Initialize Database

```bash
python -c "from src.database import create_database_manager; mgr = create_database_manager('postgresql://fraud_user:fraud_password@localhost/fraud_detection_db'); print('Database initialized')"
```

## Project Structure Guide

### Core Modules

- **`src/data_ingestion/`**: Multi-source data connector framework
  - `TransactionFeedConnector`: Real-time transaction ingestion
  - `FraudMonitoringAlertConnector`: Fraud system integration
  - `TMSAlertConnector`: Transaction monitoring integration
  - `GovernmentFraudAlertConnector`: Government alerts integration

- **`src/data_processing/`**: Data pipeline and feature engineering
  - Data cleaning and validation
  - Feature engineering for fraud detection
  - Mule account indicators
  - Normalization and scaling

- **`src/ml_models/`**: Machine learning models
  - `TransactionAnomalyDetector`: Isolation Forest-based anomaly detection
  - `MuleAccountDetector`: Random Forest classifier
  - `EnsembleAnomalyDetector`: Ensemble voting
  - `ModelRegistry`: Model versioning and management

- **`src/real_time_processing/`**: Stream processing
  - Kafka consumer/producer
  - Real-time transaction scoring
  - Alert stream processing
  - Results publishing

- **`src/api/`**: REST API
  - FastAPI application
  - Endpoints for scoring and detection
  - Request/response models
  - Health checks

- **`src/database/`**: Data persistence
  - SQLAlchemy ORM models
  - PostgreSQL schema
  - MongoDB document schemas
  - Database management

- **`src/monitoring/`**: System monitoring
  - Prometheus metrics
  - Alert management
  - Health monitoring
  - Sentry error tracking

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: description"

# Push and create PR
git push origin feature/your-feature-name
```

### 2. Testing

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_data_ingestion.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_ml_models.py::TestTransactionAnomalyDetector::test_training -v
```

### 3. Code Quality

```bash
# Format code with Black
black src/ tests/

# Lint with Flake8
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

### 4. Model Development

Use Jupyter notebooks in `notebooks/` for experimentation:

```bash
jupyter notebook notebooks/01_train_models.py
```

### 5. Documentation

Write docstrings following Google style:

```python
def example_function(param1: str, param2: int) -> Dict[str, Any]:
    """Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something is wrong
        
    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
    """
```

## Debugging

### Using Python Debugger

```python
import pdb; pdb.set_trace()  # Set breakpoint
```

### Logging

```python
from src.logging_config import get_logger

logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Database Debugging

```bash
# Connect to PostgreSQL
psql -U fraud_user -d fraud_detection_db -h localhost

# View tables
\dt

# Query data
SELECT * FROM transactions LIMIT 10;
```

### Kafka Debugging

```bash
# List topics
docker-compose exec kafka kafka-topics --bootstrap-server kafka:9092 --list

# Monitor topic messages
docker-compose exec kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic transactions --from-beginning

# Check consumer group status
docker-compose exec kafka kafka-consumer-groups --bootstrap-server kafka:9092 --list
```

## API Development

### Adding New Endpoint

1. Define request/response models in `src/api/__init__.py`:

```python
class NewRequest(BaseModel):
    field1: str
    field2: int
```

2. Add endpoint in `APIServer._setup_routes()`:

```python
@self.app.post("/api/v1/new-endpoint")
async def new_endpoint(request: NewRequest):
    """Endpoint description"""
    try:
        result = self._process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

3. Test the endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/new-endpoint \
  -H "Content-Type: application/json" \
  -d '{"field1": "value", "field2": 123}'
```

### Documentation

Auto-generated docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Performance Testing

### Load Testing with Locust

```python
# tests/locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def score_transaction(self):
        self.client.post("/api/v1/score-transaction", 
                        json={"transactions": [...]})
```

```bash
locust -f tests/locustfile.py --host=http://localhost:8000
```

## Deployment

### Local Testing

```bash
# Build image
docker build -t fraud-detection:latest -f deployment/Dockerfile .

# Run container
docker run -p 8000:8000 fraud-detection:latest

# Test API
curl http://localhost:8000/health
```

### Production Deployment

See `deployment/` directory for Kubernetes manifests and cloud deployment guides.

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running: `docker-compose ps postgres`
   - Verify credentials in `.env`
   - Check network connectivity

2. **Kafka Connection Error**
   - Ensure Kafka/Zookeeper are running: `docker-compose ps`
   - Check bootstrap servers in config
   - Verify Kafka port 9092 is accessible

3. **Model Loading Error**
   - Ensure model files exist in `models/` directory
   - Check file permissions
   - Verify pickle file integrity

4. **API Port Already in Use**
   - Kill process: `lsof -ti:8000 | xargs kill -9`
   - Or use different port in `.env`

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kafka Python Client](https://github.com/confluentinc/confluent-kafka-python)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Prometheus Metrics](https://prometheus.io/docs/)

## Getting Help

- Check existing issues on GitHub
- Review code examples in `notebooks/`
- Consult team documentation
- Contact: fraud-detection@bank.com
