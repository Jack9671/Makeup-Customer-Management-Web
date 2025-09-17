import streamlit as st
from dotenv import load_dotenv
from pages.auth_page import auth_page
from pages.user_page import user_page
from pages.admin_page import show_admin_dashboard
from components.create_customer_table import create_customers_table

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(page_title="Customer Management System", layout="wide")
    
    # Create customers table on app startup (runs once)
    #create_customers_table()
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    # Check authentication
    if st.session_state.user is None:
        auth_page()
    else:
        if st.session_state.is_admin:
            show_admin_dashboard()
        else:
            user_page()


if __name__ == "__main__":
    main()  