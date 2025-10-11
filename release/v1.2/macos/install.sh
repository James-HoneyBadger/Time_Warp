#!/bin/bash
#
# Time_Warp IDE v1.2.0 macOS Installation Script
# Automated installation with optional configurations
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
APP_NAME="Time_Warp.app"
VERSION="1.2.0"
INSTALL_DIR="/Applications"
USER_INSTALL_DIR="$HOME/Applications"

print_header() {
    echo -e "\n${PURPLE}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║         Time_Warp IDE v${VERSION} Installer           ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This installer is for macOS only"
        exit 1
    fi
    
    # Check macOS version
    MACOS_VERSION=$(sw_vers -productVersion)
    MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)
    MACOS_MINOR=$(echo $MACOS_VERSION | cut -d. -f2)
    
    if [[ $MACOS_MAJOR -lt 10 ]] || [[ $MACOS_MAJOR -eq 10 && $MACOS_MINOR -lt 13 ]]; then
        print_error "macOS 10.13 (High Sierra) or later is required"
        print_error "Your version: $MACOS_VERSION"
        exit 1
    fi
    
    print_success "macOS $MACOS_VERSION detected"
}

check_app_exists() {
    if [ ! -d "$APP_NAME" ]; then
        print_error "$APP_NAME not found in current directory"
        print_error "Please run this installer from the same directory as $APP_NAME"
        exit 1
    fi
    print_success "Found $APP_NAME"
}

choose_install_location() {
    echo -e "\n${BLUE}Choose installation location:${NC}"
    echo -e "1) System-wide installation (${INSTALL_DIR}) - Requires admin"
    echo -e "2) User installation (${USER_INSTALL_DIR}) - No admin required"
    echo -e "3) Custom location"
    echo -e "4) Cancel installation"
    
    read -p "Choose option (1-4): " choice
    
    case $choice in
        1)
            CHOSEN_INSTALL_DIR="$INSTALL_DIR"
            NEEDS_SUDO=true
            ;;
        2)
            CHOSEN_INSTALL_DIR="$USER_INSTALL_DIR"
            NEEDS_SUDO=false
            mkdir -p "$USER_INSTALL_DIR"
            ;;
        3)
            read -p "Enter custom installation path: " CUSTOM_PATH
            CHOSEN_INSTALL_DIR="$CUSTOM_PATH"
            NEEDS_SUDO=false
            mkdir -p "$CHOSEN_INSTALL_DIR"
            ;;
        4)
            print_warning "Installation cancelled by user"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            choose_install_location
            ;;
    esac
}

remove_quarantine() {
    print_step "Removing quarantine attributes..."
    
    # Remove quarantine to prevent "app is damaged" errors
    xattr -rd com.apple.quarantine "$APP_NAME" 2>/dev/null || true
    
    print_success "Quarantine attributes removed"
}

install_app() {
    print_step "Installing to $CHOSEN_INSTALL_DIR..."
    
    # Remove existing installation
    if [ -d "$CHOSEN_INSTALL_DIR/$APP_NAME" ]; then
        print_warning "Removing existing installation..."
        if $NEEDS_SUDO; then
            sudo rm -rf "$CHOSEN_INSTALL_DIR/$APP_NAME"
        else
            rm -rf "$CHOSEN_INSTALL_DIR/$APP_NAME"
        fi
    fi
    
    # Copy app bundle
    if $NEEDS_SUDO; then
        sudo cp -R "$APP_NAME" "$CHOSEN_INSTALL_DIR/"
        sudo chown -R root:wheel "$CHOSEN_INSTALL_DIR/$APP_NAME"
        sudo chmod -R 755 "$CHOSEN_INSTALL_DIR/$APP_NAME"
    else
        cp -R "$APP_NAME" "$CHOSEN_INSTALL_DIR/"
    fi
    
    print_success "Installation completed"
}

create_symlink() {
    # Ask if user wants command-line access
    echo -e "\n${BLUE}Create command-line shortcut? (y/n):${NC}"
    read -p "This will allow running 'timewarp' from Terminal: " create_symlink
    
    if [[ $create_symlink =~ ^[Yy]$ ]]; then
        SYMLINK_DIR="/usr/local/bin"
        SYMLINK_PATH="$SYMLINK_DIR/timewarp"
        
        # Create symlink script
        if $NEEDS_SUDO; then
            sudo mkdir -p "$SYMLINK_DIR"
            sudo tee "$SYMLINK_PATH" > /dev/null << EOF
#!/bin/bash
exec "$CHOSEN_INSTALL_DIR/$APP_NAME/Contents/MacOS/Time_Warp" "\$@"
EOF
            sudo chmod +x "$SYMLINK_PATH"
        else
            mkdir -p "$HOME/.local/bin"
            SYMLINK_PATH="$HOME/.local/bin/timewarp"
            cat > "$SYMLINK_PATH" << EOF
#!/bin/bash
exec "$CHOSEN_INSTALL_DIR/$APP_NAME/Contents/MacOS/Time_Warp" "\$@"
EOF
            chmod +x "$SYMLINK_PATH"
            
            # Add to PATH if not already there
            if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
                print_warning "Added $HOME/.local/bin to PATH in .zshrc"
                print_warning "Restart terminal or run: source ~/.zshrc"
            fi
        fi
        
        print_success "Command-line shortcut created: $SYMLINK_PATH"
    fi
}

setup_file_associations() {
    echo -e "\n${BLUE}Set up file associations for .pilot, .bas, .logo files? (y/n):${NC}"
    read -p "This will make Time_Warp the default app for these files: " setup_associations
    
    if [[ $setup_associations =~ ^[Yy]$ ]]; then
        # Use duti if available, otherwise provide manual instructions
        if command -v duti &> /dev/null; then
            print_step "Setting up file associations..."
            
            # Set Time_Warp as default for educational programming files
            duti -s org.time-warp-ide.Time_Warp .pilot all 2>/dev/null || true
            duti -s org.time-warp-ide.Time_Warp .bas all 2>/dev/null || true
            duti -s org.time-warp-ide.Time_Warp .logo all 2>/dev/null || true
            
            print_success "File associations configured"
        else
            print_warning "duti not found - install with: brew install duti"
            print_warning "Manual setup: Right-click any .pilot/.bas/.logo file"
            print_warning "Choose 'Open With > Time_Warp > Always Open With'"
        fi
    fi
}

create_desktop_shortcut() {
    echo -e "\n${BLUE}Create Desktop shortcut? (y/n):${NC}"
    read -p "This will add Time_Warp icon to Desktop: " create_shortcut
    
    if [[ $create_shortcut =~ ^[Yy]$ ]]; then
        ln -sf "$CHOSEN_INSTALL_DIR/$APP_NAME" "$HOME/Desktop/"
        print_success "Desktop shortcut created"
    fi
}

verify_installation() {
    print_step "Verifying installation..."
    
    if [ -d "$CHOSEN_INSTALL_DIR/$APP_NAME" ]; then
        # Check if app bundle is valid
        if [ -f "$CHOSEN_INSTALL_DIR/$APP_NAME/Contents/MacOS/Time_Warp" ]; then
            APP_SIZE=$(du -sh "$CHOSEN_INSTALL_DIR/$APP_NAME" | cut -f1)
            print_success "Installation verified (Size: $APP_SIZE)"
            
            # Test launch (quick test)
            print_step "Testing application launch..."
            timeout 5s open "$CHOSEN_INSTALL_DIR/$APP_NAME" --args --test 2>/dev/null || print_warning "Launch test timed out (normal)"
            
            return 0
        fi
    fi
    
    print_error "Installation verification failed"
    return 1
}

show_completion_message() {
    echo -e "\n${GREEN}🎉 Installation Completed Successfully!${NC}"
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
    
    echo -e "\n${BLUE}Application Details:${NC}"
    echo -e "  📱 Location: $CHOSEN_INSTALL_DIR/$APP_NAME"
    echo -e "  🔢 Version: $VERSION"
    echo -e "  💾 Size: $(du -sh "$CHOSEN_INSTALL_DIR/$APP_NAME" | cut -f1)"
    
    echo -e "\n${BLUE}How to Launch:${NC}"
    echo -e "  • Applications folder or Launchpad"
    echo -e "  • Spotlight search: 'Time_Warp'"
    echo -e "  • Double-click any .pilot/.bas/.logo file"
    if [ -f "/usr/local/bin/timewarp" ] || [ -f "$HOME/.local/bin/timewarp" ]; then
        echo -e "  • Terminal command: 'timewarp'"
    fi
    
    echo -e "\n${BLUE}First Launch:${NC}"
    echo -e "  • Right-click → 'Open' (bypass Gatekeeper)"
    echo -e "  • Select theme and preferences"
    echo -e "  • Try the interactive tutorials"
    
    echo -e "\n${BLUE}Documentation:${NC}"
    echo -e "  • README: Same directory as installer"
    echo -e "  • Help Menu: Within the application"
    echo -e "  • GitHub: https://github.com/James-HoneyBadger/Time_Warp"
    
    echo -e "\n${GREEN}Happy Programming with Time_Warp IDE! 🚀${NC}"
}

# Main installation process
main() {
    print_header
    
    check_macos
    check_app_exists
    choose_install_location
    remove_quarantine
    install_app
    
    if verify_installation; then
        create_symlink
        setup_file_associations
        create_desktop_shortcut
        show_completion_message
    else
        print_error "Installation failed"
        exit 1
    fi
}

# Handle script interruption
trap 'print_warning "Installation interrupted by user"; exit 130' INT

# Run main installation
main "$@"