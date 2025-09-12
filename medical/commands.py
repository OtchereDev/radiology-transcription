#!/usr/bin/env python3
"""
Voice Command Processing for Radiology Transcription
Handles formatting commands, corrections, and navigation
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class VoiceCommandProcessor:
    """Process voice commands for formatting and corrections"""
    
    def __init__(self):
        self.formatting_commands = self._build_formatting_commands()
        self.correction_commands = self._build_correction_commands()
        self.navigation_commands = self._build_navigation_commands()
        self.report_structure_commands = self._build_report_structure_commands()
        self.command_history = []
        self.text_history = []
        
    def _build_formatting_commands(self):
        """Text formatting voice commands"""
        return {
            'bold': {
                'triggers': ['bold that', 'make that bold', 'bold the last sentence', 'bold previous'],
                'action': 'bold',
                'target': 'previous_text'
            },
            'italic': {
                'triggers': ['italicize that', 'make that italic', 'italic the last sentence', 'italics'],
                'action': 'italic',
                'target': 'previous_text'
            },
            'underline': {
                'triggers': ['underline that', 'make that underlined', 'underline the last sentence'],
                'action': 'underline',
                'target': 'previous_text'
            },
            'new_paragraph': {
                'triggers': ['new paragraph', 'paragraph break', 'start new paragraph'],
                'action': 'paragraph_break',
                'target': 'cursor_position'
            },
            'new_line': {
                'triggers': ['new line', 'line break', 'next line'],
                'action': 'line_break',
                'target': 'cursor_position'
            },
            'bullet_list': {
                'triggers': ['make list', 'bullet list', 'create bullet points', 'bulleted list'],
                'action': 'bullet_list',
                'target': 'previous_text'
            },
            'numbered_list': {
                'triggers': ['numbered list', 'make numbered list', 'create numbers', 'number that'],
                'action': 'numbered_list',
                'target': 'previous_text'
            },
            'insert_table': {
                'triggers': ['insert table', 'create table', 'make table', 'add table'],
                'action': 'insert_table',
                'target': 'cursor_position'
            },
            'capitalize': {
                'triggers': ['capitalize that', 'make that capital', 'uppercase that'],
                'action': 'capitalize',
                'target': 'previous_text'
            },
            'lowercase': {
                'triggers': ['lowercase that', 'make that lowercase'],
                'action': 'lowercase',
                'target': 'previous_text'
            }
        }
    
    def _build_correction_commands(self):
        """Voice commands for corrections"""
        return {
            'scratch_that': {
                'triggers': ['scratch that', 'delete that', 'remove that', 'cancel that'],
                'action': 'delete_previous',
                'target': 'previous_sentence'
            },
            'scratch_all': {
                'triggers': ['scratch everything', 'delete all', 'clear all', 'start over'],
                'action': 'delete_all',
                'target': 'entire_text'
            },
            'undo': {
                'triggers': ['undo', 'undo that', 'go back', 'reverse that'],
                'action': 'undo',
                'target': 'last_action'
            },
            'select_previous': {
                'triggers': ['select previous sentence', 'select that', 'highlight previous'],
                'action': 'select',
                'target': 'previous_sentence'
            },
            'select_word': {
                'triggers': ['select previous word', 'select that word', 'select last word'],
                'action': 'select',
                'target': 'previous_word'
            },
            'replace_with': {
                'triggers': ['replace that with', 'change that to', 'substitute with'],
                'action': 'replace',
                'target': 'previous_text',
                'requires_followup': True
            },
            'spell_that': {
                'triggers': ['spell that', 'spell out', 'letter by letter'],
                'action': 'spell_mode',
                'target': 'next_input'
            }
        }
    
    def _build_navigation_commands(self):
        """Navigation and cursor movement commands"""
        return {
            'go_to_beginning': {
                'triggers': ['go to beginning', 'go to start', 'beginning of document'],
                'action': 'move_cursor',
                'target': 'document_start'
            },
            'go_to_end': {
                'triggers': ['go to end', 'end of document', 'go to bottom'],
                'action': 'move_cursor',
                'target': 'document_end'
            },
            'move_up': {
                'triggers': ['move up', 'go up', 'previous line'],
                'action': 'move_cursor',
                'target': 'up'
            },
            'move_down': {
                'triggers': ['move down', 'go down', 'next line'],
                'action': 'move_cursor',
                'target': 'down'
            },
            'next_section': {
                'triggers': ['next section', 'go to next section', 'next finding'],
                'action': 'navigate',
                'target': 'next_section'
            },
            'previous_section': {
                'triggers': ['previous section', 'go to previous section', 'last section'],
                'action': 'navigate',
                'target': 'previous_section'
            }
        }
    
    def _build_report_structure_commands(self):
        """Commands for radiology report structure"""
        return {
            'new_section': {
                'triggers': ['new section', 'next section', 'add section'],
                'action': 'create_section',
                'target': 'cursor_position',
                'requires_followup': True  # Need to specify section name
            },
            'impression': {
                'triggers': ['impression', 'impression colon', 'start impression'],
                'action': 'create_section',
                'target': 'cursor_position',
                'section_name': 'IMPRESSION'
            },
            'findings': {
                'triggers': ['findings', 'findings colon', 'start findings'],
                'action': 'create_section',
                'target': 'cursor_position',
                'section_name': 'FINDINGS'
            },
            'technique': {
                'triggers': ['technique', 'technique colon', 'start technique'],
                'action': 'create_section',
                'target': 'cursor_position',
                'section_name': 'TECHNIQUE'
            },
            'comparison': {
                'triggers': ['comparison', 'comparison colon', 'start comparison'],
                'action': 'create_section',
                'target': 'cursor_position',
                'section_name': 'COMPARISON'
            },
            'indication': {
                'triggers': ['indication', 'indication colon', 'start indication'],
                'action': 'create_section',
                'target': 'cursor_position',
                'section_name': 'INDICATION'
            },
            'recommendation': {
                'triggers': ['recommendation', 'recommendations', 'recommend'],
                'action': 'create_section',
                'target': 'cursor_position',
                'section_name': 'RECOMMENDATION'
            }
        }
    
    def process_command(self, text: str, current_document: str = "") -> Dict:
        """Process voice command and return action"""
        text_lower = text.lower().strip()
        
        # Check all command categories
        all_commands = {
            **self.formatting_commands,
            **self.correction_commands,
            **self.navigation_commands,
            **self.report_structure_commands
        }
        
        for command_name, command_info in all_commands.items():
            for trigger in command_info['triggers']:
                if self._matches_command(text_lower, trigger):
                    command_result = self._execute_command(
                        command_name, command_info, text, current_document
                    )
                    
                    # Log command for history
                    self.command_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'command': command_name,
                        'trigger': trigger,
                        'original_text': text,
                        'result': command_result
                    })
                    
                    return command_result
        
        # If no command found, return empty result
        return {'command_found': False, 'original_text': text}
    
    def _matches_command(self, text: str, trigger: str) -> bool:
        """Check if text matches a command trigger"""
        # Exact match
        if text == trigger:
            return True
        
        # Check if text starts with the trigger
        if text.startswith(trigger):
            return True
        
        # Check for variations with punctuation
        trigger_words = trigger.split()
        text_words = text.split()
        
        if len(trigger_words) <= len(text_words):
            # Check if first N words match the trigger
            if text_words[:len(trigger_words)] == trigger_words:
                return True
        
        return False
    
    def _execute_command(self, command_name: str, command_info: Dict, 
                        original_text: str, current_document: str) -> Dict:
        """Execute the specified command"""
        
        result = {
            'command_found': True,
            'command_name': command_name,
            'action': command_info['action'],
            'target': command_info['target'],
            'original_text': original_text,
            'formatted_output': '',
            'cursor_instruction': '',
            'requires_followup': command_info.get('requires_followup', False)
        }
        
        action = command_info['action']
        
        if action == 'bold':
            result['formatted_output'] = self._apply_bold_formatting(current_document)
            result['cursor_instruction'] = 'Apply bold formatting to previous sentence'
            
        elif action == 'italic':
            result['formatted_output'] = self._apply_italic_formatting(current_document)
            result['cursor_instruction'] = 'Apply italic formatting to previous sentence'
            
        elif action == 'underline':
            result['formatted_output'] = self._apply_underline_formatting(current_document)
            result['cursor_instruction'] = 'Apply underline formatting to previous sentence'
            
        elif action == 'paragraph_break':
            result['formatted_output'] = current_document + '\n\n'
            result['cursor_instruction'] = 'Insert paragraph break'
            
        elif action == 'line_break':
            result['formatted_output'] = current_document + '\n'
            result['cursor_instruction'] = 'Insert line break'
            
        elif action == 'bullet_list':
            result['formatted_output'] = self._convert_to_bullet_list(current_document)
            result['cursor_instruction'] = 'Convert previous text to bullet list'
            
        elif action == 'numbered_list':
            result['formatted_output'] = self._convert_to_numbered_list(current_document)
            result['cursor_instruction'] = 'Convert previous text to numbered list'
            
        elif action == 'insert_table':
            result['formatted_output'] = current_document + self._create_basic_table()
            result['cursor_instruction'] = 'Insert basic table template'
            
        elif action == 'capitalize':
            result['formatted_output'] = self._apply_capitalization(current_document)
            result['cursor_instruction'] = 'Capitalize previous text'
            
        elif action == 'lowercase':
            result['formatted_output'] = self._apply_lowercase(current_document)
            result['cursor_instruction'] = 'Convert previous text to lowercase'
            
        elif action == 'delete_previous':
            result['formatted_output'] = self._delete_previous_sentence(current_document)
            result['cursor_instruction'] = 'Delete previous sentence'
            
        elif action == 'delete_all':
            result['formatted_output'] = ''
            result['cursor_instruction'] = 'Clear all text'
            
        elif action == 'create_section':
            section_name = command_info.get('section_name', 'NEW SECTION')
            result['formatted_output'] = current_document + f'\n\n{section_name}:\n'
            result['cursor_instruction'] = f'Create {section_name} section'
            
        elif action == 'replace':
            # This requires followup input
            result['awaiting_replacement'] = True
            result['cursor_instruction'] = 'Waiting for replacement text'
            
        return result
    
    def _apply_bold_formatting(self, text: str) -> str:
        """Apply bold formatting to last sentence"""
        sentences = text.split('.')
        if len(sentences) > 1:
            last_sentence = sentences[-2].strip()  # -1 is usually empty after the period
            bold_sentence = f"**{last_sentence}**"
            sentences[-2] = bold_sentence
            return '.'.join(sentences)
        return f"**{text}**"
    
    def _apply_italic_formatting(self, text: str) -> str:
        """Apply italic formatting to last sentence"""
        sentences = text.split('.')
        if len(sentences) > 1:
            last_sentence = sentences[-2].strip()
            italic_sentence = f"*{last_sentence}*"
            sentences[-2] = italic_sentence
            return '.'.join(sentences)
        return f"*{text}*"
    
    def _apply_underline_formatting(self, text: str) -> str:
        """Apply underline formatting to last sentence"""
        sentences = text.split('.')
        if len(sentences) > 1:
            last_sentence = sentences[-2].strip()
            underline_sentence = f"_{last_sentence}_"
            sentences[-2] = underline_sentence
            return '.'.join(sentences)
        return f"_{text}_"
    
    def _convert_to_bullet_list(self, text: str) -> str:
        """Convert text to bullet list"""
        lines = text.strip().split('\n')
        bullet_lines = []
        for line in lines:
            if line.strip():
                sentences = line.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence:
                        bullet_lines.append(f"• {sentence}")
        return '\n'.join(bullet_lines)
    
    def _convert_to_numbered_list(self, text: str) -> str:
        """Convert text to numbered list"""
        lines = text.strip().split('\n')
        numbered_lines = []
        counter = 1
        for line in lines:
            if line.strip():
                sentences = line.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence:
                        numbered_lines.append(f"{counter}. {sentence}")
                        counter += 1
        return '\n'.join(numbered_lines)
    
    def _create_basic_table(self) -> str:
        """Create a basic table template"""
        return """
| Finding | Location | Size | Characteristics |
|---------|----------|------|----------------|
|         |          |      |                |
|         |          |      |                |
"""
    
    def _apply_capitalization(self, text: str) -> str:
        """Capitalize last sentence"""
        sentences = text.split('.')
        if len(sentences) > 1:
            last_sentence = sentences[-2].strip()
            sentences[-2] = last_sentence.upper()
            return '.'.join(sentences)
        return text.upper()
    
    def _apply_lowercase(self, text: str) -> str:
        """Convert last sentence to lowercase"""
        sentences = text.split('.')
        if len(sentences) > 1:
            last_sentence = sentences[-2].strip()
            sentences[-2] = last_sentence.lower()
            return '.'.join(sentences)
        return text.lower()
    
    def _delete_previous_sentence(self, text: str) -> str:
        """Delete the last sentence"""
        sentences = text.split('.')
        if len(sentences) > 2:  # Keep at least one sentence
            return '.'.join(sentences[:-2]) + '.'
        return ""
    
    def get_command_history(self) -> List[Dict]:
        """Get command history"""
        return self.command_history
    
    def get_available_commands(self) -> Dict:
        """Get list of available commands"""
        commands_list = {}
        
        categories = {
            'Formatting': self.formatting_commands,
            'Corrections': self.correction_commands,
            'Navigation': self.navigation_commands,
            'Report Structure': self.report_structure_commands
        }
        
        for category, commands in categories.items():
            commands_list[category] = {}
            for command_name, command_info in commands.items():
                commands_list[category][command_name] = {
                    'triggers': command_info['triggers'],
                    'description': f"Action: {command_info['action']}, Target: {command_info['target']}"
                }
        
        return commands_list
    
    def get_command_stats(self) -> Dict:
        """Get statistics about available commands"""
        return {
            'formatting_commands': len(self.formatting_commands),
            'correction_commands': len(self.correction_commands),
            'navigation_commands': len(self.navigation_commands),
            'report_structure_commands': len(self.report_structure_commands),
            'total_commands': len(self.formatting_commands) + len(self.correction_commands) + 
                            len(self.navigation_commands) + len(self.report_structure_commands),
            'commands_executed': len(self.command_history)
        }