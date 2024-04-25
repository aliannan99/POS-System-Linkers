import streamlit as st
import pandas as pd
import pdfkit
import base64

url = "https://raw.githubusercontent.com/aliannan99/POS-System-Linkers/main/Updated_FinalData305.csv"
# User credentials
users = {
    "jg001": {"name": "Jack Gustu", "password": "123456"},
    "jc002": {"name": "James Cameron", "password": "123456"},
    "en003": {"name": "Elie Nasr", "password": "123456"},
    "kl004": {"name": "Kendrick Lamar", "password": "123456"},
    "js005": {"name": "Jack Sparrow", "password": "123456"}
}

# Function to verify login credentials
def verify_login(username, password):
    return username in users and users[username]['password'] == password

# Function to generate PDF receipt
def generate_pdf(cart_df, total):
    # Convert cart dataframe to HTML
    cart_html = cart_df.to_html(index=False)
    
    # Load image
    with open("C:/Users/user/OneDrive/Desktop/logo.png", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Construct the HTML for the PDF with the logo and signature line
    receipt_html = f"""
    <html>
    <head>
    <style>
      .signature {{
        border-top: 1px solid #000;
        width: 200px;
        text-align: center;
        margin-top: 50px;
      }}
    </style>
    </head>
    <body>
    <img src="data:image/png;base64,{img_base64}" alt="Linkers Group Logo" style="width: 150px;"/>
    <h1>Linkers POS System Receipt</h1>
    {cart_html}
    <p><strong>Total: {total:.2f}</strong></p>
    <div class="signature">Signature</div>
    </body>
    </html>
    """
    # Convert HTML to PDF
    pdf_filename = 'receipt.pdf'
    pdfkit.from_string(receipt_html, pdf_filename, configuration=config)
    return pdf_filename

# Configure pdfkit with wkhtmltopdf executable path
config = pdfkit.configuration(wkhtmltopdf=r'C:\Users\user\OneDrive\Desktop\POS system\wkhtmltopdf\bin\wkhtmltopdf.exe')

# Initialize the session state for login and cart
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'cart' not in st.session_state:
    st.session_state['cart'] = []

# Login form
def login_form():
    st.header('LOG IN PORTAL')
    st.session_state['logged_in'] = False
    with st.form(key='login_form'):
        username = st.text_input('Username', key='username')
        password = st.text_input('Password', type='password', key='password')
        submit_button = st.form_submit_button(label='Login')
        if submit_button:
            if verify_login(username, password):
                st.session_state['logged_in'] = True
            else:
                st.error('Username and/or password is incorrect')

# Display login form if not logged in
if not st.session_state['logged_in']:
    login_form()
else:
    # Load data function
    def load_data():
        try:
            data = pd.read_csv(url)
            return data
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()

    # Load the data
    data = load_data()

    if not data.empty:
        # Extract item codes and descriptions
        item_codes = data['Item Code'].unique()
        item_descriptions = data.set_index('Item Code')['Description'].to_dict()

        # Cart functions
        def add_to_cart(item_code, quantity):
            item_data = data[data['Item Code'] == item_code].iloc[0]
            item = {
                'Item Code': item_code,
                'Description': item_data['Description'],
                'Quantity': quantity,
                'Unit Price': item_data['Unit Price'],
                'Total Price': item_data['Unit Price'] * quantity
            }
            found = False
            for cart_item in st.session_state['cart']:
                if cart_item['Item Code'] == item_code:
                    cart_item['Quantity'] += quantity
                    cart_item['Total Price'] = cart_item['Unit Price'] * cart_item['Quantity']
                    found = True
                    break
            if not found:
                st.session_state['cart'].append(item)

        def calculate_total():
            return sum(item['Total Price'] for item in st.session_state['cart'])

        # POS System interface
        st.title('Linkers POS System')
        selected_item_code = st.selectbox('Select an item code', item_codes)
        st.text(f"Description: {item_descriptions.get(selected_item_code, 'No description available')}")

        quantity = st.number_input('Select quantity', min_value=1, max_value=100, step=1)
        if st.button('Add to Cart'):
            add_to_cart(selected_item_code, quantity)

        # Display the cart and checkout
        if st.session_state['cart']:
            st.write('Cart')
            cart_df = pd.DataFrame(st.session_state['cart'])
            st.dataframe(cart_df[['Item Code', 'Description', 'Quantity', 'Unit Price', 'Total Price']])
            if st.button('Checkout'):
                total = calculate_total()
                st.write(f"Total: {total:.2f}")
                pdf_path = generate_pdf(cart_df, total)

                # Open the PDF file in binary mode and create a download button
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    st.download_button(label="Download Receipt",
                                       data=pdf_bytes,
                                       file_name=pdf_path,
                                       mime='application/pdf')







