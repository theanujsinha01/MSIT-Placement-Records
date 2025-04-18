import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='MSIT Placement Records', page_icon='📈', layout='wide')

# File path
DATA_FILE = "placement_records.csv"

# Admin credentials
ADMIN_CREDENTIALS = {"admin@msit.in": "Password"}

# Load and Save
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Year", "Company", "Package", "Branch", "Placed_Students"])

def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Session state
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "data" not in st.session_state:
    st.session_state.data = load_data()

# Sidebar login
st.sidebar.header("Admin Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")
logout_button = st.sidebar.button("Logout")

if login_button:
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        st.session_state.admin_logged_in = True
        st.sidebar.success("Logged in")
    else:
        st.sidebar.error("Incorrect username or password")
if logout_button:
    st.session_state.admin_logged_in = False

# Filters
st.sidebar.header("Filters")
data = st.session_state.data
year_filter = st.sidebar.multiselect("Select Year", sorted(data["Year"].unique()))
branch_filter = st.sidebar.multiselect("Select Branch", sorted(data["Branch"].unique()))

filtered_data = data.copy()
if year_filter:
    filtered_data = filtered_data[filtered_data["Year"].isin(year_filter)]
if branch_filter:
    filtered_data = filtered_data[filtered_data["Branch"].isin(branch_filter)]

# Package Range
bins = [0, 5, 10, 15, 20, float('inf')]
labels = ['0-5 LPA', '5-10 LPA', '10-15 LPA', '15-20 LPA', '20+ LPA']
filtered_data["Package Range"] = pd.cut(filtered_data["Package"], bins=bins, labels=labels, right=False)

# Display
st.title("MSIT Placement Records")
st.dataframe(filtered_data, use_container_width=True)

# Metrics
if not filtered_data.empty:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Placed", filtered_data["Placed_Students"].sum())
    col2.metric("Avg Package", f"{filtered_data['Package'].mean():.2f}")
    col3.metric("Median Package", f"{filtered_data['Package'].median():.2f}")
    col4.metric("Min Package", f"{filtered_data['Package'].min():.2f}")
    col5.metric("Max Package", f"{filtered_data['Package'].max():.2f}")
    col6.metric("Total Companies", filtered_data["Company"].nunique())

    st.subheader("Package Range vs Students Placed")
    fig1 = px.pie(filtered_data, names="Package Range", values="Placed_Students")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Branch vs Students Placed")
    fig2 = px.pie(filtered_data, names="Branch", values="Placed_Students")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available for selected filters.")

# Admin Panel
if st.session_state.admin_logged_in:
    st.subheader("Admin Panel - Add Record")

    year = st.number_input("Year", min_value=2000, max_value=2050, step=1)
    company = st.text_input("Company")
    package = st.number_input("Package (LPA)", min_value=0.0, step=0.1)
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
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        save_data(st.session_state.data)
        st.success("Record added successfully!")
        st.experimental_rerun()




