
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
ADMIN_CREDENTIALS = {"admin@msit.in": "password"}  # Change this to secure login

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

# Categorize Package Ranges
bins = [0, 5, 10, 15, 20, float('inf')]
labels = ['0-5 LPA', '5-10 LPA', '10-15 LPA', '15-20 LPA', '20+ LPA']
filtered_data['Package Range'] = pd.cut(filtered_data['Package'], bins=bins, labels=labels, right=False)

# Main UI
st.title(':rainbow[ MSIT Placement Records]')
st.subheader(':gray[Placement Statistics]', divider='rainbow')

st.dataframe(filtered_data, use_container_width=True)

# Display Metrics
if not filtered_data.empty:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    total_students_placed = filtered_data["Placed_Students"].sum()
    avg_package = filtered_data["Package"].mean()
    median_package = filtered_data["Package"].median()
    min_package = filtered_data["Package"].min()
    max_package = filtered_data["Package"].max()
    num_companies = filtered_data["Company"].nunique()
    
    col1.metric(label="🎓 Total Students Placed", value=total_students_placed)
    col2.metric(label="💰 Average Package (LPA)", value=f"{avg_package:.2f}" if not pd.isna(avg_package) else "N/A")
    col3.metric(label="📁 Median Package (LPA)", value=f"{median_package:.2f}" if not pd.isna(median_package) else "N/A")
    col4.metric(label="📉 Minimum Package (LPA)", value=f"{min_package:.2f}" if not pd.isna(min_package) else "N/A")
    col5.metric(label="📈 Maximum Package (LPA)", value=f"{max_package:.2f}" if not pd.isna(max_package) else "N/A")
    col6.metric(label="🏢 No of Companies Visited", value=num_companies)

    st.subheader("📊 Placement Insights: Package Range vs Students Placed")
    fig1 = px.pie(filtered_data, names="Package Range", values="Placed_Students", title="Distribution of Students by Package Range")
    st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("📊 Branch vs No. of Students Placed")
    fig2 = px.pie(filtered_data, names="Branch", values="Placed_Students", title="Branch-wise Student Placement Distribution")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("⚠️ No data available for selected filters.")

# Admin Panel - Add, Modify, Delete Data
if st.session_state.admin_logged_in:
    st.write("## 🔧 Admin Panel - Manage Placement Records")
    year = st.number_input("Year", min_value=2000, max_value=2050, step=1)
    company = st.text_input("🏢 Company")
    package = st.number_input("💰 Package (LPA)", min_value=0.0, step=0.1)
    branch = st.text_input("📚 Branch")
    placed_students = st.number_input("🎓 Placed Students", min_value=0, step=1)

    if st.button("✅ Add Record"):
        new_record = pd.DataFrame({"Year": [year], "Company": [company], "Package": [package], "Branch": [branch], "Placed_Students": [placed_students]})
        data = pd.concat([data, new_record], ignore_index=True)
        save_data(data)
        st.success("🎉 Record added successfully!")

    if not data.empty:
        

        company_to_delete = st.selectbox("🗑 Select Company to Delete", data["Company"].unique())
        if st.button("❌ Delete Record"):
            data = data[data["Company"] != company_to_delete]
            save_data(data)
            st.success("🗑 Record deleted successfully!")
