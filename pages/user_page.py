import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from components.upcoming_appointment_section import upcoming_appointment_section
from components.bar_chart import bar_chart
from components.supabase_client import supabase


@st.cache_data
def get_customer_data(user_id: str) -> pd.DataFrame:
    """Fetch customer data for a specific user"""
    response = supabase.table("customers").select("*").eq("user_id", user_id).execute()
    if response.data:
        df = pd.DataFrame(response.data)
        # Convert thời_gian column to datetime if it exists
        if 'thời_gian' in df.columns and not df.empty:
            df['thời_gian'] = pd.to_datetime(df['thời_gian'], format='ISO8601')
        return df
    else:
        return pd.DataFrame()

### PAGE CONTENT
def user_page():
    #section1: Upcoming Appointments
    #user select one of the hardcoded date ranges (hôm nay, ngày mai, tuần này, tuần sau, tháng này, tháng sau, năm này, năm sau, tất cả)
    user_id = st.session_state.user.id
    df = get_customer_data(user_id)
    tab1, tab2, tab3 = st.tabs(["Cuộc hẹn sắp tới", "Số liệu thống kê", "Quản lý Khách Hàng"])
    with tab1:
        upcoming_appointment_section(df)
    with tab2: 
        st.write("## Số liệu thống kê")
        # Check if we have data and the datetime column
        if df.empty or 'thời_gian' not in df.columns:
            st.info("Không có dữ liệu để hiển thị thống kê.")
            return
        
        DATE_OPTIONS = ["ngày", "tuần", "tháng", "năm"]
        num_of_units = st.number_input(f"Chọn số để xem", min_value=1, value=1, step=1)
        
        # Define time multipliers for each period type
        time_multipliers = {
            "ngày": 1,
            "tuần": 7, 
            "tháng": 30,
            "năm": 365
        }
        
        columns = st.columns(4, border=True)
        
        for i, (col, date_option) in enumerate(zip(columns, DATE_OPTIONS)):
            with col:
                st.subheader(f"{date_option.capitalize()}")
                today = datetime.now()
                today = today.replace(hour=0, minute=0, second=0, microsecond=0)
                days_multiplier = time_multipliers[date_option]
                
                first_date_of_end_period = today - pd.Timedelta(days=num_of_units * days_multiplier)
                first_date_of_start_period = first_date_of_end_period - pd.Timedelta(days=num_of_units * days_multiplier)
                
                mask_from_first_date_of_end_period = df['thời_gian'] >= first_date_of_end_period 
                mask_from_first_date_of_start_period = (df['thời_gian'] >= first_date_of_start_period) & (df['thời_gian'] < first_date_of_end_period)
                
                df_before = df[mask_from_first_date_of_start_period]
                df_after = df[mask_from_first_date_of_end_period]
                
                total_customers_before = len(df_before) if not df_before.empty else 0
                total_customers_after = len(df_after) if not df_after.empty else 0
                total_income_before = df_before['tiền_tổng'].sum() if not df_before.empty else 0
                total_income_after = df_after['tiền_tổng'].sum() if not df_after.empty else 0
                
                pct_change_customers = ((total_customers_after - total_customers_before) / total_customers_before * 100) if total_customers_before > 0 else 0
                pct_change_income = ((total_income_after - total_income_before) / total_income_before * 100) if total_income_before > 0 else 0
                if date_option == "ngày" and num_of_units == 1:
                    st.markdown(f"Thu nhập ngày hôm nay : <span style='color: #1f77b4; font-size: 18px; font-weight: bold;'>{total_income_after:,}k VND</span>", unsafe_allow_html=True)
                    st.markdown(f"Thu nhập ngày hôm qua: <span style='color: #1EB5C9; font-size: 16px; font-weight: bold;'>{total_income_before:,}k VND</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"Thu nhập {num_of_units} {date_option} gần đây: <span style='color: #1f77b4; font-size: 18px; font-weight: bold;'>{total_income_after:,}k VND</span>", unsafe_allow_html=True)
                    st.markdown(f"Thu nhập {num_of_units} {date_option} trước đó: <span style='color: #1EB5C9; font-size: 16px; font-weight: bold;'>{total_income_before:,}k VND</span>", unsafe_allow_html=True)

                if pct_change_income > 0:
                    st.success(f"Tăng **{pct_change_income:.1f}%** so với trước đó")
                elif pct_change_income < 0:
                    st.error(f"Giảm **{abs(pct_change_income):.1f}%** so với trước đó")
                elif total_income_before == 0 and total_income_after == 0:
                    pass
                
                st.divider()
                if date_option == "ngày" and num_of_units == 1:
                    st.markdown(f"Số khách hàng ngày hôm nay: <span style='color: #ff7f0e; font-size: 18px; font-weight: bold;'>{total_customers_after} người</span>", unsafe_allow_html=True)
                    st.markdown(f"Số khách hàng ngày hôm qua: <span style='color: #1EB5C9; font-size: 16px; font-weight: bold;'>{total_customers_before} người</span>", unsafe_allow_html=True)
                else:     
                    st.markdown(f"Số khách hàng {num_of_units} {date_option} gần đây: <span style='color: #ff7f0e; font-size: 18px; font-weight: bold;'>{total_customers_after} người</span>", unsafe_allow_html=True)
                    st.markdown(f"Số khách hàng {num_of_units} {date_option} trước đó: <span style='color: #1EB5C9; font-size: 16px; font-weight: bold;'>{total_customers_before} người</span>", unsafe_allow_html=True)

                if pct_change_customers > 0:
                    st.success(f"Tăng **{pct_change_customers:.1f}%** so với trước đó")
                elif pct_change_customers < 0:
                    st.error(f"Giảm **{abs(pct_change_customers):.1f}%** so với trước đó")
                elif total_customers_before == 0 or total_customers_after == 0:
                    pass
                else:
                    st.info("Không thay đổi so với trước đó")

        st.divider()
        st.write("### Biểu đồ thống kê")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Chọn ngày bắt đầu", value=today - pd.Timedelta(days=30), key="start_date")
        with col2:
            end_date = st.date_input("Chọn ngày kết thúc", value=today, key="end_date")
        col1,col2 = st.columns(2)
        with col1:
            x_axis_option = st.selectbox("Chọn chu kỳ", DATE_OPTIONS, key="x_axis_option") # chu kỳ represents a bar, where x axis range represents the day, month, year in which the start_date and end_date are within
        with col2:
            y_axis_option = st.selectbox("Chọn biến", ["tiền_tổng", "khách_hàng"], key="y_axis_option")
        if start_date > end_date:
            st.error("Ngày bắt đầu phải trước ngày kết thúc.")
        elif end_date > today.date():
            st.error("Ngày kết thúc không thể là ngày trong tương lai. Vui lòng chọn ngày hôm nay hoặc ngày trong quá khứ.")
        else:
            # Filter data based on selected date range
            mask_date_range = (df['thời_gian'] >= pd.Timestamp(start_date)) & (df['thời_gian'] <= pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
            df_filtered = df[mask_date_range]
            
            if df_filtered.empty:
                st.info("Không có dữ liệu trong khoảng thời gian đã chọn.")
            else:
                fig = bar_chart(df_filtered, x_axis_option, y_axis_option)
                st.plotly_chart(fig, use_container_width=True)
    with tab3:
        #users can select a number of fields to filter. 
        FILTERABLE_OPTIONS = ["thời_gian", "tuổi", "tiền_tổng"]
        SEARCHABLE_FIELDS = ["tên", "số_điện_thoại", "địa_chỉ", "pass", "makeup_tone"]
        st.write("## Quản lý Khách Hàng")
        with st.expander("Bộ lọc và Tìm kiếm"):
            #apply filter first, then search within the filtered data
            col1, col2 = st.columns(2)
            with col1:
                selected_filters = st.multiselect("Bộ lọc", FILTERABLE_OPTIONS)
                #for Thời Gian, create date input for start date and end date
                #for "Tuổi", "Tiền Tổng", use range slider 
                if "thời_gian" in selected_filters:
                    # Ensure thời_gian is datetime before filtering
                    if not df.empty and 'thời_gian' in df.columns:
                        if not pd.api.types.is_datetime64_any_dtype(df['thời_gian']):
                            df['thời_gian'] = pd.to_datetime(df['thời_gian'])
                    col_start, col_end = st.columns(2)
                    with col_start:
                        start_date = st.date_input("Ngày bắt đầu", key="start_date_filter")
                    with col_end:
                        end_date = st.date_input("Ngày kết thúc", key="end_date_filter")
                    if start_date > end_date:
                        st.error("Ngày bắt đầu phải trước ngày kết thúc.")
                    else:
                        # Convert dates to datetime with proper time bounds
                        start_datetime = pd.Timestamp(start_date)
                        end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                        df = df[(df['thời_gian'] >= start_datetime) & (df['thời_gian'] <= end_datetime)]
                if "tuổi" in selected_filters:
                    min_age, max_age = st.slider("Chọn độ tuổi", 0, 120, (0, 120), key="age_filter", format = "%d tuổi")
                    df = df[(df['tuổi'] >= min_age) & (df['tuổi'] <= max_age)]
                if "tiền_tổng" in selected_filters:
                    min_total, max_total = st.slider("Chọn khoảng tiền tổng", 0, 10000, (0, 10000), key="total_filter", step=100, format="%dk VNĐ")
                    df = df[(df['tiền_tổng'] >= min_total) & (df['tiền_tổng'] <= max_total)]
            with col2:
                selected_searchable_fields = st.multiselect("Tìm kiếm bằng", SEARCHABLE_FIELDS, default=SEARCHABLE_FIELDS[0])
                for field in selected_searchable_fields:
                    search_query = st.text_input(f"{field}", key=f"search_{field}", width=200)
                    if search_query:
                        df = df[df[field].astype(str).str.contains(search_query, case=False, na=False)]

        #finally, display editable dataframe with option to add new rows and column configuration
        df_display = df.copy()
        if not df_display.empty and 'thời_gian' in df_display.columns:
            df_display['thời_gian'] = pd.to_datetime(df_display['thời_gian'])
        
        # Clean name field - capitalize first letter of each word
        if not df_display.empty and 'tên' in df_display.columns:
            df_display['tên'] = df_display['tên'].astype(str).str.title()
        
        # Format phone numbers to show leading zeros (10 digits for Vietnamese phones)
        if not df_display.empty and 'số_điện_thoại' in df_display.columns:
            df_display['số_điện_thoại'] = df_display['số_điện_thoại'].astype(str).str.zfill(10)
        
        # Hide user_id, created_at, updated_at, customer_id columns from display
        display_columns = [col for col in df_display.columns if col not in ['user_id', 'created_at', 'updated_at', 'customer_id']]
        df_for_editing = df_display[display_columns].copy()
        #sort by time where newest appointment is on the top
        df_for_editing = df_for_editing.sort_values(by='thời_gian', ascending=False).reset_index(drop=True)
        
        # Display editable dataframe with proper column configuration
        edited_df = st.data_editor(
            df_for_editing,
            use_container_width=True,
            num_rows="dynamic", 
            column_config={
                "thời_gian": st.column_config.DatetimeColumn(
                    "Thời Gian",
                    format="DD/MM/YYYY, HH:mm",
                    step=60,
                    required=True,
                ),
                "tên": st.column_config.TextColumn(
                    "Tên",
                    required=True,
                ),
                "tuổi": st.column_config.NumberColumn(
                    "Tuổi",
                    min_value=1,
                    max_value=120,
                    step=1,
                    format="%d tuổi",
                    required=True,
                ),
                "địa_chỉ": st.column_config.TextColumn(
                    "Địa Chỉ",
                    required=True,
                ),
                "số_điện_thoại": st.column_config.TextColumn(
                    "Số Điện Thoại",
                    required=True,
                ),
                "tiền_cọc": st.column_config.NumberColumn(
                    "Tiền Cọc",
                    format="%dk VNĐ",
                    min_value=0,
                    required=True
                ),
                "tiền_còn_lại": st.column_config.NumberColumn(
                    "Tiền Còn Lại",
                    format="%dk VNĐ",
                    min_value=0,
                    required=True
                ),
                "tiền_tổng": st.column_config.NumberColumn(
                    "Tiền Tổng",
                    format="%dk VNĐ",
                    min_value=0,
                    required=True
                ),
                "pass": st.column_config.CheckboxColumn(
                    "Pass",
                    required=True
                ),
                "makeup_tone": st.column_config.TextColumn(
                    "Tone Makeup",
                    required=True
                ),
            },
            hide_index=True,
        )
        

        # Validation check for required fields
        required_fields = ['thời_gian', 'tên', 'tuổi', 'địa_chỉ', 'số_điện_thoại', 'tiền_cọc', 'tiền_còn_lại', 'tiền_tổng', 'pass', 'makeup_tone']
        has_empty_required_fields = False
        has_invalid_phone = False
        empty_fields = []
        
        for field in required_fields:
            if field in edited_df.columns:
                # Check for null/empty values in required fields
                if edited_df[field].isna().any() or (edited_df[field] == '').any():
                    has_empty_required_fields = True
                    empty_fields.append(field)
        
        # Validate phone numbers
        if 'số_điện_thoại' in edited_df.columns:
            for idx, phone in edited_df['số_điện_thoại'].items():
                if pd.notna(phone) and phone != '':
                    phone_str = str(phone).strip()
                    if not phone_str.isdigit(): # checks if phone contains only digits
                        has_invalid_phone = True
                        break
        
        if has_empty_required_fields:
            st.warning(f"⚠️ **Cảnh báo:** Vui lòng điền đầy đủ các trường bắt buộc trước khi lưu thay đổi. Các trường còn thiếu: {', '.join(empty_fields)}")
            update_button_disabled = True
        elif has_invalid_phone:
            st.warning("⚠️ **Cảnh báo:** Vui lòng kiểm tra lại định dạng Số Điện Thoại. Số điện thoại chỉ nên bao gồm chữ số và không chứa ký tự đặc biệt hoặc khoảng trắng.")
            update_button_disabled = True
        else:
            update_button_disabled = False
        
        # Update button
        if st.button("🔄 Cập nhật dữ liệu", type="primary", use_container_width=True, disabled=update_button_disabled):
            try:
                # Clean name field in edited data
                if 'tên' in edited_df.columns:
                    edited_df['tên'] = edited_df['tên'].astype(str).str.title()
                
                # Add back customer_id from original data for tracking
                original_customer_ids = df_display['customer_id'].reset_index(drop=True)
                
                # Add user_id and customer_id to edited data
                edited_df_with_ids = edited_df.copy()
                edited_df_with_ids['user_id'] = user_id
                edited_df_with_ids['customer_id'] = None

                # Handle customer_ids more carefully - existing rows get their original ID, new rows get None
                customer_ids = []
                for i in range(len(edited_df)):
                    if i < len(original_customer_ids):
                        # Existing row - use original customer_id
                        customer_ids.append(original_customer_ids.iloc[i])
                    else:
                        # New row - no customer_id
                        customer_ids.append(None)
                
                edited_df_with_ids['customer_id'] = customer_ids
                
                # Separate new rows (without customer_id) and existing rows
                new_rows = edited_df_with_ids[edited_df_with_ids['customer_id'].isna()]
                existing_rows = edited_df_with_ids[edited_df_with_ids['customer_id'].notna()]
                numeric_fields = ['tuổi', 'tiền_cọc', 'tiền_còn_lại', 'tiền_tổng']  # Removed số_điện_thoại as it's now text

                # Insert new rows
                if not new_rows.empty:
                    # Completely remove customer_id column for new rows to avoid conflicts
                    new_rows_for_insert = new_rows.drop(columns=['customer_id'])
                    new_rows_dict = new_rows_for_insert.to_dict('records')
                    
                    # Convert data types and handle datetime serialization
                    for record in new_rows_dict:
                        for key, value in record.items():
                            if pd.api.types.is_datetime64_any_dtype(type(value)) or isinstance(value, pd.Timestamp):
                                record[key] = value.isoformat() if pd.notna(value) else None
                            elif key in numeric_fields and pd.notna(value):
                                # Convert float to int for numeric fields
                                record[key] = int(float(value))
                    
                    insert_response = supabase.table("customers").insert(new_rows_dict).execute()
                    if insert_response.data:
                        st.success(f"✅ Đã thêm {len(new_rows_dict)} khách hàng mới!")
                
                # Update existing rows
                if not existing_rows.empty:
                    for _, row in existing_rows.iterrows():
                        customer_id = int(row['customer_id'])
                        update_data = row.drop(['customer_id']).to_dict()
                        
                        # Convert data types and handle datetime serialization
                        for key, value in update_data.items():
                            if pd.api.types.is_datetime64_any_dtype(type(value)) or isinstance(value, pd.Timestamp):
                                update_data[key] = value.isoformat() if pd.notna(value) else None
                            elif key in numeric_fields and pd.notna(value):
                                # Convert float to int for numeric fields
                                update_data[key] = int(float(value))
                                
                        
                        update_response = supabase.table("customers").update(update_data).eq("customer_id", customer_id).execute()
                    
                    st.success(f"✅ Đã cập nhật {len(existing_rows)} khách hàng!")
                
                # Handle deleted rows (rows that exist in original df but not in edited_df)
                if len(edited_df) < len(df_display):
                    # Some rows were deleted
                    deleted_count = len(df_display) - len(edited_df)
                    deleted_ids = original_customer_ids[len(edited_df):].dropna()
                    
                    if not deleted_ids.empty:
                        for customer_id in deleted_ids:
                            delete_response = supabase.table("customers").delete().eq("customer_id", int(customer_id)).execute()
                        st.success(f"✅ Đã xóa {len(deleted_ids)} khách hàng!")
                
                # Clear cache and rerun to show updated data
                get_customer_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Lỗi khi cập nhật dữ liệu: {str(e)}")

        # Download section
        if not df_for_editing.empty:
            st.write("### Tải xuống dữ liệu đã được lọc và tìm kiếm")
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV download
                csv_data = df_for_editing.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Tải xuống CSV",
                    data=csv_data,
                    file_name=f"customer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Excel download
                def convert_df_to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Khách Hàng')
                        # Get the workbook and worksheet
                        workbook = writer.book
                        worksheet = writer.sheets['Khách Hàng']
                        
                        # Auto-adjust column widths
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    output.seek(0)
                    return output.getvalue()
                
                excel_data = convert_df_to_excel(df_for_editing)
                st.download_button(
                    label="📊 Tải xuống Excel",
                    data=excel_data,
                    file_name=f"customer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
