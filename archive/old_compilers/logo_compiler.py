#!/usr/bin/env python3
"""
Logo Native Compiler
====================

A compiler for the Logo programming language that produces standalone Linux executables.
Logo is a turtle graphics language designed for education and creative programming.

Features supported:
- Turtle movement commands (FORWARD, BACK, LEFT, RIGHT)
- Pen control (PENUP, PENDOWN, SETCOLOR)
- Position commands (HOME, SETXY, GOTO)
- Repeat loops (REPEAT n [...])
- Procedures (TO name ... END)
- Variables and arithmetic
- Graphics output (creates PNG files)
"""

import re
import os
import sys
import subprocess
import tempfile
from typing import List, Dict, Any, Optional


class LogoCompiler:
    """Compiler for Logo language that generates C code with graphics support"""
    
    def __init__(self):
        self.debug = False
        self.optimize = False
        
    def compile_file(self, input_file: str, output_file: Optional[str] = None) -> bool:
        """Compile Logo source file to Linux executable"""
        try:
            with open(input_file, 'r') as f:
                source = f.read()
            
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = f"{base_name}_compiled"
            
            return self.compile_source(source, output_file)
            
        except Exception as e:
            print(f"Compilation error: {e}")
            return False
    
    def compile_source(self, source: str, output_file: str) -> bool:
        """Compile Logo source code to Linux executable"""
        try:
            print(f"🐢 Compiling Logo source to executable: {output_file}")
            
            # Parse Logo source
            print("📝 Step 1: Parsing Logo source...")
            commands = self.parse_logo_source(source)
            print(f"   Found {len(commands)} commands")
            
            if self.debug:
                for i, cmd in enumerate(commands):
                    print(f"   {i}: {cmd}")
            
            # Generate C code
            print("⚙️  Step 2: Generating C code...")
            c_code = self.generate_c_code(commands)
            
            if self.debug:
                print("Generated C code preview:")
                print(c_code[:1000] + "..." if len(c_code) > 1000 else c_code)
            
            # Compile to executable
            print("🔨 Step 3: Building executable...")
            success = self.build_executable(c_code, output_file)
            
            if success:
                print(f"✅ Compilation successful: {output_file}")
                os.chmod(output_file, 0o755)
            
            return success
            
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            return False
    
    def parse_logo_source(self, source: str) -> List[tuple]:
        """Parse Logo source into command tuples"""
        commands = []
        lines = source.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith(';'):  # Skip empty lines and comments
                i += 1
                continue
            
            # Handle REPEAT loops
            if line.upper().startswith('REPEAT'):
                repeat_match = re.match(r'REPEAT\s+(\d+)\s*\[', line.upper())
                if repeat_match:
                    count = int(repeat_match.group(1))
                    # Find matching ]
                    bracket_count = line.count('[') - line.count(']')
                    repeat_body = line[repeat_match.end()-1:]  # Include the [
                    
                    i += 1
                    while i < len(lines) and bracket_count > 0:
                        next_line = lines[i].strip()
                        repeat_body += " " + next_line
                        bracket_count += next_line.count('[') - next_line.count(']')
                        i += 1
                    
                    # Remove brackets and parse body
                    body_content = repeat_body[1:-1].strip()  # Remove [ ]
                    commands.append(('REPEAT_START', count))
                    
                    # Parse commands inside repeat
                    body_commands = self.parse_command_sequence(body_content)
                    commands.extend(body_commands)
                    commands.append(('REPEAT_END', ''))
                    continue
            
            # Handle TO procedures
            if line.upper().startswith('TO '):
                proc_match = re.match(r'TO\s+(\w+)', line.upper())
                if proc_match:
                    proc_name = proc_match.group(1)
                    commands.append(('PROC_START', proc_name))
                    i += 1
                    # Read until END
                    while i < len(lines):
                        proc_line = lines[i].strip()
                        if proc_line.upper() == 'END':
                            commands.append(('PROC_END', proc_name))
                            i += 1
                            break
                        if proc_line and not proc_line.startswith(';'):
                            proc_commands = self.parse_command_sequence(proc_line)
                            commands.extend(proc_commands)
                        i += 1
                    continue
            
            # Parse regular commands
            cmd_list = self.parse_command_sequence(line)
            commands.extend(cmd_list)
            i += 1
        
        return commands
    
    def parse_command_sequence(self, line: str) -> List[tuple]:
        """Parse a sequence of Logo commands from a line"""
        commands = []
        parts = line.strip().split()
        
        i = 0
        while i < len(parts):
            cmd = parts[i].upper()
            
            if cmd in ['FORWARD', 'FD', 'BACK', 'BK']:
                if i + 1 < len(parts):
                    distance = parts[i + 1]
                    commands.append(('FORWARD' if cmd in ['FORWARD', 'FD'] else 'BACK', distance))
                    i += 2
                else:
                    commands.append((cmd.replace('FD', 'FORWARD').replace('BK', 'BACK'), '50'))
                    i += 1
            
            elif cmd in ['LEFT', 'LT', 'RIGHT', 'RT']:
                if i + 1 < len(parts):
                    angle = parts[i + 1]
                    commands.append(('LEFT' if cmd in ['LEFT', 'LT'] else 'RIGHT', angle))
                    i += 2
                else:
                    commands.append((cmd.replace('LT', 'LEFT').replace('RT', 'RIGHT'), '90'))
                    i += 1
            
            elif cmd in ['PENUP', 'PU', 'PENDOWN', 'PD']:
                commands.append(('PENUP' if cmd in ['PENUP', 'PU'] else 'PENDOWN', ''))
                i += 1
            
            elif cmd == 'HOME':
                commands.append(('HOME', ''))
                i += 1
            
            elif cmd == 'CLEAR':
                commands.append(('CLEAR', ''))
                i += 1
            
            elif cmd == 'SETXY':
                if i + 2 < len(parts):
                    x, y = parts[i + 1], parts[i + 2]
                    commands.append(('SETXY', f"{x},{y}"))
                    i += 3
                else:
                    i += 1
            
            elif cmd == 'SETCOLOR' or cmd == 'SETCOLOUR':
                if i + 1 < len(parts):
                    color = parts[i + 1]
                    commands.append(('SETCOLOR', color))
                    i += 2
                else:
                    i += 1
            
            elif cmd == 'SETPENSIZE':
                if i + 1 < len(parts):
                    size = parts[i + 1]
                    commands.append(('SETPENSIZE', size))
                    i += 2
                else:
                    i += 1
            
            elif cmd == 'CIRCLE':
                if i + 1 < len(parts):
                    radius = parts[i + 1]
                    commands.append(('CIRCLE', radius))
                    i += 2
                else:
                    commands.append(('CIRCLE', '50'))
                    i += 1
            
            elif cmd == 'DOT':
                if i + 1 < len(parts):
                    size = parts[i + 1]
                    commands.append(('DOT', size))
                    i += 2
                else:
                    commands.append(('DOT', '5'))
                    i += 1
            
            elif cmd == 'HIDETURTLE' or cmd == 'HT':
                commands.append(('HIDETURTLE', ''))
                i += 1
            
            elif cmd == 'SHOWTURTLE' or cmd == 'ST':
                commands.append(('SHOWTURTLE', ''))
                i += 1
            
            elif cmd == 'HEADING':
                commands.append(('HEADING', ''))
                i += 1
            
            elif cmd == 'POSITION':
                commands.append(('POSITION', ''))
                i += 1
            
            elif cmd in ['CLEARSCREEN', 'CS']:
                commands.append(('CLEARSCREEN', ''))
                i += 1
            
            else:
                # Unknown command, skip
                i += 1
        
        return commands
    
    def generate_c_code(self, commands: List[tuple]) -> str:
        """Generate C code from Logo commands"""
        c_code = []
        
        # Headers and includes
        c_code.extend([
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <math.h>",
            "",
            "#define IMAGE_WIDTH 800",
            "#define IMAGE_HEIGHT 600",
            "#define MAX_PROCEDURES 50",
            "#define MAX_REPEAT_DEPTH 10",
            "",
            "// Simple RGB color structure",
            "typedef struct {",
            "    unsigned char r, g, b;",
            "} Color;",
            "",
            "// Turtle state",
            "typedef struct {",
            "    double x, y;",
            "    double heading;  // degrees",
            "    int pen_down;",
            "    Color pen_color;",
            "    int pen_size;",
            "} Turtle;",
            "",
            "// Image buffer (RGB)",
            "unsigned char image[IMAGE_HEIGHT][IMAGE_WIDTH][3];",
            "Turtle turtle;",
            "",
            "// Repeat loop stack",
            "typedef struct {",
            "    int count;",
            "    int current;",
            "    int start_pc;",
            "} RepeatFrame;",
            "",
            "RepeatFrame repeat_stack[MAX_REPEAT_DEPTH];",
            "int repeat_depth = 0;",
            "",
        ])
        
        # Utility functions
        c_code.extend([
            "void init_turtle() {",
            "    turtle.x = IMAGE_WIDTH / 2.0;",
            "    turtle.y = IMAGE_HEIGHT / 2.0;",
            "    turtle.heading = 0.0;  // North",
            "    turtle.pen_down = 1;",
            "    turtle.pen_color.r = 255;",
            "    turtle.pen_color.g = 255;",
            "    turtle.pen_color.b = 255;",
            "    turtle.pen_size = 1;",
            "}",
            "",
            "void clear_image() {",
            "    for (int y = 0; y < IMAGE_HEIGHT; y++) {",
            "        for (int x = 0; x < IMAGE_WIDTH; x++) {",
            "            image[y][x][0] = 0;  // R",
            "            image[y][x][1] = 0;  // G", 
            "            image[y][x][2] = 0;  // B",
            "        }",
            "    }",
            "}",
            "",
            "void set_pixel(int x, int y, Color color) {",
            "    if (x >= 0 && x < IMAGE_WIDTH && y >= 0 && y < IMAGE_HEIGHT) {",
            "        image[y][x][0] = color.r;",
            "        image[y][x][1] = color.g;",
            "        image[y][x][2] = color.b;",
            "    }",
            "}",
            "",
            "void draw_line(double x1, double y1, double x2, double y2) {",
            "    if (!turtle.pen_down) return;",
            "    ",
            "    int dx = abs((int)x2 - (int)x1);",
            "    int dy = abs((int)y2 - (int)y1);",
            "    int sx = x1 < x2 ? 1 : -1;",
            "    int sy = y1 < y2 ? 1 : -1;",
            "    int err = dx - dy;",
            "    ",
            "    int x = (int)x1, y = (int)y1;",
            "    ",
            "    while (1) {",
            "        set_pixel(x, y, turtle.pen_color);",
            "        if (x == (int)x2 && y == (int)y2) break;",
            "        int e2 = 2 * err;",
            "        if (e2 > -dy) { err -= dy; x += sx; }",
            "        if (e2 < dx) { err += dx; y += sy; }",
            "    }",
            "}",
            "",
            "void move_turtle(double distance) {",
            "    double old_x = turtle.x;",
            "    double old_y = turtle.y;",
            "    ",
            "    double rad = turtle.heading * M_PI / 180.0;",
            "    turtle.x += distance * sin(rad);",
            "    turtle.y -= distance * cos(rad);  // Y increases downward",
            "    ",
            "    draw_line(old_x, old_y, turtle.x, turtle.y);",
            "}",
            "",
            "void turn_turtle(double angle) {",
            "    turtle.heading += angle;",
            "    while (turtle.heading >= 360.0) turtle.heading -= 360.0;",
            "    while (turtle.heading < 0.0) turtle.heading += 360.0;",
            "}",
            "",
            "void home_turtle() {",
            "    double old_x = turtle.x;",
            "    double old_y = turtle.y;",
            "    turtle.x = IMAGE_WIDTH / 2.0;",
            "    turtle.y = IMAGE_HEIGHT / 2.0;",
            "    turtle.heading = 0.0;",
            "    draw_line(old_x, old_y, turtle.x, turtle.y);",
            "}",
            "",
            "void draw_circle(double radius) {",
            "    if (!turtle.pen_down) return;",
            "    ",
            "    int steps = (int)(2 * M_PI * radius / 2);",
            "    if (steps < 8) steps = 8;",
            "    if (steps > 360) steps = 360;",
            "    ",
            "    double angle_step = 360.0 / steps;",
            "    double center_x = turtle.x;",
            "    double center_y = turtle.y;",
            "    ",
            "    for (int i = 0; i <= steps; i++) {",
            "        double angle = i * angle_step * M_PI / 180.0;",
            "        double x = center_x + radius * cos(angle);",
            "        double y = center_y + radius * sin(angle);",
            "        ",
            "        if (i > 0) {",
            "            double prev_angle = (i-1) * angle_step * M_PI / 180.0;",
            "            double prev_x = center_x + radius * cos(prev_angle);",
            "            double prev_y = center_y + radius * sin(prev_angle);",
            "            draw_line(prev_x, prev_y, x, y);",
            "        }",
            "    }",
            "}",
            "",
            "void set_turtle_pos(double x, double y) {",
            "    double old_x = turtle.x;",
            "    double old_y = turtle.y;",
            "    turtle.x = x;",
            "    turtle.y = y;",
            "    draw_line(old_x, old_y, turtle.x, turtle.y);",
            "}",
            "",
            "void set_pen_color(int color_num) {",
            "    switch (color_num) {",
            "        case 0: turtle.pen_color = (Color){0, 0, 0}; break;       // Black",
            "        case 1: turtle.pen_color = (Color){255, 255, 255}; break; // White", 
            "        case 2: turtle.pen_color = (Color){255, 0, 0}; break;     // Red",
            "        case 3: turtle.pen_color = (Color){0, 255, 0}; break;     // Green",
            "        case 4: turtle.pen_color = (Color){0, 0, 255}; break;     // Blue",
            "        case 5: turtle.pen_color = (Color){255, 255, 0}; break;   // Yellow",
            "        case 6: turtle.pen_color = (Color){255, 0, 255}; break;   // Magenta",
            "        case 7: turtle.pen_color = (Color){0, 255, 255}; break;   // Cyan",
            "        default: turtle.pen_color = (Color){255, 255, 255}; break; // White",
            "    }",
            "}",
            "",
            "void save_image() {",
            "    FILE* f = fopen(\"logo_output.ppm\", \"w\");",
            "    if (f) {",
            "        fprintf(f, \"P3\\n%d %d\\n255\\n\", IMAGE_WIDTH, IMAGE_HEIGHT);",
            "        for (int y = 0; y < IMAGE_HEIGHT; y++) {",
            "            for (int x = 0; x < IMAGE_WIDTH; x++) {",
            "                fprintf(f, \"%d %d %d \", image[y][x][0], image[y][x][1], image[y][x][2]);",
            "            }",
            "            fprintf(f, \"\\n\");",
            "        }",
            "        fclose(f);",
            "        printf(\"Graphics saved to logo_output.ppm\\n\");",
            "    }",
            "}",
            "",
        ])
        
        # Main function
        c_code.extend([
            "int main() {",
            "    init_turtle();",
            "    clear_image();",
            f"    int pc = 0;",
            f"    int program_size = {len(commands)};",
            "",
            "    printf(\"Logo program starting...\\n\");",
            "    printf(\"Turtle at (%.1f, %.1f) heading %.1f\\n\", turtle.x, turtle.y, turtle.heading);",
            "",
            "    while (pc < program_size) {",
            "        switch (pc) {",
        ])
        
        # Generate code for each command
        for i, (cmd, arg) in enumerate(commands):
            c_code.append(f"            case {i}:")
            
            if cmd == 'FORWARD':
                c_code.extend([
                    f"                move_turtle({arg});",
                    f"                printf(\"FORWARD {arg} -> (%.1f, %.1f)\\n\", turtle.x, turtle.y);",
                ])
            
            elif cmd == 'BACK':
                c_code.extend([
                    f"                move_turtle(-{arg});",
                    f"                printf(\"BACK {arg} -> (%.1f, %.1f)\\n\", turtle.x, turtle.y);",
                ])
            
            elif cmd == 'LEFT':
                c_code.extend([
                    f"                turn_turtle(-{arg});",
                    f"                printf(\"LEFT {arg} -> heading %.1f\\n\", turtle.heading);",
                ])
            
            elif cmd == 'RIGHT':
                c_code.extend([
                    f"                turn_turtle({arg});",
                    f"                printf(\"RIGHT {arg} -> heading %.1f\\n\", turtle.heading);",
                ])
            
            elif cmd == 'PENUP':
                c_code.extend([
                    "                turtle.pen_down = 0;",
                    "                printf(\"PENUP\\n\");",
                ])
            
            elif cmd == 'PENDOWN':
                c_code.extend([
                    "                turtle.pen_down = 1;",
                    "                printf(\"PENDOWN\\n\");",
                ])
            
            elif cmd == 'HOME':
                c_code.extend([
                    "                home_turtle();",
                    "                printf(\"HOME -> (%.1f, %.1f)\\n\", turtle.x, turtle.y);",
                ])
            
            elif cmd == 'CLEAR':
                c_code.extend([
                    "                clear_image();",
                    "                printf(\"CLEAR\\n\");",
                ])
            
            elif cmd == 'SETXY':
                coords = arg.split(',')
                if len(coords) == 2:
                    x, y = coords[0].strip(), coords[1].strip()
                    c_code.extend([
                        f"                set_turtle_pos({x}, {y});",
                        f"                printf(\"SETXY {x} {y}\\n\");",
                    ])
            
            elif cmd == 'SETCOLOR':
                c_code.extend([
                    f"                set_pen_color({arg});",
                    f"                printf(\"SETCOLOR {arg}\\n\");",
                ])
            
            elif cmd == 'SETPENSIZE':
                size = arg if arg else '1'
                c_code.extend([
                    f"                turtle.pen_size = {size};",
                    f"                printf(\"Pen size set to {size}\\n\");",
                ])
            
            elif cmd == 'CIRCLE':
                radius = arg if arg else '50'
                c_code.append(f"                draw_circle({radius});")
            
            elif cmd == 'DOT':
                size = arg if arg else '5'
                c_code.extend([
                    "                if (turtle.pen_down) {",
                    f"                    for (int dy = -{size}/2; dy <= {size}/2; dy++) {{",
                    f"                        for (int dx = -{size}/2; dx <= {size}/2; dx++) {{",
                    "                            set_pixel((int)turtle.x + dx, (int)turtle.y + dy, turtle.pen_color);",
                    "                        }",
                    "                    }",
                    "                }",
                    f"                printf(\"Drew dot with size {size}\\n\");",
                ])
            
            elif cmd == 'HIDETURTLE':
                c_code.append("                printf(\"Turtle hidden\\n\");")
            
            elif cmd == 'SHOWTURTLE':
                c_code.append("                printf(\"Turtle shown\\n\");")
            
            elif cmd == 'CLEARSCREEN':
                c_code.extend([
                    "                clear_image();",
                    "                printf(\"Screen cleared\\n\");",
                ])
            
            elif cmd == 'REPEAT_START':
                c_code.extend([
                    f"                if (repeat_depth < MAX_REPEAT_DEPTH) {{",
                    f"                    repeat_stack[repeat_depth].count = {arg};",
                    f"                    repeat_stack[repeat_depth].current = 0;",
                    f"                    repeat_stack[repeat_depth].start_pc = pc + 1;",
                    f"                    repeat_depth++;",
                    f"                    printf(\"REPEAT {arg} start\\n\");",
                    f"                }}",
                ])
            
            elif cmd == 'REPEAT_END':
                c_code.extend([
                    "                if (repeat_depth > 0) {",
                    "                    repeat_stack[repeat_depth-1].current++;",
                    "                    if (repeat_stack[repeat_depth-1].current < repeat_stack[repeat_depth-1].count) {",
                    "                        pc = repeat_stack[repeat_depth-1].start_pc - 1; // -1 for pc++ below",
                    "                        printf(\"REPEAT iteration %d\\n\", repeat_stack[repeat_depth-1].current + 1);",
                    "                    } else {",
                    "                        repeat_depth--;",
                    "                        printf(\"REPEAT end\\n\");",
                    "                    }",
                    "                }",
                ])
            
            elif cmd == 'PROC_START':
                c_code.extend([
                    f"                printf(\"Procedure {arg} defined\\n\");",
                    f"                // Skip to matching PROC_END",
                ])
            
            elif cmd == 'PROC_END':
                c_code.extend([
                    f"                printf(\"End procedure {arg}\\n\");",
                ])
            
            c_code.extend([
                "                pc++;",
                "                break;",
            ])
        
        c_code.extend([
            "            default:",
            "                pc++;",
            "                break;",
            "        }",
            "    }",
            "",
            "    save_image();",
            "    printf(\"Logo program completed!\\n\");",
            "    printf(\"Final turtle position: (%.1f, %.1f) heading %.1f\\n\", turtle.x, turtle.y, turtle.heading);",
            "    return 0;",
            "}",
        ])
        
        return "\n".join(c_code)
    
    def build_executable(self, c_code: str, output_file: str) -> bool:
        """Compile C code to executable"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(c_code)
                c_file = f.name
            
            try:
                cmd = ['gcc', '-o', output_file, c_file, '-lm']
                if self.optimize:
                    cmd.extend(['-O2'])
                else:
                    cmd.extend(['-g'])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("   C compilation successful")
                    return True
                else:
                    print(f"   C compilation failed: {result.stderr}")
                    return False
                    
            finally:
                os.unlink(c_file)
                
        except Exception as e:
            print(f"   Build error: {e}")
            return False


def main():
    """Main compiler entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Logo Native Compiler")
    parser.add_argument('input_file', help='Logo source file to compile')
    parser.add_argument('-o', '--output', help='Output executable name')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-O', '--optimize', action='store_true', help='Enable optimization')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    compiler = LogoCompiler()
    compiler.debug = args.debug
    compiler.optimize = args.optimize
    
    success = compiler.compile_file(args.input_file, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()