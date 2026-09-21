import streamlit as st
import pandas as pd

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(page_title="COVID-19 Insights Dashboard", layout="wide")
st.title("COVID-19 Insights Dashboard")
st.markdown("""
This app demonstrates:
- Loading `uk_covid_clean.csv`
- Selecting a date range with a slider
- Toggling between daily cases, daily deaths, and vaccinations
- Plotting line charts (with optional 7‑day average)
""")

# ---------------------------
# Load data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        r"C:\Users\USER\Documents\Covid Insights Project\data\clean\uk_covid_clean.csv",
        parse_dates=["date"]
    )
    df = df.sort_values("date").reset_index(drop=True)
    return df

df = load_data()


# Optional raw data preview

if st.checkbox("Show raw data"):
    st.dataframe(df.head())


# Sidebar controls

st.sidebar.header("Controls")

# Date slider
min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.slider(
    label="Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Metric selector
metric = st.sidebar.radio(
    "Select metric to display",
    ("Daily Cases", "Daily Deaths", "Vaccinations"),
)

# Daily vs Yearly toggle
view = st.sidebar.radio(
    "View data by",
    ["Daily", "Yearly"]
)

# Optional checkboxes
rolling = st.sidebar.checkbox("Show 7-day rolling average", value=True)
show_table = st.sidebar.checkbox("Show data table", value=False)



# Filter data by selected date range

start = pd.to_datetime(date_range[0])
end = pd.to_datetime(date_range[1])
df_sel = df[(df["date"] >= start) & (df["date"] <= end)].copy()

# ---------------------------
# Map metric to CSV column
# ---------------------------
metric_map = {
    "Daily Cases": "new_cases",
    "Daily Deaths": "new_deaths",
    "Vaccinations": "new_vaccinations",
}
col = metric_map[metric]

# ---------------------------
# Summary stats
# ---------------------------
total_val = df_sel[col].sum()
avg_val = df_sel[col].mean()

st.markdown(
    f"""
    <div style='display:flex; gap: 20px'>
        <div style='background-color:#ffcccb; padding:10px; border-radius:10px; flex:1'>
            <h3>Total {metric}</h3>
            <h2>{int(total_val):,}</h2>
        </div>
        <div style='background-color:#cce5ff; padding:10px; border-radius:10px; flex:1'>
            <h3>Average {metric} per day</h3>
            <h2>{int(avg_val):,}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True
)

# ---------------------------
# Prepare chart data
# ---------------------------
if view == "Daily":
    df_sel = df_sel.set_index("date")
    series = df_sel[col].fillna(0)
    chart_df = pd.DataFrame({metric: series})
    if rolling:
        chart_df[f"{metric} (7d avg)"] = series.rolling(7, min_periods=1).mean()
    st.subheader(f"{metric} — Daily values ({start.date()} to {end.date()})")
    if chart_df.empty:
        st.info("No daily data available for the selected date range.")
    else:
        st.line_chart(chart_df)

else:  # Yearly view
    df_sel["year"] = df_sel["date"].dt.year
    yearly_data = df_sel.groupby("year")[col].sum().reset_index()
    st.subheader(f"{metric} — Yearly total ({start.date()} to {end.date()})")
    if yearly_data.empty:
        st.info("No yearly data available for the selected date range.")
    else:
        st.line_chart(yearly_data.rename(columns={col: metric}).set_index("year"))

# ---------------------------
# Show data table if requested
# ---------------------------
if show_table:
    st.markdown("**Underlying values**")
    if view == "Daily":
        st.dataframe(chart_df.reset_index())
    else:
        st.dataframe(yearly_data)
        
st.caption("Tip: use the sidebar to adjust the date range, metric, and view. Rolling average applies only to daily data.")
