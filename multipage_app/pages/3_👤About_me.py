import streamlit as st
import os

current_dir = os.path.dirname(__file__)


def set_office_bg():
    img_url = "https://images.unsplash.com/photo-1637946175559-22c4fe13fc54?q=80&w=627&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    # "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=765&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
    

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


st.set_page_config(page_title= "About Me", page_icon="👤")

col1, col2 = st.columns([1.08, 2], gap="medium")

with col1:
    image_path = os.path.join(current_dir, "..", "gambar", "DRK_6468.jpg")
    st.image(image_path, caption="Mochammad Reyhan Mauluddi")

with col2:
    st.title("About Me")
    st.subheader("Data Analytics Specialist")

    st.write("""
            In today’s data-heavy world, everyone has information, but very few have clear answers. 
             As a Quantitative Research and Data Analytics Specialist with over years of experience, 
             my career has been defined by a single mission: transforming complex, high-volume datasets 
             into the strategic blueprints that drive business solution. I specialize in the intersection of 
             mathematical precision and commercial intuition.
             """)
st.divider()

st.subheader("Hobbies and Interests")
st.write("""
         * **Sport**: Beyond the data, you’ll find me out for a run or a ride.
         * **Investment**: I actively explore investment opportunities in both physical assets and digital banking platforms.
         * **Data Analytics and AI**: Passionate about architecting end-to-end data solutions and diving deep into the world of 
         Generative AI to build smarter, data-driven systems.
         """)

st.subheader("Life Mission")
st.info("""
To build impactful data solutions using the latest technology and analytics while growing my career globally.
""")

st.divider()

st.subheader("Contact Me")
st.write("""
        If you're interested in discussing data projects or potential collaborations, 
         please feel free to reach out via:
         """)

contact_col1, contact_col2 = st.columns(2)
with contact_col1:
    st.write("📧 **Email:** [reyhanmauluddiin@gmail.com]")
with contact_col2:
    st.write("🔗 **LinkedIn:** [linkedin.com/in/reyhanmauluddi](https://www.linkedin.com)")
