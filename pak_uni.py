import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Pakistani Universities",
    layout="wide"
)
def get_current_theme():
    bg_color = st.get_option("theme.backgroundColor")
    if bg_color and bg_color.lower() in ["#0e1117", "#1e1e1e", "#000000"]:
        return "dark"
    return "light"

current_theme = get_current_theme()
font_color = "#ffffff" if current_theme == "dark" else "#000000"
link_color = "#00ff99" if current_theme == "dark" else "green"


# Load data
df = pd.read_csv("universities.csv")

# ------------------------------- Sidebar Layout ----------------------------------- #
with st.sidebar:
    # Load and resize banner image
    banner = Image.open("logo.png")
    st.image(banner, use_container_width=False, width=200)

    st.markdown("""
    <div style='margin-bottom: -10px;'>
    <h4 style='font-size: 20px; text-align:center; margin-bottom: -20px;'>By Hassan Raza</h4>
    <h4 style='font-size: 10px; text-align:center;'>Data Scientist | Dashboard Specialist</h4>
    </div>
    <hr style='margin: 15px;'>
    """, unsafe_allow_html=True)
    
#----------------------------- 🔍 Filters-----------------------------------------#

    st.markdown("""
    <div style='margin-bottom: -30px;'>
        <span style='font-size:14px;'>Province</span>
    </div>
    """, unsafe_allow_html=True)
    province = st.selectbox("", options=["All"] + sorted(df["Province"].dropna().unique().tolist()), key="province")

    st.markdown("""
    <div style='margin-bottom: --30px;'>
        <span style='font-size:14px;'>Sector</span>
    </div>
    """, unsafe_allow_html=True)
    sector = st.selectbox("", options=["All", "Public", "Private"], key="sector")
    
    st.markdown("""
    <div style='margin-bottom: -30px;'>
        <span style='font-size:14px;'>City</span>
    </div>""", unsafe_allow_html=True)
    
    if province == "All":
        city_options = sorted(df["City"].dropna().unique().tolist())
    else:
        city_options = sorted(df[df["Province"] == province]["City"].dropna().unique().tolist())

    city = st.selectbox("", options=["All"] + city_options, key="city")
        
        
#-----------------------------  Apply Filters ------------------------------------- #
filtered_df = df.copy()
if province != "All":
    filtered_df = filtered_df[filtered_df["Province"] == province]
    
if city != "All":
    filtered_df = filtered_df[filtered_df["City"] == city]

if sector != "All":
    filtered_df = filtered_df[filtered_df["Sector"] == sector]


#-----------------------------  Main Page Content -------------------------------- #
st.markdown("""
    <h2 style='font-size: 28px; margin-bottom: 5px; text-align: center;'>All Pakistan Universities</h2>
    <p style='font-size: 14px; color: gray;'>Interactive insights and search for HEC-listed universities in Pakistan.</p>
    <hr style='margin-top: 0;'>
""", unsafe_allow_html=True)

#-------------------------------- Summary Stats ----------------------------------- #
st.markdown("<h4 style='font-size: 20px;'>📈 Summary Stats</h4>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", filtered_df.shape[0])
col2.metric("Public", filtered_df[filtered_df["Sector"]=="Public"].shape[0])
col3.metric("Private", filtered_df[filtered_df["Sector"]=="Private"].shape[0])
distance_unis = filtered_df[filtered_df["Distance Education"]=="Yes"]["University Name"].tolist()
distance_label = distance_unis[0] if len(distance_unis) == 1 else f"{len(distance_unis)} Universities"
col4.markdown(f"<p style='font-size:14px;'>Distance Ed.</p>", unsafe_allow_html=True)
col4.markdown(f"<h6 style='font-size:18px; color:#444; margin-top:-10px'>{distance_label}</h6>", unsafe_allow_html=True)

# --------------------------------- Insights Charts ------------------------- #
st.markdown("<h4 style='font-size: 20px;'><br><br>📊 Insights</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2.5])

# --- col1: Province-wise Bar Chart --- #
with col1:
    province_counts = filtered_df["Province"].value_counts().reset_index()
    province_counts.columns = ["Province", "Count"]
    province_fig = px.bar(
        province_counts,
        x="Province",
        y="Count",
        text="Count",
        title="Province-wise University Count",
        color="Count",
        color_continuous_scale="Plasma"
    )
    province_fig.update_traces(textposition="auto", textfont_size=6)
    province_fig.update_layout(margin=dict(t=40, b=20, l=10, r=10), height=350)
    st.plotly_chart(province_fig, use_container_width=True)

# --- col2: Sector-wise Pie Chart --- #
with col2:
    sector_counts = filtered_df["Sector"].value_counts().reset_index()
    sector_counts.columns = ["Sector", "Count"]
    sector_fig = px.pie(
        sector_counts,
        names="Sector",
        values="Count",
        title="Sector-wise Distribution",
        color_discrete_sequence=["#1f77b4", "#ac89cc"]
    )
    sector_fig.update_traces(textfont_size=9)
    sector_fig.update_layout(margin=dict(t=40, b=20, l=80, r=10), height=350)
    st.plotly_chart(sector_fig, use_container_width=True)

# --- col3: Established Timeline Chart --- #
with col3:
    filtered_df["Established Since"] = pd.to_datetime(filtered_df["Established Since"], errors="coerce")
    filtered_df["Year"] = filtered_df["Established Since"].dt.year
    established_counts = filtered_df["Year"].value_counts().sort_index().reset_index()
    established_counts.columns = ["Year", "Count"]
    timeline_fig = px.line(
        established_counts,
        x="Year",
        y="Count",
        markers=True,
        title="Universities Established Over Time"
    )
    timeline_fig.update_traces(
    line=dict(
        color= '#c084f5',      
        width=1.5,
        dash='dot',         
        shape='spline'      
    ),
    marker=dict(size=6, color='#6a0dad') 
    )

    timeline_fig.update_layout(margin=dict(t=40, b=20, l=10, r=10), height=350)
    st.plotly_chart(timeline_fig, use_container_width=True)

# ---------------------------- University Browser --------------------------------- #
st.markdown("<h4 style='font-size: 20px;'><br><br>🔎 University Browser</h4>", unsafe_allow_html=True)

# Clean spaces
for col in ["University Name", "City", "Province", "Sector", "Chartered By", "Website"]:
    filtered_df[col] = filtered_df[col].astype(str).str.strip()

# Format Website column
df_display = filtered_df[["University Name", "City", "Province", "Sector", "Chartered By", "Website"]].copy()
df_display["Website"] = df_display["Website"].apply(lambda url: f"<a href='{url}' target='_blank' style='color: green; text-decoration: none;'>{url}</a>")

# CSS for scrollable box
st.markdown("""
    <style>
    .scrollable-table-container {
        max-height: 480px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 10px;
    }
    .scrollable-table-container table {
        width: 100%;
        font-size: 14px;
        table-layout: fixed;
    }
    .scrollable-table-container th, .scrollable-table-container td {
        padding: 6px 8px;
        text-align: left;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 160px;
    }
    .scrollable-table-container th:nth-child(1),
    .scrollable-table-container td:nth-child(1) {
        max-width: 180px;  /* University Name */
    }
    .scrollable-table-container th:nth-child(6),
    .scrollable-table-container td:nth-child(6) {
        max-width: 200px;  /* Website */
    }
    </style>
""", unsafe_allow_html=True)

# Scrollable HTML table inside container
st.markdown(
    f"<div class='scrollable-table-container'>{df_display.to_html(escape=False, index=False)}</div>",
    unsafe_allow_html=True)
