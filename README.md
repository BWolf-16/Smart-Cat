# Smart Cat AI Assistant Plugin 🐱👓

*Version 1.0.0*

An AI-powered assistant plugin for KiCad 7+ that helps analyze and improve PCB and schematic designs using Claude or OpenAI APIs. Smart Cat is your intelligent companion for electronics design - from simple circuit requests to complex PCB layouts!

## Features

- **AI-Powered Design Analysis**: Get intelligent feedback on your PCB layouts and schematics
- **Context-Aware**: Automatically detects your current design and provides relevant context to the AI
- **Multiple AI Providers**: Supports Claude (Anthropic), OpenAI, and any OpenAI-compatible API
- **User-Owned API Keys**: No hardcoded keys - you use your own API credentials
- **Modern UI**: Clean PyQt interface with dockable assistant window
- **Real-time Analysis**: Analyze components, nets, traces, vias, and design rules
- **Design Rule Integration**: Includes DRC information in AI analysis

## Installation

### Method 1: Manual Installation

1. **Download the Plugin**: Extract the `kicat_ai` folder to your KiCad plugins directory:
   - **Windows**: `%APPDATA%\kicad\7.0\scripting\plugins\`
   - **macOS**: `~/Library/Application Support/kicad/7.0/scripting/plugins/`
   - **Linux**: `~/.local/share/kicad/7.0/scripting/plugins/`

2. **Restart KiCad**: Close and reopen KiCad PCB Editor

3. **Verify Installation**: Look for "KiCat AI Assistant" in the Tools menu or plugin toolbar

### Method 2: Plugin Manager (if available)

1. Open KiCad Plugin and Content Manager
2. Search for "KiCat AI Assistant"
3. Click Install

## Setup

### First Time Configuration

1. **Launch the Plugin**: Click the KiCat AI Assistant button in KiCad's toolbar
2. **Open Settings**: Click the gear (⚙) icon in the assistant window
3. **Configure API**:
   - Select your preferred API provider (Claude, OpenAI, or Custom)
   - Enter your API key
   - Choose a model
   - For custom providers, set the base URL
   - Click "Test API Connection" to verify
4. **Save Settings**: Click "Save" to store your configuration

### API Keys

You'll need an API key from one of these providers:

**Claude (Anthropic)**:
- Sign up at https://console.anthropic.com
- Generate an API key (starts with `sk-ant-`)
- Recommended models: `claude-3-sonnet-20240229` (balanced), `claude-3-opus-20240229` (advanced)

**OpenAI**:
- Sign up at https://platform.openai.com
- Generate an API key (starts with `sk-`)
- Recommended models: `gpt-4-turbo-preview`, `gpt-4`

**Custom OpenAI-Compatible APIs**:
- Many providers offer OpenAI-compatible endpoints (e.g., local LLMs, hosted services)
- Set the base URL to your provider's endpoint
- Use the appropriate API key format for your provider
- Common examples: Ollama, LM Studio, Together AI, Replicate

## Usage

### Basic Usage

1. **Open a PCB or Schematic** in KiCad
2. **Launch KiCat AI Assistant** from the toolbar
3. **Ask Questions** like:
   - "Analyze my current PCB design"
   - "What potential issues do you see with component placement?"
   - "How can I improve signal integrity?"
   - "Review my power distribution"
   - "Check for EMI considerations"

### Context Detection

The assistant automatically detects:
- **PCB Context**: Components, nets, traces, vias, board dimensions, layer count
- **Design Rules**: Track widths, via sizes, clearances
- **DRC Information**: Design rule violations (if enabled)

### Example Questions

**Design Analysis**:
- "What do you think of my component placement?"
- "Are there any potential signal integrity issues?"
- "How can I optimize my routing?"

**Specific Reviews**:
- "Check my power supply section"
- "Review the high-speed signals"
- "Analyze thermal considerations"

**Learning & Improvement**:
- "Explain why this layout might cause EMI"
- "What are best practices for this type of circuit?"
- "How can I reduce crosstalk?"

## Configuration Options

### API Settings
- **Provider**: Choose between Claude, OpenAI, or Custom
- **API Key**: Your personal API key
- **Model**: Select specific AI model
- **Base URL**: Custom API endpoints (for OpenAI-compatible services)

### Advanced Settings
- **Max Tokens**: Response length limit (100-8192)
- **Temperature**: Creativity level (0-100%)
- **Chat History**: Number of messages to retain (10-200)
- **Auto Context**: Automatically include design context
- **Include DRC**: Add design rule check information

## File Structure

```
kicat_ai/
├── __init__.py          # Plugin initialization
├── main.py              # KiCad plugin entry point
├── ui.py                # PyQt user interface
├── config.py            # Configuration management
├── AI_API.py            # Universal AI API communication
├── parser.py            # KiCad context extraction
└── resources/
    └── icon.png         # Plugin icon
```

## Requirements

- **KiCad**: Version 7.0 or higher
- **Python**: 3.6+ (included with KiCad)
- **PyQt5/PyQt6**: Usually included with KiCad
- **Internet Connection**: For AI API calls
- **API Key**: From Claude (Anthropic) or OpenAI

## Troubleshooting

### Plugin Not Appearing
- Verify the plugin is in the correct directory
- Check file permissions
- Restart KiCad completely
- Check the KiCad console for error messages

### API Connection Issues
- Verify your API key is correct
- Check internet connection
- Test with the "Test API Connection" button
- Ensure you have API credits/quota available

### UI Issues
- Try closing and reopening the assistant window
- Check if PyQt is properly installed with KiCad
- Restart KiCad if the interface becomes unresponsive

### Context Not Detected
- Ensure you have an active PCB or schematic open
- Try closing and opening the design file
- Check that the design is saved

## Privacy & Security

- **API Keys**: Stored locally in encrypted configuration files
- **Design Data**: Only sent to AI when you ask questions
- **No Telemetry**: No usage data is collected by the plugin
- **Local Processing**: All design parsing happens locally

## Support

- **Issues**: Report bugs and issues on the project repository
- **Feature Requests**: Suggest improvements via GitHub issues
- **Documentation**: Check the README for latest information

## License

MIT License - See LICENSE file for details.

## Version History

### v1.0.0
- Initial release
- Claude and OpenAI API support
- PCB context analysis
- PyQt-based UI
- Configuration management
- Design rule integration

---

**Disclaimer**: This plugin sends design context to external AI services when you ask questions. Only use with designs you're comfortable sharing with your chosen AI provider. Always review AI suggestions before implementing them in your designs.
