#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Retro Media Processing Tools - Installation Script${NC}"
echo ""

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV is not installed. Installing UV...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Failed to install UV. Please install it manually.${NC}"
        exit 1
    fi
    echo -e "${GREEN}UV installed successfully!${NC}"
else
    echo -e "${GREEN}UV is already installed.${NC}"
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
uv venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
uv pip install -r requirements.txt

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}FFmpeg is not installed. For full video support with audio, please install FFmpeg:${NC}"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  - Windows: Download from https://ffmpeg.org/download.html"
    echo ""
fi

echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To start using the tools:"
echo "1. Activate the virtual environment (if not already activated):"
echo "   source .venv/bin/activate"
echo "2. Run the main script:"
echo "   python main.py"
echo ""
echo -e "${GREEN}Enjoy the Retro Media Processing Tools!${NC}"