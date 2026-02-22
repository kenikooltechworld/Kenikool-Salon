"""
Voice Command Shortcuts
Quick shortcuts for common salon operations
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from app.models.voice_models import Intent, ActionResult

logger = logging.getLogger(__name__)


class VoiceShortcuts:
    """Manages voice command shortcuts"""
    
    # Shortcut definitions with multilingual triggers
    SHORTCUTS = {
        'quick_book': {
            'triggers': {
                'en': ['quick book', 'fast book', 'quick booking'],
                'yo': ['booking iyara', 'ṣe booking kiakia'],
                'ig': ['booking ngwa ngwa', 'debe ngwa'],
                'ha': ['booking mai sauri', 'yi booking da sauri'],
                'pcm': ['quick booking', 'book sharp sharp']
            },
            'intent': Intent.QUICK_BOOK,
            'description': 'Start quick booking flow'
        },
        'daily_summary': {
            'triggers': {
                'en': ['daily summary', 'today summary', 'end of day'],
                'yo': ['akopọ ọjọ', 'akopọ oni', 'ipari ọjọ'],
                'ig': ['nchịkọta ụbọchị', 'nchịkọta taa'],
                'ha': ['taƙaitaccen yau', 'ƙarshen rana'],
                'pcm': ['daily summary', 'today summary']
            },
            'intent': Intent.DAILY_SUMMARY,
            'description': 'Get comprehensive daily report'
        },
        'emergency_cancel': {
            'triggers': {
                'en': ['emergency cancel', 'cancel now', 'urgent cancel'],
                'yo': ['fagilee pajawiri', 'fagilee ni bayi'],
                'ig': ['kagbuo mberede', 'kagbuo ugbu a'],
                'ha': ['soke gaggawa', 'soke yanzu'],
                'pcm': ['cancel sharp sharp', 'cancel now now']
            },
            'intent': Intent.EMERGENCY_CANCEL,
            'description': 'Cancel next appointment immediately'
        },
        'check_in': {
            'triggers': {
                'en': ['check in', 'client arrived', 'mark arrived'],
                'yo': ['ṣayẹwo wọle', 'alabara ti de'],
                'ig': ['nyochaa n\'ime', 'onye ahịa abịala'],
                'ha': ['duba ciki', 'abokin ciniki ya zo'],
                'pcm': ['check in', 'customer don reach']
            },
            'intent': Intent.CHECK_IN,
            'description': 'Check in arriving client'
        },
        'end_of_day': {
            'triggers': {
                'en': ['end of day', 'close day', 'daily closing'],
                'yo': ['ipari ọjọ', 'ti ọjọ'],
                'ig': ['njedebe ụbọchị', 'mechie ụbọchị'],
                'ha': ['ƙarshen rana', 'rufe rana'],
                'pcm': ['end of day', 'close for today']
            },
            'intent': Intent.END_OF_DAY,
            'description': 'Generate end of day report'
        }
    }
    
    @classmethod
    def detect_shortcut(cls, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Detect if text contains a shortcut trigger
        
        Args:
            text: User input text
            language: Language code
            
        Returns:
            Shortcut info or None
        """
        text_lower = text.lower().strip()
        
        for shortcut_name, shortcut_data in cls.SHORTCUTS.items():
            triggers = shortcut_data['triggers'].get(language, [])
            
            for trigger in triggers:
                if trigger in text_lower:
                    logger.info(f"Detected shortcut: {shortcut_name} ({language})")
                    return {
                        'name': shortcut_name,
                        'intent': shortcut_data['intent'],
                        'description': shortcut_data['description'],
                        'trigger': trigger
                    }
        
        return None
    
    @classmethod
    def get_all_shortcuts(cls, language: str = 'en') -> List[Dict[str, Any]]:
        """
        Get all available shortcuts for language
        
        Args:
            language: Language code
            
        Returns:
            List of shortcuts
        """
        shortcuts = []
        
        for shortcut_name, shortcut_data in cls.SHORTCUTS.items():
            triggers = shortcut_data['triggers'].get(language, [])
            shortcuts.append({
                'name': shortcut_name,
                'triggers': triggers,
                'description': shortcut_data['description'],
                'intent': shortcut_data['intent'].value
            })
        
        return shortcuts
    
    @classmethod
    def get_shortcut_help(cls, language: str = 'en') -> str:
        """
        Get help text for shortcuts
        
        Args:
            language: Language code
            
        Returns:
            Help text
        """
        help_texts = {
            'en': "Available shortcuts:\n",
            'yo': "Awọn itọsọna to wa:\n",
            'ig': "Ụzọ mkpirisi dị:\n",
            'ha': "Gajerun hanyoyi masu samuwa:\n",
            'pcm': "Shortcuts wey dey available:\n"
        }
        
        help_text = help_texts.get(language, help_texts['en'])
        
        shortcuts = cls.get_all_shortcuts(language)
        for shortcut in shortcuts:
            triggers = ', '.join(shortcut['triggers'][:2])  # Show first 2 triggers
            help_text += f"- {triggers}: {shortcut['description']}\n"
        
        return help_text


class ShortcutFlows:
    """Manages multi-step shortcut flows"""
    
    @staticmethod
    async def quick_book_flow(
        context: Dict[str, Any],
        step: int = 0
    ) -> Dict[str, Any]:
        """
        Quick booking flow
        
        Args:
            context: Flow context
            step: Current step
            
        Returns:
            Flow state
        """
        steps = [
            {
                'prompt': 'Who is the client?',
                'field': 'client',
                'next': 1
            },
            {
                'prompt': 'What service?',
                'field': 'service',
                'next': 2
            },
            {
                'prompt': 'Which stylist?',
                'field': 'stylist',
                'next': 3
            },
            {
                'prompt': 'What date and time?',
                'field': 'datetime',
                'next': 'complete'
            }
        ]
        
        if step >= len(steps):
            return {
                'complete': True,
                'data': context
            }
        
        current_step = steps[step]
        
        return {
            'complete': False,
            'prompt': current_step['prompt'],
            'field': current_step['field'],
            'next_step': current_step['next'],
            'context': context
        }
    
    @staticmethod
    def get_flow_prompts(flow_name: str, language: str = 'en') -> List[str]:
        """
        Get prompts for a flow in specified language
        
        Args:
            flow_name: Flow name
            language: Language code
            
        Returns:
            List of prompts
        """
        prompts = {
            'quick_book': {
                'en': [
                    'Who is the client?',
                    'What service?',
                    'Which stylist?',
                    'What date and time?'
                ],
                'yo': [
                    'Tani alabara naa?',
                    'Iru iṣẹ wo?',
                    'Oṣiṣẹ wo?',
                    'Ọjọ ati akoko wo?'
                ],
                'ig': [
                    'Onye bụ onye ahịa?',
                    'Kedu ọrụ?',
                    'Kedu onye ọrụ?',
                    'Kedu ụbọchị na oge?'
                ],
                'ha': [
                    'Wane ne abokin ciniki?',
                    'Wane aiki?',
                    'Wane ma\'aikaci?',
                    'Wane rana da lokaci?'
                ],
                'pcm': [
                    'Who be the customer?',
                    'Wetin be the service?',
                    'Which stylist?',
                    'Which day and time?'
                ]
            }
        }
        
        return prompts.get(flow_name, {}).get(language, prompts[flow_name]['en'])


class ShortcutMacros:
    """Predefined macro commands"""
    
    MACROS = {
        'morning_routine': {
            'name': 'Morning Routine',
            'commands': [
                {'intent': Intent.SHOW_APPOINTMENTS, 'entities': {'time_period': 'today'}},
                {'intent': Intent.CHECK_INVENTORY, 'entities': {}},
                {'intent': Intent.SHOW_STAFF_SCHEDULE, 'entities': {}}
            ],
            'description': 'Morning startup routine'
        },
        'end_of_day_routine': {
            'name': 'End of Day Routine',
            'commands': [
                {'intent': Intent.DAILY_SUMMARY, 'entities': {}},
                {'intent': Intent.SHOW_REVENUE, 'entities': {'time_period': 'today'}},
                {'intent': Intent.CHECK_INVENTORY, 'entities': {}}
            ],
            'description': 'End of day closing routine'
        },
        'client_check': {
            'name': 'Client Check',
            'commands': [
                {'intent': Intent.SHOW_APPOINTMENTS, 'entities': {'time_period': 'today'}},
                {'intent': Intent.FIND_INACTIVE_CLIENTS, 'entities': {'period': '30 days'}}
            ],
            'description': 'Check client status'
        }
    }
    
    @classmethod
    def get_macro(cls, macro_name: str) -> Dict[str, Any]:
        """Get macro definition"""
        return cls.MACROS.get(macro_name)
    
    @classmethod
    def list_macros(cls) -> List[Dict[str, Any]]:
        """List all available macros"""
        return [
            {
                'name': name,
                'description': macro['description'],
                'command_count': len(macro['commands'])
            }
            for name, macro in cls.MACROS.items()
        ]
