#!/usr/bin/env python3
"""
Text Formatting Utilities
Advanced text formatting for medical reports
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime

class MedicalTextFormatter:
    """Format medical transcription text for professional reports"""
    
    def __init__(self):
        self.report_sections = [
            'INDICATION',
            'TECHNIQUE', 
            'COMPARISON',
            'FINDINGS',
            'IMPRESSION',
            'RECOMMENDATION',
            'ADDENDUM'
        ]
        
        # Medical report templates
        self.templates = {
            'ct_chest': self._ct_chest_template(),
            'mri_brain': self._mri_brain_template(),
            'ultrasound_abdomen': self._ultrasound_abdomen_template()
        }
    
    def format_medical_report(self, raw_text: str, 
                             report_type: str = 'general') -> str:
        """Format raw transcription into structured medical report"""
        
        # Clean and prepare text
        cleaned_text = self._clean_transcription(raw_text)
        
        # Apply medical formatting
        formatted_text = self._apply_medical_formatting(cleaned_text)
        
        # Structure into sections
        structured_text = self._structure_report_sections(formatted_text)
        
        # Apply final formatting
        final_text = self._apply_final_formatting(structured_text, report_type)
        
        return final_text
    
    def _clean_transcription(self, text: str) -> str:
        """Clean up transcription text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common transcription issues
        cleaned = re.sub(r'\bum+\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\buh+\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\berr+\b', '', cleaned, flags=re.IGNORECASE)
        
        # Fix sentence boundaries
        cleaned = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', cleaned)
        
        return cleaned.strip()
    
    def _apply_medical_formatting(self, text: str) -> str:
        """Apply medical-specific formatting rules"""
        # Format measurements consistently
        text = re.sub(r'(\d+)\s*x\s*(\d+)\s*(?:x\s*(\d+))?\s*(mm|cm)', 
                     r'\1 × \2' + r' × \3' * bool(r'\3') + r' \4', text)
        
        # Format medical abbreviations
        text = re.sub(r'\bb\.?p\.?\b', 'blood pressure', text, flags=re.IGNORECASE)
        text = re.sub(r'\bh\.?r\.?\b', 'heart rate', text, flags=re.IGNORECASE)
        
        # Format degrees
        text = re.sub(r'(\d+)\s*degrees?', r'\1°', text)
        
        # Format percentages
        text = re.sub(r'(\d+)\s*percent', r'\1%', text)
        
        return text
    
    def _structure_report_sections(self, text: str) -> Dict[str, str]:
        """Structure text into report sections"""
        sections = {}
        current_section = 'FINDINGS'  # Default section
        current_text = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            upper_line = line.upper().rstrip(':')
            if upper_line in self.report_sections:
                # Save previous section
                if current_text:
                    sections[current_section] = ' '.join(current_text)
                
                # Start new section
                current_section = upper_line
                current_text = []
            else:
                current_text.append(line)
        
        # Save last section
        if current_text:
            sections[current_section] = ' '.join(current_text)
        
        return sections
    
    def _apply_final_formatting(self, sections: Dict[str, str], 
                               report_type: str) -> str:
        """Apply final formatting to structured report"""
        formatted_lines = []
        
        # Add header
        formatted_lines.append(self._generate_report_header())
        formatted_lines.append('')
        
        # Format each section
        for section_name in self.report_sections:
            if section_name in sections and sections[section_name].strip():
                formatted_lines.append(f"{section_name}:")
                
                # Format section content
                content = self._format_section_content(
                    sections[section_name], section_name
                )
                formatted_lines.append(content)
                formatted_lines.append('')
        
        return '\n'.join(formatted_lines)
    
    def _format_section_content(self, content: str, section_name: str) -> str:
        """Format content within a specific section"""
        # Ensure proper sentence capitalization
        sentences = content.split('. ')
        formatted_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                formatted_sentences.append(sentence)
        
        formatted_content = '. '.join(formatted_sentences)
        
        # Ensure proper ending punctuation
        if formatted_content and not formatted_content.endswith(('.', '!', '?')):
            formatted_content += '.'
        
        return formatted_content
    
    def _generate_report_header(self) -> str:
        """Generate report header with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"RADIOLOGY REPORT\nGenerated: {timestamp}"
    
    def _ct_chest_template(self) -> str:
        """CT chest report template"""
        return """
TECHNIQUE:
CT of the chest was performed without IV contrast.

COMPARISON:
[Comparison studies]

FINDINGS:
[Detailed findings]

IMPRESSION:
[Summary and impression]
"""
    
    def _mri_brain_template(self) -> str:
        """MRI brain report template"""
        return """
TECHNIQUE:
MRI of the brain was performed with and without gadolinium contrast.

COMPARISON:
[Comparison studies]

FINDINGS:
[Detailed findings]

IMPRESSION:
[Summary and impression]
"""
    
    def _ultrasound_abdomen_template(self) -> str:
        """Ultrasound abdomen report template"""
        return """
TECHNIQUE:
Ultrasound examination of the abdomen was performed.

COMPARISON:
[Comparison studies]

FINDINGS:
[Detailed findings]

IMPRESSION:
[Summary and impression]
"""
    
    def apply_voice_command_formatting(self, text: str, command: str) -> str:
        """Apply formatting based on voice commands"""
        if command == 'bold':
            return f"**{text}**"
        elif command == 'italic':
            return f"*{text}*"
        elif command == 'underline':
            return f"_{text}_"
        elif command == 'bullet_list':
            lines = text.split('\n')
            return '\n'.join(f"• {line.strip()}" for line in lines if line.strip())
        elif command == 'numbered_list':
            lines = text.split('\n')
            return '\n'.join(f"{i+1}. {line.strip()}" 
                           for i, line in enumerate(lines) if line.strip())
        
        return text