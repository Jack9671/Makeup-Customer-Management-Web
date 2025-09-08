import streamlit as st
from .supabase_client import supabase

def create_customers_table():
    """Create a shared customers table with RLS enabled"""
    try:
        # First, try to create using RPC call
        query = """
            -- 1️⃣ Shared customers table
            CREATE TABLE IF NOT EXISTS customers (
                customer_id   SERIAL PRIMARY KEY,
                user_id       uuid REFERENCES auth.users (id) ON DELETE CASCADE,
                tên          text NOT NULL,
                tuổi           integer CHECK (tuổi > 0 AND tuổi <= 120),
                địa_chỉ  text NOT NULL,
                thời_gian timestamp NOT NULL,
                số_điện_thoại  integer NOT NULL,
                tiền_cọc       integer DEFAULT 0 CHECK (tiền_cọc >= 0),
                tiền_còn_lại   integer DEFAULT 0 CHECK (tiền_còn_lại >= 0),
                tiền_tổng      integer DEFAULT 0 CHECK (tiền_tổng >= 0),
                pass           BOOLEAN DEFAULT FALSE,
                makeup_tone    text DEFAULT 'Natural',
                created_at     timestamptz DEFAULT now(),
                updated_at     timestamptz DEFAULT now()
            );

            -- 2️⃣ Index for the RLS condition (optional but recommended)
            CREATE INDEX IF NOT EXISTS idx_customers_user_id
                ON customers (user_id);

            -- 3️⃣ Enable Row‑Level Security
            ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

            -- 4️⃣ RLS policy – users can only see/modify their own rows
            -- (no IF NOT EXISTS – not supported by CREATE POLICY)
            CREATE POLICY "Users can only access their own data"
                ON customers
                FOR ALL
                TO authenticated
                USING (auth.uid() = user_id);
        """
        
        supabase.postgrest.rpc('exec_sql', {'sql': query}).execute()
        st.success("Customers table created successfully!")
        
    except Exception as e:
        error_message = str(e)
        if "already exists" in error_message:
            st.info("Customers table already exists.")
        elif "exec_sql" in error_message:
            st.error("⚠️ **Setup Required: Missing exec_sql function**")
            st.warning("The exec_sql function doesn't exist in your Supabase database.")
            
            st.info("**Please follow these steps to set up your database:**")
            
            st.subheader("Step 1: Create the exec_sql function")
            st.code("""
            -- Create the exec_sql function in Supabase SQL Editor
            CREATE OR REPLACE FUNCTION exec_sql(sql text)
            RETURNS void AS $$
            BEGIN
            EXECUTE sql;
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;

            -- Grant permission to authenticated users
            GRANT EXECUTE ON FUNCTION exec_sql TO authenticated;
            """, language="sql")
            
            st.subheader("Step 2: Create the customers table")
            st.code("""
            -- Create the customers table directly
            CREATE TABLE IF NOT EXISTS customers (
                customer_id   SERIAL PRIMARY KEY,
                user_id       uuid REFERENCES auth.users (id) ON DELETE CASCADE,
                tên          text NOT NULL,
                tuổi           integer CHECK (tuổi > 0 AND tuổi <= 120),
                địa_chỉ  text NOT NULL,
                ngày date NOT NULL,
                thời_gian timestamp NOT NULL,
                số_điện_thoại  integer NOT NULL,
                tiền_cọc       integer DEFAULT 0 CHECK (tiền_cọc >= 0),
                tiền_còn_lại   integer DEFAULT 0 CHECK (tiền_còn_lại >= 0),
                tiền_tổng      integer DEFAULT 0 CHECK (tiền_tổng >= 0),
                pass           BOOLEAN DEFAULT FALSE,
                makeup_tone    text DEFAULT 'Natural',
                created_at     timestamptz DEFAULT now(),
                updated_at     timestamptz DEFAULT now()
            );

            -- Index for better performance
            CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers (user_id);

            -- Enable Row Level Security
            ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

            -- Create RLS policy
            CREATE POLICY "Users can only access their own data"
            ON customers
            FOR ALL
            TO authenticated
            USING (auth.uid() = user_id);
                        """, language="sql")
            
            st.info("""
            **Instructions:**
            1. Go to your Supabase Dashboard
            2. Navigate to SQL Editor
            3. Copy and run the SQL code above (both steps)
            4. Refresh this page and try again
            """)
        else:
            st.error(f"Error creating customers table: {error_message}")
        
