# Hardware Controller Plugin

Professional hardware interface tool for Time_Warp IDE with comprehensive hardware management capabilities.

## Features

### 📌 GPIO Pin Control

- Visual GPIO pin layout for Raspberry Pi (40 pins)
- Pin mode configuration (Input/Output)
- Real-time pin value monitoring and control
- Pin state visualization with color coding
- Bulk GPIO operations and reset functionality

### 🌡️ Sensor Management

- Support for multiple sensor types (DHT22, DS18B20, BMP280, HC-SR04, PIR, LDR)
- Real-time sensor data monitoring
- Sensor configuration and calibration
- Data logging and export capabilities
- Visual sensor status indicators

### 🔧 Device Control

- Hardware device discovery and management
- Device control interfaces for common components
- LED strips, servo motors, buzzers, relays, displays
- Device status monitoring and diagnostics
- Configuration management for connected devices

### 🤖 Automation Engine

- Rule-based automation system
- Conditional logic support (IF-THEN-ELSE)
- Scheduled tasks and triggers
- Sensor-based automation rules
- Real-time rule execution engine

## Usage

1. **Opening the Hardware Controller**: Access via Tools menu → Hardware Controller or Ctrl+Shift+H
2. **GPIO Control**: Click pins on the visual layout to select and configure them
3. **Sensor Monitoring**: Add sensors and monitor real-time data in the Sensors tab
4. **Device Management**: Control connected devices through the Devices tab
5. **Automation**: Create and manage automation rules in the Automation tab

## Integration

The Hardware Controller integrates with:

- Time_Warp interpreter system for hardware programming
- Framework event system for real-time updates
- GPIO libraries for actual hardware control
- Sensor libraries for data acquisition

## Technical Details

- **Plugin Type**: Tool Plugin
- **Category**: Hardware
- **Dependencies**: None (hardware libraries optional)
- **Events**: Emits gpio_*, sensor_*, device_*, automation_* events
- **Architecture**: Professional 4-tab interface with hardware abstraction

## Hardware Support

### Supported Platforms

- Raspberry Pi (all models)
- Arduino (via serial communication)
- Generic GPIO devices
- I2C/SPI devices

### Supported Components

- **Sensors**: Temperature, humidity, distance, light, motion, pressure
- **Actuators**: LEDs, servos, motors, relays, buzzers
- **Displays**: LCD, OLED, LED matrices
- **Communication**: UART, I2C, SPI, wireless modules

## Development

The plugin follows the Time_Warp ToolPlugin architecture with:

- Proper lifecycle management (initialize, activate, deactivate, destroy)
- Event-driven hardware monitoring
- Professional UI with tabbed interface
- Comprehensive error handling and safety features
- Hardware abstraction for cross-platform compatibility