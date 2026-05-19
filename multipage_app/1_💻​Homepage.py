import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
from datetime import datetime, timedelta 
import base64
from pathlib import Path
import os

def set_office_bg():
    img_url = "https://images.unsplash.com/photo-1526289034009-0240ddb68ce3?q=80&w=1171&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
    # "https://images.unsplash.com/photo-1512433155034-67102234a5e4?q=80&w=688&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
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
    page_title='E-commerce Analytics',
    page_icon='📶'
)

st.title('E-commerce Analytics')
st.sidebar.success('Select a page above')

st.header('📊​ Data Analysis')
st.set_page_config(layout='wide')

current_dir = os.path.dirname(__file__)
path = os.path.join(current_dir, "..", "prod_analysis.csv")
# path = 'D:\REYHAN\BOOST ACADEMY\projek_akhir'

df_prod = pd.read_csv(path)
df_prod['is_returned'] = df_prod['status'].apply(lambda x:1 if x == 'Returned' else 0)
df_prod['is_complete'] = df_prod['status'].apply(lambda x:1 if x == 'Returned' else 0)
df_vis = df_prod.copy()

st.write('This data shows product statistics by transaction item.')
st.divider()


# visual
st.sidebar.header('Input your Filters')

# global filter
list_negara = sorted(df_vis['country'].unique())
selected_countries = st.sidebar.multiselect(
    'Select country/countries',
    options=list_negara,
    default=[list_negara[0]]
    )

list_status = df_vis['status'].unique().tolist()
selected_status = st.sidebar.multiselect(
    'Select Status',
    options=list_status,
    default=list_status
    )

top_n = st.sidebar.slider('Top N Categories', min_value=3, max_value=20, value=5)

if not selected_countries or not selected_status:
    st.error("⚠️ **Please Complete your Filters!**")
    st.info("Please select at least one country and one status to display the data.")
    st.stop()
else:
    df_filtered = df_vis[
        (df_vis['country'].isin(selected_countries)) &
        (df_vis['status'].isin(selected_status))
    ]


# top categories
data_prod = df_filtered.copy()
data_prod = data_prod[data_prod['status'] != 'Cancelled']
data_prod = (data_prod['category'].value_counts(normalize=True)*100).round(2).reset_index(name='proportion')
fig_1 = px.bar(data_prod.head(top_n), x='proportion', y='category', orientation='h', 
               title=f"Top {top_n} Categories", color='proportion', color_continuous_scale='Viridis')
fig_1.update_yaxes(autorange="reversed")
fig_1.update_layout(
    xaxis_title='Proportion (%)',
    yaxis_title='Category'
)


# total order
df_filtered['created_at'] = pd.to_datetime(df_filtered['created_at'], format='ISO8601')
df_filtered['created_at'] = df_filtered['created_at'].dt.tz_localize(None)
one_year_ago = datetime.now() - timedelta(days=365)
df_line = df_filtered[df_filtered['created_at'] >= one_year_ago].copy()

data_line = df_line.groupby(df_line['created_at'].dt.date)['id'].count().reset_index(name='total_order')
fig_2 = px.line(
    data_line, x='created_at', y='total_order', title='Trend of Total Order (Last 1 Year)', markers=True,
    template='plotly_dark'
)

fig_2.update_layout(
    xaxis_title='Order Date',
    yaxis_title='Total Order'
)


# status detail
data_stat = df_filtered.groupby('status')['id'].count().reset_index(name='proportion')
fig_3 = px.pie(
    data_stat, values='proportion', names= 'status', 
    title= 'Proportion of Status', hole=0.4
)

fig_3.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=50, b=100), # Beri margin bawah (b) lebih besar untuk legenda
    legend=dict(
        orientation="h",     # Ubah ke HORIZONTAL
        yanchor="bottom",
        y=-0.5,              # Geser ke bawah area grafik
        xanchor="center",
        x=0.5                # Taruh di tengah
    ),
    title_font_size=18
)

# age distribution
data_age = df_filtered[df_filtered['status'] != 'Cancelled']
fig_4 = px.histogram(
    data_age, x='age', nbins=25, title='Distribution of Customer Age',
    color_discrete_sequence=['#636EFA']
)
fig_4.update_layout(
    xaxis_title='Customer Age',
    yaxis_title='Number of Customers'
)


# map distribution
fig_5 = px.scatter_map(
    df_filtered, 
    lat="latitude", 
    lon="longitude", 
    color="status", # Warna titik berdasarkan kategori
    size="sale_price", # Besar titik berdasarkan harga (opsional)
    hover_name="city", # Menampilkan nama kota saat kursor diarahkan
    zoom=1, 
    title="Customer Order Geographic Distribution"
)
fig_5.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0}, # Menghapus margin kanan, kiri, dan bawah
    legend=dict(
        orientation="h",       # Legenda horizontal
        yanchor="bottom",
        y=-0.1,                # Posisi di bawah peta
        xanchor="center",
        x=0.5
    )
)



# summary dashboard
today = datetime(2026, 4, 30)

first_day_curr = today.replace(day=1, hour=0, minute=0, second=0)
last_day_prev = first_day_curr - timedelta(seconds=1)
first_day_prev = last_day_prev.replace(day=1, hour=0, minute=0, second=0)

df_curr = df_filtered[(df_filtered['created_at'] >= first_day_curr) & (df_filtered['created_at'] <= today)]
df_prev = df_filtered[(df_filtered['created_at'] >= first_day_prev) & (df_filtered['created_at'] <= last_day_prev)]

df_curr_unique = df_curr.drop_duplicates(subset=['order_id'])
df_prev_unique = df_prev.drop_duplicates(subset=['order_id'])

def calculate_growth(current, previous):
    if previous == 0: return 0
    return ((current - previous) / previous) * 100

# Total Traffic
traffic_curr, traffic_prev = len(df_curr), len(df_prev)
traffic_growth = calculate_growth(traffic_curr, traffic_prev)

# New Users
users_curr, users_prev = df_curr['user_id'].nunique(), df_prev['user_id'].nunique()
users_growth = calculate_growth(users_curr, users_prev)

# Performance (Complete Rate)
perf_curr = (df_curr_unique['status'] == 'Complete').mean() * 100 if len(df_curr_unique) > 0 else 0
perf_prev = (df_prev_unique['status'] == 'Complete').mean() * 100 if len(df_prev_unique) > 0 else 0
perf_diff = perf_curr - perf_prev # Menggunakan selisih poin persentase sesuai gambar

# Sales (Volume Order)
sales_curr, sales_prev = len(df_curr_unique), len(df_prev_unique)
sales_growth = calculate_growth(sales_curr, sales_prev)


# layout dengan tab
tab4, tab1, tab2, tab3 = st.tabs([
                            "📖 Project Overview",
                            "📈 Descriptive Analysis", 
                            "🩺 Diagnostic Analysis",
                            "🗂️ Raw Data & Filters"
                            ])

with tab4:
    col_id, col_en = st.columns(2)
    with col_id:
        with st.container(border=True):
            st.write("**_Bahasa Indonesia_**")
            st.markdown(f"""
            **Latar Belakang Proyek**
            * **Profil Perusahaan:** Startup *e-commerce* dengan pertumbuhan pesat sejak pertama kali bertransaksi di tahun 2019 hingga saat ini.
            * **Skala Produk:** Mengelola portofolio luas mencakup 26 kategori produk dan lebih dari 2.700 variasi *brand*.
            * **Skala Pasar:** Mencatatkan lebih dari 100.000 transaksi di 15 negara dengan demografi pelanggan luas (pria & wanita, usia 12–70 tahun).

            **Tantangan**
            🎯**Skalabilitas Data:** Volume data yang membengkak menuntut optimasi arsitektur pelaporan demi efisiensi pengambilan keputusan.
            🎯**Kebutuhan Pipeline:** Harus membangun arsitektur data otomatis mulai dari *source* mentah di Google BigQuery, proses ETL via Apache Airflow, hingga visualisasi akhir.
            🎯**Analisis Retensi:** Memahami karakteristik pelanggan setia dan meminimalisir angka *customer churn*.
            🎯**Prediksi Real-Time:** Memfasilitasi Head of Operational untuk memantau data secara *real-time* dan memprediksi probabilitas *churn*.            
            
            **Solusi**
            ✨**Pipeline Data Otomatis:** Mengintegrasikan Google BigQuery, Airflow, dan Streamlit Cloud untuk membangun pipeline data yang otomatis dan terjadwal.            
            ✨**Dashboard Interaktif:** Menyajikan dashboard yang memungkinkan eksplorasi data secara detail dan menggali wawasan mendalam tanpa perlu penanganan file manual.

            **Hasil**
            ✅**Efisiensi Alur Kerja 200%:** Memangkas waktu pengelolaan *big data flow* secara drastis dengan beralih dari *coding* manual ke sistem otomatis penuh untuk proses ekstraksi, pembersihan/transformasi, *push* ke GitHub, hingga visualisasi di platform Streamlit.
            ✅**Aksesibilitas Non-Teknis:** Analitik kini dapat digunakan dengan mudah oleh pengguna non-teknis melalui visualisasi interaktif yang dapat diakses secara *real-time*.
            ✅**Keamanan & Fleksibilitas Penjadwalan:** Menggunakan Apache Airflow yang terpasang langsung pada server untuk menjamin keamanan data di dalam *private cloud* serta memungkinkan penjadwalan otomatis sesuai kebutuhan bisnis.
            ✅**Asisten Analis Berbasis AI:** Integrasi *chatbot agent* berfungsi sebagai asisten analis yang mampu menyajikan penjelasan data dalam bentuk narasi kontekstual untuk mendukung fleksibilitas pengambilan keputusan bagi *decision maker*.
            """)

    with col_en:
        with st.container(border=True):
            st.write("**_English_**")
            st.markdown(f"""
            **Project Background**
            * **Company Profile:** A fast-growing e-commerce startup that has been scaling operations since its first transaction in 2019 until now.
            * **Product Scale:** Manages an extensive portfolio covering 26 product categories and over 2,700 brand variations.
            * **Market Reach:** Recorded more than 100,000 transactions across 15 countries, serving a broad customer demographic (both male & female, aged 12–70).

            **Challenges**
            🎯**Data Scalability:** Rapidly growing data volumes demand optimized reporting architecture for efficient decision-making.
            🎯**Pipeline Requirements:** Need to build an automated data architecture from raw sources in Google BigQuery through ETL via Apache Airflow to final visualization.
            🎯**Retention Analysis:** Extracting insights from loyal customer patterns to actively minimize customer churn
            🎯**Real-Time Prediction:** Empowering the Head of Operational to monitor data in real-time and predict churn probabilities seamlessly.            
            
            **Solutions**
            ✨**Automated Data Pipeline:** Integrated Google BigQuery, Apache Airflow, and Streamlit Cloud to establish a fully automated and scheduled data pipeline.            
            ✨**Interactive Dashboard:** Delivered a flexible dashboard for detailed data exploration, unlocking deep insights without any manual file handling.

            **Results**
            ✅**200% Workflow Efficiency:** Drastically cut big data flow management time by shifting from manual coding to a fully automated pipeline for extraction, cleaning/transformation, GitHub pushing, and Streamlit deployment.
            ✅**Non-Technical Accessibility:** Analytics can now be easily utilized by non-technical users through interactive, real-time visualizations.
            ✅**Security & Scheduling Flexibility:** Deployed Apache Airflow directly on the server to ensure data security within a private cloud while enabling customizable automated scheduling based on business needs.
            ✅**AI-Powered Analyst Assistant:** Integrated a chatbot agent that serves as an analyst assistant, translating complex data into narrative explanations for flexible executive decision-making.
            """)


with tab1:
    # st.subheader("Descriptive Analytics Highlights")
    st.write("Descriptive analysis summarizes historical data to provide a clear "
    "and factual picture of what has already happened.")

    with st.container():
        curr_month_name = first_day_curr.strftime('%B %Y')
        prev_month_name = first_day_prev.strftime('%B %Y')
        st.info(f"{curr_month_name} vs {prev_month_name} Performance Summary")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.markdown("<div style='background-color:#262730; color:white; padding:5px; border-radius:3px; font-size:12px; font-weight:bold; text-align:center;'>TOTAL TRAFFIC</div>", unsafe_allow_html=True)
                st.metric(label="", value=f"{traffic_curr:,}", delta=f"{traffic_growth:.2f}%")
        with m2:
            with st.container(border=True):
                st.markdown("<div style='background-color:#262730; color:white; padding:5px; border-radius:3px; font-size:12px; font-weight:bold; text-align:center;'>NEW USERS</div>", unsafe_allow_html=True)
                st.metric(label="", value=f"{users_curr:,}", delta=f"{users_growth:.2f}%")
        with m3:
            with st.container(border=True):
                st.markdown("<div style='background-color:#262730; color:white; padding:5px; border-radius:3px; font-size:12px; font-weight:bold; text-align:center;'>COMPLETE RATE</div>", unsafe_allow_html=True)
                st.metric(label="", value=f"{perf_curr:.0f}%", delta=f"{perf_diff:+.2f}%")
        with m4:
            with st.container(border=True):
                st.markdown("<div style='background-color:#262730; color:white; padding:5px; border-radius:3px; font-size:12px; font-weight:bold; text-align:center;'>SALES</div>", unsafe_allow_html=True)
                st.metric(label="", value=f"{sales_curr:,}", delta=f"{sales_growth:.2f}%")

    # st.divider()

    st.info("All Time Statistics")
    col1, col2 = st.columns([1,1.5])
    with col1:
        st.plotly_chart(fig_1, use_container_width=True)
    with col2:
        st.plotly_chart(fig_2, use_container_width=True)

    col3, col4 = st.columns([1,1.5])
    with col3:
        st.plotly_chart(fig_3, use_container_width=True)
    with col4:
        st.plotly_chart(fig_4, use_container_width=True)

    st.plotly_chart(fig_5, use_container_width=True)

with tab3:
    st.subheader("Displaying Dataset of Customer Order")

    # col_f1, col_f2 = st.columns(2)

    # with col_f1:
    #     check_one_country = st.toggle('Filter by Country')
    #     list_negara = sorted(df_vis['country'].unique())
    #     input_country = st.multiselect(
    #         'Select country/countries',
    #         options=list_negara,
    #         default=[list_negara[0]]
    #         )
        
    # with col_f2:
    #     toggle_status = st.toggle('Filter by Status')
    #     input_status = st.radio(
    #         'Input status of delivery',
    #         ('Complete','Returned','Cancelled','Shipped',
    #         'Processing'), horizontal=True
    #         )
    
    df_filtered['created_at'] = pd.to_datetime(df_vis['created_at'], format='ISO8601')
    df_filtered['created_at'] = df_filtered['created_at'].dt.date

    # logic
    # df_filtered = df_vis.copy()

    # if check_one_country and input_country:
    #     df_filtered = df_filtered.query('country in @input_country')
    # if toggle_status:
    #     df_filtered = df_filtered.query('status == @input_status')

    st.write(f"Showing **{len(df_filtered)}** rows")
    st.dataframe(df_filtered, use_container_width=True)


with tab2:
    # st.subheader("Diagnostic Analytics: Root Cause Discovery")
    # st.markdown("Fokus pada identifikasi pola kegagalan transaksi dan anomali kategori.")
    st.write("Diagnostic analysis investigates data to find the root cause and " \
    "explain the specific reasons **why** something happened.")
    st.header("1. Product Returns")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("#### Most Returned Category")
        cat_return = df_filtered.groupby('category')['is_returned'].mean().sort_values(ascending=False).reset_index()
        cat_return.columns= ['Category', 'Return Rate']
        st.dataframe(cat_return.style.background_gradient(cmap='Reds', subset=['Return Rate']))
    
    with col2:
    # Diagnostik: Apakah usia pelanggan berpengaruh pada kecenderungan mengembalikan barang?
        fig_age_return = px.histogram(
            df_filtered, x="age", color="status", 
            marginal="box", 
            title="Age Distribution vs Order Status",
            barmode="overlay"
        )

        fig_age_return.update_layout(
        xaxis_title='Age',
        yaxis_title='Order Total',
        title_font_size=25
        )

        st.plotly_chart(fig_age_return, use_container_width=True)

    st.divider()

    ## 
    st.header("2. Price Impact on Order Success")

    fig_price_diag = px.box(
        df_filtered, x='status', y='sale_price',
        color='gender',
        notched=True,
        title="Analysis of Price Variance by Order Status"
    )

    fig_price_diag.update_layout(
        xaxis_title='Status',
        yaxis_title='Sale Price',
        height=700,
        width=900,
        margin=dict(l=50, r=50, t=100, b=50),
        title_font_size=25
    )

    st.plotly_chart(fig_price_diag, use_container_width=True)
    st.info(f"""
    💡 **Insight:** 
     * A higher median price in 'Returned' versus 'Complete' orders suggests that high costs might be a primary driver of customer hesitation after purchase.
     """)

    st.divider()

    ##
    st.header("3. Traffic vs Brand Performance")
    selected_cat = st.selectbox("Choose Category", df_filtered['category'].unique())
    diag_sub_df = df_filtered[df_filtered['category'] == selected_cat]

    pivot_diag = diag_sub_df.pivot_table(
        index= 'traffic_source',
        columns= 'gender',
        values= 'is_returned',
        aggfunc= 'mean'
    )

    fig_heatmap = px.imshow(
        pivot_diag, 
        labels=dict(x="Gender", y="Traffic Source", color="Return Rate"),
        title=f"Heatmap Return Rate: {selected_cat} (Segment Risk Diagnosis)",
        text_auto=True,
        color_continuous_scale='RdBu_r'
    )

    fig_heatmap.update_layout(
        height=700,
        width=900,
        margin=dict(l=50, r=50, t=100, b=50),
        title_font_size=25
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.info(f"""  
    This heatmap identifies high-risk segments by analyzing the **Return Rate** across different traffic sources and genders. 
    * **Darker/Red cells** indicate critical segments with high return rates. 
    * **Blue/Cooler cells** represent stable segments with healthy conversion to successful delivery rate.
    """)

    st.divider()

    ##
    st.header("4. Top High Risk Brands")
    st.write("Mendiagnosis merek mana yang memiliki rasio pengembalian tidak wajar (minimal 50 transaksi).")

    brand_stats = df_filtered.groupby('brand').agg(
        total_orders= ('id','count'),
        return_rate= ('is_returned', 'mean')
    ).reset_index()

    high_risk_brands = brand_stats[brand_stats['total_orders'] > 30].sort_values('return_rate', ascending=False).head(10)

    fig_brands = px.scatter(
    high_risk_brands, x="total_orders", y="return_rate",
    text="brand", size="total_orders", color="return_rate",
    color_continuous_scale="RdBu_r",
    title="Brand with Highest Returned Risk"
    )
    
    fig_brands.update_layout(
        xaxis_title= 'Total Order',
        yaxis_title= 'Return Rate',
        height=700,
        width=900,
        margin=dict(l=50, r=50, t=100, b=50),
        title_font_size=25
    )
    fig_brands.update_traces(textposition='top center')
    st.plotly_chart(fig_brands, use_container_width=True)

    st.info(f""" 
    This visualization maps brands based on their **Total Orders** (X-axis) and **Return Rate** (Y-axis) to identify performance outliers.

    * 🔴 **High-Intensity (Red/Top)**: Represents brands with elevated return risks. Brands in this zone require closer inspection.
    * 🔵 **Low-Intensity (Blue/Bottom)**: Represents brands maintaining a **healthy conversion to successful delivery ratio**, showing high customer satisfaction.
    * ⚪ **Bubble Size**: Indicates the relative volume of orders.
    """)
