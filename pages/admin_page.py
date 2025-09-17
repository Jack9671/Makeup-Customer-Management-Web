import streamlit as st
import pandas as pd
from components.supabase_client import supabase

def view_all_users():
    """Admin function to view all registered users"""
    st.header("All Registered Users")
    
    try:
        # Get all users from auth.users (admin only)
        response = supabase.auth.admin.list_users()
        
        if response:
            users_data = []
            for user in response:
                # Count customers for each user
                customer_count = 0
                try:
                    customer_response = supabase.table("customers").select("customer_id").eq("user_id", user.id).execute()
                    customer_count = len(customer_response.data) if customer_response.data else 0
                except:
                    customer_count = 0
                
                # Extract user metadata
                metadata = user.user_metadata or {}
                users_data.append({
                    "ID": user.id,
                    "Email": user.email,
                    "Full Name": metadata.get('full_name', 'N/A'),
                    "Age": metadata.get('age', 'N/A'),
                    "Sex": metadata.get('sex', 'N/A'),
                    "Country": metadata.get('country', 'N/A'),
                    "Province/City": metadata.get('province_city', 'N/A'),
                    "Introduction Source": metadata.get('introduction_source', 'N/A'),
                    "Member Type": metadata.get('member_type', 'N/A'),
                    "Customer Count": customer_count,
                    "Email Confirmed": "Yes" if user.email_confirmed_at else "No",
                    "Created": user.created_at,
                    "Last Sign In": user.last_sign_in_at
                })
            
            if users_data:
                df = pd.DataFrame(users_data)
                # Display user information with expandable sections
                st.subheader("User Overview")
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Users", len(users_data))
                with col2:
                    confirmed_users = sum(1 for u in users_data if u["Email Confirmed"] == "Yes")
                    st.metric("Confirmed Users", confirmed_users)
                with col3:
                    premium_users = sum(1 for u in users_data if u["Member Type"] == "Premium User")
                    st.metric("Premium Users", premium_users)
                with col4:
                    total_customers = sum(u["Customer Count"] for u in users_data)
                    st.metric("Total Customers", total_customers)
                # Full user table
                st.subheader("Detailed User Information")
                st.dataframe(df, use_container_width=True)
                # User selection for detailed view
                st.subheader("View User's Customer Data")
                selected_user = st.selectbox("Select user to view their customers:", 
                                           options=[u["ID"] for u in users_data],
                                           format_func=lambda x: next(f"{u['Email']} ({u['Full Name']})" for u in users_data if u["ID"] == x))
                if st.button("View User's Customers"):
                    view_user_data(selected_user)
                    
                # Demographics analysis
                st.subheader("User Demographics")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Age distribution
                    ages = [u["Age"] for u in users_data if u["Age"] != 'N/A']
                    if ages:
                        st.write("**Age Statistics:**")
                        st.write(f"- Average Age: {sum(ages)/len(ages):.1f}")
                        st.write(f"- Age Range: {min(ages)} - {max(ages)}")
                
                with col2:
                    # Member type distribution
                    member_types = [u["Member Type"] for u in users_data if u["Member Type"] != 'N/A']
                    if member_types:
                        from collections import Counter
                        type_counts = Counter(member_types)
                        st.write("**Membership Distribution:**")
                        for mtype, count in type_counts.items():
                            st.write(f"- {mtype}: {count}")
                            
            else:
                st.info("No users found.")
                
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        st.info("Note: This feature requires admin privileges and proper Supabase configuration.")

def view_user_data(user_id):
    """Admin function to view a specific user's customer data"""
    try:
        # Get user info first
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        user_email = user_response.user.email if user_response.user else "Unknown"
        
        # Get customer data from shared table
        response = supabase.table("customers").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            st.subheader(f"Customer data for user: {user_email}")
            df = pd.DataFrame(response.data)
            # Reorder columns for better display
            column_order = ["customer_id", "tên", "tuổi", "số_điện_thoại", "địa_chỉ", 
                          "thời_gian", "tiền_cọc", "tiền_còn_lại", "tiền_tổng", 
                          "pass", "makeup_tone", "created_at", "updated_at"]
            df = df[column_order]
            st.dataframe(df, use_container_width=True)
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Customers", len(df))
            with col2:
                total_down = df['tiền_cọc'].sum()
                st.metric("Down Payments", f"{total_down:,}")
            with col3:
                total_remaining = df['tiền_còn_lại'].sum()
                st.metric("Remaining Payments", f"{total_remaining:,}")
            with col4:
                total_payments = df['tiền_tổng'].sum()
                st.metric("Total Revenue", f"{total_payments:,}")
        else:
            st.info("This user has no customer data.")
            
    except Exception as e:
        st.error(f"Error loading user data: {str(e)}")

def view_all_customers():
    """Admin function to view all customers across all users"""
    st.header("All Customers")
    
    try:
        response = supabase.table("customers").select("*").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Add user email for better identification
            user_emails = {}
            for customer in response.data:
                user_id = customer['user_id']
                if user_id not in user_emails:
                    try:
                        user_response = supabase.auth.admin.get_user_by_id(user_id)
                        user_emails[user_id] = user_response.user.email if user_response.user else "Unknown"
                    except:
                        user_emails[user_id] = "Unknown"
            
            df['user_email'] = df['user_id'].map(user_emails)
            
            # Reorder columns
            column_order = ["customer_id", "user_email", "tên", "tuổi", "số_điện_thoại", 
                          "địa_chỉ", "thời_gian", "tiền_cọc", "tiền_còn_lại", 
                          "tiền_tổng", "pass", "makeup_tone", "created_at"]
            df = df[column_order]
            
            st.dataframe(df, use_container_width=True)
            
            # Show overall statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Customers", len(df))
            with col2:
                total_down = df['tiền_cọc'].sum()
                st.metric("Total Down Payments", f"{total_down:,}")
            with col3:
                total_remaining = df['tiền_còn_lại'].sum()
                st.metric("Total Remaining", f"{total_remaining:,}")
            with col4:
                total_revenue = df['tiền_tổng'].sum()
                st.metric("Total Revenue", f"{total_revenue:,}")
        else:
            st.info("No customers found.")
            
    except Exception as e:
        st.error(f"Error loading customers: {str(e)}")

def manage_users():
    """Admin function to manage users"""
    st.header("User Management")
    
    # You can add more admin functions here like:
    # - Delete users
    # - Reset passwords
    # - View user statistics
    # etc.
    
    st.info("Additional user management features can be added here.")

def show_admin_dashboard():
    """Admin dashboard component"""
    '''
    st.title("Admin Dashboard")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()
    
    with col1:
        st.write("Welcome, Administrator!")
    
    # Admin functionality
    tab1, tab2, tab3 = st.tabs(["All Customers", "View Users", "User Management"])
    
    with tab1:
        view_all_customers()
    
    with tab2:
        view_all_users()
    
    with tab3:
        manage_users()
        '''
    return

