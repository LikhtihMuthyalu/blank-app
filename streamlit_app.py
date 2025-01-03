import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Placeholder for user credentials (replace with a database for production)
users = {
    "staff": {"username": "staff_user", "password": "staff123"},
    "owner": {"username": "owner_user", "password": "owner123"}
}

# Initialize session state for inventory if not already done
if 'inventory' not in st.session_state:
    # Example data
    st.session_state['inventory'] = pd.DataFrame({
        'Item Name': ['Apples', 'Bananas', 'Carrots', 'Detergent'],
        'Quantity': [3, 150, 10, 2],
        'Price': [0.5, 0.2, 1.0, 5.0],
        'Payment Due': ['2024-12-20', '2024-12-15', '2024-12-30', '2024-12-10']
    })

# Thresholds for alerts
LOW_STOCK_THRESHOLD = 5
EXCESS_STOCK_THRESHOLD = 100

st.set_page_config(page_title="MY INVENTORY MANAGEMENT APP", layout="wide", page_icon="📦")

st.title("📦 MY INVENTORY MANAGEMENT APP")

# Role-based login
st.write("Welcome! Please log in to access the system.")

# Sidebar for user role selection
role = st.sidebar.radio("Select your role:", ["Staff", "Owner"])

# Login Form
st.subheader("Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Log In")

# Authentication logic
if login_button:
    user = users.get(role.lower())
    if user and username == user["username"] and password == user["password"]:
        st.success(f"Welcome, {username}! You are logged in as {role}.")
        # Role-specific features can be added here
        if role == "Staff":
            st.info("You have access to view inventory and alerts.")
        elif role == "Owner":
            st.info("You have full access to manage inventory and financials.")
    else:
        st.error("Invalid username or password. Please try again.")

# Function to display the inventory
def view_inventory():
    st.subheader("📋 Current Inventory")
    if st.session_state['inventory'].empty:
        st.info("No items in inventory.")
    else:
        st.dataframe(st.session_state['inventory'])

        if PLOTLY_AVAILABLE:
            # Add a bar chart to visualize quantities
            fig = px.bar(st.session_state['inventory'], x='Item Name', y='Quantity', color='Item Name',
                         title="Inventory Quantities", labels={'Quantity': 'Stock Quantity'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Plotly is not installed. Install it using `pip install plotly` to enable visualizations.")

def add_item():
    st.subheader("➕ Add New Item")
    with st.form("add_item_form"):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price", min_value=0.0, step=0.01)
        payment_due = st.date_input("Payment Due Date")
        submit = st.form_submit_button("Add Item")

        if submit:
            if item_name:
                new_item = pd.DataFrame({
                    "Item Name": [item_name],
                    "Quantity": [quantity],
                    "Price": [price],
                    "Payment Due": [payment_due]
                })
                st.session_state['inventory'] = pd.concat([st.session_state['inventory'], new_item], ignore_index=True)
                st.success(f"Item '{item_name}' added successfully!")
            else:
                st.error("Item Name cannot be empty.")

def update_item():
    st.subheader("✏️ Update Item")
    if st.session_state['inventory'].empty:
        st.info("No items to update.")
        return

    item_names = st.session_state['inventory']['Item Name'].tolist()
    selected_item = st.selectbox("Select Item to Update", item_names)

    if selected_item:
        item_data = st.session_state['inventory'][st.session_state['inventory']['Item Name'] == selected_item]
        current_quantity = int(item_data['Quantity'].values[0])
        current_price = float(item_data['Price'].values[0])
        current_payment_due = item_data['Payment Due'].values[0]

        new_quantity = st.number_input("New Quantity", min_value=1, value=current_quantity, step=1)
        new_price = st.number_input("New Price", min_value=0.0, value=current_price, step=0.01)
        new_payment_due = st.date_input("New Payment Due Date", value=pd.to_datetime(current_payment_due))

        if st.button("Update Item"):
            st.session_state['inventory'].loc[st.session_state['inventory']['Item Name'] == selected_item, ['Quantity', 'Price', 'Payment Due']] = [new_quantity, new_price, new_payment_due]
            st.success(f"Item '{selected_item}' updated successfully!")

def delete_item():
    st.subheader("🗑️ Delete Item")
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
            # Add pie chart for low stock items
            fig = px.pie(low_stock_items, names='Item Name', values='Quantity', title="Low Stock Items")
            st.plotly_chart(fig, use_container_width=True)

    if excess_stock_items.empty:
        st.info("No excess stock items.")
    else:
        st.warning("Excess Stock Items:")
        st.dataframe(excess_stock_items)

        if PLOTLY_AVAILABLE:
            # Add bar chart for excess stock items
            fig = px.bar(excess_stock_items, x='Item Name', y='Quantity', color='Item Name',
                         title="Excess Stock Quantities", labels={'Quantity': 'Stock Quantity'})
            st.plotly_chart(fig, use_container_width=True)

def payments_due():
    st.subheader("💰 Payments Due")
    today = pd.Timestamp.now().date()
    # Ensure Payment Due column is in datetime format
    st.session_state['inventory']['Payment Due'] = pd.to_datetime(st.session_state['inventory']['Payment Due'])
    due_items = st.session_state['inventory'][st.session_state['inventory']['Payment Due'].dt.date < today]

    if due_items.empty:
        st.info("No pending payments.")
    else:
        st.warning("Items with Pending Payments:")
        st.dataframe(due_items)

        if PLOTLY_AVAILABLE:
            # Calculate days overdue
            due_items['Days Overdue'] = due_items['Payment Due'].apply(lambda x: (today - x.date()).days)
            fig = px.bar(due_items, x='Item Name', y='Days Overdue', color='Item Name',
                         title="Overdue Payments", labels={'Days Overdue': 'Days Overdue'})
            st.plotly_chart(fig, use_container_width=True)

# Menu navigation
def main():
    if role == "Staff" and username == users['staff']['username'] and password == users['staff']['password']:
        st.sidebar.title("Navigation")
        menu = st.sidebar.radio("Go to", ["View Inventory", "Alerts", "Payments Due"])
        if menu == "View Inventory":
            view_inventory()
        elif menu == "Alerts":
            alerts()
        elif menu == "Payments Due":
            payments_due()

    elif role == "Owner" and username == users['owner']['username'] and password == users['owner']['password']:
        st.sidebar.title("Navigation")
        menu = st.sidebar.radio("Go to", ["View Inventory", "Add Item", "Update Item", "Delete Item", "Alerts", "Payments Due"])
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
        elif menu == "Payments Due":
            payments_due()

if __name__ == "__main__":
    main()

