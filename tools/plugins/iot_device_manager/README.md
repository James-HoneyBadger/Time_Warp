# IoT Device Manager Plugin

A comprehensive IoT device management plugin for Time_Warp IDE that provides device discovery, control, network monitoring, protocol support, and data analytics.

## Features

### 🔍 Device Discovery
- **Network Scanning**: Automatic discovery of IoT devices on local networks
- **Protocol Support**: Detection via mDNS, UPnP, MQTT, and other protocols
- **Device Information**: Detailed device capabilities and specifications
- **Connection Testing**: Verify connectivity and protocol handshakes

### 🎛️ Device Control
- **Remote Control**: Direct control of connected IoT devices
- **Status Monitoring**: Real-time device status and health information
- **Command Interface**: Send custom commands to devices
- **Multi-Protocol Support**: HTTP/REST, MQTT, CoAP, WebSocket, RTSP

### 🌐 Network Monitoring
- **Traffic Analysis**: Real-time network traffic monitoring
- **Performance Metrics**: Network statistics and performance data
- **Connection Tracking**: Monitor active connections and data transfer
- **Export Capabilities**: Save traffic logs and analytics

### 📡 Protocol Configuration
- **Multi-Protocol Support**:
  - HTTP/REST (ports 80/443)
  - MQTT (port 1883)
  - CoAP (port 5683)
  - WebSocket (port 8080)
  - RTSP (port 554)
  - UPnP (port 1900)
  - Zigbee and LoRaWAN support
- **Protocol Management**: Enable/disable protocols as needed
- **Configuration**: Customize protocol settings and security options

### 📊 Data Analytics
- **Dashboard**: Visual analytics dashboard with charts and graphs
- **Device Statistics**: Track device types, usage patterns, and performance
- **Network Analysis**: Monitor traffic patterns and system health
- **Reporting**: Generate comprehensive IoT reports
- **Alert System**: Configure monitoring alerts and notifications

## Installation

This plugin is part of the Time_Warp IDE modular architecture. It should be automatically discovered and loaded by the Tool Manager.

## Usage

### Opening the IoT Device Manager
- **Menu**: Tools → 🌐 IoT Device Manager
- **Keyboard**: Ctrl+Shift+I
- **Toolbar**: Click the 🌐 IoT button

### Device Discovery
1. Navigate to the "🔍 Device Discovery" tab
2. Set your network range (default: 192.168.1.0/24)
3. Click "🔍 Scan Network" or "🔄 Auto-Discover"
4. Select discovered devices and add them to managed devices

### Device Control
1. Go to the "🎛️ Device Control" tab
2. Select a device from the connected devices list
3. Use control buttons to interact with devices
4. Monitor device status and send custom commands

### Network Monitoring
1. Switch to the "🌐 Network Monitor" tab
2. View real-time network statistics
3. Monitor traffic logs and patterns
4. Start/stop monitoring as needed

### Protocol Configuration
1. Access the "📡 Protocols" tab
2. View supported IoT protocols and their status
3. Configure, enable, or disable protocols
4. Test protocol connections

### Analytics
1. Open the "📊 Data Analytics" tab
2. View the analytics dashboard
3. Generate reports and export data
4. Configure monitoring alerts

## Technical Details

### Architecture
- **Plugin Type**: Tool Plugin
- **Base Class**: ToolPlugin
- **Category**: IoT
- **UI Framework**: Tkinter with TTK

### Dependencies
- Python 3.7+
- tkinter (included with Python)
- Time_Warp Core Framework

### Events
The plugin emits various events for integration with the Time_Warp framework:
- `network_scan_completed`
- `device_discovered`
- `device_added`
- `iot_device_controlled`
- `protocol_configured`
- `analytics_refreshed`

### Sample Data
The plugin includes sample IoT devices and data for demonstration:
- Smart lights and bulbs
- Thermostats and climate control
- Security cameras
- Environmental sensors
- Smart plugs and switches

## Configuration

The plugin maintains configuration in the IoT state object:
```python
iot_state = {
    'discovered_devices': [],
    'managed_devices': [],
    'protocols': {},
    'network_traffic': [],
    'analytics_data': {}
}
```

## Development

### Adding New Protocols
1. Update the `_populate_protocols()` method
2. Add protocol-specific handling in device control methods
3. Update the discovery logic for new protocol support

### Extending Device Types
1. Add new device types to sample data
2. Implement device-specific control methods
3. Update the analytics charts for new device categories

### Custom Events
The plugin supports custom event emission:
```python
self.emit_event('custom_event_name', event_data)
```

## Troubleshooting

### Common Issues
- **No devices discovered**: Check network connectivity and range settings
- **Protocol errors**: Verify protocol is enabled and configured correctly
- **UI not responsive**: Ensure proper initialization of UI components

### Debug Mode
Enable debug output by setting the plugin logging level to debug.

## Future Enhancements

- Real hardware integration with actual IoT devices
- Cloud service connectivity
- Advanced security features
- Machine learning analytics
- Mobile app integration
- Voice control interface

## License

This plugin is part of the Time_Warp IDE project and follows the same licensing terms.

## Support

For support and bug reports, please use the Time_Warp IDE issue tracker or contact the development team.