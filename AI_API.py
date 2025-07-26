"""
AI API Client for KiCat AI Assistant
Handles communication with various AI providers (Claude, OpenAI, and compatible APIs)
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, Tuple, List
from .config import config

# Try to import KiCad operations for advanced features
try:
    from .kicad_operations import kicad_ops
    KICAD_OPS_AVAILABLE = True
except ImportError:
    KICAD_OPS_AVAILABLE = False

# Try to import circuit generator for automatic circuit creation
try:
    from .circuit_generator import circuit_gen
    CIRCUIT_GEN_AVAILABLE = True
except ImportError:
    CIRCUIT_GEN_AVAILABLE = False


class AIAPIClient:
    """Universal client for communicating with various AI APIs with memory and PCB design expertise"""
    
    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        """Initialize client with config"""
        self.config = custom_config or {}
        self.session_history = []
        self.design_memory = []  # Long-term memory of design decisions
        self.max_history_length = 20  # Keep last 20 exchanges
        self.max_memory_length = 50   # Keep last 50 design decisions
    
    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value from custom config or global config"""
        if key in self.config:
            return self.config[key]
        return config.get(key, default)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        provider = self._get_config_value("api_provider", "claude")
        api_key = self._get_config_value("api_key", "")
        
        if provider == "claude":
            return {
                "Content-Type": "application/json",
                "X-API-Key": api_key,
                "anthropic-version": "2023-06-01"
            }
        elif provider == "openai":
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        elif provider == "custom":
            # For custom OpenAI-compatible APIs
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        else:
            raise ValueError(f"Unknown API provider: {provider}")
    
    def _get_api_url(self) -> str:
        """Get the API endpoint URL"""
        provider = self._get_config_value("api_provider", "claude")
        base_url = self._get_config_value("api_base_url", "")
        
        if provider == "claude":
            return f"{base_url}/v1/messages"
        elif provider in ["openai", "custom"]:
            return f"{base_url}/v1/chat/completions"
        else:
            raise ValueError(f"Unknown API provider: {provider}")
    
    def _build_claude_request(self, message: str, context: str = "", memory_context: str = "") -> Dict[str, Any]:
        """Build request payload for Claude API"""
        system_prompt = self._build_system_prompt(context, memory_context)
        
        request_data = {
            "model": self._get_config_value("model", "claude-3-sonnet-20240229"),
            "max_tokens": self._get_config_value("max_tokens", 4096),
            "temperature": self._get_config_value("temperature", 0.3),
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
        
        return request_data
    
    def _build_openai_request(self, message: str, context: str = "", memory_context: str = "") -> Dict[str, Any]:
        """Build request payload for OpenAI and compatible APIs"""
        system_prompt = self._build_system_prompt(context, memory_context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        request_data = {
            "model": self._get_config_value("model", "gpt-4"),
            "messages": messages,
            "max_tokens": self._get_config_value("max_tokens", 4096),
            "temperature": self._get_config_value("temperature", 0.3)
        }
        
        return request_data
    
    def _build_system_prompt(self, context: str = "", memory_context: str = "") -> str:
        """Build system prompt with context and memory"""
        base_prompt = """You are KiCat AI Assistant, an expert electronics engineer with deep knowledge of PCB design, schematic analysis, and manufacturing processes. You have READ and WRITE access to KiCad designs and can:

## Core Capabilities:
1. **READ ACCESS**: Analyze schematics, PCB layouts, footprints, libraries, and design rules
2. **WRITE ACCESS**: Modify designs with user permission (always ask before making changes)
3. **CIRCUIT GENERATION**: Automatically create complete circuits from simple descriptions
   - "I want a USB4 flex cable" → Generate complete USB4 circuit + PCB layout
   - "Make me an LED controller" → Create PWM LED controller circuit
   - "I need a power supply" → Generate switching power supply design
4. **ADVANCED OPERATIONS**: 
   - Change board settings (track widths, via sizes, clearances)
   - Add/modify copper layers (e.g., convert 2-layer to 4-layer board)
   - Modify design rules and constraints
   - Update layer stackup configurations
   - Change manufacturing preferences
4. **DEEP PCB KNOWLEDGE**: Understanding of:
   - Component selection and placement optimization
   - Signal integrity (impedance control, crosstalk, EMI/EMC)
   - Power distribution networks (PDN analysis, decoupling)
   - Thermal management and heat dissipation
   - Manufacturing processes (DFM, assembly, testing)
   - Footprint design and library management
   - Layer stackup design and via planning
   - Flux considerations and soldering processes
   - Design for testability (DFT) and debugging
   - Cost optimization and supplier considerations

## Design Analysis Areas:
- **Electrical**: Voltage/current ratings, power dissipation, signal timing
- **Mechanical**: Component fit, connector alignment, board flex/stress
- **Thermal**: Heat sources, thermal paths, cooling requirements  
- **Manufacturing**: Fab constraints, assembly processes, yield optimization
- **Testing**: Test points, boundary scan, functional testing
- **Reliability**: MTBF analysis, component derating, environmental factors

## Advanced Modification Capabilities:
- **Circuit Generation**: Create complete circuits from descriptions ("I want a USB4 flex cable")
- **Automatic PCB Flow**: Schematic → PCB layout with optimal layer count and settings
- **Layer Management**: Can add copper layers (e.g., "add 2 copper layers for better power distribution")
- **Board Settings**: Can modify track widths, via sizes, clearances
- **Design Rules**: Can update design rule constraints
- **Stackup Planning**: Can suggest and implement optimal layer stackups
- **Manufacturing Settings**: Can adjust settings for different fab capabilities

## Workflow Examples:
1. **Complete Design Flow**: "I want a USB4 flex cable"
   - Generate USB4 circuit with proper components and connections
   - Ask: "Circuit ready! Want to go to PCB layout?"
   - If yes: Analyze requirements, suggest 4-layer stackup
   - Create PCB with proper impedance control and routing guidelines

2. **Layer Optimization**: When PCB needs >2 layers
   - "I recommend using 4 copper layers for this design because..."
   - Explain benefits: better power distribution, controlled impedance
   - Ask for permission and implement if approved

## Interaction Protocol:
- For READ operations: Provide detailed analysis immediately
- For WRITE operations: Always explain what you want to change and ask for explicit permission
- For ADVANCED operations (layer changes, settings): Explain impact and get explicit user consent
- Always mention if changes affect manufacturing cost or complexity
- Offer "undo" option after any modification
- Remember our conversation history and previous design decisions

## Examples of Advanced Operations:
- **Complete Design**: "I want a USB4 flex cable" → Auto-generate circuit → Suggest 4-layer PCB → Create layout
- **Circuit Generation**: "Make me an LED controller" → Generate PWM controller circuit with MOSFETs
- **Layer Management**: "Add 2 copper layers to create a 4-layer board with dedicated power/ground planes"
- **Settings**: "Change minimum track width to 0.1mm for higher density routing"
- **Optimization**: "Modify via size to 0.2mm for better manufacturability"
- **Advanced Setup**: "Update board settings for advanced PCB fabrication capabilities"

You maintain context across our conversation and can reference previous discussions, design iterations, and learned preferences. Always be practical and focus on actionable improvements."""
        
        if KICAD_OPS_AVAILABLE:
            base_prompt += "\n\n## Advanced Operations Available:\nI have access to KiCad's advanced board modification capabilities including layer management and settings changes."
        
        if CIRCUIT_GEN_AVAILABLE:
            base_prompt += "\n\n## Circuit Generation Available:\nI can automatically generate complete circuits from simple descriptions like 'I want a USB4 flex cable' and guide you through the complete design process from schematic to PCB layout."
        
        if context.strip():
            base_prompt += f"\n\n## Current KiCad Design Context:\n{context}"
        
        if memory_context.strip():
            base_prompt += f"\n\n## Previous Conversation Context:\n{memory_context}"
        
        return base_prompt
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection with a simple request"""
        try:
            # Simple test message
            test_response = self.send_message(
                "Hello! Please respond with 'API connection successful' to confirm the connection is working.",
                ""
            )
            
            if test_response and "successful" in test_response.lower():
                return True, "Connection successful"
            else:
                return False, "API responded but test failed"
                
        except Exception as e:
            return False, str(e)
    
    def send_message(self, message: str, context: str = "") -> Optional[str]:
        """Send message to AI API with memory and get response"""
        try:
            # Check for circuit generation requests first
            is_circuit_request, circuit_info, circuit_data = self.identify_circuit_request(message)
            
            # Build memory context from conversation history
            memory_context = self._build_memory_context()
            
            # Add circuit generation context if applicable
            if is_circuit_request:
                memory_context += f"\n\n## Circuit Generation Request Detected:\n{circuit_info}"
                if circuit_data:
                    template = circuit_data.get('template')
                    if template:
                        memory_context += f"\nTemplate: {template.name} ({template.estimated_layers} layers recommended)"
            
            # Store the user message in history
            self.session_history.append({
                "role": "user",
                "content": message,
                "timestamp": self._get_timestamp(),
                "context": context,
                "circuit_request": is_circuit_request
            })
            
            provider = self._get_config_value("api_provider", "claude")
            
            # Build request based on provider
            if provider == "claude":
                request_data = self._build_claude_request(message, context, memory_context)
            elif provider in ["openai", "custom"]:
                request_data = self._build_openai_request(message, context, memory_context)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Prepare HTTP request
            url = self._get_api_url()
            headers = self._get_headers()
            
            # Convert data to JSON
            json_data = json.dumps(request_data).encode('utf-8')
            
            # Create request
            request = urllib.request.Request(url, data=json_data, headers=headers)
            
            # Send request
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = json.loads(response.read().decode('utf-8'))
            
            # Extract response text based on provider
            ai_response = None
            if provider == "claude":
                if 'content' in response_data and len(response_data['content']) > 0:
                    ai_response = response_data['content'][0]['text']
                else:
                    raise ValueError("Unexpected Claude API response format")
            
            elif provider in ["openai", "custom"]:
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    ai_response = response_data['choices'][0]['message']['content']
                else:
                    raise ValueError("Unexpected OpenAI-compatible API response format")
            
            # Post-process response for circuit generation workflow
            if ai_response and is_circuit_request and circuit_data:
                # Generate the actual circuit and append to response
                template = circuit_data.get('template')
                if template:
                    success, circuit_result, generation_data = self.generate_circuit(template.name)
                    if success:
                        ai_response += f"\n\n{generation_data['description']}"
                        ai_response += f"\n\n{generation_data['schematic_instructions']}"
                        ai_response += f"\n\n🤔 **Ready for PCB Layout?**\nThe circuit schematic is complete! Would you like me to proceed with creating the PCB layout? I'll automatically set up the optimal layer stackup and provide routing guidelines."
            
            # Check for PCB transition requests
            elif ai_response:
                pcb_transition, pcb_response = self.handle_pcb_transition_request(message)
                if pcb_transition:
                    ai_response += f"\n\n{pcb_response}"
                else:
                    # Check for layer approval
                    layer_approved, layer_response = self.handle_layer_approval(message)
                    if layer_approved:
                        ai_response += f"\n\n{layer_response}"
            
            # Store AI response in history
            if ai_response:
                self.session_history.append({
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": self._get_timestamp(),
                    "circuit_generated": is_circuit_request
                })
                
                # Extract and store design decisions for long-term memory
                self._extract_design_decisions(message, ai_response, context)
                
                # Trim history if needed
                self._trim_history()
            
            return ai_response
            
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP Error {e.code}: {e.reason}"
            
            # Try to get more detailed error message
            try:
                error_response = json.loads(e.read().decode('utf-8'))
                if 'error' in error_response:
                    if isinstance(error_response['error'], dict):
                        error_msg += f" - {error_response['error'].get('message', '')}"
                    else:
                        error_msg += f" - {error_response['error']}"
            except:
                pass
            
            raise Exception(error_msg)
        
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")
        
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
        
        except Exception as e:
            raise Exception(f"API call failed: {e}")
    
    def send_message_with_history(self, message: str, context: str = "") -> Optional[str]:
        """Send message with conversation history (for future enhancement)"""
        # For now, just call the basic send_message
        # This could be extended to maintain conversation context
        return self.send_message(message, context)
    
    def clear_history(self):
        """Clear conversation history"""
        self.session_history.clear()
    
    def clear_memory(self):
        """Clear design memory"""
        self.design_memory.clear()
    
    def clear_all(self):
        """Clear both conversation history and design memory"""
        self.clear_history()
        self.clear_memory()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _build_memory_context(self) -> str:
        """Build memory context from conversation history and design decisions"""
        memory_parts = []
        
        # Add recent conversation context
        if self.session_history:
            memory_parts.append("## Recent Conversation:")
            for entry in self.session_history[-6:]:  # Last 3 exchanges
                role = "You" if entry["role"] == "user" else "Assistant"
                memory_parts.append(f"{role}: {entry['content'][:200]}...")
        
        # Add design decision memory
        if self.design_memory:
            memory_parts.append("\n## Previous Design Decisions:")
            for decision in self.design_memory[-10:]:  # Last 10 decisions
                memory_parts.append(f"- {decision}")
        
        return "\n".join(memory_parts)
    
    def _extract_design_decisions(self, user_message: str, ai_response: str, context: str):
        """Extract important design decisions for long-term memory"""
        # Keywords that indicate design decisions
        decision_keywords = [
            "change", "modify", "move", "rotate", "delete", "add", "place",
            "route", "connect", "disconnect", "resize", "adjust", "optimize",
            "improve", "fix", "correct", "update", "replace", "swap"
        ]
        
        # Check if this was a design modification discussion
        user_lower = user_message.lower()
        ai_lower = ai_response.lower()
        
        if any(keyword in user_lower or keyword in ai_lower for keyword in decision_keywords):
            # Extract key information
            decision = f"[{self._get_timestamp()}] "
            
            if "component" in user_lower or "component" in ai_lower:
                decision += "Component modification: "
            elif "route" in user_lower or "trace" in user_lower:
                decision += "Routing change: "
            elif "placement" in user_lower or "move" in user_lower:
                decision += "Placement adjustment: "
            else:
                decision += "Design change: "
            
            # Add brief summary (first 100 chars of user message)
            decision += user_message[:100].replace('\n', ' ')
            
            self.design_memory.append(decision)
            
            # Trim memory if needed
            if len(self.design_memory) > self.max_memory_length:
                self.design_memory = self.design_memory[-self.max_memory_length:]
    
    def _trim_history(self):
        """Trim conversation history to maintain performance"""
        if len(self.session_history) > self.max_history_length:
            self.session_history = self.session_history[-self.max_history_length:]
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation"""
        if not self.session_history:
            return "No conversation history yet."
        
        summary_parts = [
            f"Conversation started with {len(self.session_history)} messages",
            f"Design decisions made: {len(self.design_memory)}",
        ]
        
        if self.session_history:
            last_msg = self.session_history[-1]
            summary_parts.append(f"Last message: {last_msg['content'][:100]}...")
        
        return "\n".join(summary_parts)
    
    def get_supported_models(self) -> Dict[str, list]:
        """Get list of supported models for each provider"""
        return {
            "claude": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307"
            ],
            "openai": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-4-32k",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ],
            "custom": [
                "Custom Model 1",
                "Custom Model 2",
                "Enter your model name"
            ]
        }
    
    def validate_api_key(self, api_key: str, provider: str) -> Tuple[bool, str]:
        """Validate API key format"""
        if not api_key or not api_key.strip():
            return False, "API key is empty"
        
        api_key = api_key.strip()
        
        if provider == "claude":
            if not api_key.startswith("sk-ant-"):
                return False, "Claude API key should start with 'sk-ant-'"
            if len(api_key) < 20:
                return False, "Claude API key appears too short"
        
        elif provider == "openai":
            if not api_key.startswith("sk-"):
                return False, "OpenAI API key should start with 'sk-'"
            if len(api_key) < 20:
                return False, "OpenAI API key appears too short"
        
        elif provider == "custom":
            # Less strict validation for custom providers
            if len(api_key) < 10:
                return False, "API key appears too short"
        
        return True, "API key format looks valid"
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimate of token count for text"""
        # Very rough approximation: ~4 characters per token
        return len(text) // 4
    
    def get_max_context_length(self) -> int:
        """Get maximum context length for current model"""
        model = self._get_config_value("model", "")
        
        # Model context lengths (approximate)
        context_lengths = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "gpt-4-turbo-preview": 128000,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384
        }
        
        return context_lengths.get(model, 4096)
    
    def truncate_context(self, context: str, max_tokens: int = None) -> str:
        """Truncate context to fit within token limits"""
        if max_tokens is None:
            max_tokens = self.get_max_context_length() // 2  # Use half for context
        
        current_tokens = self.estimate_tokens(context)
        
        if current_tokens <= max_tokens:
            return context
        
        # Simple truncation - take the last portion
        # This preserves the most recent/relevant information
        target_chars = max_tokens * 4  # Rough conversion back to characters
        
        if len(context) > target_chars:
            truncated = context[-target_chars:]
            # Try to start at a clean boundary
            newline_pos = truncated.find('\n')
            if newline_pos > 0:
                truncated = truncated[newline_pos + 1:]
            
            return f"[Context truncated...]\n{truncated}"
        
        return context
    
    # Advanced KiCad Operations
    def can_perform_advanced_operations(self) -> Tuple[bool, str]:
        """Check if advanced KiCad operations are available"""
        if not KICAD_OPS_AVAILABLE:
            return False, "Advanced KiCad operations module not available"
        return kicad_ops.can_modify_board()
    
    def get_layer_info(self) -> Dict[str, Any]:
        """Get current layer information"""
        if not KICAD_OPS_AVAILABLE:
            return {"error": "Advanced operations not available"}
        return kicad_ops.get_current_layer_info()
    
    def add_copper_layers(self, target_count: int) -> Tuple[bool, str]:
        """Add copper layers to reach target count"""
        if not KICAD_OPS_AVAILABLE:
            return False, "Advanced operations not available"
        return kicad_ops.add_copper_layers(target_count)
    
    def modify_board_settings(self, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Modify board settings"""
        if not KICAD_OPS_AVAILABLE:
            return False, "Advanced operations not available"
        return kicad_ops.modify_board_settings(settings)
    
    def get_layer_stackup_suggestion(self, layer_count: int) -> Dict[str, Any]:
        """Get layer stackup suggestions"""
        if not KICAD_OPS_AVAILABLE:
            return {"error": "Advanced operations not available"}
        return kicad_ops.suggest_layer_stackup(layer_count)
    
    def get_manufacturing_constraints(self) -> Dict[str, Any]:
        """Get manufacturing constraints information"""
        if not KICAD_OPS_AVAILABLE:
            return {"error": "Advanced operations not available"}
        return kicad_ops.get_manufacturing_constraints()
    
    def undo_last_operation(self) -> Tuple[bool, str]:
        """Undo the last advanced operation"""
        if not KICAD_OPS_AVAILABLE:
            return False, "Advanced operations not available"
        return kicad_ops.undo_last_operation()
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get history of advanced operations"""
        if not KICAD_OPS_AVAILABLE:
            return []
        return kicad_ops.get_operation_history()
    
    def process_advanced_request(self, user_request: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Process advanced operation requests from AI responses"""
        # Parse common advanced operation requests
        request_lower = user_request.lower()
        
        # Layer operations
        if "add" in request_lower and ("copper" in request_lower or "layer" in request_lower):
            # Extract target layer count
            import re
            numbers = re.findall(r'\d+', user_request)
            if numbers:
                try:
                    if "layer" in request_lower:
                        target_count = int(numbers[-1])  # Last number is likely target
                    else:
                        # Adding X layers to current
                        layer_info = self.get_layer_info()
                        if "error" not in layer_info:
                            current = layer_info["copper_layers"]
                            target_count = current + int(numbers[0])
                        else:
                            target_count = int(numbers[0])
                    
                    can_add, message = kicad_ops.can_add_copper_layers(target_count) if KICAD_OPS_AVAILABLE else (False, "Not available")
                    return True, f"Layer operation requested: {target_count} layers", {
                        "operation": "add_layers",
                        "target_count": target_count,
                        "can_perform": can_add,
                        "message": message
                    }
                except (ValueError, IndexError):
                    return False, "Could not parse layer count from request", {}
        
        # Settings modifications
        elif any(keyword in request_lower for keyword in ["track width", "via size", "clearance", "settings"]):
            # Extract settings values
            settings = {}
            import re
            
            # Track width
            track_match = re.search(r'track\s+width.*?(\d+\.?\d*)\s*mm', request_lower)
            if track_match:
                settings["track_width"] = float(track_match.group(1))
            
            # Via size
            via_match = re.search(r'via\s+size.*?(\d+\.?\d*)\s*mm', request_lower)
            if via_match:
                settings["via_size"] = float(via_match.group(1))
            
            # Clearance
            clear_match = re.search(r'clearance.*?(\d+\.?\d*)\s*mm', request_lower)
            if clear_match:
                settings["clearance"] = float(clear_match.group(1))
            
            if settings:
                return True, f"Settings modification requested", {
                    "operation": "modify_settings",
                    "settings": settings,
                    "can_perform": KICAD_OPS_AVAILABLE
                }
        
        return False, "No advanced operation detected", {}
    
    # Circuit Generation Methods
    def can_generate_circuits(self) -> Tuple[bool, str]:
        """Check if circuit generation is available"""
        if not CIRCUIT_GEN_AVAILABLE:
            return False, "Circuit generation module not available"
        return True, "Circuit generation available"
    
    def identify_circuit_request(self, user_message: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Identify if user is requesting circuit generation"""
        if not CIRCUIT_GEN_AVAILABLE:
            return False, "Circuit generation not available", {}
        
        template = circuit_gen.identify_circuit_from_description(user_message)
        if template:
            return True, f"Identified circuit request: {template.name}", {
                "template": template,
                "circuit_name": template.name,
                "description": template.description,
                "estimated_layers": template.estimated_layers
            }
        
        return False, "No circuit template matched", {}
    
    def generate_circuit(self, template_name: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a circuit from template"""
        if not CIRCUIT_GEN_AVAILABLE:
            return False, "Circuit generation not available", {}
        
        # Get template by name
        template = None
        for t in circuit_gen.templates.values():
            if t.name.lower() == template_name.lower():
                template = t
                break
        
        if not template:
            return False, f"Template '{template_name}' not found", {}
        
        # Generate circuit description
        circuit_description = circuit_gen.generate_circuit_description(template)
        
        # Create schematic instructions
        success, schematic_info = circuit_gen.create_schematic(template)
        
        if success:
            return True, "Circuit generated successfully", {
                "template": template,
                "description": circuit_description,
                "schematic_instructions": schematic_info,
                "ready_for_pcb": True
            }
        else:
            return False, f"Circuit generation failed: {schematic_info}", {}
    
    def get_pcb_requirements(self, template_name: str) -> Dict[str, Any]:
        """Get PCB requirements for a circuit"""
        if not CIRCUIT_GEN_AVAILABLE:
            return {"error": "Circuit generation not available"}
        
        template = circuit_gen.current_circuit
        if not template:
            return {"error": "No active circuit template"}
        
        complexity = circuit_gen.estimate_pcb_complexity(template)
        recommendations = circuit_gen.get_pcb_layout_recommendations(template)
        
        return {
            "template_name": template.name,
            "complexity": complexity,
            "recommendations": recommendations,
            "ready_for_layout": True
        }
    
    def create_pcb_layout(self, template_name: str, approved_layers: int = None) -> Tuple[bool, str]:
        """Create PCB layout from circuit template"""
        if not CIRCUIT_GEN_AVAILABLE:
            return False, "Circuit generation not available"
        
        if not KICAD_OPS_AVAILABLE:
            return False, "KiCad operations not available for PCB creation"
        
        template = circuit_gen.current_circuit
        if not template:
            return False, "No active circuit template"
        
        # Check if we need to adjust layers
        recommended_layers = template.estimated_layers
        current_layer_info = self.get_layer_info()
        
        if "error" not in current_layer_info:
            current_layers = current_layer_info.get("copper_layers", 2)
            
            if approved_layers:
                target_layers = approved_layers
            else:
                target_layers = recommended_layers
            
            # Add layers if needed
            if target_layers > current_layers:
                success, message = self.add_copper_layers(target_layers)
                if not success:
                    return False, f"Failed to add copper layers: {message}"
        
        # Get PCB layout instructions
        recommendations = circuit_gen.get_pcb_layout_recommendations(template)
        
        layout_instructions = f"""
🎯 **PCB Layout Created for {template.name}**

**Layer Configuration:**
  • Total copper layers: {target_layers if 'target_layers' in locals() else recommended_layers}
  • Stackup optimized for circuit requirements

**Layout Guidelines:**
"""
        
        for rec in recommendations[:8]:  # Show first 8 recommendations
            layout_instructions += f"  {rec}\n"
        
        layout_instructions += """
**Next Steps:**
  1. Import netlist from schematic
  2. Place components following recommendations
  3. Route critical signals first (power, clocks, high-speed)
  4. Run DRC to verify design rules
  5. Generate Gerber files for manufacturing

✅ **PCB Layout Ready!**
"""
        
        return True, layout_instructions
    
    def get_design_flow_status(self) -> Dict[str, Any]:
        """Get current status of the design flow"""
        status = {
            "circuit_generation_available": CIRCUIT_GEN_AVAILABLE,
            "advanced_operations_available": KICAD_OPS_AVAILABLE,
            "current_circuit": None,
            "design_phase": "idle"
        }
        
        if CIRCUIT_GEN_AVAILABLE:
            current_circuit = circuit_gen.get_current_circuit()
            if current_circuit:
                status["current_circuit"] = current_circuit.name
                status["design_phase"] = "circuit_ready"
                status["estimated_layers"] = current_circuit.estimated_layers
        
        return status
    
    def handle_pcb_transition_request(self, user_message: str) -> Tuple[bool, str]:
        """Handle user request to transition from schematic to PCB"""
        message_lower = user_message.lower()
        
        # Check if user wants to go to PCB
        pcb_keywords = ["go to pcb", "pcb layout", "create pcb", "make pcb", "yes", "proceed"]
        wants_pcb = any(keyword in message_lower for keyword in pcb_keywords)
        
        if not wants_pcb:
            return False, "No PCB transition request detected"
        
        if not CIRCUIT_GEN_AVAILABLE:
            return False, "Circuit generation not available"
        
        current_circuit = circuit_gen.get_current_circuit()
        if not current_circuit:
            return False, "No active circuit found. Please generate a circuit first."
        
        # Get PCB requirements
        pcb_requirements = self.get_pcb_requirements(current_circuit.name)
        
        if "error" in pcb_requirements:
            return False, pcb_requirements["error"]
        
        complexity = pcb_requirements["complexity"]
        recommended_layers = complexity["recommended_layers"]
        
        # Prepare response based on layer requirements
        if recommended_layers > 2:
            layer_recommendation = f"""
🎯 **PCB Layout Transition for {current_circuit.name}**

**Layer Recommendation:**
I recommend using **{recommended_layers} copper layers** for this design because:
"""
            
            for requirement in complexity["special_requirements"][:3]:
                layer_recommendation += f"  • {requirement}\n"
            
            layer_recommendation += f"""
**Benefits of {recommended_layers}-layer design:**
  • Better signal integrity and noise reduction
  • Improved power distribution
  • Controlled impedance for high-speed signals
  • Better thermal management

**Manufacturing Impact:**
  • Cost: ~{recommended_layers//2}x compared to 2-layer
  • Lead time: +2-3 days
  • Complexity: {complexity['complexity_level']}

🤔 **Shall I proceed with the {recommended_layers}-layer PCB layout?**
"""
            
            return True, layer_recommendation
        
        else:
            # Simple 2-layer design
            success, layout_instructions = self.create_pcb_layout(current_circuit.name, 2)
            if success:
                return True, f"✅ **Starting 2-layer PCB layout!**\n\n{layout_instructions}"
            else:
                return False, f"Failed to create PCB layout: {layout_instructions}"
    
    def handle_layer_approval(self, user_message: str) -> Tuple[bool, str]:
        """Handle user approval for recommended layer count"""
        message_lower = user_message.lower()
        
        # Check for approval
        approval_keywords = ["yes", "proceed", "ok", "agree", "go ahead", "continue"]
        approved = any(keyword in message_lower for keyword in approval_keywords)
        
        if not approved:
            return False, "Layer recommendation not approved"
        
        if not CIRCUIT_GEN_AVAILABLE:
            return False, "Circuit generation not available"
        
        current_circuit = circuit_gen.get_current_circuit()
        if not current_circuit:
            return False, "No active circuit found"
        
        # Create PCB with recommended layers
        success, layout_result = self.create_pcb_layout(current_circuit.name, current_circuit.estimated_layers)
        
        if success:
            return True, f"✅ **PCB Layout Created!**\n\n{layout_result}"
        else:
            return False, f"Failed to create PCB layout: {layout_result}"
