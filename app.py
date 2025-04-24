import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Asset Dashboard", layout="wide")

st.title("📊 Asset Management Dashboard")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, skiprows=1)
    df.columns = df.columns.str.strip()

    try:
        df['Date Placed in Service'] = pd.to_datetime(df['Date Placed in Service'], errors='coerce')
    except:
        st.warning("Date format issue")

    # Filters
    city = st.multiselect("Filter by City", options=sorted(df['City'].dropna().unique()), default=None)
    major = st.multiselect("Filter by Major Category", options=sorted(df['Major Category Desp'].dropna().unique()), default=None)

    if city:
        df = df[df['City'].isin(city)]
    if major:
        df = df[df['Major Category Desp'].isin(major)]

    # KPIs
    st.metric("Total Asset Cost", f"{df['Asset Cost'].sum():,.0f}")
    st.metric("Total Depreciation", f"{df['Depreciation Reserve'].sum():,.0f}")
    st.metric("Net Book Value", f"{df['Net Book Value'].sum():,.0f}")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(df, x='Major Category Desp', y='Asset Cost', color='Major Category Desp',
                      title='Asset Cost by Major Category')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(df, names='City', values='Asset Cost', title='Asset Distribution by City')
        st.plotly_chart(fig2, use_container_width=True)

    # Time chart
    timeline = (
        df.groupby(df['Date Placed in Service'].dt.to_period("M"))
        .size().reset_index(name='Asset Count')
    )
    timeline['Date'] = timeline['Date Placed in Service'].dt.to_timestamp()
    fig3 = px.line(timeline, x='Date', y='Asset Count', title='Assets Over Time')
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Upload an Excel file to begin.")
