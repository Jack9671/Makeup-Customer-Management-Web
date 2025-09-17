import pandas as pd
import plotly.express as px
def bar_chart(df_filtered: pd.DataFrame, x_axis_option: str, y_axis_option: str) -> px.bar:
    # Group and aggregate data based on x_axis_option and y_axis_option
    if x_axis_option == "ngày":
        df_filtered['period'] = df_filtered['thời_gian'].dt.date
    elif x_axis_option == "tuần":
        df_filtered['period'] = df_filtered['thời_gian'].dt.to_period('W').apply(lambda r: r.start_time.date())
    elif x_axis_option == "tháng":
        df_filtered['period'] = df_filtered['thời_gian'].dt.to_period('M').apply(lambda r: r.start_time.date())
    elif x_axis_option == "năm":
        df_filtered['period'] = df_filtered['thời_gian'].dt.to_period('Y').apply(lambda r: r.start_time.date())
    
    if y_axis_option == "tiền_tổng":
        df_grouped = df_filtered.groupby('period')['tiền_tổng'].sum().reset_index()
        y_label = "Tổng Thu Nhập (k VND)"
    elif y_axis_option == "khách_hàng":
        df_grouped = df_filtered.groupby('period').size().reset_index(name='khách_hàng')
        y_label = "Số Khách Hàng"
    
    # Sort by period
    df_grouped = df_grouped.sort_values(by='period')
    
    # Create bar chart using Plotly
    fig = px.bar(df_grouped, x='period', y=df_grouped.columns[1], 
                 labels={'period': 'Thời Gian', df_grouped.columns[1]: y_label}, 
                 title=f"{y_label} theo {x_axis_option}")
    fig.update_layout(xaxis_title='Thời Gian', yaxis_title=y_label)
    if x_axis_option == "ngày" or x_axis_option == "tuần":
        fig.update_xaxes(tickformat='%d/%m/%Y')
    if x_axis_option == "tháng":
        fig.update_xaxes(tickformat='%m/%Y')
    if x_axis_option == "năm":
        fig.update_xaxes(tickformat='%Y')
    return fig