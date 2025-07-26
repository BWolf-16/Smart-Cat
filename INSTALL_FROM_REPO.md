# Smart Cat AI Assistant - Install from Repository 🐱👓

This guide explains how to install the Smart Cat AI Assistant directly from the GitHub repository, ensuring you always get the latest version.

## Quick Installation Methods

### Method 1: One-Line Installation (Windows)

Download and run the installer batch file:

```powershell
# Download and run installer
curl -o install_from_repo.bat https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/install_from_repo.bat
install_from_repo.bat
```

### Method 2: One-Line Installation (macOS/Linux)

```bash
# Download and run installer
curl -o install_from_repo.sh https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/install_from_repo.sh
chmod +x install_from_repo.sh
./install_from_repo.sh
```

### Method 3: Direct Python Installation

```bash
# Download setup script and install
curl -o setup.py https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/setup.py
python setup.py install-repo
```

## Advanced Installation Options

### Install from Specific Branch

```bash
python setup.py install-repo https://github.com/BWolf-16/Smart-Cat development
```

### Install from Fork

```bash
python setup.py install-repo https://github.com/your-username/Smart-Cat main
```

### Check Requirements First

```bash
python setup.py check
python setup.py install-repo
```

## What Happens During Installation

1. **Downloads** the latest code from GitHub
2. **Extracts** the repository archive
3. **Copies** essential plugin files to KiCad's plugin directory
4. **Preserves** only necessary files (excludes documentation, tests, etc.)
5. **Cleans up** temporary files

## Installation Locations

The plugin will be installed to:
- **Windows**: `%APPDATA%\kicad\7.0\scripting\plugins\smart_cat\`
- **macOS**: `~/Library/Application Support/kicad/7.0/scripting/plugins/smart_cat/`
- **Linux**: `~/.local/share/kicad/7.0/scripting/plugins/smart_cat/`

## After Installation

1. **Restart KiCad** completely
2. Look for **"Smart Cat AI Assistant"** in the toolbar or Tools menu
3. **Configure your API key** in the plugin settings
4. Start designing with AI assistance! 🚀

## Troubleshooting

### Python Not Found
- Install Python 3.6+ from [python.org](https://python.org)
- Make sure Python is in your system PATH

### Download Failed
- Check your internet connection
- Verify the repository URL is correct
- Try using a VPN if behind restrictive firewall

### Permission Errors
- Run as Administrator (Windows) or with sudo (Linux/macOS)
- Check that KiCad plugin directory is writable

## Update Plugin

To update to the latest version, simply run the installation command again:

```bash
python setup.py install-repo
```

This will replace the existing installation with the latest version from GitHub.

## Uninstall

```bash
python setup.py uninstall
```

---

**Enjoy your Smart Cat AI Assistant! 🐱👓✨**
