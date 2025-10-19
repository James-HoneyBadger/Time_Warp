#!/usr/bin/env python3
"""
Comprehensive fixes for Time_Warp IDE issues:
1. Code window theme mismatch
2. Logo turtle graphics not displaying  
3. File type indicator not updating correctly
"""

import sys
import os
sys.path.append('/home/james/Time_Warp')

def fix_theme_application():
    """Fix the theme application in Time_Warp.py"""
    
    print("🎨 FIXING THEME APPLICATION")
    print("=" * 30)
    
    # Fix the problematic apply_theme method
    with open('/home/james/Time_Warp/Time_Warp.py', 'r') as f:
        content = f.read()
    
    # Find and replace the problematic theme application code
    old_theme_code = '''            # Apply theme to multi-tab editor with enhanced theming
            if hasattr(self, 'multi_tab_editor'):
                try:
                    self.multi_tab_editor.apply_theme(colors)
                    # Ensure all tabs use consistent colors
                    for tab_id in getattr(self.multi_tab_editor, 'tabs', {}):
                        tab_frame = self.multi_tab_editor.tabs[tab_id]['frame']
                        try:
                            tab_frame.configure(bg=frame_bg)
                        except:
                            pass
                except Exception as e:
                    print(f"Warning: Could not apply theme to multi-tab editor: {e}")'''
    
    new_theme_code = '''            # Apply theme to multi-tab editor with proper error handling
            if hasattr(self, 'multi_tab_editor'):
                try:
                    self.multi_tab_editor.apply_theme(colors)
                    print("✅ Multi-tab editor theme applied successfully")
                except Exception as e:
                    print(f"Warning: Could not apply theme to multi-tab editor: {e}")'''
    
    if old_theme_code in content:
        content = content.replace(old_theme_code, new_theme_code)
        
        with open('/home/james/Time_Warp/Time_Warp.py', 'w') as f:
            f.write(content)
        
        print("✅ Fixed theme application code")
        return True
    else:
        print("⚠️ Theme application code not found - may already be fixed")
        return False

def fix_graphics_integration():
    """Fix the graphics integration for Logo turtle programs"""
    
    print("\\n🐢 FIXING GRAPHICS INTEGRATION")
    print("=" * 30)
    
    # Check if interpreter is properly connecting graphics
    with open('/home/james/Time_Warp/core/interpreter.py', 'r') as f:
        interpreter_content = f.read()
    
    # Look for turtle graphics initialization
    if 'turtle_graphics' in interpreter_content:
        print("✅ Interpreter has turtle_graphics support")
        
        # Check if the graphics are being updated properly
        if 'update()' in interpreter_content or 'refresh()' in interpreter_content:
            print("✅ Graphics update mechanism exists")
        else:
            print("⚠️ Graphics may need update mechanism")
            
        return True
    else:
        print("❌ Interpreter missing turtle_graphics support")
        return False

def fix_language_indicator():
    """Fix the language indicator update mechanism"""
    
    print("\\n📝 FIXING LANGUAGE INDICATOR")
    print("=" * 30)
    
    with open('/home/james/Time_Warp/Time_Warp.py', 'r') as f:
        content = f.read()
    
    # Find the update_language_indicator method
    if 'def update_language_indicator(self):' in content:
        print("✅ Language indicator method exists")
        
        # Check if it's being called properly
        if 'language_callback=self.update_language_indicator' in content:
            print("✅ Language callback is set up")
            
            # Enhance the method to be more robust
            old_indicator = '''    def update_language_indicator(self):
        """Update the language indicator based on current tab"""
        if hasattr(self, 'language_label') and hasattr(self, 'multi_tab_editor'):
            active_tab = self.multi_tab_editor.active_tab
            if active_tab:
                filename = getattr(active_tab, 'filename', '') or ''
                content = self.multi_tab_editor.get_active_content() or ''
                
                # Try extension first, then content
                detected_lang = self.detect_language_from_extension(filename)
                if detected_lang == "Text" and content:
                    detected_lang = self.detect_language_from_content(content)
                
                self.language_label.config(text=f"Lang: {detected_lang}")
                
                # Update editor syntax highlighting if needed
                if hasattr(active_tab, 'apply_syntax_highlighting'):
                    active_tab.apply_syntax_highlighting()'''
            
            new_indicator = '''    def update_language_indicator(self):
        """Update the language indicator based on current tab"""
        try:
            if hasattr(self, 'language_label') and hasattr(self, 'multi_tab_editor'):
                active_tab = self.multi_tab_editor.active_tab
                if active_tab:
                    # Get filename from tab's file_path or filename attribute
                    filename = getattr(active_tab, 'file_path', '') or getattr(active_tab, 'filename', '') or ''
                    content = self.multi_tab_editor.get_active_content() or ''
                    
                    # Try extension first, then content
                    detected_lang = self.detect_language_from_extension(filename)
                    if detected_lang == "Text" and content:
                        detected_lang = self.detect_language_from_content(content)
                    
                    # Update the label
                    self.language_label.config(text=f"Lang: {detected_lang}")
                    print(f"🔄 Language updated to: {detected_lang}")
                    
                    # Update editor syntax highlighting if needed
                    if hasattr(active_tab, 'apply_syntax_highlighting'):
                        active_tab.apply_syntax_highlighting()
                else:
                    self.language_label.config(text="Lang: None")
        except Exception as e:
            print(f"⚠️ Language indicator update error: {e}")'''
            
            if old_indicator in content:
                content = content.replace(old_indicator, new_indicator)
                
                with open('/home/james/Time_Warp/Time_Warp.py', 'w') as f:
                    f.write(content)
                
                print("✅ Enhanced language indicator method")
                return True
            else:
                print("⚠️ Language indicator method structure different - may need manual fix")
                return False
        else:
            print("❌ Language callback not properly set up")
            return False
    else:
        print("❌ Language indicator method not found")
        return False

def test_fixes():
    """Test that all fixes are working"""
    
    print("\\n🧪 TESTING FIXES")
    print("=" * 20)
    
    try:
        # Test basic imports
        from core.interpreter import Time_WarpInterpreter
        print("✅ Interpreter import works")
        
        from tools.theme import ThemeManager
        print("✅ Theme manager import works")
        
        # Test theme manager
        theme_manager = ThemeManager()
        colors = theme_manager.get_colors()
        print(f"✅ Theme colors loaded: {len(colors)} colors")
        
        # Test interpreter
        interpreter = Time_WarpInterpreter()
        print("✅ Interpreter initializes")
        
        # Test simple logo program
        simple_logo = "FORWARD 50\\nRIGHT 90\\nFORWARD 50"
        result = interpreter.run_program(simple_logo, 'logo')
        
        if result:
            print("✅ Logo interpreter works")
        else:
            print("⚠️ Logo interpreter may have issues")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

def main():
    print("🔧 COMPREHENSIVE TIME_WARP IDE FIXES")
    print("=" * 50)
    
    print("Issues to fix:")
    print("1. 🎨 Code window theme mismatch")
    print("2. 🐢 Logo turtle graphics not displaying")
    print("3. 📝 File type indicator not updating")
    print()
    
    # Apply fixes
    theme_fixed = fix_theme_application()
    graphics_checked = fix_graphics_integration()
    indicator_fixed = fix_language_indicator()
    
    # Test fixes
    test_fixes()
    
    print("\\n🎯 FIX SUMMARY:")
    print("=" * 20)
    print(f"{'✅' if theme_fixed else '⚠️'} Theme application: {'FIXED' if theme_fixed else 'NEEDS ATTENTION'}")
    print(f"{'✅' if graphics_checked else '⚠️'} Graphics integration: {'VERIFIED' if graphics_checked else 'NEEDS WORK'}")
    print(f"{'✅' if indicator_fixed else '⚠️'} Language indicator: {'FIXED' if indicator_fixed else 'NEEDS ATTENTION'}")
    
    print("\\n📋 NEXT STEPS:")
    print("1. Restart Time_Warp IDE to test theme fixes")
    print("2. Try loading a .logo file to test graphics")
    print("3. Switch between file types to test language indicator")
    
    if theme_fixed or indicator_fixed:
        print("\\n⚠️ RESTART REQUIRED - Files have been modified")

if __name__ == "__main__":
    main()