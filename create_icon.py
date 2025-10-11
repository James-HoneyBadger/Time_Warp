#!/usr/bin/env python3
"""
Create application icon for Time_Warp IDE
Generates PNG icons in multiple sizes for desktop integration
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_time_warp_icon():
    """Create Time_Warp IDE application icon"""
    
    # Create icons directory
    os.makedirs('dist/icons', exist_ok=True)
    
    # Icon sizes for different uses
    sizes = [16, 32, 48, 64, 96, 128, 256, 512]
    
    for size in sizes:
        # Create new image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Define colors - educational and modern
        bg_color = (41, 128, 185)      # Blue background
        accent_color = (231, 76, 60)   # Red accent
        text_color = (255, 255, 255)   # White text
        
        # Draw background circle
        margin = size // 16
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=bg_color, outline=accent_color, width=max(1, size//32))
        
        # Calculate font size based on icon size
        font_size = max(8, size // 8)
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw "TW" text in center
        text = "TW"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 2  # Slight adjustment
        
        draw.text((x, y), text, fill=text_color, font=font)
        
        # Add small clock symbol for "Time" concept
        if size >= 48:
            clock_size = size // 6
            clock_x = size - clock_size - margin * 2
            clock_y = margin * 2
            
            # Draw small clock
            draw.ellipse([clock_x, clock_y, clock_x + clock_size, clock_y + clock_size],
                        outline=accent_color, width=max(1, clock_size//8))
            
            # Clock hands
            center_x = clock_x + clock_size // 2
            center_y = clock_y + clock_size // 2
            hand_length = clock_size // 3
            
            # Hour hand (pointing to 10)
            draw.line([center_x, center_y, center_x - hand_length//2, center_y - hand_length//2],
                     fill=accent_color, width=max(1, clock_size//12))
            
            # Minute hand (pointing to 2) 
            draw.line([center_x, center_y, center_x + hand_length//2, center_y - hand_length//2],
                     fill=accent_color, width=max(1, clock_size//16))
        
        # Save icon
        icon_path = f'dist/icons/time_warp_{size}x{size}.png'
        img.save(icon_path, 'PNG')
        print(f"✅ Created icon: {icon_path}")
    
    # Create main application icon (256x256)
    main_icon = Image.open('dist/icons/time_warp_256x256.png')
    main_icon.save('dist/icons/time_warp.png', 'PNG')
    print("✅ Created main application icon: dist/icons/time_warp.png")
    
    return 'dist/icons/time_warp.png'

if __name__ == "__main__":
    print("🎨 Creating Time_Warp IDE application icons...")
    icon_path = create_time_warp_icon()
    print(f"🎯 Main icon created at: {icon_path}")