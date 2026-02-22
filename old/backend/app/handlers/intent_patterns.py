"""
Multilingual Intent Patterns
Intent definitions and patterns for all supported languages
"""

from typing import Dict, List
from app.models.voice_models import Intent


class IntentPatterns:
    """Multilingual intent pattern definitions"""
    
    # English patterns
    ENGLISH_PATTERNS: Dict[Intent, List[str]] = {
        Intent.BOOK_APPOINTMENT: [
            "book {client} for {service}",
            "schedule {client} with {stylist}",
            "make appointment for {client}",
            "book {service} for {client}",
            "schedule {client} on {date} at {time}",
            "create booking for {client}",
        ],
        Intent.CANCEL_APPOINTMENT: [
            "cancel {client}'s appointment",
            "cancel appointment for {client}",
            "remove {client}'s booking",
            "delete appointment",
        ],
        Intent.RESCHEDULE_APPOINTMENT: [
            "reschedule {client} to {date}",
            "move {client}'s appointment",
            "change {client}'s time",
            "reschedule to {time}",
        ],
        Intent.SHOW_APPOINTMENTS: [
            "show today's appointments",
            "list appointments",
            "what appointments do I have",
            "show bookings",
            "who's coming today",
            "next appointment",
        ],
        Intent.ADD_CLIENT: [
            "add new client {name}",
            "create client {name}",
            "register client {name} {phone}",
            "new customer {name}",
        ],
        Intent.SHOW_CLIENT_INFO: [
            "show {client}'s history",
            "client information for {client}",
            "show {client}'s details",
            "what services has {client} had",
        ],
        Intent.FIND_INACTIVE_CLIENTS: [
            "find inactive clients",
            "who hasn't visited in {period}",
            "show clients who haven't come back",
            "list dormant clients",
        ],
        Intent.SHOW_REVENUE: [
            "show today's revenue",
            "how much did I make",
            "show earnings",
            "total revenue",
            "show income",
        ],
        Intent.SHOW_ANALYTICS: [
            "show analytics",
            "business performance",
            "show metrics",
            "show statistics",
        ],
        Intent.CHECK_INVENTORY: [
            "what products are low",
            "check inventory",
            "how much {product} do I have",
            "stock levels",
            "what needs reordering",
        ],
        Intent.UPDATE_INVENTORY: [
            "add {quantity} {product}",
            "update stock for {product}",
            "mark {product} as used",
            "reduce {product} by {quantity}",
        ],
        Intent.SHOW_STAFF_SCHEDULE: [
            "show {stylist}'s schedule",
            "what's {stylist}'s schedule",
            "show staff schedule",
        ],
        Intent.CHECK_AVAILABILITY: [
            "who's available at {time}",
            "check availability",
            "who's free",
        ],
        Intent.MARK_ATTENDANCE: [
            "mark {stylist} as present",
            "mark {stylist} as absent",
            "{stylist} is here",
        ],
        Intent.SHOW_PERFORMANCE: [
            "show {stylist}'s performance",
            "how is {stylist} doing",
            "staff performance",
        ],
        Intent.QUICK_BOOK: [
            "quick book",
            "fast booking",
        ],
        Intent.DAILY_SUMMARY: [
            "daily summary",
            "end of day report",
            "today's summary",
        ],
        Intent.EMERGENCY_CANCEL: [
            "emergency cancel",
            "cancel now",
        ],
        Intent.CHECK_IN: [
            "check in {client}",
            "{client} is here",
            "mark {client} as arrived",
        ],
        Intent.END_OF_DAY: [
            "end of day",
            "close day",
            "daily closing",
        ],
        Intent.SHOW_SUGGESTIONS: [
            "what do you suggest",
            "show me suggestions",
            "what should I do",
            "give me recommendations",
            "any suggestions",
        ],
        Intent.SHOW_INSIGHTS: [
            "show me insights",
            "business insights",
            "what insights do you have",
            "show me analysis",
        ],
        Intent.PREDICT_BOOKINGS: [
            "predict next week's bookings",
            "how many bookings next week",
            "forecast bookings",
            "predict demand",
        ],
        Intent.PREDICT_CHURN: [
            "which clients might not return",
            "who might churn",
            "at-risk clients",
            "clients who might leave",
        ],
        Intent.PREDICT_REORDER: [
            "when should I reorder {product}",
            "when will {product} run out",
            "predict inventory for {product}",
            "when to reorder",
        ],
        Intent.HELP: [
            "help",
            "what can you do",
            "show commands",
            "how do I",
        ],
    }
    
    # Yoruba patterns
    YORUBA_PATTERNS: Dict[Intent, List[str]] = {
        Intent.BOOK_APPOINTMENT: [
            "ṣe idapọ fun {client}",
            "ṣeto {client} pẹlu {stylist}",
            "ṣe ipade fun {client}",
            "ṣe booking fun {service}",
            "ṣeto {client} ni {date} ni {time}",
        ],
        Intent.CANCEL_APPOINTMENT: [
            "fagilee ipade {client}",
            "pa ipade {client} rẹ",
            "yọ booking {client} kuro",
        ],
        Intent.RESCHEDULE_APPOINTMENT: [
            "yi ipade {client} pada si {date}",
            "yi akoko {client} pada",
            "ṣe atunṣe ipade",
        ],
        Intent.SHOW_APPOINTMENTS: [
            "fi awọn ipade oni han",
            "kilode awọn ipade",
            "tani o nbọ loni",
            "ipade ti o tẹle",
        ],
        Intent.ADD_CLIENT: [
            "fikun alabara tuntun {name}",
            "ṣẹda alabara {name}",
            "forukọsilẹ alabara {name}",
        ],
        Intent.SHOW_CLIENT_INFO: [
            "fi itan {client} han",
            "alaye alabara fun {client}",
            "awọn iṣẹ {client}",
        ],
        Intent.FIND_INACTIVE_CLIENTS: [
            "wa awọn alabara ti ko ṣiṣẹ",
            "tani ko ti wa ni {period}",
            "awọn alabara ti ko pada",
        ],
        Intent.SHOW_REVENUE: [
            "fi owo wiwọle oni han",
            "elo ni mo ṣe",
            "fi owo han",
            "apapọ owo wiwọle",
        ],
        Intent.SHOW_ANALYTICS: [
            "fi awọn iṣiro han",
            "iṣẹ iṣowo",
            "awọn metiriki",
        ],
        Intent.CHECK_INVENTORY: [
            "awọn ọja wo lo kere",
            "ṣayẹwo ipamọ",
            "elo {product} ni mo ni",
            "ipele ipamọ",
        ],
        Intent.UPDATE_INVENTORY: [
            "fikun {quantity} {product}",
            "ṣe imudojuiwọn ipamọ fun {product}",
            "samisi {product} bi a ti lo",
        ],
        Intent.SHOW_STAFF_SCHEDULE: [
            "fi iṣeto {stylist} han",
            "kini iṣeto {stylist}",
        ],
        Intent.CHECK_AVAILABILITY: [
            "tani o wa ni {time}",
            "ṣayẹwo wiwa",
        ],
        Intent.MARK_ATTENDANCE: [
            "samisi {stylist} bi o wa",
            "samisi {stylist} bi ko si",
        ],
        Intent.SHOW_PERFORMANCE: [
            "fi iṣẹ {stylist} han",
            "bawo ni {stylist} ṣe n ṣe",
        ],
        Intent.QUICK_BOOK: [
            "booking iyara",
        ],
        Intent.DAILY_SUMMARY: [
            "akopọ ọjọ",
            "ijabọ ipari ọjọ",
        ],
        Intent.EMERGENCY_CANCEL: [
            "fagilee pajawiri",
        ],
        Intent.CHECK_IN: [
            "ṣayẹwo {client} wọle",
            "{client} ti de",
        ],
        Intent.END_OF_DAY: [
            "ipari ọjọ",
            "ti ọjọ",
        ],
        Intent.SHOW_SUGGESTIONS: [
            "kini o daba",
            "fi awọn imọran han",
            "kini mo yẹ ki n ṣe",
            "fun mi ni awọn imọran",
        ],
        Intent.SHOW_INSIGHTS: [
            "fi awọn oye han",
            "awọn oye iṣowo",
            "kini awọn oye ti o ni",
        ],
        Intent.PREDICT_BOOKINGS: [
            "sọ awọn booking ọsẹ to nbọ",
            "melo ni booking ọsẹ to nbọ",
            "asọtẹlẹ awọn booking",
        ],
        Intent.PREDICT_CHURN: [
            "awọn alabara wo le ma pada",
            "tani le lọ",
            "awọn alabara ti o lewu",
        ],
        Intent.PREDICT_REORDER: [
            "nigbawo ni mo yẹ ki n tun ra {product}",
            "nigbawo ni {product} yoo tan",
            "asọtẹlẹ ipamọ fun {product}",
        ],
        Intent.HELP: [
            "iranlọwọ",
            "kini o le ṣe",
            "fi awọn aṣẹ han",
        ],
    }
    
    # Igbo patterns
    IGBO_PATTERNS: Dict[Intent, List[str]] = {
        Intent.BOOK_APPOINTMENT: [
            "debe aha {client}",
            "hazie {client} na {stylist}",
            "mee nhọpụta maka {client}",
            "debe {service} maka {client}",
            "hazie {client} na {date} na {time}",
        ],
        Intent.CANCEL_APPOINTMENT: [
            "kagbuo nhọpụta {client}",
            "hichapụ booking {client}",
            "kagbuo nhọpụta",
        ],
        Intent.RESCHEDULE_APPOINTMENT: [
            "gbanwee nhọpụta {client} gaa {date}",
            "gbanwee oge {client}",
            "megharịa nhọpụta",
        ],
        Intent.SHOW_APPOINTMENTS: [
            "gosi nhọpụta taa",
            "depụta nhọpụta",
            "onye na-abịa taa",
            "nhọpụta na-esote",
        ],
        Intent.ADD_CLIENT: [
            "tinye onye ahịa ọhụrụ {name}",
            "mepụta onye ahịa {name}",
            "debanye aha onye ahịa {name}",
        ],
        Intent.SHOW_CLIENT_INFO: [
            "gosi akụkọ {client}",
            "ozi onye ahịa maka {client}",
            "ọrụ {client} nwere",
        ],
        Intent.FIND_INACTIVE_CLIENTS: [
            "chọta ndị ahịa na-adịghị arụ ọrụ",
            "onye na-abịaghị na {period}",
            "ndị ahịa na-alọtaghị",
        ],
        Intent.SHOW_REVENUE: [
            "gosi ego taa",
            "ego ole m nwetara",
            "gosi ego",
            "ngụkọta ego",
        ],
        Intent.SHOW_ANALYTICS: [
            "gosi nyocha",
            "arụmọrụ azụmahịa",
            "gosi ọnụọgụgụ",
        ],
        Intent.CHECK_INVENTORY: [
            "ngwaahịa ole dị ala",
            "lelee ngwaahịa",
            "ole {product} m nwere",
            "ọkwa ngwaahịa",
        ],
        Intent.UPDATE_INVENTORY: [
            "tinye {quantity} {product}",
            "melite ngwaahịa maka {product}",
            "kaa {product} dịka ejiri ya",
        ],
        Intent.SHOW_STAFF_SCHEDULE: [
            "gosi nhazi {stylist}",
            "kedu nhazi {stylist}",
        ],
        Intent.CHECK_AVAILABILITY: [
            "onye nọ na {time}",
            "lelee nnwere onwe",
        ],
        Intent.MARK_ATTENDANCE: [
            "kaa {stylist} dịka ọ nọ",
            "kaa {stylist} dịka ọ nọghị",
        ],
        Intent.SHOW_PERFORMANCE: [
            "gosi arụmọrụ {stylist}",
            "kedu ka {stylist} si eme",
        ],
        Intent.QUICK_BOOK: [
            "booking ngwa ngwa",
        ],
        Intent.DAILY_SUMMARY: [
            "nchịkọta ụbọchị",
            "mkpesa njedebe ụbọchị",
        ],
        Intent.EMERGENCY_CANCEL: [
            "kagbuo mberede",
        ],
        Intent.CHECK_IN: [
            "nyochaa {client} n'ime",
            "{client} abịala",
        ],
        Intent.END_OF_DAY: [
            "njedebe ụbọchị",
            "mechie ụbọchị",
        ],
        Intent.SHOW_SUGGESTIONS: [
            "gịnị ị na-atụ aro",
            "gosi m aro",
            "gịnị m kwesịrị ime",
            "nye m aro",
        ],
        Intent.SHOW_INSIGHTS: [
            "gosi m nghọta",
            "nghọta azụmahịa",
            "gịnị nghọta ị nwere",
        ],
        Intent.PREDICT_BOOKINGS: [
            "buo amụma booking izu na-abịa",
            "booking ole n'izu na-abịa",
            "buo amụma ọchịchọ",
        ],
        Intent.PREDICT_CHURN: [
            "ndị ahịa ole nwere ike ịlaghachi",
            "onye nwere ike ịpụ",
            "ndị ahịa nọ n'ihe ize ndụ",
        ],
        Intent.PREDICT_REORDER: [
            "mgbe m kwesịrị ịtụgharị {product}",
            "mgbe {product} ga-agwụ",
            "buo amụma ngwaahịa maka {product}",
        ],
        Intent.HELP: [
            "enyemaka",
            "gịnị ị nwere ike ime",
            "gosi iwu",
        ],
    }
    
    # Hausa patterns
    HAUSA_PATTERNS: Dict[Intent, List[str]] = {
        Intent.BOOK_APPOINTMENT: [
            "yi wa {client} alƙawari",
            "shirya {client} da {stylist}",
            "yi alƙawari ga {client}",
            "yi booking na {service}",
            "shirya {client} a {date} da {time}",
        ],
        Intent.CANCEL_APPOINTMENT: [
            "soke alƙawarin {client}",
            "cire booking na {client}",
            "soke alƙawari",
        ],
        Intent.RESCHEDULE_APPOINTMENT: [
            "sake tsara alƙawarin {client} zuwa {date}",
            "canza lokacin {client}",
            "sake tsara alƙawari",
        ],
        Intent.SHOW_APPOINTMENTS: [
            "nuna alƙawaran yau",
            "jera alƙawari",
            "wane ne ke zuwa yau",
            "alƙawari na gaba",
        ],
        Intent.ADD_CLIENT: [
            "ƙara sabon abokin ciniki {name}",
            "ƙirƙiri abokin ciniki {name}",
            "yi rajistar abokin ciniki {name}",
        ],
        Intent.SHOW_CLIENT_INFO: [
            "nuna tarihin {client}",
            "bayanin abokin ciniki na {client}",
            "ayyukan {client}",
        ],
        Intent.FIND_INACTIVE_CLIENTS: [
            "nemo abokan ciniki marasa aiki",
            "wane bai zo ba a {period}",
            "abokan ciniki da ba su dawo ba",
        ],
        Intent.SHOW_REVENUE: [
            "nuna kudin shiga na yau",
            "nawa na samu",
            "nuna kuɗi",
            "jimlar kudin shiga",
        ],
        Intent.SHOW_ANALYTICS: [
            "nuna bincike",
            "aikin kasuwanci",
            "nuna ƙididdiga",
        ],
        Intent.CHECK_INVENTORY: [
            "waɗanne kayayyaki suke ƙasa",
            "duba kaya",
            "nawa {product} nake da shi",
            "matakan kaya",
        ],
        Intent.UPDATE_INVENTORY: [
            "ƙara {quantity} {product}",
            "sabunta kaya na {product}",
            "yi alama {product} kamar yadda aka yi amfani",
        ],
        Intent.SHOW_STAFF_SCHEDULE: [
            "nuna jadawalin {stylist}",
            "menene jadawalin {stylist}",
        ],
        Intent.CHECK_AVAILABILITY: [
            "wane ne yake a {time}",
            "duba samun",
        ],
        Intent.MARK_ATTENDANCE: [
            "yi alama {stylist} yana nan",
            "yi alama {stylist} babu",
        ],
        Intent.SHOW_PERFORMANCE: [
            "nuna aikin {stylist}",
            "yaya {stylist} yake yi",
        ],
        Intent.QUICK_BOOK: [
            "booking mai sauri",
        ],
        Intent.DAILY_SUMMARY: [
            "taƙaitaccen yau",
            "rahoton ƙarshen rana",
        ],
        Intent.EMERGENCY_CANCEL: [
            "soke gaggawa",
        ],
        Intent.CHECK_IN: [
            "duba {client} ciki",
            "{client} ya zo",
        ],
        Intent.END_OF_DAY: [
            "ƙarshen rana",
            "rufe rana",
        ],
        Intent.SHOW_SUGGESTIONS: [
            "me kake ba da shawara",
            "nuna shawarwari",
            "me zan yi",
            "ba ni shawarwari",
        ],
        Intent.SHOW_INSIGHTS: [
            "nuna fahimta",
            "fahimtar kasuwanci",
            "wane fahimta kake da shi",
        ],
        Intent.PREDICT_BOOKINGS: [
            "yi hasashen booking na mako mai zuwa",
            "booking nawa a mako mai zuwa",
            "yi hasashen buƙata",
        ],
        Intent.PREDICT_CHURN: [
            "waɗanne abokan ciniki ba za su dawo ba",
            "wane zai iya tafiya",
            "abokan ciniki masu haɗari",
        ],
        Intent.PREDICT_REORDER: [
            "yaushe zan sake yin oda {product}",
            "yaushe {product} zai ƙare",
            "yi hasashen kaya na {product}",
        ],
        Intent.HELP: [
            "taimako",
            "me za ka iya yi",
            "nuna umarni",
        ],
    }
    
    # Nigerian Pidgin patterns
    PIDGIN_PATTERNS: Dict[Intent, List[str]] = {
        Intent.BOOK_APPOINTMENT: [
            "book {client} for {service}",
            "arrange {client} with {stylist}",
            "make appointment for {client}",
            "book {service} for {client}",
            "arrange {client} for {date} at {time}",
        ],
        Intent.CANCEL_APPOINTMENT: [
            "cancel {client} appointment",
            "comot {client} booking",
            "cancel appointment",
        ],
        Intent.RESCHEDULE_APPOINTMENT: [
            "change {client} appointment to {date}",
            "move {client} time",
            "reschedule appointment",
        ],
        Intent.SHOW_APPOINTMENTS: [
            "show today appointment",
            "wetin be the appointments",
            "who dey come today",
            "next appointment",
        ],
        Intent.ADD_CLIENT: [
            "add new customer {name}",
            "create client {name}",
            "register customer {name}",
        ],
        Intent.SHOW_CLIENT_INFO: [
            "show {client} history",
            "wetin be {client} info",
            "show {client} details",
        ],
        Intent.FIND_INACTIVE_CLIENTS: [
            "find customers wey no dey come",
            "who never come for {period}",
            "show customers wey no return",
        ],
        Intent.SHOW_REVENUE: [
            "show today money",
            "how much I make",
            "show the money",
            "total money wey enter",
        ],
        Intent.SHOW_ANALYTICS: [
            "show analytics",
            "how business dey go",
            "show statistics",
        ],
        Intent.CHECK_INVENTORY: [
            "which product don low",
            "check inventory",
            "how much {product} we get",
            "stock levels",
        ],
        Intent.UPDATE_INVENTORY: [
            "add {quantity} {product}",
            "update stock for {product}",
            "mark {product} say we don use am",
        ],
        Intent.SHOW_STAFF_SCHEDULE: [
            "show {stylist} schedule",
            "wetin be {stylist} schedule",
        ],
        Intent.CHECK_AVAILABILITY: [
            "who dey available for {time}",
            "check who dey free",
        ],
        Intent.MARK_ATTENDANCE: [
            "mark {stylist} say e don come",
            "mark {stylist} say e no come",
        ],
        Intent.SHOW_PERFORMANCE: [
            "show how {stylist} dey perform",
            "how {stylist} dey do",
        ],
        Intent.QUICK_BOOK: [
            "quick booking",
        ],
        Intent.DAILY_SUMMARY: [
            "daily summary",
            "end of day report",
        ],
        Intent.EMERGENCY_CANCEL: [
            "cancel sharp sharp",
        ],
        Intent.CHECK_IN: [
            "check in {client}",
            "{client} don reach",
        ],
        Intent.END_OF_DAY: [
            "end of day",
            "close for today",
        ],
        Intent.SHOW_SUGGESTIONS: [
            "wetin you suggest",
            "show me suggestions",
            "wetin I suppose do",
            "give me recommendations",
        ],
        Intent.SHOW_INSIGHTS: [
            "show me insights",
            "business insights",
            "wetin insights you get",
        ],
        Intent.PREDICT_BOOKINGS: [
            "predict next week bookings",
            "how many bookings for next week",
            "forecast bookings",
        ],
        Intent.PREDICT_CHURN: [
            "which clients fit no come back",
            "who fit leave",
            "clients wey dey risk",
        ],
        Intent.PREDICT_REORDER: [
            "when I suppose reorder {product}",
            "when {product} go finish",
            "predict inventory for {product}",
        ],
        Intent.HELP: [
            "help",
            "wetin you fit do",
            "show commands",
        ],
    }
    
    @classmethod
    def get_patterns_for_language(cls, language: str) -> Dict[Intent, List[str]]:
        """Get intent patterns for a specific language"""
        language_map = {
            'en': cls.ENGLISH_PATTERNS,
            'yo': cls.YORUBA_PATTERNS,
            'ig': cls.IGBO_PATTERNS,
            'ha': cls.HAUSA_PATTERNS,
            'pcm': cls.PIDGIN_PATTERNS,
        }
        return language_map.get(language, cls.ENGLISH_PATTERNS)
    
    @classmethod
    def get_all_patterns(cls) -> Dict[str, Dict[Intent, List[str]]]:
        """Get all patterns for all languages"""
        return {
            'en': cls.ENGLISH_PATTERNS,
            'yo': cls.YORUBA_PATTERNS,
            'ig': cls.IGBO_PATTERNS,
            'ha': cls.HAUSA_PATTERNS,
            'pcm': cls.PIDGIN_PATTERNS,
        }


# Intent to action mappings
INTENT_ACTION_MAP = {
    Intent.BOOK_APPOINTMENT: "create_booking",
    Intent.CANCEL_APPOINTMENT: "cancel_booking",
    Intent.RESCHEDULE_APPOINTMENT: "reschedule_booking",
    Intent.SHOW_APPOINTMENTS: "list_appointments",
    Intent.ADD_CLIENT: "create_client",
    Intent.SHOW_CLIENT_INFO: "get_client_info",
    Intent.FIND_INACTIVE_CLIENTS: "find_inactive_clients",
    Intent.SHOW_REVENUE: "get_revenue",
    Intent.SHOW_ANALYTICS: "get_analytics",
    Intent.CHECK_INVENTORY: "check_inventory",
    Intent.UPDATE_INVENTORY: "update_inventory",
    Intent.SHOW_STAFF_SCHEDULE: "get_staff_schedule",
    Intent.CHECK_AVAILABILITY: "check_availability",
    Intent.MARK_ATTENDANCE: "mark_attendance",
    Intent.SHOW_PERFORMANCE: "get_performance",
    Intent.QUICK_BOOK: "quick_book_flow",
    Intent.DAILY_SUMMARY: "get_daily_summary",
    Intent.EMERGENCY_CANCEL: "emergency_cancel",
    Intent.CHECK_IN: "check_in_client",
    Intent.END_OF_DAY: "end_of_day_report",
    # AI Suggestion Actions
    Intent.SHOW_SUGGESTIONS: "get_ai_suggestions",
    Intent.SHOW_INSIGHTS: "get_ai_insights",
    Intent.PREDICT_BOOKINGS: "predict_bookings",
    Intent.PREDICT_CHURN: "predict_client_churn",
    Intent.PREDICT_REORDER: "predict_inventory_reorder",
    Intent.HELP: "show_help",
}


# Required entities for each intent
INTENT_REQUIRED_ENTITIES = {
    Intent.BOOK_APPOINTMENT: ["client", "service"],
    Intent.CANCEL_APPOINTMENT: ["client"],
    Intent.RESCHEDULE_APPOINTMENT: ["client", "date"],
    Intent.SHOW_APPOINTMENTS: [],
    Intent.ADD_CLIENT: ["name"],
    Intent.SHOW_CLIENT_INFO: ["client"],
    Intent.FIND_INACTIVE_CLIENTS: [],
    Intent.SHOW_REVENUE: [],
    Intent.SHOW_ANALYTICS: [],
    Intent.CHECK_INVENTORY: [],
    Intent.UPDATE_INVENTORY: ["product"],
    Intent.SHOW_STAFF_SCHEDULE: [],
    Intent.CHECK_AVAILABILITY: [],
    Intent.MARK_ATTENDANCE: ["stylist"],
    Intent.SHOW_PERFORMANCE: [],
    Intent.QUICK_BOOK: [],
    Intent.DAILY_SUMMARY: [],
    Intent.EMERGENCY_CANCEL: [],
    Intent.CHECK_IN: ["client"],
    Intent.END_OF_DAY: [],
    Intent.HELP: [],
}
