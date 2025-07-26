"""
KiCat AI Assistant UI Components
PyQt-based interface for the AI assistant panel
"""

import sys
import os
from typing import Optional, List, Dict, Any

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea,
        QFrame, QSplitter, QDialog, QFormLayout, QComboBox,
        QCheckBox, QSpinBox, QMessageBox, QFileDialog, QTabWidget,
        QGroupBox, QGridLayout, QProgressBar, QSystemTrayIcon
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
    from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor, QPalette
    
    PYQT_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea,
            QFrame, QSplitter, QDialog, QFormLayout, QComboBox,
            QCheckBox, QSpinBox, QMessageBox, QFileDialog, QTabWidget,
            QGroupBox, QGridLayout, QProgressBar, QSystemTrayIcon
        )
        from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
        from PyQt6.QtGui import QFont, QPixmap, QIcon, QTextCursor, QPalette
        
        PYQT_AVAILABLE = True
    except ImportError:
        PYQT_AVAILABLE = False
        print("PyQt5 or PyQt6 not available. UI will not work.")

if PYQT_AVAILABLE:
    from .config import config
    from .AI_API import AIAPIClient
    from .enhanced_parser import enhanced_parser
    from .permissions import permission_manager, modification_logger, ModificationRisk


class ChatMessage:
    """Represents a single chat message"""
    
    def __init__(self, content: str, is_user: bool = True, timestamp: str = None):
        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or self._get_timestamp()
    
    @staticmethod
    def _get_timestamp() -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


class APITestThread(QThread):
    """Thread for testing API connection without blocking UI"""
    
    result_ready = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
    
    def run(self):
        try:
            success, message = self.client.test_connection()
            self.result_ready.emit(success, message)
        except Exception as e:
            self.result_ready.emit(False, f"Test failed: {str(e)}")


class ChatThread(QThread):
    """Thread for handling AI API calls without blocking UI"""
    
    response_ready = pyqtSignal(str)  # AI response
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self, client, message: str, context: str = "", parent=None):
        super().__init__(parent)
        self.client = client
        self.message = message
        self.context = context
    
    def run(self):
        try:
            response = self.client.send_message(self.message, self.context)
            if response:
                self.response_ready.emit(response)
            else:
                self.error_occurred.emit("No response received from API")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")


class PermissionDialog(QDialog):
    """Dialog for requesting user permission for design modifications"""
    
    def __init__(self, description: str, risk: ModificationRisk, details: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("KiCat AI - Permission Required")
        self.setModal(True)
        self.setFixedSize(500, 350)
        
        self.description = description
        self.risk = risk
        self.details = details
        self.approved = False
        self.remember_choice = False
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🤖 KiCat AI Permission Request")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Main content
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Box)
        content_layout = QVBoxLayout(content_frame)
        
        # Description
        desc_label = QLabel(f"<b>Proposed Change:</b><br>{self.description}")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        # Risk level
        risk_colors = {
            ModificationRisk.SAFE: ("🟢", "green"),
            ModificationRisk.LOW: ("🟡", "orange"), 
            ModificationRisk.MEDIUM: ("🟠", "darkorange"),
            ModificationRisk.HIGH: ("🔴", "red"),
            ModificationRisk.CRITICAL: ("⚠️", "darkred")
        }
        
        risk_icon, risk_color = risk_colors.get(self.risk, ("❓", "black"))
        risk_text = self.risk.value.replace('_', ' ').title()
        
        risk_label = QLabel(f"<b>Risk Level:</b> {risk_icon} <span style='color: {risk_color}'>{risk_text}</span>")
        content_layout.addWidget(risk_label)
        
        # Details
        if self.details:
            details_label = QLabel(f"<b>Details:</b><br>{self.details}")
            details_label.setWordWrap(True)
            content_layout.addWidget(details_label)
        
        layout.addWidget(content_frame)
        
        # Safety notice
        safety_label = QLabel("ℹ️ <i>You can undo this change if needed</i>")
        safety_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(safety_label)
        
        # Remember choice checkbox
        self.remember_check = QCheckBox("Remember this choice for similar modifications")
        layout.addWidget(self.remember_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        proceed_btn = QPushButton("✅ Proceed")
        proceed_btn.clicked.connect(self.accept)
        proceed_btn.setDefault(True)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(proceed_btn)
        
        layout.addLayout(button_layout)
    
    def accept(self):
        self.approved = True
        self.remember_choice = self.remember_check.isChecked()
        super().accept()


class MemoryPanel(QWidget):
    """Panel showing conversation memory and design decisions"""
    
    def __init__(self, ai_client: AIAPIClient, parent=None):
        super().__init__(parent)
        self.ai_client = ai_client
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Memory header
        header = QLabel("🧠 Memory & Context")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)
        
        # Memory display
        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        self.memory_display.setMaximumHeight(150)
        self.memory_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.memory_display)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_memory)
        
        clear_btn = QPushButton("🗑️ Clear Memory")
        clear_btn.clicked.connect(self.clear_memory)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Initial refresh
        self.refresh_memory()
    
    def refresh_memory(self):
        """Refresh the memory display"""
        try:
            summary = self.ai_client.get_conversation_summary()
            session_log = modification_logger.get_session_summary()
            
            content = f"=== Conversation Summary ===\n{summary}\n\n"
            content += f"=== Modification Log ===\n{session_log}"
            
            self.memory_display.setPlainText(content)
        except Exception as e:
            self.memory_display.setPlainText(f"Error loading memory: {e}")
    
    def clear_memory(self):
        """Clear AI memory after confirmation"""
        reply = QMessageBox.question(
            self, "Clear Memory",
            "This will clear the AI's conversation memory and design decisions.\n\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.ai_client.clear_all()
            modification_logger.log_entries.clear()
            self.refresh_memory()
            QMessageBox.information(self, "Memory Cleared", "AI memory has been cleared successfully.")


class SettingsDialog(QDialog):
    """Settings dialog for API configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KiCat AI Assistant Settings")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        
        # API Settings Tab
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        
        # API Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["claude", "openai", "custom"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        api_layout.addRow("API Provider:", self.provider_combo)
        
        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addRow("API Key:", self.api_key_input)
        
        # Model selection
        self.model_combo = QComboBox()
        api_layout.addRow("Model:", self.model_combo)
        
        # API Base URL
        self.base_url_input = QLineEdit()
        api_layout.addRow("Base URL:", self.base_url_input)
        
        # Test API button
        self.test_button = QPushButton("Test API Connection")
        self.test_button.clicked.connect(self.test_api_connection)
        api_layout.addRow("", self.test_button)
        
        # Status label
        self.status_label = QLabel("")
        api_layout.addRow("Status:", self.status_label)
        
        tabs.addTab(api_tab, "API Settings")
        
        # Advanced Settings Tab
        advanced_tab = QWidget()
        advanced_layout = QFormLayout(advanced_tab)
        
        # Max tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8192)
        self.max_tokens_spin.setValue(4096)
        advanced_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        # Temperature
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 100)
        self.temperature_spin.setValue(30)
        self.temperature_spin.setSuffix("%")
        advanced_layout.addRow("Temperature:", self.temperature_spin)
        
        # Chat history limit
        self.history_limit_spin = QSpinBox()
        self.history_limit_spin.setRange(10, 200)
        self.history_limit_spin.setValue(50)
        advanced_layout.addRow("Chat History Limit:", self.history_limit_spin)
        
        # Auto-detect context
        self.auto_context_check = QCheckBox("Automatically detect PCB/Schematic context")
        self.auto_context_check.setChecked(True)
        advanced_layout.addRow("", self.auto_context_check)
        
        # Include DRC errors
        self.include_drc_check = QCheckBox("Include DRC errors in context")
        self.include_drc_check.setChecked(True)
        advanced_layout.addRow("", self.include_drc_check)
        
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def on_provider_changed(self, provider: str):
        """Update model list when provider changes"""
        models = config.get_available_models().get(provider, [])
        self.model_combo.clear()
        self.model_combo.addItems(models)
        
        # Update base URL
        if provider == "claude":
            self.base_url_input.setText("https://api.anthropic.com")
        elif provider == "openai":
            self.base_url_input.setText("https://api.openai.com")
        elif provider == "custom":
            self.base_url_input.setText("https://api.custom-provider.com")
    
    def load_settings(self):
        """Load current settings into the dialog"""
        self.provider_combo.setCurrentText(config.get_api_provider())
        self.api_key_input.setText(config.get_api_key())
        self.model_combo.setCurrentText(config.get_model())
        self.base_url_input.setText(config.get_api_base_url())
        self.max_tokens_spin.setValue(config.get("max_tokens", 4096))
        self.temperature_spin.setValue(int(config.get("temperature", 0.3) * 100))
        self.history_limit_spin.setValue(config.get("chat_history_limit", 50))
        self.auto_context_check.setChecked(config.get("auto_detect_context", True))
        self.include_drc_check.setChecked(config.get("include_drc_errors", True))
    
    def save_settings(self):
        """Save settings and close dialog"""
        config.set_api_provider(self.provider_combo.currentText())
        config.set_api_key(self.api_key_input.text())
        config.set_model(self.model_combo.currentText())
        config.set("api_base_url", self.base_url_input.text())
        config.set("max_tokens", self.max_tokens_spin.value())
        config.set("temperature", self.temperature_spin.value() / 100.0)
        config.set("chat_history_limit", self.history_limit_spin.value())
        config.set("auto_detect_context", self.auto_context_check.isChecked())
        config.set("include_drc_errors", self.include_drc_check.isChecked())
        
        self.accept()
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            config.reset_to_defaults()
            self.load_settings()
    
    def test_api_connection(self):
        """Test the API connection"""
        self.test_button.setEnabled(False)
        self.status_label.setText("Testing connection...")
        
        # Create temporary client with current settings
        temp_config = {
            "api_key": self.api_key_input.text(),
            "api_provider": self.provider_combo.currentText(),
            "model": self.model_combo.currentText(),
            "api_base_url": self.base_url_input.text()
        }
        
        client = AIAPIClient(temp_config)
        
        # Start test thread
        self.test_thread = APITestThread(client, self)
        self.test_thread.result_ready.connect(self.on_test_result)
        self.test_thread.start()
    
    def on_test_result(self, success: bool, message: str):
        """Handle API test result"""
        self.test_button.setEnabled(True)
        
        if success:
            self.status_label.setText("✓ Connection successful")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText(f"✗ {message}")
            self.status_label.setStyleSheet("color: red;")


class SmartCatAssistantWindow(QMainWindow):
    """Main assistant window"""
    
    window_closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("KiCat AI Assistant")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # Initialize components
        self.ai_client = AIAPIClient()
        self.context_parser = enhanced_parser
        self.chat_history: List[ChatMessage] = []
        
        # Set up UI
        self.setup_ui()
        self.load_geometry()
        
        # Check initial configuration
        self.check_configuration()
    
    def setup_ui(self):
        """Set up the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("KiCat AI Assistant")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Context button
        context_button = QPushButton("📊")
        context_button.setFixedSize(30, 30)
        context_button.setToolTip("Refresh Design Context")
        context_button.clicked.connect(self.refresh_context)
        header_layout.addWidget(context_button)
        
        # Settings button
        settings_button = QPushButton("⚙")
        settings_button.setFixedSize(30, 30)
        settings_button.setToolTip("Settings")
        settings_button.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_button)
        
        main_layout.addLayout(header_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Vertical)
        
        # Chat area (top part)
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Consolas", 10))
        chat_layout.addWidget(self.chat_area)
        
        splitter.addWidget(chat_widget)
        
        # Memory panel (bottom part)
        self.memory_panel = MemoryPanel(self.ai_client)
        splitter.addWidget(self.memory_panel)
        
        # Set splitter proportions (80% chat, 20% memory)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about your PCB design or request modifications...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        # Status bar
        self.status_label = QLabel("Ready - Enhanced AI with read/write access")
        main_layout.addWidget(self.status_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def load_geometry(self):
        """Load window geometry from config"""
        geometry = config.get_window_geometry()
        self.setGeometry(
            geometry["x"], geometry["y"],
            geometry["width"], geometry["height"]
        )
    
    def save_geometry(self):
        """Save current window geometry"""
        rect = self.geometry()
        config.set_window_geometry(rect.width(), rect.height(), rect.x(), rect.y())
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_geometry()
        self.window_closed.emit()
        event.accept()
    
    def check_configuration(self):
        """Check if the assistant is properly configured"""
        if not config.is_configured():
            self.show_welcome_message()
        else:
            self.show_ready_message()
    
    def show_welcome_message(self):
        """Show welcome message for first-time users"""
        welcome_text = """
<div style='background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin: 5px;'>
<h3>🚀 Welcome to KiCat AI Assistant!</h3>
<p><strong>Enhanced with Read/Write Access & Memory</strong></p>

<h4>🔧 Setup Required:</h4>
<ol>
<li>Click the settings button (⚙) in the top right</li>
<li>Enter your Claude or OpenAI API key</li>
<li>Select your preferred model</li>
<li>Click "Test API Connection" to verify</li>
<li>Save your settings</li>
</ol>

<h4>🧠 New Capabilities:</h4>
<ul>
<li><strong>Deep PCB Analysis:</strong> Comprehensive design review including signal integrity, power distribution, thermal management</li>
<li><strong>Design Modifications:</strong> I can make changes to your design (with your permission)</li>
<li><strong>Memory:</strong> I remember our conversation and previous design decisions</li>
<li><strong>Manufacturing Expertise:</strong> DFM analysis, assembly considerations, and cost optimization</li>
<li><strong>Safety Features:</strong> All changes require approval and can be undone</li>
</ul>

<p>Once configured, I can help you create better PCB designs with intelligent analysis and safe modifications!</p>
</div>
        """
        self.chat_area.setHtml(welcome_text)
        self.status_label.setText("Configuration required - Enhanced AI ready")
        self.status_label.setStyleSheet("color: orange;")
    
    def show_ready_message(self):
        """Show ready message when configured"""
        ready_text = """
<div style='background-color: #f0fff0; padding: 15px; border-radius: 8px; margin: 5px;'>
<h3>🤖 KiCat AI Assistant Ready!</h3>
<p><strong>Enhanced AI with Read/Write Access & Memory</strong></p>

<h4>🔍 I can analyze:</h4>
<ul>
<li><strong>Components:</strong> Placement, selection, thermal considerations</li>
<li><strong>Signal Integrity:</strong> Trace routing, impedance, crosstalk, EMI</li>
<li><strong>Power Distribution:</strong> PDN analysis, decoupling, voltage regulation</li>
<li><strong>Manufacturing:</strong> DFM, assembly, cost optimization</li>
<li><strong>Footprints & Libraries:</strong> Usage analysis and recommendations</li>
</ul>

<h4>⚡ I can modify your design:</h4>
<ul>
<li>Component placement and routing optimization</li>
<li>Design rule adjustments</li>
<li>Layer stackup improvements</li>
<li>All changes require your permission</li>
<li>Full undo capability</li>
</ul>

<h4>🧠 Memory Features:</h4>
<ul>
<li>Remember our conversation and design decisions</li>
<li>Track modification history</li>
<li>Learn your preferences over time</li>
</ul>

<p><strong>Try asking:</strong> "Analyze my PCB design comprehensively" or "How can I improve signal integrity?"</p>
</div>
        """
        self.chat_area.setHtml(ready_text)
        self.status_label.setText("Ready - Enhanced AI with read/write access")
        self.status_label.setStyleSheet("color: green;")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Reinitialize client with new settings
            self.ai_client = AIAPIClient()
            self.check_configuration()
    
    def refresh_context(self):
        """Manually refresh the design context"""
        try:
            self.show_progress("Analyzing design context...")
            
            # Get comprehensive context
            context = self.context_parser.get_comprehensive_context()
            
            # Show context summary in chat
            summary_msg = ChatMessage(
                f"📊 **Design Context Refreshed**\n\n{context[:500]}...\n\n*Full context provided to AI*", 
                is_user=False
            )
            self.add_message_to_chat(summary_msg)
            
            self.hide_progress()
            self.status_label.setText("Context refreshed")
            self.status_label.setStyleSheet("color: green;")
            
        except Exception as e:
            self.hide_progress()
            error_msg = ChatMessage(f"Error refreshing context: {str(e)}", is_user=False)
            self.add_message_to_chat(error_msg)
            self.status_label.setText("Context refresh failed")
            self.status_label.setStyleSheet("color: red;")
    
    def send_message(self):
        """Send user message to AI with enhanced context and permission handling"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        if not config.is_configured():
            QMessageBox.warning(
                self, "Configuration Required",
                "Please configure your API key in settings first."
            )
            return
        
        # Clear input
        self.input_field.clear()
        
        # Add user message to chat
        user_msg = ChatMessage(message, is_user=True)
        self.add_message_to_chat(user_msg)
        
        # Get comprehensive context if auto-detect is enabled
        context = ""
        if config.get("auto_detect_context", True):
            try:
                context = self.context_parser.get_comprehensive_context()
            except Exception as e:
                context = f"Error getting context: {str(e)}"
        
        # Check if this might be a modification request
        modification_keywords = ['change', 'modify', 'move', 'rotate', 'delete', 'add', 'place', 
                               'route', 'connect', 'fix', 'improve', 'update', 'replace']
        
        is_modification_request = any(keyword in message.lower() for keyword in modification_keywords)
        
        if is_modification_request:
            # Add permission notice
            permission_notice = ChatMessage(
                "🛡️ **Permission System Active**: I'll ask for your approval before making any changes to your design.",
                is_user=False
            )
            self.add_message_to_chat(permission_notice)
        
        # Show progress
        self.show_progress("Analyzing design and generating response...")
        
        # Start chat thread
        self.chat_thread = ChatThread(self.ai_client, message, context, self)
        self.chat_thread.response_ready.connect(self.on_response_received)
        self.chat_thread.error_occurred.connect(self.on_error_occurred)
        self.chat_thread.start()
    
    def on_response_received(self, response: str):
        """Handle AI response with permission checking"""
        self.hide_progress()
        
        # Check if the response contains modification suggestions
        if self._contains_modification_suggestions(response):
            # Add disclaimer about permissions
            enhanced_response = response + "\n\n" + permission_manager.generate_safety_summary()
            
            # Add assistant message to chat
            assistant_msg = ChatMessage(enhanced_response, is_user=False)
            self.add_message_to_chat(assistant_msg)
        else:
            # Regular response
            assistant_msg = ChatMessage(response, is_user=False)
            self.add_message_to_chat(assistant_msg)
        
        # Refresh memory panel
        self.memory_panel.refresh_memory()
        
        self.status_label.setText("Ready - Enhanced AI with read/write access")
        self.status_label.setStyleSheet("color: green;")
    
    def _contains_modification_suggestions(self, response: str) -> bool:
        """Check if response contains modification suggestions"""
        modification_indicators = [
            'i can help you', 'let me', 'i would', 'i suggest changing',
            'modify', 'change', 'move', 'rotate', 'adjust', 'improve',
            'would you like me to', 'shall i', 'permission to'
        ]
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in modification_indicators)
    
    def add_message_to_chat(self, message: ChatMessage):
        """Add a message to the chat display"""
        self.chat_history.append(message)
        
        # Limit chat history
        max_history = config.get("chat_history_limit", 50)
        if len(self.chat_history) > max_history:
            self.chat_history = self.chat_history[-max_history:]
        
        # Format message
        if message.is_user:
            msg_html = f"""
            <div style='background-color: #e6f3ff; padding: 8px; margin: 5px; border-radius: 5px; border-left: 3px solid #2196f3;'>
            <strong>You ({message.timestamp}):</strong><br>
            {self.format_text(message.content)}
            </div>
            """
        else:
            msg_html = f"""
            <div style='background-color: #f0f8f0; padding: 8px; margin: 5px; border-radius: 5px; border-left: 3px solid #4caf50;'>
            <strong>KiCat AI ({message.timestamp}):</strong><br>
            {self.format_text(message.content)}
            </div>
            """
        
        # Append to chat area
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(msg_html)
        
        # Scroll to bottom
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def format_text(self, text: str) -> str:
        """Format text for HTML display"""
        # Convert newlines to <br>
        text = text.replace('\n', '<br>')
        
        # Simple markdown-like formatting
        text = text.replace('**', '<strong>').replace('**', '</strong>')
        text = text.replace('*', '<em>').replace('*', '</em>')
        
        return text
    
    def on_response_received(self, response: str):
        """Handle AI response with permission checking"""
        self.hide_progress()
        
        # Check if the response contains modification suggestions
        if self._contains_modification_suggestions(response):
            # Add disclaimer about permissions
            enhanced_response = response + "\n\n" + permission_manager.generate_safety_summary()
            
            # Add assistant message to chat
            assistant_msg = ChatMessage(enhanced_response, is_user=False)
            self.add_message_to_chat(assistant_msg)
        else:
            # Regular response
            assistant_msg = ChatMessage(response, is_user=False)
            self.add_message_to_chat(assistant_msg)
        
        # Refresh memory panel
        self.memory_panel.refresh_memory()
        
        self.status_label.setText("Ready - Enhanced AI with read/write access")
        self.status_label.setStyleSheet("color: green;")
    
    def on_error_occurred(self, error: str):
        """Handle error from AI API"""
        self.hide_progress()
        
        error_msg = ChatMessage(f"Error: {error}", is_user=False)
        self.add_message_to_chat(error_msg)
        
        self.status_label.setText("Error occurred")
        self.status_label.setStyleSheet("color: red;")
    
    def show_progress(self, message: str):
        """Show progress indicator"""
        self.status_label.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)


# Ensure QApplication exists
def ensure_qt_application():
    """Ensure QApplication instance exists"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
        return app
    return QApplication.instance()


if __name__ == "__main__" and PYQT_AVAILABLE:
    # For testing the UI outside of KiCad
    app = ensure_qt_application()
    window = SmartCatAssistantWindow()
    window.show()
    sys.exit(app.exec_())
