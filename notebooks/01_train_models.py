"""
Model training notebook template for fraud detection
This notebook demonstrates how to train and evaluate ML models
"""

# %%
# 1. Setup and Imports
# =====================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.train_test_split import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc

import sys
sys.path.insert(0, '..')

from src.data_ingestion import create_ingestor
from src.data_processing import DataProcessor
from src.ml_models import TransactionAnomalyDetector, MuleAccountDetector, ModelRegistry
from src.database import create_database_manager

# Set random seed for reproducibility
np.random.seed(42)

# %%
# 2. Load and Prepare Data
# =========================

print("Loading data...")

# Example: Load synthetic transaction data
transactions = [
    {
        'transaction_id': f'TXN_{i:05d}',
        'amount': np.random.exponential(1000),
        'sender': f'ACC_{np.random.randint(0, 1000):04d}',
        'receiver': f'ACC_{np.random.randint(0, 1000):04d}',
        'transaction_type': np.random.choice(['transfer', 'payment', 'withdrawal']),
        'timestamp': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 90)),
        'channel': np.random.choice(['online', 'atm', 'branch'])
    }
    for i in range(10000)
]

print(f"Loaded {len(transactions)} transactions")

# %%
# 3. Data Processing
# ====================

print("\nProcessing data...")

processor = DataProcessor()
df = processor.clean_transaction_data(transactions)

# Engineer features
df = processor.engineer_transaction_features(df)
df = processor.identify_mule_account_indicators(df)

# Normalize features
df, normalization_params = processor.normalize_features(df)

print(f"Processed data shape: {df.shape}")
print(f"Features: {df.columns.tolist()}")

# %%
# 4. Train Anomaly Detection Model
# ==================================

print("\nTraining anomaly detection model...")

# Select features for anomaly detection
anomaly_features = ['amount_log', 'hour', 'day_of_week', 'is_weekend']
X_anomaly = df[anomaly_features]

# Train model
anomaly_model = TransactionAnomalyDetector(contamination=0.1)
anomaly_model.train(X_anomaly)

# Get predictions
anomaly_scores = anomaly_model.predict(X_anomaly)
print(f"Anomalies detected: {anomaly_scores.sum()}")

# %%
# 5. Train Mule Account Detection Model
# ========================================

print("\nTraining mule account detection model...")

# Create synthetic labels for demonstration
mule_labels = np.random.randint(0, 2, len(df))

# Select features for mule detection
mule_features = [
    'transactions_as_sender',
    'transactions_as_receiver',
    'unique_counterparties_as_sender',
    'unique_counterparties_as_receiver',
    'small_amount_frequency'
]

# Handle missing values
mule_df = df[mule_features].fillna(0)

# Train model
mule_model = MuleAccountDetector()
mule_model.train(mule_df, mule_labels)

print("Model training completed")

# %%
# 6. Model Evaluation
# ====================

print("\nEvaluating models...")

# Evaluate anomaly detection
anomaly_proba = anomaly_model.predict_proba(X_anomaly)

# Evaluate mule detection
mule_proba = mule_model.predict_proba(mule_df)
mule_predictions = mule_model.predict(mule_df)

print("\nMule Detection Performance:")
print(classification_report(mule_labels, mule_predictions))

# %%
# 7. Visualizations
# ==================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Transaction amount distribution
axes[0, 0].hist(df['amount'], bins=50, edgecolor='black')
axes[0, 0].set_title('Transaction Amount Distribution')
axes[0, 0].set_xlabel('Amount')
axes[0, 0].set_ylabel('Frequency')

# Plot 2: Anomaly scores distribution
axes[0, 1].hist(anomaly_proba[:, 1], bins=50, edgecolor='black')
axes[0, 1].set_title('Anomaly Scores Distribution')
axes[0, 1].set_xlabel('Anomaly Score')
axes[0, 1].set_ylabel('Frequency')

# Plot 3: Mule scores distribution
axes[1, 0].hist(mule_proba[:, 1], bins=50, edgecolor='black')
axes[1, 0].set_title('Mule Scores Distribution')
axes[1, 0].set_xlabel('Mule Score')
axes[1, 0].set_ylabel('Frequency')

# Plot 4: Confusion matrix
cm = confusion_matrix(mule_labels, mule_predictions)
sns.heatmap(cm, annot=True, ax=axes[1, 1], fmt='d')
axes[1, 1].set_title('Mule Detection Confusion Matrix')
axes[1, 1].set_xlabel('Predicted')
axes[1, 1].set_ylabel('Actual')

plt.tight_layout()
plt.show()

# %%
# 8. Save Models
# ===============

print("\nSaving models...")

registry = ModelRegistry()

registry.register_model(
    'anomaly_detector',
    anomaly_model,
    {'features': anomaly_features, 'contamination': 0.1}
)

registry.register_model(
    'mule_detector',
    mule_model,
    {'features': mule_features}
)

# Optionally save to disk
anomaly_model.save('models/transaction_anomaly_detector.pkl')
mule_model.save('models/mule_account_detector.pkl')

print("Models saved successfully")

# %%
# 9. Model Feature Importance
# =============================

print("\nMule Detection Feature Importance:")
for feature, importance in sorted(
    mule_model.feature_importance.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"  {feature}: {importance:.4f}")
