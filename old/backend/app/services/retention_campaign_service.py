"""
Retention campaign message generation service
"""
from jinja2 import Template
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


# Message templates
RETENTION_TEMPLATES = {
    "high_risk": """
Hi {{client_name}}! 👋

We've missed you at {{salon_name}}! It's been {{days_since_last_visit}} days since your last visit.

We'd love to see you again! Book your next appointment and get 10% off any service.

Reply YES to book or call us at {{salon_phone}}.

See you soon! ✨
""",
    
    "medium_risk": """
Hello {{client_name}}! 

Hope you're doing well! We noticed it's been a while since your last visit to {{salon_name}}.

Your favorite stylist {{stylist_name}} is available this week. Would you like to schedule an appointment?

Reply YES or call {{salon_phone}} to book.

Looking forward to seeing you! 💇
""",
    
    "low_risk": """
Hi {{client_name}}! 

Just a friendly reminder from {{salon_name}} - it's time for your next appointment!

We have some exciting new services you might love. Book now and maintain your fabulous look!

Call {{salon_phone}} or reply YES to schedule.

Thanks for being a valued client! ⭐
""",
    
    "special_offer": """
{{client_name}}, we have a special offer just for you! 🎁

Get {{discount}}% off your next visit at {{salon_name}}!

Valid until {{expiry_date}}. Don't miss out!

Book now: {{salon_phone}}

We can't wait to pamper you! 💅
""",
    
    "birthday": """
Happy Birthday {{client_name}}! 🎉🎂

{{salon_name}} wishes you an amazing day!

Celebrate with us - enjoy a complimentary {{free_service}} on your birthday month!

Call {{salon_phone}} to book your special birthday treat.

Cheers to you! 🥳
""",
    
    "win_back": """
{{client_name}}, we miss you! 😢

It's been {{days_since_last_visit}} days since we last saw you at {{salon_name}}.

Come back and let us make it up to you with {{discount}}% off your next service!

Your satisfaction is our priority. Call {{salon_phone}} today.

We'd love to have you back! ❤️
"""
}


def generate_retention_message(
    template_type: str,
    client_data: Dict,
    salon_data: Dict,
    **kwargs
) -> str:
    """
    Generate personalized retention message
    """
    try:
        # Get template
        template_str = RETENTION_TEMPLATES.get(template_type)
        if not template_str:
            template_str = RETENTION_TEMPLATES["low_risk"]
        
        # Prepare context
        context = {
            "client_name": client_data.get("name", "Valued Client"),
            "salon_name": salon_data.get("salon_name", "Our Salon"),
            "salon_phone": salon_data.get("phone", ""),
            "days_since_last_visit": client_data.get("days_since_last_visit", 0),
            **kwargs
        }
        
        # Render template
        template = Template(template_str)
        message = template.render(**context)
        
        return message.strip()
    
    except Exception as e:
        logger.error(f"Error generating retention message: {e}")
        return f"Hi {client_data.get('name', 'there')}! We'd love to see you again at {salon_data.get('salon_name', 'our salon')}!"


def select_template_for_risk_level(risk_level: str, days_since: int) -> str:
    """
    Select appropriate template based on risk level and days since last visit
    """
    if risk_level == "high":
        if days_since > 90:
            return "win_back"
        else:
            return "high_risk"
    elif risk_level == "medium":
        return "medium_risk"
    else:
        return "low_risk"


def calculate_campaign_effectiveness(campaign_id: str, responses: List[Dict]) -> Dict:
    """
    Calculate effectiveness metrics for a campaign
    """
    try:
        total_sent = len(responses)
        if total_sent == 0:
            return {
                "campaign_id": campaign_id,
                "total_sent": 0,
                "response_rate": 0,
                "booking_rate": 0,
                "roi": 0
            }
        
        # Count responses
        responded = sum(1 for r in responses if r.get("responded"))
        booked = sum(1 for r in responses if r.get("booked"))
        
        response_rate = (responded / total_sent) * 100
        booking_rate = (booked / total_sent) * 100
        
        # Calculate ROI (simplified)
        # Assume average booking value and campaign cost
        avg_booking_value = 5000  # NGN
        cost_per_message = 10  # NGN
        
        revenue = booked * avg_booking_value
        cost = total_sent * cost_per_message
        roi = ((revenue - cost) / cost * 100) if cost > 0 else 0
        
        return {
            "campaign_id": campaign_id,
            "total_sent": total_sent,
            "responded": responded,
            "booked": booked,
            "response_rate": round(response_rate, 2),
            "booking_rate": round(booking_rate, 2),
            "estimated_revenue": revenue,
            "estimated_cost": cost,
            "roi": round(roi, 2)
        }
    
    except Exception as e:
        logger.error(f"Error calculating campaign effectiveness: {e}")
        return {"error": str(e)}


from typing import List
