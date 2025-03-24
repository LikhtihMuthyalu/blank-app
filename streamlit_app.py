import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

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

    # Create Inventory Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        expiry_date TEXT NOT NULL)''')

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

# Load Inventory
def load_inventory():
    conn = sqlite3.connect("medical_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, quantity, price, expiry_date FROM inventory")
    data = cursor.fetchall()
    conn.close()
    
    return pd.DataFrame(data, columns=["Item Name", "Quantity", "Price", "Expiry Date"])

# Add Item
def add_item_to_db(item_name, quantity, price, expiry_date):
    conn = sqlite3.connect("medical_inventory.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO inventory (item_name, quantity, price, expiry_date) VALUES (?, ?, ?, ?)", 
                   (item_name, quantity, price, expiry_date))
    
    conn.commit()
    conn.close()

# Update Item
def update_item_in_db(item_name, new_quantity, new_price, new_expiry_date):
    conn = sqlite3.connect("medical_inventory.db")
    cursor = conn.cursor()
    
    cursor.execute("UPDATE inventory SET quantity = ?, price = ?, expiry_date = ? WHERE item_name = ?", 
                   (new_quantity, new_price, new_expiry_date, item_name))
    
    conn.commit()
    conn.close()

# Delete Item
def delete_item_from_db(item_name):
    conn = sqlite3.connect("medical_inventory.db")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM inventory WHERE item_name = ?", (item_name,))
    
    conn.commit()
    conn.close()

# Streamlit UI
st.set_page_config(page_title="Medical companion", layout="wide", page_icon="🩺")
st.title("🩺 Medical companion")
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
    
    if role == "Staff":
        menu = st.sidebar.radio("Go to", ["View Inventory", "Alerts", "Expiry Alerts"])
    elif role == "Owner":
        menu = st.sidebar.radio("Go to", ["View Inventory", "Add Item", "Update Item", "Delete Item", "Alerts", "Expiry Alerts", "Manage Users"])

    # View Inventory
    if menu == "View Inventory":
        st.subheader("📋 Medical Inventory")
        inventory_df = load_inventory()
        if inventory_df.empty:
            st.info("No items in inventory.")
        else:
            st.dataframe(inventory_df)
            fig = px.bar(inventory_df, x="Item Name", y="Quantity", color="Item Name", title="Inventory Quantities")
            st.plotly_chart(fig, use_container_width=True)

    # Add Item
    elif menu == "Add Item" and role == "Owner":
        st.subheader("➕ Add New Medical Item")
        with st.form("add_item_form"):
            item_name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            price = st.number_input("Price", min_value=0.0, step=0.01)
            expiry_date = st.date_input("Expiry Date")
            submit = st.form_submit_button("Add Item")

            if submit and item_name:
                add_item_to_db(item_name, quantity, price, expiry_date)
                st.success(f"Item '{item_name}' added successfully!")

    # Update Item
    elif menu == "Update Item" and role == "Owner":
        st.subheader("✏️ Update Medical Item")
        inventory_df = load_inventory()
        if not inventory_df.empty:
            item_names = inventory_df["Item Name"].tolist()
            selected_item = st.selectbox("Select Item", item_names)
            item_data = inventory_df[inventory_df["Item Name"] == selected_item].iloc[0]

            new_quantity = st.number_input("New Quantity", min_value=1, value=int(item_data["Quantity"]), step=1)
            new_price = st.number_input("New Price", min_value=0.0, value=float(item_data["Price"]), step=0.01)
            new_expiry_date = st.date_input("New Expiry Date", value=pd.to_datetime(item_data["Expiry Date"]).date())

            if st.button("Update Item"):
                update_item_in_db(selected_item, new_quantity, new_price, new_expiry_date)
                st.success(f"Item '{selected_item}' updated successfully!")

    # Delete Item
    elif menu == "Delete Item" and role == "Owner":
        st.subheader("🗑️ Delete Medical Item")
        inventory_df = load_inventory()
        if not inventory_df.empty:
            item_names = inventory_df["Item Name"].tolist()
            selected_item = st.selectbox("Select Item to Delete", item_names)

            if st.button("Delete Item"):
                delete_item_from_db(selected_item)
                st.success(f"Item '{selected_item}' deleted successfully!")

    # Alerts
    elif menu == "Alerts":
        st.subheader("⚠️ Stock Alerts")
        inventory_df = load_inventory()
        low_stock = inventory_df[inventory_df["Quantity"] < 20]
        if not low_stock.empty:
            st.warning("Low Stock Items:")
            st.dataframe(low_stock)

    # Expiry Alerts
    elif menu == "Expiry Alerts":
        st.subheader("💰 Expiry Alerts")
        inventory_df = load_inventory()
        today = pd.Timestamp.now().date()
        expired_items = inventory_df[pd.to_datetime(inventory_df["Expiry Date"]).dt.date < today]

        if not expired_items.empty:
            st.warning("Expired Items:")
            st.dataframe(expired_items)

    # Manage Users
    elif menu == "Manage Users" and role == "Owner":
        st.subheader("👤 Manage Users")
        new_role = st.selectbox("Select Role", ["Staff", "Owner"])
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")

        if st.button("Add User"):
            conn = sqlite3.connect("medical_inventory.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (role, username, password) VALUES (?, ?, ?)", (new_role, new_username, new_password))
            conn.commit()
            conn.close()
            st.success(f"User '{new_username}' added as {new_role}.")

