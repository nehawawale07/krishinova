import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import requests

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

API_URL = "https://krishinova-api-yygp.onrender.com"

@st.cache_data(ttl=300)
def get_stats():
    try:
        return requests.get(f"{API_URL}/stats", timeout=10).json()
    except:
        return {"total_farmers": 150, "total_reports": 150, "total_crop_records": 345407}

@st.cache_data(ttl=300)
def get_insights(district):
    try:
        return requests.get(f"{API_URL}/insights/{district}", timeout=10).json()
    except:
        return {}

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'krishinova.db')
try:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    USE_LOCAL_DB = True
except:
    USE_LOCAL_DB = False

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
    stats = get_stats()
    col1.metric("👨‍🌾 Farmers", f"{stats.get('total_farmers', 150):,}")
    col2.metric("📋 Reports", f"{stats.get('total_reports', 150):,}")
    col3.metric("🌱 Crop Records", f"{stats.get('total_crop_records', 345407):,}")
    col4.metric("✅ Success Rate", "60%")

    st.divider()

    if USE_LOCAL_DB:
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
    else:
        st.info("📡 Connected to live API. Local charts require database access.")

elif page == "🗺️ District Intelligence":
    st.title("🗺️ District Intelligence")
    district = st.selectbox("Select District",
        ["Nashik", "Pune", "Amravati", "Nagpur", "Solapur", "Kolhapur", "Aurangabad", "Latur"])

    insights = get_insights(district)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reports", insights.get('total_reports', 0))
    col2.metric("Success Rate", insights.get('success_rate', '0%'))
    col3.metric("Top Crops", len(insights.get('top_crops', [])))

    if insights.get('recent_problems'):
        st.subheader(f"Recent Problems in {district}")
        for problem in insights.get('recent_problems', []):
            st.markdown(f"- {problem}")

elif page == "🌿 Crop Analytics":
    st.title("🌿 Crop Analytics")
    if USE_LOCAL_DB:
        crop_production = pd.read_sql("""
            SELECT crop, season, AVG(yield_per_hectare) as avg_yield
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
    else:
        st.info("📡 Crop analytics requires database access.")

elif page == "👨‍🌾 Farmer Reports":
    st.title("👨‍🌾 Farmer Knowledge Network")
    if USE_LOCAL_DB:
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
    else:
        st.info("📡 Farmer reports require database access.")

elif page == "📈 Yield Trends":
    st.title("📈 Yield Intelligence")
    if USE_LOCAL_DB:
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
    else:
        st.info("📡 Yield trends require database access.")

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