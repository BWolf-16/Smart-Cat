"""
KiCad Context Parser for KiCat AI Assistant
Extracts design information from KiCad schematics and PCBs
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


try:
    import pcbnew
    PCBNEW_AVAILABLE = True
except ImportError:
    PCBNEW_AVAILABLE = False
    print("pcbnew module not available - context parsing will be limited")


class KiCadContextParser:
    """Parses KiCad design files to extract context for AI analysis"""
    
    def __init__(self):
        self.current_board = None
        self.current_schematic = None
        
    def get_current_context(self) -> str:
        """Get context from the currently active KiCad editor"""
        if not PCBNEW_AVAILABLE:
            return "KiCad modules not available for context parsing."
        
        try:
            # Try to get the current board
            board = pcbnew.GetBoard()
            if board:
                return self.parse_pcb_context(board)
            else:
                return "No active PCB design found."
        except Exception as e:
            return f"Error accessing KiCad context: {str(e)}"
    
    def parse_pcb_context(self, board) -> str:
        """Parse PCB board context"""
        try:
            context_parts = []
            
            # Basic board info
            context_parts.append("=== PCB DESIGN CONTEXT ===")
            context_parts.append(f"Board file: {board.GetFileName()}")
            
            # Board dimensions
            bbox = board.GetBoardEdgesBoundingBox()
            width_mm = pcbnew.ToMM(bbox.GetWidth())
            height_mm = pcbnew.ToMM(bbox.GetHeight())
            context_parts.append(f"Board size: {width_mm:.2f} x {height_mm:.2f} mm")
            
            # Layer count
            layer_count = board.GetCopperLayerCount()
            context_parts.append(f"Layer count: {layer_count}")
            
            # Components analysis
            components_info = self.analyze_components(board)
            context_parts.append(components_info)
            
            # Nets analysis
            nets_info = self.analyze_nets(board)
            context_parts.append(nets_info)
            
            # Design rules and constraints
            drc_info = self.analyze_design_rules(board)
            if drc_info:
                context_parts.append(drc_info)
            
            # Trace analysis
            traces_info = self.analyze_traces(board)
            context_parts.append(traces_info)
            
            # Via analysis
            vias_info = self.analyze_vias(board)
            context_parts.append(vias_info)
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            return f"Error parsing PCB context: {str(e)}"
    
    def analyze_components(self, board) -> str:
        """Analyze components on the board"""
        try:
            components = []
            component_count = 0
            
            for footprint in board.GetFootprints():
                component_count += 1
                
                # Get component info
                reference = footprint.GetReference()
                value = footprint.GetValue()
                footprint_name = str(footprint.GetFPID().GetLibItemName())
                
                # Position
                pos = footprint.GetPosition()
                x_mm = pcbnew.ToMM(pos.x)
                y_mm = pcbnew.ToMM(pos.y)
                
                # Layer (Top/Bottom)
                layer = "Top" if footprint.IsFlipped() == False else "Bottom"
                
                # Rotation
                rotation = footprint.GetOrientation() / 10.0  # Convert to degrees
                
                components.append({
                    'reference': reference,
                    'value': value,
                    'footprint': footprint_name,
                    'position': (x_mm, y_mm),
                    'layer': layer,
                    'rotation': rotation
                })
            
            # Create summary
            result = [f"=== COMPONENTS ({component_count} total) ==="]
            
            # Group by component type
            component_types = {}
            for comp in components:
                ref_prefix = ''.join(filter(str.isalpha, comp['reference']))
                if ref_prefix not in component_types:
                    component_types[ref_prefix] = []
                component_types[ref_prefix].append(comp)
            
            # Summary by type
            for comp_type, comps in component_types.items():
                result.append(f"{comp_type}: {len(comps)} components")
            
            # Detailed component list (limit to avoid overwhelming)
            result.append("\nComponent Details:")
            for comp in components[:20]:  # Limit to first 20
                result.append(
                    f"  {comp['reference']}: {comp['value']} "
                    f"({comp['footprint']}) at ({comp['position'][0]:.1f}, {comp['position'][1]:.1f}) "
                    f"on {comp['layer']} layer"
                )
            
            if len(components) > 20:
                result.append(f"  ... and {len(components) - 20} more components")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing components: {str(e)}"
    
    def analyze_nets(self, board) -> str:
        """Analyze nets and connectivity"""
        try:
            netlist = board.GetNetInfo()
            net_count = netlist.GetNetCount()
            
            result = [f"=== NETS ({net_count} total) ==="]
            
            # Analyze significant nets
            power_nets = []
            signal_nets = []
            
            for net_code in range(net_count):
                net = netlist.GetNetItem(net_code)
                if net:
                    net_name = net.GetNetname()
                    
                    # Categorize nets
                    if any(power_keyword in net_name.upper() for power_keyword in 
                           ['VCC', 'VDD', 'VEE', 'VSS', 'GND', 'POWER', '+5V', '+3V3', '+12V', '-12V']):
                        power_nets.append(net_name)
                    elif net_name and net_name != "":
                        signal_nets.append(net_name)
            
            result.append(f"Power nets ({len(power_nets)}): {', '.join(power_nets[:10])}")
            if len(power_nets) > 10:
                result.append(f"  ... and {len(power_nets) - 10} more power nets")
            
            result.append(f"Signal nets: {len(signal_nets)} total")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing nets: {str(e)}"
    
    def analyze_design_rules(self, board) -> str:
        """Analyze design rules and potential DRC violations"""
        try:
            # This is a simplified version - full DRC would require running the DRC engine
            result = ["=== DESIGN RULES ==="]
            
            # Get design settings
            design_settings = board.GetDesignSettings()
            
            # Track widths
            track_width = pcbnew.ToMM(design_settings.GetCurrentTrackWidth())
            result.append(f"Current track width: {track_width:.3f} mm")
            
            # Via sizes
            via_size = pcbnew.ToMM(design_settings.GetCurrentViaSize())
            via_drill = pcbnew.ToMM(design_settings.GetCurrentViaDrill())
            result.append(f"Current via: {via_size:.3f} mm (drill: {via_drill:.3f} mm)")
            
            # Minimum values
            min_track_width = pcbnew.ToMM(design_settings.m_TrackMinWidth)
            min_via_size = pcbnew.ToMM(design_settings.m_ViasMinSize)
            result.append(f"Minimums - Track: {min_track_width:.3f} mm, Via: {min_via_size:.3f} mm")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing design rules: {str(e)}"
    
    def analyze_traces(self, board) -> str:
        """Analyze PCB traces"""
        try:
            tracks = board.GetTracks()
            
            total_tracks = 0
            total_length = 0
            width_stats = {}
            
            for track in tracks:
                if track.GetClass() == "PCB_TRACK":
                    total_tracks += 1
                    total_length += pcbnew.ToMM(track.GetLength())
                    
                    width = pcbnew.ToMM(track.GetWidth())
                    width_key = f"{width:.3f}"
                    width_stats[width_key] = width_stats.get(width_key, 0) + 1
            
            result = [f"=== TRACES ({total_tracks} total) ==="]
            result.append(f"Total trace length: {total_length:.1f} mm")
            
            # Width distribution
            result.append("Track width distribution:")
            for width, count in sorted(width_stats.items())[:5]:
                result.append(f"  {width} mm: {count} tracks")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing traces: {str(e)}"
    
    def analyze_vias(self, board) -> str:
        """Analyze vias on the board"""
        try:
            tracks = board.GetTracks()
            
            via_count = 0
            via_sizes = {}
            
            for track in tracks:
                if track.GetClass() == "PCB_VIA":
                    via_count += 1
                    
                    size = pcbnew.ToMM(track.GetWidth())
                    drill = pcbnew.ToMM(track.GetDrillValue())
                    
                    size_key = f"{size:.3f}/{drill:.3f}"
                    via_sizes[size_key] = via_sizes.get(size_key, 0) + 1
            
            result = [f"=== VIAS ({via_count} total) ==="]
            
            # Via size distribution
            result.append("Via sizes (outer/drill):")
            for size, count in via_sizes.items():
                result.append(f"  {size} mm: {count} vias")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error analyzing vias: {str(e)}"
    
    def parse_schematic_context(self, schematic_file: str) -> str:
        """Parse schematic file context (placeholder for future implementation)"""
        # This would require eeschema API access which is more complex
        # For now, return a placeholder
        return f"Schematic analysis not yet implemented for {schematic_file}"
    
    def get_project_files(self) -> Dict[str, List[str]]:
        """Get list of project files"""
        try:
            if not PCBNEW_AVAILABLE:
                return {"error": ["PCBNew not available"]}
            
            board = pcbnew.GetBoard()
            if not board:
                return {"error": ["No active board"]}
            
            board_file = board.GetFileName()
            if not board_file:
                return {"error": ["Board file path not available"]}
            
            project_dir = Path(board_file).parent
            project_name = Path(board_file).stem
            
            files = {
                "pcb": [],
                "schematic": [],
                "libraries": [],
                "gerbers": [],
                "other": []
            }
            
            # Look for related files
            for file_path in project_dir.iterdir():
                if file_path.is_file():
                    suffix = file_path.suffix.lower()
                    name = file_path.name
                    
                    if suffix == '.kicad_pcb':
                        files["pcb"].append(str(file_path))
                    elif suffix == '.kicad_sch':
                        files["schematic"].append(str(file_path))
                    elif suffix in ['.kicad_sym', '.lib']:
                        files["libraries"].append(str(file_path))
                    elif suffix in ['.gbr', '.drl', '.gko', '.gts', '.gbs']:
                        files["gerbers"].append(str(file_path))
                    elif project_name in name:
                        files["other"].append(str(file_path))
            
            return files
            
        except Exception as e:
            return {"error": [f"Error getting project files: {str(e)}"]}
    
    def get_context_summary(self) -> str:
        """Get a concise summary of the current design context"""
        try:
            if not PCBNEW_AVAILABLE:
                return "KiCad integration not available"
            
            board = pcbnew.GetBoard()
            if not board:
                return "No active PCB design"
            
            # Quick summary
            footprint_count = len(list(board.GetFootprints()))
            net_count = board.GetNetInfo().GetNetCount()
            
            bbox = board.GetBoardEdgesBoundingBox()
            width_mm = pcbnew.ToMM(bbox.GetWidth())
            height_mm = pcbnew.ToMM(bbox.GetHeight())
            
            return (
                f"Active PCB: {footprint_count} components, {net_count} nets, "
                f"{width_mm:.1f}x{height_mm:.1f}mm, {board.GetCopperLayerCount()} layers"
            )
            
        except Exception as e:
            return f"Error getting context summary: {str(e)}"
    
    def export_netlist_info(self) -> Dict[str, Any]:
        """Export detailed netlist information for AI analysis"""
        try:
            if not PCBNEW_AVAILABLE:
                return {"error": "PCBNew not available"}
            
            board = pcbnew.GetBoard()
            if not board:
                return {"error": "No active board"}
            
            netlist_data = {
                "components": [],
                "nets": [],
                "connections": []
            }
            
            # Export components
            for footprint in board.GetFootprints():
                component_data = {
                    "reference": footprint.GetReference(),
                    "value": footprint.GetValue(),
                    "footprint": str(footprint.GetFPID().GetLibItemName()),
                    "layer": "Top" if not footprint.IsFlipped() else "Bottom",
                    "pads": []
                }
                
                # Export pads
                for pad in footprint.Pads():
                    pad_data = {
                        "number": pad.GetNumber(),
                        "net": pad.GetNetname(),
                        "shape": str(pad.GetShape()),
                        "size": [pcbnew.ToMM(pad.GetSize().x), pcbnew.ToMM(pad.GetSize().y)]
                    }
                    component_data["pads"].append(pad_data)
                
                netlist_data["components"].append(component_data)
            
            # Export nets
            netinfo = board.GetNetInfo()
            for net_code in range(netinfo.GetNetCount()):
                net = netinfo.GetNetItem(net_code)
                if net:
                    net_data = {
                        "name": net.GetNetname(),
                        "code": net.GetNetCode(),
                        "class": str(net.GetNetClassName()) if hasattr(net, 'GetNetClassName') else "Default"
                    }
                    netlist_data["nets"].append(net_data)
            
            return netlist_data
            
        except Exception as e:
            return {"error": f"Error exporting netlist: {str(e)}"}


# Global parser instance
parser = KiCadContextParser()
