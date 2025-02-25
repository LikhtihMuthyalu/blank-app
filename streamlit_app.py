import streamlit as st
import pandas as pd
from fpdf import FPDF

# Initialize customer data
if "customers" not in st.session_state:
    st.session_state["customers"] = pd.DataFrame({
        "Contact": [],
        "Name": [],
        "Age": [],
        "Gender": [],
        "Address": []
    })

# Initialize purchase order data
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

# Initialize supplier data
if "suppliers" not in st.session_state:
    st.session_state["suppliers"] = pd.DataFrame({
        "Supplier Name": [],
        "Contact Info": [],
        "Pricing Terms": [],
        "Products Supplied": [],
        "Address": []
    })

# Initialize invoice data
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

# Function to add a customer
def add_customer():
    with st.form("add_customer_form"):
        contact = st.text_input("Customer Contact", max_chars=10)
        name = st.text_input("Customer Name")
        age = st.number_input("Customer Age", min_value=10, max_value=100)
        gender = st.selectbox("Customer Gender", ["Male", "Female", "Other"])
        address = st.text_area("Customer Address")
        submit = st.form_submit_button("Add Customer")
        
        if submit:
            if contact and name:
                new_customer = pd.DataFrame({
                    "Contact": [contact],
                    "Name": [name],
                    "Age": [age],
                    "Gender": [gender],
                    "Address": [address]
                })
                st.session_state["customers"] = pd.concat([st.session_state["customers"], new_customer], ignore_index=True)
                st.success(f"Customer '{name}' added successfully!")
            else:
                st.error("Customer Contact and Name are required fields.")

# Function to add a supplier
def add_supplier():
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
    st.title("Supplier and Customer Management System")
    
    tabs = st.tabs(["Customer Management", "Supplier Management", "Purchase Orders", "Invoices"])
    
    with tabs[0]:
        st.subheader("👨‍⚕️ Customer Management")
        add_customer()
        st.subheader("📋 View All Customers")
        if st.session_state["customers"].empty:
            st.info("No customers available. Add some customers to get started.")
        else:
            st.table(st.session_state["customers"])  # Non-scrollable table
    
    with tabs[1]:
        st.subheader("📦 Supplier Management")
        add_supplier()
        st.subheader("📋 View All Suppliers")
        if st.session_state["suppliers"].empty:
            st.info("No suppliers available. Add some suppliers to get started.")
        else:
            st.table(st.session_state["suppliers"])  # Non-scrollable table
    
    with tabs[2]:
        st.subheader("🛒 Add Purchase Order")
        add_purchase_order()
        st.subheader("📋 View Purchase Orders")
        if st.session_state["purchase_orders"].empty:
            st.info("No purchase orders available.")
        else:
            st.table(st.session_state["purchase_orders"])  # Non-scrollable table
    
    with tabs[3]:
        st.subheader("🧾 Generate Invoice")
        add_invoice()
        st.subheader("📋 View Invoices")
        if st.session_state["invoices"].empty:
            st.info("No invoices generated.")
        else:
            st.table(st.session_state["invoices"])  # Non-scrollable table

if __name__ == "__main__":
    main()
