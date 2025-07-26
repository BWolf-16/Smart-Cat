"""
Smart Cat AI Assistant - KiCad Plugin 🐱👓
AI-powered assistant for PCB and schematic design analysis with automatic circuit generation

This plugin provides an AI assistant panel that helps users analyze
and improve their KiCad designs using Claude, OpenAI, or custom APIs.
"""

__version__ = "1.0.0"
__author__ = "Smart Cat AI Team"
__email__ = "support@smartcat-ai.com"
__license__ = "MIT"
__description__ = "AI-powered assistant for KiCad PCB design with automatic circuit generation"

# Plugin metadata
PLUGIN_NAME = "Smart Cat AI Assistant"
PLUGIN_VERSION = __version__
PLUGIN_DESCRIPTION = __description__
KICAD_VERSION_MIN = "7.0.0"

# Import main plugin class for KiCad registration
try:
    from .main import SmartCatAIAssistantPlugin
    
    # This will register the plugin with KiCad
    plugin_instance = SmartCatAIAssistantPlugin()
    
except ImportError as e:
    print(f"Smart Cat AI Assistant: Failed to import main plugin class: {e}")
    plugin_instance = None

# Export public API
__all__ = [
    'SmartCatAIAssistantPlugin',
    'PLUGIN_NAME',
    'PLUGIN_VERSION', 
    'PLUGIN_DESCRIPTION'
]
