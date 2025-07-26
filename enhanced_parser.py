"""
Enhanced KiCad Context Parser with Read/Write Access
Extracts comprehensive design information and provides modification capabilities
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
    print("pcbnew module not available - context parsing will be limited")


class DesignModification:
    """Represents a potential design modification"""
    
    def __init__(self, description: str, action: Callable, undo_action: Callable = None):
        self.description = description
        self.action = action
        self.undo_action = undo_action
        self.applied = False
    
    def apply(self) -> bool:
        """Apply this modification"""
        try:
            self.action()
            self.applied = True
            return True
        except Exception as e:
            print(f"Failed to apply modification: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo this modification"""
        if not self.applied or not self.undo_action:
            return False
        try:
            self.undo_action()
            self.applied = False
            return True
        except Exception as e:
            print(f"Failed to undo modification: {e}")
            return False


class EnhancedKiCadParser:
    """Enhanced parser with read/write access to KiCad designs"""
    
    def __init__(self):
        self.current_board = None
        self.current_schematic = None
        self.pending_modifications = []
        self.applied_modifications = []
        
    def get_comprehensive_context(self) -> str:
        """Get comprehensive design context including all PCB design aspects"""
        if not PCBNEW_AVAILABLE:
            return "KiCad modules not available for context parsing."
        
        try:
            board = pcbnew.GetBoard()
            if not board:
                return "No active PCB design found."
            
            context_parts = []
            
            # Basic design information
            context_parts.append(self._get_basic_info(board))
            
            # Advanced operations availability
            context_parts.append(self._get_advanced_operations_info())
            
            # Detailed component analysis
            context_parts.append(self._get_detailed_components(board))
            
            # Advanced net analysis
            context_parts.append(self._get_advanced_nets(board))
            
            # Signal integrity analysis
            context_parts.append(self._get_signal_integrity_info(board))
            
            # Power distribution analysis
            context_parts.append(self._get_power_analysis(board))
            
            # Thermal analysis
            context_parts.append(self._get_thermal_analysis(board))
            
            # Manufacturing considerations
            context_parts.append(self._get_manufacturing_info(board))
            
            # Design rules and constraints
            context_parts.append(self._get_design_rules_detailed(board))
            
            # Footprint analysis
            context_parts.append(self._get_footprint_analysis(board))
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            return f"Error accessing comprehensive KiCad context: {str(e)}"
    
    def _get_basic_info(self, board) -> str:
        """Get basic board information"""
        try:
            info = ["=== BASIC DESIGN INFORMATION ==="]
            
            # Board file and project info
            board_file = board.GetFileName()
            info.append(f"Board file: {board_file}")
            
            if board_file:
                project_path = Path(board_file).parent
                project_name = Path(board_file).stem
                info.append(f"Project: {project_name}")
                info.append(f"Project path: {project_path}")
            
            # Board dimensions and layers
            bbox = board.GetBoardEdgesBoundingBox()
            width_mm = pcbnew.ToMM(bbox.GetWidth()) 
            height_mm = pcbnew.ToMM(bbox.GetHeight())
            area_cm2 = (width_mm * height_mm) / 100
            
            info.append(f"Board size: {width_mm:.2f} x {height_mm:.2f} mm ({area_cm2:.1f} cm²)")
            
            layer_count = board.GetCopperLayerCount()
            info.append(f"Layer stack: {layer_count} copper layers")
            
            # Layer names
            layer_names = []
            for layer_id in range(pcbnew.PCB_LAYER_ID_COUNT):
                if board.IsLayerEnabled(layer_id):
                    layer_name = board.GetLayerName(layer_id)
                    if layer_name:
                        layer_names.append(layer_name)
            
            if layer_names:
                info.append(f"Enabled layers: {', '.join(layer_names[:10])}")
                if len(layer_names) > 10:
                    info.append(f"  ... and {len(layer_names) - 10} more layers")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"Error getting basic info: {str(e)}"
    
    def _get_advanced_operations_info(self) -> str:
        """Get information about available advanced operations"""
        try:
            result = ["=== ADVANCED OPERATIONS AVAILABLE ==="]
            
            # Try to import advanced operations
            try:
                from .kicad_operations import kicad_ops
                can_modify, message = kicad_ops.can_modify_board()
                
                if can_modify:
                    result.append("✅ Advanced board modifications available")
                    
                    # Get current layer info
                    layer_info = kicad_ops.get_current_layer_info()
                    if "error" not in layer_info:
                        current_layers = layer_info["copper_layers"]
                        result.append(f"📋 Current copper layers: {current_layers}")
                        
                        # Suggest common layer upgrades
                        if current_layers == 2:
                            result.append("💡 Can upgrade to 4-layer for better power distribution")
                        elif current_layers == 4:
                            result.append("💡 Can upgrade to 6/8-layer for high-speed designs")
                    
                    result.append("\n🔧 Available Operations:")
                    result.append("  • Add copper layers (e.g., '2-layer to 4-layer upgrade')")
                    result.append("  • Modify track widths, via sizes, clearances")
                    result.append("  • Update design rules and constraints")
                    result.append("  • Get manufacturing recommendations")
                    result.append("  • Layer stackup planning and optimization")
                    
                    # Get manufacturing constraints
                    constraints = kicad_ops.get_manufacturing_constraints()
                    result.append(f"\n📏 Manufacturing Guidelines:")
                    result.append(f"  • Min track width: {constraints['minimum_track_width']['standard']}")
                    result.append(f"  • Min via size: {constraints['minimum_via_size']['standard']}")
                    
                else:
                    result.append(f"❌ Advanced operations not available: {message}")
                    
            except ImportError:
                result.append("❌ Advanced operations module not loaded")
                result.append("  • Basic read/analysis operations available")
                result.append("  • Write operations limited to basic modifications")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error checking advanced operations: {str(e)}"
    
    def _get_detailed_components(self, board) -> str:
        """Get detailed component analysis"""
        try:
            components = []
            component_types = {}
            power_components = []
            critical_components = []
            
            for footprint in board.GetFootprints():
                ref = footprint.GetReference()
                value = footprint.GetValue()
                fp_name = str(footprint.GetFPID().GetLibItemName())
                
                # Position and orientation
                pos = footprint.GetPosition()
                x_mm = pcbnew.ToMM(pos.x)
                y_mm = pcbnew.ToMM(pos.y)
                rotation = footprint.GetOrientation() / 10.0
                
                # Layer
                layer = "Top" if not footprint.IsFlipped() else "Bottom"
                
                # Component type analysis
                ref_prefix = ''.join(filter(str.isalpha, ref))
                if ref_prefix not in component_types:
                    component_types[ref_prefix] = {"count": 0, "components": []}
                component_types[ref_prefix]["count"] += 1
                component_types[ref_prefix]["components"].append({
                    "ref": ref, "value": value, "footprint": fp_name,
                    "position": (x_mm, y_mm), "rotation": rotation, "layer": layer
                })
                
                # Identify power components
                if any(keyword in value.upper() for keyword in ['LDO', 'BUCK', 'BOOST', 'VREG']):
                    power_components.append(f"{ref} ({value})")
                
                # Identify critical components (processors, FPGAs, etc.)
                if any(keyword in fp_name.upper() for keyword in ['BGA', 'QFP', 'QFN']) and 'C' not in ref:
                    critical_components.append(f"{ref} ({value}) - {fp_name}")
            
            result = [f"=== DETAILED COMPONENT ANALYSIS ({len(components)} total) ==="]
            
            # Component type summary
            result.append("\nComponent Types:")
            for comp_type, data in sorted(component_types.items()):
                result.append(f"  {comp_type}: {data['count']} components")
                
                # Show examples for major types
                if data['count'] > 1 and comp_type in ['R', 'C', 'L']:
                    values = list(set([comp['value'] for comp in data['components'][:5]]))
                    result.append(f"    Values: {', '.join(values[:5])}")
            
            # Power components
            if power_components:
                result.append(f"\nPower Management ({len(power_components)}):")
                for comp in power_components:
                    result.append(f"  {comp}")
            
            # Critical components
            if critical_components:
                result.append(f"\nCritical Components ({len(critical_components)}):")
                for comp in critical_components:
                    result.append(f"  {comp}")
            
            # Component density analysis
            board_bbox = board.GetBoardEdgesBoundingBox()
            board_area_mm2 = pcbnew.ToMM(board_bbox.GetWidth()) * pcbnew.ToMM(board_bbox.GetHeight())
            if board_area_mm2 > 0:
                density = len(list(board.GetFootprints())) / board_area_mm2 * 100  # components per cm²
                result.append(f"\nComponent Density: {density:.1f} components/cm²")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing components: {str(e)}"
    
    def _get_advanced_nets(self, board) -> str:
        """Get advanced net analysis"""
        try:
            netlist = board.GetNetInfo()
            net_count = netlist.GetNetCount()
            
            power_nets = []
            clock_nets = []
            differential_pairs = []
            high_speed_nets = []
            
            for net_code in range(net_count):
                net = netlist.GetNetItem(net_code)
                if net:
                    net_name = net.GetNetname()
                    
                    if not net_name or net_name == "":
                        continue
                    
                    net_upper = net_name.upper()
                    
                    # Categorize nets
                    if any(keyword in net_upper for keyword in 
                           ['VCC', 'VDD', 'VEE', 'VSS', 'GND', 'POWER', '+', '-', 'VREF']):
                        power_nets.append(net_name)
                    elif any(keyword in net_upper for keyword in ['CLK', 'CLOCK', 'OSC', 'XTAL']):
                        clock_nets.append(net_name)
                    elif '_P' in net_name or '_N' in net_name:
                        base_name = net_name.replace('_P', '').replace('_N', '')
                        if base_name not in [dp.split('_')[0] for dp in differential_pairs]:
                            differential_pairs.append(base_name)
                    elif any(keyword in net_upper for keyword in 
                             ['USB', 'PCIE', 'HDMI', 'LVDS', 'SERDES', 'HIGH_SPEED']):
                        high_speed_nets.append(net_name)
            
            result = [f"=== ADVANCED NET ANALYSIS ({net_count} total nets) ==="]
            
            result.append(f"\nPower Nets ({len(power_nets)}):")
            for net in power_nets[:10]:
                result.append(f"  {net}")
            if len(power_nets) > 10:
                result.append(f"  ... and {len(power_nets) - 10} more")
            
            if clock_nets:
                result.append(f"\nClock/Timing Nets ({len(clock_nets)}):")
                for net in clock_nets:
                    result.append(f"  {net}")
            
            if differential_pairs:
                result.append(f"\nDifferential Pairs ({len(differential_pairs)}):")
                for pair in differential_pairs:
                    result.append(f"  {pair}_P / {pair}_N")
            
            if high_speed_nets:
                result.append(f"\nHigh-Speed Nets ({len(high_speed_nets)}):")
                for net in high_speed_nets:
                    result.append(f"  {net}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing nets: {str(e)}"
    
    def _get_signal_integrity_info(self, board) -> str:
        """Analyze signal integrity considerations"""
        try:
            result = ["=== SIGNAL INTEGRITY ANALYSIS ==="]
            
            # Analyze trace lengths and impedance-critical nets
            tracks = board.GetTracks()
            long_traces = []
            short_traces = []
            
            for track in tracks:
                if track.GetClass() == "PCB_TRACK":
                    length_mm = pcbnew.ToMM(track.GetLength())
                    net_name = track.GetNetname()
                    
                    if length_mm > 50:  # Long traces that might need attention
                        long_traces.append(f"{net_name}: {length_mm:.1f}mm")
                    elif length_mm < 1:  # Very short traces
                        short_traces.append(f"{net_name}: {length_mm:.1f}mm")
            
            if long_traces:
                result.append(f"\nLong Traces (>50mm, {len(long_traces)} total):")
                for trace in long_traces[:5]:
                    result.append(f"  {trace}")
                if len(long_traces) > 5:
                    result.append(f"  ... and {len(long_traces) - 5} more")
            
            # Via analysis for signal integrity
            via_count = 0
            for track in tracks:
                if track.GetClass() == "PCB_VIA":
                    via_count += 1
            
            result.append(f"\nVia Count: {via_count} (potential impedance discontinuities)")
            
            # Layer transitions analysis
            result.append("\nSignal Integrity Recommendations:")
            result.append("  - Consider controlled impedance for traces >25mm")
            result.append("  - Review differential pair routing and spacing")
            result.append("  - Check for ground plane continuity under high-speed signals")
            result.append("  - Verify via stitching near layer transitions")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing signal integrity: {str(e)}"
    
    def _get_power_analysis(self, board) -> str:
        """Analyze power distribution network"""
        try:
            result = ["=== POWER DISTRIBUTION ANALYSIS ==="]
            
            # Count decoupling capacitors
            decap_count = 0
            bulk_caps = []
            
            for footprint in board.GetFootprints():
                ref = footprint.GetReference()
                value = footprint.GetValue()
                
                if ref.startswith('C') and any(unit in value.upper() for unit in ['UF', 'NF', 'PF']):
                    # Parse capacitor value
                    if 'UF' in value.upper():
                        decap_count += 1
                        if any(size in value for size in ['10', '22', '47', '100']):
                            bulk_caps.append(f"{ref}: {value}")
            
            result.append(f"Decoupling Capacitors: {decap_count} found")
            
            if bulk_caps:
                result.append(f"Bulk Capacitors ({len(bulk_caps)}):")
                for cap in bulk_caps[:5]:
                    result.append(f"  {cap}")
            
            result.append("\nPower Distribution Recommendations:")
            result.append("  - Verify adequate decoupling near power pins")
            result.append("  - Check power plane copper pour coverage")
            result.append("  - Consider thermal vias for power components")
            result.append("  - Review current capacity of power traces")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing power distribution: {str(e)}"
    
    def _get_thermal_analysis(self, board) -> str:
        """Analyze thermal considerations"""
        try:
            result = ["=== THERMAL ANALYSIS ==="]
            
            # Identify heat-generating components
            power_components = []
            thermal_vias = 0
            
            for footprint in board.GetFootprints():
                ref = footprint.GetReference()
                value = footprint.GetValue()
                fp_name = str(footprint.GetFPID().GetLibItemName())
                
                # Identify potential heat sources
                if any(keyword in fp_name.upper() for keyword in 
                       ['TO-', 'SOT', 'DPAK', 'D2PAK', 'PowerPAD']):
                    power_components.append(f"{ref} ({fp_name})")
                elif any(keyword in value.upper() for keyword in 
                         ['LDO', 'VREG', 'MOSFET', 'DRIVER']):
                    power_components.append(f"{ref} ({value})")
            
            # Count thermal vias (rough estimate)
            tracks = board.GetTracks()
            for track in tracks:
                if track.GetClass() == "PCB_VIA":
                    via_size = pcbnew.ToMM(track.GetWidth())
                    if via_size < 0.3:  # Small vias often used for thermal
                        thermal_vias += 1
            
            if power_components:
                result.append(f"Heat-Generating Components ({len(power_components)}):")
                for comp in power_components:
                    result.append(f"  {comp}")
            
            result.append(f"\nThermal Vias (estimated): {thermal_vias}")
            
            result.append("\nThermal Management Recommendations:")
            result.append("  - Add thermal vias under power components")
            result.append("  - Consider copper pour for heat spreading")
            result.append("  - Review component spacing for airflow")
            result.append("  - Check thermal pad connections")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing thermal considerations: {str(e)}"
    
    def _get_manufacturing_info(self, board) -> str:
        """Analyze manufacturing considerations"""
        try:
            result = ["=== MANUFACTURING ANALYSIS ==="]
            
            # Analyze minimum feature sizes
            design_settings = board.GetDesignSettings()
            
            min_track = pcbnew.ToMM(design_settings.m_TrackMinWidth)
            min_via = pcbnew.ToMM(design_settings.m_ViasMinSize)
            min_drill = pcbnew.ToMM(design_settings.m_ViasMinDrill)
            
            result.append(f"Minimum track width: {min_track:.3f}mm")
            result.append(f"Minimum via size: {min_via:.3f}mm (drill: {min_drill:.3f}mm)")
            
            # Component analysis for assembly
            smd_count = 0
            through_hole_count = 0
            fine_pitch_count = 0
            
            for footprint in board.GetFootprints():
                fp_name = str(footprint.GetFPID().GetLibItemName())
                
                if any(pkg in fp_name.upper() for pkg in ['SMD', 'QFN', 'BGA', 'LGA']):
                    smd_count += 1
                    if any(fine in fp_name.upper() for fine in ['0402', '0201', 'BGA', 'QFN']):
                        fine_pitch_count += 1
                else:
                    through_hole_count += 1
            
            result.append(f"\nAssembly Analysis:")
            result.append(f"  SMD components: {smd_count}")
            result.append(f"  Through-hole components: {through_hole_count}")
            result.append(f"  Fine-pitch components: {fine_pitch_count}")
            
            # Manufacturing recommendations
            result.append(f"\nManufacturing Recommendations:")
            if min_track < 0.1:
                result.append("  ⚠ Very fine track width - verify fab capabilities")
            if fine_pitch_count > 0:
                result.append("  ⚠ Fine-pitch components require precise assembly")
            result.append("  - Add fiducials for automated assembly")
            result.append("  - Consider panelization for small boards")
            result.append("  - Verify solder mask and silkscreen clearances")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing manufacturing: {str(e)}"
    
    def _get_design_rules_detailed(self, board) -> str:
        """Get detailed design rules analysis"""
        try:
            result = ["=== DESIGN RULES ANALYSIS ==="]
            
            design_settings = board.GetDesignSettings()
            
            # Track width analysis
            current_track = pcbnew.ToMM(design_settings.GetCurrentTrackWidth())
            min_track = pcbnew.ToMM(design_settings.m_TrackMinWidth)
            
            result.append(f"Current track width: {current_track:.3f}mm")
            result.append(f"Minimum track width: {min_track:.3f}mm")
            
            # Via analysis
            current_via = pcbnew.ToMM(design_settings.GetCurrentViaSize())
            current_drill = pcbnew.ToMM(design_settings.GetCurrentViaDrill())
            min_via = pcbnew.ToMM(design_settings.m_ViasMinSize)
            min_drill = pcbnew.ToMM(design_settings.m_ViasMinDrill)
            
            result.append(f"Current via: {current_via:.3f}mm (drill: {current_drill:.3f}mm)")
            result.append(f"Minimum via: {min_via:.3f}mm (drill: {min_drill:.3f}mm)")
            
            # Clearance analysis
            result.append(f"\nClearance Rules:")
            result.append(f"  Track-to-track: Check design rules")
            result.append(f"  Via-to-track: Check design rules")
            result.append(f"  Pad-to-pad: Check design rules")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing design rules: {str(e)}"
    
    def _get_footprint_analysis(self, board) -> str:
        """Analyze footprints and libraries"""
        try:
            result = ["=== FOOTPRINT ANALYSIS ==="]
            
            footprint_libraries = {}
            custom_footprints = []
            potential_issues = []
            
            for footprint in board.GetFootprints():
                fp_id = footprint.GetFPID()
                lib_name = str(fp_id.GetLibNickname())
                fp_name = str(fp_id.GetLibItemName())
                ref = footprint.GetReference()
                
                # Track library usage
                if lib_name not in footprint_libraries:
                    footprint_libraries[lib_name] = []
                footprint_libraries[lib_name].append(fp_name)
                
                # Identify custom footprints (no library)
                if not lib_name or lib_name == "":
                    custom_footprints.append(f"{ref}: {fp_name}")
                
                # Check for potential issues
                if "NOCONNECT" in fp_name.upper():
                    potential_issues.append(f"{ref}: No-connect footprint")
                elif "TEST" in fp_name.upper():
                    potential_issues.append(f"{ref}: Test point")
            
            result.append(f"Footprint Libraries Used ({len(footprint_libraries)}):")
            for lib, footprints in footprint_libraries.items():
                unique_fps = len(set(footprints))
                result.append(f"  {lib}: {len(footprints)} instances, {unique_fps} unique")
            
            if custom_footprints:
                result.append(f"\nCustom Footprints ({len(custom_footprints)}):")
                for fp in custom_footprints[:5]:
                    result.append(f"  {fp}")
                if len(custom_footprints) > 5:
                    result.append(f"  ... and {len(custom_footprints) - 5} more")
            
            if potential_issues:
                result.append(f"\nSpecial Footprints:")
                for issue in potential_issues:
                    result.append(f"  {issue}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing footprints: {str(e)}"
    
    # Write access methods
    def propose_modification(self, description: str, modification_func: Callable, 
                           undo_func: Callable = None) -> DesignModification:
        """Propose a design modification"""
        mod = DesignModification(description, modification_func, undo_func)
        self.pending_modifications.append(mod)
        return mod
    
    def apply_modification(self, modification: DesignModification) -> bool:
        """Apply a proposed modification"""
        if modification.apply():
            if modification in self.pending_modifications:
                self.pending_modifications.remove(modification)
            self.applied_modifications.append(modification)
            return True
        return False
    
    def undo_last_modification(self) -> bool:
        """Undo the last applied modification"""
        if self.applied_modifications:
            last_mod = self.applied_modifications[-1]
            if last_mod.undo():
                self.applied_modifications.remove(last_mod)
                return True
        return False
    
    def get_pending_modifications(self) -> List[str]:
        """Get list of pending modifications"""
        return [mod.description for mod in self.pending_modifications]
    
    def clear_pending_modifications(self):
        """Clear all pending modifications"""
        self.pending_modifications.clear()


# Global enhanced parser instance
enhanced_parser = EnhancedKiCadParser()
