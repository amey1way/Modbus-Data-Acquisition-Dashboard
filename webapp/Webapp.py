#libraries required
import streamlit as st
import mysql.connector
import time
from datetime import datetime, timedelta
from pymodbus.client import ModbusSerialClient
import json
import os
import subprocess
import signal
import psutil
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Inistialising Session State
if 'ModbusClient' not in st.session_state:
  st.session_state.ModbusClient = None
if 'Mysql' not in st.session_state:
  st.session_state.Mysql = None
if 'Logger' not in st.session_state:
  st.session_state.Logger = False

# WEb application Start
st.title("Industrial Data Logger & Analytics Dashboard")
st.caption("Real-time Modbus data acquisition with MySQL storage and comprehensive visualization tools")
st.divider()

st.header("Modbus to MySQL Data Pipeline with Advanced Analytics")
st.write("""
This dashboard provides a complete solution for industrial data monitoring and analysis. Connect to Modbus devices 
via serial communication, automatically log sensor data to a MySQL database, and perform real-time analytics with 
interactive visualizations. Features include configurable data logging intervals, gap filling for missing data points, 
multi-parameter trend analysis, and comprehensive statistical summaries. Perfect for monitoring VFDs, sensors, and 
other industrial equipment with historical data analysis capabilities.
""")

with st.expander("📖 How to Use This Dashboard"):
    st.write("""
    1. **Configure Modbus**: Set your serial port parameters
    2. **Setup Database**: Enter MySQL connection details  
    3. **Start Logging**: Begin data collection from your devices
    4. **Analyze Data**: Select time ranges and visualize trends
    5. **Export Results**: Download filtered data for further analysis
    """)


st.divider()

st.subheader("Modbus")
st.warning(":warning: Always Start Modbus Connection Before Data Logger!")

port = st.text_input("Serial Port (e.g. COM3 or /dev/ttyUSB0)", "COM3")
baudrate = st.number_input("Baudrate", 1200, 115200, 9600)  
stopbits = st.selectbox("Stop Bits", [1, 2])
parity = st.selectbox("Parity", ["N", "E", "O"])
bytesize = st.selectbox("Data Bits", [7, 8])

#modbus back ground code
if st.button("Save Modbus", use_container_width=True):
    if st.session_state.ModbusClient is None:
        st.success("Saved!")
        st.session_state.ModbusClient = True
    else:
        st.warning("Already connected")

# Disconnect button
if st.button("❌ Reset", use_container_width=True):
    if st.session_state.ModbusClient:
        st.session_state.ModbusClient = None
        st.success("Removed Modbus Details")
    else:
        st.warning("No active Modbus parameters")

st.divider()
st.subheader("Database Connection")
col1, col2 = st.columns(2)
with col1:
    host = st.text_input("HOST" ,"localhost")
    user = st.text_input("Username","root")
with col2:
    password = st.text_input("Password","Amey1105!" , type="password")
    database = st.text_input("Database", "iasys")

table ="vfd"

if st.button("Initiate Parameters", use_container_width=True ):
  if st.session_state.Mysql is None:
        st.success("Saved!")
        st.session_state.Mysql = True
  else:
        st.warning("Already Saved!")

if st.button("Reset SQL", use_container_width=True):
    if st.session_state.Mysql:
        st.session_state.Mysql = None
        st.success("Reset!")
    else:
        st.warning("None Given")




st.divider()
st.subheader("Logging")

# Define paths - make sure they match your logger.py exactly
ConfigPath = r"C:\Users\ADMIN\Desktop\IASYS\config.json"
LoggerScriptPath = r"C:\Users\ADMIN\Desktop\IASYS\logger.py"  # Full path to logger.py

if st.button("▶️ Start Logging", use_container_width=True):
    if st.session_state.ModbusClient and st.session_state.Mysql:
        try:
            # Prepare config with the exact same structure your logger expects
            cfg = {
                "modbus": {
                    "port": port,
                    "baudrate": baudrate,
                    "stopbits": stopbits,
                    "parity": parity,
                    "bytesize": bytesize
                },
                "mysql": {
                    "host": host,
                    "user": user,
                    "password": password,
                    "database": database
                },
                "interval": 1
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(ConfigPath), exist_ok=True)
            
            # Write config file
            with open(ConfigPath, "w") as f:
                json.dump(cfg, f, indent=2)
            
            st.info(f"Config written to: {ConfigPath}")
            
            # Check if logger is already running
            if "Logger" not in st.session_state:
                st.session_state.Logger = None
                
            if st.session_state.Logger is None or st.session_state.Logger.poll() is not None:
                # Start logger process from the correct directory
                working_dir = os.path.dirname(LoggerScriptPath)
                
                proc = subprocess.Popen(
                    ["python", "logger.py"],
                    cwd=working_dir,  # Set working directory
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                st.session_state.Logger = proc
                st.success(f"Logger started with PID: {proc.pid}")
                time.sleep(1)  # Give it a moment to start
                
                # Verify it's actually running
                if proc.poll() is None:
                    st.success("✅ Logger is running successfully")
                else:
                    st.error("❌ Logger failed to start")
                    st.session_state.Logger = None
            else:
                st.warning("Logger already running")
                
        except Exception as e:
            st.error(f"Error starting logger: {e}")
            st.session_state.Logger = None
    else:
        st.error("Connect Modbus and SQL first!")

if st.button("⏹️ Stop Logging", use_container_width=True):
    if "Logger" in st.session_state and st.session_state.Logger is not None:
        try:
            proc = st.session_state.Logger
            
            # Check if process is still running
            if proc.poll() is None:
                st.info(f"Stopping logger process (PID: {proc.pid})...")
                
                # Try graceful termination first
                if os.name == 'nt':  # Windows
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                else:  # Unix/Linux
                    proc.terminate()
                
                # Wait a bit for graceful shutdown
                try:
                    proc.wait(timeout=5)
                    st.success("Logger stopped gracefully")
                except subprocess.TimeoutExpired:
                    st.warning("Logger didn't stop gracefully, forcing termination...")
                    
                    # Force kill if graceful didn't work
                    if os.name == 'nt':  # Windows
                        subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], 
                                     capture_output=True)
                    else:  # Unix/Linux
                        proc.kill()
                        proc.wait()
                    
                    st.success("Logger forcefully terminated")
            else:
                st.info("Logger process was already stopped")
                
            st.session_state.Logger = None
            
        except Exception as e:
            st.error(f"Error stopping logger: {e}")
            # Try to clean up anyway
            st.session_state.Logger = None
    else:
        st.warning("No logger process running")

# Optional: Add status check
if st.button("🔍 Check Logger Status", use_container_width=True):
    if "Logger" in st.session_state and st.session_state.Logger is not None:
        proc = st.session_state.Logger
        if proc.poll() is None:
            st.success(f"✅ Logger is running (PID: {proc.pid})")
            
            # Optional: Check if the process is actually doing work
            try:
                # Try to read the status file
                StatusPath = r"C:\Users\ADMIN\Desktop\IASYS\status.json"
                if os.path.exists(StatusPath):
                    with open(StatusPath, "r") as f:
                        status = json.load(f)
                    st.json(status)
                else:
                    st.info("Status file not found yet")
            except Exception as e:
                st.warning(f"Could not read status: {e}")
        else:
            st.error("❌ Logger process has stopped")
            st.session_state.Logger = None
    else:
        st.info("No logger process in session state")

# Optional: Display current config
with st.expander("Current Config"):
    try:
        if os.path.exists(ConfigPath):
            with open(ConfigPath, "r") as f:
                current_config = json.load(f)
            st.json(current_config)
        else:
            st.info("No config file found")
    except Exception as e:
        st.error(f"Error reading config: {e}")

st.divider()
st.subheader("Status LOG")
StatusPath = r"C:\Users\ADMIN\Desktop\IASYS\status.json"
if st.button("LOGS", use_container_width=True):
  if os.path.exists(StatusPath):
      with open(StatusPath, "r") as f:
        status = json.load(f)
      st.json(status)
  else:
      st.info("No status file found")


st.divider()

st.subheader("📅 Time Range Selection")

# Initialize session state for form inputs if they don't exist
if 'form_start_date' not in st.session_state:
    st.session_state.form_start_date = datetime.now().date() - timedelta(days=1)
if 'form_start_time' not in st.session_state:
    st.session_state.form_start_time = datetime.now().time().replace(hour=0, minute=0)
if 'form_end_date' not in st.session_state:
    st.session_state.form_end_date = datetime.now().date()
if 'form_end_time' not in st.session_state:
    st.session_state.form_end_time = datetime.now().time()

with st.form("time_range_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Start:**")
        start_date = st.date_input("Start Date", value=st.session_state.form_start_date)
        start_time = st.time_input("Start Time", value=st.session_state.form_start_time)
    
    with col2:
        st.write("**End:**")
        end_date = st.date_input("End Date", value=st.session_state.form_end_date)
        end_time = st.time_input("End Time", value=st.session_state.form_end_time)
    
    submitted = st.form_submit_button("📅 Set Time Range", use_container_width=True)
    
    if submitted:
        # Combine datetime first
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        current_datetime = datetime.now()
        
        # Validate start time
        if start_datetime > current_datetime:
            st.warning("⚠️ Start time cannot be in the future! Using current time.")
            start_datetime = current_datetime
        
        # Validate end time - cap at current time if greater
        if end_datetime > current_datetime:
            st.warning(f"⚠️ End time cannot be in the future! Capped to current time: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            end_datetime = current_datetime
        
        # Validate start < end
        if start_datetime >= end_datetime:
            st.error("❌ Start time must be before end time!")
              # Don't proceed further
        
        # Update session state with validated values
        st.session_state.form_start_date = start_datetime.date()
        st.session_state.form_start_time = start_datetime.time()
        st.session_state.form_end_date = end_datetime.date()
        st.session_state.form_end_time = end_datetime.time()
        
        # Store final validated datetime
        st.session_state.start_datetime = start_datetime
        st.session_state.end_datetime = end_datetime
        
        st.success(f"✅ Time range set: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')} to {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

# Display current selection if it exists
if 'start_datetime' in st.session_state and 'end_datetime' in st.session_state:
    start_datetime = st.session_state.start_datetime
    end_datetime = st.session_state.end_datetime
    
    # Show time range with helpful info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📊 **Start:**    {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.info(f"📊 **End:** {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    with col3:
        duration = end_datetime - start_datetime
        st.info(f"⏱️ **Duration:** {duration}")

st.divider()

# Data retrieval function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def retrieve_data(host, user, password, database, table, start_datetime, end_datetime):
    """Retrieve data from MySQL database"""
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        # SQL query to get data in time range
        query = f"""
        SELECT * FROM vfd 
        WHERE Date_Time BETWEEN %s AND %s 
        ORDER BY Date_Time ASC
        """
        
        # Read data into pandas DataFrame
        df = pd.read_sql(query, connection, params=[start_datetime, end_datetime])
        
        connection.close()
        return df, None
        
    except Exception as e:
        return None, str(e)

# Function to fill gaps
def fill_data_gaps(df, interval='1T'):
    """Fill gaps in data with 0 values"""
    if df.empty:
        return df
    
    # Convert Date_Time to datetime if it's not already
    df['Date_Time'] = pd.to_datetime(df['Date_Time'])
    
    # Set Date_Time as index
    df_indexed = df.set_index('Date_Time')
    
    # Create complete time range
    start_time = df_indexed.index.min()
    end_time = df_indexed.index.max()
    complete_range = pd.date_range(start=start_time, end=end_time, freq=interval)
    
    # Reindex with complete range and fill missing values with 0
    df_filled = df_indexed.reindex(complete_range, fill_value=0)
    
    # Reset index to get Date_Time back as a column
    df_filled = df_filled.reset_index()
    df_filled.rename(columns={'index': 'Date_Time'}, inplace=True)
    
    return df_filled

# Main retrieval button
if st.button("🔍 Retrieve Data", use_container_width=True, type="primary"):
    if not all([host, user, password, database, table]):
        st.error("Please fill in all database connection fields!")
    else:
        with st.spinner("Retrieving data from database..."):
            # Retrieve raw data
            raw_data, error = retrieve_data(
                host, user, password, database, 
                table, start_datetime, end_datetime
            )
            
            if error:
                st.error(f"Database Error: {error}")
            elif raw_data is None or raw_data.empty:
                st.warning("No data found for the selected time period!")
            else:
                st.success(f"✅ Retrieved {len(raw_data)} records")
                
                # Store in session state
                st.session_state.raw_data = raw_data
                
                # Fill gaps
                with st.spinner("Filling data gaps..."):
                    filled_data = fill_data_gaps(raw_data, "1s")
                    st.session_state.filled_data = filled_data
                
                st.success(f"✅ After gap filling: {len(filled_data)} records")
if 'filled_data' in st.session_state:
    filled_data = st.session_state.filled_data 

    st.divider()

    st.subheader("📊 Data Analysis & Visualization")
        
    # Get all column names except id and date_time related columns
    exclude_columns = ['ID', 'Date_Time']
        
    # Get all columns and filter out the excluded ones
    all_columns = filled_data.columns.tolist()
    available_columns = [col for col in all_columns if col not in exclude_columns]

    time_column = 'Date_Time'    

    # Initialize session state for selected columns
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = available_columns[:3] if len(available_columns) >= 3 else available_columns
                
    # Multiselect for column selection
    st.write("### 📈 Select Columns to Analyze")
    selected_columns = st.multiselect(
        "Choose columns to display and plot:",
        options=available_columns,
        default=st.session_state.selected_columns,
        key="column_selector",
        help="Select which data columns you want to analyze"
    )
                    
    # Update session state when selection changes
    st.session_state.selected_columns = selected_columns
                
    col1, col2 = st.columns(2)
    with col1:
        # Quick selection buttons
        if st.button("📊 Select All", use_container_width=True):
            st.session_state.selected_columns = available_columns
            st.rerun()
    with col2:            
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.selected_columns = []
            st.rerun()

    if selected_columns:
        # Create filtered dataframe with time column and selected columns
        display_columns = [time_column] + selected_columns
        filtered_df = filled_data[display_columns].copy()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        
        with col1:
            st.metric("📊 Columns Selected", len(selected_columns))
        
        with col2:
            st.metric("📅 Data Points", len(filtered_df))
        
        with col3:
            time_range = filtered_df[time_column].max() - filtered_df[time_column].min()
            st.metric("⏱️ Time Span", str(time_range))
        
        with col4:
            # Check for missing values in selected columns
            missing_count = filtered_df[selected_columns].isnull().sum().sum()
            st.metric("🔍 Missing Values", missing_count)
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Filtered Data", "📈 Individual Plots", "📊 Combined Plot", "📉 Subplots", "📈 Summary Statistics"])
        
        with tab1:
            st.write("### 📋 Filtered DataFrame")
            st.write(f"Showing {len(selected_columns)} selected columns:")
            
            # Display column info
            for i, col in enumerate(selected_columns):
                col_info = f"**{i+1}. {col}** - {filtered_df[col].dtype}"
                if filtered_df[col].dtype in ['int64', 'float64']:
                    col_info += f" (Range: {filtered_df[col].min():.2f} to {filtered_df[col].max():.2f})"
                st.write(col_info)
            
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            # Download filtered data
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name=f"filtered_data_{len(selected_columns)}_columns.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with tab2:
            st.write("### 📈 Individual Line Plots")
            
            for col in selected_columns:
                fig = px.line(
                    filtered_df, 
                    x=time_column, 
                    y=col,
                    title=f"{col} Over Time",
                    labels={time_column: "Time", col: col}
                )
                
                # Customize the plot
                fig.update_traces(line=dict(width=2))
                fig.update_layout(
                    height=400,
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.write("### 📊 Combined Line Plot")
            
            if len(selected_columns) > 1:
                # Create combined plot with all selected columns
                fig = go.Figure()
                
                colors = px.colors.qualitative.Set1[:len(selected_columns)]
                
                for i, col in enumerate(selected_columns):
                    fig.add_trace(go.Scatter(
                        x=filtered_df[time_column],
                        y=filtered_df[col],
                        mode='lines',
                        name=col,
                        line=dict(width=2, color=colors[i]),
                        hovertemplate=f'<b>{col}</b><br>Value: %{{y}}<br>Time: %{{x}}<extra></extra>'
                    ))
                
                fig.update_layout(
                    title=f"Combined Plot: {', '.join(selected_columns)}",
                    xaxis_title="Time",
                    yaxis_title="Values",
                    height=500,
                    hovermode='x unified',
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=1.01
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **Tip:** This plot shows all selected columns on the same scale. Use subplots if your data has very different ranges.")
            
            else:
                st.info("Select multiple columns to see a combined plot.")
        
        with tab4:
            st.write("### 📉 Individual Subplots")
            
            if len(selected_columns) > 1:
                # Create subplots
                fig = make_subplots(
                    rows=len(selected_columns),
                    cols=1,
                    subplot_titles=selected_columns,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    specs=[[{"secondary_y": False}] for _ in selected_columns]
                )
                
                colors = px.colors.qualitative.Set1[:len(selected_columns)]
                
                for i, col in enumerate(selected_columns):
                    fig.add_trace(
                        go.Scatter(
                            x=filtered_df[time_column],
                            y=filtered_df[col],
                            mode='lines',
                            name=col,
                            line=dict(width=2, color=colors[i]),
                            showlegend=False,
                            hovertemplate=f'<b>{col}</b><br>Value: %{{y}}<br>Time: %{{x}}<extra></extra>'
                        ),
                        row=i+1, col=1
                    )
                    
                    # Update y-axis title for each subplot
                    fig.update_yaxes(title_text=col, row=i+1, col=1)
                
                fig.update_layout(
                    height=300 * len(selected_columns),
                    title_text="Individual Parameter Analysis",
                    showlegend=False
                )
                
                # Only show x-axis title on bottom plot
                fig.update_xaxes(title_text="Time", row=len(selected_columns), col=1)
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **Tip:** Subplots are ideal when your data columns have different scales or units.")
            
            else:
                st.info("Select multiple columns to see subplots.")
        
        with tab5:
            st.write("### 📈 Summary Statistics")
            
            # Calculate summary statistics for selected columns
            numeric_columns = [col for col in selected_columns if pd.api.types.is_numeric_dtype(filtered_df[col])]
            
            if numeric_columns:
                try:
                    # Basic descriptive statistics
                    st.write("#### 📊 Descriptive Statistics")
                    summary_stats = filtered_df[numeric_columns].describe()
                    st.dataframe(summary_stats, use_container_width=True)
                    
                    # Additional statistics
                    st.write("#### 📈 Additional Metrics")
                    additional_stats = pd.DataFrame(index=numeric_columns)
                    
                    for col in numeric_columns:
                        try:
                            additional_stats.loc[col, 'Variance'] = filtered_df[col].var()
                            additional_stats.loc[col, 'Skewness'] = filtered_df[col].skew()
                            additional_stats.loc[col, 'Kurtosis'] = filtered_df[col].kurtosis()
                            additional_stats.loc[col, 'Missing %'] = (filtered_df[col].isnull().sum() / len(filtered_df)) * 100
                            additional_stats.loc[col, 'Unique Values'] = filtered_df[col].nunique()
                            additional_stats.loc[col, 'Range'] = filtered_df[col].max() - filtered_df[col].min()
                        except Exception as e:
                            st.warning(f"Could not calculate some statistics for {col}: {str(e)}")
                    
                    st.dataframe(additional_stats.round(4), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error calculating basic statistics: {str(e)}")
            
            else:
                st.info("No numeric columns selected. Summary statistics are only available for numeric data.")
                
                # Show info about non-numeric columns
                if selected_columns:
                    st.write("#### ℹ️ Selected Non-Numeric Columns")
                    for col in selected_columns:
                        if col not in numeric_columns:
                            try:
                                col_type = str(filtered_df[col].dtype)
                                unique_count = filtered_df[col].nunique()
                                st.write(f"**{col}:** {col_type} - {unique_count} unique values")
                            except Exception as e:
                                st.write(f"**{col}:** Could not analyze - {str(e)}")
    else:
        st.info("👆 Please select at least one column to analyze and visualize the data.")

    st.divider()
    st.subheader("📋 Data Quality Summary")
    
    total_rows = len(st.session_state.filled_data)
    total_cols = len(st.session_state.filled_data.columns)
    missing_cells = st.session_state.filled_data.isnull().sum().sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", total_rows)
    col2.metric("Total Columns", total_cols)  
    col3.metric("Missing Values", missing_cells)
    col4.metric("Data Completeness", f"{((total_rows * total_cols - missing_cells) / (total_rows * total_cols) * 100):.1f}%")
else:
    st.warning("⚠️ No data available! Please retrieve and process data first.")

st.divider()

st.caption("Built by Amey")
st.link_button("Linkedin", url="https://www.linkedin.com/in/amey1way/")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")