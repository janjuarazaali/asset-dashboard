
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Asset Dashboard", layout="wide")
st.title("📊 Asset Management Dashboard")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

def numeric_filter_ui(col_name, df):
    min_val, max_val = float(df[col_name].min()), float(df[col_name].max())
    return st.slider(f"{col_name} range", min_val, max_val, (min_val, max_val))

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df['Date Placed in Service'] = pd.to_datetime(df['Date Placed in Service'], errors='coerce')
    
    st.sidebar.header("🔍 Search or Filter")
    search_asset = st.sidebar.text_input("Search by Asset Number")
    
    if search_asset:
        result = df[df['Asset Number'].astype(str).str.contains(search_asset)]
        st.subheader("🔎 Search Result")
        st.dataframe(result)
    else:
        city = st.sidebar.multiselect("City", df['City'].dropna().unique())
        office = st.sidebar.multiselect("Office or Warehouse", df['Office or Warehouse'].dropna().unique())
        major = st.sidebar.multiselect("Major Category", df['Major Category Desp'].dropna().unique())
        minor = st.sidebar.multiselect("Minor Category", df['Minor Category Desp'].dropna().unique())
        desc = st.sidebar.multiselect("Asset Description", df['Asset Description'].dropna().unique())
        date_range = st.sidebar.date_input("Date Placed in Service Range", [])
        
        cost_min, cost_max = numeric_filter_ui("Asset Cost", df)
        nbv_min, nbv_max = numeric_filter_ui("Net Book Value", df)
        life_min, life_max = numeric_filter_ui("Remaining Life", df)

        filtered_df = df.copy()
        if city: filtered_df = filtered_df[filtered_df['City'].isin(city)]
        if office: filtered_df = filtered_df[filtered_df['Office or Warehouse'].isin(office)]
        if major: filtered_df = filtered_df[filtered_df['Major Category Desp'].isin(major)]
        if minor: filtered_df = filtered_df[filtered_df['Minor Category Desp'].isin(minor)]
        if desc: filtered_df = filtered_df[filtered_df['Asset Description'].isin(desc)]
        if date_range and len(date_range) == 2:
            filtered_df = filtered_df[(filtered_df['Date Placed in Service'] >= pd.to_datetime(date_range[0])) & 
                                      (filtered_df['Date Placed in Service'] <= pd.to_datetime(date_range[1]))]
        filtered_df = filtered_df[(filtered_df['Asset Cost'] >= cost_min) & (filtered_df['Asset Cost'] <= cost_max)]
        filtered_df = filtered_df[(filtered_df['Net Book Value'] >= nbv_min) & (filtered_df['Net Book Value'] <= nbv_max)]
        filtered_df = filtered_df[(filtered_df['Remaining Life'] >= life_min) & (filtered_df['Remaining Life'] <= life_max)]

        st.subheader("📄 Filtered Asset Data")
        st.dataframe(filtered_df)

        st.download_button("📥 Download Filtered Data", data=filtered_df.to_csv(index=False), file_name="filtered_assets.csv")

        st.subheader("📈 Summary KPIs")
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Asset Cost", f"{filtered_df['Asset Cost'].sum():,.0f}")
        kpi2.metric("Total Depreciation", f"{filtered_df['Depreciation Reserve'].sum():,.0f}")
        kpi3.metric("Net Book Value", f"{filtered_df['Net Book Value'].sum():,.0f}")

        st.subheader("📊 Charts")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.bar(filtered_df, x="Major Category Desp", y="Asset Cost", title="Asset Cost by Major Category"), use_container_width=True)
            st.plotly_chart(px.bar(filtered_df, x="Minor Category Desp", y="Asset Cost", title="Asset Cost by Minor Category"), use_container_width=True)
        with col2:
            st.plotly_chart(px.bar(filtered_df, x="City", y="Asset Cost", title="Asset Cost by City"), use_container_width=True)
            st.plotly_chart(px.bar(filtered_df, x="Office or Warehouse", y="Asset Cost", title="Asset Cost by Office/Warehouse"), use_container_width=True)
        
        time_df = filtered_df.dropna(subset=["Date Placed in Service"])
        time_df = time_df.groupby(time_df["Date Placed in Service"].dt.to_period("M")).agg({
            "Asset Cost": "sum",
            "Asset Number": "count"
        }).reset_index()
        time_df["Date"] = time_df["Date Placed in Service"].dt.to_timestamp()
        st.plotly_chart(px.line(time_df, x="Date", y="Asset Cost", markers=True, title="Asset Cost Over Time"), use_container_width=True)
        st.plotly_chart(px.line(time_df, x="Date", y="Asset Number", markers=True, title="Asset Count Over Time"), use_container_width=True)
else:
    st.info("📤 Upload an Excel file to begin.")
