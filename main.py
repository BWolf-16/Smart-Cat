"""
Smart Cat AI Assistant - Main KiCad Action Plugin Entry Point 🐱👓
"""

import sys
import os

# Add plugin directory to path for imports
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    import pcbnew
    from .ui import SmartCatAssistantWindow
    from .config import config
except ImportError as e:
    print(f"Import error in Smart Cat AI Assistant: {e}")
    pcbnew = None


class SmartCatAIAssistantPlugin(pcbnew.ActionPlugin):
    """
    KiCad Action Plugin for Smart Cat AI-powered design assistance
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Smart Cat AI Assistant"
        self.category = "Design Tools"
        self.description = "AI-powered assistant for schematic and PCB design analysis with automatic circuit generation"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(plugin_dir, "resources", "smart_cat_logo.png")
        
        # Store reference to assistant window
        self.assistant_window = None
    
    def defaults(self):
        """Set up default plugin configuration"""
        self.name = "Smart Cat AI Assistant"
        self.category = "Design Tools" 
        self.description = "AI-powered assistant for schematic and PCB design analysis"
        self.show_toolbar_button = True
    
    def Run(self):
        """Main plugin execution - called when user clicks the plugin button"""
        try:
            # Check if window already exists
            if self.assistant_window is not None:
                # Bring existing window to front
                self.assistant_window.show()
                self.assistant_window.raise_()
                self.assistant_window.activateWindow()
                return
            
            # Create new assistant window
            self.assistant_window = SmartCatAssistantWindow()
            
            # Set up window close event to clean up reference
            def on_window_close():
                self.assistant_window = None
            
            self.assistant_window.window_closed.connect(on_window_close)
            
            # Show the assistant window
            self.assistant_window.show()
            
        except Exception as e:
            # Fallback error handling
            try:
                import wx
                wx.MessageBox(
                    f"Error launching Smart Cat AI Assistant: {str(e)}\n\n"
                    "Please check the plugin installation and try again.",
                    "Smart Cat AI Assistant Error",
                    wx.OK | wx.ICON_ERROR
                )
            except:
                print(f"Smart Cat AI Assistant Error: {e}")


# Register the plugin
if pcbnew:
    SmartCatAIAssistantPlugin().register()
else:
    print("Smart Cat AI Assistant: PCBNew not available, plugin not registered")


def get_plugin_version():
    """Get plugin version"""
    return "1.0.0"


def get_plugin_info():
    """Get plugin information"""
    return {
        "name": "Smart Cat AI Assistant",
        "version": get_plugin_version(),
        "description": "AI-powered assistant for schematic and PCB design analysis with automatic circuit generation",
        "author": "Smart Cat AI Team",
        "license": "MIT",
        "kicad_version": "7.0+",
        "python_version": "3.6+"
    }


# Plugin metadata for KiCad
__version__ = get_plugin_version()
__author__ = "Smart Cat AI Team"
__email__ = "support@smartcat-ai.com"
__license__ = "MIT"
