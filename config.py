"""
Configuration management for KiCat AI Assistant
Handles API key storage, model selection, and user preferences
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration settings for the KiCat AI Assistant"""
    
    def __init__(self):
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "config.json"
        self.config_data = self._load_config()
    
    def _get_config_directory(self) -> Path:
        """Get the appropriate config directory based on OS"""
        system = platform.system()
        
        if system == "Windows":
            config_dir = Path(os.environ.get("APPDATA", "")) / "kicat-ai"
        elif system == "Darwin":  # macOS
            config_dir = Path.home() / ".config" / "kicat-ai"
        else:  # Linux and others
            config_dir = Path.home() / ".config" / "kicat-ai"
        
        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "api_key": "",
            "api_provider": "claude",  # claude, openai, or custom
            "model": "claude-3-sonnet-20240229",
            "api_base_url": "https://api.anthropic.com",
            "max_tokens": 4096,
            "temperature": 0.3,
            "window_geometry": {
                "width": 500,
                "height": 700,
                "x": 100,
                "y": 100
            },
            "chat_history_limit": 50,
            "auto_detect_context": True,
            "include_drc_errors": True,
            "theme": "default"
        }
        
        if not self.config_file.exists():
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults to handle new config options
            for key, value in default_config.items():
                if key not in loaded_config:
                    loaded_config[key] = value
            
            return loaded_config
        
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def _save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except (PermissionError, IOError) as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value and save"""
        self.config_data[key] = value
        return self._save_config(self.config_data)
    
    def get_api_key(self) -> str:
        """Get the API key"""
        return self.config_data.get("api_key", "")
    
    def set_api_key(self, api_key: str) -> bool:
        """Set the API key"""
        return self.set("api_key", api_key)
    
    def get_model(self) -> str:
        """Get the selected model"""
        return self.config_data.get("model", "claude-3-sonnet-20240229")
    
    def set_model(self, model: str) -> bool:
        """Set the selected model"""
        return self.set("model", model)
    
    def get_api_provider(self) -> str:
        """Get the API provider (claude or openai)"""
        return self.config_data.get("api_provider", "claude")
    
    def set_api_provider(self, provider: str) -> bool:
        """Set the API provider"""
        valid_providers = ["claude", "openai", "custom"]
        if provider not in valid_providers:
            raise ValueError(f"Invalid provider. Must be one of: {valid_providers}")
        return self.set("api_provider", provider)
    
    def get_api_base_url(self) -> str:
        """Get the API base URL"""
        provider = self.get_api_provider()
        if provider == "claude":
            return self.config_data.get("api_base_url", "https://api.anthropic.com")
        elif provider == "openai":
            return self.config_data.get("api_base_url", "https://api.openai.com")
        elif provider == "custom":
            return self.config_data.get("api_base_url", "https://api.custom-provider.com")
        return self.config_data.get("api_base_url", "https://api.anthropic.com")
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get window geometry settings"""
        return self.config_data.get("window_geometry", {
            "width": 500, "height": 700, "x": 100, "y": 100
        })
    
    def set_window_geometry(self, width: int, height: int, x: int, y: int) -> bool:
        """Set window geometry"""
        return self.set("window_geometry", {
            "width": width, "height": height, "x": x, "y": y
        })
    
    def is_configured(self) -> bool:
        """Check if the basic configuration is complete"""
        api_key = self.get_api_key()
        return bool(api_key and api_key.strip())
    
    def get_available_models(self) -> Dict[str, list]:
        """Get available models for each provider"""
        return {
            "claude": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "openai": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ],
            "custom": [
                "llama-2-70b-chat",
                "mixtral-8x7b-instruct",
                "custom-model-1",
                "Enter your model name"
            ]
        }
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        if self.config_file.exists():
            try:
                self.config_file.unlink()
            except PermissionError:
                return False
        
        self.config_data = self._load_config()
        return True
    
    def export_config(self, export_path: str) -> bool:
        """Export configuration to a file (excluding API key for security)"""
        try:
            export_data = self.config_data.copy()
            export_data["api_key"] = ""  # Don't export API key
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except (PermissionError, IOError):
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Preserve current API key
            current_api_key = self.get_api_key()
            imported_config["api_key"] = current_api_key
            
            self.config_data = imported_config
            return self._save_config(self.config_data)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            return False


# Global config instance
config = ConfigManager()
