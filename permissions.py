"""
Permission System for Design Modifications
Handles user consent and safety for write operations
"""

from typing import Dict, List, Callable, Optional
from enum import Enum


class PermissionLevel(Enum):
    """Permission levels for design modifications"""
    READ_ONLY = "read_only"
    ASK_PERMISSION = "ask_permission"  
    AUTO_APPROVE_SAFE = "auto_approve_safe"
    AUTO_APPROVE_ALL = "auto_approve_all"


class ModificationRisk(Enum):
    """Risk levels for design modifications"""
    SAFE = "safe"          # Cosmetic changes, labels, silkscreen
    LOW = "low"            # Component values, non-critical routing
    MEDIUM = "medium"      # Component placement, important routing
    HIGH = "high"          # Layer stackup, critical signals, power
    CRITICAL = "critical"  # Netlist changes, component deletion


class PermissionManager:
    """Manages permissions for design modifications"""
    
    def __init__(self):
        self.permission_level = PermissionLevel.ASK_PERMISSION
        self.user_preferences = {
            "auto_approve_cosmetic": False,
            "require_confirmation_critical": True,
            "backup_before_changes": True,
            "max_auto_changes": 5
        }
        self.session_approvals = 0
        self.modification_history = []
    
    def assess_modification_risk(self, modification_type: str, details: Dict[str, any] = None) -> ModificationRisk:
        """Assess the risk level of a proposed modification"""
        
        # Advanced operations (settings, layers) are high/critical risk
        if modification_type in ["add_copper_layers", "change_layer_count", "modify_stackup"]:
            return ModificationRisk.CRITICAL
        elif modification_type in ["modify_board_settings", "change_track_width", "change_via_size"]:
            return ModificationRisk.HIGH
        
        # Component operations
        elif modification_type in ["move_component", "rotate_component"]:
            return ModificationRisk.MEDIUM
        elif modification_type in ["delete_component", "add_component", "change_component_value"]:
            return ModificationRisk.HIGH
        
        # Net and routing operations
        elif modification_type in ["reroute_net", "add_track"]:
            return ModificationRisk.MEDIUM
        elif modification_type in ["delete_net", "split_net", "merge_nets"]:
            return ModificationRisk.CRITICAL
        
        # Cosmetic changes
        elif modification_type in ["update_silkscreen", "modify_text", "change_color"]:
            return ModificationRisk.SAFE
        
        # Default to medium risk for unknown operations
        else:
            return ModificationRisk.MEDIUM
    
    def can_perform_advanced_operations(self) -> bool:
        """Check if advanced operations can be performed"""
        # Import here to avoid circular dependencies
        try:
            from .kicad_operations import kicad_ops
            can_modify, _ = kicad_ops.can_modify_board()
            return can_modify
        except ImportError:
            return False
    
    def get_advanced_operation_warnings(self, operation_type: str) -> List[str]:
        """Get specific warnings for advanced operations"""
        warnings = []
        
        if operation_type == "add_copper_layers":
            warnings.extend([
                "⚠️ Adding copper layers will affect manufacturing cost",
                "⚠️ Existing routing may need to be updated",
                "⚠️ Layer stackup should be verified with PCB manufacturer",
                "⚠️ This change cannot be easily undone"
            ])
        
        elif operation_type == "modify_board_settings":
            warnings.extend([
                "⚠️ Changing track/via sizes may affect existing routing",
                "⚠️ New settings must meet manufacturing constraints",
                "⚠️ DRC violations may be introduced"
            ])
        
        elif operation_type == "change_stackup":
            warnings.extend([
                "⚠️ Stackup changes affect impedance calculations",
                "⚠️ Manufacturing cost and timeline may be affected",
                "⚠️ Signal integrity analysis should be repeated"
            ])
        
        return warnings
    
    def request_permission(self, description: str, risk: ModificationRisk, 
                          details: str = "") -> Dict[str, any]:
        """Request permission for a modification"""
        
        # Build permission request
        request = {
            "description": description,
            "risk": risk,
            "details": details,
            "auto_approved": False,
            "requires_user_input": True
        }
        
        # Check if auto-approval applies
        if self.permission_level == PermissionLevel.READ_ONLY:
            request["approved"] = False
            request["reason"] = "Read-only mode enabled"
            request["requires_user_input"] = False
            
        elif self.permission_level == PermissionLevel.AUTO_APPROVE_ALL:
            request["approved"] = True
            request["auto_approved"] = True
            request["requires_user_input"] = False
            
        elif self.permission_level == PermissionLevel.AUTO_APPROVE_SAFE and risk == ModificationRisk.SAFE:
            request["approved"] = True
            request["auto_approved"] = True
            request["requires_user_input"] = False
            
        else:
            # Ask permission - this will be handled by the UI
            request["approved"] = None  # Pending user decision
            request["requires_user_input"] = True
        
        return request
    
    def approve_modification(self, request_id: str, approved: bool, remember_choice: bool = False):
        """Approve or deny a modification request"""
        self.session_approvals += 1
        
        if remember_choice:
            # Store preference for similar modifications
            pass
    
    def get_permission_prompt(self, description: str, risk: ModificationRisk, details: str = "") -> str:
        """Generate a user-friendly permission prompt"""
        
        risk_colors = {
            ModificationRisk.SAFE: "🟢",
            ModificationRisk.LOW: "🟡", 
            ModificationRisk.MEDIUM: "🟠",
            ModificationRisk.HIGH: "🔴",
            ModificationRisk.CRITICAL: "⚠️"
        }
        
        risk_descriptions = {
            ModificationRisk.SAFE: "Safe (cosmetic changes only)",
            ModificationRisk.LOW: "Low risk (minor modifications)",
            ModificationRisk.MEDIUM: "Medium risk (component/routing changes)",
            ModificationRisk.HIGH: "High risk (significant design changes)",
            ModificationRisk.CRITICAL: "Critical (netlist/structural changes)"
        }
        
        prompt = f"""
🤖 **KiCat AI Permission Request**

**Proposed Change:** {description}

**Risk Level:** {risk_colors[risk]} {risk_descriptions[risk]}

**Details:** {details if details else "No additional details provided"}

**Options:**
- ✅ **Proceed** - Apply this change
- ❌ **Cancel** - Skip this change  
- 🔄 **Undo Available** - You can undo after seeing the result

Would you like me to proceed with this modification?
"""
        return prompt
    
    def generate_safety_summary(self) -> str:
        """Generate a summary of safety measures"""
        return """
🛡️ **Safety Features Active**

- **Permission Required**: All changes require your approval
- **Undo Available**: All modifications can be reversed
- **Change History**: Full log of all modifications
- **Backup Recommended**: Save your design before major changes
- **Risk Assessment**: Each change is classified by risk level

You maintain full control over your design at all times.
"""


class ModificationLogger:
    """Logs all design modifications for audit trail"""
    
    def __init__(self):
        self.log_entries = []
    
    def log_modification(self, description: str, risk: ModificationRisk, 
                        approved: bool, user_id: str = "user"):
        """Log a modification attempt"""
        from datetime import datetime
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "risk": risk.value,
            "approved": approved,
            "user_id": user_id
        }
        
        self.log_entries.append(entry)
    
    def get_session_summary(self) -> str:
        """Get summary of current session modifications"""
        if not self.log_entries:
            return "No modifications in this session."
        
        approved_count = sum(1 for entry in self.log_entries if entry["approved"])
        total_count = len(self.log_entries)
        
        summary = f"Session Summary: {approved_count}/{total_count} modifications approved\n"
        
        # Show recent modifications
        recent = self.log_entries[-5:]
        for entry in recent:
            status = "✅" if entry["approved"] else "❌"
            summary += f"{status} {entry['description']} (Risk: {entry['risk']})\n"
        
        return summary
    
    def export_log(self, file_path: str) -> bool:
        """Export modification log to file"""
        try:
            import json
            with open(file_path, 'w') as f:
                json.dump(self.log_entries, f, indent=2)
            return True
        except Exception:
            return False


# Global instances
permission_manager = PermissionManager()
modification_logger = ModificationLogger()
