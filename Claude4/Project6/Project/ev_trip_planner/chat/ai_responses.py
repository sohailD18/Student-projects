"""
AI Charging Assistant - Rule-based Response System

This module provides intelligent responses to common EV-related questions
without requiring an external LLM API.
"""

import re
from core.models import ChargingStation


class EVAssistant:
    """Rule-based AI assistant for EV-related queries"""

    # Knowledge base of FAQ responses
    FAQ_RESPONSES = {
        # Battery Maintenance
        r'(battery|maintain|care|healthy|health|degrade|lifespan|long last).*\?': {
            'response': """**Battery Maintenance Tips:**

🔋 **Daily Charging:**
• Try to keep your battery between 20-80% for daily use
• Avoid letting it drop to 0% regularly
• Don't keep it at 100% for extended periods

🌡️ **Temperature:**
• Park in shade when possible
• Pre-condition battery while plugged in extreme weather
• Garage parking helps battery longevity

⚡ **Charging Habits:**
• Use Level 2 (home) charging when possible
• Save fast charging for road trips
• Avoid frequent rapid charging when not needed

💡 **Long-term:**
• Follow manufacturer guidelines
• Consider battery health when buying used EVs
• Modern EV batteries last 8-15 years with proper care""",
            'category': 'battery'
        },

        # Range and Efficiency
        r'(range|miles|kilometer|distance|efficiency|how far).*\?': {
            'response': """**Understanding EV Range:**

📊 **Factors Affecting Range:**
• **Speed:** Highway driving reduces range (80-100 km/h optimal)
• **Temperature:** Hot weather can reduce range by 15-25%
• **Terrain:** Hills and mountains consume more energy
• **Climate Control:** Air conditioning uses 10-15% of battery
• **Driving Style:** Smooth acceleration maximizes range

🔧 **Improving Efficiency:**
• Use Eco mode when available
• Pre-condition while plugged in
• Maintain proper tire pressure
• Remove unnecessary weight
• Plan routes with charging stops

📱 **Use our Trip Planner** to calculate your exact route needs!""",
            'category': 'range'
        },

        # Charging Basics
        r'(charge|charging|how to charge|plug).*\?': {
            'response': """**EV Charging Guide for India:**

🔌 **AC Charging (Home/Work)**
• 15A Standard Socket: ~3-4 km per hour
• 32A Wall-Mounted Charger: ~20-25 km per hour
• Recommended for daily home charging

🏠 **Public AC Charging**
• Type 2/GB_T Connectors (7-22 kW)
• ~25-40 km per hour
• Available at malls, offices, hotels

⚡ **DC Fast Charging (Bharat DC/CCS2)**
• 25-50 kW DC chargers
• 0-80% in 60-90 minutes
• Perfect for highway travel
• Tata Power, Ather, Statiq, Zeon networks

📍 **Use our Station Finder** to locate chargers in Karnataka!""",
            'category': 'charging'
        },

        # Charging Time
        r'(long|how long|time|wait).*charge.*\?': {
            'response': """**Charging Time Estimates:**

⏱️ **Home AC Charging (15A socket):**
• 8-10 hours for ~200 km
• Full charge: 8-12 hours

⏱️ **Wall-Mounted Charger (32A):**
• 4-6 hours for ~200 km
• Full charge: 4-6 hours

⏱️ **DC Fast Charging (50kW):**
• 60 minutes for 0-80% charge
• 30-40 minutes for 50-80%
• Most charging happens in first 50%

💡 **Tips for Faster Charging:**
• Charge to 80% for daily use (faster)
• Use fast chargers for road trips only
• Battery charges slower when nearly full
• Avoid charging in extreme heat if possible

**Tata Power, Ather Grid offer fast charging in Karnataka!**""",
            'category': 'charging_time'
        },

        # Charging Costs
        r'(cost|price|expensive|money|save|cheap).*\?': {
            'response': """**EV Charging Costs in India:**

💰 **Home Charging:**
• Average: ₹8-12 per kWh (domestic rate)
• Full charge: ₹300-600 (depending on battery)
• Per km: ~₹1-2
• vs Petrol/Diesel: ~70-80% cheaper per km

💵 **Public Charging:**
• Level 2: ₹12-20 per kWh
• DC Fast: ₹15-25 per kWh
• Some stations charge by time

🏆 **Money Saving Tips:**
• Charge at home overnight when possible
• Use free charging stations (some malls, workplaces)
• Consider installing solar panels for free home charging
• Check for government subsidies on home chargers

**Use our Station Finder** to compare prices!""",
            'category': 'cost'
        },

        # Finding Chargers
        r'(find|where|near|locate|station|charger).*\?': {
            'response': """**Find Charging Stations:**

🗺️ **Use Our Tools:**
• **Station Map** - Interactive map with all stations
• **Station List** - Filtered list with details
• **Trip Planner** - Auto-finds stops along your route

📍 **What We Show:**
• Connector types (CCS, CHAdeMO, Tesla)
• Charging speed (kW)
• Pricing per kWh
• Real-time availability
• Amenities (WiFi, restrooms, etc.)

🔍 **Filter Options:**
• Fast charging only
• Available stations only
• By connector type
• Max price

Navigate to **Charging Stations** in the menu to get started!""",
            'category': 'find_stations'
        },

        # Trip Planning
        r'(trip|plan|route|road trip|travel|journey).*\?': {
            'response': """**EV Trip Planning:**

🛣️ **Use Our Trip Planner:**
1. Enter start and destination
2. Select your vehicle
3. Input current battery %
4. Get optimized route with charging stops!

📋 **What We Calculate:**
• Total distance and time
• Battery consumption
• Recommended charging stops
• Charging time and cost estimates
• Final battery percentage

🎯 **Planning Tips:**
• Plan charging stops around meals
• Book hotels with charging
• Always have backup charging options
• Check station availability before leaving

Start planning from the **Trip Planner** page!""",
            'category': 'trip_planning'
        },

        # EV Types/Models
        r'(type|model|brand|which ev|best ev|recommend|tesla|buy|choose).*\?': {
            'response': """**Popular EVs in India:**

🚗 **Budget-Friendly Options:**
• Tata Nexon EV (~312 km range) - ₹15-18 lakhs
• Tata Tiago EV (~315 km range) - ₹8-11 lakhs
• MG Comet EV (~230 km range) - ₹7-9 lakhs

**Mid-Range:**
• Tata Punch EV (~421 km range) - ₹11-15 lakhs
• Mahindra XUV400 (~456 km range) - ₹16-19 lakhs
• Hyundai Kona Electric (~452 km range) - ₹24-26 lakhs
• MG ZS EV (~461 km range) - ₹22-26 lakhs

**Premium:**
• Hyundai Ioniq 5 (~631 km range) - ₹46-48 lakhs
• BMW iX (~425 km range) - ₹1.2 crore+
• Mercedes EQS (~577 km range) - ₹1.5 crore+

**Consider:**
• Budget (₹8-25 lakhs typical range)
• Daily commute distance
• Home charging ability
• Passenger/cargo needs
• FAME II subsidy eligibility

Visit Tata, Mahindra, Hyundai, MG dealers for test drives!""",
            'category': 'ev_types'
        },

        # Cold Weather
        r'(cold|winter|freeze|snow|ice|temperature|weather).*\?': {
            'response': """**EV Cold Weather Guide:**

❄️ **Cold Weather Impact:**
• Range can drop 20-40% in freezing temps
• Battery chemistry slows in cold
• Cabin heating uses extra energy
• Regenerative braking reduced

🔧 **Cold Weather Tips:**
• Pre-condition while plugged in
• Use heated seats vs cabin heat (more efficient)
• Keep battery above 20% when possible
• Park in garage when available
• Reduce highway speeds
• Use Eco mode

🔋 **Charging in Cold:**
• Cold batteries charge slower
• Some EVs have battery preconditioning
• Plan extra charging time
• Fast chargers may limit power

Modern EVs handle cold well - just plan ahead!""",
            'category': 'cold_weather'
        },

        # Safety
        r'(safe|safety|danger|fire|water|wet|flood).*\?': {
            'response': """**EV Safety Information:**

🛡️ **EV Safety Features:**
• Rigorous crash testing standards
• Battery protection in collision
• Automatic shutoff in accidents
• Lower center of gravity (less rollover risk)

⚡ **Battery Safety:**
• Modern batteries are very stable
• Extensive thermal management
• Protection systems built-in
• Rare fire risk compared to gas cars

💧 **Water Safety:**
• EVs handle water well
• High IP ratings for components
• Can drive through moderate flooding
• No risk of electric shock

🔌 **Charging Safety:**
• Weather-resistant connectors
• Ground fault protection
• Auto-shutoff if disconnected
• Safe in rain/snow

EVs are among the safest vehicles on the road!""",
            'category': 'safety'
        },

        # Regenerative Braking
        r'(regen|regenerative|brake|braking|one pedal).*\?': {
            'response': """**Regenerative Braking Explained:**

🔄 **What It Does:**
• Converts kinetic energy to electricity
• Charges battery when slowing/stopping
• Extends range by 5-20%
• Reduces wear on brake pads

⚡ **How It Works:**
• Lift off accelerator → car slows
• Energy captured = battery charge
• Feels like engine braking
• Adjustable in most EVs

🎮 **Using Regen Effectively:**
• One-pedal driving in city traffic
• Adjust regen level to preference
• Learn to modulate for smooth stops
• Different in different drive modes

📈 **Maximizing Benefits:**
• Use highest regen in city
• Anticipate stops early
• Coast on highways (less braking needed)
• Check efficiency stats in your EV

Regen is one of the best EV features!""",
            'category': 'regen'
        },
    }

    # Greeting patterns
    GREETING_RESPONSES = [
        "Hello! I'm your EV Charging Assistant. I can help you with:",
        "Hi there! Need help with your EV? I'm here to assist with:",
        "Hey! Welcome to EV Trip Planner. Ask me anything about:",
    ]

    HELPS = [
        "• 📍 Finding charging stations",
        "• 🗺️ Planning your trips",
        "• 🔋 Battery maintenance tips",
        "• ⚡ Charging information",
        "• 💰 Cost comparisons",
        "• 🚗 EV recommendations",
        "• And much more!",
    ]

    def __init__(self):
        self.default_response = """**I'm here to help with EV-related questions!**

Here's what I can assist with:

• Finding charging stations nearby
• Planning trips with charging stops
• Battery maintenance and care
• Charging times and costs
• Range and efficiency tips
• EV recommendations
• Troubleshooting common issues

**Try asking:**
• "How do I maintain my battery?"
• "Find charging stations near me"
• "How long does it take to charge?"
• "What affects my EV range?"
• "Is electric cheaper than gas?"

**Navigate the menu** to use our full suite of tools!"""

    def get_response(self, user_message, user_context=None):
        """
        Generate a response to user message

        Args:
            user_message: The user's input message
            user_context: Optional dict with user info (vehicles, location, etc.)

        Returns:
            Tuple of (response, category)
        """
        message = user_message.lower().strip()

        # Check for greetings
        if any(greeting in message for greeting in ['hi', 'hello', 'hey', 'greetings']):
            import random
            greeting = random.choice(self.GREETING_RESPONSES)
            helps = '\n'.join(self.HELPS)
            return (f"{greeting}\n\n{helps}\n\nHow can I help you today?", 'greeting')

        # Check for thank you
        if any(word in message for word in ['thank', 'thanks', 'appreciate']):
            return ("You're welcome! Is there anything else I can help you with regarding EV charging or trip planning?", 'thanks')

        # Check for bye
        if any(word in message for word in ['bye', 'goodbye', 'see you']):
            return ("Goodbye! Safe travels and happy charging! ⚡", 'goodbye')

        # Check FAQ patterns
        for pattern, data in self.FAQ_RESPONSES.items():
            if re.search(pattern, message, re.IGNORECASE):
                return (data['response'], data['category'])

        # Check for specific station queries
        if 'station' in message and any(word in message for word in ['near', 'close', 'around', 'find']):
            return (self.FAQ_RESPONSES[r'(find|where|near|locate|station|charger).*\?']['response'], 'find_stations')

        # Check for trip planning queries
        if 'trip' in message or 'plan' in message:
            return (self.FAQ_RESPONSES[r'(trip|plan|route|road trip|travel|journey).*\?']['response'], 'trip_planning')

        # Default response
        return (self.default_response, 'default')


# Global assistant instance
ev_assistant = EVAssistant()


def get_ai_response(user_message, user_context=None):
    """Convenience function to get AI response"""
    return ev_assistant.get_response(user_message, user_context)
