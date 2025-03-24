import streamlit as st
import sqlite3

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("medical_inventory.db")
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    # Insert Default Users
    cursor.execute("INSERT OR IGNORE INTO users (role, username, password) VALUES ('Staff', 'staff_user', 'staff123')")
    cursor.execute("INSERT OR IGNORE INTO users (role, username, password) VALUES ('Owner', 'owner_user', 'owner123')")

    conn.commit()
    conn.close()

init_db()

# Authenticate user
def authenticate_user(role, username, password):
    conn = sqlite3.connect("medical_inventory.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE role = ? AND username = ? AND password = ?", (role, username, password))
    user = cursor.fetchone()
    
    conn.close()
    return user

# Streamlit UI
st.set_page_config(page_title="Medical Companion", layout="wide", page_icon="🩺")
st.title("🩺 Medical Companion")
st.image("https://imgs.search.brave.com/9EE7oXDTnPTUhNYceozZyHyPayDG_ieLeplku_pEgd8/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWcu/ZnJlZXBpay5jb20v/ZnJlZS12ZWN0b3Iv/ZG9jdG9yLWRvb2Rs/ZS1oYW5kLWRyYXdu/LWNvbG9yLXZlY3Rv/ci1jb2xsZWN0aW9u/XzE3OTIzNC0zOTcu/anBnP3NlbXQ9YWlz/X2h5YnJpZA", caption="Prevention is better than cure!!")

st.sidebar.title("Login")
role = st.sidebar.radio("Select your role:", ["Staff", "Owner"])
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Log In")

if login_button:
    user = authenticate_user(role, username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.role = role
        st.session_state.username = username
        st.success(f"Welcome, {username}! You are logged in as {role}.")
    else:
        st.error("Invalid username or password.")

if "logged_in" in st.session_state and st.session_state.logged_in:
    st.sidebar.title("Navigation")

    # Define menu based on role
    if st.session_state.role == "Owner":
        menu_options = ["🔬Clinical Advisor", "🤝Customer Relation", "📦Spplier Management", "💰Financial Advisor"]
    else:  # Staff role
        menu_options = ["🔬Clinical Advisor", "🤝Customer Relation"]

    menu = st.sidebar.radio("Go to", menu_options)

    # Clinical Advisor Page
    if menu == "🔬Clinical Advisor":
        st.subheader("🔬 Clinical Advisor")
        st.write("This section will provide clinical insights and medical recommendations.")

    # Customer Relation Page
    elif menu == "🤝Customer Relation":
        st.subheader("🤝 Customer Relation")
        st.write("This section will help manage customer interactions and relations.")

    # Supplier Management Page (Only for Owner)
    elif menu == "📦Spplier Management" and st.session_state.role == "Owner":
        st.subheader("📦 Supplier Management")
        st.write("This section will manage supplier details and transactions.")

    # Financial Advisor Page (Only for Owner)
    elif menu == "💰Financial Advisor" and st.session_state.role == "Owner":
        st.subheader("💰 Financial Advisor")
        st.write("This section will provide financial insights and reports.")


