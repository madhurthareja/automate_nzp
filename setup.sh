#!/bin/zsh

# NZP CLI Automation Tool Setup Script

echo "Setting up NZP CLI Automation Tool..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama is not installed. Please install Ollama from https://ollama.ai and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install required packages
echo "Installing required Python packages..."
pip install --upgrade pip
pip install requests rich prompt_toolkit

# Check if Ollama models are available
echo "Checking available Ollama models..."
ollama list

echo "Setup complete!"
echo ""
echo "Usage:"
echo "  source .venv/bin/activate"
echo "  python nzp_cli.py --project \"Your Project Name\""
echo ""
echo "Available options:"
echo "  --project          Project name (required)"
echo "  --interviewer-model Model for asking questions (default: llama3.1:8b-instruct-q4_K_M)"
echo "  --responder-model   Model for generating answers (default: llama3.2:3b-instruct-q4_K_M)"
echo "  --type             Project type/profile (default: General)"
echo ""
echo "Example:"
echo "  python nzp_cli.py --project \"AI Documentation\" --interviewer-model \"phi3:mini\""
