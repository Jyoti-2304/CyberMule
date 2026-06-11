import streamlit as st
import pandas as pd
import random

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

st.divider()
st.caption("FraudGuard AI | Hackthon Project 2026")

#df = pd.read_csv("data.csv")


st.caption("Real-time Fraud Detection and Risk Analysis Platform")
st.sidebar.title("⚙️ Control Panel")
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
    with st.spinner("Analyzing transactions......"):
        df = pd.read_csv(file)
    st.subheader("📊 Input Data")
    st.dataframe(df)
    total_transactions = len(df)
    scores, labels = predict(df)
    df["Risk Score"] = scores
    df["Prediction"] = labels

    def get_risk(score):
        if score > 70:
            return "High"
        elif score > 40:
            return "Medium"
        else:
            return "Low"
    df["Risk Level"] = df["Risk Score"].apply(get_risk)

    st.success("✅ Analysis Completed Successfully")

    st.subheader("🧠 Results")
    st.dataframe(df)
    fraud_count = labels.count("Fraud")
col1,col2,col3,col4 = st.columns(4)
with col1:
    st.metric("Total Transactions", total_transactions)
with col2:
    st.metric("Fraud Cases", fraud_count)
with col3:
    if file:
        st.metric("Model Status", "Active")
    else:
        st.metric("Accuracy", "N/A")
with col4:
    if file:
        st.metric("Risk Alert", fraud_count)
    else:
        st.metric("Risk Alert", "N/A")

if file:
    if fraud_count > 0:
        st.error(f"🚨 Fraud Detected: {fraud_count} cases")
    else:
        st.success("✅ No Fraud Detected")

    st.subheader("📊 Analytics")

    risk_counts = df["Risk Level"].value_counts()
    st.write("### Risk Category Distribution")
    st.bar_chart(risk_counts)

    top30 = df.sort_values(
        by="Risk Score",
        ascending=False
        ).head(30)
    st.write("### Top 30 High-Risk Transactions")
    st.dataframe(top30)
else:
    st.info("👈 Upload CSV to start")
