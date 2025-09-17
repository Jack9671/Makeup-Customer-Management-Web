import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta

def _filter_data_by_hardcoded_range(df: pd.DataFrame, option: str) -> pd.DataFrame:
    """Filter DataFrame based on predefined time ranges"""
    if df.empty:
        return df
    
    # Convert thời_gian to datetime if it's not already
    df = df.copy()
    df['thời_gian'] = pd.to_datetime(df['thời_gian'])
    
    # Get current date and time
    now = datetime.now()
    today = now.date()
    
    if option == "Hôm nay":
        start_date = today
        end_date = today
    elif option == "Ngày mai":
        tomorrow = today + timedelta(days=1)
        start_date = tomorrow
        end_date = tomorrow
    elif option == "Tuần này":
        # Start of current week (Monday)
        start_date = today - timedelta(days=today.weekday())
        # End of current week (Sunday)
        end_date = start_date + timedelta(days=6)
    elif option == "Tuần sau":
        # Start of next week (Monday)
        start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
        # End of next week (Sunday)
        end_date = start_date + timedelta(days=6)
    elif option == "Tháng này":
        # First day of current month
        start_date = today.replace(day=1)
        # Last day of current month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1)
        else:
            next_month = today.replace(month=today.month + 1)
        end_date = (next_month - timedelta(days=1))
    elif option == "Tháng sau":
        # First day of next month
        if today.month == 12:
            start_date = today.replace(year=today.year + 1, month=1, day=1)
            # Last day of next month
            if start_date.month == 12:
                next_month = start_date.replace(year=start_date.year + 1, month=1)
            else:
                next_month = start_date.replace(month=start_date.month + 1)
        else:
            start_date = today.replace(month=today.month + 1, day=1)
            # Last day of next month
            if start_date.month == 12:
                next_month = start_date.replace(year=start_date.year + 1, month=1)
            else:
                next_month = start_date.replace(month=start_date.month + 1)
        end_date = (next_month - timedelta(days=1))
    elif option == "Năm này":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    elif option == "Năm sau":
        start_date = today.replace(year=today.year + 1, month=1, day=1)
        end_date = today.replace(year=today.year + 1, month=12, day=31)
    elif option == "Tất cả sắp tới":
        return df[df['thời_gian'] >= pd.Timestamp(now)]
    
    # Filter the DataFrame
    start_datetime = pd.Timestamp(start_date)
    end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    
    filtered_df = df[(df['thời_gian'] >= start_datetime) & (df['thời_gian'] <= end_datetime)]
    return filtered_df

def _filter_data_by_custom_range(df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
    """Filter DataFrame based on custom date range"""
    if df.empty:
        return df
    
    # Convert thời_gian to datetime if it's not already
    df = df.copy()
    df['thời_gian'] = pd.to_datetime(df['thời_gian'])
    
    # Convert dates to datetime for comparison
    start_datetime = pd.Timestamp(start_date)
    end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    
    # Filter the DataFrame
    filtered_df = df[(df['thời_gian'] >= start_datetime) & (df['thời_gian'] <= end_datetime)]
    return filtered_df


def upcoming_appointment_section(df):
        st.write("## chọn khoảng thời gian")
        OPTIONS = [
            "Hôm nay", "Ngày mai", "Tuần này", "Tuần sau", 
            "Tháng này", "Tháng sau", "Năm này", "Năm sau", "Tất cả sắp tới"]
        time_config = st.segmented_control("Quãng Thời Gian", ["Có sẵn", "Tự chọn"], selection_mode="single", default="Có sẵn")
        if time_config == "Có sẵn":
            time_option = st.selectbox("Chọn khoảng thời gian có sẵn:", OPTIONS, index=OPTIONS.index(OPTIONS[0]))
            filtered_df = _filter_data_by_hardcoded_range(df, time_option)
        elif time_config == "Tự chọn":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Ngày bắt đầu")
            with col2:
                end_date = st.date_input("Ngày kết thúc")
            if start_date > end_date:
                st.error("Ngày bắt đầu phải trước ngày kết thúc.")
                filtered_df = pd.DataFrame()    
            else:
                filtered_df = _filter_data_by_custom_range(df, start_date, end_date)
        # Display upcoming appointments
        if filtered_df.empty:
            st.info("Không có cuộc hẹn nào trong khoảng thời gian đã chọn.")
        else:
            filtered_df = filtered_df.sort_values(by='thời_gian')
            # Hide user_id, created_at, updated_at, customer_id columns from display
            display_df = filtered_df.drop(columns=['user_id','created_at','updated_at','customer_id'], errors='ignore')
            
            # Calculate summary statistics
            total_customers = len(display_df)
            median_age = display_df['tuổi'].median() if 'tuổi' in display_df.columns and not display_df.empty else 0
            total_deposit = display_df['tiền_cọc'].sum() if 'tiền_cọc' in display_df.columns else 0
            total_remaining = display_df['tiền_còn_lại'].sum() if 'tiền_còn_lại' in display_df.columns else 0
            total_amount = display_df['tiền_tổng'].sum() if 'tiền_tổng' in display_df.columns else 0
            passed_count = display_df['pass'].sum() if 'pass' in display_df.columns else 0
            
            # Display summary metrics
            st.write("## Tổng kết:")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("Tổng khách hàng sắp tới", total_customers)
            with col2:
                st.metric("Độ tuổi trung vị", f"{round(median_age):.0f}" if median_age > 0 else "N/A")
            with col3:
                st.metric("Tổng tiền cọc", f"{total_deposit:,}k")
            with col4:
                st.metric("Tổng tiền còn lại", f"{total_remaining:,}k")
            with col5:
                st.metric("Tổng tiền thu", f"{total_amount:,}k")
            with col6:
                st.metric("Số khách Pass", f"{passed_count} trên {total_customers} người")

            st.write("### Chi tiết:")
            st.dataframe(
                display_df, 
                use_container_width=True, 
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
                        required=True,
                    ),
                    "tiền_còn_lại": st.column_config.NumberColumn(
                        "Tiền Còn Lại",
                        format="%dk VNĐ",
                        min_value=0,
                        required=True,
                    ),
                    "tiền_tổng": st.column_config.NumberColumn(
                        "Tiền Tổng",
                        format="%dk VNĐ",
                        min_value=0,
                        required=True,
                    ),
                    "pass": st.column_config.CheckboxColumn(
                        "Pass",
                        required=True
                    ),
                    "makeup_tone": st.column_config.SelectboxColumn(
                        "Tone Makeup",
                        options= [
                            "Hồng nhẹ",
                            "Hồng đỏ",
                            "Hồng Khói",
                            "Cam đất",
                            "Neutral",
                            "Natural",
                            "Nude",
                            "Chưa biết"
                            ],
                        default="Chưa biết",
                        required=True
                    ), 
                }, 
                hide_index=True,
            )
