

import streamlit as st
import pandas as pd
import plotly.express as px

# Page title and icon
st.set_page_config(
    page_title='MSIT Placement Records',
    page_icon='📈'
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

# Admin Authentication
st.sidebar.header("Admin Login")
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
st.sidebar.header("Filters")
year_filter = st.sidebar.multiselect("Select Year", options=sorted(data["Year"].unique()))
branch_filter = st.sidebar.multiselect("Select Branch", options=sorted(data["Branch"].unique()))
company_filter = st.sidebar.multiselect("Select Company", options=sorted(data["Company"].unique()))

# Apply filters
filtered_data = data
if year_filter:
    filtered_data = filtered_data[filtered_data["Year"].isin(year_filter)]
if branch_filter:
    filtered_data = filtered_data[filtered_data["Branch"].isin(branch_filter)]
if company_filter:
    filtered_data = filtered_data[filtered_data["Company"].isin(company_filter)]

# Title
st.title(':rainbow[MSIT Placement Records]')
# Subheader and divider
st.subheader(':gray[Placement Statistics]', divider='rainbow')

# Display filtered data
if not filtered_data.empty:
    total_students_placed = filtered_data["Placed_Students"].sum()
    avg_package = filtered_data["Package"].mean()
    
    st.metric(label="Total Students Placed", value=total_students_placed)
    st.metric(label="Average Package (LPA)", value=f"{avg_package:.2f}" if not pd.isna(avg_package) else "N/A")
    
    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart", "Line Chart"])

    if chart_type == "Bar Chart":
        fig = px.bar(filtered_data, x="Company", y="Placed_Students", color="Year", barmode="group")
        st.plotly_chart(fig)
    elif chart_type == "Pie Chart":
        fig = px.pie(filtered_data, names="Company", values="Placed_Students", title="Placement Distribution")
        st.plotly_chart(fig)
    elif chart_type == "Line Chart":
        fig = px.line(filtered_data, x="Year", y="Placed_Students", color="Company", markers=True)
        st.plotly_chart(fig)
else:
    st.warning("No data available for selected filters.")

# Show data table
st.subheader("Filtered Placement Data")
st.dataframe(filtered_data)

st.subheader("Full Placement Data")
st.dataframe(data)

# Admin Section to Add/Delete Data
if st.session_state.admin_logged_in:
    st.write("## Admin Panel - Add or Delete Placement Records")
    year = st.number_input("Year", min_value=2000, max_value=2050, step=1)
    company = st.text_input("Company")
    package = st.number_input("Package (LPA)", min_value=0.0, step=0.1)
    branch = st.text_input("Branch")
    placed_students = st.number_input("Placed Students", min_value=0, step=1)

    if st.button("Add Record"):
        new_record = pd.DataFrame({"Year": [year], "Company": [company], "Package": [package], "Branch": [branch], "Placed_Students": [placed_students]})
        data = pd.concat([data, new_record], ignore_index=True)
        save_data(data)
        st.success("Record added successfully!")

    delete_company = st.selectbox("Select Company to Delete", data["Company"].unique() if not data.empty else [])
    if st.button("Delete Record"):
        data = data[data["Company"] != delete_company]
        save_data(data)
        st.success(f"Records for {delete_company} deleted successfully!")
else:
    st.warning("Admin login required to add or delete records.")
