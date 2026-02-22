"""
Multilingual Response Templates
Response templates for all supported languages
"""

from typing import Dict, Any
from app.models.voice_models import Intent


class ResponseTemplates:
    """Multilingual response template generator"""
    
    # English templates
    ENGLISH_TEMPLATES = {
        Intent.BOOK_APPOINTMENT: {
            'success': "I've booked {client} for {service} on {date} at {time}",
            'success_no_time': "I've booked {client} for {service}",
            'client_not_found': "I couldn't find a client named {client}. Would you like to add them first?",
            'error': "I couldn't complete the booking. {error}"
        },
        Intent.CANCEL_APPOINTMENT: {
            'success': "I've cancelled the appointment for {client}",
            'not_found': "I couldn't find any upcoming appointments for {client}",
            'error': "I couldn't cancel the appointment. {error}"
        },
        Intent.RESCHEDULE_APPOINTMENT: {
            'success': "I've rescheduled {client}'s appointment to {date} at {time}",
            'not_found': "I couldn't find any appointments for {client}",
            'error': "I couldn't reschedule the appointment. {error}"
        },
        Intent.SHOW_APPOINTMENTS: {
            'success': "You have {count} appointments today",
            'none': "No appointments scheduled for today",
            'list': "Today's appointments: {appointments}"
        },
        Intent.ADD_CLIENT: {
            'success': "I've added {name} as a new client",
            'error': "I couldn't add the client. {error}"
        },
        Intent.SHOW_CLIENT_INFO: {
            'success': "{client} has {visits} total visits. Last visit was on {last_visit}",
            'not_found': "I couldn't find a client named {client}",
            'error': "I couldn't retrieve client information. {error}"
        },
        Intent.FIND_INACTIVE_CLIENTS: {
            'success': "I found {count} clients who haven't visited in {period}",
            'none': "All clients are active",
            'error': "I couldn't find inactive clients. {error}"
        },
        Intent.SHOW_REVENUE: {
            'success': "Revenue for {period} is ${amount}",
            'error': "I couldn't retrieve revenue information. {error}"
        },
        Intent.SHOW_ANALYTICS: {
            'success': "Total revenue: ${revenue}, Total bookings: {bookings}, Total clients: {clients}",
            'error': "I couldn't retrieve analytics. {error}"
        },
        Intent.CHECK_INVENTORY: {
            'success': "{product} has {quantity} units in stock",
            'low_stock': "{count} products are running low",
            'not_found': "I couldn't find {product} in inventory",
            'error': "I couldn't check inventory. {error}"
        },
        Intent.UPDATE_INVENTORY: {
            'success': "Updated {product} to {quantity} units",
            'error': "I couldn't update inventory. {error}"
        },
        Intent.SHOW_STAFF_SCHEDULE: {
            'success': "{stylist} has {count} appointments today",
            'not_found': "I couldn't find a stylist named {stylist}",
            'error': "I couldn't retrieve the schedule. {error}"
        },
        Intent.CHECK_AVAILABILITY: {
            'success': "{count} staff members are available: {staff}",
            'none': "No staff available at {time}",
            'error': "I couldn't check availability. {error}"
        },
        Intent.MARK_ATTENDANCE: {
            'success': "Marked {stylist} as {status}",
            'error': "I couldn't mark attendance. {error}"
        },
        Intent.SHOW_PERFORMANCE: {
            'success': "Retrieved performance metrics for {stylist}",
            'error': "I couldn't retrieve performance data. {error}"
        },
        Intent.DAILY_SUMMARY: {
            'success': "Today: {bookings} bookings, {completed} completed, ${revenue} revenue",
            'error': "I couldn't generate the summary. {error}"
        },
        Intent.CHECK_IN: {
            'success': "Checked in {client}",
            'not_found': "No appointment found for {client} today",
            'error': "I couldn't check in the client. {error}"
        },
        Intent.HELP: {
            'success': "I can help you with bookings, clients, inventory, staff, and analytics. What would you like to do?"
        },
        'error_general': "I'm sorry, I encountered an error: {error}",
        'clarification': "I need more information. {question}",
        'unknown_intent': "I didn't understand that. Could you rephrase?"
    }

    
    # Yoruba templates
    YORUBA_TEMPLATES = {
        Intent.BOOK_APPOINTMENT: {
            'success': "Mo ti ṣe idapọ {client} fun {service} ni {date} ni {time}",
            'success_no_time': "Mo ti ṣe idapọ {client} fun {service}",
            'client_not_found': "Mi o ri alabara ti a npè ni {client}. Ṣe o fẹ fikun wọn ni akọkọ?",
            'error': "Mi o le pari idapọ naa. {error}"
        },
        Intent.CANCEL_APPOINTMENT: {
            'success': "Mo ti fagilee ipade {client}",
            'not_found': "Mi o ri ipade ti o nbọ fun {client}",
            'error': "Mi o le fagilee ipade naa. {error}"
        },
        Intent.RESCHEDULE_APPOINTMENT: {
            'success': "Mo ti yi ipade {client} pada si {date} ni {time}",
            'not_found': "Mi o ri ipade kankan fun {client}",
            'error': "Mi o le yi ipade pada. {error}"
        },
        Intent.SHOW_APPOINTMENTS: {
            'success': "O ni ipade {count} loni",
            'none': "Ko si ipade ti a ṣeto fun oni",
            'list': "Awọn ipade oni: {appointments}"
        },
        Intent.ADD_CLIENT: {
            'success': "Mo ti fikun {name} bi alabara tuntun",
            'error': "Mi o le fikun alabara naa. {error}"
        },
        Intent.SHOW_CLIENT_INFO: {
            'success': "{client} ni ibẹwo {visits} lapapọ. Ibẹwo to kẹhin ni {last_visit}",
            'not_found': "Mi o ri alabara ti a npè ni {client}",
            'error': "Mi o le gba alaye alabara. {error}"
        },
        Intent.FIND_INACTIVE_CLIENTS: {
            'success': "Mo ri awọn alabara {count} ti ko ti wa ni {period}",
            'none': "Gbogbo awọn alabara n ṣiṣẹ",
            'error': "Mi o le wa awọn alabara ti ko ṣiṣẹ. {error}"
        },
        Intent.SHOW_REVENUE: {
            'success': "Owo wiwọle fun {period} jẹ ${amount}",
            'error': "Mi o le gba alaye owo wiwọle. {error}"
        },
        Intent.SHOW_ANALYTICS: {
            'success': "Apapọ owo: ${revenue}, Apapọ idapọ: {bookings}, Apapọ alabara: {clients}",
            'error': "Mi o le gba awọn iṣiro. {error}"
        },
        Intent.CHECK_INVENTORY: {
            'success': "{product} ni awọn ẹya {quantity} ni ipamọ",
            'low_stock': "Awọn ọja {count} ti dinku",
            'not_found': "Mi o ri {product} ninu ipamọ",
            'error': "Mi o le ṣayẹwo ipamọ. {error}"
        },
        Intent.UPDATE_INVENTORY: {
            'success': "Ti ṣe imudojuiwọn {product} si awọn ẹya {quantity}",
            'error': "Mi o le ṣe imudojuiwọn ipamọ. {error}"
        },
        Intent.SHOW_STAFF_SCHEDULE: {
            'success': "{stylist} ni ipade {count} loni",
            'not_found': "Mi o ri oṣiṣẹ ti a npè ni {stylist}",
            'error': "Mi o le gba iṣeto naa. {error}"
        },
        Intent.CHECK_AVAILABILITY: {
            'success': "Awọn oṣiṣẹ {count} wa: {staff}",
            'none': "Ko si oṣiṣẹ ti o wa ni {time}",
            'error': "Mi o le ṣayẹwo wiwa. {error}"
        },
        Intent.MARK_ATTENDANCE: {
            'success': "Samisi {stylist} bi {status}",
            'error': "Mi o le samisi wiwa. {error}"
        },
        Intent.SHOW_PERFORMANCE: {
            'success': "Gba awọn metiriki iṣẹ fun {stylist}",
            'error': "Mi o le gba data iṣẹ. {error}"
        },
        Intent.DAILY_SUMMARY: {
            'success': "Loni: idapọ {bookings}, {completed} ti pari, owo ${revenue}",
            'error': "Mi o le ṣe akopọ. {error}"
        },
        Intent.CHECK_IN: {
            'success': "Ṣayẹwo {client} wọle",
            'not_found': "Ko si ipade fun {client} loni",
            'error': "Mi o le ṣayẹwo alabara wọle. {error}"
        },
        Intent.HELP: {
            'success': "Mo le ran ọ lọwọ pẹlu awọn idapọ, alabara, ipamọ, oṣiṣẹ, ati awọn iṣiro. Kini o fẹ ṣe?"
        },
        'error_general': "Ma binu, mo pade aṣiṣe: {error}",
        'clarification': "Mo nilo alaye diẹ sii. {question}",
        'unknown_intent': "Mi o loye iyẹn. Ṣe o le sọ ọ ni ọna miiran?"
    }

    
    # Igbo templates
    IGBO_TEMPLATES = {
        Intent.BOOK_APPOINTMENT: {
            'success': "Edebela m {client} maka {service} na {date} na {time}",
            'success_no_time': "Edebela m {client} maka {service}",
            'client_not_found': "Achọtaghị m onye ahịa a na-akpọ {client}. Ị chọrọ itinye ha na mbụ?",
            'error': "Enweghị m ike imecha ndebe ahụ. {error}"
        },
        Intent.CANCEL_APPOINTMENT: {
            'success': "Akagbuola m nhọpụta {client}",
            'not_found': "Achọtaghị m nhọpụta ọ bụla na-abịa maka {client}",
            'error': "Enweghị m ike ịkagbu nhọpụta ahụ. {error}"
        },
        Intent.RESCHEDULE_APPOINTMENT: {
            'success': "Agbanweela m nhọpụta {client} gaa {date} na {time}",
            'not_found': "Achọtaghị m nhọpụta ọ bụla maka {client}",
            'error': "Enweghị m ike ịgbanwe nhọpụta ahụ. {error}"
        },
        Intent.SHOW_APPOINTMENTS: {
            'success': "Ị nwere nhọpụta {count} taa",
            'none': "Enweghị nhọpụta edebere maka taa",
            'list': "Nhọpụta taa: {appointments}"
        },
        Intent.ADD_CLIENT: {
            'success': "Etinyela m {name} dị ka onye ahịa ọhụrụ",
            'error': "Enweghị m ike itinye onye ahịa ahụ. {error}"
        },
        Intent.SHOW_CLIENT_INFO: {
            'success': "{client} nwere nleta {visits} n'ozuzu. Nleta ikpeazụ bụ na {last_visit}",
            'not_found': "Achọtaghị m onye ahịa a na-akpọ {client}",
            'error': "Enweghị m ike inweta ozi onye ahịa. {error}"
        },
        Intent.FIND_INACTIVE_CLIENTS: {
            'success': "Achọtara m ndị ahịa {count} na-abịaghị na {period}",
            'none': "Ndị ahịa niile na-arụ ọrụ",
            'error': "Enweghị m ike ịchọta ndị ahịa na-adịghị arụ ọrụ. {error}"
        },
        Intent.SHOW_REVENUE: {
            'success': "Ego maka {period} bụ ${amount}",
            'error': "Enweghị m ike inweta ozi ego. {error}"
        },
        Intent.SHOW_ANALYTICS: {
            'success': "Ngụkọta ego: ${revenue}, Ngụkọta ndebe: {bookings}, Ngụkọta ndị ahịa: {clients}",
            'error': "Enweghị m ike inweta nyocha. {error}"
        },
        Intent.CHECK_INVENTORY: {
            'success': "{product} nwere ngwaahịa {quantity} na nchekwa",
            'low_stock': "Ngwaahịa {count} na-agwụ",
            'not_found': "Achọtaghị m {product} na nchekwa",
            'error': "Enweghị m ike ịlelee nchekwa. {error}"
        },
        Intent.UPDATE_INVENTORY: {
            'success': "Emelitela {product} ka ọ bụrụ ngwaahịa {quantity}",
            'error': "Enweghị m ike imelite nchekwa. {error}"
        },
        Intent.SHOW_STAFF_SCHEDULE: {
            'success': "{stylist} nwere nhọpụta {count} taa",
            'not_found': "Achọtaghị m onye ọrụ a na-akpọ {stylist}",
            'error': "Enweghị m ike inweta nhazi ahụ. {error}"
        },
        Intent.CHECK_AVAILABILITY: {
            'success': "Ndị ọrụ {count} dị: {staff}",
            'none': "Ọ dịghị onye ọrụ dị na {time}",
            'error': "Enweghị m ike ịlelee nnwere onwe. {error}"
        },
        Intent.MARK_ATTENDANCE: {
            'success': "Kaara {stylist} dị ka {status}",
            'error': "Enweghị m ike ịka ọbịbịa. {error}"
        },
        Intent.SHOW_PERFORMANCE: {
            'success': "Nwetara ọnụọgụgụ arụmọrụ maka {stylist}",
            'error': "Enweghị m ike inweta data arụmọrụ. {error}"
        },
        Intent.DAILY_SUMMARY: {
            'success': "Taa: ndebe {bookings}, {completed} emechara, ego ${revenue}",
            'error': "Enweghị m ike ịmepụta nchịkọta. {error}"
        },
        Intent.CHECK_IN: {
            'success': "Nyochaa {client} n'ime",
            'not_found': "Enweghị nhọpụta maka {client} taa",
            'error': "Enweghị m ike ịnyocha onye ahịa n'ime. {error}"
        },
        Intent.HELP: {
            'success': "Enwere m ike inyere gị aka na ndebe, ndị ahịa, nchekwa, ndị ọrụ, na nyocha. Gịnị ka ị chọrọ ime?"
        },
        'error_general': "Ndo, ezutere m njehie: {error}",
        'clarification': "Achọrọ m ozi ndị ọzọ. {question}",
        'unknown_intent': "Aghọtaghị m nke ahụ. Ị nwere ike ikwughachi ya?"
    }

    
    # Hausa templates
    HAUSA_TEMPLATES = {
        Intent.BOOK_APPOINTMENT: {
            'success': "Na yi wa {client} alƙawari don {service} a {date} da {time}",
            'success_no_time': "Na yi wa {client} alƙawari don {service}",
            'client_not_found': "Ban sami abokin ciniki da ake kira {client} ba. Kuna son ƙara su da farko?",
            'error': "Ba zan iya kammala alƙawarin ba. {error}"
        },
        Intent.CANCEL_APPOINTMENT: {
            'success': "Na soke alƙawarin {client}",
            'not_found': "Ban sami alƙawari mai zuwa don {client} ba",
            'error': "Ba zan iya soke alƙawarin ba. {error}"
        },
        Intent.RESCHEDULE_APPOINTMENT: {
            'success': "Na sake tsara alƙawarin {client} zuwa {date} da {time}",
            'not_found': "Ban sami alƙawari don {client} ba",
            'error': "Ba zan iya sake tsara alƙawarin ba. {error}"
        },
        Intent.SHOW_APPOINTMENTS: {
            'success': "Kuna da alƙawari {count} a yau",
            'none': "Babu alƙawari da aka tsara don yau",
            'list': "Alƙawaran yau: {appointments}"
        },
        Intent.ADD_CLIENT: {
            'success': "Na ƙara {name} a matsayin sabon abokin ciniki",
            'error': "Ba zan iya ƙara abokin ciniki ba. {error}"
        },
        Intent.SHOW_CLIENT_INFO: {
            'success': "{client} yana da ziyara {visits} gabaɗaya. Ziyara ta ƙarshe ita ce {last_visit}",
            'not_found': "Ban sami abokin ciniki da ake kira {client} ba",
            'error': "Ba zan iya samun bayanan abokin ciniki ba. {error}"
        },
        Intent.FIND_INACTIVE_CLIENTS: {
            'success': "Na sami abokan ciniki {count} waɗanda ba su zo ba a {period}",
            'none': "Duk abokan ciniki suna aiki",
            'error': "Ba zan iya nemo abokan ciniki marasa aiki ba. {error}"
        },
        Intent.SHOW_REVENUE: {
            'success': "Kudin shiga don {period} shine ${amount}",
            'error': "Ba zan iya samun bayanan kudin shiga ba. {error}"
        },
        Intent.SHOW_ANALYTICS: {
            'success': "Jimlar kudin shiga: ${revenue}, Jimlar alƙawari: {bookings}, Jimlar abokan ciniki: {clients}",
            'error': "Ba zan iya samun bincike ba. {error}"
        },
        Intent.CHECK_INVENTORY: {
            'success': "{product} yana da raka'a {quantity} a ajiya",
            'low_stock': "Kayayyaki {count} suna ƙarancewa",
            'not_found': "Ban sami {product} a cikin ajiya ba",
            'error': "Ba zan iya duba ajiya ba. {error}"
        },
        Intent.UPDATE_INVENTORY: {
            'success': "An sabunta {product} zuwa raka'a {quantity}",
            'error': "Ba zan iya sabunta ajiya ba. {error}"
        },
        Intent.SHOW_STAFF_SCHEDULE: {
            'success': "{stylist} yana da alƙawari {count} a yau",
            'not_found': "Ban sami ma'aikaci da ake kira {stylist} ba",
            'error': "Ba zan iya samun jadawalin ba. {error}"
        },
        Intent.CHECK_AVAILABILITY: {
            'success': "Ma'aikata {count} suna samuwa: {staff}",
            'none': "Babu ma'aikaci a {time}",
            'error': "Ba zan iya duba samun ba. {error}"
        },
        Intent.MARK_ATTENDANCE: {
            'success': "An yi wa {stylist} alama a matsayin {status}",
            'error': "Ba zan iya yi wa halarta alama ba. {error}"
        },
        Intent.SHOW_PERFORMANCE: {
            'success': "An sami ƙididdiga na aiki don {stylist}",
            'error': "Ba zan iya samun bayanan aiki ba. {error}"
        },
        Intent.DAILY_SUMMARY: {
            'success': "Yau: alƙawari {bookings}, {completed} an kammala, kuɗi ${revenue}",
            'error': "Ba zan iya samar da taƙaitaccen ba. {error}"
        },
        Intent.CHECK_IN: {
            'success': "An duba {client} ciki",
            'not_found': "Babu alƙawari don {client} a yau",
            'error': "Ba zan iya duba abokin ciniki ciki ba. {error}"
        },
        Intent.HELP: {
            'success': "Zan iya taimaka muku da alƙawari, abokan ciniki, ajiya, ma'aikata, da bincike. Me kuke son yi?"
        },
        'error_general': "Yi hakuri, na gamu da kuskure: {error}",
        'clarification': "Ina buƙatar ƙarin bayani. {question}",
        'unknown_intent': "Ban fahimci wannan ba. Za ku iya sake faɗi?"
    }

    
    # Nigerian Pidgin templates
    PIDGIN_TEMPLATES = {
        Intent.BOOK_APPOINTMENT: {
            'success': "I don book {client} for {service} on {date} at {time}",
            'success_no_time': "I don book {client} for {service}",
            'client_not_found': "I no fit find customer wey dem dey call {client}. You wan add am first?",
            'error': "I no fit complete the booking. {error}"
        },
        Intent.CANCEL_APPOINTMENT: {
            'success': "I don cancel {client} appointment",
            'not_found': "I no see any appointment wey dey come for {client}",
            'error': "I no fit cancel the appointment. {error}"
        },
        Intent.RESCHEDULE_APPOINTMENT: {
            'success': "I don change {client} appointment to {date} at {time}",
            'not_found': "I no see any appointment for {client}",
            'error': "I no fit reschedule the appointment. {error}"
        },
        Intent.SHOW_APPOINTMENTS: {
            'success': "You get {count} appointments today",
            'none': "No appointment for today",
            'list': "Today appointments: {appointments}"
        },
        Intent.ADD_CLIENT: {
            'success': "I don add {name} as new customer",
            'error': "I no fit add the customer. {error}"
        },
        Intent.SHOW_CLIENT_INFO: {
            'success': "{client} get {visits} total visits. Last visit na {last_visit}",
            'not_found': "I no fit find customer wey dem dey call {client}",
            'error': "I no fit get customer information. {error}"
        },
        Intent.FIND_INACTIVE_CLIENTS: {
            'success': "I find {count} customers wey never come for {period}",
            'none': "All customers dey active",
            'error': "I no fit find inactive customers. {error}"
        },
        Intent.SHOW_REVENUE: {
            'success': "Money wey enter for {period} na ${amount}",
            'error': "I no fit get revenue information. {error}"
        },
        Intent.SHOW_ANALYTICS: {
            'success': "Total money: ${revenue}, Total bookings: {bookings}, Total customers: {clients}",
            'error': "I no fit get analytics. {error}"
        },
        Intent.CHECK_INVENTORY: {
            'success': "{product} get {quantity} units for stock",
            'low_stock': "{count} products don low",
            'not_found': "I no fit find {product} for inventory",
            'error': "I no fit check inventory. {error}"
        },
        Intent.UPDATE_INVENTORY: {
            'success': "I don update {product} to {quantity} units",
            'error': "I no fit update inventory. {error}"
        },
        Intent.SHOW_STAFF_SCHEDULE: {
            'success': "{stylist} get {count} appointments today",
            'not_found': "I no fit find staff wey dem dey call {stylist}",
            'error': "I no fit get the schedule. {error}"
        },
        Intent.CHECK_AVAILABILITY: {
            'success': "{count} staff dey available: {staff}",
            'none': "No staff dey available for {time}",
            'error': "I no fit check availability. {error}"
        },
        Intent.MARK_ATTENDANCE: {
            'success': "I don mark {stylist} as {status}",
            'error': "I no fit mark attendance. {error}"
        },
        Intent.SHOW_PERFORMANCE: {
            'success': "I don get performance metrics for {stylist}",
            'error': "I no fit get performance data. {error}"
        },
        Intent.DAILY_SUMMARY: {
            'success': "Today: {bookings} bookings, {completed} don complete, ${revenue} money",
            'error': "I no fit make the summary. {error}"
        },
        Intent.CHECK_IN: {
            'success': "I don check in {client}",
            'not_found': "No appointment for {client} today",
            'error': "I no fit check in the customer. {error}"
        },
        Intent.HELP: {
            'success': "I fit help you with bookings, customers, inventory, staff, and analytics. Wetin you wan do?"
        },
        'error_general': "Sorry o, I see error: {error}",
        'clarification': "I need more information. {question}",
        'unknown_intent': "I no understand that one. You fit talk am again?"
    }
    
    @classmethod
    def get_template(cls, intent: Intent, template_key: str, language: str = 'en') -> str:
        """
        Get response template for intent and language
        
        Args:
            intent: Intent type
            template_key: Template key (success, error, etc.)
            language: Language code
            
        Returns:
            Template string
        """
        language_templates = {
            'en': cls.ENGLISH_TEMPLATES,
            'yo': cls.YORUBA_TEMPLATES,
            'ig': cls.IGBO_TEMPLATES,
            'ha': cls.HAUSA_TEMPLATES,
            'pcm': cls.PIDGIN_TEMPLATES
        }
        
        templates = language_templates.get(language, cls.ENGLISH_TEMPLATES)
        intent_templates = templates.get(intent, {})
        
        return intent_templates.get(template_key, templates.get('error_general', 'Error occurred'))
    
    @classmethod
    def format_response(
        cls,
        intent: Intent,
        template_key: str,
        language: str = 'en',
        **kwargs
    ) -> str:
        """
        Format response with template and data
        
        Args:
            intent: Intent type
            template_key: Template key
            language: Language code
            **kwargs: Template variables
            
        Returns:
            Formatted response string
        """
        template = cls.get_template(intent, template_key, language)
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # Missing template variable, return template as-is
            return template
