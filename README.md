# Modbus-Data-Acquisition-Dashboard
# Industrial Data Logger & Analytics Dashboard

A comprehensive real-time data acquisition system for industrial equipment monitoring. Connect to Modbus devices via serial communication, automatically log sensor data to MySQL database, and perform advanced analytics with interactive visualizations.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

- **Real-time Modbus Communication**: Serial port connectivity with configurable parameters
- **Automated Data Logging**: Continuous background logging with configurable intervals
- **MySQL Integration**: Robust database storage with connection management
- **Gap Filling**: Automatic detection and filling of missing data points
- **Interactive Visualizations**: 
  - Individual parameter plots
  - Combined multi-parameter analysis
  - Subplot comparisons
  - Real-time dashboard updates
- **Advanced Analytics**:
  - Descriptive statistics
  - Time-series analysis
  - Data quality metrics
  - Custom time range filtering
- **Export Capabilities**: Download filtered data as CSV
- **Process Management**: Start/stop logger with status monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server (local or remote)
- Serial port access for Modbus devices
- Windows/Linux/MacOS

## 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/industrial-data-logger.git
cd industrial-data-logger
```

2. **Install required packages**
```bash
pip install streamlit mysql-connector-python pymodbus pandas plotly psutil
```

3. **Setup MySQL Database**
```sql
CREATE DATABASE iasys;
USE iasys;

CREATE TABLE vfd (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Date_Time DATETIME NOT NULL,
    -- Add your sensor columns here
    -- Example: voltage FLOAT, current FLOAT, frequency FLOAT
    INDEX idx_datetime (Date_Time)
);
```

4. **Configure paths in the application**

Edit these paths in the main script to match your system:
```python
ConfigPath = r"C:\path\to\your\config.json"
LoggerScriptPath = r"C:\path\to\your\logger.py"
StatusPath = r"C:\path\to\your\status.json"
```

## 🎯 Usage

### Starting the Application

```bash
streamlit run app.py
```

### Workflow

1. **Configure Modbus Connection**
   - Enter serial port (e.g., COM3 or /dev/ttyUSB0)
   - Set baudrate, stop bits, parity, and data bits
   - Click "Save Modbus"

2. **Setup Database Connection**
   - Enter MySQL host, username, password, and database name
   - Click "Initiate Parameters"

3. **Start Data Logging**
   - Click "▶️ Start Logging" to begin background data collection
   - Monitor status with "🔍 Check Logger Status"
   - View logs with "LOGS" button

4. **Analyze Data**
   - Select time range using the date/time pickers
   - Click "🔍 Retrieve Data" to fetch from database
   - Choose columns to analyze
   - Explore different visualization tabs

5. **Stop Logging**
   - Click "⏹️ Stop Logging" when done

## 📁 Project Structure

```
industrial-data-logger/
│
├── app.py                 # Main Streamlit application
├── logger.py              # Background logging script
├── config.json            # Configuration file (auto-generated)
├── status.json            # Logger status file (auto-generated)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔌 Modbus Configuration

Supported parameters:
- **Baudrate**: 1200 - 115200
- **Stop Bits**: 1 or 2
- **Parity**: None (N), Even (E), Odd (O)
- **Data Bits**: 7 or 8

## 💾 Database Schema

The application expects a table with the following structure:
```sql
CREATE TABLE vfd (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Date_Time DATETIME NOT NULL,
    [your_parameter_1] FLOAT,
    [your_parameter_2] FLOAT,
    [your_parameter_3] FLOAT,
    ...
    INDEX idx_datetime (Date_Time)
);
```

## 📊 Visualization Options

- **Filtered Data Tab**: View and download selected data
- **Individual Plots**: Separate graphs for each parameter
- **Combined Plot**: Overlay multiple parameters
- **Subplots**: Vertically stacked individual plots
- **Summary Statistics**: Descriptive analytics and metrics

## 🛠️ Configuration

### Logging Interval

Default: 1 second (configurable in code)

### Data Gap Filling

Automatically fills missing timestamps with zero values at 1-second intervals

### Cache Settings

Data retrieval is cached for 5 minutes to improve performance

## ⚠️ Important Notes

- Always start Modbus connection before starting the logger
- Ensure MySQL server is running and accessible
- Serial port must not be in use by other applications
- Logger runs as a separate background process
- Stop logger before closing the application

## 🐛 Troubleshooting

**Logger won't start**
- Verify Modbus and MySQL connections are configured
- Check that serial port is available
- Ensure MySQL credentials are correct

**No data retrieved**
- Verify time range contains logged data
- Check database connection parameters
- Ensure logger is running

**Serial port access denied**
- Close other applications using the port
- Run with administrator privileges (Windows)
- Check port permissions (Linux)

## 📈 Performance Tips

- Use appropriate time ranges to avoid loading too much data
- Clear cache if data seems outdated
- Monitor logger status regularly
- Close unused database connections

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Amey**
- LinkedIn: [linkedin.com/in/amey1way](https://www.linkedin.com/in/amey1way/)

## 🙏 Acknowledgments

- Built with Streamlit
- Modbus communication via pymodbus
- Visualizations powered by Plotly
- Database connectivity with MySQL Connector

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub or contact via LinkedIn.

---

**Last Updated**: October 2025
