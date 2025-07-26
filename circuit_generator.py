"""
Circuit Generator Module
Handles automatic circuit generation from user descriptions
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path

try:
    import pcbnew
    import eeschema
    KICAD_AVAILABLE = True
except ImportError:
    KICAD_AVAILABLE = False
    print("KiCad modules not available - circuit generation will be limited")


class CircuitTemplate:
    """Represents a circuit template for common designs"""
    
    def __init__(self, name: str, description: str, components: List[Dict], 
                 connections: List[Dict], estimated_layers: int = 2):
        self.name = name
        self.description = description
        self.components = components  # List of component specifications
        self.connections = connections  # List of net connections
        self.estimated_layers = estimated_layers
        self.design_rules = {}
        self.special_requirements = []


class CircuitGenerator:
    """Generates circuits automatically from user descriptions"""
    
    def __init__(self):
        self.templates = {}
        self._load_circuit_templates()
        self.current_circuit = None
    
    def _load_circuit_templates(self):
        """Load predefined circuit templates"""
        
        # USB4 Flex Cable Template
        self.templates["usb4_flex"] = CircuitTemplate(
            name="USB4 Flex Cable",
            description="USB4 flexible cable with high-speed differential pairs",
            components=[
                {
                    "ref": "J1", "value": "USB4_Connector_A", 
                    "footprint": "Connector_USB:USB_C_Receptacle_Palconn_UTC16-G",
                    "description": "USB4 Type-C connector (source)"
                },
                {
                    "ref": "J2", "value": "USB4_Connector_B",
                    "footprint": "Connector_USB:USB_C_Receptacle_Palconn_UTC16-G", 
                    "description": "USB4 Type-C connector (destination)"
                },
                {
                    "ref": "C1", "value": "100nF", 
                    "footprint": "Capacitor_SMD:C_0402_1005Metric",
                    "description": "Decoupling capacitor for VBUS"
                },
                {
                    "ref": "C2", "value": "100nF",
                    "footprint": "Capacitor_SMD:C_0402_1005Metric", 
                    "description": "Decoupling capacitor for VCONN"
                },
                {
                    "ref": "R1", "value": "5.1k",
                    "footprint": "Resistor_SMD:R_0402_1005Metric",
                    "description": "CC1 pull-down resistor"
                },
                {
                    "ref": "R2", "value": "5.1k", 
                    "footprint": "Resistor_SMD:R_0402_1005Metric",
                    "description": "CC2 pull-down resistor"
                }
            ],
            connections=[
                {"net": "VBUS", "pins": ["J1.A4", "J1.A9", "J1.B4", "J1.B9", "J2.A4", "J2.A9", "J2.B4", "J2.B9"]},
                {"net": "GND", "pins": ["J1.A1", "J1.A12", "J1.B1", "J1.B12", "J2.A1", "J2.A12", "J2.B1", "J2.B12", "C1.2", "C2.2"]},
                {"net": "USB_D_P", "pins": ["J1.A6", "J2.A6"]},
                {"net": "USB_D_N", "pins": ["J1.A7", "J2.A7"]},
                {"net": "USB_TX1_P", "pins": ["J1.A2", "J2.A2"]},
                {"net": "USB_TX1_N", "pins": ["J1.A3", "J2.A3"]},
                {"net": "USB_RX1_P", "pins": ["J1.B10", "J2.B10"]},
                {"net": "USB_RX1_N", "pins": ["J1.B11", "J2.B11"]},
                {"net": "USB_TX2_P", "pins": ["J1.B2", "J2.B2"]},
                {"net": "USB_TX2_N", "pins": ["J1.B3", "J2.B3"]},
                {"net": "USB_RX2_P", "pins": ["J1.A10", "J2.A10"]},
                {"net": "USB_RX2_N", "pins": ["J1.A11", "J2.A11"]},
                {"net": "CC1", "pins": ["J1.A5", "J2.A5", "R1.1"]},
                {"net": "CC2", "pins": ["J1.B5", "J2.B5", "R2.1"]},
                {"net": "VCONN", "pins": ["J1.A8", "J2.A8", "C2.1"]},
                {"net": "GND", "pins": ["R1.2", "R2.2"]}
            ],
            estimated_layers=4  # Need 4 layers for proper impedance control
        )
        
        # USB-C to Lightning Cable
        self.templates["usbc_lightning"] = CircuitTemplate(
            name="USB-C to Lightning Cable",
            description="USB-C to Lightning cable with authentication",
            components=[
                {
                    "ref": "J1", "value": "USB_C_Receptacle",
                    "footprint": "Connector_USB:USB_C_Receptacle_Palconn_UTC16-G",
                    "description": "USB-C connector"
                },
                {
                    "ref": "J2", "value": "Lightning_Connector",
                    "footprint": "Connector:Lightning_8Pin",
                    "description": "Lightning connector"
                },
                {
                    "ref": "U1", "value": "Lightning_Auth_IC",
                    "footprint": "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm",
                    "description": "Lightning authentication IC"
                }
            ],
            connections=[
                {"net": "VBUS", "pins": ["J1.A4", "J1.B4", "J2.1"]},
                {"net": "GND", "pins": ["J1.A1", "J1.B1", "J2.8", "U1.EP"]},
                {"net": "USB_D_P", "pins": ["J1.A6", "U1.1"]},
                {"net": "USB_D_N", "pins": ["J1.A7", "U1.2"]},
                {"net": "LIGHTNING_D_P", "pins": ["U1.15", "J2.3"]},
                {"net": "LIGHTNING_D_N", "pins": ["U1.16", "J2.4"]}
            ],
            estimated_layers=2
        )
        
        # Simple LED Strip Controller
        self.templates["led_controller"] = CircuitTemplate(
            name="LED Strip Controller",
            description="Simple RGB LED strip controller with PWM",
            components=[
                {
                    "ref": "U1", "value": "STM32F103C8T6",
                    "footprint": "Package_QFP:LQFP-48_7x7mm_P0.5mm",
                    "description": "Microcontroller"
                },
                {
                    "ref": "Q1", "value": "MOSFET_N_CH",
                    "footprint": "Package_TO_SOT_SMD:SOT-23",
                    "description": "Red channel MOSFET"
                },
                {
                    "ref": "Q2", "value": "MOSFET_N_CH", 
                    "footprint": "Package_TO_SOT_SMD:SOT-23",
                    "description": "Green channel MOSFET"
                },
                {
                    "ref": "Q3", "value": "MOSFET_N_CH",
                    "footprint": "Package_TO_SOT_SMD:SOT-23", 
                    "description": "Blue channel MOSFET"
                }
            ],
            connections=[
                {"net": "VCC", "pins": ["U1.1", "U1.48"]},
                {"net": "GND", "pins": ["U1.8", "U1.23", "Q1.2", "Q2.2", "Q3.2"]},
                {"net": "PWM_R", "pins": ["U1.15", "Q1.1"]},
                {"net": "PWM_G", "pins": ["U1.16", "Q2.1"]},
                {"net": "PWM_B", "pins": ["U1.17", "Q3.1"]}
            ],
            estimated_layers=2
        )
        
        # Power Supply Module
        self.templates["power_supply"] = CircuitTemplate(
            name="Switching Power Supply",
            description="Buck converter power supply module",
            components=[
                {
                    "ref": "U1", "value": "LM2596",
                    "footprint": "Package_TO_SOT_SMD:TO-263-5_TabPin3",
                    "description": "Buck converter IC"
                },
                {
                    "ref": "L1", "value": "100uH",
                    "footprint": "Inductor_SMD:L_1210_3225Metric",
                    "description": "Switching inductor"
                },
                {
                    "ref": "C1", "value": "1000uF",
                    "footprint": "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
                    "description": "Input capacitor"
                },
                {
                    "ref": "C2", "value": "1000uF",
                    "footprint": "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
                    "description": "Output capacitor"
                }
            ],
            connections=[
                {"net": "VIN", "pins": ["U1.1", "C1.1"]},
                {"net": "GND", "pins": ["U1.2", "C1.2", "C2.2"]},
                {"net": "SW", "pins": ["U1.4", "L1.1"]},
                {"net": "VOUT", "pins": ["L1.2", "C2.1", "U1.5"]}
            ],
            estimated_layers=2
        )
    
    def identify_circuit_from_description(self, description: str) -> Optional[CircuitTemplate]:
        """Identify the most suitable circuit template from user description"""
        desc_lower = description.lower()
        
        # USB4 related keywords
        if any(keyword in desc_lower for keyword in ["usb4", "usb 4", "thunderbolt", "usb-c flex", "usb4 flex"]):
            return self.templates.get("usb4_flex")
        
        # USB-C to Lightning
        elif any(keyword in desc_lower for keyword in ["lightning", "usbc lightning", "usb-c lightning"]):
            return self.templates.get("usbc_lightning")
        
        # LED controller
        elif any(keyword in desc_lower for keyword in ["led strip", "rgb led", "led controller", "pwm led"]):
            return self.templates.get("led_controller")
        
        # Power supply
        elif any(keyword in desc_lower for keyword in ["power supply", "buck converter", "voltage regulator", "psu"]):
            return self.templates.get("power_supply")
        
        return None
    
    def generate_circuit_description(self, template: CircuitTemplate) -> str:
        """Generate a detailed description of the circuit"""
        description = f"""
🔧 **{template.name}** Circuit Generation

**Description:** {template.description}

**Components ({len(template.components)}):**
"""
        
        for comp in template.components:
            description += f"  • {comp['ref']}: {comp['value']} ({comp['description']})\n"
        
        description += f"""
**Key Connections ({len(template.connections)} nets):**
"""
        
        for conn in template.connections[:5]:  # Show first 5 connections
            pins_str = ", ".join(conn['pins'][:3])
            if len(conn['pins']) > 3:
                pins_str += f" + {len(conn['pins']) - 3} more"
            description += f"  • {conn['net']}: {pins_str}\n"
        
        if len(template.connections) > 5:
            description += f"  • ... and {len(template.connections) - 5} more connections\n"
        
        description += f"""
**Estimated PCB Requirements:**
  • Recommended layers: {template.estimated_layers}
  • Board complexity: {'High' if template.estimated_layers > 2 else 'Medium'}
"""
        
        if template.estimated_layers > 2:
            description += f"  • Reason: High-speed signals require controlled impedance\n"
        
        return description
    
    def can_create_schematic(self) -> Tuple[bool, str]:
        """Check if schematic creation is possible"""
        if not KICAD_AVAILABLE:
            return False, "KiCad modules not available"
        
        # Check if we have an active project
        try:
            # This would check for active schematic editor
            return True, "Schematic creation available"
        except Exception as e:
            return False, f"Schematic creation not available: {str(e)}"
    
    def create_schematic(self, template: CircuitTemplate) -> Tuple[bool, str]:
        """Create schematic from template (placeholder implementation)"""
        # This would be a complex implementation involving KiCad's schematic API
        # For now, return success with instructions for manual creation
        
        self.current_circuit = template
        
        schematic_instructions = f"""
📋 **Schematic Creation Instructions for {template.name}:**

**Step 1: Create New Schematic**
  • Open KiCad Project Manager
  • Create new project or open existing
  • Open Schematic Editor (Eeschema)

**Step 2: Add Components**
"""
        
        for comp in template.components:
            schematic_instructions += f"  • Add {comp['ref']}: {comp['value']} (footprint: {comp['footprint']})\n"
        
        schematic_instructions += """
**Step 3: Create Connections**
"""
        
        for conn in template.connections:
            schematic_instructions += f"  • Connect net '{conn['net']}' to pins: {', '.join(conn['pins'])}\n"
        
        schematic_instructions += """
**Step 4: Electrical Rules Check (ERC)**
  • Run Tools > Electrical Rules Checker
  • Fix any violations

**Step 5: Generate Netlist**
  • Tools > Generate Netlist File
  • Save for PCB import

✅ **Ready for PCB Layout!**
"""
        
        return True, schematic_instructions
    
    def estimate_pcb_complexity(self, template: CircuitTemplate) -> Dict[str, Any]:
        """Estimate PCB layout complexity and requirements"""
        complexity = {
            "recommended_layers": template.estimated_layers,
            "complexity_level": "Low",
            "special_requirements": [],
            "estimated_size": "Small",
            "manufacturing_notes": []
        }
        
        # Analyze components for complexity
        high_speed_components = 0
        power_components = 0
        fine_pitch_components = 0
        
        for comp in template.components:
            footprint = comp.get('footprint', '').upper()
            value = comp.get('value', '').upper()
            
            # High-speed components
            if any(keyword in value for keyword in ['USB4', 'THUNDERBOLT', 'PCIE', 'HDMI']):
                high_speed_components += 1
                complexity["special_requirements"].append("Controlled impedance routing")
                complexity["special_requirements"].append("Length matching for differential pairs")
            
            # Power components
            if any(keyword in footprint for keyword in ['TO-', 'DPAK', 'D2PAK']) or \
               any(keyword in value for keyword in ['LDO', 'BUCK', 'BOOST', 'VREG']):
                power_components += 1
                complexity["special_requirements"].append("Thermal management")
                complexity["special_requirements"].append("Power plane design")
            
            # Fine pitch components
            if any(keyword in footprint for keyword in ['QFN', 'BGA', '0.4MM', '0.5MM']):
                fine_pitch_components += 1
                complexity["special_requirements"].append("Fine-pitch component placement")
                complexity["manufacturing_notes"].append("Advanced PCB fabrication required")
        
        # Determine complexity level
        if high_speed_components > 0 or template.estimated_layers > 4:
            complexity["complexity_level"] = "High"
            complexity["estimated_size"] = "Medium"
        elif power_components > 2 or template.estimated_layers > 2:
            complexity["complexity_level"] = "Medium"
        
        # Layer-specific recommendations
        if template.estimated_layers == 4:
            complexity["manufacturing_notes"].append("4-layer stackup: Sig-Gnd-Pwr-Sig recommended")
        elif template.estimated_layers == 6:
            complexity["manufacturing_notes"].append("6-layer stackup: Sig-Gnd-Sig-Pwr-Sig-Gnd recommended")
        
        # Add impedance control requirements
        if high_speed_components > 0:
            complexity["special_requirements"].append("50Ω single-ended / 90Ω differential impedance")
            complexity["manufacturing_notes"].append("Impedance control required (+/- 10%)")
        
        return complexity
    
    def get_pcb_layout_recommendations(self, template: CircuitTemplate) -> List[str]:
        """Get specific PCB layout recommendations for the circuit"""
        recommendations = []
        
        # Analyze circuit for specific recommendations
        circuit_name = template.name.lower()
        
        if "usb4" in circuit_name or "thunderbolt" in circuit_name:
            recommendations.extend([
                "🔌 Keep USB4 differential pairs short and matched (±0.1mm)",
                "⚡ Use 90Ω differential impedance for USB4 pairs",
                "🛡️ Add ground guard traces around high-speed signals",
                "📏 Maintain 3W spacing between differential pairs",
                "🔄 Avoid vias in high-speed signal paths when possible",
                "⚠️ Place decoupling capacitors close to connector pins"
            ])
        
        elif "lightning" in circuit_name:
            recommendations.extend([
                "🔐 Keep authentication IC close to Lightning connector",
                "⚡ Use controlled impedance for data lines",
                "🛡️ Add ESD protection on all connector pins",
                "🔋 Ensure robust power delivery path"
            ])
        
        elif "led" in circuit_name:
            recommendations.extend([
                "💡 Use thick traces for LED power connections",
                "🔥 Add thermal vias under MOSFETs",
                "⚡ Keep PWM signals short to reduce EMI",
                "🔌 Add TVS diodes for ESD protection"
            ])
        
        elif "power" in circuit_name:
            recommendations.extend([
                "⚡ Use wide traces and copper pour for power paths",
                "🔥 Add thermal relief for power components",
                "🌊 Minimize switching node area and trace length",
                "📦 Place input/output capacitors close to IC",
                "🛡️ Use ground plane for noise reduction"
            ])
        
        # General recommendations
        recommendations.extend([
            "📐 Run DRC (Design Rule Check) frequently",
            "🎯 Place components before routing",
            "🔄 Route critical signals first",
            "✅ Verify all connections with netlist"
        ])
        
        return recommendations
    
    def get_current_circuit(self) -> Optional[CircuitTemplate]:
        """Get the currently selected circuit template"""
        return self.current_circuit
    
    def clear_current_circuit(self):
        """Clear the current circuit selection"""
        self.current_circuit = None


# Global circuit generator instance
circuit_gen = CircuitGenerator()
