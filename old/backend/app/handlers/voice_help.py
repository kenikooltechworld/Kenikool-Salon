"""
Voice Assistant Help and Tutorial System
Provides contextual help and tutorials for users
"""

import logging
from typing import Dict, Any, List, Optional
from app.models.voice_models import Intent

logger = logging.getLogger(__name__)


class VoiceHelpSystem:
    """Manages help content and tutorials"""
    
    # Multilingual help content
    HELP_CONTENT = {
        'en': {
            'welcome': "Welcome to the Voice Assistant! I can help you manage bookings, clients, inventory, staff, and more. Say 'help' anytime for assistance.",
            'getting_started': "To get started, try saying: 'Show today's appointments' or 'Book a client'",
            'categories': {
                'bookings': "For bookings, you can say:\n- Book [client] for [service]\n- Cancel [client]'s appointment\n- Show today's appointments",
                'clients': "For clients, you can say:\n- Add new client [name]\n- Show [client]'s history\n- Find inactive clients",
                'inventory': "For inventory, you can say:\n- What products are low\n- How much [product] do I have\n- Add [quantity] [product]",
                'staff': "For staff, you can say:\n- Show [stylist]'s schedule\n- Who's available at [time]\n- Mark [stylist] as present",
                'finance': "For finances, you can say:\n- Show today's revenue\n- Show this week's revenue\n- Show analytics"
            }
        },
        'yo': {
            'welcome': "Ẹ káàbọ̀ sí Olùrànlọ́wọ́ Ohùn! Mo lè ràn ọ́ lọ́wọ́ láti ṣàkóso àwọn ìdápọ̀, àwọn oníbàárà, ohun èlò, àwọn oṣìṣẹ́, àti púpọ̀ síi. Sọ 'ìrànlọ́wọ́' nígbàkúgbà fún ìrànlọ́wọ́.",
            'getting_started': "Láti bẹ̀rẹ̀, gbìyànjú láti sọ: 'Fi àwọn ìdápọ̀ òní hàn' tàbí 'Ṣe ìdápọ̀ oníbàárà kan'",
            'categories': {
                'bookings': "Fún àwọn ìdápọ̀:\n- Ṣe ìdápọ̀ [oníbàárà] fún [iṣẹ́]\n- Fagilee ìdápọ̀ [oníbàárà]\n- Fi àwọn ìdápọ̀ òní hàn",
                'clients': "Fún àwọn oníbàárà:\n- Fikún oníbàárà tuntun [orúkọ]\n- Fi ìtàn [oníbàárà] hàn\n- Wá àwọn oníbàárà tí kò ṣiṣẹ́",
                'inventory': "Fún ohun èlò:\n- Àwọn ọjà wo ló kéré\n- Elo [ọjà] ni mo ní\n- Fikún [iye] [ọjà]",
                'staff': "Fún àwọn oṣìṣẹ́:\n- Fi ìṣètò [oṣìṣẹ́] hàn\n- Tani ó wà ní [àkókò]\n- Samisi [oṣìṣẹ́] bí ó wà",
                'finance': "Fún owó:\n- Fi owó wiwọlé òní hàn\n- Fi owó ọ̀sẹ̀ yìí hàn\n- Fi àwọn ìṣirò hàn"
            }
        },
        'ig': {
            'welcome': "Nnọọ na Voice Assistant! Enwere m ike inyere gị aka ijikwa ndebe, ndị ahịa, ngwaahịa, ndị ọrụ, na ndị ọzọ. Kwuo 'enyemaka' mgbe ọ bụla maka enyemaka.",
            'getting_started': "Iji malite, gbalịa ikwu: 'Gosi nhọpụta taa' ma ọ bụ 'Debe onye ahịa'",
            'categories': {
                'bookings': "Maka ndebe:\n- Debe [onye ahịa] maka [ọrụ]\n- Kagbuo nhọpụta [onye ahịa]\n- Gosi nhọpụta taa",
                'clients': "Maka ndị ahịa:\n- Tinye onye ahịa ọhụrụ [aha]\n- Gosi akụkọ [onye ahịa]\n- Chọta ndị ahịa na-adịghị arụ ọrụ",
                'inventory': "Maka ngwaahịa:\n- Ngwaahịa ole dị ala\n- Ole [ngwaahịa] m nwere\n- Tinye [ọnụọgụgụ] [ngwaahịa]",
                'staff': "Maka ndị ọrụ:\n- Gosi nhazi [onye ọrụ]\n- Onye dị na [oge]\n- Kaa [onye ọrụ] dịka ọ nọ",
                'finance': "Maka ego:\n- Gosi ego taa\n- Gosi ego izu a\n- Gosi nyocha"
            }
        },
        'ha': {
            'welcome': "Barka da zuwa Voice Assistant! Zan iya taimaka muku wajen sarrafa alƙawari, abokan ciniki, kayayyaki, ma'aikata, da sauransu. Ku ce 'taimako' kowane lokaci don samun taimako.",
            'getting_started': "Don farawa, gwada cewa: 'Nuna alƙawaran yau' ko 'Yi wa abokin ciniki alƙawari'",
            'categories': {
                'bookings': "Don alƙawari:\n- Yi wa [abokin ciniki] alƙawari don [aiki]\n- Soke alƙawarin [abokin ciniki]\n- Nuna alƙawaran yau",
                'clients': "Don abokan ciniki:\n- Ƙara sabon abokin ciniki [suna]\n- Nuna tarihin [abokin ciniki]\n- Nemo abokan ciniki marasa aiki",
                'inventory': "Don kayayyaki:\n- Waɗanne kayayyaki suke ƙasa\n- Nawa [kayayyaki] nake da shi\n- Ƙara [adadi] [kayayyaki]",
                'staff': "Don ma'aikata:\n- Nuna jadawalin [ma'aikaci]\n- Wane ne yake a [lokaci]\n- Yi wa [ma'aikaci] alama yana nan",
                'finance': "Don kuɗi:\n- Nuna kudin shiga na yau\n- Nuna kudin mako\n- Nuna bincike"
            }
        },
        'pcm': {
            'welcome': "Welcome to Voice Assistant! I fit help you manage bookings, customers, inventory, staff, and more. Talk 'help' anytime for assistance.",
            'getting_started': "To start, try talk: 'Show today appointments' or 'Book customer'",
            'categories': {
                'bookings': "For bookings:\n- Book [customer] for [service]\n- Cancel [customer] appointment\n- Show today appointments",
                'clients': "For customers:\n- Add new customer [name]\n- Show [customer] history\n- Find customers wey no dey come",
                'inventory': "For inventory:\n- Which products don low\n- How much [product] we get\n- Add [quantity] [product]",
                'staff': "For staff:\n- Show [stylist] schedule\n- Who dey available for [time]\n- Mark [stylist] say e don come",
                'finance': "For money:\n- Show today money\n- Show this week money\n- Show analytics"
            }
        }
    }
    
    @classmethod
    def get_welcome_message(cls, language: str = 'en') -> str:
        """Get welcome message"""
        return cls.HELP_CONTENT.get(language, cls.HELP_CONTENT['en'])['welcome']
    
    @classmethod
    def get_getting_started(cls, language: str = 'en') -> str:
        """Get getting started message"""
        return cls.HELP_CONTENT.get(language, cls.HELP_CONTENT['en'])['getting_started']
    
    @classmethod
    def get_category_help(cls, category: str, language: str = 'en') -> str:
        """Get help for specific category"""
        content = cls.HELP_CONTENT.get(language, cls.HELP_CONTENT['en'])
        return content['categories'].get(category, "Category not found")
    
    @classmethod
    def get_all_help(cls, language: str = 'en') -> str:
        """Get comprehensive help"""
        content = cls.HELP_CONTENT.get(language, cls.HELP_CONTENT['en'])
        
        help_text = content['welcome'] + "\n\n"
        help_text += content['getting_started'] + "\n\n"
        
        for category, text in content['categories'].items():
            help_text += f"\n{text}\n"
        
        return help_text


class ContextualHelp:
    """Provides contextual help based on user situation"""
    
    @staticmethod
    def get_contextual_help(
        intent: Optional[Intent],
        error_type: Optional[str],
        language: str = 'en'
    ) -> str:
        """
        Get contextual help based on situation
        
        Args:
            intent: Current intent
            error_type: Type of error if any
            language: Language code
            
        Returns:
            Contextual help message
        """
        if error_type:
            return ContextualHelp._get_error_help(error_type, language)
        
        if intent:
            return ContextualHelp._get_intent_help(intent, language)
        
        return VoiceHelpSystem.get_welcome_message(language)
    
    @staticmethod
    def _get_error_help(error_type: str, language: str) -> str:
        """Get help for error situation"""
        error_help = {
            'en': {
                'missing_info': "I need more information. Try providing the client name, service, and date.",
                'not_found': "I couldn't find that. Try checking the spelling or use a different name.",
                'permission': "You don't have permission for that action. Contact your administrator."
            },
            'yo': "Mo nilo alaye diẹ sii",
            'ig': "Achọrọ m ozi ndị ọzọ",
            'ha': "Ina buƙatar ƙarin bayani",
            'pcm': "I need more information"
        }
        
        if language == 'en':
            return error_help['en'].get(error_type, "An error occurred. Try rephrasing your request.")
        
        return error_help.get(language, error_help['en'])
    
    @staticmethod
    def _get_intent_help(intent: Intent, language: str) -> str:
        """Get help for specific intent"""
        intent_help = {
            Intent.BOOK_APPOINTMENT: {
                'en': "To book an appointment, say: 'Book [client name] for [service] with [stylist] on [date] at [time]'",
                'yo': "Láti ṣe ìdápọ̀, sọ: 'Ṣe ìdápọ̀ [orúkọ oníbàárà] fún [iṣẹ́] pẹ̀lú [oṣìṣẹ́] ní [ọjọ́] ní [àkókò]'",
                'ig': "Iji debe nhọpụta, kwuo: 'Debe [aha onye ahịa] maka [ọrụ] na [onye ọrụ] na [ụbọchị] na [oge]'",
                'ha': "Don yi alƙawari, ku ce: 'Yi wa [sunan abokin ciniki] alƙawari don [aiki] da [ma'aikaci] a [rana] da [lokaci]'",
                'pcm': "To book appointment, talk: 'Book [customer name] for [service] with [stylist] on [date] at [time]'"
            }
        }
        
        return intent_help.get(intent, {}).get(language, VoiceHelpSystem.get_welcome_message(language))


class TutorialSystem:
    """Interactive tutorial system"""
    
    TUTORIALS = {
        'first_booking': {
            'name': 'Your First Booking',
            'steps': [
                {
                    'instruction': "Let's book your first appointment. Say: 'Book a client'",
                    'expected_intent': Intent.BOOK_APPOINTMENT
                },
                {
                    'instruction': "Great! Now provide the client name",
                    'field': 'client'
                },
                {
                    'instruction': "Perfect! What service do they want?",
                    'field': 'service'
                },
                {
                    'instruction': "Excellent! You've created your first booking!",
                    'complete': True
                }
            ]
        },
        'check_revenue': {
            'name': 'Checking Revenue',
            'steps': [
                {
                    'instruction': "Let's check your revenue. Say: 'Show today's revenue'",
                    'expected_intent': Intent.SHOW_REVENUE
                },
                {
                    'instruction': "Great! You can also say 'Show this week's revenue' or 'Show this month's revenue'",
                    'complete': True
                }
            ]
        }
    }
    
    @classmethod
    def get_tutorial(cls, tutorial_name: str) -> Dict[str, Any]:
        """Get tutorial by name"""
        return cls.TUTORIALS.get(tutorial_name)
    
    @classmethod
    def list_tutorials(cls) -> List[Dict[str, str]]:
        """List all available tutorials"""
        return [
            {'name': name, 'title': tutorial['name']}
            for name, tutorial in cls.TUTORIALS.items()
        ]
    
    @classmethod
    def get_tutorial_step(cls, tutorial_name: str, step: int) -> Optional[Dict[str, Any]]:
        """Get specific tutorial step"""
        tutorial = cls.TUTORIALS.get(tutorial_name)
        if not tutorial or step >= len(tutorial['steps']):
            return None
        
        return tutorial['steps'][step]


class CommandSuggestions:
    """Suggests commands based on context"""
    
    @staticmethod
    def get_suggestions(
        time_of_day: str,
        recent_intents: List[Intent],
        language: str = 'en'
    ) -> List[str]:
        """
        Get command suggestions based on context
        
        Args:
            time_of_day: morning, afternoon, evening
            recent_intents: Recently used intents
            language: Language code
            
        Returns:
            List of suggested commands
        """
        suggestions = {
            'morning': {
                'en': [
                    "Show today's appointments",
                    "Check inventory",
                    "Show staff schedule"
                ],
                'yo': [
                    "Fi àwọn ìdápọ̀ òní hàn",
                    "Ṣayẹwo ohun èlò",
                    "Fi ìṣètò oṣìṣẹ́ hàn"
                ]
            },
            'evening': {
                'en': [
                    "Daily summary",
                    "Show today's revenue",
                    "End of day"
                ],
                'yo': [
                    "Akopọ ọjọ",
                    "Fi owó wiwọlé òní hàn",
                    "Ìparí ọjọ́"
                ]
            }
        }
        
        return suggestions.get(time_of_day, {}).get(language, suggestions['morning']['en'])
