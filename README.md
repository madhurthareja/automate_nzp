# NZP CLI Automation Tool

A command-line interface tool that uses two Ollama models to create structured project documentation following NZP (Non-Zero Project) methodology.

## Overview

This tool automates the creation of project documentation by using:
- **Model A (Interviewer)**: Asks structured questions for each section
- **Model B (Responder)**: Generates draft answers
- **Interactive Editor**: Allows you to review, edit, or regenerate responses

## Features

- Interactive CLI with rich formatting
- Two-model conversation system (interviewer + responder)
- Built-in validation for word count requirements
- Inline text editor for answer refinement
- Automatic compilation to markdown format
- Configurable Ollama models

## Requirements

- Python 3.9+
- Ollama installed and running
- At least one Ollama model downloaded

## Installation

1. Run the setup script:
```bash
./setup.zsh
```

2. Or install manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests rich prompt_toolkit
```

## Usage

### Basic Usage
```bash
source .venv/bin/activate
python nzp_cli.py --project "Your Project Name"
```

### Advanced Usage
```bash
python nzp_cli.py \
  --project "AI Documentation System" \
  --interviewer-model "llama3.1:8b-instruct-q4_K_M" \
  --responder-model "llama3.2:3b-instruct-q4_K_M" \
  --type "Technical Documentation"
```

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project` | Project name (required) | - |
| `--interviewer-model` | Model for asking questions | llama3.1:8b-instruct-q4_K_M |
| `--responder-model` | Model for generating answers | llama3.2:3b-instruct-q4_K_M |
| `--type` | Project type/profile | General |

## Interactive Commands

During the interview process, you can:
- **a** - Accept the current answer
- **e** - Edit the answer (use Ctrl+D to save)
- **r** - Regenerate the answer
- **q** - Quit the session

## NZP Structure

The tool generates documentation with these sections:

### Objective (What)
- Minimum 150 words
- Single paragraph format
- Describes project outcomes and deliverables

### Purpose (Why)
- Minimum 100 words
- Explains project importance and impact

### Plan-of-Action (How)
- Detailed actionable steps
- Implementation methodology

### Progress-so-far (Status)
- Minimum 10 words
- Current project status

### Glossary (Appendix)
- Key terms and definitions
- Project-specific concepts

## Output

The tool generates a markdown file named after your project:
```
your_project_name.md
```

## Troubleshooting

### Common Issues

**Error: Unable to connect to Ollama**
- Ensure Ollama is running: `ollama serve`
- Check if models are available: `ollama list`

**Model not found**
- Download required models: `ollama pull llama3.1:8b-instruct-q4_K_M`

**Edit mode not working**
- Use Ctrl+D to save and exit the editor
- Use Ctrl+C to cancel editing

## Examples

### Documentation Project
```bash
python nzp_cli.py --project "API Documentation System"
```

### Research Project
```bash
python nzp_cli.py --project "Machine Learning Model Evaluation" --type "Research"
```

## File Structure

```
automate_nzp/
├── nzp_cli.py          # Main CLI application
├── setup.zsh           # Setup script
├── README.md           # This file
├── .venv/              # Python virtual environment
└── *.md                # Generated project files
```

## Contributing

This is a utility tool for creating structured project documentation. Feel free to modify the prompts and validation rules to fit your specific needs.

## License

This project is provided as-is for educational and productivity purposes.
