# 🎯 Time_Warp IDE

> **Educational Programming Environment** - A comprehensive multi-language IDE designed for learning and teaching programming with integrated turtle graphics, professional themes, and intuitive tools.

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/James-HoneyBadger/Time_Warp/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

## ✨ Features

### 🔤 **Multi-Language Support**
- **BASIC** - Classic line-numbered programming with variables and loops
- **PILOT** - Educational programming with turtle graphics and text commands  
- **Logo** - Turtle graphics programming for visual learning
- **Python** - Modern scripting with full library support
- **JavaScript** - Web development and scripting (Node.js)
- **Perl** - Text processing and system scripting

### 🎨 **Professional Environment**
- **Multi-Tab Editor** - Syntax highlighting and code completion
- **8 Beautiful Themes** - 4 dark themes, 4 light themes
- **Turtle Graphics** - Visual programming canvas
- **File Management** - Project organization and file handling
- **Real-time Execution** - Immediate code execution and results

### 📚 **Educational Focus**
- **Learning-Centered Design** - Built specifically for programming education
- **Visual Programming** - Turtle graphics for Logo and PILOT
- **Clear Error Messages** - Educational feedback for learning
- **Example Programs** - Comprehensive sample code library

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/James-HoneyBadger/Time_Warp.git
cd Time_Warp

# Install dependencies
pip install -r requirements.txt

# Run Time_Warp IDE
python timewarp.py
```

### First Program
1. **Launch** Time_Warp IDE
2. **Select Language** from the dropdown menu
3. **Write Code** in the editor with syntax highlighting
4. **Run Program** with F5 or the Run button
5. **View Results** in the output panel and graphics canvas

## 📋 Language Examples

<details>
<summary><strong>BASIC - Classic Programming</strong></summary>

```basic
10 PRINT "Welcome to BASIC!"
20 FOR I = 1 TO 10
30 PRINT "Number: "; I
40 NEXT I
50 END
```
</details>

<details>
<summary><strong>Logo - Turtle Graphics</strong></summary>

```logo
; Draw a colorful flower
REPEAT 8 [
  REPEAT 4 [FORWARD 50 RIGHT 90]
  RIGHT 45
]
```
</details>

<details>
<summary><strong>PILOT - Educational Programming</strong></summary>

```pilot
T:Welcome to PILOT programming!
A:What is your name?
T:Nice to meet you, #NAME!
T:Let's draw a square:
T:FORWARD 100
T:RIGHT 90
; Continue for all 4 sides...
```
</details>

## 🎨 Themes

Professional color schemes for comfortable coding:

| Dark Themes | Light Themes |
|-------------|--------------|
| 🌙 Dracula | 🌸 Spring |
| 🔥 Monokai | 🌅 Sunset |
| 🌊 Solarized Dark | 🍭 Candy |
| 🌌 Ocean | 🌲 Forest |

## 📁 Project Structure

```
Time_Warp/
├── src/timewarp/          # Main application package
│   ├── core/              # Core interpreter and language engines
│   ├── gui/               # User interface components
│   ├── utils/             # Utilities and theme management
│   └── games/             # Game engine framework
├── tests/                 # Comprehensive test suite
├── docs/                  # Documentation and guides
├── examples/              # Sample programs and tutorials
└── scripts/               # Development and build scripts
```

## 🧪 Testing

```bash
# Run comprehensive test suite
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/          # Unit tests
python -m pytest tests/integration/   # Integration tests
```

## 📖 Documentation

- **[User Guide](docs/user-guide/)** - Complete usage documentation
- **[Developer Guide](docs/developer-guide/)** - Contributing and development
- **[API Reference](docs/api/)** - Technical API documentation
- **[Examples](examples/)** - Sample programs and tutorials

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](docs/developer-guide/CONTRIBUTING.md) for:
- Code style guidelines
- Development setup
- Pull request process
- Issue reporting

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🌟 Support

- **🐛 Issues**: [GitHub Issues](https://github.com/James-HoneyBadger/Time_Warp/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/James-HoneyBadger/Time_Warp/discussions)
- **📚 Documentation**: Complete guides in `docs/` directory

---

<div align="center">

**Time_Warp IDE v1.1** - *Making programming education accessible, visual, and enjoyable*

[🌟 Star this project](https://github.com/James-HoneyBadger/Time_Warp) • [🔗 Share with educators](https://github.com/James-HoneyBadger/Time_Warp) • [🚀 Try it now](https://github.com/James-HoneyBadger/Time_Warp/releases)

</div>