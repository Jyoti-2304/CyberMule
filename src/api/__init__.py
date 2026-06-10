"""
FastAPI server for fraud detection endpoints.
Provides REST API for transaction fraud scoring and mule account detection.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

logger = logging.getLogger(__name__)


# Pydantic models for request/response
class Transaction(BaseModel):
    """Transaction model"""
    transaction_id: str
    amount: float
    sender: str
    receiver: str
    transaction_type: str
    timestamp: str
    channel: Optional[str] = None


class FraudScoreRequest(BaseModel):
    """Request model for fraud scoring"""
    transactions: List[Transaction]
    include_details: bool = False


class FraudScoreResponse(BaseModel):
    """Response model for fraud scores"""
    transaction_id: str
    is_fraud: bool
    fraud_score: float
    fraud_probability: float
    risk_level: str
    confidence: float
    flagged_features: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None


class MuleAccountRequest(BaseModel):
    """Request model for mule account detection"""
    account_id: str
    time_window_days: int = 30


class MuleAccountResponse(BaseModel):
    """Response model for mule account detection"""
    account_id: str
    is_mule_account: bool
    mule_score: float
    indicators: Dict[str, Any]
    recommendation: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


class APIServer:
    """FastAPI server for fraud detection"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.app = FastAPI(
            title="Bank Fraud Detection API",
            description="API for detecting fraudulent transactions and mule accounts",
            version="1.0.0"
        )
        self.transaction_model = None
        self.mule_model = None
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup API routes"""
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            }
        
        @self.app.post("/api/v1/score-transaction", response_model=List[FraudScoreResponse])
        async def score_transactions(request: FraudScoreRequest):
            """Score transactions for fraud risk"""
            try:
                if not self.transaction_model:
                    raise HTTPException(status_code=503, detail="Transaction model not loaded")
                
                results = []
                
                for transaction in request.transactions:
                    try:
                        # Get fraud score
                        score = self._get_transaction_fraud_score(transaction)
                        results.append(score)
                    except Exception as e:
                        logger.error(f"Error scoring transaction {transaction.transaction_id}: {str(e)}")
                        raise HTTPException(status_code=400, detail=f"Error scoring transaction: {str(e)}")
                
                return results
            
            except Exception as e:
                logger.error(f"Error in score_transactions: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/v1/detect-mule-account", response_model=MuleAccountResponse)
        async def detect_mule_account(request: MuleAccountRequest):
            """Detect if account is a mule account"""
            try:
                if not self.mule_model:
                    raise HTTPException(status_code=503, detail="Mule account model not loaded")
                
                result = self._detect_mule_account(request.account_id, request.time_window_days)
                return result
            
            except Exception as e:
                logger.error(f"Error detecting mule account: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/v1/batch-score")
        async def batch_score(request: FraudScoreRequest, background_tasks: BackgroundTasks):
            """Batch score transactions asynchronously"""
            try:
                job_id = self._create_batch_job(request.transactions)
                background_tasks.add_task(self._process_batch_job, job_id)
                
                return {
                    'job_id': job_id,
                    'status': 'queued',
                    'created_at': datetime.utcnow().isoformat()
                }
            
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/api/v1/batch-score/{job_id}")
        async def get_batch_result(job_id: str):
            """Get batch scoring result"""
            try:
                result = self._get_batch_result(job_id)
                
                if not result:
                    raise HTTPException(status_code=404, detail="Batch job not found")
                
                return result
            
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/api/v1/alert")
        async def receive_alert(alert: Dict[str, Any]):
            """Receive fraud alert from monitoring system"""
            try:
                alert_id = self._process_fraud_alert(alert)
                
                return {
                    'alert_id': alert_id,
                    'status': 'received',
                    'received_at': datetime.utcnow().isoformat()
                }
            
            except Exception as e:
                logger.error(f"Error processing alert: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _get_transaction_fraud_score(self, transaction: Transaction) -> FraudScoreResponse:
        """Calculate fraud score for transaction"""
        # Placeholder implementation
        fraud_score = 0.3
        is_fraud = fraud_score > 0.5
        
        risk_level = 'HIGH' if fraud_score > 0.7 else 'MEDIUM' if fraud_score > 0.4 else 'LOW'
        
        flagged_features = []
        if transaction.amount > 50000:
            flagged_features.append('high_amount')
        
        recommendations = []
        if is_fraud:
            recommendations.append('Block transaction')
            recommendations.append('Investigate sender account')
        else:
            recommendations.append('Allow transaction')
        
        return FraudScoreResponse(
            transaction_id=transaction.transaction_id,
            is_fraud=is_fraud,
            fraud_score=fraud_score,
            fraud_probability=fraud_score,
            risk_level=risk_level,
            confidence=0.85,
            flagged_features=flagged_features,
            recommendations=recommendations
        )
    
    def _detect_mule_account(self, account_id: str, time_window_days: int) -> MuleAccountResponse:
        """Detect if account is a mule account"""
        # Placeholder implementation
        mule_score = 0.4
        is_mule = mule_score > 0.5
        
        indicators = {
            'transaction_frequency': 'high',
            'unique_counterparties': 15,
            'small_transaction_ratio': 0.8,
            'money_flow_direction': 'predominantly_outbound'
        }
        
        recommendation = 'Monitor closely' if is_mule else 'Normal activity'
        
        return MuleAccountResponse(
            account_id=account_id,
            is_mule_account=is_mule,
            mule_score=mule_score,
            indicators=indicators,
            recommendation=recommendation
        )
    
    def _create_batch_job(self, transactions: List[Transaction]) -> str:
        """Create batch scoring job"""
        job_id = f"batch_{datetime.utcnow().timestamp()}"
        logger.info(f"Created batch job {job_id} with {len(transactions)} transactions")
        return job_id
    
    def _process_batch_job(self, job_id: str) -> None:
        """Process batch job in background"""
        logger.info(f"Processing batch job {job_id}")
        # Placeholder implementation
        pass
    
    def _get_batch_result(self, job_id: str) -> Dict[str, Any]:
        """Get batch job result"""
        return {
            'job_id': job_id,
            'status': 'completed',
            'results': []
        }
    
    def _process_fraud_alert(self, alert: Dict[str, Any]) -> str:
        """Process fraud alert"""
        alert_id = alert.get('alert_id', f"alert_{datetime.utcnow().timestamp()}")
        logger.info(f"Processing fraud alert: {alert_id}")
        return alert_id
    
    def set_models(self, transaction_model=None, mule_model=None) -> None:
        """Set ML models for the API"""
        self.transaction_model = transaction_model
        self.mule_model = mule_model
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
        """Run the FastAPI server"""
        logger.info(f"Starting API server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, reload=reload)
    
    def get_app(self):
        """Get FastAPI app instance"""
        return self.app


def create_api_server(config: Dict[str, Any] = None) -> APIServer:
    """Factory function to create API server"""
    return APIServer(config)
