#!/usr/bin/env python3
"""
TimeWarp IDE Facebook Cover Generator
Creates a professional Facebook cover image based on design specifications.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_facebook_cover():
    """Generate TimeWarp IDE Facebook cover image."""

    # Canvas dimensions
    width, height = 820, 312

    # Create new image with RGBA mode for transparency support
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Create gradient background (left to right: dark purple -> teal -> light blue)
    for x in range(width):
        # Calculate gradient position (0.0 to 1.0)
        pos = x / width

        if pos < 0.5:
            # Dark purple to teal (first half)
            r = int(45 + (0 - 45) * (pos * 2))  # 2D -> 00
            g = int(27 + (180 - 27) * (pos * 2))  # 1B -> B4
            b = int(105 + (216 - 105) * (pos * 2))  # 69 -> D8
        else:
            # Teal to light blue (second half)
            r = int(0 + (135 - 0) * ((pos - 0.5) * 2))  # 00 -> 87
            g = int(180 + (206 - 180) * ((pos - 0.5) * 2))  # B4 -> CE
            b = int(216 + (235 - 216) * ((pos - 0.5) * 2))  # D8 -> EB

        # Draw vertical line with gradient color
        draw.line([(x, 0), (x, height)], fill=(r, g, b))

    # Try to load fonts, fall back to default if not available
    try:
        # Try to use system fonts
        title_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42
        )
        tagline_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24
        )
        code_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16
        )
        small_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
        )
    except:
        # Fallback to default fonts
        title_font = ImageFont.load_default()
        tagline_font = ImageFont.load_default()
        code_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Colors
    retro_teal = (0, 180, 216)
    deep_purple = (106, 13, 173)
    warm_orange = (255, 107, 53)
    classic_gray = (44, 44, 44)
    electric_blue = (0, 102, 204)
    gold = (255, 215, 0)
    neon_green = (0, 255, 65)
    white = (255, 255, 255)

    # Section 1: Retro Left (30% width)
    left_section_width = int(width * 0.3)

    # Draw retro computer screen
    screen_x = 20
    screen_y = 20
    screen_width = 180
    screen_height = 120

    # Screen border
    draw.rectangle(
        [screen_x, screen_y, screen_x + screen_width, screen_y + screen_height],
        outline=classic_gray,
        fill=(20, 20, 20),
        width=3,
    )

    # Screen content
    draw.text(
        (screen_x + 10, screen_y + 10),
        '10 PRINT "HELLO"',
        font=code_font,
        fill=neon_green,
    )
    draw.text(
        (screen_x + 10, screen_y + 30), "20 GOTO 10", font=code_font, fill=neon_green
    )

    # Command prompts
    draw.text(
        (screen_x, screen_y + screen_height + 20),
        ">_ PILOT",
        font=code_font,
        fill=electric_blue,
    )
    draw.text(
        (screen_x, screen_y + screen_height + 40),
        ">_ BASIC",
        font=code_font,
        fill=electric_blue,
    )
    draw.text(
        (screen_x, screen_y + screen_height + 60),
        ">_ LOGO",
        font=code_font,
        fill=electric_blue,
    )

    # Section 2: Center Logo (40% width)
    center_start = left_section_width
    center_width = int(width * 0.4)

    # Main logo - TimeWarp IDE
    logo_text = "⏰ TIMEWARP IDE"
    bbox = draw.textbbox((0, 0), logo_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    logo_x = center_start + (center_width - text_width) // 2 - 25
    logo_y = height // 2 - text_height - 20

    # Add glow effect to logo
    for offset in range(3, 0, -1):
        draw.text(
            (logo_x - offset, logo_y - offset),
            logo_text,
            font=title_font,
            fill=(255, 255 - offset * 20, 0),
        )  # Orange glow

    draw.text((logo_x, logo_y), logo_text, font=title_font, fill=white)

    # Tagline
    tagline_text = "Compile BASIC, PILOT & Logo\nto Native Code"
    tagline_bbox = draw.textbbox((0, 0), tagline_text, font=tagline_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]

    tagline_x = center_start + (center_width - tagline_width) // 2 - 25
    tagline_y = logo_y + text_height + 10

    draw.text((tagline_x, tagline_y), tagline_text, font=tagline_font, fill=white)

    # Section 3: Modern Right (30% width)
    right_start = center_start + center_width

    # Terminal window
    term_x = right_start + 20
    term_y = 20
    term_width = 200
    term_height = 150

    # Terminal background
    draw.rectangle(
        [term_x, term_y, term_x + term_width, term_y + term_height],
        fill=(20, 20, 20),
        outline=electric_blue,
        width=2,
    )

    # Terminal content
    draw.text(
        (term_x + 10, term_y + 10),
        "$ timewarp-compiler hello.bas -o hello",
        font=code_font,
        fill=neon_green,
    )
    draw.text((term_x + 10, term_y + 30), "$ ./hello", font=code_font, fill=white)
    draw.text((term_x + 10, term_y + 50), "Hello World!", font=code_font, fill=white)

    # Tech badges
    badge_y = term_y + term_height + 20
    badges = ["GCC COMPILATION", "NATIVE EXECUTABLE", "ZERO DEPENDENCIES"]

    for i, badge in enumerate(badges):
        badge_x = right_start + 20
        draw.rectangle(
            [badge_x, badge_y + i * 25, badge_x + 180, badge_y + i * 25 + 20],
            fill=electric_blue,
            outline=white,
            width=1,
        )
        draw.text(
            (badge_x + 5, badge_y + i * 25 + 2), badge, font=small_font, fill=white
        )

    # Add some binary code decoration
    binary_x = width - 50
    binary_y = height - 50
    binary_text = "01010101\n01001000\n01000101\n01001100\n01001100\n01001111"
    draw.text(
        (binary_x, binary_y),
        binary_text,
        font=small_font,
        fill=(neon_green[0], neon_green[1], neon_green[2], 128),
    )

    return img


def main():
    """Main function to generate and save the Facebook cover."""
    print("🎨 Generating TimeWarp IDE Facebook Cover...")

    # Create the cover image
    cover_img = create_facebook_cover()

    # Save as PNG first (better quality)
    png_path = "timewarp_facebook_cover.png"
    cover_img.save(png_path, "PNG")
    print(f"✅ PNG version saved as: {png_path}")

    # Convert to JPG for Facebook
    # Create RGB version (JPG doesn't support transparency)
    rgb_img = Image.new("RGB", cover_img.size, (255, 255, 255))
    rgb_img.paste(
        cover_img, mask=cover_img.split()[-1] if cover_img.mode == "RGBA" else None
    )

    jpg_path = "timewarp_facebook_cover.jpg"
    rgb_img.save(jpg_path, "JPEG", quality=95)
    print(f"✅ JPG version saved as: {jpg_path}")

    # Display image info
    print(f"📐 Dimensions: {cover_img.size[0]}x{cover_img.size[1]} pixels")
    print(f"📁 File size: {os.path.getsize(jpg_path)} bytes")

    print("\n🚀 Ready to upload to Facebook!")
    print("💡 Tips:")
    print("   - Upload the JPG version to Facebook")
    print("   - Position it so the logo stays visible")
    print("   - Test on mobile to ensure it looks good when cropped")


if __name__ == "__main__":
    main()
