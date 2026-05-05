import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np


def set_office_bg():
    img_url = "https://images.unsplash.com/photo-1579441982815-be67da231afb?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
    # "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070"

    st.markdown(
        f"""
        <style>
        .stApp {{
            /* Gradient gelap agar teks tetap kontras di atas gambar gedung */
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)), 
                        url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}

        /* Warna teks judul: Putih bersih dengan sedikit glow */
        h1, h2, h3 {{
            color: #ffffff !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
        }}

        /* Teks pendukung */
        p, span, label {{
            color: #e0e0e0 !important;
        }}

        /* Merapikan kontainer grafik Plotly */
        .stPlotlyChart {{
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_office_bg()


st.set_page_config(
    page_title='Dashboard Ecommerce Startup',
    page_icon='📶'
)

st.title('Dashboard Ecommerce Startup')
st.sidebar.success('Select a page above')

st.header('🤖 Churn Prediction Tool')
st.write('Input customer details in the sidebar to predict churn risk.')

st.sidebar.divider()
st.sidebar.header('User Input Features')
encoders = joblib.load('label_encoder.pkl')

list_gender = encoders['gender'].classes_
gender_user = st.sidebar.selectbox("Gender", list_gender)
gender_encoded = encoders['gender'].transform([gender_user])[0]

list_country = encoders['country'].classes_
country_user = st.sidebar.selectbox("Country", list_country)
country_encoded = encoders['country'].transform([country_user])[0]

list_traffic = encoders['traffic_source'].classes_
traffic_user = st.sidebar.selectbox("Traffic Source", list_traffic)
traffic_encoded = encoders['traffic_source'].transform([traffic_user])[0]


age = st.sidebar.slider("Age", 10, 100, 30)

total_order = st.sidebar.slider("Total Order", 1, 10, 5)

total_spend = st.sidebar.number_input("Total Spend ($)", min_value=0.1, max_value=2000.0, value=900.0)

avg_order_value = st.sidebar.number_input("Average Order Value ($)", min_value=0.1, max_value=1200.0, value=500.0)

unique_category_count = st.sidebar.slider("Unique Category Count", 1, 26, 3)

if st.sidebar.button("Predict Now"):
    state_default = 0
    city_default = 0
    features = np.array(
        [[
            age, gender_encoded, state_default, city_default, country_encoded,
            traffic_encoded, total_order, total_spend, avg_order_value, unique_category_count
        ]]
    )

    model = joblib.load('model.pkl')

    prediction = model.predict(features)
    y_pred = prediction[0]
    y_probs = model.predict_proba(features)[0][1]

    st.divider()
    st.subheader("📊 Prediction Analysis Result")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Prediction:**")
        if y_pred == 1:
            st.error(f"## CHURN")
        else:
            st.success(f"## STAY")

    with col2:
        st.write("**Churn Prediction:**")
        st.info(f"## {y_probs*100:.2f}%")

    st.write(f"The prediction probability of churn is: **{y_probs*100:.2f}%**")
    st.progress(y_probs)

    if y_pred == 1:
        st.warning("👉 **Action:** High churn risk detected. Consider providing a targeted promotion.")
    else:
        st.info("👉 **Action:** Stable customer. Consider loyalty programs to maintain retention.")