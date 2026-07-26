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
            ("ai-voice-agent", "AI Voice Agent"),
            ("ai-answering-service", "AI Answering Service"),
            ("ai-phone-answering", "AI Phone Answering"),
            ("ai-appointment-booking", "AI Appointment Booking"),
            ("ai-lead-qualification", "AI Lead Qualification"),
            ("ai-customer-service", "AI Customer Service"),
            ("ai-sales-agent", "AI Sales Agent"),
            ("ai-virtual-receptionist", "AI Virtual Receptionist"),
            ("ai-call-handling", "AI Call Handling"),
            ("ai-inbound-calls", "AI Inbound Calls"),
            ("ai-outbound-calls", "AI Outbound Calls"),
            ("ai-phone-agent", "AI Phone Agent"),
            ("ai-phone-system", "AI Phone System"),
            ("ai-voice-assistant", "AI Voice Assistant"),
            ("ai-voice-bot", "AI Voice Bot"),
            ("ai-business-calls", "AI Business Calls"),
            ("ai-call-center", "AI Call Center"),
            ("automated-phone-calls", "Automated Phone Calls"),
            ("conversational-ai", "Conversational AI"),
        ],
    },
    "reviewpro": {
        "repo": "dominionsoundmusic-create/dominionreviewpro-site",
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
            ("5-star-reviews", "5-Star Reviews"),
            ("google-review-management", "Google Review Management"),
            ("automated-review-requests", "Automated Review Requests"),
            ("get-more-google-reviews", "Get More Google Reviews"),
            ("online-reputation-management", "Online Reputation Management"),
            ("reputation-management", "Reputation Management"),
            ("google-business-reviews", "Google Business Reviews"),
            ("review-generation-service", "Review Generation Service"),
            ("sms-review-requests", "SMS Review Requests"),
            ("customer-review-automation", "Customer Review Automation"),
            ("review-request-service", "Review Request Service"),
            ("google-maps-ranking", "Google Maps Ranking"),
            ("increase-google-reviews", "Increase Google Reviews"),
            ("business-review-management", "Business Review Management"),
            ("local-business-reviews", "Local Business Reviews"),
            ("local-seo-reviews", "Local SEO Reviews"),
            ("review-management-software", "Review Management Software"),
            ("review-monitoring-service", "Review Monitoring Service"),
            ("negative-review-alerts", "Negative Review Alerts"),
            ("google-review-service", "Google Review Service"),
        ],
    },
    "aiagency": {
        "repo": "dominionsoundmusic-create/dominionaiagency-site",
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
            ("ai-agency", "AI Agency"),
            ("ai-automation-agency", "AI Automation Agency"),
            ("ai-business-automation", "AI Business Automation"),
            ("ai-chatbot-agency", "AI Chatbot Agency"),
            ("ai-consulting", "AI Consulting"),
            ("ai-crm-automation", "AI CRM Automation"),
            ("ai-customer-automation", "AI Customer Automation"),
            ("ai-digital-agency", "AI Digital Agency"),
            ("ai-for-business", "AI for Business"),
            ("ai-growth-agency", "AI Growth Agency"),
            ("ai-lead-generation", "AI Lead Generation"),
            ("ai-marketing-agency", "AI Marketing Agency"),
            ("ai-powered-agency", "AI Powered Agency"),
            ("ai-sales-automation", "AI Sales Automation"),
            ("ai-solutions", "AI Solutions"),
            ("ai-tools-for-business", "AI Tools for Business"),
            ("ai-workflow-automation", "AI Workflow Automation"),
            ("business-ai-automation", "Business AI Automation"),
            ("local-business-ai", "Local Business AI"),
            ("small-business-ai", "Small Business AI"),
        ],
    },
    "webdesign": {
        "repo": "dominionsoundmusic-create/dominionwebdesignpro-site",
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
        "pitch": "professional custom website built first — you only pay when you love it, starting at $497 with SEO, mobile design, and AI chat included",
        "favicon": "/favicon.svg",
        "service_folders": [
            ("web-design", "Web Design"),
            ("website-design", "Website Design"),
            ("custom-website-design", "Custom Website Design"),
            ("small-business-website", "Small Business Website"),
            ("local-business-website", "Local Business Website"),
            ("professional-website-design", "Professional Website Design"),
            ("affordable-web-design", "Affordable Web Design"),
            ("business-website-design", "Business Website Design"),
            ("seo-web-design", "SEO Web Design"),
            ("mobile-website-design", "Mobile Website Design"),
            ("lead-generation-website", "Lead Generation Website"),
            ("contractor-website-design", "Contractor Website Design"),
            ("restaurant-website-design", "Restaurant Website Design"),
            ("medical-website-design", "Medical Website Design"),
            ("real-estate-website-design", "Real Estate Website Design"),
            ("ecommerce-website-design", "Ecommerce Website Design"),
            ("ai-website-design", "AI Website Design"),
            ("website-designer", "Website Designer"),
            ("website-redesign", "Website Redesign"),
            ("wordpress-web-design", "WordPress Web Design"),
        ],
    },
    "hardmoney": {
        "repo": "dominionsoundmusic-create/dominion-hard-money",
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
        "domain": "sage-tarsier-f0ded1.netlify.app",
        "name": "Dallas Metro Power Washing Pro",
        "tagline": "Professional Power Washing in Dallas-Fort Worth TX",
        "cta": "Get a Free Quote",
        "phone": "two one four, five five five, zero one nine nine",
        "phone_display": "214-555-0199",
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
        "domain": "ornate-wisp-2520ba.netlify.app",
        "name": "Dallas Metro HVAC Pro",
        "tagline": "AC Repair and HVAC Service in Dallas-Fort Worth TX",
        "cta": "Call for Same-Day Service",
        "phone": "two one four, five five five, zero one nine nine",
        "phone_display": "214-555-0199",
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
        "domain": "splendid-sable-28fb05.netlify.app",
        "name": "Dallas Metro Roofing Pro",
        "tagline": "Roof Repair and Replacement in Dallas-Fort Worth TX",
        "cta": "Get Free Roof Inspection",
        "phone": "two one four, five five five, zero one nine nine",
        "phone_display": "214-555-0199",
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
    'solarpro': {
        'repo': 'dominionsoundmusic-create/dominionsolarpro-site',
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
    ("Abilene","Texas","TX","West Texas","Taylor County",30.4382,-99.7384),
    ("Akron","Ohio","OH","Northeast Ohio","Summit County",41.0814,-81.5190),
    ("Albany","Georgia","GA","Southwest Georgia","Dougherty County",31.5785,-84.1557),
    ("Albany","New York","NY","Capital Region","Albany County",42.6526,-73.7562),
    ("Albuquerque","New Mexico","NM","Central New Mexico","Bernalillo County",35.0844,-106.6504),
    ("Alexandria","Louisiana","LA","Central Louisiana","Rapides Parish",31.3113,-92.4452),
    ("Alexandria","Virginia","VA","Northern Virginia","Alexandria City",38.8048,-77.0469),
    ("Allen","Texas","TX","North Texas","Collin County",33.1032,-96.6705),
    ("Allentown","Pennsylvania","PA","Lehigh Valley","Lehigh County",40.6084,-75.4902),
    ("Alpharetta","Georgia","GA","Metro Atlanta","Fulton County",34.0754,-84.2941),
    ("Alvin","Texas","TX","Southeast Texas","Brazoria County",29.4238,-95.2441),
    ("Amarillo","Texas","TX","Panhandle Texas","Potter County",35.2220,-101.8313),
    ("Anaheim","California","CA","Southern California","Orange County",33.8366,-117.9143),
    ("Anchorage","Alaska","AK","Southcentral Alaska","Anchorage Municipality",61.2181,-149.9003),
    ("Anderson","Indiana","IN","Central Indiana","Madison County",40.1053,-85.6803),
    ("Anderson","South Carolina","SC","Upstate","Anderson County",34.5034,-82.6501),
    ("Ann Arbor","Michigan","MI","Southeast Michigan","Washtenaw County",42.2808,-83.7430),
    ("Anniston","Alabama","AL","Northeast Alabama","Calhoun County",33.6596,-85.8316),
    ("Apex","North Carolina","NC","Triangle","Wake County",35.7327,-78.8502),
    ("Appleton","Wisconsin","WI","Fox Valley","Outagamie County",44.2619,-88.4154),
    ("Arlington","Texas","TX","North Texas","Tarrant County",32.7357,-97.1081),
    ("Arvada","Colorado","CO","Front Range","Jefferson County",39.8028,-105.0875),
    ("Asheville","North Carolina","NC","Western NC","Buncombe County",35.5951,-82.5515),
    ("Athens","Georgia","GA","Northeast Georgia","Clarke County",33.9519,-83.3576),
    ("Atlanta","Georgia","GA","Metro Atlanta","Fulton County",33.7490,-84.3880),
    ("Auburn","Alabama","AL","East Alabama","Lee County",32.6099,-85.4808),
    ("Augusta","Georgia","GA","East Georgia","Richmond County",33.4735,-82.0105),
    ("Aurora","Colorado","CO","Front Range","Arapahoe County",39.7294,-104.8319),
    ("Aurora","Illinois","IL","Northeast Illinois","Kane County",41.7606,-88.3201),
    ("Austin","Texas","TX","Central Texas","Travis County",30.2672,-97.7431),
    ("Avondale","Arizona","AZ","Valley of the Sun","Maricopa County",33.4356,-112.3496),
    ("Bakersfield","California","CA","Central California","Kern County",35.3733,-119.0187),
    ("Baltimore","Maryland","MD","Central Maryland","Baltimore City",39.2904,-76.6122),
    ("Bartlett","Tennessee","TN","West Tennessee","Shelby County",35.2045,-89.8742),
    ("Baton Rouge","Louisiana","LA","South Central Louisiana","East Baton Rouge Parish",30.4515,-91.1871),
    ("Baytown","Texas","TX","Southeast Texas","Harris County",29.7355,-94.9774),
    ("Beaumont","Texas","TX","Southeast Texas","Jefferson County",30.0802,-94.1266),
    ("Beaverton","Oregon","OR","Willamette Valley","Washington County",45.4871,-122.8037),
    ("Bellevue","Washington","WA","Puget Sound","King County",47.6101,-122.2015),
    ("Bellingham","Washington","WA","Northwest Washington","Whatcom County",48.7519,-122.4787),
    ("Belton","Texas","TX","Central Texas","Bell County",31.0557,-97.4641),
    ("Bend","Oregon","OR","Central Oregon","Deschutes County",44.0582,-121.3153),
    ("Bentonville","Arkansas","AR","Northwest Arkansas","Benton County",36.3728,-94.2088),
    ("Bethlehem","Pennsylvania","PA","Lehigh Valley","Northampton County",40.6259,-75.3705),
    ("Big Spring","Texas","TX","West Texas","Howard County",32.2504,-101.4788),
    ("Billings","Montana","MT","South Central Montana","Yellowstone County",45.7833,-108.5007),
    ("Birmingham","Alabama","AL","North Central Alabama","Jefferson County",33.5186,-86.8104),
    ("Bismarck","North Dakota","ND","South Central ND","Burleigh County",46.8083,-100.7837),
    ("Bloomington","Indiana","IN","South Central Indiana","Monroe County",39.1653,-86.5264),
    ("Bloomington","Minnesota","MN","Twin Cities","Hennepin County",44.8408,-93.3771),
    ("Boca Raton","Florida","FL","Southeast Florida","Palm Beach County",26.3683,-80.1289),
    ("Boerne","Texas","TX","South Texas","Kendall County",29.7947,-98.7317),
    ("Boise","Idaho","ID","Southwest Idaho","Ada County",43.6150,-116.2023),
    ("Bonita Springs","Florida","FL","Southwest Florida","Lee County",26.3398,-81.7787),
    ("Boston","Massachusetts","MA","Greater Boston","Suffolk County",42.3601,-71.0589),
    ("Boulder","Colorado","CO","Front Range","Boulder County",40.0150,-105.2705),
    ("Bowling Green","Kentucky","KY","South Central Kentucky","Warren County",36.9685,-86.4808),
    ("Boynton Beach","Florida","FL","Southeast Florida","Palm Beach County",26.5317,-80.0905),
    ("Brentwood","Tennessee","TN","Middle Tennessee","Williamson County",36.0331,-86.7828),
    ("Broken Arrow","Oklahoma","OK","Northeast Oklahoma","Tulsa County",36.0526,-95.7908),
    ("Brooklyn Park","Minnesota","MN","Twin Cities","Hennepin County",45.0941,-93.3752),
    ("Brownsville","Texas","TX","South Texas","Cameron County",25.9017,-97.4975),
    ("Bryan","Texas","TX","Central Texas","Brazos County",30.6744,-96.3698),
    ("Buckeye","Arizona","AZ","Valley of the Sun","Maricopa County",33.3703,-112.5838),
    ("Buffalo","New York","NY","Western New York","Erie County",42.8864,-78.8784),
    ("Burleson","Texas","TX","North Texas","Johnson County",32.5421,-97.3208),
    ("Burlington","North Carolina","NC","Piedmont","Alamance County",36.0957,-79.4378),
    ("Cambridge","Massachusetts","MA","Greater Boston","Middlesex County",42.3736,-71.1097),
    ("Cape Coral","Florida","FL","Southwest Florida","Lee County",26.5629,-81.9495),
    ("Carrollton","Texas","TX","North Texas","Dallas County",32.9537,-96.8903),
    ("Cary","North Carolina","NC","Triangle","Wake County",35.7915,-78.7811),
    ("Cedar Park","Texas","TX","Central Texas","Williamson County",30.5052,-97.8203),
    ("Celina","Texas","TX","North Texas","Collin County",33.3251,-96.7836),
    ("Chandler","Arizona","AZ","Valley of the Sun","Maricopa County",33.3062,-111.8413),
    ("Chapel Hill","North Carolina","NC","Triangle","Orange County",35.9132,-79.0558),
    ("Charleston","South Carolina","SC","Lowcountry","Charleston County",32.7765,-79.9311),
    ("Charlotte","North Carolina","NC","Piedmont","Mecklenburg County",35.2271,-80.8431),
    ("Chattanooga","Tennessee","TN","Southeast Tennessee","Hamilton County",35.0456,-85.3097),
    ("Chesapeake","Virginia","VA","Hampton Roads","Chesapeake City",36.7682,-76.2875),
    ("Chicago","Illinois","IL","Northeast Illinois","Cook County",41.8781,-87.6298),
    ("Chula Vista","California","CA","Southern California","San Diego County",32.6401,-117.0842),
    ("Cincinnati","Ohio","OH","Southwest Ohio","Hamilton County",39.1031,-84.5120),
    ("Clarksville","Tennessee","TN","Middle Tennessee","Montgomery County",36.5298,-87.3595),
    ("Clearwater","Florida","FL","Tampa Bay","Pinellas County",27.9659,-82.8001),
    ("Cleburne","Texas","TX","North Texas","Johnson County",32.3474,-97.3869),
    ("Cleveland","Ohio","OH","Northeast Ohio","Cuyahoga County",41.4993,-81.6944),
    ("College Station","Texas","TX","Central Texas","Brazos County",30.6280,-96.3344),
    ("Colleyville","Texas","TX","North Texas","Tarrant County",32.8887,-97.1500),
    ("Colorado Springs","Colorado","CO","Front Range","El Paso County",38.8339,-104.8214),
    ("Columbia","Maryland","MD","Central Maryland","Howard County",39.2037,-76.8610),
    ("Columbia","Missouri","MO","Central Missouri","Boone County",38.9517,-92.3341),
    ("Columbia","South Carolina","SC","Midlands","Richland County",34.0007,-81.0348),
    ("Columbus","Georgia","GA","West Georgia","Muscogee County",32.4610,-84.9877),
    ("Columbus","Ohio","OH","Central Ohio","Franklin County",39.9612,-82.9988),
    ("Concord","North Carolina","NC","Piedmont","Cabarrus County",35.4088,-80.5795),
    ("Conroe","Texas","TX","Southeast Texas","Montgomery County",30.3119,-95.4561),
    ("Conway","Arkansas","AR","Central Arkansas","Faulkner County",35.0887,-92.4421),
    ("Coppell","Texas","TX","North Texas","Dallas County",32.9546,-97.0150),
    ("Coral Springs","Florida","FL","Southeast Florida","Broward County",26.2707,-80.2706),
    ("Corpus Christi","Texas","TX","Coastal Texas","Nueces County",27.8006,-97.3964),
    ("Covington","Kentucky","KY","Northern Kentucky","Kenton County",39.0837,-84.5086),
    ("Dallas","Texas","TX","North Texas","Dallas County",32.7767,-96.7970),
    ("Davenport","Iowa","IA","Quad Cities","Scott County",41.5236,-90.5776),
    ("Davie","Florida","FL","Southeast Florida","Broward County",26.0765,-80.2521),
    ("Dayton","Ohio","OH","Southwest Ohio","Montgomery County",39.7589,-84.1916),
    ("Daytona Beach","Florida","FL","East Central Florida","Volusia County",29.2108,-81.0228),
    ("Dearborn","Michigan","MI","Southeast Michigan","Wayne County",42.3223,-83.1763),
    ("Decatur","Alabama","AL","North Alabama","Morgan County",34.6059,-86.9833),
    ("Denton","Texas","TX","North Texas","Denton County",33.2148,-97.1331),
    ("Denver","Colorado","CO","Front Range","Denver County",39.7392,-104.9903),
    ("DeSoto","Texas","TX","North Texas","Dallas County",32.5896,-96.8572),
    ("Detroit","Michigan","MI","Southeast Michigan","Wayne County",42.3314,-83.0458),
    ("Doral","Florida","FL","Southeast Florida","Miami-Dade County",25.8196,-80.3554),
    ("Dothan","Alabama","AL","Southeast Alabama","Houston County",31.2232,-85.3905),
    ("Dripping Springs","Texas","TX","Central Texas","Hays County",30.1905,-98.0869),
    ("Dublin","Ohio","OH","Central Ohio","Franklin County",40.0992,-83.1141),
    ("Duluth","Minnesota","MN","Northern Minnesota","St Louis County",46.7867,-92.1005),
    ("Durham","North Carolina","NC","Triangle","Durham County",35.9940,-78.8986),
    ("Eagan","Minnesota","MN","Twin Cities","Dakota County",44.8041,-93.1669),
    ("Edinburg","Texas","TX","South Texas","Hidalgo County",26.3017,-98.1633),
    ("Edison","New Jersey","NJ","Central New Jersey","Middlesex County",40.5187,-74.4121),
    ("Edmond","Oklahoma","OK","Central Oklahoma","Oklahoma County",35.6528,-97.4781),
    ("El Paso","Texas","TX","West Texas","El Paso County",31.7619,-106.4850),
    ("Elizabeth","New Jersey","NJ","Northeast New Jersey","Union County",40.6640,-74.2107),
    ("Elk Grove","California","CA","Central California","Sacramento County",38.4088,-121.3716),
    ("Erie","Pennsylvania","PA","Northwest Pennsylvania","Erie County",42.1292,-80.0851),
    ("Eugene","Oregon","OR","Willamette Valley","Lane County",44.0521,-123.0868),
    ("Euless","Texas","TX","North Texas","Tarrant County",32.8371,-97.0819),
    ("Evansville","Indiana","IN","Southwest Indiana","Vanderburgh County",37.9716,-87.5711),
    ("Everett","Washington","WA","Puget Sound","Snohomish County",47.9790,-122.2021),
    ("Fargo","North Dakota","ND","Eastern North Dakota","Cass County",46.8772,-96.7898),
    ("Fayetteville","Arkansas","AR","Northwest Arkansas","Washington County",36.0626,-94.1574),
    ("Fayetteville","North Carolina","NC","Sandhills","Cumberland County",35.0527,-78.8784),
    ("Federal Way","Washington","WA","Puget Sound","King County",47.3223,-122.3126),
    ("Fishers","Indiana","IN","Central Indiana","Hamilton County",39.9567,-86.0133),
    ("Flagstaff","Arizona","AZ","Northern Arizona","Coconino County",35.1983,-111.6513),
    ("Flint","Michigan","MI","Mid-Michigan","Genesee County",43.0125,-83.6875),
    ("Florence","Alabama","AL","North Alabama","Lauderdale County",34.7998,-87.6773),
    ("Florence","South Carolina","SC","Pee Dee","Florence County",34.1954,-79.7626),
    ("Flower Mound","Texas","TX","North Texas","Denton County",33.0146,-97.0969),
    ("Fontana","California","CA","Southern California","San Bernardino County",34.0922,-117.4350),
    ("Fort Collins","Colorado","CO","Northern Colorado","Larimer County",40.5853,-105.0844),
    ("Fort Lauderdale","Florida","FL","Southeast Florida","Broward County",26.1224,-80.1373),
    ("Fort Myers","Florida","FL","Southwest Florida","Lee County",26.6406,-81.8723),
    ("Fort Smith","Arkansas","AR","River Valley","Sebastian County",35.3859,-94.3985),
    ("Fort Wayne","Indiana","IN","Northeast Indiana","Allen County",41.1306,-85.1289),
    ("Fort Worth","Texas","TX","North Texas","Tarrant County",32.7555,-97.3308),
    ("Franklin","Tennessee","TN","Middle Tennessee","Williamson County",35.9251,-86.8689),
    ("Fredericksburg","Virginia","VA","Northern Virginia","Fredericksburg City",38.3032,-77.4605),
    ("Fresno","California","CA","Central California","Fresno County",36.7378,-119.7871),
    ("Frisco","Texas","TX","North Texas","Collin County",33.1507,-96.8236),
    ("Gainesville","Florida","FL","North Central Florida","Alachua County",29.6516,-82.3248),
    ("Gainesville","Georgia","GA","Northeast Georgia","Hall County",34.2979,-83.8241),
    ("Garland","Texas","TX","North Texas","Dallas County",32.9126,-96.6389),
    ("Gastonia","North Carolina","NC","Piedmont","Gaston County",35.2621,-81.1873),
    ("Georgetown","Texas","TX","Central Texas","Williamson County",30.6332,-97.6775),
    ("Gilbert","Arizona","AZ","Valley of the Sun","Maricopa County",33.3528,-111.7890),
    ("Glendale","Arizona","AZ","Valley of the Sun","Maricopa County",33.5387,-112.1860),
    ("Grand Prairie","Texas","TX","North Texas","Dallas County",32.7460,-97.0000),
    ("Grand Rapids","Michigan","MI","West Michigan","Kent County",42.9634,-85.6681),
    ("Grapevine","Texas","TX","North Texas","Tarrant County",32.9343,-97.0781),
    ("Green Bay","Wisconsin","WI","Northeast Wisconsin","Brown County",44.5133,-88.0133),
    ("Greensboro","North Carolina","NC","Piedmont Triad","Guilford County",36.0726,-79.7920),
    ("Greenville","North Carolina","NC","Eastern NC","Pitt County",35.6127,-77.3663),
    ("Greenville","South Carolina","SC","Upstate","Greenville County",34.8526,-82.3940),
    ("Gresham","Oregon","OR","Willamette Valley","Multnomah County",45.5001,-122.4302),
    ("Hampton","Virginia","VA","Hampton Roads","Hampton City",37.0299,-76.3452),
    ("Harlingen","Texas","TX","South Texas","Cameron County",26.1906,-97.6961),
    ("Harrisburg","Pennsylvania","PA","South Central PA","Dauphin County",40.2732,-76.8867),
    ("Henderson","Kentucky","KY","Western Kentucky","Henderson County",37.8362,-87.5900),
    ("Henderson","Nevada","NV","Southern Nevada","Clark County",36.0397,-114.9819),
    ("Hendersonville","Tennessee","TN","Middle Tennessee","Sumner County",36.3020,-86.6197),
    ("Hialeah","Florida","FL","Southeast Florida","Miami-Dade County",25.8576,-80.2781),
    ("High Point","North Carolina","NC","Piedmont Triad","Guilford County",35.9557,-79.9553),
    ("Hillsboro","Oregon","OR","Willamette Valley","Washington County",45.5229,-122.9898),
    ("Hollywood","Florida","FL","Southeast Florida","Broward County",26.0112,-80.1495),
    ("Honolulu","Hawaii","HI","Oahu","City and County of Honolulu",21.3069,-157.8583),
    ("Hoover","Alabama","AL","North Central Alabama","Jefferson County",33.4054,-86.8113),
    ("Houston","Texas","TX","Southeast Texas","Harris County",29.7604,-95.3698),
    ("Humble","Texas","TX","Southeast Texas","Harris County",29.9988,-95.2627),
    ("Huntington","West Virginia","WV","Western WV","Cabell County",38.4193,-82.4452),
    ("Huntington Beach","California","CA","Southern California","Orange County",33.6595,-117.9988),
    ("Huntsville","Alabama","AL","North Alabama","Madison County",34.7304,-86.5861),
    ("Hurst","Texas","TX","North Texas","Tarrant County",32.8232,-97.1886),
    ("Indianapolis","Indiana","IN","Central Indiana","Marion County",39.7684,-86.1581),
    ("Irvine","California","CA","Southern California","Orange County",33.6839,-117.7947),
    ("Irving","Texas","TX","North Texas","Dallas County",32.8140,-96.9489),
    ("Jackson","Mississippi","MS","Central Mississippi","Hinds County",32.2988,-90.1848),
    ("Jackson","Tennessee","TN","West Tennessee","Madison County",35.6145,-88.8139),
    ("Jacksonville","Florida","FL","Northeast Florida","Duval County",30.3322,-81.6557),
    ("Jacksonville","North Carolina","NC","Coastal Plain","Onslow County",34.7540,-77.4302),
    ("Jersey City","New Jersey","NJ","Northeast New Jersey","Hudson County",40.7178,-74.0431),
    ("Johnson City","Tennessee","TN","Northeast Tennessee","Washington County",36.3134,-82.3535),
    ("Joliet","Illinois","IL","Northeast Illinois","Will County",41.5250,-88.0817),
    ("Jonesboro","Arkansas","AR","Northeast Arkansas","Craighead County",35.8423,-90.7043),
    ("Kansas City","Kansas","KS","Northeast Kansas","Wyandotte County",39.1155,-94.6268),
    ("Kansas City","Missouri","MO","Western Missouri","Jackson County",39.0997,-94.5786),
    ("Katy","Texas","TX","Southeast Texas","Harris County",29.7858,-95.8244),
    ("Keller","Texas","TX","North Texas","Tarrant County",32.9343,-97.2294),
    ("Kent","Washington","WA","Puget Sound","King County",47.3809,-122.2348),
    ("Killeen","Texas","TX","Central Texas","Bell County",31.1171,-97.7278),
    ("Kingsport","Tennessee","TN","Northeast Tennessee","Sullivan County",36.5484,-82.5618),
    ("Kirkland","Washington","WA","Puget Sound","King County",47.6815,-122.2087),
    ("Kissimmee","Florida","FL","Central Florida","Osceola County",28.2919,-81.4076),
    ("Knoxville","Tennessee","TN","East Tennessee","Knox County",35.9606,-83.9207),
    ("Kyle","Texas","TX","Central Texas","Hays County",29.9888,-97.8803),
    ("Lafayette","Louisiana","LA","South Central Louisiana","Lafayette Parish",30.2241,-92.0198),
    ("Lakeland","Florida","FL","Central Florida","Polk County",28.0395,-81.9498),
    ("Lakewood","Colorado","CO","Front Range","Jefferson County",39.7047,-105.0814),
    ("Lancaster","Pennsylvania","PA","South Central PA","Lancaster County",40.0379,-76.3055),
    ("Lansing","Michigan","MI","Mid-Michigan","Ingham County",42.7325,-84.5555),
    ("Laredo","Texas","TX","South Texas","Webb County",27.5036,-99.5075),
    ("Las Vegas","Nevada","NV","Southern Nevada","Clark County",36.1699,-115.1398),
    ("League City","Texas","TX","Southeast Texas","Galveston County",29.5075,-95.0949),
    ("Leander","Texas","TX","Central Texas","Williamson County",30.5788,-97.8531),
    ("Lee's Summit","Missouri","MO","Western Missouri","Jackson County",38.9108,-94.3827),
    ("Lewisville","Texas","TX","North Texas","Denton County",33.0462,-96.9942),
    ("Lexington","Kentucky","KY","Bluegrass Region","Fayette County",38.0406,-84.5037),
    ("Lincoln","Nebraska","NE","Eastern Nebraska","Lancaster County",40.8136,-96.7026),
    ("Little Rock","Arkansas","AR","Central Arkansas","Pulaski County",34.7465,-92.2896),
    ("Livonia","Michigan","MI","Southeast Michigan","Wayne County",42.3684,-83.3527),
    ("Long Beach","California","CA","Southern California","Los Angeles County",33.7701,-118.1937),
    ("Longview","Texas","TX","East Texas","Gregg County",32.5007,-94.7405),
    ("Los Angeles","California","CA","Southern California","Los Angeles County",34.0522,-118.2437),
    ("Louisville","Kentucky","KY","North Central Kentucky","Jefferson County",38.2527,-85.7585),
    ("Lubbock","Texas","TX","West Texas","Lubbock County",33.5779,-101.8552),
    ("Lufkin","Texas","TX","East Texas","Angelina County",31.3382,-94.7291),
    ("Lynchburg","Virginia","VA","Central Virginia","Lynchburg City",37.4138,-79.1422),
    ("Macon","Georgia","GA","Central Georgia","Bibb County",32.8407,-83.6324),
    ("Madison","Alabama","AL","North Alabama","Madison County",34.6993,-86.7483),
    ("Madison","Wisconsin","WI","South Central Wisconsin","Dane County",43.0731,-89.4012),
    ("Mansfield","Texas","TX","North Texas","Tarrant County",32.5632,-97.1417),
    ("Marietta","Georgia","GA","Metro Atlanta","Cobb County",33.9526,-84.5499),
    ("McAllen","Texas","TX","South Texas","Hidalgo County",26.2034,-98.2300),
    ("McKinney","Texas","TX","North Texas","Collin County",33.1972,-96.6397),
    ("Melbourne","Florida","FL","Space Coast","Brevard County",28.0836,-80.6081),
    ("Memphis","Tennessee","TN","West Tennessee","Shelby County",35.1495,-90.0490),
    ("Mesa","Arizona","AZ","Valley of the Sun","Maricopa County",33.4152,-111.8315),
    ("Mesquite","Texas","TX","North Texas","Dallas County",32.7668,-96.5992),
    ("Metairie","Louisiana","LA","Southeast Louisiana","Jefferson Parish",29.9940,-90.1626),
    ("Miami","Florida","FL","Southeast Florida","Miami-Dade County",25.7617,-80.1918),
    ("Miami Gardens","Florida","FL","Southeast Florida","Miami-Dade County",25.9420,-80.2456),
    ("Midland","Texas","TX","West Texas","Midland County",31.9973,-102.0779),
    ("Milwaukee","Wisconsin","WI","Southeast Wisconsin","Milwaukee County",43.0389,-87.9065),
    ("Minneapolis","Minnesota","MN","Twin Cities","Hennepin County",44.9778,-93.2650),
    ("Miramar","Florida","FL","Southeast Florida","Broward County",25.9871,-80.2338),
    ("Mission","Texas","TX","South Texas","Hidalgo County",26.2159,-98.3252),
    ("Missouri City","Texas","TX","Southeast Texas","Fort Bend County",29.6185,-95.5377),
    ("Mobile","Alabama","AL","South Alabama","Mobile County",30.6954,-88.0399),
    ("Modesto","California","CA","Central California","Stanislaus County",37.6391,-120.9969),
    ("Montgomery","Alabama","AL","Central Alabama","Montgomery County",32.3668,-86.2999),
    ("Moore","Oklahoma","OK","Central Oklahoma","Cleveland County",35.3395,-97.4867),
    ("Moreno Valley","California","CA","Southern California","Riverside County",33.9425,-117.2297),
    ("Murfreesboro","Tennessee","TN","Middle Tennessee","Rutherford County",35.8456,-86.3903),
    ("Naperville","Illinois","IL","Northeast Illinois","DuPage County",41.7508,-88.1535),
    ("Nashville","Tennessee","TN","Middle Tennessee","Davidson County",36.1627,-86.7816),
    ("New Braunfels","Texas","TX","South Texas","Comal County",29.7030,-98.1244),
    ("New Haven","Connecticut","CT","South Central Connecticut","New Haven County",41.3082,-72.9282),
    ("New Orleans","Louisiana","LA","Southeast Louisiana","Orleans Parish",29.9511,-90.0715),
    ("New York City","New York","NY","New York Metro","New York County",40.7128,-74.0060),
    ("Newark","New Jersey","NJ","Northeast New Jersey","Essex County",40.7357,-74.1724),
    ("Newport News","Virginia","VA","Hampton Roads","Newport News City",37.0871,-76.4730),
    ("Norfolk","Virginia","VA","Hampton Roads","Norfolk City",36.8508,-76.2859),
    ("Norman","Oklahoma","OK","Central Oklahoma","Cleveland County",35.2226,-97.4395),
    ("North Charleston","South Carolina","SC","Lowcountry","Charleston County",32.8546,-79.9748),
    ("North Las Vegas","Nevada","NV","Southern Nevada","Clark County",36.1989,-115.1175),
    ("North Richland Hills","Texas","TX","North Texas","Tarrant County",32.8343,-97.2289),
    ("Oakland","California","CA","Northern California","Alameda County",37.8044,-122.2712),
    ("Ocala","Florida","FL","North Central Florida","Marion County",29.1872,-82.1401),
    ("Odessa","Texas","TX","West Texas","Ector County",31.8457,-102.3676),
    ("Oklahoma City","Oklahoma","OK","Central Oklahoma","Oklahoma County",35.4676,-97.5164),
    ("Olathe","Kansas","KS","Northeast Kansas","Johnson County",38.8814,-94.8191),
    ("Olympia","Washington","WA","South Puget Sound","Thurston County",47.0379,-122.9007),
    ("Omaha","Nebraska","NE","Eastern Nebraska","Douglas County",41.2565,-95.9345),
    ("Ontario","California","CA","Southern California","San Bernardino County",34.0633,-117.6509),
    ("Orlando","Florida","FL","Central Florida","Orange County",28.5384,-81.3789),
    ("Overland Park","Kansas","KS","Northeast Kansas","Johnson County",38.9822,-94.6708),
    ("Oxnard","California","CA","Southern California","Ventura County",34.1975,-119.1771),
    ("Palm Bay","Florida","FL","Space Coast","Brevard County",27.9859,-80.6690),
    ("Pasadena","California","CA","Southern California","Los Angeles County",34.1478,-118.1445),
    ("Pasadena","Texas","TX","Southeast Texas","Harris County",29.6911,-95.2091),
    ("Paterson","New Jersey","NJ","Northeast New Jersey","Passaic County",40.9176,-74.1719),
    ("Pearland","Texas","TX","Southeast Texas","Brazoria County",29.5635,-95.2860),
    ("Pembroke Pines","Florida","FL","Southeast Florida","Broward County",26.0078,-80.2963),
    ("Pensacola","Florida","FL","Northwest Florida","Escambia County",30.4213,-87.2169),
    ("Peoria","Arizona","AZ","Valley of the Sun","Maricopa County",33.5806,-112.2374),
    ("Philadelphia","Pennsylvania","PA","Southeast Pennsylvania","Philadelphia County",39.9526,-75.1652),
    ("Phoenix","Arizona","AZ","Valley of the Sun","Maricopa County",33.4484,-112.0740),
    ("Pittsburgh","Pennsylvania","PA","Western Pennsylvania","Allegheny County",40.4406,-79.9959),
    ("Plano","Texas","TX","North Texas","Collin County",33.0198,-96.6989),
    ("Plymouth","Minnesota","MN","Twin Cities","Hennepin County",45.0105,-93.4555),
    ("Pompano Beach","Florida","FL","Southeast Florida","Broward County",26.2379,-80.1248),
    ("Port Arthur","Texas","TX","Southeast Texas","Jefferson County",29.8988,-93.9196),
    ("Port St Lucie","Florida","FL","Treasure Coast","St Lucie County",27.2730,-80.3582),
    ("Portland","Maine","ME","Southern Maine","Cumberland County",43.6591,-70.2568),
    ("Portland","Oregon","OR","Willamette Valley","Multnomah County",45.5051,-122.6750),
    ("Portsmouth","Virginia","VA","Hampton Roads","Portsmouth City",36.8354,-76.2983),
    ("Prosper","Texas","TX","North Texas","Collin County",33.2362,-96.8003),
    ("Providence","Rhode Island","RI","Providence County","Providence County",41.8240,-71.4128),
    ("Pueblo","Colorado","CO","Southern Colorado","Pueblo County",38.2544,-104.6091),
    ("Raleigh","North Carolina","NC","Triangle","Wake County",35.7796,-78.6382),
    ("Rancho Cucamonga","California","CA","Southern California","San Bernardino County",34.1064,-117.5931),
    ("Reno","Nevada","NV","Northern Nevada","Washoe County",39.5296,-119.8138),
    ("Renton","Washington","WA","Puget Sound","King County",47.4829,-122.2171),
    ("Richardson","Texas","TX","North Texas","Dallas County",32.9483,-96.7299),
    ("Richmond","Virginia","VA","Central Virginia","Richmond City",37.5407,-77.4360),
    ("Riverside","California","CA","Southern California","Riverside County",33.9533,-117.3962),
    ("Roanoke","Virginia","VA","Southwest Virginia","Roanoke City",37.2710,-79.9414),
    ("Rochester","Minnesota","MN","Southeast Minnesota","Olmsted County",44.0121,-92.4802),
    ("Rochester","New York","NY","Finger Lakes","Monroe County",43.1566,-77.6088),
    ("Rock Hill","South Carolina","SC","Piedmont","York County",34.9249,-81.0251),
    ("Rockford","Illinois","IL","Northern Illinois","Winnebago County",42.2711,-89.0940),
    ("Rockwall","Texas","TX","North Texas","Rockwall County",32.9293,-96.4597),
    ("Round Rock","Texas","TX","Central Texas","Williamson County",30.5083,-97.6789),
    ("Rowlett","Texas","TX","North Texas","Dallas County",32.9029,-96.5636),
    ("Sacramento","California","CA","Central California","Sacramento County",38.5816,-121.4944),
    ("Saint Paul","Minnesota","MN","Twin Cities","Ramsey County",44.9537,-93.0900),
    ("Salinas","California","CA","Central California","Monterey County",36.6777,-121.6555),
    ("Salt Lake City","Utah","UT","Wasatch Front","Salt Lake County",40.7608,-111.8910),
    ("San Angelo","Texas","TX","West Texas","Tom Green County",31.4638,-100.4370),
    ("San Antonio","Texas","TX","South Texas","Bexar County",29.4241,-98.4936),
    ("San Diego","California","CA","Southern California","San Diego County",32.7157,-117.1611),
    ("San Francisco","California","CA","Northern California","San Francisco County",37.7749,-122.4194),
    ("San Jose","California","CA","Northern California","Santa Clara County",37.3382,-121.8863),
    ("San Marcos","Texas","TX","Central Texas","Hays County",29.8833,-97.9414),
    ("Sandy Springs","Georgia","GA","Metro Atlanta","Fulton County",33.9304,-84.3733),
    ("Santa Ana","California","CA","Southern California","Orange County",33.7455,-117.8677),
    ("Santa Clarita","California","CA","Southern California","Los Angeles County",34.3917,-118.5426),
    ("Santa Rosa","California","CA","Northern California","Sonoma County",38.4404,-122.7141),
    ("Sarasota","Florida","FL","Southwest Florida","Sarasota County",27.3364,-82.5307),
    ("Savannah","Georgia","GA","Coastal Georgia","Chatham County",32.0835,-81.0998),
    ("Schertz","Texas","TX","South Texas","Guadalupe County",29.5538,-98.2631),
    ("Scottsdale","Arizona","AZ","Valley of the Sun","Maricopa County",33.4942,-111.9261),
    ("Seattle","Washington","WA","Puget Sound","King County",47.6062,-122.3321),
    ("Sherman","Texas","TX","North Texas","Grayson County",33.6357,-96.6089),
    ("Shreveport","Louisiana","LA","Northwest Louisiana","Caddo Parish",32.5252,-93.7502),
    ("Sioux Falls","South Dakota","SD","Southeast South Dakota","Minnehaha County",43.5446,-96.7311),
    ("Smyrna","Georgia","GA","Metro Atlanta","Cobb County",33.8840,-84.5144),
    ("South Bend","Indiana","IN","North Central Indiana","St Joseph County",41.6764,-86.2520),
    ("Southlake","Texas","TX","North Texas","Tarrant County",32.9440,-97.1342),
    ("Sparks","Nevada","NV","Northern Nevada","Washoe County",39.5349,-119.7527),
    ("Spokane","Washington","WA","Eastern Washington","Spokane County",47.6588,-117.4260),
    ("Spring","Texas","TX","Southeast Texas","Harris County",30.0799,-95.4172),
    ("Springfield","Illinois","IL","Central Illinois","Sangamon County",39.7817,-89.6501),
    ("Springfield","Massachusetts","MA","Western Massachusetts","Hampden County",42.1015,-72.5898),
    ("Springfield","Missouri","MO","Southwest Missouri","Greene County",37.2090,-93.2923),
    ("St Louis","Missouri","MO","Eastern Missouri","St Louis City",38.6270,-90.1994),
    ("St Paul","Minnesota","MN","Twin Cities","Ramsey County",44.9537,-93.0900),
    ("St Petersburg","Florida","FL","Tampa Bay","Pinellas County",27.7676,-82.6403),
    ("Stamford","Connecticut","CT","Southwest Connecticut","Fairfield County",41.0534,-73.5387),
    ("Sterling Heights","Michigan","MI","Southeast Michigan","Macomb County",42.5803,-83.0302),
    ("Stockton","California","CA","Central California","San Joaquin County",37.9577,-121.2908),
    ("Sugar Land","Texas","TX","Southeast Texas","Fort Bend County",29.6196,-95.6349),
    ("Sunnyvale","California","CA","Northern California","Santa Clara County",37.3688,-122.0363),
    ("Surprise","Arizona","AZ","Valley of the Sun","Maricopa County",33.6292,-112.3679),
    ("Syracuse","New York","NY","Central New York","Onondaga County",43.0481,-76.1474),
    ("Tacoma","Washington","WA","Puget Sound","Pierce County",47.2529,-122.4443),
    ("Tallahassee","Florida","FL","North Florida","Leon County",30.4383,-84.2807),
    ("Tampa","Florida","FL","Tampa Bay","Hillsborough County",27.9506,-82.4572),
    ("Tempe","Arizona","AZ","Valley of the Sun","Maricopa County",33.4255,-111.9400),
    ("Temple","Texas","TX","Central Texas","Bell County",31.0982,-97.3428),
    ("The Colony","Texas","TX","North Texas","Denton County",33.0812,-96.8883),
    ("The Woodlands","Texas","TX","Southeast Texas","Montgomery County",30.1588,-95.4853),
    ("Thornton","Colorado","CO","Front Range","Adams County",39.8680,-104.9719),
    ("Thousand Oaks","California","CA","Southern California","Ventura County",34.1706,-118.8376),
    ("Toledo","Ohio","OH","Northwest Ohio","Lucas County",41.6639,-83.5552),
    ("Topeka","Kansas","KS","Northeast Kansas","Shawnee County",39.0558,-95.6890),
    ("Torrance","California","CA","Southern California","Los Angeles County",33.8358,-118.3406),
    ("Tucson","Arizona","AZ","Southern Arizona","Pima County",32.2226,-110.9747),
    ("Tulsa","Oklahoma","OK","Northeast Oklahoma","Tulsa County",36.1540,-95.9928),
    ("Tyler","Texas","TX","East Texas","Smith County",32.3513,-95.3011),
    ("Utica","New York","NY","Mohawk Valley","Oneida County",43.1009,-75.2327),
    ("Valdosta","Georgia","GA","South Georgia","Lowndes County",30.8327,-83.2785),
    ("Vancouver","Washington","WA","Southwest Washington","Clark County",45.6387,-122.6615),
    ("Virginia Beach","Virginia","VA","Hampton Roads","Virginia Beach City",36.8529,-75.9780),
    ("Waco","Texas","TX","Central Texas","McLennan County",31.5493,-97.1467),
    ("Warren","Michigan","MI","Southeast Michigan","Macomb County",42.4775,-83.0277),
    ("Washington","District of Columbia","DC","Mid-Atlantic","District of Columbia",38.9072,-77.0369),
    ("Waukegan","Illinois","IL","Northeast Illinois","Lake County",42.3636,-87.8448),
    ("Waxahachie","Texas","TX","North Texas","Ellis County",32.3868,-96.8489),
    ("Weatherford","Texas","TX","North Texas","Parker County",32.7596,-97.7975),
    ("West Jordan","Utah","UT","Wasatch Front","Salt Lake County",40.6097,-111.9391),
    ("West Palm Beach","Florida","FL","Southeast Florida","Palm Beach County",26.7153,-80.0534),
    ("West Valley City","Utah","UT","Wasatch Front","Salt Lake County",40.6916,-111.9391),
    ("Westminster","Colorado","CO","Front Range","Adams County",39.8367,-105.0372),
    ("Wichita","Kansas","KS","South Central Kansas","Sedgwick County",37.6872,-97.3301),
    ("Wichita Falls","Texas","TX","North Texas","Wichita County",33.9137,-98.4934),
    ("Wilmington","North Carolina","NC","Cape Fear","New Hanover County",34.2257,-77.9447),
    ("Winston-Salem","North Carolina","NC","Piedmont Triad","Forsyth County",36.0999,-80.2442),
    ("Woodbury","Minnesota","MN","Twin Cities","Washington County",44.9239,-92.9594),
    ("Worcester","Massachusetts","MA","Central Massachusetts","Worcester County",42.2626,-71.8023),
    ("Wylie","Texas","TX","North Texas","Collin County",33.0151,-96.5388),
    ("Yonkers","New York","NY","New York Metro","Westchester County",40.9312,-73.8988),
    ("Youngstown","Ohio","OH","Northeast Ohio","Mahoning County",41.0998,-80.6495),
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

def make_slug(city, abbr):
    slug = city.lower().replace(' ','-').replace("'","").replace('.','').replace(',','')
    return f"{slug}-{abbr.lower()}"

def get_state_slug(state):
    return state.lower().replace(' ','-')

# ============================================================
# PAGE BUILDERS — one per brand
# ============================================================

def build_aivoice_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    b = BRANDS["aivoice"]
    slug = make_slug(city, abbr)
    url = f"https://{b['domain']}/{folder_slug}/{slug}.html"
    info = get_state_info(abbr)
    return f'''




{folder_name} in {city}, {state} | {b["name"]}









{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"Professional {folder_name.lower()} for businesses in {city}, {state}. AI answers every call 24/7.","offers":{{"@type":"Offer","price":"297","priceCurrency":"USD","priceSpecification":{{"@type":"UnitPriceSpecification","price":"297","priceCurrency":"USD","unitText":"month"}}}}}}


{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://{b['domain']}"}},{{"@type":"ListItem","position":2,"name":"{folder_name}","item":"https://{b['domain']}/{folder_slug}"}},{{"@type":"ListItem","position":3,"name":"{city}, {state}","item":"{url}"}}]}}


{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"How does {folder_name.lower()} work for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Our AI answers every call to your {city} business in a natural voice, qualifies the lead, books appointments, and takes messages — 24 hours a day, 7 days a week, starting at $297/month."}}}},{{"@type":"Question","name":"How quickly can my {city} business get set up?","acceptedAnswer":{{"@type":"Answer","text":"Most {city} businesses are live with their AI receptionist within 48 hours. Call 903-636-7511 or visit AIVoiceAgentPros.com to get started."}}}}]}}


*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0A0A14;color:#F9FAFB;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
nav{{background:rgba(10,10,20,.95);border-bottom:1px solid #1F1F35;padding:0 20px;position:sticky;top:0;z-index:100}}
.nav-inner{{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:62px}}
.logo{{font-weight:800;font-size:.95rem}}
.logo span{{color:#A78BFA}}
.nav-cta{{background:#7C3AED;color:#fff;font-weight:700;padding:9px 20px;border-radius:7px;font-size:.88rem}}
.hero{{background:linear-gradient(160deg,#0A0A14,#0f0a1e 50%,#0A0A14);padding:60px 20px 50px;text-align:center}}
.breadcrumb{{font-size:.78rem;color:#6B7280;margin-bottom:16px}}
.breadcrumb a{{color:#A78BFA}}
.eyebrow{{display:inline-block;background:rgba(124,58,237,.12);border:1px solid rgba(124,58,237,.25);color:#A78BFA;font-size:.77rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:18px}}
h1{{font-size:clamp(1.7rem,4.5vw,2.9rem);font-weight:900;line-height:1.1;margin-bottom:14px}}
h1 span{{color:#A78BFA}}
.sub{{color:#9CA3AF;max-width:580px;margin:0 auto 28px;font-size:1rem}}
.btns{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
.btn-p{{background:#7C3AED;color:#fff;font-weight:800;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.btn-o{{border:1px solid #1F1F35;color:#F9FAFB;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.section{{max-width:1100px;margin:0 auto;padding:56px 20px}}
.grid-3{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:32px}}
.card{{background:#111120;border:1px solid #1F1F35;border-radius:14px;padding:24px}}
.card-icon{{font-size:1.8rem;margin-bottom:12px}}
.card h3{{font-size:1rem;font-weight:700;margin-bottom:8px}}
.card p{{color:#9CA3AF;font-size:.88rem;line-height:1.6}}
.local-box{{background:#111120;border:1px solid #1F1F35;border-radius:14px;padding:28px;margin-top:40px}}
.local-box h2{{font-size:1.3rem;font-weight:800;margin-bottom:12px}}
.local-box h2 span{{color:#A78BFA}}
.local-box p{{color:#9CA3AF;font-size:.9rem;line-height:1.8;margin-bottom:10px}}
.cta-box{{background:linear-gradient(135deg,rgba(124,58,237,.12),rgba(124,58,237,.04));border:1px solid rgba(124,58,237,.2);border-radius:14px;padding:40px;text-align:center;margin-top:40px}}
.cta-box h2{{font-size:1.5rem;font-weight:800;margin-bottom:10px}}
.cta-box p{{color:#9CA3AF;margin-bottom:20px;font-size:.9rem}}
.cta-btn{{display:inline-block;background:#7C3AED;color:#fff;font-weight:800;padding:14px 30px;border-radius:9px;font-size:.95rem}}
footer{{background:#111120;border-top:1px solid #1F1F35;padding:32px 20px;text-align:center;color:#6B7280;font-size:.82rem}}
footer a{{color:#6B7280}}
footer a:hover{{color:#A78BFA}}




  
    🤖 AI Voice Agent Pros
    Get Started
  


  Home → {folder_name} → {city}, {state}
  🤖 {folder_name}
  {info['emoji']} {folder_name} in {city}, {state}
  AI that answers every call for {city} businesses 24 hours a day, 7 days a week. Qualify leads, book appointments, never miss a customer again.
  
    Get Started — {b['starting_price']} →
    📞 Call 903-636-7511
  


  Why {city} Businesses Need {folder_name}
  Every missed call in {city} is a customer going to your competitor. Our AI receptionist answers every call instantly, day or night, and handles the conversation so you can focus on your work.
  
    📞Never Miss a CallYour {city} AI receptionist picks up every call — after hours, weekends, holidays, when you're on the job. Every lead captured.
    📅Books AppointmentsAI qualifies the lead and books directly to your calendar. Your {city} customers get instant scheduling — you get confirmed appointments.
    💬Natural ConversationNot a phone tree. Not hold music. A real AI conversation that represents your {city} business professionally every single time.
    ⚡Live in 48 HoursYour {city} AI receptionist can be answering calls within 48 hours of signup. No tech skills needed — we handle everything.
    💰From {b['starting_price']}Less than a part-time employee for a fraction of the cost. No long contracts, no setup fees. Cancel any time.
    📊Every Call LoggedFull transcript and recording of every call. Know exactly what your {city} customers are asking about and never lose a lead.
  
  
    Serving {city}, {state} Businesses
    {city} is a thriving community in {region}, located in {county}. Local businesses in {city} face the same challenge as businesses everywhere — calls come in at the worst possible times. When you're on a job, in a meeting, or it's 10 PM on a Sunday, your AI receptionist is still there answering professionally and capturing every lead.
    Contractors, HVAC companies, plumbers, electricians, law firms, medical offices, restaurants, auto shops — any {city} business that gets phone calls can benefit from AI Voice Agent Pros. Stop losing customers to voicemail and start converting more calls into appointments.
    📍 {info['emoji']} Fun fact: {info['fact']}.
  
  
    Ready to Never Miss a Call in {city}?
    Get your AI receptionist live in 48 hours. Starting at {b['starting_price']} — no long contracts.
    Get Started Today →
    Or call us: 903-636-7511 · AIVoiceAgentPros.com
  


  © 2025 AI Voice Agent Pros · Part of the Dominion Brand Family
  Home · Web Design · Review Pro · AI Agency


'''


def build_reviewpro_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    b = BRANDS["reviewpro"]
    slug = make_slug(city, abbr)
    url = f"https://{b['domain']}/{folder_slug}/{slug}.html"
    info = get_state_info(abbr)
    return f'''




{folder_name} in {city}, {state} | {b["name"]}







{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"{folder_name} for businesses in {city}, {state}. Automated Google review generation starting at $197/month."}}


{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"How does {folder_name.lower()} work for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"After every job, our system automatically sends your {city} customer a review request via SMS or email. One tap takes them straight to your Google review page. Most {city} clients double their review count within 60 days."}}}},{{"@type":"Question","name":"How much does review management cost for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Dominion Review Pro starts at $197/month for {city} businesses. Setup takes less than 24 hours. Call 903-636-7511 or visit DominionReviewPro.com."}}}}]}}


*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0A0F0A;color:#F9FAFB;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
nav{{background:rgba(10,15,10,.95);border-bottom:1px solid #1A3A1A;padding:0 20px;position:sticky;top:0;z-index:100}}
.nav-inner{{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:62px}}
.logo{{font-weight:800;font-size:.95rem}}
.logo span{{color:#34D399}}
.nav-cta{{background:#059669;color:#fff;font-weight:700;padding:9px 20px;border-radius:7px;font-size:.88rem}}
.hero{{background:linear-gradient(160deg,#0A0F0A,#0F1A0F 50%,#0A0F0A);padding:60px 20px 50px;text-align:center}}
.breadcrumb{{font-size:.78rem;color:#6B7280;margin-bottom:16px}}
.breadcrumb a{{color:#34D399}}
.eyebrow{{display:inline-block;background:rgba(5,150,105,.12);border:1px solid rgba(5,150,105,.25);color:#34D399;font-size:.77rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:18px}}
h1{{font-size:clamp(1.7rem,4.5vw,2.9rem);font-weight:900;line-height:1.1;margin-bottom:14px}}
h1 span{{color:#34D399}}
.sub{{color:#9CA3AF;max-width:580px;margin:0 auto 28px;font-size:1rem}}
.btns{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
.btn-p{{background:#059669;color:#fff;font-weight:800;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.btn-o{{border:1px solid #1A3A1A;color:#F9FAFB;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.section{{max-width:1100px;margin:0 auto;padding:56px 20px}}
.grid-3{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:32px}}
.card{{background:#0F1A0F;border:1px solid #1A3A1A;border-radius:14px;padding:24px}}
.card-icon{{font-size:1.8rem;margin-bottom:12px}}
.card h3{{font-size:1rem;font-weight:700;margin-bottom:8px}}
.card p{{color:#9CA3AF;font-size:.88rem;line-height:1.6}}
.stars{{color:#F5A623;font-size:1.2rem;margin-bottom:8px}}
.local-box{{background:#0F1A0F;border:1px solid #1A3A1A;border-radius:14px;padding:28px;margin-top:40px}}
.local-box h2{{font-size:1.3rem;font-weight:800;margin-bottom:12px}}
.local-box h2 span{{color:#34D399}}
.local-box p{{color:#9CA3AF;font-size:.9rem;line-height:1.8;margin-bottom:10px}}
.cta-box{{background:linear-gradient(135deg,rgba(5,150,105,.12),rgba(5,150,105,.04));border:1px solid rgba(5,150,105,.2);border-radius:14px;padding:40px;text-align:center;margin-top:40px}}
.cta-box h2{{font-size:1.5rem;font-weight:800;margin-bottom:10px}}
.cta-box p{{color:#9CA3AF;margin-bottom:20px;font-size:.9rem}}
.cta-btn{{display:inline-block;background:#059669;color:#fff;font-weight:800;padding:14px 30px;border-radius:9px;font-size:.95rem}}
footer{{background:#0F1A0F;border-top:1px solid #1A3A1A;padding:32px 20px;text-align:center;color:#6B7280;font-size:.82rem}}
footer a{{color:#6B7280}}
footer a:hover{{color:#34D399}}




  
    ⭐ Dominion Review Pro
    Get Started
  


  Home → {folder_name} → {city}, {state}
  ⭐ {folder_name}
  {info['emoji']} {folder_name} in {city}, {state}
  Get more 5-star Google reviews for your {city} business — automatically. Our system follows up with every customer and guides them to leave a review in one tap.
  
    Start Getting Reviews — {b['starting_price']} →
    📞 Call 903-636-7511
  


  Why {city} Businesses Need More Google Reviews
  When someone in {city} searches for your type of business, the first thing they see is the star rating. More reviews means more trust, higher Google ranking, and more customers choosing you over your competition.
  
    ★★★★★Automated RequestsAfter every job, our system automatically sends your {city} customer a review request. No awkward asks. No manual follow-up. Just results.
    📱One-Tap ReviewCustomers get a link that takes them straight to your Google review page. One tap and they're writing a review for your {city} business.
    📈Double in 60 DaysMost {city} clients double their Google review count within the first 60 days. More reviews means higher ranking in {city} local search results.
    🚨Negative Review AlertsGet notified immediately if a {city} customer is unhappy — before they post publicly. Address issues fast and protect your reputation.
    💰From {b['starting_price']}Less than a single lost customer. Setup in under 24 hours. No long contracts. Cancel any time. Start getting reviews this week.
    🗺️Google Maps RankingMore reviews directly improves your Google Maps ranking in {city}. Show up higher when local customers search for your services.
  
  
    Serving {city}, {state} Businesses
    {city} is a competitive market in {region}. Local customers in {county} are reading reviews before they call anyone. If your competitors have hundreds of 5-star reviews and you have a handful, you're losing business before the phone ever rings.
    Dominion Review Pro levels the playing field for {city} small businesses. Whether you run an HVAC company, a restaurant, a law firm, an auto shop, or any other local business in {city} — our automated review system gets you more 5-star reviews every single week without you lifting a finger.
    📍 {info['emoji']} Fun fact: {info['fact']}.
  
  
    Start Getting More Reviews in {city}
    Setup in under 24 hours. Starting at {b['starting_price']}. No long contracts.
    Get Started Today →
    Or call us: 903-636-7511 · DominionReviewPro.com
  


  © 2025 Dominion Review Pro · Part of the Dominion Brand Family
  Home · Web Design · AI Voice · AI Agency


'''


def build_aiagency_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    b = BRANDS["aiagency"]
    slug = make_slug(city, abbr)
    url = f"https://{b['domain']}/{folder_slug}/{slug}.html"
    info = get_state_info(abbr)
    return f'''




{folder_name} in {city}, {state} | {b["name"]}







{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"{folder_name} for businesses in {city}, {state}. Full AI automation starting at $497/month."}}


{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"What does an {folder_name.lower()} do for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Dominion AI Agency provides full AI automation for {city} businesses — AI voice agents, CRM automation, lead generation, review management, and more. Starting at $497/month."}}}},{{"@type":"Question","name":"How do I get started with AI automation in {city}?","acceptedAnswer":{{"@type":"Answer","text":"Call 903-636-7511 or visit DominionAIAgency.com to get a free consultation for your {city} business. Most clients are up and running within one week."}}}}]}}


*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0A1628;color:#F5F0E8;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
nav{{background:rgba(10,22,40,.98);border-bottom:1px solid #1E3050;padding:0 20px;position:sticky;top:0;z-index:100}}
.nav-inner{{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:62px}}
.logo{{font-weight:800;font-size:.95rem}}
.logo span{{color:#E8C97A}}
.nav-cta{{background:linear-gradient(135deg,#C9A84C,#A8832A);color:#0A1628;font-weight:700;padding:9px 20px;border-radius:7px;font-size:.88rem}}
.hero{{background:linear-gradient(160deg,#0A1628,#0F1E35 50%,#0A1628);padding:60px 20px 50px;text-align:center}}
.breadcrumb{{font-size:.78rem;color:#8B9AB0;margin-bottom:16px}}
.breadcrumb a{{color:#E8C97A}}
.eyebrow{{display:inline-block;background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.25);color:#E8C97A;font-size:.77rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:18px}}
h1{{font-size:clamp(1.7rem,4.5vw,2.9rem);font-weight:900;line-height:1.1;margin-bottom:14px}}
h1 span{{color:#E8C97A}}
.sub{{color:#8B9AB0;max-width:580px;margin:0 auto 28px;font-size:1rem}}
.btns{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
.btn-p{{background:linear-gradient(135deg,#C9A84C,#A8832A);color:#0A1628;font-weight:800;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.btn-o{{border:1px solid #1E3050;color:#F5F0E8;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.section{{max-width:1100px;margin:0 auto;padding:56px 20px}}
.grid-3{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:32px}}
.card{{background:#0F1E35;border:1px solid #1E3050;border-radius:14px;padding:24px}}
.card-icon{{font-size:1.8rem;margin-bottom:12px}}
.card h3{{font-size:1rem;font-weight:700;margin-bottom:8px}}
.card p{{color:#8B9AB0;font-size:.88rem;line-height:1.6}}
.local-box{{background:#0F1E35;border:1px solid #1E3050;border-radius:14px;padding:28px;margin-top:40px}}
.local-box h2{{font-size:1.3rem;font-weight:800;margin-bottom:12px}}
.local-box h2 span{{color:#E8C97A}}
.local-box p{{color:#8B9AB0;font-size:.9rem;line-height:1.8;margin-bottom:10px}}
.cta-box{{background:linear-gradient(135deg,rgba(201,168,76,.1),rgba(201,168,76,.03));border:1px solid rgba(201,168,76,.2);border-radius:14px;padding:40px;text-align:center;margin-top:40px}}
.cta-box h2{{font-size:1.5rem;font-weight:800;margin-bottom:10px}}
.cta-box p{{color:#8B9AB0;margin-bottom:20px;font-size:.9rem}}
.cta-btn{{display:inline-block;background:linear-gradient(135deg,#C9A84C,#A8832A);color:#0A1628;font-weight:800;padding:14px 30px;border-radius:9px;font-size:.95rem}}
footer{{background:#0F1E35;border-top:1px solid #1E3050;padding:32px 20px;text-align:center;color:#8B9AB0;font-size:.82rem}}
footer a{{color:#8B9AB0}}
footer a:hover{{color:#E8C97A}}




  
    👑 Dominion AI Agency
    Get Started
  


  Home → {folder_name} → {city}, {state}
  👑 {folder_name}
  {info['emoji']} {folder_name} in {city}, {state}
  Full AI automation for {city} businesses. Voice agents, CRM, lead generation, and reputation management — all under one roof starting at {b['starting_price']}.
  
    Get Started — {b['starting_price']} →
    📞 Call 903-636-7511
  


  Full AI Automation for {city} Businesses
  Dominion AI Agency brings enterprise-level AI automation to {city} small businesses. Instead of hiring staff for every role, our AI handles your calls, CRM, lead generation, and reviews — automatically, around the clock.
  
    📞AI Voice AgentsAI receptionist answers every call to your {city} business 24/7. Qualifies leads, books appointments, takes messages. Never miss a customer.
    🤖CRM AutomationYour CRM runs itself. Contacts auto-created, pipeline stages auto-updated, follow-up sequences auto-triggered. No manual data entry.
    🎯Lead GenerationAutomated lead scraping, outreach, and follow-up for {city} area prospects. New leads flowing into your pipeline every day on autopilot.
    ⭐Review ManagementAutomated Google review requests after every job. Most {city} clients double their review count in 60 days.
    💰From {b['starting_price']}Everything your {city} business needs to run on AI — for less than the cost of a single part-time employee. No long contracts.
    ⚡Up and Running FastMost {city} businesses are fully onboarded within one week. We handle all the setup — you just run your business.
  
  
    Serving {city}, {state} Businesses
    {city} is a growing community in {region}, {state}. Local businesses in {county} are increasingly competing with larger companies that have full marketing and sales teams. Dominion AI Agency gives {city} small businesses access to the same AI tools that big companies use — at a fraction of the cost.
    Whether you're a contractor, a service business, a restaurant, or a professional office in {city}, our AI automation stack handles your customer communication, follow-up, and reputation management so you can focus on delivering great work.
    📍 {info['emoji']} Fun fact: {info['fact']}.
  
  
    Ready to Automate Your {city} Business?
    Free consultation. Up and running in one week. Starting at {b['starting_price']}.
    Get Started Today →
    Or call us: 903-636-7511 · DominionAIAgency.com
  


  © 2025 Dominion AI Agency · Part of the Dominion Brand Family
  Home · Web Design · AI Voice · Review Pro


'''


def build_webdesign_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    b = BRANDS["webdesign"]
    slug = make_slug(city, abbr)
    url = f"https://{b['domain']}/{folder_slug}/{slug}.html"
    info = get_state_info(abbr)
    return f'''




{folder_name} in {city}, {state} | {b["name"]}







{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"Professional {folder_name.lower()} for businesses in {city}, {state}. Custom websites from $497 — we build it first, you pay when you love it."}}


{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"How much does {folder_name.lower()} cost in {city}?","acceptedAnswer":{{"@type":"Answer","text":"Dominion Web Design Pro builds professional websites for {city} businesses starting at $497. We build your demo site first — you only pay when you love it. Call 903-636-7511 or visit DominionWebDesignPro.com."}}}},{{"@type":"Question","name":"Do you build websites for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Yes! We serve businesses in {city}, {state} and all across the US. Every site includes SEO optimization, mobile design, and an AI chat widget. Get your free demo today."}}}}]}}


*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0A0A18;color:#F9FAFB;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
nav{{background:rgba(10,10,24,.98);border-bottom:1px solid #1E1E40;padding:0 20px;position:sticky;top:0;z-index:100}}
.nav-inner{{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:62px}}
.logo{{font-weight:800;font-size:.95rem}}
.logo span{{color:#60A5FA}}
.nav-cta{{background:#1D4ED8;color:#fff;font-weight:700;padding:9px 20px;border-radius:7px;font-size:.88rem}}
.hero{{background:linear-gradient(160deg,#0A0A18,#0F0F22 50%,#0A0A18);padding:60px 20px 50px;text-align:center}}
.breadcrumb{{font-size:.78rem;color:#6B7280;margin-bottom:16px}}
.breadcrumb a{{color:#60A5FA}}
.eyebrow{{display:inline-block;background:rgba(29,78,216,.12);border:1px solid rgba(29,78,216,.25);color:#60A5FA;font-size:.77rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:18px}}
h1{{font-size:clamp(1.7rem,4.5vw,2.9rem);font-weight:900;line-height:1.1;margin-bottom:14px}}
h1 span{{color:#60A5FA}}
.sub{{color:#9CA3AF;max-width:580px;margin:0 auto 28px;font-size:1rem}}
.btns{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
.btn-p{{background:#1D4ED8;color:#fff;font-weight:800;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.btn-o{{border:1px solid #1E1E40;color:#F9FAFB;padding:14px 28px;border-radius:9px;font-size:.95rem}}
.section{{max-width:1100px;margin:0 auto;padding:56px 20px}}
.grid-3{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:32px}}
.card{{background:#0F0F22;border:1px solid #1E1E40;border-radius:14px;padding:24px}}
.card-icon{{font-size:1.8rem;margin-bottom:12px}}
.card h3{{font-size:1rem;font-weight:700;margin-bottom:8px}}
.card p{{color:#9CA3AF;font-size:.88rem;line-height:1.6}}
.local-box{{background:#0F0F22;border:1px solid #1E1E40;border-radius:14px;padding:28px;margin-top:40px}}
.local-box h2{{font-size:1.3rem;font-weight:800;margin-bottom:12px}}
.local-box h2 span{{color:#60A5FA}}
.local-box p{{color:#9CA3AF;font-size:.9rem;line-height:1.8;margin-bottom:10px}}
.cta-box{{background:linear-gradient(135deg,rgba(29,78,216,.12),rgba(29,78,216,.04));border:1px solid rgba(29,78,216,.2);border-radius:14px;padding:40px;text-align:center;margin-top:40px}}
.cta-box h2{{font-size:1.5rem;font-weight:800;margin-bottom:10px}}
.cta-box p{{color:#9CA3AF;margin-bottom:20px;font-size:.9rem}}
.cta-btn{{display:inline-block;background:#1D4ED8;color:#fff;font-weight:800;padding:14px 30px;border-radius:9px;font-size:.95rem}}
footer{{background:#0F0F22;border-top:1px solid #1E1E40;padding:32px 20px;text-align:center;color:#6B7280;font-size:.82rem}}
footer a{{color:#6B7280}}
footer a:hover{{color:#60A5FA}}




  
    🌐 Dominion Web Design Pro
    Get Free Demo
  


  Home → {folder_name} → {city}, {state}
  🌐 {folder_name}
  {info['emoji']} {folder_name} in {city}, {state}
  We build your {city} business website first — you only pay when you love it. SEO ready, mobile first, AI chat included. Starting at {b['starting_price']}.
  
    Get Your Free Demo →
    📞 Call 903-636-7511
  


  Professional {folder_name} for {city} Businesses
  Your website is your most important marketing tool. {city} customers are searching for your services online right now. If your site looks outdated, loads slowly, or isn't mobile friendly — they're going to your competitor.
  
    🎨Built First, Pay LaterWe build your complete {city} business website before you pay a single dollar. No risk, no guessing. Love it or we keep working until you do.
    📱Mobile First DesignOver 70% of your {city} customers are on mobile. Every site we build looks and works perfectly on phones, tablets, and desktop.
    🔍SEO OptimizedBuilt from the ground up to rank in {city} local search. Schema markup, fast load times, proper meta tags — everything Google loves.
    🤖AI Chat IncludedEvery website includes an AI chat widget that answers questions and captures leads from your {city} visitors — even when you're busy.
    💰From {b['starting_price']}Professional website for less than most people spend on one month of ads. No monthly fees on base package. You own it outright.
    ⚡Fast TurnaroundMost {city} business sites are ready for your review within 5-7 days. We move fast so you can start getting online leads quickly.
  
  
    Serving {city}, {state} Businesses
    {city} is a thriving community in {region}, {state}. Businesses in {county} need a strong online presence to compete in today's market. Whether you're a contractor, restaurant, law firm, medical office, or any other local business in {city} — your website is the foundation of all your marketing.
    Dominion Web Design Pro has built websites for businesses across Texas and all 50 states. We understand what local {city} customers are looking for and we build sites that convert visitors into calls and appointments.
    📍 {info['emoji']} Fun fact: {info['fact']}.
  
  
    Get Your Free {city} Website Demo
    We build it first. You pay only when you love it. Starting at {b['starting_price']}.
    Get Your Free Demo →
    Or call us: 903-636-7511 · DominionWebDesignPro.com
  


  © 2025 Dominion Web Design Pro · Part of the Dominion Brand Family
  Home · AI Voice · Review Pro · AI Agency


'''
def _phone_digits(brand):
    return brand.get("phone_display", brand.get("phone", ""))


def build_leadpro_page(brand_key, city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    county = county.replace(' County', '').strip()
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
            + ' serves ' + city + ' and all of ' + county + ' County. Free quotes, fast scheduling, work starting at '
            + brand["starting_price"] + '.')
    canonical = base + '/' + folder_slug + '/' + slug + '.html'

    city_intro = (city + ' sits in ' + county + ' County, ' + state + ', in the ' + region + ' region. '
        + 'Homes and businesses here deal with the same weather everyone in ' + state + ' deals with — heat, humidity, '
        + 'storms, and the wear that comes with all of it. That is exactly the kind of thing ' + folder_name.lower()
        + ' is meant to handle. ' + brand["name"] + ' works with property owners across ' + city + ' and the surrounding '
        + county + ' County area, from single-family homes to commercial buildings and rental properties. '
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

    html += '<header><a class="logo" href="' + base + '/">' + brand["favicon"] + ' ' + brand["name"] + '</a><nav>'
    for fs, fn in brand["service_folders"][:5]:
        html += '<a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + '</a>'
    html += '<a href="' + tel + '">' + phone + '</a></nav></header>'

    html += '<div class="hero"><h1>' + folder_name + ' in ' + city + ', ' + state + '</h1>'
    html += '<p>' + brand["pitch"] + ' Serving ' + city + ' and all of ' + county + ' County. Work starting at ' + brand["starting_price"] + '.</p>'
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
        html += '<p>' + fn + ' for homes and businesses across ' + county + ' County.</p></div>'
    html += '</div>'

    html += '<h2>Why ' + city + ' Property Owners Call Us</h2><div class="grid">'
    html += '<div class="card"><h3>Free Quotes</h3><p>You get the price before any work starts. No surprises on the invoice.</p></div>'
    html += '<div class="card"><h3>Local Crews</h3><p>We work ' + city + ' and the surrounding ' + county + ' County area regularly.</p></div>'
    html += '<div class="card"><h3>Fast Scheduling</h3><p>Most ' + city + ' jobs get on the calendar within the same week.</p></div>'
    html += '<div class="card"><h3>Insured Work</h3><p>Fully insured, so your property is covered while we are on it.</p></div>'
    html += '</div>'

    html += '<div class="callout"><strong>Need ' + folder_name.lower() + ' in ' + city + '?</strong><br>'
    html += 'Call <a href="' + tel + '">' + phone + '</a> for a free quote today.</div>'
    html += '</div>'

    html += '<footer>&copy; 2026 ' + brand["name"] + ' &middot; Serving ' + city + ', ' + county + ' County, ' + state
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
    county = county.replace(' County', '').strip()
    slug = make_slug(city, abbr)
    state_info = get_state_info(abbr)
    title = folder_name + ' in ' + city + ', ' + state + ' | Dominion Solar Pro'
    desc = 'Shop the best ' + folder_name.lower() + ' near ' + city + ', ' + state + '. Jackery solar generators, portable power stations, and solar panels for camping, RV, home backup, and off-grid living. Free shipping.'
    city_intro = city + ' is a community in ' + county + ' County, ' + state + ', situated in the heart of ' + region + '. Like much of ' + state + ', ' + city + ' experiences a wide range of weather — from intense summer heat to severe storms that can knock out power for hours or even days. That makes reliable portable power not just a convenience but a necessity for ' + city + ' residents, campers, RV travelers, and off-grid homesteaders across ' + region + '. Whether you are spending a weekend at one of ' + region + 's many outdoor destinations, living the van life across ' + state + ', running a remote job site in ' + county + ' County, or simply want peace of mind when the next storm rolls through — a Jackery solar generator gives you clean, quiet, zero-emission power wherever you are. No fuel, no fumes, no noise. Just sunlight turning into electricity, ready when you need it most in ' + city + ' and across ' + state + '.'
    html = '<html lang="en"><head>'
    html += '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    html += '<title>' + title + '</title>'
    html += '<meta name="description" content="' + desc + '">'
    html += '<link rel="canonical" href="https://dominionsolarpro.com/cities/' + folder_slug + '/' + slug + '.html">'
    html += '<style>body{font-family:sans-serif;margin:0;background:#f8fafc;color:#1a2332}header{background:#1a2332;color:#fff;padding:16px 24px;display:flex;align-items:center;gap:12px}header h1{font-size:1.2em;margin:0}.hero{background:linear-gradient(135deg,#1a2332,#2d4a6e);color:#fff;padding:48px 24px;text-align:center}.hero h2{font-size:2em;margin-bottom:12px;color:#f59e0b}.hero p{max-width:640px;margin:0 auto 24px;opacity:0.85;line-height:1.7}.btn{background:#f59e0b;color:#1a2332;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:1em;display:inline-block}.section{padding:48px 24px;max-width:900px;margin:0 auto}.section h3{color:#1a2332;font-size:1.4em;border-bottom:3px solid #f59e0b;padding-bottom:8px;margin-bottom:20px}.city-intro{background:#fff;border-left:4px solid #f59e0b;padding:24px;border-radius:4px;margin-bottom:32px;line-height:1.8;color:#334155}.kw-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:32px}.kw-card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;border-left:4px solid #f59e0b}.kw-card h4{margin:0 0 6px;color:#1a2332;font-size:0.95em}.kw-card p{margin:0;font-size:0.82em;color:#64748b;line-height:1.5}footer{background:#1a2332;color:rgba(255,255,255,0.6);padding:24px;text-align:center;font-size:0.82em}</style>'
    html += '</head><body>'
    html += '<header><span style="font-size:1.8em">☀️</span><h1>Dominion Solar Pro | ' + folder_name + ' in ' + city + ', ' + state + '</h1></header>'
    html += '<div class="hero"><h2>Best ' + folder_name + ' near ' + city + ', ' + state + '</h2>'
    html += '<p>Jackery solar generators, portable power stations, and solar panels — perfect for ' + city + ' residents, campers, RV travelers, and off-grid homesteaders across ' + region + '. Free shipping nationwide.</p>'
    html += '<a href="https://www.jackery.com?aff=1363" class="btn" target="_blank">Shop Solar Generators on Jackery.com →</a></div>'
    html += '<div class="section"><h3>Solar Power in ' + city + ', ' + state + '</h3>'
    html += '<div class="city-intro">' + city_intro + '</div>'
    html += '<h3>' + folder_name + ' — Popular Searches near ' + city + '</h3>'
    html += '<div class="kw-grid">'
    html += '<div class="kw-card"><h4>Solar Generator ' + city + '</h4><p>Complete kits — power station plus solar panels bundled for ' + city + ' residents.</p></div>'
    html += '<div class="kw-card"><h4>Portable Power Station ' + city + '</h4><p>Standalone power stations — charge from wall, car, or solar panel anywhere in ' + county + ' County.</p></div>'
    html += '<div class="kw-card"><h4>Jackery ' + city + ' ' + state + '</h4><p>Official Jackery products — the #1 portable solar brand trusted by millions worldwide.</p></div>'
    html += '<div class="kw-card"><h4>Solar Generator for Camping ' + city + '</h4><p>Lightweight solar power for weekend camping and outdoor adventures in ' + region + '.</p></div>'
    html += '<div class="kw-card"><h4>Home Backup Solar ' + city + '</h4><p>Keep your fridge, lights, and devices running during ' + state + ' power outages.</p></div>'
    html += '<div class="kw-card"><h4>RV Solar Generator ' + city + '</h4><p>Full RV power without hookups — go anywhere across ' + state + ' off-grid.</p></div>'
    html += '<div class="kw-card"><h4>Off Grid Solar ' + county + ' County</h4><p>Remote cabins, homesteads, and job sites — power anywhere in ' + county + ' County.</p></div>'
    html += '<div class="kw-card"><h4>Emergency Power ' + city + '</h4><p>Storm and severe weather backup — keep your family safe when the grid goes down in ' + region + '.</p></div>'
    html += '<div class="kw-card"><h4>Solar Panels ' + city + '</h4><p>Foldable, lightweight solar panels that charge any Jackery station from the sun.</p></div>'
    html += '<div class="kw-card"><h4>Best Solar Generator ' + state + '</h4><p>Top-rated solar generators for ' + state + ' — camping, RV, home backup, and off-grid.</p></div>'
    html += '</div>'
    html += '<p style="text-align:center;margin-top:32px"><a href="https://www.jackery.com?aff=1363" class="btn" target="_blank">Shop All Jackery Solar Products →</a></p>'
    html += '<p style="text-align:center;margin-top:16px;font-size:0.8em;color:#94a3b8">Affiliate Disclosure: Dominion Solar Pro is a Jackery authorized affiliate. We may earn a commission on purchases at no extra cost to you.</p>'
    html += '</div>'
    html += '<footer>© 2026 Dominion Solar Pro | Serving ' + city + ', ' + county + ' County, ' + state + ' and all of ' + region + ' | ' + state_info["emoji"] + ' ' + state_info["fact"] + '</footer>'
    html += '</body></html>'
    return html

def build_hardmoney_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    brand = BRANDS["hardmoney"]
    county = county.replace(" County", "").strip()
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

    intro = (city + " sits in " + county + " County, " + state + ". Investors working this market run into the same wall "
        "everyone else does — a conventional lender wants two years of returns, a full appraisal cycle, and thirty to "
        "forty-five days before anyone sees a dollar. Distressed deals do not wait that long. "
        "Dominion Hard Money lends against the asset instead of the borrower's tax returns, which is why a "
        + city + " deal can close in days. We fund purchases, rehabs, and refinances across " + state
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
        "@media(max-width:560px){.hero h1{font-size:1.5em}.btn-o{margin:10px 0 0;display:block}}")

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

    html += '<header><a class="logo" href="' + base + '/">' + brand["favicon"] + ' Dominion Hard Money</a><nav>'
    for fs, fn in brand["service_folders"][:5]:
        html += '<a href="' + base + '/' + fs + '/' + slug + '.html">' + fn + '</a>'
    html += '<a href="' + tel + '">' + phone + '</a></nav></header>'

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
        html += '<p>' + fn + ' for investors across ' + county + ' County and ' + state + '.</p></div>'
    html += '</div>'

    html += '<h2>What Investors Use This For</h2><div class="grid">'
    html += '<div class="card"><h3>Auction and foreclosure buys</h3><p>Deals with a closing clock a bank cannot meet.</p></div>'
    html += '<div class="card"><h3>Rehab and resale</h3><p>Purchase plus renovation on one loan, repaid at sale.</p></div>'
    html += '<div class="card"><h3>Rental refinance</h3><p>DSCR loans qualified on the property income, not tax returns.</p></div>'
    html += '<div class="card"><h3>Bridge financing</h3><p>Short-term capital while a longer-term loan is arranged.</p></div>'
    html += '</div>'

    html += '<div class="callout"><strong>Working a deal in ' + city + '?</strong><br>'
    html += 'Call <a href="' + tel + '">' + phone + '</a> and we will tell you in one conversation whether it is fundable.</div>'
    html += '<p style="font-size:.78em;color:#6b6455;margin-top:26px;font-family:system-ui,sans-serif">'
    html += 'Dominion Hard Money arranges private and asset-based real estate financing for business purposes only. '
    html += 'Not a commitment to lend. All loans subject to underwriting, property review, and approval. '
    html += 'Terms vary by property, borrower experience, and exit strategy.</p>'
    html += '</div>'

    html += '<footer>&copy; 2026 Dominion Hard Money &middot; Serving ' + city + ', ' + county + ' County, ' + state
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
]


def cities_for_brand(brand_key):
    """Cities this brand is allowed to build. Metro brands are limited to their radius."""
    brand = BRANDS[brand_key]
    c = brand.get("metro_center")
    if not c:
        return list(ALL_US_CITIES)
    rad = brand.get("metro_radius", 60)
    pool, seen, out = list(ALL_US_CITIES) + list(METRO_EXTRA_CITIES), set(), []
    for cd in pool:
        key = make_slug(cd[0], cd[2])
        if key in seen:
            continue
        if _miles(c[0], c[1], cd[5], cd[6]) <= rad:
            seen.add(key); out.append(cd)
    return out


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


def get_existing_slugs(brand_key):
    brand = BRANDS[brand_key]
    existing = set()
    first_folder = brand["service_folders"][0][0]
    pattern = os.path.join(brand["work_dir"], first_folder, "*.html")
    for f in glob.glob(pattern):
        existing.add(os.path.basename(f).replace('.html',''))
    return existing

def write_redirects(brand_key):
    """Netlify _redirects for URL structures we have retired."""
    brand = BRANDS[brand_key]
    if brand_key != "hardmoney":
        return
    lines = ["# retired /texas/ prefix — national site now", ""]
    for folder_slug, _ in brand["service_folders"]:
        lines.append(f"/texas/{folder_slug}/*  /{folder_slug}/:splat  301")
    lines.append("/texas/*  /  301")
    with open(os.path.join(brand["work_dir"], "_redirects"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  wrote _redirects for {brand['name']}")


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
    with open(os.path.join(brand["work_dir"], "sitemap.xml"), 'w', encoding='utf-8') as f:
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
    result = subprocess.run(['git','commit','-m',f'Daily build {today}: +{count_built} cities ({total} total) — {brand["name"]}'], capture_output=True, text=True)
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
    if os.environ.get('PURGE') == '1':
        purge_stale_folders(brand_key)
        purge_out_of_area(brand_key)
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
            print(f"  {brand['name']}: nothing to regenerate")
            return 0
    else:
        if not unbuilt:
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
    for brand_key in BRANDS:
        print(f"\n▶ Building {BRANDS[brand_key]['name']}...")
        count = build_brand(brand_key)
        total_built += count
    print(f"\n{'='*60}")
    print(f"TOTAL PAGES BUILT TODAY: {total_built * 20} ({total_built} cities × 20 folders × 4 brands)")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
