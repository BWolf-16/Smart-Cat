"""
KiCad Advanced Operations Module
Handles board settings, layer management, preferences, and advanced modifications
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path

try:
    import pcbnew
    PCBNEW_AVAILABLE = True
except ImportError:
    PCBNEW_AVAILABLE = False
    print("pcbnew module not available - advanced operations will be limited")


class KiCadOperations:
    """Advanced KiCad operations including settings, preferences, and layer management"""
    
    def __init__(self):
        self.backup_settings = {}
        self.operation_history = []
    
    def can_modify_board(self) -> Tuple[bool, str]:
        """Check if board modifications are possible"""
        if not PCBNEW_AVAILABLE:
            return False, "KiCad pcbnew module not available"
        
        board = pcbnew.GetBoard()
        if not board:
            return False, "No active board found"
        
        # Check if board is saved (modifications need saved file)
        board_file = board.GetFileName()
        if not board_file:
            return False, "Board must be saved before modifications"
        
        return True, "Board ready for modifications"
    
    def backup_current_settings(self) -> bool:
        """Backup current board settings before modifications"""
        try:
            board = pcbnew.GetBoard()
            if not board:
                return False
            
            design_settings = board.GetDesignSettings()
            
            self.backup_settings = {
                'layer_count': board.GetCopperLayerCount(),
                'track_width': design_settings.GetCurrentTrackWidth(),
                'via_size': design_settings.GetCurrentViaSize(),
                'via_drill': design_settings.GetCurrentViaDrill(),
                'min_track_width': design_settings.m_TrackMinWidth,
                'min_via_size': design_settings.m_ViasMinSize,
                'min_via_drill': design_settings.m_ViasMinDrill,
                'enabled_layers': [layer for layer in range(pcbnew.PCB_LAYER_ID_COUNT) 
                                 if board.IsLayerEnabled(layer)]
            }
            
            return True
            
        except Exception as e:
            print(f"Error backing up settings: {e}")
            return False
    
    def restore_settings(self) -> bool:
        """Restore previously backed up settings"""
        try:
            if not self.backup_settings:
                return False
            
            board = pcbnew.GetBoard()
            if not board:
                return False
            
            design_settings = board.GetDesignSettings()
            
            # Restore basic settings
            design_settings.SetCurrentTrackWidth(self.backup_settings['track_width'])
            design_settings.SetCurrentViaSize(self.backup_settings['via_size'])
            design_settings.SetCurrentViaDrill(self.backup_settings['via_drill'])
            
            # Note: Layer count changes require more complex operations
            # and may not be directly reversible
            
            return True
            
        except Exception as e:
            print(f"Error restoring settings: {e}")
            return False
    
    def get_current_layer_info(self) -> Dict[str, Any]:
        """Get comprehensive information about current layer setup"""
        try:
            board = pcbnew.GetBoard()
            if not board:
                return {"error": "No active board"}
            
            layer_info = {
                "copper_layers": board.GetCopperLayerCount(),
                "total_layers": 0,
                "enabled_layers": [],
                "layer_names": {},
                "stackup_info": {}
            }
            
            # Get all enabled layers
            for layer_id in range(pcbnew.PCB_LAYER_ID_COUNT):
                if board.IsLayerEnabled(layer_id):
                    layer_info["total_layers"] += 1
                    layer_name = board.GetLayerName(layer_id)
                    layer_info["enabled_layers"].append({
                        "id": layer_id, 
                        "name": layer_name,
                        "type": self._get_layer_type(layer_id)
                    })
                    layer_info["layer_names"][layer_id] = layer_name
            
            return layer_info
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_layer_type(self, layer_id: int) -> str:
        """Get the type of layer based on layer ID"""
        # KiCad layer types
        if layer_id in [pcbnew.F_Cu, pcbnew.B_Cu]:
            return "copper_outer"
        elif layer_id in range(pcbnew.In1_Cu, pcbnew.In30_Cu + 1):
            return "copper_inner"
        elif layer_id in [pcbnew.F_SilkS, pcbnew.B_SilkS]:
            return "silkscreen"
        elif layer_id in [pcbnew.F_Mask, pcbnew.B_Mask]:
            return "solder_mask"
        elif layer_id in [pcbnew.F_Paste, pcbnew.B_Paste]:
            return "solder_paste"
        elif layer_id == pcbnew.Edge_Cuts:
            return "board_edge"
        elif layer_id in [pcbnew.F_Fab, pcbnew.B_Fab]:
            return "fabrication"
        elif layer_id in [pcbnew.Dwgs_User, pcbnew.Cmts_User]:
            return "user"
        else:
            return "technical"
    
    def can_add_copper_layers(self, target_count: int) -> Tuple[bool, str]:
        """Check if copper layers can be added to reach target count"""
        try:
            board = pcbnew.GetBoard()
            if not board:
                return False, "No active board"
            
            current_count = board.GetCopperLayerCount()
            
            if target_count <= current_count:
                return False, f"Board already has {current_count} copper layers (requested: {target_count})"
            
            if target_count > 30:  # KiCad limitation
                return False, "KiCad supports maximum 30 copper layers"
            
            if target_count % 2 != 0 and target_count > 2:
                return False, "Multilayer boards typically use even number of layers for manufacturing"
            
            return True, f"Can add {target_count - current_count} copper layers"
            
        except Exception as e:
            return False, str(e)
    
    def add_copper_layers(self, target_count: int) -> Tuple[bool, str]:
        """Add copper layers to reach the target count"""
        try:
            can_add, message = self.can_add_copper_layers(target_count)
            if not can_add:
                return False, message
            
            board = pcbnew.GetBoard()
            current_count = board.GetCopperLayerCount()
            layers_to_add = target_count - current_count
            
            # Backup current settings first
            if not self.backup_current_settings():
                return False, "Failed to backup current settings"
            
            # Enable the required inner layers
            layer_ids_to_enable = []
            
            # KiCad inner layers start from In1_Cu
            inner_layer_start = pcbnew.In1_Cu
            for i in range(layers_to_add):
                layer_id = inner_layer_start + i
                if layer_id <= pcbnew.In30_Cu:  # Maximum inner layers
                    layer_ids_to_enable.append(layer_id)
                    # Enable the layer
                    board.SetEnabledLayers(board.GetEnabledLayers().set(layer_id))
                    
                    # Set default layer name
                    layer_name = f"In{i+1}.Cu"
                    board.SetLayerName(layer_id, layer_name)
            
            # Update copper layer count
            board.SetCopperLayerCount(target_count)
            
            # Record the operation
            operation = {
                "type": "add_copper_layers",
                "from_count": current_count,
                "to_count": target_count,
                "added_layers": layer_ids_to_enable,
                "timestamp": self._get_timestamp()
            }
            self.operation_history.append(operation)
            
            # Refresh the board
            pcbnew.Refresh()
            
            return True, f"Successfully added {layers_to_add} copper layers (now {target_count} total)"
            
        except Exception as e:
            return False, f"Error adding copper layers: {str(e)}"
    
    def modify_board_settings(self, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Modify various board settings"""
        try:
            board = pcbnew.GetBoard()
            if not board:
                return False, "No active board"
            
            design_settings = board.GetDesignSettings()
            changes_made = []
            
            # Backup current settings
            if not self.backup_current_settings():
                return False, "Failed to backup current settings"
            
            # Track width settings
            if 'track_width' in settings:
                width_mm = settings['track_width']
                width_internal = pcbnew.FromMM(width_mm)
                design_settings.SetCurrentTrackWidth(width_internal)
                changes_made.append(f"Track width: {width_mm}mm")
            
            if 'min_track_width' in settings:
                min_width_mm = settings['min_track_width']
                min_width_internal = pcbnew.FromMM(min_width_mm)
                design_settings.m_TrackMinWidth = min_width_internal
                changes_made.append(f"Min track width: {min_width_mm}mm")
            
            # Via settings
            if 'via_size' in settings:
                via_size_mm = settings['via_size']
                via_size_internal = pcbnew.FromMM(via_size_mm)
                design_settings.SetCurrentViaSize(via_size_internal)
                changes_made.append(f"Via size: {via_size_mm}mm")
            
            if 'via_drill' in settings:
                drill_mm = settings['via_drill']
                drill_internal = pcbnew.FromMM(drill_mm)
                design_settings.SetCurrentViaDrill(drill_internal)
                changes_made.append(f"Via drill: {drill_mm}mm")
            
            # Clearance settings (if supported)
            if 'clearance' in settings:
                clearance_mm = settings['clearance']
                clearance_internal = pcbnew.FromMM(clearance_mm)
                # Note: Clearance setting may vary by KiCad version
                try:
                    design_settings.m_TrackClearance = clearance_internal
                    changes_made.append(f"Track clearance: {clearance_mm}mm")
                except AttributeError:
                    changes_made.append("Clearance setting not available in this KiCad version")
            
            # Record the operation
            operation = {
                "type": "modify_board_settings",
                "settings": settings,
                "changes": changes_made,
                "timestamp": self._get_timestamp()
            }
            self.operation_history.append(operation)
            
            # Refresh the board
            pcbnew.Refresh()
            
            return True, f"Settings modified: {', '.join(changes_made)}"
            
        except Exception as e:
            return False, f"Error modifying board settings: {str(e)}"
    
    def get_design_rule_violations(self) -> Dict[str, Any]:
        """Get current design rule check violations"""
        try:
            # Note: DRC access might be limited in some KiCad versions
            # This is a basic implementation
            return {
                "drc_available": False,
                "message": "DRC integration requires additional KiCad API access",
                "suggestion": "Run DRC manually in KiCad: Inspect > Design Rules Checker"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def suggest_layer_stackup(self, target_layers: int) -> Dict[str, Any]:
        """Suggest optimal layer stackup for given layer count"""
        stackup_suggestions = {
            2: {
                "description": "Standard 2-layer PCB",
                "layers": ["Top Copper", "Bottom Copper"],
                "typical_thickness": "1.6mm",
                "applications": "Simple circuits, low-speed digital, analog",
                "cost": "Low"
            },
            4: {
                "description": "Standard 4-layer PCB",
                "layers": ["Top Copper", "Ground Plane", "Power Plane", "Bottom Copper"],
                "typical_thickness": "1.6mm",
                "applications": "Mixed-signal, medium-speed digital, better EMI control",
                "cost": "Medium"
            },
            6: {
                "description": "6-layer PCB",
                "layers": ["Top", "Ground", "Inner Signal 1", "Inner Signal 2", "Power", "Bottom"],
                "typical_thickness": "1.6mm",
                "applications": "High-speed digital, complex mixed-signal",
                "cost": "Medium-High"
            },
            8: {
                "description": "8-layer PCB",
                "layers": ["Top", "Ground", "Signal 1", "Signal 2", "Power 1", "Signal 3", "Power 2", "Bottom"],
                "typical_thickness": "1.6mm",
                "applications": "High-speed digital, DDR memory interfaces, complex power distribution",
                "cost": "High"
            }
        }
        
        if target_layers in stackup_suggestions:
            return stackup_suggestions[target_layers]
        else:
            return {
                "description": f"Custom {target_layers}-layer PCB",
                "layers": [f"Layer {i+1}" for i in range(target_layers)],
                "typical_thickness": "Custom",
                "applications": "Complex, high-density designs",
                "cost": "High",
                "note": "Consult with PCB manufacturer for optimal stackup"
            }
    
    def get_manufacturing_constraints(self) -> Dict[str, Any]:
        """Get typical manufacturing constraints"""
        return {
            "minimum_track_width": {
                "standard": "0.1mm (4 mil)",
                "fine_pitch": "0.075mm (3 mil)",
                "advanced": "0.05mm (2 mil)"
            },
            "minimum_via_size": {
                "standard": "0.2mm (8 mil)",
                "micro_via": "0.1mm (4 mil)",
                "advanced": "0.075mm (3 mil)"
            },
            "layer_count_costs": {
                "2_layer": "Base cost",
                "4_layer": "1.5-2x base cost",
                "6_layer": "2-3x base cost",
                "8_layer": "3-4x base cost",
                "10+_layer": "4-6x base cost"
            },
            "typical_delivery": {
                "2-4_layer": "5-7 days",
                "6-8_layer": "7-10 days",
                "10+_layer": "10-15 days"
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get history of operations performed"""
        return self.operation_history.copy()
    
    def clear_operation_history(self):
        """Clear the operation history"""
        self.operation_history.clear()
    
    def can_undo_last_operation(self) -> Tuple[bool, str]:
        """Check if the last operation can be undone"""
        if not self.operation_history:
            return False, "No operations to undo"
        
        last_op = self.operation_history[-1]
        op_type = last_op.get("type", "unknown")
        
        if op_type == "add_copper_layers":
            return True, f"Can undo layer addition from {last_op['from_count']} to {last_op['to_count']} layers"
        elif op_type == "modify_board_settings":
            return True, f"Can undo board settings changes: {', '.join(last_op['changes'])}"
        else:
            return False, f"Cannot undo operation type: {op_type}"
    
    def undo_last_operation(self) -> Tuple[bool, str]:
        """Undo the last operation"""
        try:
            can_undo, message = self.can_undo_last_operation()
            if not can_undo:
                return False, message
            
            # For now, use the backup settings restore
            # More sophisticated undo would require per-operation restore functions
            if self.restore_settings():
                undone_op = self.operation_history.pop()
                return True, f"Undone: {undone_op['type']} from {undone_op['timestamp']}"
            else:
                return False, "Failed to restore settings"
                
        except Exception as e:
            return False, f"Error during undo: {str(e)}"


# Global operations instance
kicad_ops = KiCadOperations()
