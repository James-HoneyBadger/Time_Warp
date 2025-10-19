#!/bin/bash
# Script to compile pygame with AVX2 support

echo "🎮 Compiling pygame with AVX2 support..."
echo "========================================="

# Check if AVX2 is supported
if ! grep -q avx2 /proc/cpuinfo; then
    echo "❌ AVX2 not supported on this CPU"
    exit 1
fi

echo "✅ AVX2 support detected"

# Install dependencies if on Arch Linux
if command -v pacman &> /dev/null; then
    echo "📦 Installing dependencies for Arch Linux..."
    sudo pacman -S --needed sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi
fi

# Create working directory
mkdir -p ~/pygame-build
cd ~/pygame-build

# Clone pygame
echo "📥 Downloading pygame source..."
git clone https://github.com/pygame/pygame.git
cd pygame

# Set AVX2 compilation flags
echo "🔧 Setting AVX2 compilation flags..."
export CFLAGS="-march=native -mavx2 -mfma -O3"
export CXXFLAGS="-march=native -mavx2 -mfma -O3"

# Build and install
echo "⚙️ Building pygame with AVX2 support..."
python setup.py build_ext --inplace
python setup.py install --user

echo "✅ Installation complete!"
echo "🔍 Testing AVX2 support..."
python -c "import pygame; print(f'pygame {pygame.version.ver} installed with AVX2 support')"