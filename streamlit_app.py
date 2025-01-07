import streamlit as st
import pandas as pd
import json

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Load and save users to/from a JSON file
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "staff": {"username": "staff_user", "password": "staff123"},
            "owner": {"username": "owner_user", "password": "owner123"}
        }

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# Load users at the start
users = load_users()

# Initialize session state for inventory if not already done
if 'inventory' not in st.session_state:
    # Example medical inventory data
    st.session_state['inventory'] = pd.DataFrame({
        'Item Name': ['Bandages', 'Syringes', 'Face Masks', 'Gloves', 'Paracetamol'],
        'Quantity': [50, 200, 100, 150, 500],
        'Price': [0.1, 0.5, 0.2, 0.15, 0.05],
        'Expiry Date': ['2025-01-10', '2025-06-20', '2024-12-31', '2025-03-15', '2026-01-01']
    })

# Update thresholds for medical inventory
LOW_STOCK_THRESHOLD = 20
EXCESS_STOCK_THRESHOLD = 300

st.set_page_config(page_title="MEDICAL INVENTORY MANAGEMENT APP", layout="wide", page_icon="🩺")

st.title("🩺 MEDICAL INVENTORY MANAGEMENT APP")

# Role-based login
st.write("Welcome! Please log in to access the system.")

# Sidebar for user role selection
role = st.sidebar.radio("Select your role:", ["Staff", "Owner"])

# Login Form
st.subheader("Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Log In")
logout_button = st.button("Log Out")

# Authentication logic
if login_button:
    user = users.get(role.lower())
    if user and username == user["username"] and password == user["password"]:
        st.success(f"Welcome, {username}! You are logged in as {role}.")
        if role == "Staff":
            st.info("You have access to view inventory and alerts.")
        elif role == "Owner":
            st.info("You have full access to manage inventory and financials.")
        st.session_state.logged_in = True
    else:
        st.error("Invalid username or password. Please try again.")

elif logout_button:
    st.session_state.logged_in = False
    st.success("You have been logged out.")

# Function to display the inventory
def view_inventory():
    st.subheader("📋 Current Medical Inventory")
    if st.session_state['inventory'].empty:
        st.info("No items in inventory.")
    else:
        st.dataframe(st.session_state['inventory'])

        if PLOTLY_AVAILABLE:
            # Add a bar chart to visualize quantities
            fig = px.bar(st.session_state['inventory'], x='Item Name', y='Quantity', color='Item Name',
                         title="Medical Inventory Quantities", labels={'Quantity': 'Stock Quantity'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Plotly is not installed. Install it using `pip install plotly` to enable visualizations.")

def add_item():
    st.subheader("➕ Add New Medical Item")
    with st.form("add_item_form"):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price", min_value=0.0, step=0.01)
        expiry_date = st.date_input("Expiry Date")
        submit = st.form_submit_button("Add Item")

        if submit:
            if item_name:
                new_item = pd.DataFrame({
                    "Item Name": [item_name],
                    "Quantity": [quantity],
                    "Price": [price],
                    "Expiry Date": [expiry_date]
                })
                st.session_state['inventory'] = pd.concat([st.session_state['inventory'], new_item], ignore_index=True)
                st.success(f"Item '{item_name}' added successfully!")
            else:
                st.error("Item Name cannot be empty.")

def update_item():
    st.subheader("✏️ Update Medical Item")
    if st.session_state['inventory'].empty:
        st.info("No items to update.")
        return

    item_names = st.session_state['inventory']['Item Name'].tolist()
    selected_item = st.selectbox("Select Item to Update", item_names)

    if selected_item:
        item_data = st.session_state['inventory'][st.session_state['inventory']['Item Name'] == selected_item]
        current_quantity = int(item_data['Quantity'].values[0])
        current_price = float(item_data['Price'].values[0])
        current_expiry_date = item_data['Expiry Date'].values[0]

        new_quantity = st.number_input("New Quantity", min_value=1, value=current_quantity, step=1)
        new_price = st.number_input("New Price", min_value=0.0, value=current_price, step=0.01)
        new_expiry_date = st.date_input("New Expiry Date", value=pd.to_datetime(current_expiry_date))

        if st.button("Update Item"):
            st.session_state['inventory'].loc[st.session_state['inventory']['Item Name'] == selected_item, ['Quantity', 'Price', 'Expiry Date']] = [new_quantity, new_price, new_expiry_date]
            st.success(f"Item '{selected_item}' updated successfully!")

def delete_item():
    st.subheader("🗑️ Delete Medical Item")
    if st.session_state['inventory'].empty:
        st.info("No items to delete.")
        return

    item_names = st.session_state['inventory']['Item Name'].tolist()
    selected_item = st.selectbox("Select Item to Delete", item_names)

    if selected_item and st.button("Delete Item"):
        st.session_state['inventory'] = st.session_state['inventory'][st.session_state['inventory']['Item Name'] != selected_item]
        st.success(f"Item '{selected_item}' deleted successfully!")

def alerts():
    st.subheader("⚠️ Stock Alerts")
    low_stock_items = st.session_state['inventory'][st.session_state['inventory']['Quantity'] < LOW_STOCK_THRESHOLD]
    excess_stock_items = st.session_state['inventory'][st.session_state['inventory']['Quantity'] > EXCESS_STOCK_THRESHOLD]

    if low_stock_items.empty:
        st.info("No low stock items.")
    else:
        st.warning("Low Stock Items:")
        st.dataframe(low_stock_items)

        if PLOTLY_AVAILABLE:
            fig = px.pie(low_stock_items, names='Item Name', values='Quantity', title="Low Stock Items")
            st.plotly_chart(fig, use_container_width=True)

    if excess_stock_items.empty:
        st.info("No excess stock items.")
    else:
        st.warning("Excess Stock Items:")
        st.dataframe(excess_stock_items)

        if PLOTLY_AVAILABLE:
            fig = px.bar(excess_stock_items, x='Item Name', y='Quantity', color='Item Name',
                         title="Excess Stock Quantities", labels={'Quantity': 'Stock Quantity'})
            st.plotly_chart(fig, use_container_width=True)

def payments_due():
    st.subheader("💰 Expiry Alerts")
    today = pd.Timestamp.now().date()
    st.session_state['inventory']['Expiry Date'] = pd.to_datetime(st.session_state['inventory']['Expiry Date'])
    expired_items = st.session_state['inventory'][st.session_state['inventory']['Expiry Date'].dt.date < today]

    if expired_items.empty:
        st.info("No expired items.")
    else:
        st.warning("Expired Items:")
        st.dataframe(expired_items)

        if PLOTLY_AVAILABLE:
            expired_items['Days Expired'] = expired_items['Expiry Date'].apply(lambda x: (today - x.date()).days)
            fig = px.bar(expired_items, x='Item Name', y='Days Expired', color='Item Name',
                         title="Expired Items", labels={'Days Expired': 'Days Expired'})
            st.plotly_chart(fig, use_container_width=True)

def manage_users():
    st.subheader("👤 Manage Users")
    action = st.radio("Select Action", ["Add User", "Remove User"])

    if action == "Add User":
        with st.form("add_user_form"):
            new_role = st.selectbox("Select Role", ["Staff", "Owner"])
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            submit_button = st.form_submit_button("Add User")

            if submit_button:
                if new_username and new_password:
                    users[new_role.lower()] = {"username": new_username, "password": new_password}
                    save_users()
                    st.success(f"User '{new_username}' added successfully as {new_role}.")
                else:
                    st.error("Both username and password are required.")

    elif action == "Remove User":
        remove_role = st.selectbox("Select Role to Remove", ["Staff", "Owner"])
        if st.button("Remove User"):
            if remove_role.lower() in users:
                del users[remove_role.lower()]
                save_users()
                st.success(f"User with role '{remove_role}' removed successfully.")
            else:
                st.error(f"No user with role '{remove_role}' found.")

def main():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        return

    if role == "Staff" and username == users['staff']['username'] and password == users['staff']['password']:
        st.sidebar.title("Navigation")
        menu = st.sidebar.radio("Go to", ["View Inventory", "Alerts", "Expiry Alerts"])
        if menu == "View Inventory":
            view_inventory()
        elif menu == "Alerts":
            alerts()
        elif menu == "Expiry Alerts":
            payments_due()

    elif role == "Owner" and username == users['owner']['username'] and password == users['owner']['password']:
        st.sidebar.title("Navigation")
        menu = st.sidebar.radio("Go to", ["View Inventory", "Add Item", "Update Item", "Delete Item", "Alerts", "Expiry Alerts", "Manage Users"])
        if menu == "View Inventory":
            view_inventory()
        elif menu == "Add Item":
            add_item()
        elif menu == "Update Item":
            update_item()
        elif menu == "Delete Item":
            delete_item()
        elif menu == "Alerts":
            alerts()
        elif menu == "Expiry Alerts":
            payments_due()
        elif menu == "Manage Users":
            manage_users()

if __name__ == "__main__":
    main()
