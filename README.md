# Makeup Customer Management Website

A comprehensive customer management web application built with Streamlit for makeup and beauty service businesses. This application helps manage customer information, appointments, analytics, and provides data visualization tools.

## Features

### 🎯 Customer Management
- **CRUD Operations**: Add, edit, and delete customer records
- **Advanced Filtering**: Filter customers by date, age, and total amount
- **Search Functionality**: Search across multiple fields (name, phone, address, etc.)
- **Data Export**: Download customer data in CSV or Excel format

### 📊 Analytics & Reporting
- **Statistical Dashboard**: View revenue and customer metrics
- **Time-based Analysis**: Compare performance across different time periods (day, week, month, year)
- **Interactive Charts**: Visualize data with Plotly charts
- **Trend Analysis**: Track growth and changes over time

### 📅 Appointment Management
- **Upcoming Appointments**: View appointments by various time ranges
- **Date Filtering**: Filter appointments by today, tomorrow, this week, next week, etc.
- **Appointment Tracking**: Monitor appointment status and details

### 🔐 Authentication
- **User Authentication**: Secure login system with Supabase
- **User-specific Data**: Each user sees only their own customer data
- **Session Management**: Secure session handling

### 💄 Makeup Customization
- **Tone Selection**: Choose from 27+ makeup tone options
- **Customer Preferences**: Track individual customer makeup preferences
- **Service Tracking**: Monitor service completion status

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **Data Visualization**: Plotly
- **Data Processing**: Pandas
- **Authentication**: Supabase Auth
- **File Export**: openpyxl for Excel, built-in CSV

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Jack9671/Makeup-Customer-Management-Web.git
   cd Makeup-Customer-Management-Web
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

5. **Run the application**:
   ```bash
   streamlit run main.py
   ```

## Project Structure

```
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── components/            # Reusable components
│   ├── __init__.py
│   ├── bar_chart.py      # Chart components
│   ├── customer_management_section.py
│   ├── supabase_client.py # Database connection
│   ├── upcoming_appointment_section.py
│   └── create_customer_table.py
└── pages/                 # Application pages
    ├── admin_page.py     # Admin dashboard
    ├── auth_page.py      # Authentication page
    └── user_page.py      # User dashboard
```

## Database Schema

The application uses Supabase with the following main table:

### Customers Table
- `customer_id` (Primary Key): Unique identifier
- `user_id`: Links customer to specific user
- `tên`: Customer name
- `tuổi`: Customer age
- `địa_chỉ`: Customer address
- `số_điện_thoại`: Phone number
- `thời_gian`: Appointment datetime
- `tiền_cọc`: Deposit amount
- `tiền_còn_lại`: Remaining amount
- `tiền_tổng`: Total amount
- `pass`: Service completion status
- `makeup_tone`: Selected makeup tone
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

## Usage

### For Users
1. **Login**: Use your credentials to access the system
2. **View Dashboard**: See upcoming appointments and statistics
3. **Manage Customers**: Add, edit, or delete customer records
4. **Filter & Search**: Use advanced filtering to find specific customers
5. **Export Data**: Download customer data for external use

### For Administrators
- Access to all user data
- System-wide analytics
- User management capabilities

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please contact the development team or create an issue in the GitHub repository.

## Acknowledgments

- Built with ❤️ for makeup and beauty professionals
- Thanks to the Streamlit and Supabase communities
- Special thanks to all contributors and testers

---

**Note**: Make sure to set up your Supabase database and configure the environment variables before running the application.
