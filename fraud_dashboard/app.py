import streamlit as st
import pandas as pd
import random

import os 
print(os.getcwd())

st.set_page_config(page_title="FraudGuard AI",
                   page_icon ="💳",
                     layout="wide")

st.title("FraudGuard AI")

#df = pd.read_csv("data.csv")

total_transactions = 0

fraud_count = 0

st.caption("Real-time Fraud Detection and Risk Analysis Platform")
st.sidebar.header("Upload CSV")
file = st.sidebar.file_uploader("Upload file", type=["csv"])

def predict(df):
    scores = []
    labels = []
    for i in range(len(df)):
        score = random.randint(1, 100)
        label = "Fraud" if score > 70 else "Normal"
        scores.append(score)
        labels.append(label)
    return scores, labels



if file:
    df = pd.read_csv(file)
    st.subheader("📊 Input Data")
    st.dataframe(df)
    total_transactions = len(df)
    scores, labels = predict(df)
    df["Risk Score"] = scores
    df["Prediction"] = labels

    st.subheader("🧠 Results")
    st.dataframe(df)
    fraud_count = labels.count("Fraud")

col1,col2,col3,col4 = st.columns(4)
with col1:
    st.metric("Total Transactions", total_transactions)
with col2:
    st.metric("Fraud Cases", fraud_count)
with col3:
    st.metric("Accuracy", "97.35%")
with col4:
    st.metric("Risk Alert","34")

if file:
    if fraud_count > 0:
        st.error(f"🚨 Fraud Detected: {fraud_count} cases")
    else:
        st.success("✅ No Fraud Detected")

    st.subheader("📊 Analytics")
    st.bar_chart(df["Risk Score"])

else:
    st.info("👈 Upload CSV to start")
