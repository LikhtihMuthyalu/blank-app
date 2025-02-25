import streamlit as st
import pandas as pd
from fpdf import FPDF

# Initialize in-memory data structures
if "customers" not in st.session_state:
    st.session_state["customers"] = []

if "purchase_history" not in st.session_state:
    st.session_state["purchase_history"] = []

if "suppliers" not in st.session_state:
    st.session_state["suppliers"] = pd.DataFrame({
        "Supplier Name": [],
        "Contact Info": [],
        "Pricing Terms": [],
        "Products Supplied": [],
        "Address": []
    })

if "purchase_orders" not in st.session_state:
    st.session_state["purchase_orders"] = pd.DataFrame({
        "Order ID": [],
        "Supplier Name": [],
        "Order Date": [],
        "Expected Delivery Date": [],
        "Actual Delivery Date": [],
        "Order Status": [],
        "Lead Time (days)": []
    })

if "invoices" not in st.session_state:
    st.session_state["invoices"] = pd.DataFrame({
        "Invoice ID": [],
        "Order ID": [],
        "Supplier Name": [],
        "Invoice Date": [],
        "Items": [],
        "Subtotal": [],
        "Tax (%)": [],
        "Tax Amount": [],
        "Discount": [],
        "Shipping Cost": [],
        "Total Amount": [],
        "Payment Status": []
    })

# Streamlit App Configurations
st.set_page_config(layout="wide")  # Makes the layout wider

# Function to add a customer
def add_customer():
    st.header("➕ Add Customer")
    contact = st.text_input("Customer Contact", max_chars=10, key="customer_contact")
    name = st.text_input("Customer Name", key="customer_name")
    age = st.number_input("Customer Age", min_value=10, max_value=100, key="customer_age")
    gender = st.selectbox("Customer Gender", ["Male", "Female", "Other"], key="customer_gender")
    address = st.text_area("Customer Address", key="customer_address")

    if st.button("💾 Add Customer"):
        if contact and name and age and gender:
            if any(c['contact'] == contact for c in st.session_state["customers"]):
                st.error("📞 Customer with this contact already exists.")
            else:
                st.session_state["customers"].append({
                    "contact": contact,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "address": address
                })
                st.success("✔️ Customer added successfully!")

# Function to view customers
def view_customers():
    st.header("👀 View Customers")
    if st.session_state["customers"]:
        customer_df = pd.DataFrame(st.session_state["customers"])
        st.dataframe(customer_df)
    else:
        st.info("🧐 No customers found.")

# Function to delete a customer
def delete_customer():
    st.header("🗑️ Delete Customer")
    del_contact = st.text_input("Enter Customer Contact to Delete", max_chars=10)
    if st.button("🗑️ Delete Customer"):
        if del_contact:
            for customer in st.session_state["customers"]:
                if customer['contact'] == del_contact:
                    st.session_state["customers"].remove(customer)
                    st.success("✅ Customer deleted successfully!")
                    break
            else:
                st.error("❌ Customer not found.")

# Function to add a purchase record
def add_purchase():
    st.header("🛒 Add Purchase Records")
    contact = st.text_input("Customer Contact", max_chars=10, key="add_purchase_contact")
    item = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    price = st.number_input("Price", min_value=0.01, step=0.01, format="%.2f")
    date = st.date_input("Purchase Date")

    if st.button("💾 Add Purchase"):
        if contact and item:
            if any(c['contact'] == contact for c in st.session_state["customers"]):
                st.session_state["purchase_history"].append({
                    "contact": contact,
                    "item": item,
                    "quantity": quantity,
                    "price": price,
                    "date": str(date)
                })
                st.success("✔️ Purchase record added successfully!")
            else:
                st.error("❌ The contact number does not exist in the customers' list.")

# Function to view purchase history
def view_purchase_history():
    st.header("📝 Purchase History")
    if st.session_state["purchase_history"]:
        purchase_df = pd.DataFrame(st.session_state["purchase_history"])
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

# Function to add a supplier
def add_supplier():
    st.header("➕ Add Supplier")
    with st.form("add_supplier_form"):
        name = st.text_input("Supplier Name")
        contact = st.text_input("Contact Info")
        pricing = st.text_area("Pricing Terms")
        products = st.text_area("Products Supplied (comma-separated)")
        address = st.text_area("Address")
        submit = st.form_submit_button("Add Supplier")
        
        if submit:
            if name and contact:
                new_supplier = pd.DataFrame({
                    "Supplier Name": [name],
                    "Contact Info": [contact],
                    "Pricing Terms": [pricing],
                    "Products Supplied": [products],
                    "Address": [address]
                })
                st.session_state["suppliers"] = pd.concat([st.session_state["suppliers"], new_supplier], ignore_index=True)
                st.success(f"Supplier '{name}' added successfully!")
            else:
                st.error("Supplier Name and Contact Info are required fields.")

# Function to add a purchase order
def add_purchase_order():
    st.header("🛒 Add Purchase Order")
    supplier_names = st.session_state["suppliers"]["Supplier Name"].tolist()
    selected_supplier = st.selectbox("Select Supplier", supplier_names)
    order_date = st.date_input("Order Date")
    expected_delivery_date = st.date_input("Expected Delivery Date")
    order_status = st.selectbox("Order Status", ["Pending", "Shipped", "Delivered"])
    
    if st.button("Save Purchase Order"):
        new_order = pd.DataFrame({
            "Order ID": [len(st.session_state["purchase_orders"]) + 1],
            "Supplier Name": [selected_supplier],
            "Order Date": [order_date],
            "Expected Delivery Date": [expected_delivery_date],
            "Actual Delivery Date": [None],
            "Order Status": [order_status],
            "Lead Time (days)": [(expected_delivery_date - order_date).days]
        })
        st.session_state["purchase_orders"] = pd.concat([st.session_state["purchase_orders"], new_order], ignore_index=True)
        st.success("Purchase Order added successfully!")

# Function to generate invoice ID
def generate_invoice_id():
    return f"INV-{2025000 + len(st.session_state['invoices']) + 1}"

# Function to create a detailed PDF invoice
def create_invoice_pdf(invoice_id, supplier_name, invoice_date, items, subtotal, tax, tax_amount, discount, shipping, total_amount, payment_status):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Invoice", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(100, 10, f"Invoice No: {invoice_id}")
    pdf.cell(100, 10, f"Invoice Date: {invoice_date}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "From:")
    pdf.cell(100, 10, "Bill To:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(100, 10, f"{supplier_name}")
    pdf.cell(100, 10, f"{supplier_name}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, "Description", border=1)
    pdf.cell(30, 10, "Rate (RS)", border=1)
    pdf.cell(20, 10, "Qty", border=1)
    pdf.cell(20, 10, "Tax (%)", border=1)
    pdf.cell(30, 10, "Discount", border=1)
    pdf.cell(40, 10, "Amount (RS)", border=1)
    pdf.ln()
    
    pdf.set_font("Arial", "", 12)
    for item in items:
        pdf.cell(50, 10, item["name"], border=1)
        pdf.cell(30, 10, f"{item['rate']:.2f}", border=1)
        pdf.cell(20, 10, str(item["quantity"]), border=1)
        pdf.cell(20, 10, f"{item['tax']:.2f}", border=1)
        pdf.cell(30, 10, f"{item['discount']:.2f}", border=1)
        pdf.cell(40, 10, f"{item['total']:.2f}", border=1)
        pdf.ln()
    
    pdf.ln(5)
    pdf.cell(200, 10, f"Subtotal: {subtotal:.2f}", ln=True)
    pdf.cell(200, 10, f"Tax Amount: {tax_amount:.2f}", ln=True)
    pdf.cell(200, 10, f"Discount: {discount:.2f}", ln=True)
    pdf.cell(200, 10, f"Shipping Cost: {shipping:.2f}", ln=True)
    pdf.cell(200, 10, f"Total Amount: {total_amount:.2f}", ln=True)
    pdf.cell(200, 10, f"Payment Status: {payment_status}", ln=True)
    
    pdf_output = f"invoice_{invoice_id}.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Function to add an invoice
def add_invoice():
    order_ids = st.session_state["purchase_orders"]["Order ID"].tolist()
    selected_order = st.selectbox("Select Purchase Order", order_ids)
    invoice_date = st.date_input("Invoice Date")
    supplier_name = st.text_input("Supplier Name")
    payment_status = st.selectbox("Payment Status", ["Paid", "Pending", "Overdue"])
    
    num_items = st.number_input("Number of Items", min_value=1, value=1)
    items = []
    subtotal = 0
    st.subheader("Add Items")
    for i in range(int(num_items)):
        name = st.text_input(f"Item {i+1} Name", key=f"item_{i}_name")
        rate = st.number_input(f"Rate (RS)", min_value=0.0, format="%.2f", key=f"item_{i}_rate")
        quantity = st.number_input(f"Quantity", min_value=1, key=f"item_{i}_quantity")
        item_tax = st.number_input(f"Tax (%)", min_value=0.0, format="%.2f", key=f"item_{i}_tax")
        item_discount = st.number_input(f"Discount (RS)", min_value=0.0, format="%.2f", key=f"item_{i}_discount")
        total = (rate * quantity) + ((rate * quantity) * item_tax / 100) - item_discount
        if name:
            items.append({"name": name, "rate": rate, "quantity": quantity, "tax": item_tax, "discount": item_discount, "total": total})
            subtotal += total
    
    tax_amount = sum(item['total'] * (item['tax'] / 100) for item in items)
    total_amount = subtotal + tax_amount
    
    if st.button("Generate Invoice"):
        invoice_id = generate_invoice_id()
        pdf_path = create_invoice_pdf(invoice_id, supplier_name, invoice_date, items, subtotal, tax_amount, tax_amount, 0, 0, total_amount, payment_status)
        with open(pdf_path, "rb") as file:
            st.download_button(label="Download Invoice PDF", data=file, file_name=pdf_path, mime="application/pdf")

# Main application
def main():
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio("Go to", ["Customer Management", "Purchase History", "Pharmacy Financial Advisory", "Supplier Management", "Invoice Management"])

    if page == "Customer Management":
        add_customer()
        view_customers()
        delete_customer()

    elif page == "Purchase History":
        tab1, tab2 = st.tabs(["➕ Add Purchase", "📝 View Purchase History"])
        with tab1:
            add_purchase()
        with tab2:
            view_purchase_history()

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

    elif page == "Supplier Management":
        st.title
