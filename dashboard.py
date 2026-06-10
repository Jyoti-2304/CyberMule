import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Page Configuration
st.set_page_config(
    page_title="AI Bank Fraud Detection",
    page_icon="🏦",
    layout="wide"
)

# Header
st.title("🏦 AI-Powered Bank Fraud Detection System")
st.markdown("### Real-Time Fraud & Mule Account Monitoring Dashboard")

# Metrics Section
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Transactions", "12,458")

with col2:
    st.metric("Fraud Alerts", "145")

with col3:
    st.metric("Mule Accounts", "23")

with col4:
    st.metric("Risk Level", "HIGH")

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    pie_data = pd.DataFrame({
        "Type": ["Normal", "Fraud"],
        "Count": [11800, 658]
    })

    fig = px.pie(
        pie_data,
        values="Count",
        names="Type",
        title="Transaction Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    risk_data = pd.DataFrame({
        "Risk": ["Low", "Medium", "High"],
        "Count": [700, 250, 100]
    })

    fig2 = px.bar(
        risk_data,
        x="Risk",
        y="Count",
        title="Risk Distribution"
    )

    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Fraud Detection Section
st.subheader("🔍 Fraud Transaction Analysis")

amount = st.number_input(
    "Transaction Amount",
    min_value=0,
    value=500000
)

if st.button("Analyze Transaction"):

    payload = {
        "transaction_id": "TXN1001",
        "amount": amount,
        "sender": "ACC001",
        "receiver": "ACC999",
        "transaction_type": "IMPS",
        "timestamp": "2026-06-05T23:00:00",
        "channel": "Mobile Banking"
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/score-transaction",
            json=payload
        )

        st.success("API Connected Successfully")
        st.json(response.json())

    except Exception as e:
        st.error(f"Connection Error: {e}")

st.divider()

# Alerts Table
st.subheader("🚨 Recent Fraud Alerts")

alerts = pd.DataFrame({
    "Account": ["ACC101", "ACC202", "ACC303", "ACC404"],
    "Amount": [450000, 720000, 380000, 910000],
    "Risk": ["High", "High", "Medium", "Critical"]
})

st.dataframe(alerts, use_container_width=True)

st.divider()

# Footer
st.markdown(
    """
    ### About the System
    This platform detects suspicious transactions and mule accounts using:
    
    - AI/ML-based Fraud Detection
    - Real-Time Transaction Monitoring
    - Mule Account Identification
    - Government Fraud Alert Integration
    - Cross-Channel Banking Analytics
    """
)
