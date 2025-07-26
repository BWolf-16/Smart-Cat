"""
Test script to verify Smart Cat AI Assistant plugin loading
Run this in KiCad's scripting console to debug plugin issues
"""

import sys
import os

def test_plugin_loading():
    """Test if the plugin can be loaded properly"""
    print("Testing Smart Cat AI Assistant plugin loading...")
    
    # Add plugin path
    plugin_path = r"C:\Users\bened\Documents\KiCad\9.0\3rdparty\plugins\com_smartcat_ai_assistant"
    if plugin_path not in sys.path:
        sys.path.insert(0, plugin_path)
        print(f"Added plugin path: {plugin_path}")
    
    # Test imports
    try:
        print("Testing pcbnew import...")
        import pcbnew
        print("✓ pcbnew imported successfully")
        
        print("Testing plugin import...")
        import main
        print("✓ main module imported successfully")
        
        print("Testing plugin class...")
        plugin = main.SmartCatAIAssistantPlugin()
        print(f"✓ Plugin created: {plugin.name}")
        
        print("Testing plugin registration...")
        plugin.register()
        print("✓ Plugin registered successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_plugin_loading()
