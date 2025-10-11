# Time_Warp IDE v1.2.0 - macOS Release

## 🚀 New Features in v1.2.0

### Enhanced Educational Programming Environment
- **Multi-tab Code Editor**: Work on multiple files simultaneously with syntax highlighting
- **Enhanced Error Handling**: Better error messages and debugging support
- **AI Code Assistant**: Intelligent code completion and suggestions
- **Gamification System**: Learn programming through achievements and progress tracking
- **Tutorial System**: Interactive tutorials for PILOT, BASIC, and Logo languages

### Language Support
- **PILOT**: Educational programming language with turtle graphics commands
- **BASIC**: Classic line-numbered programming with full interpreter
- **Logo**: Turtle graphics programming with advanced geometric functions
- **Python**: Full Python scripting support with enhanced features
- **JavaScript**: Basic JavaScript execution environment

### macOS-Specific Features
- Native macOS .app bundle
- Optimized for Apple Silicon (M1/M2/M3) and Intel Macs
- File associations for .pilot, .bas, and .logo files
- macOS-native UI integration
- Spotlight indexing support

## 📋 System Requirements

### Minimum Requirements
- **macOS**: 10.13 (High Sierra) or later
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Architecture**: Universal binary (Intel x64 and Apple Silicon)

### Recommended
- macOS 12.0 (Monterey) or later for best performance
- 8GB+ RAM for large projects
- Graphics acceleration (Metal support) for enhanced visuals

## 📦 Installation

### Method 1: Simple Installation
1. Download `Time_Warp.app`
2. Drag to `/Applications` folder
3. Right-click → "Open" on first launch (to bypass Gatekeeper)
4. Grant any requested permissions

### Method 2: Terminal Installation
```bash
# Navigate to download location
cd ~/Downloads

# Copy to Applications
sudo cp -R Time_Warp.app /Applications/

# Launch
open /Applications/Time_Warp.app
```

### Method 3: User-Specific Installation
```bash
# Install to user Applications folder
cp -R Time_Warp.app ~/Applications/
```

## 🔧 First Launch Configuration

### Initial Setup
1. **Theme Selection**: Choose from 8 built-in themes
2. **Language Preference**: Set default programming language
3. **Tutorial System**: Enable/disable guided learning
4. **File Associations**: Configure for .pilot, .bas, .logo files

### Directory Structure
Time_Warp creates the following in your home directory:
```
~/.Time_Warp/
├── config.json          # User preferences
├── themes/              # Custom themes
├── plugins/             # User plugins
├── projects/            # Sample projects
└── tutorials/           # Tutorial progress
```

## 🎯 Getting Started

### Quick Start Tutorial
1. **Launch Time_Warp**: Open from Applications or Launchpad
2. **Select "New Project"**: Choose PILOT for beginners
3. **Try Sample Code**:
   ```pilot
   T: Hello from Time_Warp IDE on macOS!
   Y: Welcome to educational programming
   ```
4. **Run**: Click "Execute" or press ⌘+R

### Language Examples

#### PILOT Programming
```pilot
T: Welcome to PILOT programming!
A: What's your name?
T: Hello, #name!
T: Let's draw something...
G: FORWARD 100
G: RIGHT 90
G: FORWARD 100
```

#### BASIC Programming
```basic
10 PRINT "Time_Warp BASIC on macOS"
20 FOR I = 1 TO 10
30 CIRCLE 100 + I*10, 100 + I*5, I*5
40 NEXT I
50 PRINT "Graphics complete!"
```

#### Logo Programming
```logo
TO SQUARE :SIZE
  REPEAT 4 [FORWARD :SIZE RIGHT 90]
END

TO SPIRAL
  REPEAT 36 [SQUARE 10 + REPCOUNT * 5 RIGHT 10]
END

SPIRAL
```

## 🎨 Theme System

### Built-in Themes
- **Dark Themes**: Dracula, Monokai, Solarized Dark, Ocean
- **Light Themes**: Spring, Sunset, Candy, Forest

### Theme Selection
- Menu: `Preferences > Themes`
- Keyboard: `⌘+T`
- Automatic: Follows macOS system appearance

## 🔌 Plugin System

### Installing Plugins
1. Download `.twplugin` file
2. Double-click to install, or
3. Menu: `Tools > Install Plugin`

### Creating Plugins
See `/Applications/Time_Warp.app/Contents/Resources/plugins/sample_plugin/` for template.

## 🏆 Gamification Features

### Achievement System
- **Code Warrior**: Write 100 lines of code
- **Bug Hunter**: Fix 10 syntax errors
- **Artist**: Create 5 turtle graphics programs
- **Explorer**: Try all programming languages

### Progress Tracking
- Lines of code written
- Programs completed
- Tutorial progress
- Time spent coding

## 🎓 Educational Features

### Interactive Tutorials
- **PILOT Basics**: Learn educational programming fundamentals
- **BASIC Graphics**: Classic programming with visual output
- **Logo Geometry**: Mathematical programming concepts
- **Python Integration**: Modern programming practices

### Classroom Integration
- **Student Progress**: Track learning milestones
- **Assignment Templates**: Pre-built programming exercises
- **Export Options**: Save work in multiple formats

## 🚨 Troubleshooting

### Common Issues

#### "Time_Warp.app is damaged and can't be opened"
**Solution**:
```bash
sudo xattr -rd com.apple.quarantine /Applications/Time_Warp.app
```

#### App Won't Launch
**Check**:
1. macOS version compatibility (10.13+)
2. Available disk space (100MB+)
3. Permissions: System Preferences > Security & Privacy

#### Graphics Not Working
**Solutions**:
1. Update macOS to latest version
2. Reset graphics preferences: Delete `~/.Time_Warp/graphics_config.json`
3. Try different theme: Menu > Preferences > Themes

#### Python Integration Issues
**Solution**:
```bash
# Verify Python installation
python3 --version

# Reinstall if needed (requires Homebrew)
brew install python@3.9
```

### Performance Optimization

#### For Older Macs
- Disable animations: Preferences > Performance
- Use light themes for better performance
- Close unused tabs in multi-tab editor

#### For Apple Silicon Macs
- Enable Metal acceleration: Preferences > Graphics
- Use native ARM optimizations (automatic)

## 🔒 Security & Privacy

### Code Signing
This application is **unsigned**. On first launch:
1. Right-click the app
2. Select "Open"
3. Click "Open" in security dialog

### Permissions
Time_Warp may request:
- **File Access**: To save/load your programs
- **Network**: For AI assistant features (optional)
- **Microphone**: For voice commands (optional)

## 🌐 Online Resources

### Documentation
- **Official Docs**: https://github.com/James-HoneyBadger/Time_Warp
- **Tutorial Videos**: https://github.com/James-HoneyBadger/Time_Warp/docs
- **Community Forum**: https://github.com/James-HoneyBadger/Time_Warp/discussions

### Support
- **Issue Tracker**: https://github.com/James-HoneyBadger/Time_Warp/issues
- **Email Support**: time-warp-ide@example.com
- **Discord Community**: [Join Server](https://discord.gg/time-warp-ide)

## 📝 Release Notes

### Version 1.2.0 Changes
- ✨ Native macOS app bundle
- ✨ Universal binary (Intel + Apple Silicon)
- ✨ Multi-tab code editor
- ✨ Enhanced graphics rendering
- ✨ AI-powered code assistance
- ✨ Gamification system
- ✨ Interactive tutorial system
- 🔧 Improved error handling
- 🔧 Better theme management
- 🔧 Enhanced plugin system
- 🐛 Fixed turtle graphics on Retina displays
- 🐛 Resolved memory leaks in long sessions

### Previous Versions
- **v1.1.0**: Multi-language support, basic GUI
- **v1.0.0**: Initial release with PILOT language

## 📄 License

**MIT License** - See LICENSE file for full text.

Copyright © 2024 Time_Warp Development Team

---

**Enjoy programming with Time_Warp IDE v1.2.0 on macOS! 🎉**

*Built with ❤️ for educational programming*