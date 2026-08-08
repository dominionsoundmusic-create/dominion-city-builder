#!/usr/bin/env python3
"""
Dominion Brand City Builder — Daily Auto-Builder
Runs daily on Render at 6 AM UTC
Builds 50 new city pages across ALL 4 brand sites simultaneously
Each city gets pages in all service folders for maximum SEO coverage
Pushes each brand to its own GitHub repo → Netlify auto-deploys
"""

import os, re, math, json, glob, shutil, subprocess
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
CITIES_PER_DAY = int(os.environ.get('CITIES_PER_DAY', '100'))
BASE_DIR = "/opt/render/project/src"

BRANDS = {
    "aivoice": {
        "repo": "dominionsoundmusic-create/aivoiceagentpros-site",
        "retired_folders": ['ai-voice-agent', 'ai-phone-answering', 'ai-customer-service', 'ai-sales-agent', 'ai-virtual-receptionist', 'ai-call-handling', 'ai-inbound-calls', 'ai-phone-agent', 'ai-phone-system', 'ai-voice-assistant', 'ai-voice-bot', 'ai-business-calls', 'automated-phone-calls', 'conversational-ai'],
        "work_dir": f"{BASE_DIR}/aivoice",
        "domain": "aivoiceagentpros.com",
        "color": "#7C3AED",
        "color_dark": "#6D28D9",
        "color_light": "#A78BFA",
        "color_bg": "#0A0A14",
        "color_bg2": "#111120",
        "color_border": "#1F1F35",
        "name": "AI Voice Agent Pros",
        "tagline": "AI That Answers Every Call. 24/7.",
        "cta": "Get Your AI Receptionist →",
        "cta_url": "#pricing",
        "phone": "903-636-7511",
        "starting_price": "$297/month",
        "pitch": "24/7 AI receptionist that answers every call, qualifies leads, and books appointments automatically",
        "favicon": "/favicon.svg",
        "service_folders": [
            ("ai-receptionist", "AI Receptionist"),
            ("ai-answering-service", "AI Answering Service"),
            ("ai-appointment-booking", "AI Appointment Booking"),
            ("ai-lead-qualification", "AI Lead Qualification"),
            ("ai-outbound-calls", "AI Outbound Calling"),
            ("ai-call-center", "AI Call Center"),
        ],
    },
    "reviewpro": {
        "repo": "dominionsoundmusic-create/dominionreviewpro-site",
        "retired_folders": ['5-star-reviews', 'get-more-google-reviews', 'reputation-management', 'google-business-reviews', 'review-generation-service', 'customer-review-automation', 'review-request-service', 'increase-google-reviews', 'business-review-management', 'local-business-reviews', 'local-seo-reviews', 'review-management-software', 'review-monitoring-service', 'google-review-service'],
        "work_dir": f"{BASE_DIR}/reviewpro",
        "domain": "dominionreviewpro.com",
        "color": "#059669",
        "color_dark": "#047857",
        "color_light": "#34D399",
        "color_bg": "#0A0F0A",
        "color_bg2": "#0F1A0F",
        "color_border": "#1A3A1A",
        "name": "Dominion Review Pro",
        "tagline": "More 5-Star Google Reviews. On Autopilot.",
        "cta": "Start Getting Reviews →",
        "cta_url": "#pricing",
        "phone": "903-636-7511",
        "starting_price": "$197/month",
        "pitch": "automated Google review system that follows up with customers and gets you more 5-star reviews every week",
        "favicon": "/favicon.svg",
        "service_folders": [
            ("google-review-management", "Google Review Management"),
            ("automated-review-requests", "Automated Review Requests"),
            ("online-reputation-management", "Online Reputation Management"),
            ("sms-review-requests", "SMS Review Requests"),
            ("negative-review-alerts", "Negative Review Alerts"),
            ("google-maps-ranking", "Google Maps Ranking"),
        ],
    },
    "aiagency": {
        "repo": "dominionsoundmusic-create/dominionaiagency-site",
        "retired_folders": ['ai-agency', 'ai-business-automation', 'ai-customer-automation', 'ai-digital-agency', 'ai-for-business', 'ai-growth-agency', 'ai-marketing-agency', 'ai-powered-agency', 'ai-sales-automation', 'ai-solutions', 'ai-tools-for-business', 'business-ai-automation', 'local-business-ai', 'small-business-ai'],
        "work_dir": f"{BASE_DIR}/aiagency",
        "domain": "dominionaiagency.com",
        "color": "#C9A84C",
        "color_dark": "#A8832A",
        "color_light": "#E8C97A",
        "color_bg": "#0A1628",
        "color_bg2": "#0F1E35",
        "color_border": "#1E3050",
        "name": "Dominion AI Agency",
        "tagline": "Full AI Automation for Local Businesses.",
        "cta": "Get Started with AI →",
        "cta_url": "#pricing",
        "phone": "903-636-7511",
        "starting_price": "$497/month",
        "pitch": "full AI automation including voice agents, CRM automation, lead generation, and reputation management",
        "favicon": "/favicon.svg",
        "service_folders": [
            ("ai-automation-agency", "AI Automation Agency"),
            ("ai-chatbot-agency", "AI Chatbot Development"),
            ("ai-lead-generation", "AI Lead Generation"),
            ("ai-workflow-automation", "AI Workflow Automation"),
            ("ai-crm-automation", "AI CRM Automation"),
            ("ai-consulting", "AI Consulting"),
        ],
    },
    "webdesign": {
        "repo": "dominionsoundmusic-create/dominionwebdesignpro-site",
        "retired_folders": ['website-design', 'custom-website-design', 'small-business-website', 'local-business-website', 'professional-website-design', 'affordable-web-design', 'business-website-design', 'seo-web-design', 'mobile-website-design', 'ecommerce-website-design', 'ai-website-design', 'website-designer', 'website-redesign', 'wordpress-web-design'],
        "work_dir": f"{BASE_DIR}/webdesign",
        "domain": "dominionwebdesignpro.com",
        "color": "#1D4ED8",
        "color_dark": "#1E40AF",
        "color_light": "#60A5FA",
        "color_bg": "#0A0A18",
        "color_bg2": "#0F0F22",
        "color_border": "#1E1E40",
        "name": "Dominion Web Design Pro",
        "tagline": "Professional Websites for Local Businesses.",
        "cta": "Get Your Free Demo →",
        "cta_url": "#pricing",
        "phone": "903-636-7511",
        "starting_price": "$497",
        "pitch": "professional custom website built first — you only pay when you love it, starting at $497 with SEO and mobile design included",
        "favicon": "/favicon.svg",
        "service_folders": [
            ("web-design", "Web Design"),
            ("lead-generation-website", "Lead Generation Websites"),
            ("contractor-website-design", "Contractor Web Design"),
            ("restaurant-website-design", "Restaurant Web Design"),
            ("medical-website-design", "Medical Web Design"),
            ("real-estate-website-design", "Real Estate Web Design"),
        ],
    },
    "hardmoney": {
        "repo": "dominionsoundmusic-create/dominion-hard-money",
        "excluded_states": ['NV', 'UT', 'SD', 'VT'],
        "retired_folders": ["texas"],
        "work_dir": "/opt/render/project/src/dominion-hard-money",
        "domain": "dominionhardmoney.com",
        "name": "Dominion Hard Money",
        "tagline": "Private Money for Real Estate Investors",
        "cta": "Apply Now",
        "phone": "nine zero three, six three six, seven five one one",
        "phone_display": "903-636-7511",
        "colors": {"primary": "#0a1628", "accent": "#c9a84c", "text": "#ffffff", "bg": "#f8f6f0"},
        "starting_price": "$50,000",
        "pitch": "Fast private money loans for fix and flip, DSCR rental, and bridge financing.",
        "favicon": "💰",
        "service_folders": [
            ("hard-money-loans", "Hard Money Loans"),
            ("fix-and-flip-loans", "Fix and Flip Loans"),
            ("bridge-loans", "Bridge Loans"),
            ("dscr-loans", "DSCR Rental Loans"),
            ("private-money-lender", "Private Money Lender"),
            ("rehab-loans", "Rehab Loans"),
            ("real-estate-investor-loans", "Real Estate Investor Loans"),
            ("hard-money-lender", "Hard Money Lender"),
        ],
    },
    "houstonwash": {
        "repo": "dominionsoundmusic-create/houston-powerwashing-pro",
        "metro_center": (29.7604, -95.3698),
        "metro_radius": 60,
        "work_dir": "/opt/render/project/src/houston-powerwashing-pro",
        "domain": "houston-powerwashing-pro.netlify.app",
        "name": "Houston Power Washing Pro",
        "tagline": "Professional Power Washing in Houston TX",
        "cta": "Get a Free Quote",
        "phone": "eight three two, six six two, four one zero seven",
        "phone_display": "832-662-4107",
        "colors": {"primary": "#0d1f3c", "accent": "#00c6ff", "text": "#ffffff", "bg": "#f5f8fc"},
        "starting_price": "$99",
        "pitch": "Professional power washing for driveways, fences, roofs, and decks across Houston and surrounding communities.",
        "favicon": "💧",
        "service_folders": [
            ("power-washing", "Power Washing"),
            ("pressure-washing", "Pressure Washing"),
            ("driveway-cleaning", "Driveway Cleaning"),
            ("fence-cleaning", "Fence Cleaning"),
            ("roof-soft-wash", "Roof Soft Wash"),
            ("deck-cleaning", "Deck Cleaning"),
        ],
    },
    "houstonhvac": {
        "repo": "dominionsoundmusic-create/houston-hvac-pro",
        "metro_center": (29.7604, -95.3698),
        "metro_radius": 60,
        "work_dir": "/opt/render/project/src/houston-hvac-pro",
        "domain": "stirring-gumdrop-4e30a6.netlify.app",
        "name": "Houston HVAC Pro",
        "tagline": "AC Repair and HVAC Service in Houston TX",
        "cta": "Call for Same-Day Service",
        "phone": "eight three two, six six two, four one zero seven",
        "phone_display": "832-662-4107",
        "colors": {"primary": "#0d2137", "accent": "#00b4d8", "text": "#ffffff", "bg": "#f0f4f8"},
        "starting_price": "$89",
        "pitch": "Fast AC repair, air conditioning installation, and 24/7 emergency HVAC service across Houston and surrounding communities.",
        "favicon": "❄️",
        "service_folders": [
            ("ac-repair", "AC Repair"),
            ("air-conditioning-repair", "Air Conditioning Repair"),
            ("ac-installation", "AC Installation"),
            ("emergency-ac-repair", "Emergency AC Repair"),
            ("hvac-tune-up", "HVAC Tune Up"),
            ("furnace-repair", "Furnace Repair"),
        ],
    },
    "houstonroofing": {
        "repo": "dominionsoundmusic-create/houston-roofing-pro",
        "metro_center": (29.7604, -95.3698),
        "metro_radius": 60,
        "work_dir": "/opt/render/project/src/houston-roofing-pro",
        "domain": "delicate-bavarois-59069c.netlify.app",
        "name": "Houston Roofing Pro",
        "tagline": "Roof Repair and Replacement in Houston TX",
        "cta": "Get Free Roof Inspection",
        "phone": "eight three two, six six two, four one zero seven",
        "phone_display": "832-662-4107",
        "colors": {"primary": "#12111a", "accent": "#c9a84c", "text": "#ffffff", "bg": "#f8f7f2"},
        "starting_price": "Free Inspection",
        "pitch": "Expert roof repair, replacement, and storm damage restoration across Houston and surrounding communities. Free inspections. Insurance claims handled.",
        "favicon": "🏠",
        "service_folders": [
            ("roof-repair", "Roof Repair"),
            ("roof-replacement", "Roof Replacement"),
            ("storm-damage-roof-repair", "Storm Damage Roof Repair"),
            ("hail-damage-roof-repair", "Hail Damage Roof Repair"),
            ("free-roof-inspection", "Free Roof Inspection"),
            ("roof-leak-repair", "Roof Leak Repair"),
        ],
    },
    "dallaswash": {
        "repo": "dominionsoundmusic-create/dallas-powerwashing-pro",
        "metro_center": (32.7767, -96.797),
        "metro_radius": 60,
        "work_dir": "/opt/render/project/src/dallas-powerwashing-pro",
        "domain": "dallaspowerwashingpro.com",
        "name": "Dallas Metro Power Washing Pro",
        "tagline": "Professional Power Washing in Dallas-Fort Worth TX",
        "cta": "Get a Free Quote",
        "phone": "four six nine, six four nine, seven zero six six",
        "phone_display": "469-649-7066",
        "colors": {"primary": "#0d1f3c", "accent": "#00c6ff", "text": "#ffffff", "bg": "#f5f8fc"},
        "starting_price": "$99",
        "pitch": "Professional power washing for driveways, fences, roofs, and decks across Dallas-Fort Worth and all surrounding communities.",
        "favicon": "💧",
        "service_folders": [
            ("power-washing", "Power Washing"),
            ("pressure-washing", "Pressure Washing"),
            ("driveway-cleaning", "Driveway Cleaning"),
            ("fence-cleaning", "Fence Cleaning"),
            ("roof-soft-wash", "Roof Soft Wash"),
            ("deck-cleaning", "Deck Cleaning"),
        ],
    },
    "dallashvac": {
        "repo": "dominionsoundmusic-create/dallas-hvac-pro",
        "metro_center": (32.7767, -96.797),
        "metro_radius": 60,
        "work_dir": "/opt/render/project/src/dallas-hvac-pro",
        "domain": "dallasairandheating.com",
        "name": "Dallas Metro HVAC Pro",
        "tagline": "AC Repair and HVAC Service in Dallas-Fort Worth TX",
        "cta": "Call for Same-Day Service",
        "phone": "four six nine, six four nine, seven zero six six",
        "phone_display": "469-649-7066",
        "colors": {"primary": "#0d1f3a", "accent": "#00b4d8", "text": "#ffffff", "bg": "#f0f4f8"},
        "starting_price": "$89",
        "pitch": "Fast AC repair, air conditioning installation, and 24/7 emergency HVAC service across Dallas-Fort Worth and all surrounding communities.",
        "favicon": "❄️",
        "service_folders": [
            ("ac-repair", "AC Repair"),
            ("air-conditioning-repair", "Air Conditioning Repair"),
            ("ac-installation", "AC Installation"),
            ("emergency-ac-repair", "Emergency AC Repair"),
            ("hvac-tune-up", "HVAC Tune Up"),
            ("furnace-repair", "Furnace Repair"),
        ],
    },
    "dallasroofing": {
        "repo": "dominionsoundmusic-create/dallas-roofing-pro",
        "metro_center": (32.7767, -96.797),
        "metro_radius": 60,
        "work_dir": "/opt/render/project/src/dallas-roofing-pro",
        "domain": "dfwexpertroofers.com",
        "name": "Dallas Metro Roofing Pro",
        "tagline": "Roof Repair and Replacement in Dallas-Fort Worth TX",
        "cta": "Get Free Roof Inspection",
        "phone": "four six nine, six four nine, seven zero six six",
        "phone_display": "469-649-7066",
        "colors": {"primary": "#12111a", "accent": "#c9a84c", "text": "#ffffff", "bg": "#f8f7f2"},
        "starting_price": "Free Inspection",
        "pitch": "Expert roof repair, replacement, and hail damage restoration across Dallas-Fort Worth. Free inspections. Insurance claims handled. 25-year warranty.",
        "favicon": "🏠",
        "service_folders": [
            ("roof-repair", "Roof Repair"),
            ("roof-replacement", "Roof Replacement"),
            ("hail-damage-roof-repair", "Hail Damage Roof Repair"),
            ("storm-damage-roof-repair", "Storm Damage Roof Repair"),
            ("free-roof-inspection", "Free Roof Inspection"),
            ("roof-leak-repair", "Roof Leak Repair"),
        ],
    },
    'phoenixpool': {
        'repo': 'dominionsoundmusic-create/phoenix-pool-cleaning-pro',
        'metro_center': (33.4484, -112.0740),
        'metro_radius': 50,
        'work_dir': '/opt/render/project/src/phoenix-pool-cleaning-pro',
        'domain': 'superlative-mandazi-aa17b9.netlify.app',
        'name': 'Phoenix Pool Cleaning Pro',
        'tagline': 'Professional Pool Cleaning & Maintenance',
        'cta': 'Get a Free Quote',
        'phone': 'nine zero three, six three six, seven five one one',
        'phone_display': '903-636-7511',
        'colors': {'primary': '#0c1a2e', 'accent': '#0ea5e9', 'text': '#ffffff', 'bg': '#f0f9ff'},
        'starting_price': 'From $99/month',
        'pitch': 'Professional pool cleaning, chemical balancing, algae treatment, and equipment repair across the Phoenix metro. Weekly service available. Licensed and insured.',
        'favicon': '🏊',
        'service_folders': [
            ('weekly-pool-cleaning', 'Weekly Pool Cleaning'),
            ('pool-chemical-balancing', 'Pool Chemical Balancing'),
            ('algae-treatment', 'Pool Algae Treatment'),
            ('pool-equipment-repair', 'Pool Equipment Repair'),
            ('pool-cleaning-service', 'Pool Cleaning Service'),
            ('pool-maintenance', 'Pool Maintenance'),
            ('swimming-pool-service', 'Swimming Pool Service'),
            ('pool-cleaning-near-me', 'Pool Cleaning Near Me'),
        ],
    },
    'tucsonpool': {
        'repo': 'dominionsoundmusic-create/tucson-pool-cleaning-pro',
        'metro_center': (32.2226, -110.9747),
        'metro_radius': 60,
        'work_dir': '/opt/render/project/src/tucson-pool-cleaning-pro',
        'domain': 'superb-cendol-81e0e8.netlify.app',
        'name': 'Tucson Pool Cleaning Pro',
        'tagline': 'Professional Pool Cleaning & Maintenance',
        'cta': 'Get a Free Quote',
        'phone': 'nine zero three, six three six, seven five one one',
        'phone_display': '903-636-7511',
        'colors': {'primary': '#1a0e08', 'accent': '#e07040', 'text': '#ffffff', 'bg': '#fdf6f0'},
        'starting_price': 'From $99/month',
        'pitch': 'Professional pool cleaning, chemical balancing, algae treatment, and equipment repair across the Tucson metro. Weekly service available. Licensed and insured.',
        'favicon': '🌵',
        'service_folders': [
            ('weekly-pool-cleaning', 'Weekly Pool Cleaning'),
            ('pool-chemical-balancing', 'Pool Chemical Balancing'),
            ('algae-treatment', 'Pool Algae Treatment'),
            ('pool-equipment-repair', 'Pool Equipment Repair'),
            ('pool-cleaning-service', 'Pool Cleaning Service'),
            ('pool-maintenance', 'Pool Maintenance'),
            ('swimming-pool-service', 'Swimming Pool Service'),
            ('pool-cleaning-near-me', 'Pool Cleaning Near Me'),
        ],
    },
    'yumapool': {
        'repo': 'dominionsoundmusic-create/arizona-pool-cleaning-pro',
        'metro_center': (32.6927, -114.6277),
        'metro_radius': 65,
        'metro_states': ('AZ',),
        'work_dir': '/opt/render/project/src/arizona-pool-cleaning-pro',
        'domain': 'majestic-youtiao-97786f.netlify.app',
        'name': 'Yuma Pool Cleaning Pro',
        'tagline': 'Professional Pool Cleaning & Maintenance',
        'cta': 'Get a Free Quote',
        'phone': 'nine zero three, six three six, seven five one one',
        'phone_display': '903-636-7511',
        'colors': {'primary': '#0a1f1c', 'accent': '#0d9488', 'text': '#ffffff', 'bg': '#f0fdfa'},
        'starting_price': 'From $99/month',
        'pitch': 'Professional pool cleaning, chemical balancing, algae treatment, and equipment repair across Yuma County. Weekly service available. Licensed and insured.',
        'favicon': '\U0001F31E',
        'service_folders': [
            ('weekly-pool-cleaning', 'Weekly Pool Cleaning'),
            ('pool-chemical-balancing', 'Pool Chemical Balancing'),
            ('algae-treatment', 'Pool Algae Treatment'),
            ('pool-equipment-repair', 'Pool Equipment Repair'),
            ('pool-cleaning-service', 'Pool Cleaning Service'),
            ('pool-maintenance', 'Pool Maintenance'),
            ('swimming-pool-service', 'Swimming Pool Service'),
            ('pool-cleaning-near-me', 'Pool Cleaning Near Me'),
        ],
    },
    'solarpro': {
        'repo': 'dominionsoundmusic-create/dominionsolarpro-site',
        'retired_folders': ['solar-generator', 'portable-power-station', 'portable-solar-panels', 'rv-solar-generator', 'camping-solar-generator', 'home-backup-solar', 'off-grid-solar-generator', 'portable-solar-generator', 'jackery-affiliate', 'jackery-explorer', 'jackery-power-station', 'best-jackery-deals', 'best-portable-power-station', 'solar-generator-reviews', 'solar-generator-sale', 'emergency-power-station', 'solar-power-station'],
        'redirect_map': {'solar-generator': 'solar-generators', 'portable-power-station': 'portable-power-stations', 'portable-solar-panels': 'solar-panels', 'rv-solar-generator': 'solar-generator-for-rv', 'camping-solar-generator': 'solar-generator-for-camping', 'home-backup-solar': 'solar-generator-for-home-backup', 'off-grid-solar-generator': 'off-grid-solar-power', 'portable-solar-generator': 'portable-solar-power', 'jackery-affiliate': 'jackery-solar-generator', 'jackery-explorer': 'jackery-solar-generator', 'jackery-power-station': 'jackery-solar-generator', 'best-jackery-deals': 'best-solar-generator', 'best-portable-power-station': 'best-solar-generator', 'solar-generator-reviews': 'best-solar-generator', 'solar-generator-sale': 'best-solar-generator', 'emergency-power-station': 'solar-generator-for-home-backup', 'solar-power-station': 'portable-power-stations'},
        'work_dir': '/opt/render/project/src/dominionsolarpro-site',
        'domain': 'dominionsolarpro.com',
        'name': 'Dominion Solar Pro',
        'tagline': 'Jackery Solar Generators and Portable Power Stations',
        'cta': 'Shop Solar Generators',
        'phone': '',
        'colors': {'primary': '#1a2332', 'accent': '#f59e0b', 'text': '#ffffff', 'bg': '#f8fafc'},
        'starting_price': 'From $149',
        'pitch': 'Shop the best Jackery solar generators, portable power stations, and solar panels. Perfect for camping, RV, home backup, and off-grid living. Free shipping on all orders.',
        'favicon': '☀️',
        'service_folders': [
            ('solar-generators', 'Solar Generators'),
            ('portable-power-stations', 'Portable Power Stations'),
            ('solar-panels', 'Solar Panels'),
            ('jackery-solar-generator', 'Jackery Solar Generator'),
            ('best-solar-generator', 'Best Solar Generator'),
            ('solar-generator-for-camping', 'Solar Generator for Camping'),
            ('solar-generator-for-home-backup', 'Solar Generator for Home Backup'),
            ('solar-generator-for-rv', 'Solar Generator for RV'),
            ('off-grid-solar-power', 'Off Grid Solar Power'),
            ('portable-solar-power', 'Portable Solar Power'),
        ],
    },
}

# ============================================================
# FULL US CITY DATABASE
# ============================================================

ALL_US_CITIES = [
    ('New York', 'New York', 'NY', 'Capital Region', 'New York County', 40.7484, -73.9967),
    ('Los Angeles', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9731, -118.2479),
    ('Chicago', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.8858, -87.6181),
    ('Houston', 'Texas', 'TX', 'Southeast Texas', 'Fort Bend County', 29.5962, -95.4587),
    ('Philadelphia', 'Pennsylvania', 'PA', 'Southeast Pennsylvania', 'Delaware County', 39.865, -75.2752),
    ('Phoenix', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.451, -112.0685),
    ('San Antonio', 'Texas', 'TX', 'South Texas', 'Bexar County', 29.4685, -98.5264),
    ('San Diego', 'California', 'CA', 'Southern California', 'San Diego County', 32.7185, -117.1593),
    ('Dallas', 'Texas', 'TX', 'North Texas', 'Collin County', 32.9968, -96.7921),
    ('San Jose', 'California', 'CA', 'Northern California', 'Santa Clara County', 37.3894, -121.8868),
    ('Austin', 'Texas', 'TX', 'Central Texas', 'Hays County', 30.2107, -97.9427),
    ('Indianapolis', 'Indiana', 'IN', 'Central Indiana', 'Hamilton County', 39.9384, -86.1389),
    ('Jacksonville', 'Florida', 'FL', 'Northeast Florida', 'Duval County', 30.3163, -81.4175),
    ('San Francisco', 'California', 'CA', 'Northern California', 'San Francisco County', 37.775, -122.4183),
    ('Columbus', 'Ohio', 'OH', 'Central Ohio', 'Delaware County', 40.1444, -82.9789),
    ('Charlotte', 'North Carolina', 'NC', 'Piedmont', 'Mecklenburg County', 35.2269, -80.8433),
    ('Fort Worth', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.7469, -97.3268),
    ('Detroit', 'Michigan', 'MI', 'Southeast Michigan', 'Wayne County', 42.3474, -83.0604),
    ('El Paso', 'Texas', 'TX', 'West Texas', 'El Paso County', 31.7584, -106.4783),
    ('Memphis', 'Tennessee', 'TN', 'West Tennessee', 'Shelby County', 35.0337, -89.9343),
    ('Seattle', 'Washington', 'WA', 'Puget Sound', 'King County', 47.6114, -122.3305),
    ('Denver', 'Colorado', 'CO', 'Front Range', 'Adams County', 39.8406, -105.008),
    ('Washington', 'District of Columbia', 'DC', 'Mid-Atlantic', 'District Of Columbia County', 38.9122, -77.0177),
    ('Boston', 'Massachusetts', 'MA', 'Greater Boston', 'Suffolk County', 42.3576, -71.0684),
    ('Nashville', 'Tennessee', 'TN', 'Middle Tennessee', 'Davidson County', 36.167, -86.7784),
    ('Baltimore', 'Maryland', 'MD', 'Central Maryland', 'Anne Arundel County', 39.1718, -76.6483),
    ('Oklahoma City', 'Oklahoma', 'OK', 'Central Oklahoma', 'Cleveland County', 35.3337, -97.4922),
    ('Louisville', 'Kentucky', 'KY', 'North Central Kentucky', 'Jefferson County', 38.2435, -85.7639),
    ('Portland', 'Oregon', 'OR', 'Willamette Valley', 'Clackamas County', 45.4429, -122.6151),
    ('Las Vegas', 'Nevada', 'NV', 'Southern Nevada', 'Clark County', 36.1721, -115.1224),
    ('Milwaukee', 'Wisconsin', 'WI', 'Southeast Wisconsin', 'Milwaukee County', 43.0343, -87.9151),
    ('Albuquerque', 'New Mexico', 'NM', 'Central New Mexico', 'Bernalillo County', 35.0936, -106.6423),
    ('Tucson', 'Arizona', 'AZ', 'Southern Arizona', 'Pima County', 32.2139, -110.9694),
    ('Fresno', 'California', 'CA', 'Central California', 'Fresno County', 36.8411, -119.8004),
    ('Sacramento', 'California', 'CA', 'Central California', 'Sacramento County', 38.5816, -121.4933),
    ('Long Beach', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.7705, -118.1885),
    ('Kansas City', 'Missouri', 'MO', 'Western Missouri', 'Clay County', 39.1632, -94.5699),
    ('Mesa', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.4317, -111.8469),
    ('Virginia Beach', 'Virginia', 'VA', 'Hampton Roads', 'Virginia Beach City County', 36.8527, -75.9783),
    ('Atlanta', 'Georgia', 'GA', 'Metro Atlanta', 'Dekalb County', 33.7498, -84.3169),
    ('Colorado Springs', 'Colorado', 'CO', 'Front Range', 'El Paso County', 38.8335, -104.8206),
    ('Omaha', 'Nebraska', 'NE', 'Eastern Nebraska', 'Douglas County', 41.261, -95.9376),
    ('Raleigh', 'North Carolina', 'NC', 'Triangle', 'Wake County', 35.7727, -78.6324),
    ('Miami', 'Florida', 'FL', 'Southeast Florida', 'Miami-dade County', 25.779, -80.1982),
    ('Oakland', 'California', 'CA', 'Northern California', 'Alameda County', 37.7806, -122.2166),
    ('Minneapolis', 'Minnesota', 'MN', 'Twin Cities', 'Anoka County', 45.0496, -93.2461),
    ('Tulsa', 'Oklahoma', 'OK', 'Northeast Oklahoma', 'Creek County', 36.0557, -96.0602),
    ('Cleveland', 'Ohio', 'OH', 'Northeast Ohio', 'Cuyahoga County', 41.4918, -81.6757),
    ('Wichita', 'Kansas', 'KS', 'South Central Kansas', 'Sedgwick County', 37.6898, -97.3415),
    ('Arlington', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.6336, -97.1469),
    ('New Orleans', 'Louisiana', 'LA', 'Southeast Louisiana', 'Jefferson County', 29.9631, -90.161),
    ('Bakersfield', 'California', 'CA', 'Central California', 'Kern County', 35.3866, -119.0171),
    ('Honolulu', 'Hawaii', 'HI', 'Oahu', 'Honolulu County', 21.3095, -157.863),
    ('Aurora', 'Colorado', 'CO', 'Front Range', 'Adams County', 39.7378, -104.8152),
    ('Anaheim', 'California', 'CA', 'Southern California', 'Orange County', 33.8427, -117.954),
    ('Santa Ana', 'California', 'CA', 'Southern California', 'Orange County', 33.7502, -117.8577),
    ('Riverside', 'California', 'CA', 'Southern California', 'Riverside County', 33.9924, -117.3694),
    ('Corpus Christi', 'Texas', 'TX', 'Coastal Texas', 'Nueces County', 27.7941, -97.403),
    ('Pittsburgh', 'Pennsylvania', 'PA', 'Western Pennsylvania', 'Allegheny County', 40.4745, -79.9525),
    ('Anchorage', 'Alaska', 'AK', 'Southcentral Alaska', 'Anchorage County', 61.2116, -149.8761),
    ('Stockton', 'California', 'CA', 'Central California', 'San Joaquin County', 37.958, -121.2876),
    ('Cincinnati', 'Ohio', 'OH', 'Southwest Ohio', 'Clermont County', 39.0913, -84.2774),
    ('Toledo', 'Ohio', 'OH', 'Northwest Ohio', 'Lucas County', 41.642, -83.5438),
    ('Greensboro', 'North Carolina', 'NC', 'Piedmont Triad', 'Caswell County', 36.0726, -79.792),
    ('Newark', 'New Jersey', 'NJ', 'Northeast New Jersey', 'Essex County', 40.7308, -74.1744),
    ('Plano', 'Texas', 'TX', 'North Texas', 'Collin County', 33.055, -96.7365),
    ('Henderson', 'Nevada', 'NV', 'Southern Nevada', 'Clark County', 35.9927, -114.9517),
    ('Lincoln', 'Nebraska', 'NE', 'Eastern Nebraska', 'Lancaster County', 40.8169, -96.7103),
    ('Buffalo', 'New York', 'NY', 'Western New York', 'Erie County', 42.8967, -78.8846),
    ('Jersey City', 'New Jersey', 'NJ', 'Northeast New Jersey', 'Hudson County', 40.7164, -74.038),
    ('Chula Vista', 'California', 'CA', 'Southern California', 'San Diego County', 32.64, -117.0833),
    ('Fort Wayne', 'Indiana', 'IN', 'Northeast Indiana', 'Allen County', 41.0716, -85.1367),
    ('Orlando', 'Florida', 'FL', 'Central Florida', 'Brevard County', 28.4988, -80.5825),
    ('Chandler', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.3301, -111.8632),
    ('Laredo', 'Texas', 'TX', 'South Texas', 'Webb County', 27.5155, -99.4986),
    ('Norfolk', 'Virginia', 'VA', 'Hampton Roads', 'Norfolk City County', 36.8466, -76.2855),
    ('Durham', 'North Carolina', 'NC', 'Triangle', 'Durham County', 35.9967, -78.8966),
    ('Madison', 'Wisconsin', 'WI', 'South Central Wisconsin', 'Dane County', 43.073, -89.3817),
    ('Lubbock', 'Texas', 'TX', 'West Texas', 'Lubbock County', 33.5865, -101.8606),
    ('Irvine', 'California', 'CA', 'Southern California', 'Orange County', 33.7357, -117.7672),
    ('Glendale', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.5311, -112.1767),
    ('Garland', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.9227, -96.6248),
    ('Hialeah', 'Florida', 'FL', 'Southeast Florida', 'Miami-dade County', 25.905, -80.3049),
    ('Reno', 'Nevada', 'NV', 'Northern Nevada', 'Washoe County', 39.5268, -119.8113),
    ('Chesapeake', 'Virginia', 'VA', 'Hampton Roads', 'Chesapeake City County', 36.7352, -76.2384),
    ('Gilbert', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.35, -111.8092),
    ('Baton Rouge', 'Louisiana', 'LA', 'South Central Louisiana', 'East Baton Rouge County', 30.4507, -91.187),
    ('Irving', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.842, -96.9719),
    ('Scottsdale', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.5218, -111.9049),
    ('North Las Vegas', 'Nevada', 'NV', 'Southern Nevada', 'Clark County', 36.4475, -114.8514),
    ('Fremont', 'California', 'CA', 'Southern California', 'Alameda County', 37.5605, -121.9999),
    ('Richmond', 'Virginia', 'VA', 'Central Virginia', 'Chesterfield County', 37.4532, -77.4698),
    ('San Bernardino', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.1105, -117.2898),
    ('Birmingham', 'Alabama', 'AL', 'North Central Alabama', 'Jefferson County', 33.519, -86.8014),
    ('Spokane', 'Washington', 'WA', 'Eastern Washington', 'Spokane County', 47.6665, -117.4365),
    ('Rochester', 'New York', 'NY', 'Finger Lakes', 'Monroe County', 43.1683, -77.6026),
    ('Modesto', 'California', 'CA', 'Central California', 'Stanislaus County', 37.6746, -121.0113),
    ('Fayetteville', 'North Carolina', 'NC', 'Sandhills', 'Cumberland County', 35.051, -78.8423),
    ('Tacoma', 'Washington', 'WA', 'Puget Sound', 'Pierce County', 47.2764, -122.7583),
    ('Oxnard', 'California', 'CA', 'Southern California', 'Ventura County', 34.2141, -119.175),
    ('Fontana', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.0589, -117.4383),
    ('Columbus', 'Georgia', 'GA', 'West Georgia', 'Muscogee County', 32.473, -84.9795),
    ('Montgomery', 'Alabama', 'AL', 'Central Alabama', 'Montgomery County', 32.3743, -86.3118),
    ('Moreno Valley', 'California', 'CA', 'Southern California', 'Riverside County', 33.8858, -117.2211),
    ('Shreveport', 'Louisiana', 'LA', 'Northwest Louisiana', 'Caddo County', 32.5037, -93.7487),
    ('Aurora', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.7826, -88.2607),
    ('Yonkers', 'New York', 'NY', 'New York Metro', 'Westchester County', 40.9407, -73.8883),
    ('Akron', 'Ohio', 'OH', 'Northeast Ohio', 'Summit County', 41.0449, -81.52),
    ('Huntington Beach', 'California', 'CA', 'Southern California', 'Orange County', 33.7152, -118.0088),
    ('Little Rock', 'Arkansas', 'AR', 'Central Arkansas', 'Pulaski County', 34.7483, -92.2819),
    ('Amarillo', 'Texas', 'TX', 'Panhandle Texas', 'Potter County', 35.2032, -101.8421),
    ('Glendale', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.1716, -118.2899),
    ('Mobile', 'Alabama', 'AL', 'South Alabama', 'Mobile County', 30.6959, -88.0434),
    ('Grand Rapids', 'Michigan', 'MI', 'West Michigan', 'Kent County', 42.9704, -85.6738),
    ('Salt Lake City', 'Utah', 'UT', 'Wasatch Front', 'Salt Lake County', 40.7559, -111.8967),
    ('Tallahassee', 'Florida', 'FL', 'North Florida', 'Leon County', 30.4286, -84.2593),
    ('Huntsville', 'Alabama', 'AL', 'North Alabama', 'Madison County', 34.7269, -86.5673),
    ('Grand Prairie', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.7649, -97.0112),
    ('Knoxville', 'Tennessee', 'TN', 'East Tennessee', 'Knox County', 35.9609, -83.9189),
    ('Worcester', 'Massachusetts', 'MA', 'Central Massachusetts', 'Worcester County', 42.2621, -71.8034),
    ('Newport News', 'Virginia', 'VA', 'Hampton Roads', 'Newport News City County', 37.058, -76.4607),
    ('Brownsville', 'Texas', 'TX', 'South Texas', 'Cameron County', 25.9337, -97.5174),
    ('Overland Park', 'Kansas', 'KS', 'Northeast Kansas', 'Johnson County', 38.9925, -94.6748),
    ('Santa Clarita', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.4597, -118.489),
    ('Providence', 'Rhode Island', 'RI', 'Providence County', 'Providence County', 41.8255, -71.4114),
    ('Garden Grove', 'California', 'CA', 'Southern California', 'Orange County', 33.7857, -117.9318),
    ('Chattanooga', 'Tennessee', 'TN', 'Southeast Tennessee', 'Hamilton County', 35.0455, -85.3081),
    ('Oceanside', 'California', 'CA', 'Southern California', 'San Diego County', 33.1951, -117.3776),
    ('Jackson', 'Mississippi', 'MS', 'Central Mississippi', 'Hinds County', 32.2935, -90.1867),
    ('Fort Lauderdale', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.1216, -80.1288),
    ('Santa Rosa', 'California', 'CA', 'Northern California', 'Sonoma County', 38.4431, -122.7517),
    ('Rancho Cucamonga', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.1339, -117.5991),
    ('Tempe', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.4273, -111.9307),
    ('Ontario', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.0631, -117.6197),
    ('Vancouver', 'Washington', 'WA', 'Southwest Washington', 'Clark County', 45.6418, -122.6801),
    ('Cape Coral', 'Florida', 'FL', 'Southwest Florida', 'Lee County', 26.5775, -81.9522),
    ('Sioux Falls', 'South Dakota', 'SD', 'Southeast South Dakota', 'Lincoln County', 43.488, -96.7343),
    ('Springfield', 'Missouri', 'MO', 'Southwest Missouri', 'Greene County', 37.2152, -93.295),
    ('Peoria', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.5761, -112.2344),
    ('Pembroke Pines', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.0229, -80.2974),
    ('Elk Grove', 'California', 'CA', 'Central California', 'Sacramento County', 38.4127, -121.3599),
    ('Salem', 'Oregon', 'OR', 'Willamette Valley', 'Marion County', 44.926, -122.9797),
    ('Lancaster', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.6909, -118.1491),
    ('Corona', 'California', 'CA', 'Southern California', 'Riverside County', 33.8815, -117.6078),
    ('Eugene', 'Oregon', 'OR', 'Willamette Valley', 'Lane County', 44.0737, -123.0788),
    ('Palmdale', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.5715, -118.0613),
    ('Salinas', 'California', 'CA', 'Central California', 'Monterey County', 36.6677, -121.6596),
    ('Springfield', 'Massachusetts', 'MA', 'Western Massachusetts', 'Hampden County', 42.106, -72.5977),
    ('Pasadena', 'Texas', 'TX', 'Southeast Texas', 'Harris County', 29.692, -95.2005),
    ('Fort Collins', 'Colorado', 'CO', 'Northern Colorado', 'Larimer County', 40.5813, -105.1039),
    ('Hayward', 'California', 'CA', 'Southern California', 'Alameda County', 37.6564, -122.0957),
    ('Pomona', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0433, -117.7521),
    ('Cary', 'North Carolina', 'NC', 'Triangle', 'Wake County', 35.7641, -78.7786),
    ('Rockford', 'Illinois', 'IL', 'Northern Illinois', 'Winnebago County', 42.2922, -89.1161),
    ('Alexandria', 'Virginia', 'VA', 'Northern Virginia', 'Alexandria City County', 38.82, -77.0589),
    ('Escondido', 'California', 'CA', 'Southern California', 'San Diego County', 33.1101, -117.07),
    ('McKinney', 'Texas', 'TX', 'North Texas', 'Collin County', 33.1966, -96.6085),
    ('Kansas City', 'Kansas', 'KS', 'Northeast Kansas', 'Wyandotte County', 39.1157, -94.6271),
    ('Joliet', 'Illinois', 'IL', 'Northeast Illinois', 'Will County', 41.5272, -88.0824),
    ('Sunnyvale', 'California', 'CA', 'Northern California', 'Santa Clara County', 37.3689, -122.0353),
    ('Torrance', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8268, -118.3118),
    ('Bridgeport', 'Connecticut', 'CT', 'South Central Connecticut', 'Fairfield County', 41.1669, -73.2052),
    ('Hollywood', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.007, -80.1219),
    ('Paterson', 'New Jersey', 'NJ', 'Northeast New Jersey', 'Passaic County', 40.9143, -74.1671),
    ('Naperville', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.7662, -88.141),
    ('Syracuse', 'New York', 'NY', 'Central New York', 'Onondaga County', 43.0459, -76.1528),
    ('Mesquite', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.7678, -96.6082),
    ('Dayton', 'Ohio', 'OH', 'Southwest Ohio', 'Greene County', 39.7654, -84.0998),
    ('Savannah', 'Georgia', 'GA', 'Coastal Georgia', 'Chatham County', 32.0676, -81.1024),
    ('Clarksville', 'Tennessee', 'TN', 'Middle Tennessee', 'Montgomery County', 36.522, -87.349),
    ('Orange', 'California', 'CA', 'Southern California', 'Orange County', 33.7877, -117.8755),
    ('Pasadena', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.1468, -118.1391),
    ('Fullerton', 'California', 'CA', 'Southern California', 'Orange County', 33.8796, -117.8951),
    ('Killeen', 'Texas', 'TX', 'Central Texas', 'Bell County', 31.117, -97.7261),
    ('Frisco', 'Texas', 'TX', 'North Texas', 'Collin County', 33.1506, -96.8233),
    ('Hampton', 'Virginia', 'VA', 'Hampton Roads', 'Hampton City County', 37.0065, -76.413),
    ('McAllen', 'Texas', 'TX', 'South Texas', 'Hidalgo County', 26.2154, -98.2359),
    ('Warren', 'Michigan', 'MI', 'Southeast Michigan', 'Macomb County', 42.5159, -82.9824),
    ('Bellevue', 'Washington', 'WA', 'Puget Sound', 'King County', 47.6199, -122.2074),
    ('Columbia', 'South Carolina', 'SC', 'Midlands', 'Lexington County', 34.0726, -81.1796),
    ('Olathe', 'Kansas', 'KS', 'Northeast Kansas', 'Johnson County', 38.8822, -94.8178),
    ('Sterling Heights', 'Michigan', 'MI', 'Southeast Michigan', 'Macomb County', 42.5648, -83.0701),
    ('New Haven', 'Connecticut', 'CT', 'South Central Connecticut', 'New Haven County', 41.308, -72.9286),
    ('Waco', 'Texas', 'TX', 'Central Texas', 'Mclennan County', 31.5525, -97.1396),
    ('Thousand Oaks', 'California', 'CA', 'Southern California', 'Ventura County', 34.1706, -118.8367),
    ('Cedar Rapids', 'Iowa', 'IA', 'Quad Cities', 'Linn County', 41.9743, -91.6554),
    ('Charleston', 'South Carolina', 'SC', 'Lowcountry', 'Berkeley County', 32.9622, -79.8653),
    ('Visalia', 'California', 'CA', 'Southern California', 'Tulare County', 36.3114, -119.3065),
    ('Topeka', 'Kansas', 'KS', 'Northeast Kansas', 'Shawnee County', 39.0541, -95.6719),
    ('Elizabeth', 'New Jersey', 'NJ', 'Northeast New Jersey', 'Union County', 40.6717, -74.2043),
    ('Gainesville', 'Florida', 'FL', 'North Central Florida', 'Alachua County', 29.645, -82.31),
    ('Roseville', 'California', 'CA', 'Southern California', 'Placer County', 38.7346, -121.234),
    ('Carrollton', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.9657, -96.8825),
    ('Stamford', 'Connecticut', 'CT', 'Southwest Connecticut', 'Fairfield County', 41.0531, -73.539),
    ('Simi Valley', 'California', 'CA', 'Southern California', 'Ventura County', 34.2694, -118.7805),
    ('Concord', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.9504, -122.0263),
    ('Hartford', 'Connecticut', 'CT', 'South Central Connecticut', 'Hartford County', 41.7636, -72.6855),
    ('Kent', 'Washington', 'WA', 'Puget Sound', 'King County', 47.3695, -122.1949),
    ('Lafayette', 'Louisiana', 'LA', 'South Central Louisiana', 'Lafayette County', 30.2361, -92.0083),
    ('Midland', 'Texas', 'TX', 'West Texas', 'Midland County', 31.9896, -102.0626),
    ('Surprise', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.63, -112.3314),
    ('Denton', 'Texas', 'TX', 'North Texas', 'Denton County', 33.2289, -97.1314),
    ('Victorville', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.5039, -117.3192),
    ('Evansville', 'Indiana', 'IN', 'Southwest Indiana', 'Vanderburgh County', 37.9746, -87.5674),
    ('Santa Clara', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.3473, -121.9541),
    ('Abilene', 'Texas', 'TX', 'West Texas', 'Taylor County', 32.4682, -99.7182),
    ('Vallejo', 'California', 'CA', 'Southern California', 'Solano County', 38.1483, -122.2493),
    ('Allentown', 'Pennsylvania', 'PA', 'Lehigh Valley', 'Lehigh County', 40.6027, -75.471),
    ('Norman', 'Oklahoma', 'OK', 'Central Oklahoma', 'Cleveland County', 35.2212, -97.4448),
    ('Beaumont', 'Texas', 'TX', 'Southeast Texas', 'Jefferson County', 30.0688, -94.1039),
    ('Independence', 'Missouri', 'MO', 'Central Missouri', 'Jackson County', 39.0983, -94.4111),
    ('Murfreesboro', 'Tennessee', 'TN', 'Middle Tennessee', 'Rutherford County', 35.7913, -86.357),
    ('Ann Arbor', 'Michigan', 'MI', 'Southeast Michigan', 'Washtenaw County', 42.2794, -83.784),
    ('Springfield', 'Illinois', 'IL', 'Central Illinois', 'Sangamon County', 39.8, -89.6495),
    ('Berkeley', 'California', 'CA', 'Southern California', 'Alameda County', 37.8691, -122.2696),
    ('Peoria', 'Illinois', 'IL', 'Northeast Illinois', 'Peoria County', 40.6854, -89.5953),
    ('Provo', 'Utah', 'UT', 'Wasatch Front', 'Utah County', 40.2319, -111.6755),
    ('El Monte', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0791, -118.0371),
    ('Columbia', 'Missouri', 'MO', 'Central Missouri', 'Boone County', 38.9382, -92.3049),
    ('Lansing', 'Michigan', 'MI', 'Mid-Michigan', 'Eaton County', 42.7335, -84.6391),
    ('Fargo', 'North Dakota', 'ND', 'Eastern North Dakota', 'Cass County', 46.9009, -96.7936),
    ('Downey', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.94, -118.1317),
    ('Costa Mesa', 'California', 'CA', 'Southern California', 'Orange County', 33.6777, -117.9096),
    ('Wilmington', 'North Carolina', 'NC', 'Cape Fear', 'New Hanover County', 34.2253, -77.9379),
    ('Arvada', 'Colorado', 'CO', 'Front Range', 'Jefferson County', 39.8039, -105.0859),
    ('Inglewood', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.955, -118.3556),
    ('Carlsbad', 'California', 'CA', 'Southern California', 'San Diego County', 33.1602, -117.325),
    ('Westminster', 'Colorado', 'CO', 'Front Range', 'Adams County', 39.8542, -105.0371),
    ('Rochester', 'Minnesota', 'MN', 'Southeast Minnesota', 'Olmsted County', 44.0496, -92.4896),
    ('Odessa', 'Texas', 'TX', 'West Texas', 'Ector County', 31.8465, -102.3663),
    ('Manchester', 'New Hampshire', 'NH', 'New Hampshire Region', 'Hillsborough County', 42.9929, -71.4633),
    ('Elgin', 'Illinois', 'IL', 'Northeast Illinois', 'Kane County', 42.0384, -88.2606),
    ('West Jordan', 'Utah', 'UT', 'Wasatch Front', 'Salt Lake County', 40.6254, -111.9677),
    ('Round Rock', 'Texas', 'TX', 'Central Texas', 'Williamson County', 30.5145, -97.668),
    ('Clearwater', 'Florida', 'FL', 'Tampa Bay', 'Pinellas County', 27.9799, -82.7806),
    ('Waterbury', 'Connecticut', 'CT', 'South Central Connecticut', 'New Haven County', 41.558, -73.0519),
    ('Gresham', 'Oregon', 'OR', 'Willamette Valley', 'Multnomah County', 45.5154, -122.4203),
    ('Fairfield', 'California', 'CA', 'Southern California', 'Solano County', 38.2671, -122.0357),
    ('Billings', 'Montana', 'MT', 'South Central Montana', 'Yellowstone County', 45.7745, -108.5005),
    ('Lowell', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.656, -71.3051),
    ('Pueblo', 'Colorado', 'CO', 'Southern Colorado', 'Pueblo County', 38.2879, -104.5848),
    ('High Point', 'North Carolina', 'NC', 'Piedmont Triad', 'Guilford County', 35.9593, -80.0117),
    ('West Covina', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0673, -117.9366),
    ('Richmond', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.94, -122.362),
    ('Murrieta', 'California', 'CA', 'Southern California', 'Riverside County', 33.5631, -117.2738),
    ('Cambridge', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.377, -71.1256),
    ('Antioch', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.9939, -121.8089),
    ('Temecula', 'California', 'CA', 'Southern California', 'Riverside County', 33.4936, -117.1475),
    ('Norwalk', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9056, -118.0818),
    ('Everett', 'Washington', 'WA', 'Puget Sound', 'Snohomish County', 47.9884, -122.2006),
    ('Wichita Falls', 'Texas', 'TX', 'North Texas', 'Wichita County', 33.9053, -98.4976),
    ('Palm Bay', 'Florida', 'FL', 'Space Coast', 'Brevard County', 28.0146, -80.5991),
    ('Green Bay', 'Wisconsin', 'WI', 'Northeast Wisconsin', 'Brown County', 44.4853, -88.0169),
    ('Daly City', 'California', 'CA', 'Southern California', 'San Mateo County', 37.7074, -122.4587),
    ('Burbank', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.1862, -118.3009),
    ('Richardson', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.966, -96.7452),
    ('Pompano Beach', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.2315, -80.1235),
    ('North Charleston', 'South Carolina', 'SC', 'Lowcountry', 'Berkeley County', 33.0562, -80.0759),
    ('Broken Arrow', 'Oklahoma', 'OK', 'Northeast Oklahoma', 'Tulsa County', 35.9908, -95.8143),
    ('Boulder', 'Colorado', 'CO', 'Front Range', 'Boulder County', 40.0497, -105.2143),
    ('West Palm Beach', 'Florida', 'FL', 'Southeast Florida', 'Palm Beach County', 26.714, -80.0659),
    ('Santa Maria', 'California', 'CA', 'Southern California', 'Santa Barbara County', 34.9545, -120.4325),
    ('El Cajon', 'California', 'CA', 'Southern California', 'San Diego County', 32.7777, -116.9191),
    ('Davenport', 'Iowa', 'IA', 'Quad Cities', 'Scott County', 41.5218, -90.5743),
    ('Rialto', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.1132, -117.3771),
    ('Las Cruces', 'New Mexico', 'NM', 'Central New Mexico', 'Dona Ana County', 32.3216, -106.746),
    ('San Mateo', 'California', 'CA', 'Southern California', 'San Mateo County', 37.5723, -122.3203),
    ('Lewisville', 'Texas', 'TX', 'North Texas', 'Denton County', 33.0461, -96.9939),
    ('South Bend', 'Indiana', 'IN', 'North Central Indiana', 'St Joseph County', 41.6727, -86.2535),
    ('Lakeland', 'Florida', 'FL', 'Central Florida', 'Polk County', 28.0381, -81.9392),
    ('Erie', 'Pennsylvania', 'PA', 'Northwest Pennsylvania', 'Erie County', 42.126, -80.086),
    ('Tyler', 'Texas', 'TX', 'East Texas', 'Smith County', 32.3254, -95.2922),
    ('Pearland', 'Texas', 'TX', 'Southeast Texas', 'Brazoria County', 29.5617, -95.2721),
    ('College Station', 'Texas', 'TX', 'Central Texas', 'Brazos County', 30.6045, -96.3123),
    ('Kenosha', 'Wisconsin', 'WI', 'Fox Valley', 'Kenosha County', 42.6052, -87.8299),
    ('Clovis', 'California', 'CA', 'Southern California', 'Fresno County', 36.8243, -119.6824),
    ('Flint', 'Michigan', 'MI', 'Mid-Michigan', 'Genesee County', 43.0233, -83.6856),
    ('Roanoke', 'Virginia', 'VA', 'Southwest Virginia', 'Botetourt County', 37.2725, -79.953),
    ('Albany', 'New York', 'NY', 'Capital Region', 'Albany County', 42.6525, -73.7566),
    ('Compton', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8907, -118.239),
    ('San Angelo', 'Texas', 'TX', 'West Texas', 'Tom Green County', 31.4782, -100.4818),
    ('Hillsboro', 'Oregon', 'OR', 'Willamette Valley', 'Washington County', 45.4984, -122.957),
    ('Lawton', 'Oklahoma', 'OK', 'Northeast Oklahoma', 'Comanche County', 34.5915, -98.3698),
    ('Renton', 'Washington', 'WA', 'Puget Sound', 'King County', 47.4648, -122.2075),
    ('Vista', 'California', 'CA', 'Southern California', 'San Diego County', 33.1694, -117.242),
    ('Greeley', 'Colorado', 'CO', 'Front Range', 'Weld County', 40.414, -104.7048),
    ('Mission Viejo', 'California', 'CA', 'Southern California', 'Orange County', 33.6, -117.6711),
    ('Portsmouth', 'Virginia', 'VA', 'Hampton Roads', 'Portsmouth City County', 36.8089, -76.3671),
    ('Dearborn', 'Michigan', 'MI', 'Southeast Michigan', 'Wayne County', 42.3053, -83.1605),
    ('South Gate', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9462, -118.2013),
    ('Tuscaloosa', 'Alabama', 'AL', 'Northeast Alabama', 'Tuscaloosa County', 33.1969, -87.5627),
    ('Livonia', 'Michigan', 'MI', 'Southeast Michigan', 'Wayne County', 42.3615, -83.3649),
    ('New Bedford', 'Massachusetts', 'MA', 'Greater Boston', 'Bristol County', 41.6347, -70.9372),
    ('Vacaville', 'California', 'CA', 'Southern California', 'Solano County', 38.3419, -121.9623),
    ('Brockton', 'Massachusetts', 'MA', 'Greater Boston', 'Plymouth County', 42.08, -71.0377),
    ('Roswell', 'Georgia', 'GA', 'Southwest Georgia', 'Fulton County', 34.0408, -84.3859),
    ('Beaverton', 'Oregon', 'OR', 'Willamette Valley', 'Washington County', 45.475, -122.8054),
    ('Quincy', 'Massachusetts', 'MA', 'Greater Boston', 'Norfolk County', 42.2491, -70.9978),
    ('Sparks', 'Nevada', 'NV', 'Northern Nevada', 'Washoe County', 39.5473, -119.7556),
    ('Yakima', 'Washington', 'WA', 'Puget Sound', 'Yakima County', 46.607, -120.4773),
    ('Federal Way', 'Washington', 'WA', 'Puget Sound', 'King County', 47.3203, -122.3117),
    ('Carson', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.823, -118.2684),
    ('Santa Monica', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0176, -118.4907),
    ('Hesperia', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.4264, -117.3),
    ('Allen', 'Texas', 'TX', 'North Texas', 'Collin County', 33.0934, -96.6454),
    ('Rio Rancho', 'New Mexico', 'NM', 'Central New Mexico', 'Sandoval County', 35.2493, -106.6818),
    ('Yuma', 'Arizona', 'AZ', 'Valley of the Sun', 'Yuma County', 32.7015, -114.6424),
    ('Westminster', 'California', 'CA', 'Southern California', 'Orange County', 33.7528, -117.9913),
    ('Orem', 'Utah', 'UT', 'Wasatch Front', 'Utah County', 40.3134, -111.6953),
    ('Lynn', 'Massachusetts', 'MA', 'Greater Boston', 'Essex County', 42.4634, -70.9455),
    ('Redding', 'California', 'CA', 'Southern California', 'Shasta County', 40.5605, -122.4116),
    ('Miami Beach', 'Florida', 'FL', 'Southeast Florida', 'Miami-dade County', 25.7611, -80.1403),
    ('League City', 'Texas', 'TX', 'Southeast Texas', 'Galveston County', 29.5173, -95.0963),
    ('Lawrence', 'Kansas', 'KS', 'Northeast Kansas', 'Douglas County', 38.9644, -95.2418),
    ('Santa Barbara', 'California', 'CA', 'Southern California', 'Santa Barbara County', 34.4197, -119.7078),
    ('Sandy', 'Utah', 'UT', 'Wasatch Front', 'Salt Lake County', 40.5794, -111.8816),
    ('Macon', 'Georgia', 'GA', 'Central Georgia', 'Bibb County', 32.8439, -83.5987),
    ('Longmont', 'Colorado', 'CO', 'Front Range', 'Boulder County', 40.1779, -105.1009),
    ('Boca Raton', 'Florida', 'FL', 'Southeast Florida', 'Palm Beach County', 26.3583, -80.0833),
    ('San Marcos', 'California', 'CA', 'Southern California', 'San Diego County', 33.1444, -117.1697),
    ('Greenville', 'North Carolina', 'NC', 'Eastern NC', 'Pitt County', 35.6594, -77.3974),
    ('Waukegan', 'Illinois', 'IL', 'Northeast Illinois', 'Lake County', 42.3636, -87.8447),
    ('Fall River', 'Massachusetts', 'MA', 'Greater Boston', 'Bristol County', 41.7182, -71.14),
    ('Chico', 'California', 'CA', 'Southern California', 'Butte County', 39.7565, -121.8518),
    ('Newton', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.3545, -71.1877),
    ('San Leandro', 'California', 'CA', 'Southern California', 'Alameda County', 37.7205, -122.1587),
    ('Reading', 'Pennsylvania', 'PA', 'Lehigh Valley', 'Berks County', 40.3466, -75.9351),
    ('Norwalk', 'Connecticut', 'CT', 'South Central Connecticut', 'Fairfield County', 41.1222, -73.4358),
    ('Fort Smith', 'Arkansas', 'AR', 'River Valley', 'Sebastian County', 35.3653, -94.411),
    ('Newport Beach', 'California', 'CA', 'Southern California', 'Orange County', 33.6398, -117.8643),
    ('Asheville', 'North Carolina', 'NC', 'Western NC', 'Buncombe County', 35.5971, -82.5565),
    ('Nashua', 'New Hampshire', 'NH', 'New Hampshire Region', 'Hillsborough County', 42.7564, -71.4667),
    ('Edmond', 'Oklahoma', 'OK', 'Central Oklahoma', 'Oklahoma County', 35.68, -97.53),
    ('Whittier', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0011, -118.0371),
    ('Nampa', 'Idaho', 'ID', 'Southwest Idaho', 'Canyon County', 43.5834, -116.5848),
    ('Deltona', 'Florida', 'FL', 'Southeast Florida', 'Volusia County', 28.8989, -81.2473),
    ('Hawthorne', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9132, -118.347),
    ('Duluth', 'Minnesota', 'MN', 'Northern Minnesota', 'Saint Louis County', 47.0944, -91.8467),
    ('Carmel', 'Indiana', 'IN', 'Central Indiana', 'Hamilton County', 39.9712, -86.1245),
    ('Suffolk', 'Virginia', 'VA', 'Northern Virginia', 'Suffolk City County', 36.8668, -76.5598),
    ('Clifton', 'New Jersey', 'NJ', 'Central New Jersey', 'Passaic County', 40.8789, -74.1425),
    ('Citrus Heights', 'California', 'CA', 'Southern California', 'Sacramento County', 38.6946, -121.2692),
    ('Livermore', 'California', 'CA', 'Southern California', 'Alameda County', 37.683, -121.763),
    ('Tracy', 'California', 'CA', 'Southern California', 'San Joaquin County', 37.7544, -121.3697),
    ('Alhambra', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0914, -118.1293),
    ('Kirkland', 'Washington', 'WA', 'Puget Sound', 'King County', 47.6786, -122.1894),
    ('Ogden', 'Utah', 'UT', 'Wasatch Front', 'Weber County', 41.2443, -112.0072),
    ('Cicero', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.8456, -87.7539),
    ('Fishers', 'Indiana', 'IN', 'Central Indiana', 'Hamilton County', 39.9573, -85.9457),
    ('Sugar Land', 'Texas', 'TX', 'Southeast Texas', 'Fort Bend County', 29.6342, -95.6219),
    ('Danbury', 'Connecticut', 'CT', 'South Central Connecticut', 'Fairfield County', 41.3917, -73.4532),
    ('Meridian', 'Idaho', 'ID', 'Southwest Idaho', 'Ada County', 43.615, -116.3975),
    ('Indio', 'California', 'CA', 'Southern California', 'Riverside County', 33.7219, -116.2357),
    ('Concord', 'North Carolina', 'NC', 'Piedmont', 'Cabarrus County', 35.3716, -80.53),
    ('Menifee', 'California', 'CA', 'Southern California', 'Riverside County', 33.6647, -117.1743),
    ('Champaign', 'Illinois', 'IL', 'Northeast Illinois', 'Champaign County', 40.111, -88.2407),
    ('Buena Park', 'California', 'CA', 'Southern California', 'Orange County', 33.8406, -118.0114),
    ('Troy', 'Michigan', 'MI', 'Southeast Michigan', 'Oakland County', 42.5609, -83.1471),
    ('Bellingham', 'Washington', 'WA', 'Northwest Washington', 'Whatcom County', 48.749, -122.4887),
    ('Westland', 'Michigan', 'MI', 'Southeast Michigan', 'Wayne County', 42.3189, -83.3749),
    ('Bloomington', 'Indiana', 'IN', 'South Central Indiana', 'Monroe County', 39.1401, -86.5083),
    ('Sioux City', 'Iowa', 'IA', 'Quad Cities', 'Woodbury County', 42.4972, -96.4029),
    ('Warwick', 'Rhode Island', 'RI', 'Providence County', 'Kent County', 41.7026, -71.4476),
    ('Hemet', 'California', 'CA', 'Southern California', 'Riverside County', 33.7416, -116.973),
    ('Longview', 'Texas', 'TX', 'East Texas', 'Gregg County', 32.5269, -94.7233),
    ('Bend', 'Oregon', 'OR', 'Central Oregon', 'Deschutes County', 44.0928, -121.2936),
    ('Lakewood', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8517, -118.1328),
    ('Merced', 'California', 'CA', 'Southern California', 'Merced County', 37.3007, -120.4617),
    ('Mission', 'Texas', 'TX', 'South Texas', 'Hidalgo County', 26.2415, -98.3426),
    ('Chino', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.0122, -117.6881),
    ('Redwood City', 'California', 'CA', 'Southern California', 'San Mateo County', 37.4647, -122.2304),
    ('Edinburg', 'Texas', 'TX', 'South Texas', 'Hidalgo County', 26.3042, -98.1569),
    ('Cranston', 'Rhode Island', 'RI', 'Providence County', 'Providence County', 41.7766, -71.4383),
    ('New Rochelle', 'New York', 'NY', 'Capital Region', 'Westchester County', 40.9166, -73.7877),
    ('Lake Forest', 'California', 'CA', 'Southern California', 'Orange County', 33.64, -117.6882),
    ('Napa', 'California', 'CA', 'Southern California', 'Napa County', 38.3281, -122.3055),
    ('Hammond', 'Indiana', 'IN', 'Central Indiana', 'Lake County', 41.6099, -87.5079),
    ('Fayetteville', 'Arkansas', 'AR', 'Northwest Arkansas', 'Washington County', 36.052, -94.1534),
    ('Bloomington', 'Illinois', 'IL', 'Northeast Illinois', 'Mclean County', 40.4783, -88.9893),
    ('Avondale', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.4321, -112.3438),
    ('Somerville', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.3829, -71.1028),
    ('Palm Coast', 'Florida', 'FL', 'Southeast Florida', 'Flagler County', 29.5847, -81.208),
    ('Bryan', 'Texas', 'TX', 'Central Texas', 'Brazos County', 30.6327, -96.3662),
    ('Gary', 'Indiana', 'IN', 'Central Indiana', 'Lake County', 41.5933, -87.3464),
    ('Largo', 'Florida', 'FL', 'Southeast Florida', 'Pinellas County', 27.9163, -82.7996),
    ('Tustin', 'California', 'CA', 'Southern California', 'Orange County', 33.7382, -117.8207),
    ('Deerfield Beach', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.3096, -80.0992),
    ('Lynchburg', 'Virginia', 'VA', 'Central Virginia', 'Lynchburg City County', 37.3862, -79.1715),
    ('Mountain View', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.41, -122.0519),
    ('Medford', 'Oregon', 'OR', 'Willamette Valley', 'Jackson County', 42.3193, -122.887),
    ('Lawrence', 'Massachusetts', 'MA', 'Greater Boston', 'Essex County', 42.708, -71.1638),
    ('Bellflower', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8867, -118.1265),
    ('Melbourne', 'Florida', 'FL', 'Space Coast', 'Brevard County', 28.0691, -80.62),
    ('Camden', 'New Jersey', 'NJ', 'Central New Jersey', 'Camden County', 39.9258, -75.12),
    ('Kennewick', 'Washington', 'WA', 'Puget Sound', 'Benton County', 46.2109, -119.168),
    ('Baldwin Park', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0842, -117.9695),
    ('Chino Hills', 'California', 'CA', 'Southern California', 'San Bernardino County', 33.9797, -117.7308),
    ('Alameda', 'California', 'CA', 'Southern California', 'Alameda County', 37.7648, -122.2605),
    ('Albany', 'Georgia', 'GA', 'Southwest Georgia', 'Dougherty County', 31.5678, -84.1619),
    ('Arlington Heights', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.1116, -87.9791),
    ('Scranton', 'Pennsylvania', 'PA', 'Lehigh Valley', 'Lackawanna County', 41.3731, -75.6841),
    ('Evanston', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0546, -87.6943),
    ('Kalamazoo', 'Michigan', 'MI', 'Southeast Michigan', 'Kalamazoo County', 42.2736, -85.5457),
    ('Baytown', 'Texas', 'TX', 'Southeast Texas', 'Harris County', 29.7461, -94.9653),
    ('Upland', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.1368, -117.6598),
    ('Springdale', 'Arkansas', 'AR', 'Northwest Arkansas', 'Washington County', 36.1835, -94.1762),
    ('Bethlehem', 'Pennsylvania', 'PA', 'Lehigh Valley', 'Lehigh County', 40.6335, -75.3952),
    ('Schaumburg', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0333, -88.0833),
    ('Mount Pleasant', 'South Carolina', 'SC', 'Upstate', 'Charleston County', 32.8162, -79.852),
    ('Auburn', 'Washington', 'WA', 'Puget Sound', 'King County', 47.3163, -122.2701),
    ('Decatur', 'Illinois', 'IL', 'Northeast Illinois', 'Macon County', 39.8271, -88.926),
    ('San Ramon', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.78, -121.9769),
    ('Pleasanton', 'California', 'CA', 'Southern California', 'Alameda County', 37.6658, -121.8755),
    ('Wyoming', 'Michigan', 'MI', 'Southeast Michigan', 'Kent County', 42.9009, -85.7058),
    ('Lake Charles', 'Louisiana', 'LA', 'Central Louisiana', 'Calcasieu County', 30.2285, -93.188),
    ('Bolingbrook', 'Illinois', 'IL', 'Northeast Illinois', 'Will County', 41.6976, -88.0873),
    ('Pharr', 'Texas', 'TX', 'West Texas', 'Hidalgo County', 26.1771, -98.187),
    ('Appleton', 'Wisconsin', 'WI', 'Fox Valley', 'Outagamie County', 44.2773, -88.3976),
    ('Gastonia', 'North Carolina', 'NC', 'Piedmont', 'Gaston County', 35.2449, -81.2194),
    ('Folsom', 'California', 'CA', 'Southern California', 'Sacramento County', 38.6879, -121.1409),
    ('Southfield', 'Michigan', 'MI', 'Southeast Michigan', 'Oakland County', 42.463, -83.288),
    ('New Britain', 'Connecticut', 'CT', 'South Central Connecticut', 'Hartford County', 41.6611, -72.78),
    ('Goodyear', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.4368, -112.3834),
    ('Warner Robins', 'Georgia', 'GA', 'Southwest Georgia', 'Houston County', 32.5934, -83.6416),
    ('Union City', 'California', 'CA', 'Southern California', 'Alameda County', 37.5895, -122.0497),
    ('Perris', 'California', 'CA', 'Southern California', 'Riverside County', 33.7975, -117.28),
    ('Manteca', 'California', 'CA', 'Southern California', 'San Joaquin County', 37.8088, -121.2186),
    ('Iowa City', 'Iowa', 'IA', 'Quad Cities', 'Johnson County', 41.6549, -91.5112),
    ('Jonesboro', 'Arkansas', 'AR', 'Northeast Arkansas', 'Craighead County', 35.833, -90.6965),
    ('Wilmington', 'Delaware', 'DE', 'Delaware Region', 'New Castle County', 39.7378, -75.5497),
    ('Lynwood', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9241, -118.2013),
    ('Loveland', 'Colorado', 'CO', 'Front Range', 'Larimer County', 40.3849, -105.0916),
    ('Pawtucket', 'Rhode Island', 'RI', 'Providence County', 'Providence County', 41.8729, -71.3907),
    ('Boynton Beach', 'Florida', 'FL', 'Southeast Florida', 'Palm Beach County', 26.525, -80.0666),
    ('Waukesha', 'Wisconsin', 'WI', 'Fox Valley', 'Waukesha County', 42.9993, -88.2196),
    ('Gulfport', 'Mississippi', 'MS', 'Central Mississippi', 'Harrison County', 30.3826, -89.0976),
    ('Apple Valley', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.5291, -117.2132),
    ('Passaic', 'New Jersey', 'NJ', 'Central New Jersey', 'Passaic County', 40.8601, -74.1283),
    ('Rapid City', 'South Dakota', 'SD', 'Southeast South Dakota', 'Pennington County', 44.077, -103.2003),
    ('Layton', 'Utah', 'UT', 'Wasatch Front', 'Davis County', 41.0846, -111.9274),
    ('Lafayette', 'Indiana', 'IN', 'Central Indiana', 'Tippecanoe County', 40.4177, -86.8884),
    ('Turlock', 'California', 'CA', 'Southern California', 'Stanislaus County', 37.5036, -120.8505),
    ('Muncie', 'Indiana', 'IN', 'Central Indiana', 'Delaware County', 40.1684, -85.3807),
    ('Temple', 'Texas', 'TX', 'Central Texas', 'Bell County', 31.0895, -97.3343),
    ('Missouri City', 'Texas', 'TX', 'Southeast Texas', 'Fort Bend County', 29.5704, -95.5423),
    ('Redlands', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.0397, -117.1804),
    ('Santa Fe', 'New Mexico', 'NM', 'Central New Mexico', 'Santa Fe County', 35.7025, -105.9748),
    ('Milpitas', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.4365, -121.8929),
    ('Palatine', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.1258, -88.0764),
    ('Missoula', 'Montana', 'MT', 'South Central Montana', 'Missoula County', 46.8563, -114.0252),
    ('Rock Hill', 'South Carolina', 'SC', 'Piedmont', 'York County', 34.9151, -81.0129),
    ('Jacksonville', 'North Carolina', 'NC', 'Coastal Plain', 'Onslow County', 34.7375, -77.4628),
    ('Franklin', 'Tennessee', 'TN', 'Middle Tennessee', 'Williamson County', 35.9328, -86.8788),
    ('Flagstaff', 'Arizona', 'AZ', 'Northern Arizona', 'Coconino County', 35.1859, -111.662),
    ('Flower Mound', 'Texas', 'TX', 'North Texas', 'Denton County', 33.0238, -97.1044),
    ('Waterloo', 'Iowa', 'IA', 'Quad Cities', 'Black Hawk County', 42.4778, -92.3661),
    ('Union City', 'New Jersey', 'NJ', 'Central New Jersey', 'Hudson County', 40.7682, -74.0306),
    ('Mount Vernon', 'New York', 'NY', 'Capital Region', 'Westchester County', 40.9079, -73.838),
    ('Fort Myers', 'Florida', 'FL', 'Southwest Florida', 'Lee County', 26.6204, -81.8725),
    ('Dothan', 'Alabama', 'AL', 'Southeast Alabama', 'Houston County', 31.2029, -85.418),
    ('Rancho Cordova', 'California', 'CA', 'Southern California', 'Sacramento County', 38.6019, -121.2894),
    ('Redondo Beach', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8307, -118.3832),
    ('Jackson', 'Tennessee', 'TN', 'West Tennessee', 'Madison County', 35.6102, -88.814),
    ('Pasco', 'Washington', 'WA', 'Puget Sound', 'Franklin County', 46.2492, -119.1044),
    ('Eau Claire', 'Wisconsin', 'WI', 'Fox Valley', 'Eau Claire County', 44.784, -91.4877),
    ('North Richland Hills', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.854, -97.2207),
    ('Bismarck', 'North Dakota', 'ND', 'South Central ND', 'Burleigh County', 46.8234, -100.7748),
    ('Yorba Linda', 'California', 'CA', 'Southern California', 'Orange County', 33.8913, -117.8191),
    ('Kenner', 'Louisiana', 'LA', 'Central Louisiana', 'Jefferson County', 29.9912, -90.2479),
    ('Walnut Creek', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.8753, -122.0703),
    ('Frederick', 'Maryland', 'MD', 'Central Maryland', 'Frederick County', 39.4082, -77.4009),
    ('Oshkosh', 'Wisconsin', 'WI', 'Fox Valley', 'Winnebago County', 44.022, -88.5436),
    ('Pittsburg', 'California', 'CA', 'Southern California', 'Contra Costa County', 38.0169, -121.9082),
    ('Palo Alto', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.4443, -122.1497),
    ('Bossier City', 'Louisiana', 'LA', 'Central Louisiana', 'Bossier County', 32.5449, -93.7038),
    ('Portland', 'Maine', 'ME', 'Southern Maine', 'Cumberland County', 43.6606, -70.2589),
    ('Davis', 'California', 'CA', 'Southern California', 'Yolo County', 38.5548, -121.7485),
    ('South San Francisco', 'California', 'CA', 'Southern California', 'San Mateo County', 37.6538, -122.4347),
    ('Camarillo', 'California', 'CA', 'Southern California', 'Ventura County', 34.2313, -119.0464),
    ('North Little Rock', 'Arkansas', 'AR', 'Northwest Arkansas', 'Pulaski County', 34.767, -92.2654),
    ('Schenectady', 'New York', 'NY', 'Capital Region', 'Schenectady County', 42.8155, -73.9395),
    ('Gaithersburg', 'Maryland', 'MD', 'Central Maryland', 'Montgomery County', 39.1419, -77.189),
    ('Harlingen', 'Texas', 'TX', 'South Texas', 'Cameron County', 26.1951, -97.689),
    ('Yuba City', 'California', 'CA', 'Southern California', 'Sutter County', 39.1286, -121.6216),
    ('Youngstown', 'Ohio', 'OH', 'Northeast Ohio', 'Mahoning County', 41.0986, -80.6474),
    ('Skokie', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0362, -87.7328),
    ('Kissimmee', 'Florida', 'FL', 'Central Florida', 'Osceola County', 28.3051, -81.4242),
    ('Johnson City', 'Tennessee', 'TN', 'Northeast Tennessee', 'Washington County', 36.3339, -82.3408),
    ('Victoria', 'Texas', 'TX', 'West Texas', 'Victoria County', 28.809, -96.9993),
    ('San Clemente', 'California', 'CA', 'Southern California', 'Orange County', 33.4308, -117.6101),
    ('Bayonne', 'New Jersey', 'NJ', 'Central New Jersey', 'Hudson County', 40.6664, -74.1192),
    ('Laguna Niguel', 'California', 'CA', 'Southern California', 'Orange County', 33.5225, -117.7067),
    ('East Orange', 'New Jersey', 'NJ', 'Central New Jersey', 'Essex County', 40.7696, -74.2077),
    ('Shawnee', 'Kansas', 'KS', 'Northeast Kansas', 'Johnson County', 39.0198, -94.7083),
    ('Homestead', 'Florida', 'FL', 'Southeast Florida', 'Miami-dade County', 25.4766, -80.4839),
    ('Delray Beach', 'Florida', 'FL', 'Southeast Florida', 'Palm Beach County', 26.4564, -80.0793),
    ('Rockville', 'Maryland', 'MD', 'Central Maryland', 'Montgomery County', 39.0838, -77.153),
    ('Janesville', 'Wisconsin', 'WI', 'Fox Valley', 'Rock County', 42.6915, -89.0331),
    ('Conway', 'Arkansas', 'AR', 'Central Arkansas', 'Faulkner County', 35.0842, -92.4236),
    ('Pico Rivera', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9886, -118.0883),
    ('Lorain', 'Ohio', 'OH', 'Northeast Ohio', 'Lorain County', 41.4578, -82.171),
    ('Montebello', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0133, -118.113),
    ('Lodi', 'California', 'CA', 'Southern California', 'San Joaquin County', 38.1236, -121.263),
    ('New Braunfels', 'Texas', 'TX', 'South Texas', 'Comal County', 29.6947, -98.113),
    ('Marysville', 'Washington', 'WA', 'Puget Sound', 'Snohomish County', 48.0656, -122.1562),
    ('Madera', 'California', 'CA', 'Southern California', 'Madera County', 36.9528, -119.8806),
    ('Conroe', 'Texas', 'TX', 'Southeast Texas', 'Montgomery County', 30.3125, -95.4527),
    ('Santa Cruz', 'California', 'CA', 'Southern California', 'Santa Cruz County', 36.9829, -122.0436),
    ('Eden Prairie', 'Minnesota', 'MN', 'Twin Cities', 'Hennepin County', 44.8574, -93.4376),
    ('Cheyenne', 'Wyoming', 'WY', 'Wyoming Region', 'Laramie County', 41.1437, -104.7962),
    ('Daytona Beach', 'Florida', 'FL', 'East Central Florida', 'Volusia County', 29.2012, -81.0371),
    ('Alpharetta', 'Georgia', 'GA', 'Metro Atlanta', 'Fulton County', 34.1048, -84.2949),
    ('Hamilton', 'Ohio', 'OH', 'Northeast Ohio', 'Butler County', 39.4059, -84.5221),
    ('Waltham', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.3954, -71.2508),
    ('Haverhill', 'Massachusetts', 'MA', 'Greater Boston', 'Essex County', 42.7856, -71.0721),
    ('Council Bluffs', 'Iowa', 'IA', 'Quad Cities', 'Pottawattamie County', 41.253, -95.881),
    ('Taylor', 'Michigan', 'MI', 'Southeast Michigan', 'Wayne County', 42.2317, -83.2673),
    ('Utica', 'New York', 'NY', 'Mohawk Valley', 'Oneida County', 43.0871, -75.2315),
    ('Ames', 'Iowa', 'IA', 'Quad Cities', 'Story County', 42.0299, -93.6394),
    ('La Habra', 'California', 'CA', 'Southern California', 'Orange County', 33.9322, -117.9497),
    ('Encinitas', 'California', 'CA', 'Southern California', 'San Diego County', 33.0369, -117.2911),
    ('Bowling Green', 'Kentucky', 'KY', 'South Central Kentucky', 'Warren County', 37.0079, -86.4559),
    ('Burnsville', 'Minnesota', 'MN', 'Twin Cities', 'Dakota County', 44.7678, -93.2775),
    ('Greenville', 'South Carolina', 'SC', 'Upstate', 'Greenville County', 34.8472, -82.406),
    ('West Des Moines', 'Iowa', 'IA', 'Quad Cities', 'Polk County', 41.5805, -93.7447),
    ('Cedar Park', 'Texas', 'TX', 'Central Texas', 'Williamson County', 30.4772, -97.8176),
    ('Tulare', 'California', 'CA', 'Southern California', 'Tulare County', 36.2022, -119.338),
    ('Monterey Park', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0534, -118.1271),
    ('Vineland', 'New Jersey', 'NJ', 'Central New Jersey', 'Cumberland County', 39.4818, -75.0091),
    ('Mansfield', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.5773, -97.1416),
    ('Bristol', 'Connecticut', 'CT', 'South Central Connecticut', 'Hartford County', 41.6823, -72.9302),
    ('Malden', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.4291, -71.0605),
    ('Meriden', 'Connecticut', 'CT', 'South Central Connecticut', 'New Haven County', 41.5334, -72.7997),
    ('Cupertino', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.3174, -122.0386),
    ('Springfield', 'Oregon', 'OR', 'Willamette Valley', 'Lane County', 44.0611, -123.0153),
    ('Rogers', 'Arkansas', 'AR', 'Northwest Arkansas', 'Benton County', 36.3363, -94.1148),
    ('Gardena', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8925, -118.2961),
    ('Pontiac', 'Michigan', 'MI', 'Southeast Michigan', 'Oakland County', 42.668, -83.2893),
    ('National City', 'California', 'CA', 'Southern California', 'San Diego County', 32.6749, -117.0897),
    ('Grand Junction', 'Colorado', 'CO', 'Front Range', 'Mesa County', 39.0783, -108.5457),
    ('Rocklin', 'California', 'CA', 'Southern California', 'Placer County', 38.7919, -121.2434),
    ('Chapel Hill', 'North Carolina', 'NC', 'Triangle', 'Orange County', 35.9203, -79.0372),
    ('Casper', 'Wyoming', 'WY', 'Wyoming Region', 'Natrona County', 42.8458, -106.3166),
    ('Broomfield', 'Colorado', 'CO', 'Front Range', 'Broomfield County', 39.9245, -105.0609),
    ('Petaluma', 'California', 'CA', 'Southern California', 'Sonoma County', 38.2403, -122.6777),
    ('South Jordan', 'Utah', 'UT', 'Wasatch Front', 'Salt Lake County', 40.5219, -111.9383),
    ('Springfield', 'Ohio', 'OH', 'Northeast Ohio', 'Clark County', 39.9242, -83.8089),
    ('Great Falls', 'Montana', 'MT', 'South Central Montana', 'Cascade County', 47.5098, -111.2734),
    ('Lancaster', 'Pennsylvania', 'PA', 'South Central PA', 'Lancaster County', 40.0754, -76.3199),
    ('North Port', 'Florida', 'FL', 'Southeast Florida', 'Sarasota County', 27.0781, -82.1735),
    ('Lakewood', 'Washington', 'WA', 'Puget Sound', 'Pierce County', 47.1229, -122.5293),
    ('Marietta', 'Georgia', 'GA', 'Metro Atlanta', 'Cobb County', 33.9043, -84.468),
    ('San Rafael', 'California', 'CA', 'Southern California', 'Marin County', 37.9691, -122.5105),
    ('Royal Oak', 'Michigan', 'MI', 'Southeast Michigan', 'Oakland County', 42.4906, -83.1366),
    ('Des Plaines', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0467, -87.8859),
    ('Huntington Park', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9769, -118.2161),
    ('La Mesa', 'California', 'CA', 'Southern California', 'San Diego County', 32.7604, -117.0115),
    ('Orland Park', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.6194, -87.8423),
    ('Auburn', 'Alabama', 'AL', 'East Alabama', 'Lee County', 32.602, -85.489),
    ('Lakeville', 'Minnesota', 'MN', 'Twin Cities', 'Dakota County', 44.6749, -93.2578),
    ('Owensboro', 'Kentucky', 'KY', 'South Central Kentucky', 'Daviess County', 37.7513, -87.1554),
    ('Jupiter', 'Florida', 'FL', 'Southeast Florida', 'Palm Beach County', 26.9339, -80.1201),
    ('Idaho Falls', 'Idaho', 'ID', 'Southwest Idaho', 'Bonneville County', 43.5177, -111.9906),
    ('Dubuque', 'Iowa', 'IA', 'Quad Cities', 'Dubuque County', 42.515, -90.6819),
    ('Rowlett', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.9027, -96.5636),
    ('Novi', 'Michigan', 'MI', 'Southeast Michigan', 'Oakland County', 42.4735, -83.5224),
    ('White Plains', 'New York', 'NY', 'Capital Region', 'Westchester County', 41.033, -73.7652),
    ('Arcadia', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.1324, -118.0264),
    ('Redmond', 'Washington', 'WA', 'Puget Sound', 'King County', 47.6718, -122.1232),
    ('Lake Elsinore', 'California', 'CA', 'Southern California', 'Riverside County', 33.6598, -117.3485),
    ('Ocala', 'Florida', 'FL', 'North Central Florida', 'Marion County', 29.1981, -82.0974),
    ('Port Orange', 'Florida', 'FL', 'Southeast Florida', 'Volusia County', 29.1214, -80.9767),
    ('Medford', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.4183, -71.1067),
    ('Oak Lawn', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.7143, -87.7516),
    ('Rocky Mount', 'North Carolina', 'NC', 'Triangle', 'Edgecombe County', 35.9427, -77.7608),
    ('Kokomo', 'Indiana', 'IN', 'Central Indiana', 'Howard County', 40.4988, -86.1453),
    ('Coconut Creek', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.2441, -80.2066),
    ('Bowie', 'Maryland', 'MD', 'Central Maryland', 'Prince Georges County', 38.9797, -76.7435),
    ('Berwyn', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.8418, -87.7908),
    ('Fountain Valley', 'California', 'CA', 'Southern California', 'Orange County', 33.7108, -117.9523),
    ('Buckeye', 'Arizona', 'AZ', 'Valley of the Sun', 'Maricopa County', 33.389, -112.6077),
    ('Dearborn Heights', 'Michigan', 'MI', 'Southeast Michigan', 'Wayne County', 42.2768, -83.2606),
    ('Woodland', 'California', 'CA', 'Southern California', 'Yolo County', 38.6743, -121.7793),
    ('Noblesville', 'Indiana', 'IN', 'Central Indiana', 'Hamilton County', 40.0563, -86.0163),
    ('Valdosta', 'Georgia', 'GA', 'South Georgia', 'Lowndes County', 30.8106, -83.2772),
    ('Diamond Bar', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0066, -117.8098),
    ('Manhattan', 'Kansas', 'KS', 'Northeast Kansas', 'Riley County', 39.1938, -96.5858),
    ('Santee', 'California', 'CA', 'Southern California', 'San Diego County', 32.8486, -116.9862),
    ('Taunton', 'Massachusetts', 'MA', 'Greater Boston', 'Bristol County', 41.905, -71.1026),
    ('Sanford', 'Florida', 'FL', 'Southeast Florida', 'Seminole County', 28.8013, -81.285),
    ('New Brunswick', 'New Jersey', 'NJ', 'Central New Jersey', 'Middlesex County', 40.4891, -74.4482),
    ('Decatur', 'Alabama', 'AL', 'North Alabama', 'Morgan County', 34.5896, -86.9887),
    ('Chicopee', 'Massachusetts', 'MA', 'Greater Boston', 'Hampden County', 42.162, -72.608),
    ('Anderson', 'Indiana', 'IN', 'Central Indiana', 'Madison County', 40.1146, -85.7253),
    ('Hempstead', 'New York', 'NY', 'Capital Region', 'Nassau County', 40.7139, -73.6003),
    ('Corvallis', 'Oregon', 'OR', 'Willamette Valley', 'Benton County', 44.5904, -123.2722),
    ('Porterville', 'California', 'CA', 'Southern California', 'Tulare County', 36.0686, -119.0315),
    ('West Haven', 'Connecticut', 'CT', 'South Central Connecticut', 'New Haven County', 41.2701, -72.9638),
    ('Brentwood', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.9324, -121.6894),
    ('Paramount', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8969, -118.1632),
    ('Grand Forks', 'North Dakota', 'ND', 'South Central ND', 'Grand Forks County', 47.901, -97.0446),
    ('Georgetown', 'Texas', 'TX', 'Central Texas', 'Williamson County', 30.633, -97.6707),
    ('Mount Prospect', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0624, -87.9377),
    ('Hanford', 'California', 'CA', 'Southern California', 'Kings County', 36.3314, -119.6491),
    ('Normal', 'Illinois', 'IL', 'Northeast Illinois', 'Mclean County', 40.5124, -88.9883),
    ('Rosemead', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0658, -118.0853),
    ('Lehi', 'Utah', 'UT', 'Wasatch Front', 'Utah County', 40.3958, -111.8506),
    ('Pocatello', 'Idaho', 'ID', 'Southwest Idaho', 'Bannock County', 42.8876, -112.4381),
    ('Highland', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.127, -117.2087),
    ('Novato', 'California', 'CA', 'Southern California', 'Marin County', 38.1163, -122.5714),
    ('Port Arthur', 'Texas', 'TX', 'Southeast Texas', 'Jefferson County', 29.8826, -93.9626),
    ('Carson City', 'Nevada', 'NV', 'Southern Nevada', 'Carson City County', 39.1507, -119.7459),
    ('San Marcos', 'Texas', 'TX', 'Central Texas', 'Hays County', 29.8754, -97.9404),
    ('Hendersonville', 'Tennessee', 'TN', 'Middle Tennessee', 'Sumner County', 36.3054, -86.6072),
    ('Elyria', 'Ohio', 'OH', 'Northeast Ohio', 'Lorain County', 41.3724, -82.1051),
    ('Revere', 'Massachusetts', 'MA', 'Greater Boston', 'Suffolk County', 42.4138, -71.0052),
    ('Pflugerville', 'Texas', 'TX', 'West Texas', 'Travis County', 30.4421, -97.6299),
    ('Greenwood', 'Indiana', 'IN', 'Central Indiana', 'Johnson County', 39.6224, -86.149),
    ('Bellevue', 'Nebraska', 'NE', 'Eastern Nebraska', 'Sarpy County', 41.1497, -95.9099),
    ('Wheaton', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.8566, -88.1076),
    ('Smyrna', 'Georgia', 'GA', 'Metro Atlanta', 'Cobb County', 33.8796, -84.5023),
    ('Sarasota', 'Florida', 'FL', 'Southwest Florida', 'Manatee County', 27.4072, -82.5303),
    ('Blue Springs', 'Missouri', 'MO', 'Central Missouri', 'Jackson County', 39.0169, -94.2814),
    ('Colton', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.058, -117.3186),
    ('Euless', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.8582, -97.0832),
    ('Castle Rock', 'Colorado', 'CO', 'Front Range', 'Douglas County', 39.3926, -104.8602),
    ('Cathedral City', 'California', 'CA', 'Southern California', 'Riverside County', 33.8098, -116.4665),
    ('Kingsport', 'Tennessee', 'TN', 'Northeast Tennessee', 'Sullivan County', 36.5528, -82.554),
    ('Lake Havasu City', 'Arizona', 'AZ', 'Valley of the Sun', 'Mohave County', 34.4929, -114.3081),
    ('Pensacola', 'Florida', 'FL', 'Northwest Florida', 'Escambia County', 30.4223, -87.2248),
    ('Hoboken', 'New Jersey', 'NJ', 'Central New Jersey', 'Hudson County', 40.7445, -74.0329),
    ('Yucaipa', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.0282, -117.0489),
    ('Watsonville', 'California', 'CA', 'Southern California', 'Santa Cruz County', 36.9205, -121.7634),
    ('Richland', 'Washington', 'WA', 'Puget Sound', 'Benton County', 46.2833, -119.2892),
    ('Delano', 'California', 'CA', 'Southern California', 'Kern County', 35.7715, -119.2459),
    ('Hoffman Estates', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0481, -88.1047),
    ('Florissant', 'Missouri', 'MO', 'Central Missouri', 'Saint Louis County', 38.8069, -90.3401),
    ('Placentia', 'California', 'CA', 'Southern California', 'Orange County', 33.881, -117.8553),
    ('West New York', 'New Jersey', 'NJ', 'Central New Jersey', 'Hudson County', 40.7882, -74.0129),
    ('Dublin', 'California', 'CA', 'Southern California', 'Alameda County', 37.7166, -121.9226),
    ('Oak Park', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.8886, -87.7986),
    ('Peabody', 'Massachusetts', 'MA', 'Greater Boston', 'Essex County', 42.5326, -70.9612),
    ('Perth Amboy', 'New Jersey', 'NJ', 'Central New Jersey', 'Middlesex County', 40.5176, -74.2754),
    ('Battle Creek', 'Michigan', 'MI', 'Southeast Michigan', 'Calhoun County', 42.3053, -85.1389),
    ('Bradenton', 'Florida', 'FL', 'Southeast Florida', 'Manatee County', 27.5028, -82.5139),
    ('Gilroy', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.016, -121.5782),
    ('Milford', 'Connecticut', 'CT', 'South Central Connecticut', 'New Haven County', 41.2175, -73.0549),
    ('Albany', 'Oregon', 'OR', 'Willamette Valley', 'Linn County', 44.6277, -123.0944),
    ('Ankeny', 'Iowa', 'IA', 'Quad Cities', 'Polk County', 41.7276, -93.6022),
    ('La Crosse', 'Wisconsin', 'WI', 'Fox Valley', 'La Crosse County', 43.7989, -91.2175),
    ('Burlington', 'North Carolina', 'NC', 'Piedmont', 'Alamance County', 36.072, -79.4622),
    ('DeSoto', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.5932, -96.8547),
    ('Harrisonburg', 'Virginia', 'VA', 'Northern Virginia', 'Harrisonburg City County', 38.4489, -78.8714),
    ('Minnetonka', 'Minnesota', 'MN', 'Twin Cities', 'Hennepin County', 44.9138, -93.485),
    ('Elkhart', 'Indiana', 'IN', 'Central Indiana', 'Elkhart County', 41.7101, -85.9729),
    ('Lakewood', 'Ohio', 'OH', 'Northeast Ohio', 'Cuyahoga County', 41.4827, -81.7971),
    ('Glendora', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.1287, -117.8552),
    ('Southaven', 'Mississippi', 'MS', 'Central Mississippi', 'Desoto County', 34.9771, -89.9992),
    ('Charleston', 'West Virginia', 'WV', 'Western WV', 'Kanawha County', 38.349, -81.6306),
    ('Joplin', 'Missouri', 'MO', 'Central Missouri', 'Jasper County', 37.0969, -94.5051),
    ('Enid', 'Oklahoma', 'OK', 'Northeast Oklahoma', 'Garfield County', 36.4028, -97.8623),
    ('Palm Beach Gardens', 'Florida', 'FL', 'Southeast Florida', 'Palm Beach County', 26.8444, -80.0873),
    ('Plainfield', 'New Jersey', 'NJ', 'Central New Jersey', 'Union County', 40.6198, -74.4253),
    ('Grand Island', 'Nebraska', 'NE', 'Eastern Nebraska', 'Hall County', 40.9219, -98.3411),
    ('Palm Desert', 'California', 'CA', 'Southern California', 'Riverside County', 33.7611, -116.3249),
    ('Huntersville', 'North Carolina', 'NC', 'Triangle', 'Mecklenburg County', 35.4106, -80.8431),
    ('Lenexa', 'Kansas', 'KS', 'Northeast Kansas', 'Johnson County', 38.963, -94.7399),
    ('Saginaw', 'Michigan', 'MI', 'Southeast Michigan', 'Saginaw County', 43.4047, -83.9156),
    ('Grapevine', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.9314, -97.0962),
    ('Aliso Viejo', 'California', 'CA', 'Southern California', 'Orange County', 33.5724, -117.7089),
    ('Sammamish', 'Washington', 'WA', 'Puget Sound', 'King County', 47.6244, -122.0423),
    ('Casa Grande', 'Arizona', 'AZ', 'Valley of the Sun', 'Pinal County', 32.8927, -111.7561),
    ('Pinellas Park', 'Florida', 'FL', 'Southeast Florida', 'Pinellas County', 27.8387, -82.7151),
    ('Troy', 'New York', 'NY', 'Capital Region', 'Albany County', 42.7438, -73.6937),
    ('West Sacramento', 'California', 'CA', 'Southern California', 'Yolo County', 38.5924, -121.5264),
    ('Commerce City', 'Colorado', 'CO', 'Front Range', 'Adams County', 39.8259, -104.9113),
    ('Monroe', 'Louisiana', 'LA', 'Central Louisiana', 'Ouachita County', 32.5286, -92.1061),
    ('Cerritos', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8583, -118.0639),
    ('Downers Grove', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.8034, -88.0138),
    ('Wilson', 'North Carolina', 'NC', 'Triangle', 'Wilson County', 35.727, -77.9227),
    ('Niagara Falls', 'New York', 'NY', 'Capital Region', 'Niagara County', 43.0955, -79.0414),
    ('Poway', 'California', 'CA', 'Southern California', 'San Diego County', 32.9756, -117.0402),
    ('Cuyahoga Falls', 'Ohio', 'OH', 'Northeast Ohio', 'Summit County', 41.1401, -81.479),
    ('Rancho Santa Margarita', 'California', 'CA', 'Southern California', 'Orange County', 33.6518, -117.5884),
    ('Harrisburg', 'Pennsylvania', 'PA', 'South Central PA', 'Dauphin County', 40.2618, -76.8831),
    ('Huntington', 'West Virginia', 'WV', 'Western WV', 'Cabell County', 38.4097, -82.4423),
    ('La Mirada', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.8953, -118.0024),
    ('Cypress', 'California', 'CA', 'Southern California', 'Orange County', 33.8186, -118.0387),
    ('Caldwell', 'Idaho', 'ID', 'Southwest Idaho', 'Canyon County', 43.6627, -116.7),
    ('Logan', 'Utah', 'UT', 'Wasatch Front', 'Cache County', 41.747, -111.8226),
    ('Galveston', 'Texas', 'TX', 'West Texas', 'Galveston County', 29.2983, -94.793),
    ('Sheboygan', 'Wisconsin', 'WI', 'Fox Valley', 'Sheboygan County', 43.741, -87.7247),
    ('Middletown', 'Ohio', 'OH', 'Northeast Ohio', 'Butler County', 39.5321, -84.3896),
    ('Roswell', 'New Mexico', 'NM', 'Central New Mexico', 'Chaves County', 33.3885, -104.5259),
    ('Parker', 'Colorado', 'CO', 'Front Range', 'Douglas County', 39.5055, -104.7349),
    ('Bedford', 'Texas', 'TX', 'West Texas', 'Tarrant County', 32.8536, -97.1358),
    ('East Lansing', 'Michigan', 'MI', 'Southeast Michigan', 'Ingham County', 42.7388, -84.4764),
    ('Methuen', 'Massachusetts', 'MA', 'Greater Boston', 'Essex County', 42.728, -71.181),
    ('Covina', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0972, -117.9065),
    ('Alexandria', 'Louisiana', 'LA', 'Central Louisiana', 'Rapides County', 31.2885, -92.4633),
    ('Olympia', 'Washington', 'WA', 'South Puget Sound', 'Thurston County', 47.0129, -122.8763),
    ('Euclid', 'Ohio', 'OH', 'Northeast Ohio', 'Cuyahoga County', 41.5696, -81.5257),
    ('Mishawaka', 'Indiana', 'IN', 'Central Indiana', 'St Joseph County', 41.6507, -86.1623),
    ('Salina', 'Kansas', 'KS', 'Northeast Kansas', 'Saline County', 38.8238, -97.6088),
    ('Azusa', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.1248, -117.9031),
    ('Newark', 'Ohio', 'OH', 'Northeast Ohio', 'Licking County', 40.0724, -82.4046),
    ('Chesterfield', 'Missouri', 'MO', 'Central Missouri', 'Saint Louis County', 38.6318, -90.6142),
    ('Leesburg', 'Virginia', 'VA', 'Northern Virginia', 'Loudoun County', 39.0867, -77.5775),
    ('Hattiesburg', 'Mississippi', 'MS', 'Central Mississippi', 'Forrest County', 31.3146, -89.3065),
    ('Roseville', 'Michigan', 'MI', 'Southeast Michigan', 'Macomb County', 42.5034, -82.9387),
    ('Bonita Springs', 'Florida', 'FL', 'Southwest Florida', 'Lee County', 26.3869, -81.733),
    ('Portage', 'Michigan', 'MI', 'Southeast Michigan', 'Kalamazoo County', 42.2075, -85.5957),
    ('Collierville', 'Tennessee', 'TN', 'West Tennessee', 'Shelby County', 35.0551, -89.6767),
    ('Middletown', 'Connecticut', 'CT', 'South Central Connecticut', 'Middlesex County', 41.5569, -72.6652),
    ('Stillwater', 'Oklahoma', 'OK', 'Northeast Oklahoma', 'Payne County', 36.1043, -97.0609),
    ('East Providence', 'Rhode Island', 'RI', 'Providence County', 'Providence County', 41.8138, -71.3688),
    ('Mentor', 'Ohio', 'OH', 'Northeast Ohio', 'Lake County', 41.6895, -81.3421),
    ('Ceres', 'California', 'CA', 'Southern California', 'Stanislaus County', 37.5881, -120.9499),
    ('Cedar Hill', 'Texas', 'TX', 'West Texas', 'Dallas County', 32.5885, -96.9438),
    ('Mansfield', 'Ohio', 'OH', 'Northeast Ohio', 'Richland County', 40.7633, -82.5138),
    ('Binghamton', 'New York', 'NY', 'Capital Region', 'Broome County', 42.1463, -75.8865),
    ('San Luis Obispo', 'California', 'CA', 'Southern California', 'San Luis Obispo County', 35.2635, -120.6509),
    ('Minot', 'North Dakota', 'ND', 'South Central ND', 'Ward County', 48.2291, -101.2985),
    ('Palm Springs', 'California', 'CA', 'Southern California', 'Riverside County', 33.8414, -116.5347),
    ('Pine Bluff', 'Arkansas', 'AR', 'Northwest Arkansas', 'Jefferson County', 34.2154, -91.9958),
    ('Texas City', 'Texas', 'TX', 'West Texas', 'Galveston County', 29.397, -94.9203),
    ('Summerville', 'South Carolina', 'SC', 'Upstate', 'Dorchester County', 33.028, -80.1739),
    ('Twin Falls', 'Idaho', 'ID', 'Southwest Idaho', 'Twin Falls County', 42.5565, -114.4693),
    ('Jeffersonville', 'Indiana', 'IN', 'Central Indiana', 'Clark County', 38.3078, -85.7359),
    ('San Jacinto', 'California', 'CA', 'Southern California', 'Riverside County', 33.7839, -116.9578),
    ('Madison', 'Alabama', 'AL', 'North Alabama', 'Limestone County', 34.6578, -86.8056),
    ('Altoona', 'Pennsylvania', 'PA', 'Lehigh Valley', 'Blair County', 40.5209, -78.4089),
    ('Columbus', 'Indiana', 'IN', 'Central Indiana', 'Bartholomew County', 39.2055, -85.9317),
    ('Apopka', 'Florida', 'FL', 'Southeast Florida', 'Orange County', 28.6619, -81.4851),
    ('Elmhurst', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.8927, -87.941),
    ('Maricopa', 'Arizona', 'AZ', 'Valley of the Sun', 'Pinal County', 32.9874, -112.0752),
    ('Farmington', 'New Mexico', 'NM', 'Central New Mexico', 'San Juan County', 36.7065, -108.1995),
    ('Glenview', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0758, -87.8223),
    ('Draper', 'Utah', 'UT', 'Wasatch Front', 'Salt Lake County', 40.5046, -111.881),
    ('Lincoln', 'California', 'CA', 'Southern California', 'Placer County', 38.904, -121.2955),
    ('Sierra Vista', 'Arizona', 'AZ', 'Valley of the Sun', 'Cochise County', 31.5365, -110.2666),
    ('Lacey', 'Washington', 'WA', 'Puget Sound', 'Thurston County', 47.024, -122.7827),
    ('Biloxi', 'Mississippi', 'MS', 'Central Mississippi', 'Harrison County', 30.4035, -88.8971),
    ('Strongsville', 'Ohio', 'OH', 'Northeast Ohio', 'Cuyahoga County', 41.3132, -81.8285),
    ('Wylie', 'Texas', 'TX', 'North Texas', 'Collin County', 33.0041, -96.5394),
    ('Sayreville', 'New Jersey', 'NJ', 'Central New Jersey', 'Middlesex County', 40.4592, -74.3614),
    ('Kannapolis', 'North Carolina', 'NC', 'Triangle', 'Cabarrus County', 35.502, -80.6359),
    ('Charlottesville', 'Virginia', 'VA', 'Northern Virginia', 'Albemarle County', 38.0548, -78.4909),
    ('Littleton', 'Colorado', 'CO', 'Front Range', 'Arapahoe County', 39.5994, -105.0044),
    ('Titusville', 'Florida', 'FL', 'Southeast Florida', 'Brevard County', 28.5697, -80.8191),
    ('Hackensack', 'New Jersey', 'NJ', 'Central New Jersey', 'Bergen County', 40.8882, -74.0503),
    ('Newark', 'California', 'CA', 'Southern California', 'Alameda County', 37.5368, -122.032),
    ('Pittsfield', 'Massachusetts', 'MA', 'Greater Boston', 'Berkshire County', 42.4531, -73.2471),
    ('York', 'Pennsylvania', 'PA', 'Lehigh Valley', 'York County', 39.9635, -76.7269),
    ('Lombard', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.8721, -88.016),
    ('Attleboro', 'Massachusetts', 'MA', 'Greater Boston', 'Bristol County', 41.9296, -71.3009),
    ('DeKalb', 'Illinois', 'IL', 'Northeast Illinois', 'Dekalb County', 41.9342, -88.7607),
    ('Blacksburg', 'Virginia', 'VA', 'Northern Virginia', 'Montgomery County', 37.2288, -80.4273),
    ('Dublin', 'Ohio', 'OH', 'Central Ohio', 'Franklin County', 40.0992, -83.1142),
    ('Haltom City', 'Texas', 'TX', 'West Texas', 'Tarrant County', 32.8087, -97.2709),
    ('Lompoc', 'California', 'CA', 'Southern California', 'Santa Barbara County', 34.6583, -120.4506),
    ('El Centro', 'California', 'CA', 'Southern California', 'Imperial County', 32.7893, -115.5665),
    ('Danville', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.8208, -121.9067),
    ('Jefferson City', 'Missouri', 'MO', 'Central Missouri', 'Cole County', 38.5462, -92.1525),
    ('North Miami Beach', 'Florida', 'FL', 'Southeast Florida', 'Miami-dade County', 25.9361, -80.1351),
    ('Freeport', 'New York', 'NY', 'Capital Region', 'Nassau County', 40.6536, -73.5866),
    ('Moline', 'Illinois', 'IL', 'Northeast Illinois', 'Rock Island County', 41.4906, -90.498),
    ('Coachella', 'California', 'CA', 'Southern California', 'Riverside County', 33.675, -116.1772),
    ('Fort Pierce', 'Florida', 'FL', 'Southeast Florida', 'Saint Lucie County', 27.4382, -80.444),
    ('Smyrna', 'Tennessee', 'TN', 'West Tennessee', 'Rutherford County', 35.9656, -86.5048),
    ('Bountiful', 'Utah', 'UT', 'Wasatch Front', 'Davis County', 40.8775, -111.8727),
    ('Fond du Lac', 'Wisconsin', 'WI', 'Fox Valley', 'Fond Du Lac County', 43.7704, -88.4291),
    ('Everett', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.4112, -71.0514),
    ('Danville', 'Virginia', 'VA', 'Northern Virginia', 'Danville City County', 36.6218, -79.4124),
    ('Keller', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.9344, -97.2514),
    ('Belleville', 'Illinois', 'IL', 'Northeast Illinois', 'Saint Clair County', 38.5127, -89.9847),
    ('Bell Gardens', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9775, -118.1861),
    ('Cleveland', 'Tennessee', 'TN', 'West Tennessee', 'Bradley County', 35.1313, -84.875),
    ('Fairfield', 'Ohio', 'OH', 'Northeast Ohio', 'Butler County', 39.3266, -84.5479),
    ('Salem', 'Massachusetts', 'MA', 'Greater Boston', 'Essex County', 42.5151, -70.9003),
    ('Rancho Palos Verdes', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.7878, -118.3572),
    ('San Bruno', 'California', 'CA', 'Southern California', 'San Mateo County', 37.6247, -122.429),
    ('Concord', 'New Hampshire', 'NH', 'New Hampshire Region', 'Merrimack County', 43.2185, -71.5277),
    ('Burlington', 'Vermont', 'VT', 'Vermont Region', 'Chittenden County', 44.484, -73.2199),
    ('Apex', 'North Carolina', 'NC', 'Triangle', 'Wake County', 35.7225, -78.8408),
    ('Midland', 'Michigan', 'MI', 'Southeast Michigan', 'Midland County', 43.6376, -84.268),
    ('Altamonte Springs', 'Florida', 'FL', 'Southeast Florida', 'Seminole County', 28.6627, -81.3719),
    ('Hutchinson', 'Kansas', 'KS', 'Northeast Kansas', 'Reno County', 38.055, -97.9311),
    ('Buffalo Grove', 'Illinois', 'IL', 'Northeast Illinois', 'Lake County', 42.1598, -87.9644),
    ('Urbandale', 'Iowa', 'IA', 'Quad Cities', 'Polk County', 41.6295, -93.723),
    ('State College', 'Pennsylvania', 'PA', 'Lehigh Valley', 'Centre County', 40.7925, -77.8523),
    ('Urbana', 'Illinois', 'IL', 'Northeast Illinois', 'Champaign County', 40.1095, -88.2036),
    ('Plainfield', 'Illinois', 'IL', 'Northeast Illinois', 'Will County', 41.6009, -88.1994),
    ('Manassas', 'Virginia', 'VA', 'Northern Virginia', 'Manassas City County', 38.7518, -77.4728),
    ('Bartlett', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.9836, -88.1604),
    ('Kearny', 'New Jersey', 'NJ', 'Central New Jersey', 'Hudson County', 40.7647, -74.1471),
    ('Findlay', 'Ohio', 'OH', 'Northeast Ohio', 'Hancock County', 41.0442, -83.65),
    ('Rohnert Park', 'California', 'CA', 'Southern California', 'Sonoma County', 38.3269, -122.7061),
    ('Westfield', 'Massachusetts', 'MA', 'Greater Boston', 'Hampden County', 42.1295, -72.7543),
    ('Linden', 'New Jersey', 'NJ', 'Central New Jersey', 'Union County', 40.6354, -74.2556),
    ('Sumter', 'South Carolina', 'SC', 'Upstate', 'Sumter County', 33.9282, -80.321),
    ('Woonsocket', 'Rhode Island', 'RI', 'Providence County', 'Providence County', 41.9995, -71.5137),
    ('Leominster', 'Massachusetts', 'MA', 'Greater Boston', 'Worcester County', 42.5274, -71.7563),
    ('Shelton', 'Connecticut', 'CT', 'South Central Connecticut', 'Fairfield County', 41.3047, -73.1294),
    ('Brea', 'California', 'CA', 'Southern California', 'Orange County', 33.9252, -117.8895),
    ('Covington', 'Kentucky', 'KY', 'Northern Kentucky', 'Kenton County', 39.0708, -84.5212),
    ('Rockwall', 'Texas', 'TX', 'North Texas', 'Rockwall County', 32.9311, -96.4594),
    ('Riverton', 'Utah', 'UT', 'Wasatch Front', 'Salt Lake County', 40.5379, -111.9547),
    ('Meridian', 'Mississippi', 'MS', 'Central Mississippi', 'Lauderdale County', 32.3574, -88.656),
    ('Quincy', 'Illinois', 'IL', 'Northeast Illinois', 'Adams County', 39.9307, -91.3763),
    ('Morgan Hill', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.1292, -121.6464),
    ('Warren', 'Ohio', 'OH', 'Northeast Ohio', 'Trumbull County', 41.1724, -80.8718),
    ('Edmonds', 'Washington', 'WA', 'Puget Sound', 'Snohomish County', 47.8007, -122.3669),
    ('Burleson', 'Texas', 'TX', 'North Texas', 'Johnson County', 32.5316, -97.309),
    ('Beverly', 'Massachusetts', 'MA', 'Greater Boston', 'Essex County', 42.5608, -70.8759),
    ('Mankato', 'Minnesota', 'MN', 'Twin Cities', 'Blue Earth County', 44.1538, -93.996),
    ('Hagerstown', 'Maryland', 'MD', 'Central Maryland', 'Washington County', 39.632, -77.7372),
    ('Prescott', 'Arizona', 'AZ', 'Valley of the Sun', 'Yavapai County', 34.6299, -113.0225),
    ('Campbell', 'California', 'CA', 'Southern California', 'Santa Clara County', 37.28, -121.9554),
    ('Cedar Falls', 'Iowa', 'IA', 'Quad Cities', 'Black Hawk County', 42.5241, -92.4497),
    ('Beaumont', 'California', 'CA', 'Southern California', 'Riverside County', 33.9504, -116.9701),
    ('La Puente', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.0294, -117.9341),
    ('Crystal Lake', 'Illinois', 'IL', 'Northeast Illinois', 'Mchenry County', 42.2662, -88.3213),
    ('Fitchburg', 'Massachusetts', 'MA', 'Greater Boston', 'Worcester County', 42.5796, -71.8031),
    ('Carol Stream', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.9166, -88.1209),
    ('Hickory', 'North Carolina', 'NC', 'Triangle', 'Catawba County', 35.7576, -81.3289),
    ('Streamwood', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0225, -88.169),
    ('Norwich', 'Connecticut', 'CT', 'South Central Connecticut', 'New London County', 41.5371, -72.0849),
    ('Coppell', 'Texas', 'TX', 'North Texas', 'Dallas County', 32.9673, -96.9805),
    ('San Gabriel', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.1155, -118.0857),
    ('Holyoke', 'Massachusetts', 'MA', 'Greater Boston', 'Hampden County', 42.202, -72.6262),
    ('Bentonville', 'Arkansas', 'AR', 'Northwest Arkansas', 'Benton County', 36.3577, -94.2224),
    ('Florence', 'Alabama', 'AL', 'North Alabama', 'Lauderdale County', 34.8305, -87.656),
    ('Brentwood', 'Tennessee', 'TN', 'Middle Tennessee', 'Williamson County', 36.0331, -86.7828),
    ('Bozeman', 'Montana', 'MT', 'South Central Montana', 'Gallatin County', 45.6693, -111.0431),
    ('New Berlin', 'Wisconsin', 'WI', 'Fox Valley', 'Waukesha County', 42.974, -88.1553),
    ('Goose Creek', 'South Carolina', 'SC', 'Upstate', 'Berkeley County', 32.9887, -80.0199),
    ('Huntsville', 'Texas', 'TX', 'West Texas', 'Walker County', 30.7947, -95.5337),
    ('Prescott Valley', 'Arizona', 'AZ', 'Valley of the Sun', 'Yavapai County', 34.61, -112.315),
    ('Romeoville', 'Illinois', 'IL', 'Northeast Illinois', 'Will County', 41.6475, -88.0894),
    ('Duncanville', 'Texas', 'TX', 'West Texas', 'Dallas County', 32.6587, -96.9114),
    ('Atlantic City', 'New Jersey', 'NJ', 'Central New Jersey', 'Atlantic County', 39.3664, -74.4317),
    ('Clovis', 'New Mexico', 'NM', 'Central New Mexico', 'Curry County', 34.4126, -103.2214),
    ('The Colony', 'Texas', 'TX', 'North Texas', 'Denton County', 33.094, -96.8836),
    ('Culver City', 'California', 'CA', 'Southern California', 'Los Angeles County', 33.9949, -118.3991),
    ('Marlborough', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.3509, -71.5434),
    ('Hilton Head Island', 'South Carolina', 'SC', 'Upstate', 'Beaufort County', 32.1632, -80.7533),
    ('Moorhead', 'Minnesota', 'MN', 'Twin Cities', 'Clay County', 46.8677, -96.7572),
    ('Calexico', 'California', 'CA', 'Southern California', 'Imperial County', 32.6832, -115.5028),
    ('Bullhead City', 'Arizona', 'AZ', 'Valley of the Sun', 'Mohave County', 35.1678, -114.543),
    ('Germantown', 'Tennessee', 'TN', 'West Tennessee', 'Shelby County', 35.0883, -89.8053),
    ('La Quinta', 'California', 'CA', 'Southern California', 'Riverside County', 34.3278, -118.6406),
    ('Lancaster', 'Ohio', 'OH', 'Northeast Ohio', 'Fairfield County', 39.7187, -82.6031),
    ('Wausau', 'Wisconsin', 'WI', 'Fox Valley', 'Marathon County', 44.9634, -89.634),
    ('Sherman', 'Texas', 'TX', 'North Texas', 'Grayson County', 33.6435, -96.6075),
    ('Ocoee', 'Florida', 'FL', 'Southeast Florida', 'Orange County', 28.5837, -81.5326),
    ('Shakopee', 'Minnesota', 'MN', 'Twin Cities', 'Scott County', 44.7793, -93.5197),
    ('Woburn', 'Massachusetts', 'MA', 'Greater Boston', 'Middlesex County', 42.4829, -71.1574),
    ('Bremerton', 'Washington', 'WA', 'Puget Sound', 'Kitsap County', 47.6019, -122.6299),
    ('Rock Island', 'Illinois', 'IL', 'Northeast Illinois', 'Rock Island County', 41.4913, -90.5648),
    ('Muskogee', 'Oklahoma', 'OK', 'Northeast Oklahoma', 'Muskogee County', 35.7307, -95.3755),
    ('Cape Girardeau', 'Missouri', 'MO', 'Central Missouri', 'Cape Girardeau County', 37.3169, -89.5459),
    ('Annapolis', 'Maryland', 'MD', 'Central Maryland', 'Anne Arundel County', 38.9996, -76.5031),
    ('Ormond Beach', 'Florida', 'FL', 'Southeast Florida', 'Volusia County', 29.2855, -81.0561),
    ('Stanton', 'California', 'CA', 'Southern California', 'Orange County', 33.803, -117.9947),
    ('Puyallup', 'Washington', 'WA', 'Puget Sound', 'Pierce County', 47.1991, -122.3151),
    ('Pacifica', 'California', 'CA', 'Southern California', 'San Mateo County', 37.6196, -122.4816),
    ('Hanover Park', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.7944, -87.8083),
    ('Hurst', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.8211, -97.1756),
    ('Lima', 'Ohio', 'OH', 'Northeast Ohio', 'Allen County', 40.7641, -84.0973),
    ('Marana', 'Arizona', 'AZ', 'Valley of the Sun', 'Pima County', 32.4047, -111.2736),
    ('Carpentersville', 'Illinois', 'IL', 'Northeast Illinois', 'Kane County', 42.123, -88.2606),
    ('Oakley', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.994, -121.7036),
    ('Lancaster', 'Texas', 'TX', 'West Texas', 'Dallas County', 32.6161, -96.783),
    ('Montclair', 'California', 'CA', 'Southern California', 'San Bernardino County', 34.0733, -117.6987),
    ('Wheeling', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.134, -87.9341),
    ('Brookfield', 'Wisconsin', 'WI', 'Fox Valley', 'Waukesha County', 43.0622, -88.098),
    ('Park Ridge', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 42.0122, -87.8417),
    ('Florence', 'South Carolina', 'SC', 'Pee Dee', 'Florence County', 34.1838, -79.7728),
    ('Roy', 'Utah', 'UT', 'Wasatch Front', 'Weber County', 41.1724, -112.0382),
    ('Winter Garden', 'Florida', 'FL', 'Southeast Florida', 'Orange County', 28.4867, -81.6051),
    ('Chelsea', 'Massachusetts', 'MA', 'Greater Boston', 'Suffolk County', 42.3963, -71.0325),
    ('Valley Stream', 'New York', 'NY', 'Capital Region', 'Nassau County', 40.6742, -73.7057),
    ('Spartanburg', 'South Carolina', 'SC', 'Upstate', 'Spartanburg County', 34.9352, -81.9654),
    ('Lake Oswego', 'Oregon', 'OR', 'Willamette Valley', 'Clackamas County', 45.4093, -122.6847),
    ('Friendswood', 'Texas', 'TX', 'West Texas', 'Galveston County', 29.5224, -95.1879),
    ('Westerville', 'Ohio', 'OH', 'Northeast Ohio', 'Delaware County', 40.1545, -82.9097),
    ('Phenix City', 'Alabama', 'AL', 'Northeast Alabama', 'Lee County', 32.484, -85.0911),
    ('Grove City', 'Ohio', 'OH', 'Northeast Ohio', 'Franklin County', 39.8814, -83.0839),
    ('Texarkana', 'Texas', 'TX', 'West Texas', 'Bowie County', 33.4074, -94.1182),
    ('Addison', 'Illinois', 'IL', 'Northeast Illinois', 'Dupage County', 41.9335, -88.0054),
    ('Dover', 'Delaware', 'DE', 'Delaware Region', 'Kent County', 39.1566, -75.536),
    ('Lincoln Park', 'Michigan', 'MI', 'Southeast Michigan', 'Wayne County', 42.2422, -83.1807),
    ('Calumet City', 'Illinois', 'IL', 'Northeast Illinois', 'Cook County', 41.6153, -87.5483),
    ('Muskegon', 'Michigan', 'MI', 'Southeast Michigan', 'Muskegon County', 43.2326, -86.2492),
    ('Martinez', 'California', 'CA', 'Southern California', 'Contra Costa County', 37.9932, -122.1117),
    ('Apache Junction', 'Arizona', 'AZ', 'Valley of the Sun', 'Pinal County', 33.3277, -111.3259),
    ('Monrovia', 'California', 'CA', 'Southern California', 'Los Angeles County', 34.144, -118.0014),
    ('Weslaco', 'Texas', 'TX', 'West Texas', 'Hidalgo County', 26.1694, -97.9887),
    ('Keizer', 'Oregon', 'OR', 'Willamette Valley', 'Marion County', 44.9903, -123.025),
    ('Spanish Fork', 'Utah', 'UT', 'Wasatch Front', 'Utah County', 40.1099, -111.6462),
    ('Beloit', 'Wisconsin', 'WI', 'Fox Valley', 'Rock County', 42.5229, -89.0399),
    ('Panama City', 'Florida', 'FL', 'Southeast Florida', 'Bay County', 30.1606, -85.6494),
    ('Alvin', 'Texas', 'TX', 'Southeast Texas', 'Brazoria County', 29.4238, -95.2441),
    ('Anderson', 'South Carolina', 'SC', 'Upstate', 'Anderson County', 34.5034, -82.6501),
    ('Anniston', 'Alabama', 'AL', 'Northeast Alabama', 'Calhoun County', 33.6596, -85.8316),
    ('Athens', 'Georgia', 'GA', 'Northeast Georgia', 'Clarke County', 33.9519, -83.3576),
    ('Augusta', 'Georgia', 'GA', 'East Georgia', 'Richmond County', 33.4735, -82.0105),
    ('Bartlett', 'Tennessee', 'TN', 'West Tennessee', 'Shelby County', 35.2045, -89.8742),
    ('Belton', 'Texas', 'TX', 'Central Texas', 'Bell County', 31.0557, -97.4641),
    ('Big Spring', 'Texas', 'TX', 'West Texas', 'Howard County', 32.2504, -101.4788),
    ('Bloomington', 'Minnesota', 'MN', 'Twin Cities', 'Hennepin County', 44.8408, -93.3771),
    ('Boerne', 'Texas', 'TX', 'South Texas', 'Kendall County', 29.7947, -98.7317),
    ('Boise', 'Idaho', 'ID', 'Southwest Idaho', 'Ada County', 43.615, -116.2023),
    ('Brooklyn Park', 'Minnesota', 'MN', 'Twin Cities', 'Hennepin County', 45.0941, -93.3752),
    ('Celina', 'Texas', 'TX', 'North Texas', 'Collin County', 33.3251, -96.7836),
    ('Cleburne', 'Texas', 'TX', 'North Texas', 'Johnson County', 32.3474, -97.3869),
    ('Colleyville', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.8887, -97.15),
    ('Columbia', 'Maryland', 'MD', 'Central Maryland', 'Howard County', 39.2037, -76.861),
    ('Coral Springs', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.2707, -80.2706),
    ('Davie', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 26.0765, -80.2521),
    ('Doral', 'Florida', 'FL', 'Southeast Florida', 'Miami-Dade County', 25.8196, -80.3554),
    ('Dripping Springs', 'Texas', 'TX', 'Central Texas', 'Hays County', 30.1905, -98.0869),
    ('Eagan', 'Minnesota', 'MN', 'Twin Cities', 'Dakota County', 44.8041, -93.1669),
    ('Edison', 'New Jersey', 'NJ', 'Central New Jersey', 'Middlesex County', 40.5187, -74.4121),
    ('Fredericksburg', 'Virginia', 'VA', 'Northern Virginia', 'Fredericksburg City', 38.3032, -77.4605),
    ('Gainesville', 'Georgia', 'GA', 'Northeast Georgia', 'Hall County', 34.2979, -83.8241),
    ('Henderson', 'Kentucky', 'KY', 'Western Kentucky', 'Henderson County', 37.8362, -87.59),
    ('Hoover', 'Alabama', 'AL', 'North Central Alabama', 'Jefferson County', 33.4054, -86.8113),
    ('Humble', 'Texas', 'TX', 'Southeast Texas', 'Harris County', 29.9988, -95.2627),
    ('Katy', 'Texas', 'TX', 'Southeast Texas', 'Harris County', 29.7858, -95.8244),
    ('Kyle', 'Texas', 'TX', 'Central Texas', 'Hays County', 29.9888, -97.8803),
    ('Lakewood', 'Colorado', 'CO', 'Front Range', 'Jefferson County', 39.7047, -105.0814),
    ('Leander', 'Texas', 'TX', 'Central Texas', 'Williamson County', 30.5788, -97.8531),
    ("Lee's Summit", 'Missouri', 'MO', 'Western Missouri', 'Jackson County', 38.9108, -94.3827),
    ('Lexington', 'Kentucky', 'KY', 'Bluegrass Region', 'Fayette County', 38.0406, -84.5037),
    ('Lufkin', 'Texas', 'TX', 'East Texas', 'Angelina County', 31.3382, -94.7291),
    ('Metairie', 'Louisiana', 'LA', 'Southeast Louisiana', 'Jefferson Parish', 29.994, -90.1626),
    ('Miami Gardens', 'Florida', 'FL', 'Southeast Florida', 'Miami-Dade County', 25.942, -80.2456),
    ('Miramar', 'Florida', 'FL', 'Southeast Florida', 'Broward County', 25.9871, -80.2338),
    ('Moore', 'Oklahoma', 'OK', 'Central Oklahoma', 'Cleveland County', 35.3395, -97.4867),
    ('New York City', 'New York', 'NY', 'New York Metro', 'New York County', 40.7128, -74.006),
    ('Plymouth', 'Minnesota', 'MN', 'Twin Cities', 'Hennepin County', 45.0105, -93.4555),
    ('Port St Lucie', 'Florida', 'FL', 'Treasure Coast', 'St Lucie County', 27.273, -80.3582),
    ('Prosper', 'Texas', 'TX', 'North Texas', 'Collin County', 33.2362, -96.8003),
    ('Saint Paul', 'Minnesota', 'MN', 'Twin Cities', 'Ramsey County', 44.9537, -93.09),
    ('Sandy Springs', 'Georgia', 'GA', 'Metro Atlanta', 'Fulton County', 33.9304, -84.3733),
    ('Schertz', 'Texas', 'TX', 'South Texas', 'Guadalupe County', 29.5538, -98.2631),
    ('Southlake', 'Texas', 'TX', 'North Texas', 'Tarrant County', 32.944, -97.1342),
    ('Spring', 'Texas', 'TX', 'Southeast Texas', 'Harris County', 30.0799, -95.4172),
    ('St Louis', 'Missouri', 'MO', 'Eastern Missouri', 'St Louis City', 38.627, -90.1994),
    ('St Paul', 'Minnesota', 'MN', 'Twin Cities', 'Ramsey County', 44.9537, -93.09),
    ('St Petersburg', 'Florida', 'FL', 'Tampa Bay', 'Pinellas County', 27.7676, -82.6403),
    ('Tampa', 'Florida', 'FL', 'Tampa Bay', 'Hillsborough County', 27.9506, -82.4572),
    ('The Woodlands', 'Texas', 'TX', 'Southeast Texas', 'Montgomery County', 30.1588, -95.4853),
    ('Thornton', 'Colorado', 'CO', 'Front Range', 'Adams County', 39.868, -104.9719),
    ('Waxahachie', 'Texas', 'TX', 'North Texas', 'Ellis County', 32.3868, -96.8489),
    ('Weatherford', 'Texas', 'TX', 'North Texas', 'Parker County', 32.7596, -97.7975),
    ('West Valley City', 'Utah', 'UT', 'Wasatch Front', 'Salt Lake County', 40.6916, -111.9391),
    ('Winston-Salem', 'North Carolina', 'NC', 'Piedmont Triad', 'Forsyth County', 36.0999, -80.2442),
    ('Woodbury', 'Minnesota', 'MN', 'Twin Cities', 'Washington County', 44.9239, -92.9594),
]

# ============================================================
# STATE INFO
# ============================================================

STATE_INFO = {
    'TX':{'emoji':'🤠','fact':'Texas was an independent republic from 1836 to 1846'},
    'FL':{'emoji':'🌴','fact':'Florida has more golf courses per capita than any other state'},
    'GA':{'emoji':'🍑','fact':'Atlanta is home to more Fortune 500 companies than any other Southern city'},
    'NC':{'emoji':'🏔️','fact':'North Carolina is the birthplace of powered flight'},
    'TN':{'emoji':'🎸','fact':'Tennessee is home to more than 3,900 documented caves'},
    'VA':{'emoji':'🏛️','fact':'Eight US Presidents were born in Virginia'},
    'AZ':{'emoji':'🌵','fact':'Arizona does not observe daylight saving time'},
    'CO':{'emoji':'⛰️','fact':'Colorado has 58 mountain peaks over 14,000 feet'},
    'WA':{'emoji':'🌲','fact':'Washington produces more apples than any other state'},
    'MI':{'emoji':'🚗','fact':'Michigan touches four of the five Great Lakes'},
    'OH':{'emoji':'🏈','fact':'Ohio has produced more US Presidents than any other state'},
    'IL':{'emoji':'🌆','fact':'Chicago is the birthplace of the modern skyscraper'},
    'PA':{'emoji':'🔔','fact':'Pennsylvania had the first commercial oil well in the world'},
    'IN':{'emoji':'🏎️','fact':'The Indianapolis 500 is the largest single-day sporting event in the world'},
    'MA':{'emoji':'🦞','fact':'Massachusetts was home to the first public school in America'},
    'MN':{'emoji':'❄️','fact':'Minnesota has over 11,000 lakes'},
    'MO':{'emoji':'🌉','fact':'Missouri is the Gateway to the West'},
    'NV':{'emoji':'🎰','fact':'Las Vegas has more hotel rooms than any other city in America'},
    'OR':{'emoji':'🌲','fact':'Crater Lake is the deepest lake in the United States'},
    'LA':{'emoji':'🎺','fact':'New Orleans is the birthplace of jazz music'},
    'KY':{'emoji':'🏇','fact':'Kentucky produces 95 percent of the world\'s bourbon whiskey'},
    'OK':{'emoji':'🌪️','fact':'Oklahoma has more man-made lakes than any other state'},
    'SC':{'emoji':'🌺','fact':'South Carolina was the site of the first battle of the Civil War'},
    'AL':{'emoji':'🌹','fact':'Alabama was the birthplace of the Civil Rights Movement'},
    'MD':{'emoji':'🦀','fact':'Maryland is home to the United States Naval Academy'},
    'WI':{'emoji':'🧀','fact':'Wisconsin produces over 3 billion pounds of cheese annually'},
    'AR':{'emoji':'💎','fact':'Arkansas is the only US state with an active diamond mine open to the public'},
    'MS':{'emoji':'🎵','fact':'Mississippi is the birthplace of blues music'},
    'IA':{'emoji':'🌽','fact':'Iowa produces more corn than any other state'},
    'KS':{'emoji':'🌾','fact':'Kansas produces enough wheat to feed the world for two weeks'},
    'NJ':{'emoji':'🏖️','fact':'New Jersey is the most densely populated state in America'},
    'NY':{'emoji':'🗽','fact':'New York City has more people than 40 of the 50 US states'},
    'CA':{'emoji':'🌞','fact':'California has the fifth largest economy in the world'},
    'UT':{'emoji':'🏜️','fact':'Utah has the highest literacy rate of any state'},
    'NM':{'emoji':'🌶️','fact':'New Mexico has more PhD scientists per capita than any other state'},
    'ID':{'emoji':'🥔','fact':'Idaho produces one-third of all potatoes in the United States'},
    'MT':{'emoji':'🦌','fact':'Montana has more cattle than people'},
    'AK':{'emoji':'🐻','fact':'Alaska is larger than the next three biggest states combined'},
    'HI':{'emoji':'🌺','fact':'Hawaii is the only US state composed entirely of islands'},
    'WV':{'emoji':'🏔️','fact':'West Virginia is the only state formed by seceding from a Confederate state'},
    'ND':{'emoji':'🦅','fact':'North Dakota produces more honey and sunflowers than any other state'},
    'SD':{'emoji':'🗿','fact':'South Dakota is home to Mount Rushmore National Memorial'},
    'WY':{'emoji':'🐃','fact':'Wyoming was the first state to grant women the right to vote'},
    'NE':{'emoji':'🌽','fact':'Nebraska is the only state with a unicameral legislature'},
    'CT':{'emoji':'🏛️','fact':'Connecticut was the first state to enact laws governing automobiles'},
    'NH':{'emoji':'🍂','fact':'New Hampshire was the first colony to establish its own government'},
    'ME':{'emoji':'🦞','fact':'Maine produces 99 percent of all commercially grown blueberries'},
    'VT':{'emoji':'🍁','fact':'Vermont produces more maple syrup than any other state'},
    'RI':{'emoji':'⚓','fact':'Rhode Island is the smallest state in America'},
    'DE':{'emoji':'🦅','fact':'Delaware was the first state to ratify the US Constitution'},
    'DC':{'emoji':'🏛️','fact':'Washington DC is the capital of the United States of America'},
}

def get_state_info(abbr):
    return STATE_INFO.get(abbr, {'emoji':'📍','fact':f'A great state for local business growth'})

# Hard money borrower leads go to Maurice by email via his own Render backend.
# Deliberately NOT GoHighLevel — this is a separate business from the agency.
HARDMONEY_WEBHOOK = "https://dominion-demo-backend.onrender.com/hard-money-lead"

HM_LANG_HTML = "<div class='hml' id='hml'><button type='button' class='hml-btn' id='hmlBtn' aria-haspopup='listbox' aria-expanded='false'><span class='hml-f' id='hmlFlag'><svg viewBox='0 0 60 40'><rect width='60' height='40' fill='#B22234'/><g fill='#fff'><rect y='3.1' width='60' height='3.1'/><rect y='9.2' width='60' height='3.1'/><rect y='15.4' width='60' height='3.1'/><rect y='21.5' width='60' height='3.1'/><rect y='27.7' width='60' height='3.1'/><rect y='33.8' width='60' height='3.1'/></g><rect width='26' height='21.5' fill='#3C3B6E'/></svg></span><span id='hmlCode'>EN</span><svg class='hml-car' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='3' stroke-linecap='round'><polyline points='6 9 12 15 18 9'/></svg></button><div class='hml-menu' id='hmlMenu' role='listbox'><button type='button' class='hml-i' data-l='en' data-s='EN'><span class='hml-f'><svg viewBox='0 0 60 40'><rect width='60' height='40' fill='#B22234'/><g fill='#fff'><rect y='3.1' width='60' height='3.1'/><rect y='9.2' width='60' height='3.1'/><rect y='15.4' width='60' height='3.1'/><rect y='21.5' width='60' height='3.1'/><rect y='27.7' width='60' height='3.1'/><rect y='33.8' width='60' height='3.1'/></g><rect width='26' height='21.5' fill='#3C3B6E'/></svg></span>English</button><button type='button' class='hml-i' data-l='es' data-s='ES'><span class='hml-f'><svg viewBox='0 0 60 40'><rect width='20' height='40' fill='#006847'/><rect x='20' width='20' height='40' fill='#fff'/><rect x='40' width='20' height='40' fill='#CE1126'/><ellipse cx='30' cy='20' rx='4.4' ry='3.8' fill='none' stroke='#8C6239' stroke-width='1.5'/></svg></span>Español</button><button type='button' class='hml-i' data-l='zh-CN' data-s='ZH'><span class='hml-f'><svg viewBox='0 0 60 40'><rect width='60' height='40' fill='#DE2910'/><path fill='#FFDE00' d='M10 6l1.9 5.9H18l-5 3.6 1.9 5.9-5-3.7-5 3.7 1.9-5.9-5-3.6h6.1z'/><circle cx='22' cy='5' r='1.7' fill='#FFDE00'/><circle cx='26' cy='9' r='1.7' fill='#FFDE00'/><circle cx='26' cy='15' r='1.7' fill='#FFDE00'/><circle cx='22' cy='19' r='1.7' fill='#FFDE00'/></svg></span>中文</button><button type='button' class='hml-i' data-l='vi' data-s='VI'><span class='hml-f'><svg viewBox='0 0 60 40'><rect width='60' height='40' fill='#DA251D'/><path fill='#FF0' d='M30 10.5l2.8 8.6h9l-7.3 5.3 2.8 8.6-7.3-5.3-7.3 5.3 2.8-8.6-7.3-5.3h9z'/></svg></span>Tiếng Việt</button><button type='button' class='hml-i' data-l='ko' data-s='KO'><span class='hml-f'><svg viewBox='0 0 60 40'><rect width='60' height='40' fill='#fff'/><path d='M30 12a8 8 0 010 16 8 8 0 010-16z' fill='#CD2E3A'/><path d='M30 12a8 8 0 000 16 4 4 0 010-8 4 4 0 000-8z' fill='#0047A0'/><g stroke='#000' stroke-width='1.6'><path d='M11 11l4 5M9 13l4 5M49 24l-4 5M51 26l-4 5'/></g></svg></span>한국어</button><button type='button' class='hml-i' data-l='ru' data-s='RU'><span class='hml-f'><svg viewBox='0 0 60 40'><rect width='60' height='13.3' fill='#fff'/><rect y='13.3' width='60' height='13.3' fill='#0039A6'/><rect y='26.6' width='60' height='13.4' fill='#D52B1E'/></svg></span>Русский</button><button type='button' class='hml-i' data-l='pt' data-s='PT'><span class='hml-f'><svg viewBox='0 0 60 40'><rect width='60' height='40' fill='#009B3A'/><path d='M30 5l25 15-25 15L5 20z' fill='#FEDF00'/><circle cx='30' cy='20' r='8' fill='#002776'/></svg></span>Português</button></div></div>"

HM_LANG_CSS = '.hml{position:relative;font-family:system-ui,-apple-system,sans-serif;flex:0 0 auto}.hml-btn{display:flex;align-items:center;gap:10px;background:#0f0f1a;color:#a99e86;border:2px solid #d4af37;border-radius:6px;padding:12px 16px;cursor:pointer;font:inherit;font-size:15px;font-weight:700;letter-spacing:.05em;line-height:1;transition:background .15s,color .15s}.hml-btn:hover{background:#d4af37;color:#0a0a14}.hml-btn:focus-visible{outline:3px solid #d4af37;outline-offset:2px}.hml-car{width:13px;height:13px;opacity:.7;transition:transform .18s}.hml.open .hml-car{transform:rotate(180deg)}.hml-f{width:27px;height:18px;border-radius:3px;overflow:hidden;display:block;flex:0 0 auto;box-shadow:0 0 0 1px rgba(0,0,0,.35) inset}.hml-f svg{display:block;width:100%;height:100%}.hml-menu{position:absolute;right:0;top:calc(100% + 8px);min-width:210px;background:#0f0f1a;border:2px solid #d4af37;border-radius:6px;overflow:hidden;z-index:200;box-shadow:0 16px 40px -12px rgba(0,0,0,.75);opacity:0;transform:translateY(-6px);pointer-events:none;transition:opacity .16s,transform .16s}.hml.open .hml-menu{opacity:1;transform:none;pointer-events:auto}.hml-i{display:flex;align-items:center;gap:11px;width:100%;background:none;border:0;cursor:pointer;padding:12px 16px;font:inherit;font-size:15px;color:#eae4d8;text-align:left;border-bottom:1px solid rgba(212,175,55,.22)}.hml-i:last-child{border-bottom:0}.hml-i:hover,.hml-i:focus-visible{background:#d4af37;color:#0a0a14;outline:none}.hml-i.on{background:rgba(212,175,55,.2)}.goog-te-banner-frame,.skiptranslate iframe,#goog-gt-tt{display:none!important}body{top:0!important}.goog-text-highlight{background:none!important;box-shadow:none!important}@media(max-width:640px){.hml-btn{padding:10px 13px;font-size:14px}.hml-menu{min-width:186px}}'

HM_LANG_JS = "(function(){var r=document.getElementById('hml'),b=document.getElementById('hmlBtn'),mn=document.getElementById('hmlMenu'),fl=document.getElementById('hmlFlag'),cd=document.getElementById('hmlCode');function cur(){var m=document.cookie.match(/googtrans=\\/[^/]+\\/([a-zA-Z-]+)/);return (m&&m[1])||'en';}function paint(c){var hit=null;Array.prototype.forEach.call(mn.children,function(e){var on=e.dataset.l===c;e.classList.toggle('on',on);if(on)hit=e;});if(!hit)hit=mn.children[0];fl.innerHTML=hit.querySelector('.hml-f').innerHTML;cd.textContent=hit.dataset.s;}function set(c){if(c===cur())return;var h=location.hostname,v=(c==='en')?'/en/en':'/en/'+c;document.cookie='googtrans='+v+';path=/';document.cookie='googtrans='+v+';path=/;domain='+h;var p=h.split('.');if(p.length>1)document.cookie='googtrans='+v+';path=/;domain=.'+p.slice(-2).join('.');location.reload();}Array.prototype.forEach.call(mn.children,function(e){e.addEventListener('click',function(){set(e.dataset.l);});});b.addEventListener('click',function(ev){ev.stopPropagation();r.classList.toggle('open');b.setAttribute('aria-expanded',r.classList.contains('open'));});document.addEventListener('click',function(ev){if(!r.contains(ev.target))r.classList.remove('open');});document.addEventListener('keydown',function(ev){if(ev.key==='Escape')r.classList.remove('open');});paint(cur());window.googleTranslateElementInit=function(){new google.translate.TranslateElement({pageLanguage:'en',includedLanguages:'en,es,zh-CN,vi,ko,ru,pt',autoDisplay:false},'google_translate_element');};var s=document.createElement('script');s.src='//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';document.body.appendChild(s);})();"

SCRIPTURE_BAR = ('<div style="background:#0a0a12;color:#c9a84c;padding:7px 22px;'
                 'font-family:system-ui,sans-serif;font-size:12px;font-weight:700;'
                 'letter-spacing:.08em;border-bottom:1px solid rgba(201,168,76,.25)">John 3:16</div>')


def fmt_county(value):
    """Louisiana has parishes, Alaska boroughs, VA/MO independent cities."""
    v = (value or "").strip()
    for suffix in (" County", " Parish", " Borough", " City", " Municipality", " Census Area"):
        if v.endswith(suffix):
            return v
    return v + " County" if v else v


def make_slug(city, abbr):
    slug = city.lower().replace(' ','-').replace("'","").replace('.','').replace(',','')
    return f"{slug}-{abbr.lower()}"

def get_state_slug(state):
    return state.lower().replace(' ','-')

# ============================================================
# PAGE BUILDERS — one per brand
# ============================================================

def _phone_digits(brand):
    return brand.get("phone_display", brand.get("phone", ""))


def build_leadpro_page(brand_key, city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    county = fmt_county(county)
    """Generic local-service city page. Used by all six Lead Pro brands."""
    brand = BRANDS[brand_key]
    slug = make_slug(city, abbr)
    state_info = get_state_info(abbr)
    c = brand["colors"]
    primary, accent, bg = c["primary"], c["accent"], c["bg"]
    base = "https://" + brand["domain"]
    phone = _phone_digits(brand)
    tel = "tel:+1" + ''.join(ch for ch in phone if ch.isdigit())

    title = folder_name + ' in ' + city + ', ' + state + ' | ' + brand["name"]
    desc = ('Professional ' + folder_name.lower() + ' in ' + city + ', ' + state + '. ' + brand["name"]
            + ' serves ' + city + ' and all of ' + county + '. Free quotes, fast scheduling, work starting at '
            + brand["starting_price"] + '.')
    canonical = base + '/' + folder_slug + '/' + slug + '.html'

    city_intro = (city + ' sits in ' + county + ', ' + state + ', in the ' + region + ' region. '
        + 'Homes and businesses here deal with the same weather everyone in ' + state + ' deals with — heat, humidity, '
        + 'storms, and the wear that comes with all of it. That is exactly the kind of thing ' + folder_name.lower()
        + ' is meant to handle. ' + brand["name"] + ' works with property owners across ' + city + ' and the surrounding '
        + county + ' area, from single-family homes to commercial buildings and rental properties. '
        + 'Every job starts with a free quote so you know the number before anyone touches your property. '
        + 'If you are comparing ' + folder_name.lower() + ' options near ' + city + ', call ' + phone
        + ' and we will walk you through what the work actually involves and what it costs.')

    schema = ('{"@context":"https://schema.org","@type":"LocalBusiness","name":"' + brand["name"]
        + '","description":"' + brand["pitch"].replace('"', "'")
        + '","telephone":"' + phone + '","url":"' + canonical
        + '","areaServed":{"@type":"City","name":"' + city.replace('"', "'") + '","addressRegion":"' + abbr
        + '"},"geo":{"@type":"GeoCoordinates","latitude":"' + str(lat) + '","longitude":"' + str(lng)
        + '"},"priceRange":"' + brand["starting_price"] + '+"}')

    crumbs = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        + '{"@type":"ListItem","position":1,"name":"Home","item":"' + base + '/"},'
        + '{"@type":"ListItem","position":2,"name":"' + folder_name + '","item":"' + base + '/' + folder_slug + '/"},'
        + '{"@type":"ListItem","position":3,"name":"' + city.replace('"', "'") + ', ' + abbr + '","item":"' + canonical + '"}]}')

    css = ('*{box-sizing:border-box}body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;'
        'background:' + bg + ';color:#1a2332;line-height:1.6}'
        'a{color:inherit}header{background:' + primary + ';color:#fff;padding:14px 22px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}'
        'header .logo{font-weight:800;font-size:1.05em;text-decoration:none;color:#fff}'
        'header nav{margin-left:auto;display:flex;gap:16px;flex-wrap:wrap}'
        'header nav a{color:rgba(255,255,255,.85);text-decoration:none;font-size:.86em}'
        'header nav a:hover{color:' + accent + '}'
        '.hero{background:linear-gradient(135deg,' + primary + ',#000);color:#fff;padding:52px 22px;text-align:center}'
        '.hero h1{font-size:1.9em;margin:0 0 10px;line-height:1.2}'
        '.hero p{max-width:640px;margin:0 auto 22px;opacity:.88}'
        '.btn{background:' + accent + ';color:' + primary + ';padding:14px 30px;border-radius:6px;text-decoration:none;'
        'font-weight:700;display:inline-block}'
        '.btn-outline{border:2px solid rgba(255,255,255,.5);color:#fff;background:none;margin-left:8px}'
        '.wrap{max-width:900px;margin:0 auto;padding:44px 22px}'
        'h2{font-size:1.35em;border-bottom:3px solid ' + accent + ';padding-bottom:8px;margin:0 0 18px}'
        '.intro{background:#fff;border-left:4px solid ' + accent + ';padding:22px;border-radius:4px;margin-bottom:30px;color:#334155}'
        '.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-bottom:26px}'
        '.card{background:#fff;border:1px solid #e2e8f0;border-left:4px solid ' + accent + ';border-radius:8px;padding:15px}'
        '.card h3{margin:0 0 5px;font-size:.95em}.card p{margin:0;font-size:.82em;color:#64748b}'
        '.card a{text-decoration:none}'
        '.callout{background:' + primary + ';color:#fff;padding:26px 22px;border-radius:8px;text-align:center;margin-top:30px}'
        '.callout a{color:' + accent + ';font-weight:700}'
        'footer{background:' + primary + ';color:rgba(255,255,255,.62);padding:26px 22px;text-align:center;font-size:.8em}'
        'footer a{color:rgba(255,255,255,.8)}'
        '@media(max-width:560px){.hero h1{font-size:1.45em}.btn-outline{margin:10px 0 0;display:block}}')

    html = '<!DOCTYPE html><html lang="en"><head>'
    html += '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    html += '<title>' + title + '</title>'
    html += '<meta name="description" content="' + desc + '">'
    html += '<link rel="canonical" href="' + canonical + '">'
    html += '<meta name="geo.region" content="US-' + abbr + '"><meta name="geo.placename" content="' + city + '">'
    html += '<meta name="ICBM" content="' + str(lat) + ', ' + str(lng) + '">'
    html += '<meta property="og:title" content="' + title + '"><meta property="og:description" content="' + desc + '">'
    html += '<meta property="og:type" content="website"><meta property="og:url" content="' + canonical + '">'
    html += '<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>' + brand["favicon"] + '</text></svg>">'
    html += '<script type="application/ld+json">' + schema + '</script>'
    html += '<script type="application/ld+json">' + crumbs + '</script>'
    html += '<style>' + css + '</style>'
    html += '</head><body>'
    html += SCRIPTURE_BAR

    html += '<header><a class="logo" href="' + base + '/">' + brand["favicon"] + ' ' + brand["name"] + '</a><nav>'
    for fs, fn in brand["service_folders"][:5]:
        html += '<a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + '</a>'
    html += '<a href="' + tel + '">' + phone + '</a></nav></header>'

    html += '<div class="hero"><h1>' + folder_name + ' in ' + city + ', ' + state + '</h1>'
    html += '<p>' + brand["pitch"] + ' Serving ' + city + ' and all of ' + county + '. Work starting at ' + brand["starting_price"] + '.</p>'
    html += '<a class="btn" href="' + tel + '">' + brand["cta"] + ' — ' + phone + '</a>'
    html += '<a class="btn btn-outline" href="' + base + '/">See All Services</a></div>'

    html += '<div class="wrap">'
    html += '<h2>' + folder_name + ' in ' + city + ', ' + state + '</h2>'
    html += '<div class="intro">' + city_intro + '</div>'

    html += '<h2>Other Services We Offer in ' + city + '</h2><div class="grid">'
    for fs, fn in brand["service_folders"]:
        if fs == folder_slug:
            continue
        html += '<div class="card"><h3><a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + ' in ' + city + '</a></h3>'
        html += '<p>' + fn + ' for homes and businesses across ' + county + '.</p></div>'
    html += '</div>'

    html += '<h2>Why ' + city + ' Property Owners Call Us</h2><div class="grid">'
    html += '<div class="card"><h3>Free Quotes</h3><p>You get the price before any work starts. No surprises on the invoice.</p></div>'
    html += '<div class="card"><h3>Local Crews</h3><p>We work ' + city + ' and the surrounding ' + county + ' area regularly.</p></div>'
    html += '<div class="card"><h3>Fast Scheduling</h3><p>Most ' + city + ' jobs get on the calendar within the same week.</p></div>'
    html += '<div class="card"><h3>Insured Work</h3><p>Fully insured, so your property is covered while we are on it.</p></div>'
    html += '</div>'

    html += '<div class="callout"><strong>Need ' + folder_name.lower() + ' in ' + city + '?</strong><br>'
    html += 'Call <a href="' + tel + '">' + phone + '</a> for a free quote today.</div>'
    html += '</div>'

    html += '<footer>&copy; 2026 ' + brand["name"] + ' &middot; Serving ' + city + ', ' + county + ', ' + state
    html += ' and all of ' + region + ' &middot; <a href="' + base + '/">Home</a><br>'
    html += state_info["emoji"] + ' ' + state_info["fact"] + '</footer>'
    html += '</body></html>'
    return html


def _leadpro_builder(brand_key):
    def _builder(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
        return build_leadpro_page(brand_key, city, state, abbr, region, county, lat, lng, folder_slug, folder_name)
    return _builder


build_houstonwash_page = _leadpro_builder("houstonwash")
build_houstonhvac_page = _leadpro_builder("houstonhvac")
build_houstonroofing_page = _leadpro_builder("houstonroofing")
build_dallaswash_page = _leadpro_builder("dallaswash")
build_dallashvac_page = _leadpro_builder("dallashvac")
build_dallasroofing_page = _leadpro_builder("dallasroofing")

def build_solarpro_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    county = fmt_county(county)
    slug = make_slug(city, abbr)
    state_info = get_state_info(abbr)
    title = folder_name + ' in ' + city + ', ' + state + ' | Dominion Solar Pro'
    desc = 'Shop the best ' + folder_name.lower() + ' near ' + city + ', ' + state + '. Jackery solar generators, portable power stations, and solar panels for camping, RV, home backup, and off-grid living. Free shipping.'
    city_intro = city + ' is a community in ' + county + ', ' + state + ', situated in the heart of ' + region + '. Like much of ' + state + ', ' + city + ' experiences a wide range of weather — from intense summer heat to severe storms that can knock out power for hours or even days. That makes reliable portable power not just a convenience but a necessity for ' + city + ' residents, campers, RV travelers, and off-grid homesteaders across ' + region + '. Whether you are spending a weekend at one of ' + region + 's many outdoor destinations, living the van life across ' + state + ', running a remote job site in ' + county + ', or simply want peace of mind when the next storm rolls through — a Jackery solar generator gives you clean, quiet, zero-emission power wherever you are. No fuel, no fumes, no noise. Just sunlight turning into electricity, ready when you need it most in ' + city + ' and across ' + state + '.'
    html = '<html lang="en"><head>'
    html += '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    html += '<title>' + title + '</title>'
    html += '<meta name="description" content="' + desc + '">'
    html += '<link rel="canonical" href="https://dominionsolarpro.com/' + folder_slug + '/' + slug + '.html">'
    html += '<style>body{font-family:sans-serif;margin:0;background:#f8fafc;color:#1a2332}header{background:#1a2332;color:#fff;padding:16px 24px;display:flex;align-items:center;gap:12px}header h1{font-size:1.2em;margin:0}.hero{background:linear-gradient(135deg,#1a2332,#2d4a6e);color:#fff;padding:48px 24px;text-align:center}.hero h2{font-size:2em;margin-bottom:12px;color:#f59e0b}.hero p{max-width:640px;margin:0 auto 24px;opacity:0.85;line-height:1.7}.btn{background:#f59e0b;color:#1a2332;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:1em;display:inline-block}.section{padding:48px 24px;max-width:900px;margin:0 auto}.section h3{color:#1a2332;font-size:1.4em;border-bottom:3px solid #f59e0b;padding-bottom:8px;margin-bottom:20px}.city-intro{background:#fff;border-left:4px solid #f59e0b;padding:24px;border-radius:4px;margin-bottom:32px;line-height:1.8;color:#334155}.kw-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:32px}.kw-card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;border-left:4px solid #f59e0b}.kw-card h4{margin:0 0 6px;color:#1a2332;font-size:0.95em}.kw-card p{margin:0;font-size:0.82em;color:#64748b;line-height:1.5}footer{background:#1a2332;color:rgba(255,255,255,0.6);padding:24px;text-align:center;font-size:0.82em}</style>'
    html += '</head><body>'
    html += SCRIPTURE_BAR
    html += '<header><a href="https://dominionsolarpro.com/" style="color:#fff;text-decoration:none;font-weight:700"><span style="font-size:1.3em">☀️</span> Dominion Solar Pro</a>'
    html += '<nav style="margin-left:auto;display:flex;gap:14px;flex-wrap:wrap">'
    for _fs, _fn in BRANDS['solarpro']['service_folders'][:5]:
        html += '<a href="https://dominionsolarpro.com/' + _fs + '/' + slug + '.html" style="color:rgba(255,255,255,.8);text-decoration:none;font-size:.85em">' + _fn + '</a>'
    html += '</nav></header>'
    html += '<h1 style="max-width:1100px;margin:28px auto 0;padding:0 24px">' + folder_name + ' in ' + city + ', ' + state + '</h1>'
    html += '<div class="hero"><h2>Best ' + folder_name + ' near ' + city + ', ' + state + '</h2>'
    html += '<p>Jackery solar generators, portable power stations, and solar panels — perfect for ' + city + ' residents, campers, RV travelers, and off-grid homesteaders across ' + region + '. Free shipping nationwide.</p>'
    html += '<a href="https://www.jackery.com?aff=1363" class="btn" target="_blank">Shop Solar Generators on Jackery.com →</a></div>'
    html += '<div class="section"><h3>Solar Power in ' + city + ', ' + state + '</h3>'
    html += '<div class="city-intro">' + city_intro + '</div>'
    html += '<h3>' + folder_name + ' — Popular Searches near ' + city + '</h3>'
    html += '<div class="kw-grid">'
    html += '<div class="kw-card"><h4>Solar Generator ' + city + '</h4><p>Complete kits — power station plus solar panels bundled for ' + city + ' residents.</p></div>'
    html += '<div class="kw-card"><h4>Portable Power Station ' + city + '</h4><p>Standalone power stations — charge from wall, car, or solar panel anywhere in ' + county + '.</p></div>'
    html += '<div class="kw-card"><h4>Jackery ' + city + ' ' + state + '</h4><p>Official Jackery products — the #1 portable solar brand trusted by millions worldwide.</p></div>'
    html += '<div class="kw-card"><h4>Solar Generator for Camping ' + city + '</h4><p>Lightweight solar power for weekend camping and outdoor adventures in ' + region + '.</p></div>'
    html += '<div class="kw-card"><h4>Home Backup Solar ' + city + '</h4><p>Keep your fridge, lights, and devices running during ' + state + ' power outages.</p></div>'
    html += '<div class="kw-card"><h4>RV Solar Generator ' + city + '</h4><p>Full RV power without hookups — go anywhere across ' + state + ' off-grid.</p></div>'
    html += '<div class="kw-card"><h4>Off Grid Solar ' + county + '</h4><p>Remote cabins, homesteads, and job sites — power anywhere in ' + county + '.</p></div>'
    html += '<div class="kw-card"><h4>Emergency Power ' + city + '</h4><p>Storm and severe weather backup — keep your family safe when the grid goes down in ' + region + '.</p></div>'
    html += '<div class="kw-card"><h4>Solar Panels ' + city + '</h4><p>Foldable, lightweight solar panels that charge any Jackery station from the sun.</p></div>'
    html += '<div class="kw-card"><h4>Best Solar Generator ' + state + '</h4><p>Top-rated solar generators for ' + state + ' — camping, RV, home backup, and off-grid.</p></div>'
    html += '</div>'
    html += '<section style="max-width:1100px;margin:44px auto 0;padding:0 24px">'
    html += '<h2 style="font-size:1.3em;border-bottom:2px solid #f5a623;padding-bottom:8px">More for ' + city + '</h2>'
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:18px">'
    for _fs, _fn in BRANDS['solarpro']['service_folders']:
        if _fs == folder_slug:
            continue
        html += '<a href="https://dominionsolarpro.com/' + _fs + '/' + slug + '.html" style="display:block;background:#fff;border:1px solid #e2e8f0;border-left:3px solid #f5a623;border-radius:8px;padding:14px;text-decoration:none;color:#1a2332">'
        html += '<strong>' + _fn + ' in ' + city + '</strong></a>'
    html += '</div></section>'
    html += '<p style="text-align:center;margin-top:28px"><a href="https://dominionsolarpro.com/" style="color:#1a2332">← All Dominion Solar Pro guides</a></p>'
    html += '<p style="text-align:center;margin-top:32px"><a href="https://www.jackery.com?aff=1363" class="btn" target="_blank">Shop All Jackery Solar Products →</a></p>'
    html += '<p style="text-align:center;margin-top:16px;font-size:0.8em;color:#94a3b8">Affiliate Disclosure: Dominion Solar Pro is a Jackery authorized affiliate. We may earn a commission on purchases at no extra cost to you.</p>'
    html += '</div>'
    html += '<footer>© 2026 Dominion Solar Pro | Serving ' + city + ', ' + county + ', ' + state + ' and all of ' + region + ' | ' + state_info["emoji"] + ' ' + state_info["fact"] + '</footer>'
    html += '</body></html>'
    return html

def build_hardmoney_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    brand = BRANDS["hardmoney"]
    county = fmt_county(county)
    slug = make_slug(city, abbr)
    state_info = get_state_info(abbr)
    c = brand["colors"]
    primary, accent, bg = c["primary"], c["accent"], c["bg"]
    base = "https://" + brand["domain"]
    phone = brand.get("phone_display", "903-636-7511")
    tel = "tel:+1" + "".join(ch for ch in phone if ch.isdigit())

    title = folder_name + " in " + city + ", " + state + " | Dominion Hard Money"
    desc = ("Private money and " + folder_name.lower() + " for real estate investors in " + city + ", " + state
            + ". Asset-based lending from " + brand["starting_price"] + ", funding in days rather than months.")
    canonical = base + "/" + folder_slug + "/" + slug + ".html"

    intro = (city + " sits in " + county + ", " + state + ". Investors working this market run into the same wall "
        "everyone else does — a conventional lender wants two years of returns, a full appraisal cycle, and thirty to "
        "forty-five days before anyone sees a dollar. Distressed deals do not wait that long. "
        "Dominion Hard Money is a private money brokerage. We place your deal with private lenders who "
        "underwrite the asset instead of the borrower's tax returns, which is why a "
        + city + " deal can close in days. We arrange financing for purchases, rehabs, and refinances across " + state
        + ", from single-family flips to small multifamily and rental portfolios. Loans start at "
        + brand["starting_price"] + ". Terms depend on the property, the exit, and the numbers — not on how long you have been in business.")

    schema = ('{"@context":"https://schema.org","@type":"FinancialService","name":"Dominion Hard Money",'
        '"description":"' + brand["pitch"].replace('"', "'") + '",'
        '"telephone":"' + phone + '","url":"' + canonical + '",'
        '"areaServed":{"@type":"City","name":"' + city.replace('"', "'") + '","addressRegion":"' + abbr + '"},'
        '"geo":{"@type":"GeoCoordinates","latitude":"' + str(lat) + '","longitude":"' + str(lng) + '"},'
        '"serviceType":"' + folder_name + '"}')

    crumbs = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"' + base + '/"},'
        '{"@type":"ListItem","position":2,"name":"' + folder_name + '","item":"' + base + '/' + folder_slug + '/"},'
        '{"@type":"ListItem","position":3,"name":"' + city.replace('"', "'") + ', ' + abbr + '","item":"' + canonical + '"}]}')

    css = ("*{box-sizing:border-box}body{font-family:Georgia,'Times New Roman',serif;margin:0;background:" + bg +
        ";color:#16202e;line-height:1.65}a{color:inherit}"
        "header{background:" + primary + ";color:#fff;padding:15px 22px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}"
        "header .logo{font-weight:700;font-size:1.05em;text-decoration:none;color:#fff;letter-spacing:.4px}"
        "header nav{margin-left:auto;display:flex;gap:15px;flex-wrap:wrap;font-family:system-ui,sans-serif}"
        "header nav a{color:rgba(255,255,255,.82);text-decoration:none;font-size:.83em}"
        "header nav a:hover{color:" + accent + "}"
        ".hero{background:linear-gradient(150deg," + primary + ",#050d18);color:#fff;padding:56px 22px;text-align:center}"
        ".hero h1{font-size:2em;margin:0 0 12px;line-height:1.18}"
        ".hero .kicker{font-family:system-ui,sans-serif;font-size:.75em;letter-spacing:.18em;text-transform:uppercase;"
        "color:" + accent + ";margin-bottom:14px}"
        ".hero p{max-width:660px;margin:0 auto 24px;opacity:.85}"
        ".btn{display:inline-block;background:" + accent + ";color:" + primary + ";padding:14px 30px;border-radius:3px;"
        "text-decoration:none;font-family:system-ui,sans-serif;font-weight:700}"
        ".btn-o{border:1px solid rgba(255,255,255,.45);color:#fff;background:none;margin-left:8px}"
        ".wrap{max-width:880px;margin:0 auto;padding:46px 22px}"
        "h2{font-size:1.3em;border-bottom:2px solid " + accent + ";padding-bottom:8px;margin:0 0 18px}"
        ".intro{background:#fff;border-left:3px solid " + accent + ";padding:22px;margin-bottom:30px}"
        ".terms{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:28px;"
        "font-family:system-ui,sans-serif}"
        ".term{background:#fff;border:1px solid #ded8c8;padding:15px;text-align:center}"
        ".term b{display:block;font-size:1.45em;color:" + primary + "}"
        ".term span{font-size:.78em;color:#6b6455;letter-spacing:.06em;text-transform:uppercase}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:12px;margin-bottom:26px}"
        ".card{background:#fff;border:1px solid #ded8c8;border-left:3px solid " + accent + ";padding:15px}"
        ".card h3{margin:0 0 5px;font-size:.98em}.card p{margin:0;font-size:.85em;color:#6b6455}"
        ".card a{text-decoration:none}"
        ".callout{background:" + primary + ";color:#fff;padding:26px;text-align:center;margin-top:28px}"
        ".callout a{color:" + accent + ";font-weight:700}"
        "footer{background:" + primary + ";color:rgba(255,255,255,.6);padding:26px 22px;text-align:center;"
        "font-size:.8em;font-family:system-ui,sans-serif}footer a{color:rgba(255,255,255,.8)}"
        "@media(max-width:560px){.hero h1{font-size:1.5em}.btn-o{margin:10px 0 0;display:block}}"
        ".apply{background:#fff;border:1px solid #d9d2c4;border-top:4px solid " + primary + ";"
        "border-radius:10px;padding:34px 32px;margin:44px 0;font-family:system-ui,sans-serif}"
        ".apply h2{font-family:Georgia,serif;font-size:1.5em}"
        ".apply-sub{color:#5d564a;font-size:.94em;margin:8px 0 22px}"
        ".f-head{font-family:Georgia,serif;font-size:1.02em;color:" + primary + ";border-bottom:1px solid #e6e0d3;padding-bottom:7px;margin:26px 0 4px}"
        ".f-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}"
        ".apply label{display:block;font-size:.72em;font-weight:700;letter-spacing:.06em;"
        "text-transform:uppercase;color:#6b6455;margin:14px 0 5px}"
        ".apply input,.apply select,.apply textarea{width:100%;padding:12px 13px;border:1.5px solid #d9d2c4;"
        "border-radius:7px;font:inherit;font-size:.95em;background:#fdfcfa;color:#16202e}"
        ".apply input:focus,.apply select:focus,.apply textarea:focus{outline:0;border-color:" + primary + "}"
        ".apply input[aria-invalid=true]{border-color:#c0392b}"
        ".apply textarea{min-height:92px;resize:vertical}"
        ".apply .err{display:block;color:#c0392b;font-size:.8em;font-weight:600;margin-top:4px}"
        ".consent{display:flex!important;gap:11px;align-items:flex-start;margin-top:20px;background:#faf7f1;"
        "border:1px solid #e6e0d3;border-radius:8px;padding:14px 16px;text-transform:none!important;"
        "letter-spacing:0!important;font-size:.85em!important;font-weight:400!important;color:#4a4437!important}"
        ".consent input{width:19px!important;height:19px;flex:0 0 auto;margin-top:2px}"
        ".apply-btn{display:block;width:100%;text-align:center;margin-top:20px;border:0;cursor:pointer;font-size:1em}"
        ".apply-note{font-size:.8em;color:#6b6455;margin-top:14px;text-align:center}"
        ".apply-done{display:none;text-align:center;padding:30px 10px}"
        ".apply-done.on{display:block}.apply-done h3{font-family:Georgia,serif;font-size:1.4em;color:" + primary + "}"
        ".apply-done p{color:#5d564a;font-size:.94em;margin-top:8px}"
        "@media(max-width:640px){.f-row{grid-template-columns:1fr}.apply{padding:26px 20px}}"
        + HM_LANG_CSS)

    html = '<!DOCTYPE html><html lang="en"><head>'
    html += '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    html += '<title>' + title + '</title>'
    html += '<meta name="description" content="' + desc + '">'
    html += '<link rel="canonical" href="' + canonical + '">'
    html += '<meta name="geo.region" content="US-' + abbr + '"><meta name="geo.placename" content="' + city + '">'
    html += '<meta name="ICBM" content="' + str(lat) + ', ' + str(lng) + '">'
    html += '<meta property="og:title" content="' + title + '"><meta property="og:description" content="' + desc + '">'
    html += '<meta property="og:type" content="website"><meta property="og:url" content="' + canonical + '">'
    html += '<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>' + brand["favicon"] + '</text></svg>">'
    html += '<script type="application/ld+json">' + schema + '</script>'
    html += '<script type="application/ld+json">' + crumbs + '</script>'
    html += '<style>' + css + '</style></head><body>'
    html += SCRIPTURE_BAR

    html += '<header><a class="logo" href="' + base + '/">' + brand["favicon"] + ' Dominion Hard Money</a><nav>'
    for fs, fn in brand["service_folders"][:5]:
        html += '<a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + '</a>'
    html += '<a href="' + tel + '">' + phone + '</a>' + HM_LANG_HTML + '</nav></header>'

    html += '<div class="hero"><div class="kicker">' + city + ', ' + state + '</div>'
    html += '<h1>' + folder_name + ' in ' + city + ', ' + state + '</h1>'
    html += '<p>' + brand["pitch"] + ' Asset-based lending for investors in ' + city
    html += ' and across ' + state + '. Loans from ' + brand["starting_price"] + '.</p>'
    html += '<a class="btn" href="' + tel + '">' + brand["cta"] + ' — ' + phone + '</a>'
    html += '<a class="btn btn-o" href="' + base + '/">All Loan Programs</a></div>'

    html += '<div class="wrap">'
    html += '<h2>' + folder_name + ' for ' + city + ' Investors</h2>'
    html += '<div class="intro">' + intro + '</div>'

    html += '<div class="terms">'
    html += '<div class="term"><b>Days</b><span>Typical close</span></div>'
    html += '<div class="term"><b>' + brand["starting_price"] + '</b><span>Loan minimum</span></div>'
    html += '<div class="term"><b>Asset</b><span>Based on the deal</span></div>'
    html += '<div class="term"><b>1–4</b><span>Unit residential</span></div>'
    html += '</div>'

    html += '<h2>Other Programs Available in ' + city + '</h2><div class="grid">'
    for fs, fn in brand["service_folders"]:
        if fs == folder_slug:
            continue
        html += '<div class="card"><h3><a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + ' in ' + city + '</a></h3>'
        html += '<p>' + fn + ' for investors across ' + county + ' and ' + state + '.</p></div>'
    html += '</div>'

    html += '<h2>What Investors Use This For</h2><div class="grid">'
    html += '<div class="card"><h3>Auction and foreclosure buys</h3><p>Deals with a closing clock a bank cannot meet.</p></div>'
    html += '<div class="card"><h3>Rehab and resale</h3><p>Purchase plus renovation on one loan, repaid at sale.</p></div>'
    html += '<div class="card"><h3>Rental refinance</h3><p>DSCR loans qualified on the property income, not tax returns.</p></div>'
    html += '<div class="card"><h3>Bridge financing</h3><p>Short-term capital while a longer-term loan is arranged.</p></div>'
    html += '</div>'

    # ── BORROWER VETTING ────────────────────────────────────────────────
    # Fields taken from the Capital Syndicate Borrower Vetting Worksheet
    # (Module 4B) plus the 5 Basic Musts and 3 Must-Nots from Module 4C.
    # Entity and occupancy are first because they are instant disqualifiers.
    html += '<div class="apply" id="apply">'
    html += '<h2 style="margin-top:0">Get your deal reviewed</h2>'
    html += '<p class="apply-sub">Answer these and we will tell you whether it is fundable, on what terms, '
    html += 'and how fast it could close. Investment property only &mdash; we do not lend on a home you will live in.</p>'
    html += '<form id="dealForm" novalidate>'

    html += '<div class="f-head">About you</div>'
    html += '<div class="f-row">'
    html += '<div><label for="fname">Name</label><input id="fname" type="text" autocomplete="name"></div>'
    html += '<div><label for="fphone">Phone</label><input id="fphone" type="tel" autocomplete="tel"></div>'
    html += '</div>'
    html += '<div class="f-row">'
    html += '<div><label for="femail">Email</label><input id="femail" type="email" autocomplete="email"></div>'
    html += '<div><label for="fentity">Buying in an entity?</label><select id="fentity">'
    html += '<option value="">Choose one</option><option>Yes &mdash; LLC or corporation</option>'
    html += '<option>Not yet, but I can set one up</option><option>No &mdash; personal name only</option>'
    html += '</select></div></div>'
    html += '<div class="f-row">'
    html += '<div><label for="fcredit">Credit score range</label><select id="fcredit">'
    html += '<option value="">Choose one</option><option>720+</option><option>680&ndash;719</option>'
    html += '<option>650&ndash;679</option><option>600&ndash;649</option><option>Under 600</option>'
    html += '<option>Not sure</option></select></div>'
    html += '<div><label for="fexp">Deals completed</label><select id="fexp">'
    html += '<option value="">Choose one</option><option>This is my first</option><option>1&ndash;3</option>'
    html += '<option>4&ndash;9</option><option>10 or more</option></select></div>'
    html += '</div>'

    html += '<div class="f-head">The property</div>'
    html += '<div class="f-row">'
    html += '<div><label for="faddr">Property address or city</label><input id="faddr" type="text" value="' + city + ', ' + abbr + '"></div>'
    html += '<div><label for="fpurpose">Purchase or refinance?</label><select id="fpurpose">'
    html += '<option value="">Choose one</option><option>Purchase</option><option>Refinance</option>'
    html += '<option>Cash-out refinance</option></select></div>'
    html += '</div>'
    html += '<div class="f-row">'
    html += '<div><label for="ftype">What are you doing with it?</label><select id="ftype">'
    html += '<option>Fix and flip &mdash; sell it</option><option>Fix and keep &mdash; rent it</option>'
    html += '<option>Bridge &mdash; short-term while I arrange other financing</option>'
    html += '<option>DSCR rental loan</option><option>Not sure yet</option></select></div>'
    html += '<div><label for="foccupy">Will you live in it?</label><select id="foccupy">'
    html += '<option value="">Choose one</option><option>No &mdash; investment property</option>'
    html += '<option>Yes</option></select></div>'
    html += '</div>'

    html += '<div class="f-head">The numbers</div>'
    html += '<div class="f-row">'
    html += '<div><label for="fprice">Purchase price</label><input id="fprice" type="text" placeholder="$"></div>'
    html += '<div><label for="fasis">Current as-is value</label><input id="fasis" type="text" placeholder="$"></div>'
    html += '</div>'
    html += '<div class="f-row">'
    html += '<div><label for="frehab">Rehab budget</label><input id="frehab" type="text" placeholder="$"></div>'
    html += '<div><label for="farv">Value after repair (ARV)</label><input id="farv" type="text" placeholder="$"></div>'
    html += '</div>'
    html += '<div class="f-row">'
    html += '<div><label for="famt">Loan amount needed</label><input id="famt" type="text" placeholder="$"></div>'
    html += '<div><label for="fdown">Cash you are putting in</label><input id="fdown" type="text" placeholder="$ or none"></div>'
    html += '</div>'
    html += '<label for="fexit">Exit strategy &mdash; how does the loan get paid back?</label>'
    html += '<textarea id="fexit" placeholder="Selling in six months, refinancing into a rental loan, timeline, and anything else we should know."></textarea>'

    html += '<label class="consent"><input type="checkbox" id="fsms">'
    html += '<span>Text me about this deal. By checking this box I agree to receive text messages from Dominion Hard Money '
    html += 'about my loan enquiry and its status. Message frequency varies. Message and data rates may apply. '
    html += 'Reply STOP to opt out or HELP for help. Optional &mdash; not required to submit.</span></label>'
    html += '<button class="btn apply-btn" type="submit" id="fbtn">Send my deal &rarr;</button>'
    html += '<p class="apply-note">Prefer to talk? Call <a href="' + tel + '">' + phone + '</a>. '
    html += 'Business-purpose loans on non-owner-occupied property only. Submitting this form is not an application '
    html += 'or a commitment to lend.</p>'
    html += '</form>'
    html += '<div class="apply-done" id="dealDone"><h3>Got it.</h3>'
    html += '<p>We will run the numbers and come back to you. If it is time-sensitive, call ' + phone + '.</p></div>'
    html += '</div>'

    html += '<div class="callout"><strong>Working a deal in ' + city + '?</strong><br>'
    html += 'Call <a href="' + tel + '">' + phone + '</a> and we will tell you in one conversation whether it is fundable.</div>'
    html += '<p style="font-size:.78em;color:#6b6455;margin-top:26px;font-family:system-ui,sans-serif">'
    html += 'Dominion Hard Money arranges private and asset-based real estate financing for business purposes only. '
    html += 'Not a commitment to lend. All loans subject to underwriting, property review, and approval. '
    html += 'Terms vary by property, borrower experience, and exit strategy.</p>'
    html += '</div>'

    # form handler — emails Maurice directly, never GoHighLevel
    html += '<script>(function(){'
    html += 'var W="' + HARDMONEY_WEBHOOK + '";'
    html += 'var f=document.getElementById("dealForm"),d=document.getElementById("dealDone"),b=document.getElementById("fbtn");'
    html += 'function g(i){return (document.getElementById(i)||{}).value||"";}'
    html += 'function clr(e){e.removeAttribute("aria-invalid");var x=document.getElementById("e-"+e.id);if(x)x.remove();}'
    html += 'function bad(e,m){clr(e);e.setAttribute("aria-invalid","true");var s=document.createElement("span");'
    html += 's.className="err";s.id="e-"+e.id;s.textContent=m;e.insertAdjacentElement("afterend",s);}'
    html += 'document.addEventListener("input",function(e){if(e.target.matches("input,textarea"))clr(e.target);});'
    html += 'document.addEventListener("change",function(e){if(e.target.matches("select"))clr(e.target);});'
    html += 'f.addEventListener("submit",function(ev){ev.preventDefault();'
    html += 'var n=document.getElementById("fname"),p=document.getElementById("fphone"),'
    html += 'm=document.getElementById("femail"),x=document.getElementById("fexit"),'
    html += 'oc=document.getElementById("foccupy");'
    html += '[n,p,m,x,oc].forEach(clr);var ok=true;'
    html += 'if(!n.value.trim()){bad(n,"Your name");ok=false;}'
    html += 'if(p.value.replace(/\\D/g,"").length<10){bad(p,"A 10-digit phone number");ok=false;}'
    html += 'if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(m.value.trim())){bad(m,"A valid email");ok=false;}'
    html += 'if(!oc.value){bad(oc,"Please answer this one");ok=false;}'
    html += 'if(!x.value.trim()){bad(x,"How does the loan get paid back?");ok=false;}'
    html += 'if(!ok)return;b.disabled=true;b.textContent="Sending...";'
    html += 'var pl={name:n.value.trim(),phone:p.value.trim(),email:m.value.trim(),'
    html += 'entity:g("fentity"),credit:g("fcredit"),experience:g("fexp"),'
    html += 'property:g("faddr"),purpose:g("fpurpose"),loan_type:g("ftype"),owner_occupied:g("foccupy"),'
    html += 'purchase_price:g("fprice"),as_is_value:g("fasis"),rehab:g("frehab"),arv:g("farv"),'
    html += 'loan_amount:g("famt"),cash_in:g("fdown"),exit_strategy:x.value.trim(),'
    html += 'sms_consent:document.getElementById("fsms").checked,'
    html += 'consent_timestamp:new Date().toISOString(),'
    html += 'source_city:"' + city + ', ' + abbr + '",source_state:"' + state + '",source_url:location.href};'
    html += 'function done(){f.style.display="none";d.classList.add("on");}'
    html += 'if(!W){done();return;}'
    html += 'fetch(W,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(pl)})'
    html += '.then(done).catch(function(){b.disabled=false;b.textContent="Send my deal \\u2192";'
    html += 'alert("Could not send that. Please call ' + phone + '.");});});})();</script>'

    html += '<div id="google_translate_element" style="display:none"></div>'
    html += '<script>' + HM_LANG_JS + '</script>'
    html += '<footer>&copy; 2026 Dominion Hard Money &middot; Serving ' + city + ', ' + county + ', ' + state
    html += ' and investors nationwide &middot; <a href="' + base + '/">Home</a><br>'
    html += state_info["emoji"] + ' ' + state_info["fact"] + '</footer>'
    html += '</body></html>'
    return html

def _miles(lat1, lng1, lat2, lng2):
    R = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1); dl = math.radians(lng2 - lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

METRO_EXTRA_CITIES = [
    # ---------- Houston metro : Harris County ----------
    ("Tomball", "Texas", "TX", "Southeast Texas", "Harris County", 30.0972, -95.6161),
    ("Cypress", "Texas", "TX", "Southeast Texas", "Harris County", 29.9691, -95.6972),
    ("Deer Park", "Texas", "TX", "Southeast Texas", "Harris County", 29.7052, -95.1238),
    ("La Porte", "Texas", "TX", "Southeast Texas", "Harris County", 29.6658, -95.0194),
    ("Bellaire", "Texas", "TX", "Southeast Texas", "Harris County", 29.7058, -95.4588),
    ("West University Place", "Texas", "TX", "Southeast Texas", "Harris County", 29.7180, -95.4344),
    ("Jersey Village", "Texas", "TX", "Southeast Texas", "Harris County", 29.8891, -95.5622),
    ("Galena Park", "Texas", "TX", "Southeast Texas", "Harris County", 29.7397, -95.2313),
    ("South Houston", "Texas", "TX", "Southeast Texas", "Harris County", 29.6627, -95.2377),
    ("Seabrook", "Texas", "TX", "Southeast Texas", "Harris County", 29.5638, -95.0230),
    ("Webster", "Texas", "TX", "Southeast Texas", "Harris County", 29.5377, -95.1183),
    ("Channelview", "Texas", "TX", "Southeast Texas", "Harris County", 29.7763, -95.1138),
    ("Crosby", "Texas", "TX", "Southeast Texas", "Harris County", 29.9127, -95.0621),
    ("Atascocita", "Texas", "TX", "Southeast Texas", "Harris County", 29.9993, -95.1766),
    ("Kingwood", "Texas", "TX", "Southeast Texas", "Harris County", 30.0530, -95.1815),
    ("Highlands", "Texas", "TX", "Southeast Texas", "Harris County", 29.8180, -95.0577),
    ("Hockley", "Texas", "TX", "Southeast Texas", "Harris County", 30.0405, -95.8330),

    # ---------- Houston metro : Fort Bend County ----------
    ("Stafford", "Texas", "TX", "Southeast Texas", "Fort Bend County", 29.6161, -95.5577),
    ("Richmond", "Texas", "TX", "Southeast Texas", "Fort Bend County", 29.5822, -95.7607),
    ("Rosenberg", "Texas", "TX", "Southeast Texas", "Fort Bend County", 29.5572, -95.8085),
    ("Fulshear", "Texas", "TX", "Southeast Texas", "Fort Bend County", 29.6905, -95.8913),
    ("Needville", "Texas", "TX", "Southeast Texas", "Fort Bend County", 29.3958, -95.8380),
    ("Fresno", "Texas", "TX", "Southeast Texas", "Fort Bend County", 29.5386, -95.4477),

    # ---------- Houston metro : Montgomery County ----------
    ("Magnolia", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.2094, -95.7513),
    ("Willis", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.4257, -95.4788),
    ("Montgomery", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.3888, -95.6963),
    ("Shenandoah", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.1830, -95.4530),
    ("Oak Ridge North", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.1594, -95.4519),
    ("New Caney", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.1519, -95.2130),
    ("Porter", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.1055, -95.2380),
    ("Splendora", "Texas", "TX", "Southeast Texas", "Montgomery County", 30.2333, -95.1608),

    # ---------- Houston metro : Galveston County ----------
    ("Friendswood", "Texas", "TX", "Southeast Texas", "Galveston County", 29.5294, -95.2010),
    ("Dickinson", "Texas", "TX", "Southeast Texas", "Galveston County", 29.4608, -95.0513),
    ("Texas City", "Texas", "TX", "Southeast Texas", "Galveston County", 29.3838, -94.9027),
    ("La Marque", "Texas", "TX", "Southeast Texas", "Galveston County", 29.3683, -94.9777),
    ("Santa Fe", "Texas", "TX", "Southeast Texas", "Galveston County", 29.3822, -95.1005),
    ("Galveston", "Texas", "TX", "Coastal Texas", "Galveston County", 29.3013, -94.7977),
    ("Kemah", "Texas", "TX", "Southeast Texas", "Galveston County", 29.5441, -95.0197),

    # ---------- Houston metro : Brazoria County ----------
    ("Manvel", "Texas", "TX", "Southeast Texas", "Brazoria County", 29.4788, -95.3577),
    ("Angleton", "Texas", "TX", "Southeast Texas", "Brazoria County", 29.1694, -95.4319),
    ("Lake Jackson", "Texas", "TX", "Southeast Texas", "Brazoria County", 29.0339, -95.4344),

    # ---------- Houston metro : outer counties ----------
    ("Waller", "Texas", "TX", "Southeast Texas", "Waller County", 30.0574, -95.9280),
    ("Hempstead", "Texas", "TX", "Southeast Texas", "Waller County", 30.0977, -96.0764),
    ("Brookshire", "Texas", "TX", "Southeast Texas", "Waller County", 29.7861, -95.9538),
    ("Cleveland", "Texas", "TX", "Southeast Texas", "Liberty County", 30.3413, -95.0855),

    # ---------- DFW : Dallas County ----------
    ("Duncanville", "Texas", "TX", "North Texas", "Dallas County", 32.6518, -96.9083),
    ("Cedar Hill", "Texas", "TX", "North Texas", "Dallas County", 32.5885, -96.9561),
    ("Lancaster", "Texas", "TX", "North Texas", "Dallas County", 32.5921, -96.7561),
    ("Balch Springs", "Texas", "TX", "North Texas", "Dallas County", 32.7287, -96.6228),
    ("Farmers Branch", "Texas", "TX", "North Texas", "Dallas County", 32.9268, -96.8961),
    ("Addison", "Texas", "TX", "North Texas", "Dallas County", 32.9618, -96.8292),
    ("Highland Park", "Texas", "TX", "North Texas", "Dallas County", 32.8332, -96.8022),
    ("University Park", "Texas", "TX", "North Texas", "Dallas County", 32.8507, -96.8003),
    ("Seagoville", "Texas", "TX", "North Texas", "Dallas County", 32.6540, -96.5383),
    ("Sachse", "Texas", "TX", "North Texas", "Dallas County", 32.9762, -96.5952),
    ("Sunnyvale", "Texas", "TX", "North Texas", "Dallas County", 32.7973, -96.5580),
    ("Glenn Heights", "Texas", "TX", "North Texas", "Dallas County", 32.5460, -96.8572),

    # ---------- DFW : Tarrant County ----------
    ("Bedford", "Texas", "TX", "North Texas", "Tarrant County", 32.8440, -97.1431),
    ("Haltom City", "Texas", "TX", "North Texas", "Tarrant County", 32.7996, -97.2692),
    ("Watauga", "Texas", "TX", "North Texas", "Tarrant County", 32.8579, -97.2547),
    ("Saginaw", "Texas", "TX", "North Texas", "Tarrant County", 32.8601, -97.3639),
    ("Benbrook", "Texas", "TX", "North Texas", "Tarrant County", 32.6732, -97.4606),
    ("Crowley", "Texas", "TX", "North Texas", "Tarrant County", 32.5793, -97.3628),
    ("White Settlement", "Texas", "TX", "North Texas", "Tarrant County", 32.7593, -97.4586),
    ("Trophy Club", "Texas", "TX", "North Texas", "Tarrant County", 33.0043, -97.1856),
    ("Forest Hill", "Texas", "TX", "North Texas", "Tarrant County", 32.6607, -97.2691),
    ("Kennedale", "Texas", "TX", "North Texas", "Tarrant County", 32.6468, -97.2258),
    ("Azle", "Texas", "TX", "North Texas", "Tarrant County", 32.8957, -97.5439),
    ("Richland Hills", "Texas", "TX", "North Texas", "Tarrant County", 32.8107, -97.2278),
    ("River Oaks", "Texas", "TX", "North Texas", "Tarrant County", 32.7752, -97.3944),
    ("Lake Worth", "Texas", "TX", "North Texas", "Tarrant County", 32.8085, -97.4453),
    ("Everman", "Texas", "TX", "North Texas", "Tarrant County", 32.6307, -97.2891),

    # ---------- DFW : Collin County ----------
    ("Murphy", "Texas", "TX", "North Texas", "Collin County", 33.0151, -96.6130),
    ("Princeton", "Texas", "TX", "North Texas", "Collin County", 33.1801, -96.4980),
    ("Anna", "Texas", "TX", "North Texas", "Collin County", 33.3495, -96.5486),
    ("Melissa", "Texas", "TX", "North Texas", "Collin County", 33.2857, -96.5728),
    ("Fairview", "Texas", "TX", "North Texas", "Collin County", 33.1451, -96.6314),
    ("Lucas", "Texas", "TX", "North Texas", "Collin County", 33.0854, -96.5772),
    ("Parker", "Texas", "TX", "North Texas", "Collin County", 33.0543, -96.6222),

    # ---------- DFW : Denton County ----------
    ("Little Elm", "Texas", "TX", "North Texas", "Denton County", 33.1626, -96.9375),
    ("Corinth", "Texas", "TX", "North Texas", "Denton County", 33.1540, -97.0647),
    ("Highland Village", "Texas", "TX", "North Texas", "Denton County", 33.0918, -97.0467),
    ("Argyle", "Texas", "TX", "North Texas", "Denton County", 33.1212, -97.1836),
    ("Justin", "Texas", "TX", "North Texas", "Denton County", 33.0846, -97.2969),
    ("Roanoke", "Texas", "TX", "North Texas", "Denton County", 33.0040, -97.2253),
    ("Sanger", "Texas", "TX", "North Texas", "Denton County", 33.3640, -97.1739),
    ("Aubrey", "Texas", "TX", "North Texas", "Denton County", 33.3043, -96.9861),

    # ---------- DFW : outer counties ----------
    ("Heath", "Texas", "TX", "North Texas", "Rockwall County", 32.8368, -96.4756),
    ("Royse City", "Texas", "TX", "North Texas", "Rockwall County", 32.9746, -96.3325),
    ("Fate", "Texas", "TX", "North Texas", "Rockwall County", 32.9418, -96.3811),
    ("Midlothian", "Texas", "TX", "North Texas", "Ellis County", 32.4826, -96.9944),
    ("Ennis", "Texas", "TX", "North Texas", "Ellis County", 32.3293, -96.6253),
    ("Red Oak", "Texas", "TX", "North Texas", "Ellis County", 32.5185, -96.8044),
    ("Ferris", "Texas", "TX", "North Texas", "Ellis County", 32.5340, -96.6644),
    ("Forney", "Texas", "TX", "North Texas", "Kaufman County", 32.7482, -96.4719),
    ("Terrell", "Texas", "TX", "North Texas", "Kaufman County", 32.7360, -96.2752),
    ("Kaufman", "Texas", "TX", "North Texas", "Kaufman County", 32.5885, -96.3086),
    ("Crandall", "Texas", "TX", "North Texas", "Kaufman County", 32.6274, -96.4530),
    ("Joshua", "Texas", "TX", "North Texas", "Johnson County", 32.4612, -97.3883),
    ("Alvarado", "Texas", "TX", "North Texas", "Johnson County", 32.4062, -97.2117),
    ("Aledo", "Texas", "TX", "North Texas", "Parker County", 32.6957, -97.6022),
    ("Willow Park", "Texas", "TX", "North Texas", "Parker County", 32.7549, -97.6459),
    ("Springtown", "Texas", "TX", "North Texas", "Parker County", 32.9654, -97.6828),
    # --- Tucson metro (Southern Arizona) ---
    ("Oro Valley", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.3909, -110.9665),
    ("Sahuarita", "Arizona", "AZ", "Southern Arizona", "Pima County", 31.9576, -110.9558),
    ("Vail", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.0490, -110.7118),
    ("Green Valley", "Arizona", "AZ", "Southern Arizona", "Pima County", 31.8543, -110.9937),
    ("Catalina Foothills", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.3020, -110.9192),
    ("Casas Adobes", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.3325, -111.0117),
    ("Drexel Heights", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.1273, -111.0221),
    ("Tanque Verde", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.2648, -110.7451),
    ("Corona de Tucson", "Arizona", "AZ", "Southern Arizona", "Pima County", 31.9540, -110.7737),
    ("Picture Rocks", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.3348, -111.1421),
    ("Flowing Wells", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.2870, -111.0092),
    ("South Tucson", "Arizona", "AZ", "Southern Arizona", "Pima County", 32.1948, -110.9686),
    ("Benson", "Arizona", "AZ", "Southern Arizona", "Cochise County", 31.9679, -110.2945),
    # --- Yuma County (Southwest Arizona) ---
    ("Fortuna Foothills", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.6570, -114.4108),
    ("Somerton", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.5965, -114.7097),
    ("San Luis", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.4870, -114.7822),
    ("Wellton", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.6721, -114.1480),
    ("Gadsden", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.5476, -114.7825),
    ("Roll", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.7554, -113.9800),
    ("Tacna", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.7017, -113.9500),
    ("Dateland", "Arizona", "AZ", "Southwest Arizona", "Yuma County", 32.8034, -113.5397),
]


def cities_for_brand(brand_key):
    """Cities this brand is allowed to build. Metro brands are limited to their
    radius; any brand can also exclude states it cannot legally serve."""
    brand = BRANDS[brand_key]
    blocked = set(brand.get("excluded_states") or [])
    c = brand.get("metro_center")
    if not c:
        return [cd for cd in ALL_US_CITIES if cd[2] not in blocked]
    rad = brand.get("metro_radius", 60)
    states = brand.get("metro_states")  # optional: restrict brand to these state abbrs
    pool, seen, out = list(ALL_US_CITIES) + list(METRO_EXTRA_CITIES), set(), []
    for cd in pool:
        key = make_slug(cd[0], cd[2])
        if key in seen:
            continue
        if states and cd[2] not in states:
            continue
        if cd[2] in blocked:
            continue
        if _miles(c[0], c[1], cd[5], cd[6]) <= rad:
            seen.add(key); out.append(cd)
    return out


def build_national_page(brand_key, city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    """Local landing page for the four national B2B brands (dark theme)."""
    brand = BRANDS[brand_key]
    county = fmt_county(county)
    slug = make_slug(city, abbr)
    state_info = get_state_info(abbr)
    base = "https://" + brand["domain"]
    accent, dark, light = brand["color"], brand["color_dark"], brand["color_light"]
    bg, bg2, border = brand["color_bg"], brand["color_bg2"], brand["color_border"]
    phone = brand["phone"]
    tel = "tel:+1" + "".join(ch for ch in phone if ch.isdigit())

    title = folder_name + " in " + city + ", " + state + " | " + brand["name"]
    desc = (brand["pitch"] + " Serving businesses in " + city + ", " + state
            + " and across " + county + ". From " + brand["starting_price"] + ".")
    canonical = base + "/" + folder_slug + "/" + slug + ".html"

    intro = (city + " is in " + county + ", " + state + ", and the businesses here compete for the same "
        "customers everyone else does — with fewer hands to do it. Most small operations in " + city
        + " lose work for one boring reason: nobody picked up, nobody followed up, or the website did not "
        "give anyone a reason to call. " + brand["name"] + " exists to close that gap. "
        "We work with " + city + " businesses across " + county + " and the wider " + region
        + " area, and the setup is the same whether you run one location or five. Pricing starts at "
        + brand["starting_price"] + ", month to month, no long contract.")

    schema = ('{"@context":"https://schema.org","@type":"Service","name":"' + folder_name
        + '","provider":{"@type":"Organization","name":"' + brand["name"] + '","telephone":"' + phone
        + '","url":"' + base + '/"},"areaServed":{"@type":"City","name":"' + city.replace('"', "'")
        + '","addressRegion":"' + abbr + '"},"description":"' + brand["pitch"].replace('"', "'")
        + '","url":"' + canonical + '"}')

    crumbs = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"' + base + '/"},'
        '{"@type":"ListItem","position":2,"name":"' + folder_name + '","item":"' + base + '/' + folder_slug + '/"},'
        '{"@type":"ListItem","position":3,"name":"' + city.replace('"', "'") + ', ' + abbr + '","item":"' + canonical + '"}]}')

    css = ("*{box-sizing:border-box}body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;"
        "background:" + bg + ";color:#e7e7f0;line-height:1.65}a{color:inherit}"
        "header{background:" + bg2 + ";border-bottom:1px solid " + border + ";padding:14px 22px;"
        "display:flex;align-items:center;gap:12px;flex-wrap:wrap}"
        "header .logo{font-weight:800;text-decoration:none;color:#fff;font-size:1.02em}"
        "header .logo span{color:" + accent + "}"
        "header nav{margin-left:auto;display:flex;gap:16px;flex-wrap:wrap}"
        "header nav a{color:#9a9ab4;text-decoration:none;font-size:.84em}header nav a:hover{color:" + light + "}"
        ".hero{padding:60px 22px;text-align:center;background:radial-gradient(900px 400px at 50% -10%," + dark + "55,transparent 70%)," + bg + "}"
        ".eyebrow{display:inline-block;border:1px solid " + border + ";color:" + light + ";font-size:.72em;"
        "letter-spacing:.16em;text-transform:uppercase;padding:6px 14px;border-radius:100px;margin-bottom:16px}"
        ".hero h1{font-size:2.05em;margin:0 0 12px;line-height:1.16;color:#fff}"
        ".hero p{max-width:640px;margin:0 auto 24px;color:#a9a9c2}"
        ".btn{display:inline-block;background:" + accent + ";color:#fff;padding:14px 30px;border-radius:8px;"
        "text-decoration:none;font-weight:700}"
        ".btn-o{background:none;border:1px solid " + border + ";color:#e7e7f0;margin-left:8px}"
        ".wrap{max-width:900px;margin:0 auto;padding:46px 22px}"
        "h2{font-size:1.28em;color:#fff;margin:0 0 16px}"
        "h2::after{content:'';display:block;width:46px;height:3px;background:" + accent + ";margin-top:8px;border-radius:2px}"
        ".intro{background:" + bg2 + ";border:1px solid " + border + ";border-left:3px solid " + accent + ";"
        "padding:22px;border-radius:8px;margin-bottom:30px;color:#b9b9cf}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-bottom:28px}"
        ".card{background:" + bg2 + ";border:1px solid " + border + ";border-radius:8px;padding:16px}"
        ".card h3{margin:0 0 6px;font-size:.96em;color:#fff}.card p{margin:0;font-size:.85em;color:#9a9ab4}"
        ".card a{text-decoration:none;color:" + light + "}"
        ".price{background:" + bg2 + ";border:1px solid " + border + ";border-radius:10px;padding:24px;text-align:center;margin-top:8px}"
        ".price b{display:block;font-size:1.9em;color:#fff}"
        ".price span{color:#9a9ab4;font-size:.88em}"
        ".callout{background:linear-gradient(135deg," + dark + "," + bg2 + ");border:1px solid " + border + ";"
        "border-radius:10px;padding:26px;text-align:center;margin-top:30px}"
        ".callout a{color:" + light + ";font-weight:700}"
        "footer{background:" + bg2 + ";border-top:1px solid " + border + ";color:#7e7e99;padding:26px 22px;"
        "text-align:center;font-size:.8em}footer a{color:#9a9ab4}"
        "@media(max-width:560px){.hero h1{font-size:1.55em}.btn-o{margin:10px 0 0;display:block}}")

    html = '<!DOCTYPE html><html lang="en"><head>'
    html += '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    html += '<title>' + title + '</title>'
    html += '<meta name="description" content="' + desc + '">'
    html += '<link rel="canonical" href="' + canonical + '">'
    html += '<meta name="geo.region" content="US-' + abbr + '"><meta name="geo.placename" content="' + city + '">'
    html += '<meta name="ICBM" content="' + str(lat) + ', ' + str(lng) + '">'
    html += '<meta property="og:title" content="' + title + '"><meta property="og:description" content="' + desc + '">'
    html += '<meta property="og:type" content="website"><meta property="og:url" content="' + canonical + '">'
    html += '<script type="application/ld+json">' + schema + '</script>'
    html += '<script type="application/ld+json">' + crumbs + '</script>'
    html += '<style>' + css + '</style></head><body>'
    html += SCRIPTURE_BAR

    html += '<header><a class="logo" href="' + base + '/">' + brand["name"].split()[0] + ' <span>'
    html += ' '.join(brand["name"].split()[1:]) + '</span></a><nav>'
    for fs, fn in brand["service_folders"][:5]:
        html += '<a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + '</a>'
    html += '<a href="' + tel + '">' + phone + '</a></nav></header>'

    html += '<div class="hero"><div class="eyebrow">' + city + ', ' + abbr + '</div>'
    html += '<h1>' + folder_name + ' in ' + city + ', ' + state + '</h1>'
    html += '<p>' + brand["tagline"] + ' ' + brand["pitch"] + '</p>'
    html += '<a class="btn" href="' + tel + '">' + brand["cta"] + '</a>'
    html += '<a class="btn btn-o" href="' + base + '/">See How It Works</a></div>'

    html += '<div class="wrap">'
    html += '<h2>' + folder_name + ' for ' + city + ' Businesses</h2>'
    html += '<div class="intro">' + intro + '</div>'

    html += '<h2>What Else We Do in ' + city + '</h2><div class="grid">'
    for fs, fn in brand["service_folders"]:
        if fs == folder_slug:
            continue
        html += '<div class="card"><h3><a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + '</a></h3>'
        html += '<p>' + fn + ' for businesses in ' + city + ' and across ' + county + '.</p></div>'
    html += '</div>'

    html += '<h2>Why ' + city + ' Businesses Use Us</h2><div class="grid">'
    html += '<div class="card"><h3>Set up for you</h3><p>We configure the whole thing. You are not learning software.</p></div>'
    html += '<div class="card"><h3>Month to month</h3><p>No annual contract. Cancel whenever it stops earning.</p></div>'
    html += '<div class="card"><h3>Works after hours</h3><p>Most missed opportunities happen when the office is closed.</p></div>'
    html += '<div class="card"><h3>One point of contact</h3><p>You deal with us directly, not a support queue.</p></div>'
    html += '</div>'

    html += '<div class="price"><b>' + brand["starting_price"] + '</b><span>Starting price &middot; setup included &middot; no contract</span></div>'

    html += '<div class="callout"><strong>Serving ' + city + ' and all of ' + county + '</strong><br>'
    html += 'Call <a href="' + tel + '">' + phone + '</a> or book a walkthrough and see it working on your own business.</div>'
    html += '</div>'

    html += '<footer>&copy; 2026 ' + brand["name"] + ' &middot; Serving ' + city + ', ' + county + ', ' + state
    html += ' and the ' + region + ' area &middot; <a href="' + base + '/">Home</a><br>'
    html += state_info["emoji"] + ' ' + state_info["fact"] + '</footer>'
    html += '</body></html>'
    return html


def _national_builder(brand_key):
    def _b(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
        return build_national_page(brand_key, city, state, abbr, region, county, lat, lng, folder_slug, folder_name)
    return _b


build_aivoice_page = _national_builder("aivoice")
build_reviewpro_page = _national_builder("reviewpro")
build_aiagency_page = _national_builder("aiagency")
build_webdesign_page = _national_builder("webdesign")


def build_phoenixpool_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    return build_leadpro_page("phoenixpool", city, state, abbr, region, county, lat, lng, folder_slug, folder_name)

def build_tucsonpool_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    return build_leadpro_page("tucsonpool", city, state, abbr, region, county, lat, lng, folder_slug, folder_name)

def build_yumapool_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    return build_leadpro_page("yumapool", city, state, abbr, region, county, lat, lng, folder_slug, folder_name)

PAGE_BUILDERS = {
    "aivoice": build_aivoice_page,
    "reviewpro": build_reviewpro_page,
    "aiagency": build_aiagency_page,
    "webdesign": build_webdesign_page,
    "hardmoney": build_hardmoney_page,
    "houstonwash": build_houstonwash_page,
    "houstonhvac": build_houstonhvac_page,
    "houstonroofing": build_houstonroofing_page,
    "dallaswash": build_dallaswash_page,
    "dallashvac": build_dallashvac_page,
    "dallasroofing": build_dallasroofing_page,
    "solarpro": build_solarpro_page,
    "phoenixpool": build_phoenixpool_page,
    "tucsonpool": build_tucsonpool_page,
    "yumapool": build_yumapool_page,
}


def purge_stale_folders(brand_key):
    """Remove ONLY folders explicitly listed as retired for this brand.

    Deliberately an allowlist, not "anything not in service_folders" — several
    brands legitimately hold directories the builder does not manage.
    """
    brand = BRANDS[brand_key]
    retired = brand.get("retired_folders") or []
    removed = 0
    for entry in retired:
        p = os.path.join(brand["work_dir"], entry)
        if not os.path.isdir(p):
            continue
        n = len(glob.glob(os.path.join(p, '**', '*.html'), recursive=True))
        shutil.rmtree(p); removed += n
        print(f"  PURGE: removed retired folder '{entry}' ({n} pages) from {brand['name']}")
    return removed


def purge_out_of_area(brand_key):
    """Delete page files for cities outside this brand's metro. Returns count removed."""
    brand = BRANDS[brand_key]
    if not brand.get("metro_center"):
        return 0
    allowed = {make_slug(cd[0], cd[2]) for cd in cities_for_brand(brand_key)}
    removed = 0
    for folder_slug, _ in brand["service_folders"]:
        for f in glob.glob(os.path.join(brand["work_dir"], folder_slug, "*.html")):
            if os.path.basename(f).replace('.html','') not in allowed:
                os.remove(f); removed += 1
    if removed:
        print(f"  PURGE: removed {removed} out-of-area pages from {brand['name']}")
    return removed


def purge_excluded_states(brand_key):
    """Delete pages for states the brand cannot legally serve.

    Hard money is the case this exists for: the site's own states page says we
    cannot originate loans or pay broker fees in NV, UT, SD or VT, while pages
    in those states were still advertising loans. Contradicting your own
    disclosure is the kind of thing a lender's compliance review picks up.
    """
    brand = BRANDS[brand_key]
    blocked = [st.lower() for st in (brand.get("excluded_states") or [])]
    if not blocked:
        return 0
    removed = 0
    for folder_slug, _ in brand["service_folders"]:
        for f in glob.glob(os.path.join(brand["work_dir"], folder_slug, "*.html")):
            stem = os.path.basename(f).replace('.html', '')
            if stem.rsplit('-', 1)[-1] in blocked:
                os.remove(f); removed += 1
    if removed:
        print(f"  PURGE: removed {removed} pages in excluded states "
              f"({', '.join(st.upper() for st in blocked)}) from {brand['name']}")
    return removed


def get_existing_slugs(brand_key):
    brand = BRANDS[brand_key]
    existing = set()
    first_folder = brand["service_folders"][0][0]
    pattern = os.path.join(brand["work_dir"], first_folder, "*.html")
    for f in glob.glob(pattern):
        existing.add(os.path.basename(f).replace('.html',''))
    return existing

def write_redirects(brand_key):
    """301 retired folder URLs to the brand's primary service folder."""
    brand = BRANDS[brand_key]
    retired = brand.get("retired_folders") or []
    extra_state_lines = []
    if not retired and not (brand.get("excluded_states") or []):
        return
    core = brand["service_folders"][0][0]
    rmap = brand.get("redirect_map") or {}
    # pages pulled for state ineligibility go to the states page, which explains why
    for st in (brand.get("excluded_states") or []):
        for fs, _ in brand["service_folders"]:
            extra_state_lines.append(f"/{fs}/*-{st.lower()}.html  /states.html  301")
    lines = ["# retired URL structures -> current service pages", ""]
    for folder in retired:
        target = rmap.get(folder, core)
        lines.append(f"/{folder}/*  /{target}/:splat  301")
        lines.append(f"/{folder}/  /{target}/  301")
    if extra_state_lines:
        lines += ["", "# states this brand cannot serve -> availability page"] + extra_state_lines
    with open(os.path.join(brand["work_dir"], "_redirects"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  wrote _redirects ({len(retired)} retired paths) for {brand['name']}")


def update_sitemap(brand_key):
    brand = BRANDS[brand_key]
    base = f"https://{brand['domain']}"
    pages = [f"{base}/"]
    for extra in ("index.html", "service-areas.html"):
        if os.path.exists(os.path.join(brand["work_dir"], extra)):
            pages.append(f"{base}/{extra}")
    for folder_slug, _ in brand["service_folders"]:
        for f in sorted(glob.glob(os.path.join(brand["work_dir"], folder_slug, "*.html"))):
            pages.append(f"{base}/{folder_slug}/{os.path.basename(f)}")
    today = datetime.now().strftime('%Y-%m-%d')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        priority = '1.0' if p.endswith('/') or p.endswith('index.html') else '0.8'
        xml += '  <url><loc>' + p + '</loc><lastmod>' + today + '</lastmod>'
        xml += '<changefreq>weekly</changefreq><priority>' + priority + '</priority></url>\n'
    xml += '</urlset>\n'

    # Only rewrite the sitemap if the URL set actually changed. Rewriting it
    # every night just to bump <lastmod> forces a commit, which forces a
    # Netlify deploy, which burns credits on brands that built nothing new.
    path = os.path.join(brand["work_dir"], "sitemap.xml")
    try:
        existing = open(path, encoding='utf-8').read()
        old_urls = set(re.findall(r'<loc>([^<]+)</loc>', existing))
        if old_urls == set(pages):
            return len(pages)
    except FileNotFoundError:
        pass

    with open(path, 'w', encoding='utf-8') as f:
        f.write(xml)
    return len(pages)


def git_push(brand_key, count_built, total):
    brand = BRANDS[brand_key]
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{brand['repo']}.git"
    os.chdir(brand["work_dir"])
    today = datetime.now().strftime('%Y-%m-%d')
    subprocess.run(['git','config','user.email','build@dominion.com'])
    subprocess.run(['git','config','user.name','Dominion Builder'])
    subprocess.run(['git', 'pull', '--rebase', repo_url, 'main'], capture_output=True, text=True)
    subprocess.run(['git','add','-A'])
    msg = (f'Daily build {today}: +{count_built} cities ({total} total) — {brand["name"]}'
           if count_built else f'Cleanup {today}: removed retired pages — {brand["name"]}')
    result = subprocess.run(['git','commit','-m',msg], capture_output=True, text=True)
    if 'nothing to commit' in result.stdout:
        print(f"  {brand['name']}: nothing new")
        return
    subprocess.run(['git','push', '--force', repo_url,'main'])
    print(f"  ✅ {brand['name']}: +{count_built} cities pushed ({total} total)")

RESERVED_FAKE = re.compile(r"\b555-01\d\d\b")

def build_brand(brand_key):
    brand = BRANDS[brand_key]
    _ph = brand.get("phone_display", "")
    if _ph and RESERVED_FAKE.search(_ph):
        print(f"  !! {brand['name']}: SKIPPED — phone_display {_ph} is a reserved placeholder number.")
        print(f"     Set a real number in BRANDS['{brand_key}']['phone_display'] before building.")
        return 0
    if not os.path.exists(brand['work_dir']):
        repo_url = f'https://{GITHUB_TOKEN}@github.com/{brand["repo"]}.git'
        subprocess.run(['git', 'clone', repo_url, brand['work_dir']])
    builder = PAGE_BUILDERS[brand_key]
    purged = 0
    if os.environ.get('PURGE') == '1':
        purged += purge_stale_folders(brand_key)
        purged += purge_out_of_area(brand_key)
        purged += purge_excluded_states(brand_key)
    brand_cities = cities_for_brand(brand_key)
    existing = get_existing_slugs(brand_key)
    seen = set()
    unbuilt = []
    for city_data in brand_cities:
        city, state, abbr, region, county, lat, lng = city_data
        slug = make_slug(city, abbr)
        if slug not in existing and slug not in seen:
            seen.add(slug)
            unbuilt.append(city_data)
    if os.environ.get('REBUILD') == '1':
        batch = [cd for cd in brand_cities if make_slug(cd[0], cd[2]) in existing]
        print(f"  REBUILD MODE: regenerating {len(batch)} existing cities")
        if not batch:
            if purged:
                print(f"  {brand['name']}: nothing to regenerate, but pushing {purged} deletions")
                update_sitemap(brand_key); write_redirects(brand_key); git_push(brand_key, 0, 0)
            else:
                print(f"  {brand['name']}: nothing to regenerate")
            return 0
    else:
        if not unbuilt:
            if purged:
                print(f"  {brand['name']}: all cities built — pushing {purged} purged pages")
                update_sitemap(brand_key); write_redirects(brand_key); git_push(brand_key, 0, 0)
            else:
                print(f"  {brand['name']}: ALL CITIES COMPLETE ✅")
            return 0
        batch = unbuilt[:CITIES_PER_DAY]
    built = 0
    for city_data in batch:
        city, state, abbr, region, county, lat, lng = city_data
        slug = make_slug(city, abbr)
        for folder_slug, folder_name in brand["service_folders"]:
            folder_path = os.path.join(brand["work_dir"], folder_slug)
            os.makedirs(folder_path, exist_ok=True)
            filepath = os.path.join(folder_path, f"{slug}.html")
            try:
                html = builder(city, state, abbr, region, county, lat, lng, folder_slug, folder_name)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
            except Exception as e:
                print(f"    ✗ {city} {folder_slug}: {e}")
        built += 1
        print(f"    ✓ {city}, {state}")
    total = len(existing) if os.environ.get('REBUILD') == '1' else len(existing) + built
    write_redirects(brand_key)
    sitemap_count = update_sitemap(brand_key)
    git_push(brand_key, built, total)
    return built

def main():
    print(f"\n{'='*60}")
    print(f"Dominion Brand Builder — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    total_built = 0
    only = [b.strip() for b in os.environ.get('ONLY_BRANDS', '').split(',') if b.strip()]
    if only:
        unknown = [b for b in only if b not in BRANDS]
        if unknown:
            print(f"  !! unknown brand key(s) in ONLY_BRANDS: {', '.join(unknown)}")
        print(f"  ONLY_BRANDS set — restricting this run to: {', '.join(only)}")
    for brand_key in BRANDS:
        if only and brand_key not in only:
            continue
        print(f"\n▶ Building {BRANDS[brand_key]['name']}...")
        count = build_brand(brand_key)
        total_built += count
    print(f"\n{'='*60}")
    print(f"TOTAL PAGES BUILT TODAY: {total_built * 20} ({total_built} cities × 20 folders × 4 brands)")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
