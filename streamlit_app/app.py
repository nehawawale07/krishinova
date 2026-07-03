import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import sys

st.set_page_config(
    page_title="KrishiNova Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    h1, h2, h3 { color: #D4A017; }
</style>
""", unsafe_allow_html=True)

# DB connection — works both locally and on Streamlit Cloud
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'krishinova.db')

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

try:
    conn = get_connection()
except:
    st.error("Database not found. Make sure krishinova.db is in the backend folder.")
    st.stop()

st.sidebar.image("https://img.icons8.com/emoji/96/seedling.png", width=80)
st.sidebar.title("🌾 KrishiNova")
st.sidebar.markdown("**Hyperlocal Farmer Intelligence Network**")
st.sidebar.divider()

page = st.sidebar.selectbox("Navigate", [
    "📊 Overview Dashboard",
    "🗺️ District Intelligence",
    "🌿 Crop Analytics",
    "👨‍🌾 Farmer Reports",
    "📈 Yield Trends",
    "🕸️ Knowledge Graph"
])

if page == "📊 Overview Dashboard":
    st.title("🌾 KrishiNova — Farm Intelligence Dashboard")
    st.markdown("*Real-time insights from Maharashtra's farmer knowledge network*")

    col1, col2, col3, col4 = st.columns(4)
    total_farmers = pd.read_sql("SELECT COUNT(*) as count FROM farmers", conn).iloc[0]['count']
    total_reports = pd.read_sql("SELECT COUNT(*) as count FROM farmer_reports", conn).iloc[0]['count']
    total_crops = pd.read_sql("SELECT COUNT(*) as count FROM crop_data", conn).iloc[0]['count']
    success_count = pd.read_sql("SELECT COUNT(*) as count FROM farmer_reports WHERE outcome='success'", conn).iloc[0]['count']

    col1.metric("👨‍🌾 Farmers", f"{total_farmers:,}")
    col2.metric("📋 Reports", f"{total_reports:,}")
    col3.metric("🌱 Crop Records", f"{total_crops:,}")
    col4.metric("✅ Success Rate", f"{round(success_count/total_reports*100)}%")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Reports by District")
        district_data = pd.read_sql("""
            SELECT district, COUNT(*) as reports,
            SUM(CASE WHEN outcome='success' THEN 1 ELSE 0 END) as successes
            FROM farmer_reports GROUP BY district ORDER BY reports DESC
        """, conn)
        fig = px.bar(district_data, x='district', y='reports',
                    color='successes', color_continuous_scale='Greens')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌿 Crop Distribution")
        crop_data = pd.read_sql("SELECT crop, COUNT(*) as count FROM farmer_reports GROUP BY crop", conn)
        fig = px.pie(crop_data, values='count', names='crop',
                    color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Outcome Distribution")
        outcome_data = pd.read_sql("SELECT outcome, COUNT(*) as count FROM farmer_reports GROUP BY outcome", conn)
        fig = px.pie(outcome_data, values='count', names='outcome',
                    color_discrete_map={'success': '#2D6A4F', 'failure': '#D62828', 'partial': '#D4A017'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌱 Season Analysis")
        season_data = pd.read_sql("""
            SELECT season, COUNT(*) as reports,
            SUM(CASE WHEN outcome='success' THEN 1 ELSE 0 END) as successes
            FROM farmer_reports GROUP BY season
        """, conn)
        fig = px.bar(season_data, x='season', y=['reports', 'successes'],
                    barmode='group', color_discrete_sequence=['#2D6A4F', '#D4A017'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

elif page == "🗺️ District Intelligence":
    st.title("🗺️ District Intelligence")
    district = st.selectbox("Select District",
        ["Nashik", "Pune", "Amravati", "Nagpur", "Solapur", "Kolhapur", "Aurangabad", "Latur"])

    reports = pd.read_sql(f"SELECT * FROM farmer_reports WHERE district='{district}'", conn)
    success = len(reports[reports['outcome'] == 'success'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reports", len(reports))
    col2.metric("Success Rate", f"{round(success/len(reports)*100) if len(reports) > 0 else 0}%")
    col3.metric("Crops Tracked", reports['crop'].nunique())

    st.subheader(f"Common Problems in {district}")
    for _, row in reports.head(5).iterrows():
        with st.expander(f"🌿 {row['crop']} — {row['outcome'].upper()}"):
            st.write(f"**Problem:** {row['problem']}")
            st.write(f"**Solution:** {row['solution']}")
            st.write(f"**Soil:** {row['soil_type']} | **Season:** {row['season']}")

elif page == "🌿 Crop Analytics":
    st.title("🌿 Crop Analytics")
    crop_production = pd.read_sql("""
        SELECT crop, season, AVG(yield_per_hectare) as avg_yield, COUNT(*) as records
        FROM crop_data WHERE state = 'Maharashtra'
        GROUP BY crop, season ORDER BY avg_yield DESC LIMIT 20
    """, conn)

    if crop_production.empty:
        crop_production = pd.read_sql("""
            SELECT crop, season, AVG(yield_per_hectare) as avg_yield
            FROM crop_data GROUP BY crop, season
            ORDER BY avg_yield DESC LIMIT 20
        """, conn)

    fig = px.bar(crop_production, x='crop', y='avg_yield', color='season',
                barmode='group', title="Average Yield by Crop and Season",
                color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(crop_production, use_container_width=True)

elif page == "👨‍🌾 Farmer Reports":
    st.title("👨‍🌾 Farmer Knowledge Network")
    col1, col2 = st.columns(2)
    crop_filter = col1.selectbox("Filter by Crop",
        ["All", "Onion", "Soybean", "Cotton", "Sugarcane", "Wheat", "Rice", "Tur Dal", "Jowar"])
    outcome_filter = col2.selectbox("Filter by Outcome", ["All", "success", "failure", "partial"])

    query = "SELECT f.name, fr.* FROM farmer_reports fr JOIN farmers f ON f.id = fr.farmer_id WHERE 1=1"
    if crop_filter != "All":
        query += f" AND fr.crop = '{crop_filter}'"
    if outcome_filter != "All":
        query += f" AND fr.outcome = '{outcome_filter}'"

    reports = pd.read_sql(query, conn)
    st.markdown(f"**Showing {len(reports)} reports**")

    for _, row in reports.iterrows():
        color = "🟢" if row['outcome'] == 'success' else "🔴" if row['outcome'] == 'failure' else "🟡"
        with st.expander(f"{color} {row['name']} — {row['crop']} ({row['district']})"):
            st.write(f"**Problem:** {row['problem']}")
            st.write(f"**Solution:** {row['solution']}")
            st.write(f"**Soil:** {row['soil_type']} | **Season:** {row['season']}")

elif page == "📈 Yield Trends":
    st.title("📈 Yield Intelligence")
    top_crops = pd.read_sql("""
        SELECT crop, SUM(production) as total_production
        FROM crop_data GROUP BY crop ORDER BY total_production DESC LIMIT 10
    """, conn)
    fig = px.bar(top_crops, x='crop', y='total_production',
                title="Top 10 Crops by Total Production",
                color='total_production', color_continuous_scale='Greens')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    state_data = pd.read_sql("""
        SELECT state, SUM(production) as total_production
        FROM crop_data GROUP BY state ORDER BY total_production DESC LIMIT 15
    """, conn)
    fig2 = px.bar(state_data, x='state', y='total_production',
                 title="Production by State",
                 color='total_production', color_continuous_scale='Greens')
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

elif page == "🕸️ Knowledge Graph":
    st.title("🕸️ Farmer Knowledge Graph")
    st.markdown("*Live network of crops, districts, soils and outcomes*")

    col1, col2, col3 = st.columns(3)
    col1.metric("🔵 Total Nodes", "21")
    col2.metric("🔗 Connections", "103")
    col3.metric("👨‍🌾 Reports Mapped", "150")

    st.divider()
    graph_path = os.path.join(os.path.dirname(__file__), 'knowledge_graph.html')
    if os.path.exists(graph_path):
        with open(graph_path, 'r', encoding='utf-8') as f:
            html = f.read()
        st.components.v1.html(html, height=620, scrolling=False)
    else:
        st.info("Knowledge graph will appear here once generated.")

st.sidebar.divider()
st.sidebar.markdown("*Built with ❤️ for Indian farmers*")
st.sidebar.markdown("**KrishiNova v1.0** | Maharashtra")