# Sensor Visualizer Plugin

A comprehensive sensor data visualization plugin for Time_Warp IDE that provides real-time charts, data logging, historical analysis, and alert management.

## Features

### 📊 Live Data Visualization

- **Real-time Charts**: Live sensor data displayed in interactive charts
- **Multiple Chart Types**: Line charts, bar charts, gauges, and status indicators  
- **Customizable Display**: Configure chart colors, scales, and refresh rates
- **Status Monitoring**: Visual indicators for sensor health and connectivity

### 📈 Advanced Charts

- **Historical Analysis**: View long-term trends and patterns
- **Multi-sensor Comparison**: Compare data from multiple sensors
- **Trend Analysis**: Identify patterns and seasonal variations
- **Statistical Analysis**: Average, min, max, and standard deviation calculations

### 📝 Data Logging

- **Configurable Logging**: Set custom intervals and file formats
- **Real-time Log Display**: View recent sensor readings in tabular format
- **Export Capabilities**: Export logs to CSV, JSON, XML, Excel, or PDF
- **Data Quality Monitoring**: Track sensor uptime and data integrity

### ⚙️ Sensor Management

- **Multi-sensor Support**: Manage multiple sensor types simultaneously
- **Sensor Configuration**: Enable/disable individual sensors
- **Calibration Tools**: Sensor calibration and adjustment utilities
- **Connection Monitoring**: Track sensor connectivity and status

### 🚨 Alert System

- **Threshold Configuration**: Set min/max values for each sensor
- **Real-time Alerts**: Immediate notifications when thresholds are exceeded
- **Alert History**: Track all alerts with timestamps and details
- **Email Notifications**: Configure email alerts for critical events

## Supported Sensor Types

- **Temperature**: Environmental temperature monitoring
- **Humidity**: Relative humidity measurements
- **Pressure**: Atmospheric pressure readings
- **Light Level**: Ambient light intensity
- **Motion**: Motion detection and tracking
- **Distance**: Ultrasonic distance measurements
- **Air Quality**: Air quality index and pollutant levels
- **Sound Level**: Ambient sound level monitoring

## Installation

This plugin is part of the Time_Warp IDE modular architecture and is automatically discovered by the Tool Manager.

## Usage

### Opening the Sensor Visualizer

- **Menu**: Tools → 📊 Sensor Visualizer  
- **Keyboard**: Ctrl+Shift+S
- **Toolbar**: Click the 📊 Sensors button

### Live Data Tab

1. Navigate to the "📊 Live Data" tab
2. Click "▶️ Start Real-time" to begin monitoring
3. View real-time charts updating automatically
4. Use chart controls to pause, refresh, or configure displays

### Charts Tab

1. Go to the "📈 Charts" tab  
2. Set date range for historical analysis
3. Click "📊 Load Data" to analyze historical trends
4. Use analysis tools for trend detection and statistics

### Data Logging Tab

1. Switch to the "📝 Data Log" tab
2. Configure logging interval and file location
3. Select active sensors for logging
4. Start/stop logging and export data as needed

### Sensor Configuration Tab

1. Access the "⚙️ Sensors" tab
2. Enable/disable individual sensors
3. Configure export formats and reports
4. Generate various sensor reports

### Alerts Tab  

1. Open the "🚨 Alerts" tab
2. Configure threshold values for each sensor
3. View alert history and recent notifications
4. Set up email alerts and notifications

## Real-time Features

### Data Visualization

- **Live Charts**: Charts update automatically with new sensor data
- **Multiple Views**: Line charts for trends, bar charts for comparisons
- **Status Indicators**: Visual status for each connected sensor
- **Performance Metrics**: Real-time statistics and calculations

### Data Processing

- **Automatic Scaling**: Charts auto-scale to accommodate data ranges  
- **Data Filtering**: Filter out noise and invalid readings
- **Trend Detection**: Identify increasing/decreasing trends
- **Anomaly Detection**: Highlight unusual readings or patterns

## Export and Reporting

### Available Reports

- **Daily Sensor Summary**: 24-hour sensor overview
- **Weekly Trend Analysis**: 7-day trend analysis  
- **Monthly Performance Report**: Monthly statistics and insights
- **Alert History Report**: Complete alert log with analysis
- **Sensor Calibration Report**: Calibration status and history
- **Data Quality Assessment**: Data integrity and completeness analysis
- **Comparative Analysis**: Multi-sensor comparison report
- **Mobile Dashboard Export**: Mobile-friendly dashboard

### Export Formats

- **CSV**: Comma-separated values for spreadsheet analysis
- **JSON**: JavaScript Object Notation for web applications
- **XML**: Structured markup for data exchange  
- **Excel**: Microsoft Excel format with charts
- **PDF**: Formatted reports with graphs and analysis

## Technical Details

### Architecture

- **Plugin Type**: Tool Plugin
- **Base Class**: ToolPlugin  
- **Category**: Sensors
- **UI Framework**: Tkinter with TTK

### Dependencies

- Python 3.7+
- tkinter (included with Python)
- Time_Warp Core Framework

### Events

The plugin emits and subscribes to various events:

**Subscribes to:**
- `sensor_data_received`
- `sensor_connected` 
- `sensor_disconnected`

**Emits:**
- `sensor_configured`
- `visualization_updated`
- `alert_triggered`
- `data_exported`
- `dashboard_created`

### Configuration

Sensor configuration is maintained in the plugin state:

```python
sensor_state = {
    'active_sensors': {},
    'data_log': [],
    'thresholds': {},
    'real_time_enabled': False,
    'logging_enabled': False
}
```

## Advanced Features

### Pattern Recognition

- **Trend Analysis**: Detect upward/downward trends over time
- **Seasonal Patterns**: Identify daily, weekly, or seasonal cycles
- **Correlation Analysis**: Find relationships between different sensors
- **Anomaly Detection**: Automatically identify unusual readings

### Alert Management

- **Smart Thresholds**: Dynamic thresholds based on historical data
- **Alert Escalation**: Progressive alert levels (info, warning, critical)
- **Alert Grouping**: Group related alerts to reduce noise
- **Custom Actions**: Execute custom actions when alerts trigger

### Data Analysis

- **Statistical Functions**: Mean, median, standard deviation, variance
- **Frequency Analysis**: Identify periodic patterns in data  
- **Data Interpolation**: Fill gaps in sensor data
- **Filtering**: Remove noise and smooth data series

## Customization

### Chart Customization

- **Colors**: Customize chart colors and themes
- **Scales**: Set custom min/max values for axes
- **Time Ranges**: Configure display time windows
- **Update Intervals**: Set chart refresh rates

### Dashboard Configuration

- **Layout**: Arrange charts and widgets
- **Widgets**: Add custom sensor widgets
- **Themes**: Apply different visual themes
- **Responsive Design**: Adapt to different screen sizes

## Integration

### Hardware Integration

The plugin integrates with various sensor hardware:
- Raspberry Pi GPIO sensors
- Arduino-based sensor networks
- USB sensor devices
- Network-connected IoT sensors

### Software Integration

- **Time_Warp Framework**: Full integration with Time_Warp event system
- **File System**: Automatic data persistence and backup
- **Network Services**: Web dashboard and API endpoints
- **Email Services**: Automated alert notifications

## Troubleshooting

### Common Issues

- **No sensor data**: Check sensor connections and drivers
- **Chart not updating**: Verify real-time monitoring is enabled
- **Export errors**: Check file permissions and disk space
- **Alert not working**: Verify threshold configuration

### Debug Mode

Enable debug logging in the plugin settings to troubleshoot issues.

## Performance Optimization

- **Data Buffering**: Efficient memory management for large datasets
- **Chart Optimization**: Optimized rendering for smooth updates
- **Background Processing**: Non-blocking data processing
- **Resource Management**: Automatic cleanup of old data

## Future Enhancements

- Machine learning-based pattern recognition
- Predictive analytics and forecasting
- Advanced statistical analysis tools
- Cloud-based data synchronization
- Mobile companion app
- Voice-controlled monitoring

## License

This plugin is part of the Time_Warp IDE project and follows the same licensing terms.

## Support

For support and bug reports, please use the Time_Warp IDE issue tracker or contact the development team.