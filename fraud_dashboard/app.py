import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os 

print(os.getcwd())

st.set_page_config(page_title="FraudGuard AI",
                   page_icon ="💳",
                     layout="wide")

st.markdown("""
<style>
h1{
   color: #2563EB;
}
            
div[data_testid="metric-container"]{
    background-color: white;
    border: 1px solid #E5E7EB;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

st.title("FraudGuard AI")
total_transactions = 0
fraud_count = 0

st.caption("Real-time Fraud Detection and Risk Analysis Platform")
st.sidebar.title("⚙️ Control Panel")
st.sidebar.header("Upload CSV")
file = st.sidebar.file_uploader("Upload file", type=["csv"])

anomaly_model = joblib.load("../models/transaction_anomaly_detector.pkl")
mule_model = joblib.load("../models/mule_account_detector.pkl")

st.success("✅ Models Loaded Successfully")

if file:
    df = pd.read_csv(file)

    st.write("📌 Uploaded Columns:", df.columns)

    def detect_column(df, column_type):

        patterns = {
            "amount": [
                "amount", "amt", "value", "price",
                "payment", "money", "debit",
                "credit", "txn_amount",
                "transaction_amount"
            ],

        "date": [
            "date", "time", "timestamp",
            "datetime", "created",
            "transaction_date",
            "txn_date"
        ]
    }
        for col in df.columns:
            col_lower = col.lower().replace(" ", "_")

            for keyword in patterns[column_type]:
                if keyword in col_lower:
                    return col

        return None   

    amount_col = detect_column(df, "amount")
    date_col = detect_column(df,"date")

    if amount_col is None:

        numeric_cols = df.select_dtypes(
            include=["int64", "float64"]
        ).columns

        if len(numeric_cols) > 0:
            amount_col = numeric_cols[0]
    if date_col is None:

        for col in df.columns:

            try:
                pd.to_datetime(
                    df[col].head(10),
                    errors="raise"
                )

                date_col = col
                break

            except:
                continue            
    if amount_col is None:

        st.warning(
        "Amount column not detected automatically."
        )

        amount_col = st.selectbox(
            "Select Amount Column",
            df.columns
        )

    if date_col is None:

        st.warning(
            "Date column not detected automatically."
        )

        date_col = st.selectbox(
            "Select Date Column",
            df.columns
        )

    print(df.columns.tolist())
    df[date_col] = pd.to_datetime(
    df[date_col],
    errors="coerce"
)
    df["hour"] = df[date_col].dt.hour
    df["day_of_week"] = df[date_col].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    
    df[amount_col] = (
        df[amount_col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
    )
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
    
    df = df.dropna(subset=[amount_col, date_col])
    
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        st.error("Date conversion failed. Invalid date format in CSV.")
        st.stop()
    df["amount_log"] = np.log1p(df[amount_col])
    df["hour"] = df[date_col].dt.hour
    df["day_of_week"] = df[date_col].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    features = anomaly_model["feature_names"]
    missing = [c for c in features if c not in df.columns]

    if missing:
        st.error(f"❌ Feature engineering failed: {missing}")
        st.stop()

    X = df[features]

    model = anomaly_model["model"]

    try:
        preds = model.predict(X)
        scores = model.decision_function(X)

    except Exception as e:
        st.error(f"Prediction Error: {e}")
        st.stop()

    df["Prediction"] = [
        "Fraud" if p == -1 else "Normal"
        for p in preds
    ]

    df["Risk Score"] = (
        (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
    ) * 100

    df["Risk Level"] = pd.cut(
        df["Risk Score"],
        bins=[-1, 40, 70, 100],
        labels=["Low", "Medium", "High"]
    )

    fraud_count = (preds == -1).sum()
    total_transactions = len(df)        

    st.subheader("📊 Results")
    st.dataframe(df)

    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", total_transactions)
    with col2:
        st.metric("Fraud Cases", fraud_count)
    with col3:
        st.metric("Model Status", "Active")
    with col4:
        st.metric("Risk Alert", fraud_count)


    if fraud_count > 0:
        st.error(f"🚨 Fraud Detected: {fraud_count} cases")
    else:
        st.success("✅ No Fraud Detected")

    st.subheader("📊 Risk Distribution")
    st.bar_chart(df["Risk Level"].value_counts())

    st.subheader("🔥 Top Risk Transactions")
    st.dataframe(df.sort_values("Risk Score", ascending=False).head(20))
  

st.divider()
st.caption("FraudGuard AI | Hackthon Project 2026")