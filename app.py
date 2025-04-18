import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page setup
st.set_page_config(page_title="MSIT Placement Records", page_icon="📈", layout="wide")

# File path
DATA_FILE = "placement_records.csv"

# Admin credentials
ADMIN_CREDENTIALS = {"admin@msit.in": "Password"}

# Load CSV
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Year", "Company", "Package", "Branch", "Placed_Students"])

# Save CSV
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Load data
data = load_data()

# Sidebar Login
st.sidebar.header("Admin Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")
logout_btn = st.sidebar.button("Logout")

# Session state
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if login_btn:
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        st.session_state.admin_logged_in = True
        st.sidebar.success("Login Successful ✅")
    else:
        st.sidebar.error("Wrong credentials ❌")

if logout_btn:
    st.session_state.admin_logged_in = False
    st.sidebar.info("Logged Out")

# Filters
st.sidebar.header("Filters")
year_filter = st.sidebar.multiselect("Select Year", options=sorted(data["Year"].unique()))
branch_filter = st.sidebar.multiselect("Select Branch", options=sorted(data["Branch"].unique()))

filtered_data = data.copy()
if year_filter:
    filtered_data = filtered_data[filtered_data["Year"].isin(year_filter)]
if branch_filter:
    filtered_data = filtered_data[filtered_data["Branch"].isin(branch_filter)]

# Package range
bins = [0, 5, 10, 15, 20, float('inf')]
labels = ['0-5 LPA', '5-10 LPA', '10-15 LPA', '15-20 LPA', '20+ LPA']
filtered_data["Package Range"] = pd.cut(filtered_data["Package"], bins=bins, labels=labels, right=False)

# Main Title
st.title("📊 MSIT Placement Records Dashboard")

# Show Data Table
st.dataframe(filtered_data, use_container_width=True)

# Metrics
if not filtered_data.empty:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Placed", int(filtered_data["Placed_Students"].sum()))
    col2.metric("Avg Package", f"{filtered_data['Package'].mean():.2f}")
    col3.metric("Median Package", f"{filtered_data['Package'].median():.2f}")
    col4.metric("Min Package", f"{filtered_data['Package'].min():.2f}")
    col5.metric("Max Package", f"{filtered_data['Package'].max():.2f}")
    col6.metric("Total Companies", filtered_data["Company"].nunique())

    st.subheader("📈 Package Range vs Students Placed")
    fig1 = px.pie(filtered_data, names="Package Range", values="Placed_Students", title="Package Range")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🏫 Branch vs Students Placed")
    fig2 = px.pie(filtered_data, names="Branch", values="Placed_Students", title="Branch Distribution")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available for selected filters.")

# Admin Panel
if st.session_state.admin_logged_in:
    st.subheader("🔐 Admin Panel - Add New Record")

    year = st.number_input("Year", min_value=2000, max_value=2050, step=1)
    company = st.text_input("Company")
    package = st.number_input("Package (in LPA)", min_value=0.0, step=0.1)
    branch = st.text_input("Branch")
    placed_students = st.number_input("Placed Students", min_value=0, step=1)

    if st.button("Add Record"):
        new_row = pd.DataFrame({
            "Year": [year],
            "Company": [company],
            "Package": [package],
            "Branch": [branch],
            "Placed_Students": [placed_students]
        })

        updated_data = pd.concat([data, new_row], ignore_index=True)
        save_data(updated_data)
        st.success("✅ Record added and saved in CSV!")



