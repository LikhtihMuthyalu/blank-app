import streamlit as st
import pandas as pd
import datetime

# In-memory data structures
customers = []
purchase_history = []

# Streamlit App Configurations
st.set_page_config(layout="wide")  # Makes the layout wider

# Streamlit App
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio("Go to", ["Customer Management", "Purchase History", "Pharmacy Financial Advisory"])

if page == "Customer Management":
    st.title("👨‍⚕️ Customer Management")

    # Add Customer
    st.header("➕ Add Customer")
    contact = st.text_input("Customer Contact", max_chars=10, key="customer_contact")
    name = st.text_input("Customer Name", key="customer_name")
    age = st.number_input("Customer Age", min_value=10, max_value=100, key="customer_age")
    gender = st.selectbox("Customer Gender", ["Male", "Female", "Other"], key="customer_gender")
    address = st.text_area("Customer Address", key="customer_address")

    if st.button("💾 Add Customer"):
        if contact and name and age and gender:
            if any(c['contact'] == contact for c in customers):
                st.error("📞 Customer with this contact already exists.")
            else:
                customers.append({
                    "contact": contact,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "address": address
                })
                st.success("✔️ Customer added successfully!")

    # View Customers
    st.header("👀 View Customers")
    if customers:
        customer_df = pd.DataFrame(customers)
        st.dataframe(customer_df)
    else:
        st.info("🧐 No customers found.")

    # Delete Customer
    st.header("🗑️ Delete Customer")
    del_contact = st.text_input("Enter Customer Contact to Delete", max_chars=10)
    if st.button("🗑️ Delete Customer"):
        if del_contact:
            for customer in customers:
                if customer['contact'] == del_contact:
                    customers.remove(customer)
                    st.success("✅ Customer deleted successfully!")
                    break
            else:
                st.error("❌ Customer not found.")

elif page == "Purchase History":
    st.title("🛒 Purchase History Management")

    # Tabs for Navigation
    tab1, tab2 = st.tabs(["➕ Add Purchase", "📝 View Purchase History"])

    # Tab 1: Add Purchase
    with tab1:
        st.header("🛒 Add Purchase Records")
        contact = st.text_input("Customer Contact", max_chars=10, key="add_purchase_contact")
        item = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price", min_value=0.01, step=0.01, format="%.2f")
        date = st.date_input("Purchase Date")

        if st.button("💾 Add Purchase"):
            if contact and item:
                if any(c['contact'] == contact for c in customers):
                    purchase_history.append({
                        "contact": contact,
                        "item": item,
                        "quantity": quantity,
                        "price": price,
                        "date": str(date)
                    })
                    st.success("✔️ Purchase record added successfully!")
                else:
                    st.error("❌ The contact number does not exist in the customers' list.")

    # Tab 2: View Purchase History - Grouped by Contact
    with tab2:
        st.header("📝 Purchase History")
        if purchase_history:
            purchase_df = pd.DataFrame(purchase_history)
            grouped_purchase_df = purchase_df.groupby("contact").agg({
                "item": lambda x: ", ".join(x),
                "quantity": "sum",
                "price": "sum",
                "date": lambda x: ", ".join(x)
            }).reset_index()

            # Format Price as currency
            grouped_purchase_df['price'] = grouped_purchase_df['price'].apply(lambda x: f"₹{x:.2f}")
            grouped_purchase_df['quantity'] = grouped_purchase_df['quantity'].astype(int)

            st.dataframe(grouped_purchase_df)
        else:
            st.info("🧐 No purchase records found.")

elif page == "Pharmacy Financial Advisory":
    st.title("Pharmacy Financial Advisory Module")

    # Sample DataFrame structure
    data = {
        "Company": ["MICRO LABS LTD", "Cadila Healthcare Ltd", "Enzymes Pharmaceuticals", "Sun Pharmaceutical Industries"],
        "Product Name": ["DOLO 650", "Albendazole", "ASPIRIN", "PARACETAMOL"],
        "Product Description": [
            "DOLO 650 is a widely used analgesic and antipyretic.",
            "Albendazole is an anthelmintic used to treat parasitic worm infections.",
            "ASPIRIN is a pain reliever and anti-inflammatory drug.",
            "PARACETAMOL is a common pain reliever and fever reducer."
        ],
        "Usage": [
            "Used for fever, body aches, and pain relief.",
            "Used for treating worm infections such as tapeworm and roundworm.",
            "Used to reduce pain, inflammation, and prevent heart attacks.",
            "Used for headache, fever, and mild to moderate pain."
        ],
        "Manufacture Date": ["2024-01-01", "2024-02-15", "2024-01-20", "2024-03-10"],
        "Expiry Date": ["2026-01-01", "2026-02-15", "2026-01-20", "2026-03-10"],
        "Date of Purchase": ["2024-04-01", "2024-04-10", "2024-04-05", "2024-04-15"],
        "Next Stock Purchase": ["2024-05-01", "2024-05-10", "2024-05-05", "2024-05-15"],
        "Selling Price": [150, 200, 180, 250],
        "Purchase Price": [100, 150, 130, 200],
        "Sales Quantity": [10, 5, 8, 12],
        "Purchase Quantity": [20, 10, 15, 25],
        "Date of Sale": ["2024-04-02", "2024-04-11", "2024-04-06", "2024-04-16"]
    }

    df = pd.DataFrame(data)
    df["Manufacture Date"] = pd.to_datetime(df["Manufacture Date"])
    df["Expiry Date"] = pd.to_datetime(df["Expiry Date"])
    df["Date of Purchase"] = pd.to_datetime(df["Date of Purchase"])
    df["Next Stock Purchase"] = pd.to_datetime(df["Next Stock Purchase"])
    df["Date of Sale"] = pd.to_datetime(df["Date of Sale"])

    # Sales Report
    st.header("Company-wise Sales Report")
    company_sales = df.groupby("Company")["Sales Quantity"].sum()
    st.bar_chart(company_sales)

    # Products under each company
    st.header("Products by Company")
    for company, group in df.groupby("Company"):
        st.subheader(company)
        st.write(group[["Product Name", "Product Description", "Usage", "Selling Price", "Purchase Price"]])

    # Product-wise Sales and Purchase Report
    st.header("Product-wise Sales and Purchase Report")
    product_sales = df.groupby("Product Name")["Sales Quantity"].sum()
    product_purchases = df.groupby("Product Name")["Purchase Quantity"].sum()

    st.subheader("Sales per Product")
    st.bar_chart(product_sales)

    st.subheader("Purchases per Product")
    st.bar_chart(product_purchases)

    # Most Selling Product
    st.header("Most Selling Product")
    most_selling_product = df.loc[df["Sales Quantity"].idxmax(), ["Product Name", "Sales Quantity"]]
    st.write(most_selling_product)

    # Product in Demand During a Specific Time Period
    st.header("Product in Demand During a Specific Time Period")
    selected_start_date = st.date_input("Select Start Date", df["Date of Sale"].min())
    selected_end_date = st.date_input("Select End Date", df["Date of Sale"].max())

    demand_df = df[(df["Date of Sale"] >= pd.to_datetime(selected_start_date)) & (df["Date of Sale"] <= pd.to_datetime(selected_end_date))]
    if not demand_df.empty:
        most_demanded_product = demand_df.groupby("Product Name")["Sales Quantity"].sum().idxmax()
        st.write(f"Most Demanded Product: {most_demanded_product}")
    else:
        st.write("No sales data available for the selected period.")

    # Daily, Weekly, Yearly Sales Report
    st.header("Sales Reports")
    df["Sale Year"] = df["Date of Sale"].dt.year
    df["Sale Week"] = df["Date of Sale"].dt.isocalendar().week
    df["Sale Day"] = df["Date of Sale"].dt.date

    sales_daily = df.groupby("Sale Day")["Sales Quantity"].sum()
    sales_weekly = df.groupby("Sale Week")["Sales Quantity"].sum()
    sales_yearly = df.groupby("Sale Year")["Sales Quantity"].sum()

    st.subheader("Daily Sales")
    st.bar_chart(sales_daily)

    st.subheader("Weekly Sales")
    st.bar_chart(sales_weekly)

    st.subheader("Yearly Sales")
    st.bar_chart(sales_yearly)

    # Expiry, Purchase, and Next Stock Purchase Info
    st.header("Stock Information")
    st.write(df[["Company", "Product Name", "Manufacture Date", "Expiry Date", "Date of Purchase", "Next Stock Purchase"]])

    # Selling Price and Purchase Price
    st.header("Selling and Purchase Prices")
    price_data = df.groupby("Company")[["Selling Price", "Purchase Price"]].mean()
    st.bar_chart(price_data)

    # Profit Analysis
    st.header("Profit Analysis")
    df["Profit per Unit"] = df["Selling Price"] - df["Purchase Price"]
    df["Total Profit"] = df["Profit per Unit"] * df["Sales Quantity"]
    profit_by_company = df.groupby("Company")["Total Profit"].sum()
    st.bar_chart(profit_by_company)
