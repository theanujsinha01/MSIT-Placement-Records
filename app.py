

import streamlit as st
import pandas as pd
import plotly.express as px

# Page title and icon
st.set_page_config(
    page_title='MSIT Placement Records',
    page_icon='📈',
    layout='wide'
)

# Load or initialize data
DATA_FILE = "placement_records.csv"
ADMIN_CREDENTIALS = {"admin": "password123"}  # Change this to secure login

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Year", "Company", "Package", "Branch", "Placed_Students"])

def save_data(data):
    data.to_csv(DATA_FILE, index=False)

data = load_data()

# Sidebar Styling
st.sidebar.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #f4f4f4;
        }
    </style>
    """, unsafe_allow_html=True)

# Admin Authentication
st.sidebar.header("🔒 Admin Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")
logout_button = st.sidebar.button("Logout")

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if login_button:
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        st.session_state.admin_logged_in = True
        st.sidebar.success("Logged in as Admin")
    else:
        st.sidebar.error("Invalid credentials")

if logout_button:
    st.session_state.admin_logged_in = False
    st.sidebar.info("Logged out")

# Sidebar filters
st.sidebar.header("🎯 Filters")
year_filter = st.sidebar.multiselect("Select Year", options=sorted(data["Year"].unique()))
branch_filter = st.sidebar.multiselect("Select Branch", options=sorted(data["Branch"].unique()))

# Apply filters
filtered_data = data
if year_filter:
    filtered_data = filtered_data[filtered_data["Year"].isin(year_filter)]
if branch_filter:
    filtered_data = filtered_data[filtered_data["Branch"].isin(branch_filter)]

# Main UI
st.title(':rainbow[ MSIT Placement Records]')
st.subheader(':gray[Placement Statistics]', divider='rainbow')

st.dataframe(filtered_data, use_container_width=True)

# Display filtered data
if not filtered_data.empty:
    st.subheader("📊 Placement Insights: Package vs Students Placed")
    chart_type = st.selectbox("📊 Select Chart Type", ["Bar Chart", "Pie Chart", "Box Plot"], key='chart_select')

    # Define package ranges for better grouping
    bins = [0, 5, 10, 20, 50, 100]
    labels = ["<5 LPA", "5-10 LPA", "10-20 LPA", "20-50 LPA", "50+ LPA"]
    filtered_data["Package Range"] = pd.cut(filtered_data["Package"], bins=bins, labels=labels)

    if chart_type == "Bar Chart":
        fig = px.bar(filtered_data, x="Package Range", y="Placed_Students", color="Year", barmode="group", title="Number of Students Placed at Different Salary Ranges")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie Chart":
        fig = px.pie(filtered_data, names="Package Range", values="Placed_Students", title="Distribution of Students by Package Range")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box Plot":
        fig = px.box(filtered_data, x="Year", y="Package", points="all", title="Package Distribution by Year")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No data available for selected filters.")
