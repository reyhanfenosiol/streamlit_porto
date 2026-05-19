import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
import os


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
    page_title='E-commerce Churn Prediction',
    page_icon='📶'
)

st.title('E-commerce Churn Prediction')
st.sidebar.success('Select a page above')

st.header('👤 Customer Churn Prediction')

st.sidebar.divider()

current_dir = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_dir, ".."))
path_ke_encoder = os.path.join(root_path, 'label_encoder.pkl')
path_ke_model = os.path.join(root_path, 'model.pkl')
path_ke_compare = os.path.join(root_path, 'best_model.csv')
path_ke_customer = os.path.join(root_path, 'model_results.csv')

try:
    encoders = joblib.load(path_ke_encoder)
    model = joblib.load(path_ke_model)
    compare = pd.read_csv(path_ke_compare)
except Exception as e:
    st.error(f"Gagal memuat file: {e}")
    st.info(f"Mencari di: {root_path}")



# pembagian tab
tab1, tab2, tab3 = st.tabs(["🧠 Churn Model",
                      "⚖️ Model Comparison",
                      "🗂️ Raw Data & Filters"])

with tab1:
    st.sidebar.header('User Input Features')
    list_gender = encoders['gender'].classes_
    gender_user = st.sidebar.selectbox("Gender", list_gender)
    gender_encoded = encoders['gender'].transform([gender_user])[0]

    list_country = encoders['country'].classes_
    country_user = st.sidebar.selectbox("Country", list_country)
    country_encoded = encoders['country'].transform([country_user])[0]

    list_traffic = encoders['traffic_source'].classes_
    traffic_user = st.sidebar.selectbox("Traffic Source", list_traffic)
    traffic_encoded = encoders['traffic_source'].transform([traffic_user])[0]


    st.write('Input customer details in the sidebar to predict churn risk.')
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


with tab2:
    st.write("The churn model uses Light Gradient Boosting Machine for a reason below.")
    st.info("""
            Among all model LGBM delivers the best overall performance accross
            Recall, Precision, F1-Score, AUC and Accuracy.  
    """)
    compare = compare.iloc[:, 1:-1]
    compare.index = range(1, len(compare)+1)
    compare.index.name = 'Rank'
    styled_compare = compare.style.background_gradient(
        cmap='RdYlGn'
    ).format(precision=3)
    st.dataframe(styled_compare, use_container_width=True)


with tab3:
    st.subheader("Displaying Dataset of Customer Churn")
    df_churn = pd.read_csv(path_ke_customer)
    df_churn.index.name = 'no'
    # df_churn = df_churn.reset_index()
    ui_cols = st.columns(3)
    df_churn_filter = df_churn.copy()
    for i, col_name in enumerate(df_churn.select_dtypes(include=['number']).columns):
        ui_idx = i % 3
        with ui_cols[ui_idx]:
            # Cek apakah kolom adalah y_prob atau bertipe float
            if col_name == 'y_prob' or df_churn[col_name].dtype == 'float64':
                min_val = float(df_churn[col_name].min())
                max_val = float(df_churn[col_name].max())
                step = 0.01 # Agar slider bisa digeser per 0.01
                format = "%.2f"
            else:
                min_val = int(df_churn[col_name].min())
                max_val = int(df_churn[col_name].max())
                step = 1
                format = "%d"
            
            if min_val < max_val:
                selected_range = st.slider(
                    f"Filter {col_name}", 
                    min_val, 
                    max_val, 
                    (min_val, max_val),
                    step=step,
                    format=format,
                    key=f"slider_{col_name}"
                )
                
                df_churn_filter = df_churn_filter[
                    (df_churn_filter[col_name] >= selected_range[0]) &
                    (df_churn_filter[col_name] <= selected_range[1])
                ]
            else:
                st.write(f"Filter {col_name}")
                st.caption(f"Value: {min_val}")

    st.dataframe(df_churn_filter, use_container_width=True)
    st.info(f"Showing {len(df_churn_filter)} out of {len(df_churn)} records after applying filters.")




    # Menampilkan detail label encoding
    encoder_show = joblib.load(path_ke_encoder)
    # Memeriksa apakah ini adalah LabelEncoder (memiliki atribut classes_)
    kolom_pilihan = st.selectbox("Choose a column to view label details:", list(encoder_show.keys()))

    # Ambil objek encoder berdasarkan pilihan
    target_encoder = encoder_show[kolom_pilihan]

    # Bongkar classes_ untuk mendapatkan arti numeriknya
    if hasattr(target_encoder, 'classes_'):
        mapping_dict = {
            "Numeric Value": range(len(target_encoder.classes_)),
            "Original Label": target_encoder.classes_
        }
        df_mapping = pd.DataFrame(mapping_dict)
        
        st.write(f"These are the mappings for column **{kolom_pilihan}**:")
        st.dataframe(df_mapping, use_container_width=True, hide_index=True)
    else:
        st.warning("This object does not have a 'classes_' attribute.")