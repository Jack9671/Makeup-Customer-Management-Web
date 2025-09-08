import streamlit as st
from dotenv import load_dotenv
from components.supabase_client import supabase
from components.create_customer_table import create_customers_table
import pycountry

# Load environment variables
load_dotenv()
# Admin credentials
ADMIN_EMAIL = "duyt76078@gmail.com"

@st.cache_data
def get_countries():
    """Get list of all countries"""
    countries = []
    for country in pycountry.countries:
        countries.append(country.name)
    return sorted(countries)

@st.cache_data
def get_all_subdivisions():
    """Get all subdivisions from all countries"""
    subdivisions = []
    for subdivision in pycountry.subdivisions:
        subdivisions.append(subdivision.name)
    return sorted(subdivisions)

def _login_form():
    """Login form component"""
    st.header("Login")
    st.info("Please use your registered email and password to log in.")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your-email@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Validate inputs
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            try:
                # Authenticate with Supabase Auth
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if response.user:
                    st.session_state.user = response.user
                    
                    # Check if user is admin
                    if email == ADMIN_EMAIL:
                        st.session_state.is_admin = True
                    else:
                        st.session_state.is_admin = False
                        # Create customers table if it doesn't exist (runs once)
                        from components.create_customer_table import create_customers_table
                        create_customers_table()
                    
                    st.success("Login successful!")
                    st.rerun()
                else: 
                    st.error("Invalid email or password. Please try again.")
                    
            except Exception as e:
                error_message = str(e)
                if "Invalid login credentials" in error_message:
                    st.error("Invalid email or password. Please check your credentials.")
                elif "Email not confirmed" in error_message:
                    st.error("Please confirm your email address before logging in. Check your inbox for the confirmation email.")
                else:
                    st.error(f"Login failed: {error_message}")

def _signup_form():
    """Sign up form component"""
    st.header("Sign Up")
    with st.form("signup_form"):
        st.subheader("Account Information")
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email*", help="Required field")
            password = st.text_input("Password*", type="password", help="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password*", type="password")
            full_name = st.text_input("Full Name*", help="Required field")
            
        with col2:
            age = st.number_input("Age*", min_value=13, max_value=120, value=25, help="Must be 13 or older")
            sex = st.selectbox("Sex*", ["Male", "Female", "Other", "Prefer not to say"], help="Required field")
            
            # Country selection with real data
            countries = get_countries()
            country = st.selectbox("Country*", [""] + countries, help="Required field")
            
            # Province/City selection with all subdivisions from all countries
            all_subdivisions = get_all_subdivisions()
            province_city = st.selectbox("Province/City*", [""] + all_subdivisions, help="Required field")
        
        st.subheader("Additional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            introduction_source = st.selectbox(
                "What introduced you to this app?*",
                [
                    "Social Media (Facebook, Instagram, etc.)",
                    "Google Search",
                    "Friend/Family Recommendation",
                    "Online Advertisement",
                    "Beauty Blog/Website",
                    "YouTube",
                    "TikTok",
                    "Other"
                ],
                help="Required field"
            )
            
        with col4:
            member_type = st.selectbox(
                "Membership Type*",
                ["Free User", "Premium User"],
                help="Choose your membership level"
            )
        
        submit = st.form_submit_button("Sign Up")

        if submit:
            # Validate required fields
            required_fields = {
                "Email": email,
                "Password": password,
                "Full Name": full_name,
                "Age": age,
                "Sex": sex,
                "Country": country,
                "Province/City": province_city,
                "Introduction Source": introduction_source,
                "Member Type": member_type
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value or value == ""]
            
            if missing_fields:
                st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                return
                
            if password != confirm_password:
                st.error("Passwords don't match!")
                return
            if len(password) < 6:
                st.error("Password must be at least 6 characters!")
                return
            try:
                # Sign up with Supabase Auth including all user metadata
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": full_name,
                            "age": age,
                            "sex": sex,
                            "country": country,
                            "province_city": province_city,
                            "introduction_source": introduction_source,
                            "member_type": member_type
                        }
                    }
                })
                if response.user:
                    st.success("Account created successfully! Please check your email for verification.")
                    st.info("You will be able to log in after confirming your email address.")
                else:
                    st.error("Failed to create account. Please try again.")
            except Exception as e:
                st.error(f"Sign up failed: {str(e)}")
def auth_page():
    """Authentication page component with login and signup tabs"""
    st.title("Customer Management System")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        _login_form()
    with tab2:
        _signup_form()
