# Advanced Debugger Plugin

Professional-grade debugging tool for Time_Warp IDE with comprehensive debugging capabilities.

## Features

### 🔴 Breakpoint Management
- Add/remove breakpoints with line numbers
- Conditional breakpoints with custom conditions
- Enable/disable breakpoints individually or in bulk
- Visual breakpoint status indicators

### 📊 Variable Inspection  
- Real-time variable monitoring across all language executors
- Variable type and value display
- Watch list for specific variables
- Variable value editing capabilities
- Export variable states to JSON

### 📚 Call Stack Analysis
- Complete call stack visualization
- Stack frame details with local variables
- Function argument inspection
- Source file and line number tracking

### ⚡ Execution Control
- Run, pause, stop, and restart execution
- Step over, step into, step out debugging
- Run to cursor functionality
- Real-time execution status monitoring

### 💾 Memory Monitoring
- System and process memory usage statistics
- Python object count tracking
- Memory profiling with tracemalloc integration
- Garbage collection management
- Memory leak detection capabilities

## Usage

1. **Opening the Debugger**: Access via Tools menu → Advanced Debugger or Ctrl+Shift+D
2. **Setting Breakpoints**: Use the Breakpoints tab to add breakpoints at specific lines
3. **Variable Monitoring**: Variables tab shows real-time values from all language executors
4. **Execution Control**: Use the Execution tab for step-by-step debugging
5. **Memory Analysis**: Monitor memory usage and performance in the Memory tab

## Integration

The Advanced Debugger integrates with:
- Time_Warp interpreter system
- All language executors (PILOT, BASIC, Logo, Python, JavaScript, Perl)
- Framework event system for real-time updates
- IDE menu and toolbar systems

## Technical Details

- **Plugin Type**: Tool Plugin
- **Category**: Debugging
- **Dependencies**: psutil, tracemalloc (optional)
- **Events**: Subscribes to interpreter_ready, code_executed, execution_error
- **Architecture**: Modular tabbed interface with specialized debugging components

## Development

The plugin follows the Time_Warp ToolPlugin architecture with:
- Proper lifecycle management (initialize, activate, deactivate, destroy)
- Event-driven updates
- Comprehensive error handling
- Professional UI design with tooltips and help text