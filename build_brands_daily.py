#!/usr/bin/env python3
"""
Dominion Brand City Builder — Daily Auto-Builder
Runs daily on Render at 6 AM UTC
Builds 50 new city pages across ALL 4 brand sites simultaneously
Each city gets pages in all service folders for maximum SEO coverage
Pushes each brand to its own GitHub repo → Netlify auto-deploys
"""

import os, json, glob, subprocess
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
GITHUB_TOKEN = "GITHUB_TOKEN_HERE"
CITIES_PER_DAY = 100
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
        "work_dir": "/opt/render/project/src/dominion-hard-money",
        "domain": "dominionhardmoney.com",
        "name": "Dominion Hard Money",
        "tagline": "Private Money for Real Estate Investors",
        "cta": "Apply Now",
        "phone": "nine zero three, six three six, seven five one one",
        "colors": {"primary": "#0a1628", "accent": "#c9a84c", "text": "#ffffff", "bg": "#f8f6f0"},
        "starting_price": "$50,000",
        "pitch": "Fast private money loans for fix and flip, DSCR rental, and bridge financing.",
        "favicon": "💰",
        "service_folders": [
            ("texas/hard-money-loans", "Hard Money Loans"),
            ("texas/fix-and-flip-loans", "Fix and Flip Loans"),
            ("texas/bridge-loans", "Bridge Loans"),
            ("texas/dscr-loans", "DSCR Rental Loans"),
            ("texas/private-money-lender", "Private Money Lender"),
            ("texas/rehab-loans", "Rehab Loans"),
            ("texas/real-estate-investor-loans", "Real Estate Investor Loans"),
            ("texas/hard-money-lender", "Hard Money Lender"),
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
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{folder_name} in {city}, {state} | {b["name"]}</title>
<meta name="description" content="Professional {folder_name.lower()} for {city}, {state} businesses. AI that answers every call 24/7, qualifies leads, and books appointments. Starting at {b["starting_price"]}.">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:title" content="{folder_name} in {city}, {state} | {b['name']}">
<meta property="og:description" content="Never miss another call in {city}. AI receptionist answers 24/7 from {b['starting_price']}.">
<meta name="geo.region" content="US-{abbr}">
<meta name="geo.placename" content="{city}, {state}">
<meta name="geo.position" content="{lat};{lng}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"Professional {folder_name.lower()} for businesses in {city}, {state}. AI answers every call 24/7.","offers":{{"@type":"Offer","price":"297","priceCurrency":"USD","priceSpecification":{{"@type":"UnitPriceSpecification","price":"297","priceCurrency":"USD","unitText":"month"}}}}}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://{b['domain']}"}},{{"@type":"ListItem","position":2,"name":"{folder_name}","item":"https://{b['domain']}/{folder_slug}"}},{{"@type":"ListItem","position":3,"name":"{city}, {state}","item":"{url}"}}]}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"How does {folder_name.lower()} work for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Our AI answers every call to your {city} business in a natural voice, qualifies the lead, books appointments, and takes messages — 24 hours a day, 7 days a week, starting at $297/month."}}}},{{"@type":"Question","name":"How quickly can my {city} business get set up?","acceptedAnswer":{{"@type":"Answer","text":"Most {city} businesses are live with their AI receptionist within 48 hours. Call 903-636-7511 or visit AIVoiceAgentPros.com to get started."}}}}]}}
</script>
<style>
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
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/index.html"><span class="logo">🤖 <span>AI Voice Agent Pros</span></span></a>
    <a href="/index.html#pricing" class="nav-cta">Get Started</a>
  </div>
</nav>
<div class="hero">
  <div class="breadcrumb"><a href="/index.html">Home</a> → <a href="/{folder_slug}">{folder_name}</a> → {city}, {state}</div>
  <div class="eyebrow">🤖 {folder_name}</div>
  <h1>{info['emoji']} {folder_name} in <span>{city}, {state}</span></h1>
  <p class="sub">AI that answers every call for {city} businesses 24 hours a day, 7 days a week. Qualify leads, book appointments, never miss a customer again.</p>
  <div class="btns">
    <a href="/index.html#pricing" class="btn-p">Get Started — {b['starting_price']} →</a>
    <a href="tel:+19036367511" class="btn-o">📞 Call 903-636-7511</a>
  </div>
</div>
<div class="section">
  <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:8px">Why {city} Businesses Need {folder_name}</h2>
  <p style="color:#9CA3AF;font-size:.92rem;max-width:680px">Every missed call in {city} is a customer going to your competitor. Our AI receptionist answers every call instantly, day or night, and handles the conversation so you can focus on your work.</p>
  <div class="grid-3">
    <div class="card"><div class="card-icon">📞</div><h3>Never Miss a Call</h3><p>Your {city} AI receptionist picks up every call — after hours, weekends, holidays, when you're on the job. Every lead captured.</p></div>
    <div class="card"><div class="card-icon">📅</div><h3>Books Appointments</h3><p>AI qualifies the lead and books directly to your calendar. Your {city} customers get instant scheduling — you get confirmed appointments.</p></div>
    <div class="card"><div class="card-icon">💬</div><h3>Natural Conversation</h3><p>Not a phone tree. Not hold music. A real AI conversation that represents your {city} business professionally every single time.</p></div>
    <div class="card"><div class="card-icon">⚡</div><h3>Live in 48 Hours</h3><p>Your {city} AI receptionist can be answering calls within 48 hours of signup. No tech skills needed — we handle everything.</p></div>
    <div class="card"><div class="card-icon">💰</div><h3>From {b['starting_price']}</h3><p>Less than a part-time employee for a fraction of the cost. No long contracts, no setup fees. Cancel any time.</p></div>
    <div class="card"><div class="card-icon">📊</div><h3>Every Call Logged</h3><p>Full transcript and recording of every call. Know exactly what your {city} customers are asking about and never lose a lead.</p></div>
  </div>
  <div class="local-box">
    <h2>Serving <span>{city}, {state}</span> Businesses</h2>
    <p>{city} is a thriving community in {region}, located in {county}. Local businesses in {city} face the same challenge as businesses everywhere — calls come in at the worst possible times. When you're on a job, in a meeting, or it's 10 PM on a Sunday, your AI receptionist is still there answering professionally and capturing every lead.</p>
    <p>Contractors, HVAC companies, plumbers, electricians, law firms, medical offices, restaurants, auto shops — any {city} business that gets phone calls can benefit from AI Voice Agent Pros. Stop losing customers to voicemail and start converting more calls into appointments.</p>
    <p style="font-size:.85rem;color:#6B7280">📍 {info['emoji']} Fun fact: {info['fact']}.</p>
  </div>
  <div class="cta-box">
    <h2>Ready to Never Miss a Call in {city}?</h2>
    <p>Get your AI receptionist live in 48 hours. Starting at {b['starting_price']} — no long contracts.</p>
    <a href="/index.html#pricing" class="cta-btn">Get Started Today →</a>
    <p style="margin-top:14px;font-size:.82rem;color:#6B7280">Or call us: <a href="tel:+19036367511" style="color:#A78BFA">903-636-7511</a> · <a href="https://aivoiceagentpros.com" style="color:#A78BFA">AIVoiceAgentPros.com</a></p>
  </div>
</div>
<footer>
  <p style="margin-bottom:8px">© 2025 AI Voice Agent Pros · Part of the <a href="https://dominionaiagency.com">Dominion Brand Family</a></p>
  <p><a href="/index.html">Home</a> · <a href="https://dominionwebdesignpro.com">Web Design</a> · <a href="https://dominionreviewpro.com">Review Pro</a> · <a href="https://dominionaiagency.com">AI Agency</a></p>
</footer>
</body>
</html>'''


def build_reviewpro_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    b = BRANDS["reviewpro"]
    slug = make_slug(city, abbr)
    url = f"https://{b['domain']}/{folder_slug}/{slug}.html"
    info = get_state_info(abbr)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{folder_name} in {city}, {state} | {b["name"]}</title>
<meta name="description" content="{folder_name} for {city}, {state} businesses. Get more 5-star Google reviews automatically. Most clients double their reviews in 60 days. Starting at {b['starting_price']}.">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="geo.region" content="US-{abbr}">
<meta name="geo.placename" content="{city}, {state}">
<meta name="geo.position" content="{lat};{lng}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"{folder_name} for businesses in {city}, {state}. Automated Google review generation starting at $197/month."}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"How does {folder_name.lower()} work for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"After every job, our system automatically sends your {city} customer a review request via SMS or email. One tap takes them straight to your Google review page. Most {city} clients double their review count within 60 days."}}}},{{"@type":"Question","name":"How much does review management cost for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Dominion Review Pro starts at $197/month for {city} businesses. Setup takes less than 24 hours. Call 903-636-7511 or visit DominionReviewPro.com."}}}}]}}
</script>
<style>
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
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/index.html"><span class="logo">⭐ <span>Dominion Review Pro</span></span></a>
    <a href="/index.html#pricing" class="nav-cta">Get Started</a>
  </div>
</nav>
<div class="hero">
  <div class="breadcrumb"><a href="/index.html">Home</a> → <a href="/{folder_slug}">{folder_name}</a> → {city}, {state}</div>
  <div class="eyebrow">⭐ {folder_name}</div>
  <h1>{info['emoji']} {folder_name} in <span>{city}, {state}</span></h1>
  <p class="sub">Get more 5-star Google reviews for your {city} business — automatically. Our system follows up with every customer and guides them to leave a review in one tap.</p>
  <div class="btns">
    <a href="/index.html#pricing" class="btn-p">Start Getting Reviews — {b['starting_price']} →</a>
    <a href="tel:+19036367511" class="btn-o">📞 Call 903-636-7511</a>
  </div>
</div>
<div class="section">
  <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:8px">Why {city} Businesses Need More Google Reviews</h2>
  <p style="color:#9CA3AF;font-size:.92rem;max-width:680px">When someone in {city} searches for your type of business, the first thing they see is the star rating. More reviews means more trust, higher Google ranking, and more customers choosing you over your competition.</p>
  <div class="grid-3">
    <div class="card"><div class="stars">★★★★★</div><h3>Automated Requests</h3><p>After every job, our system automatically sends your {city} customer a review request. No awkward asks. No manual follow-up. Just results.</p></div>
    <div class="card"><div class="card-icon">📱</div><h3>One-Tap Review</h3><p>Customers get a link that takes them straight to your Google review page. One tap and they're writing a review for your {city} business.</p></div>
    <div class="card"><div class="card-icon">📈</div><h3>Double in 60 Days</h3><p>Most {city} clients double their Google review count within the first 60 days. More reviews means higher ranking in {city} local search results.</p></div>
    <div class="card"><div class="card-icon">🚨</div><h3>Negative Review Alerts</h3><p>Get notified immediately if a {city} customer is unhappy — before they post publicly. Address issues fast and protect your reputation.</p></div>
    <div class="card"><div class="card-icon">💰</div><h3>From {b['starting_price']}</h3><p>Less than a single lost customer. Setup in under 24 hours. No long contracts. Cancel any time. Start getting reviews this week.</p></div>
    <div class="card"><div class="card-icon">🗺️</div><h3>Google Maps Ranking</h3><p>More reviews directly improves your Google Maps ranking in {city}. Show up higher when local customers search for your services.</p></div>
  </div>
  <div class="local-box">
    <h2>Serving <span>{city}, {state}</span> Businesses</h2>
    <p>{city} is a competitive market in {region}. Local customers in {county} are reading reviews before they call anyone. If your competitors have hundreds of 5-star reviews and you have a handful, you're losing business before the phone ever rings.</p>
    <p>Dominion Review Pro levels the playing field for {city} small businesses. Whether you run an HVAC company, a restaurant, a law firm, an auto shop, or any other local business in {city} — our automated review system gets you more 5-star reviews every single week without you lifting a finger.</p>
    <p style="font-size:.85rem;color:#6B7280">📍 {info['emoji']} Fun fact: {info['fact']}.</p>
  </div>
  <div class="cta-box">
    <h2>Start Getting More Reviews in {city}</h2>
    <p>Setup in under 24 hours. Starting at {b['starting_price']}. No long contracts.</p>
    <a href="/index.html#pricing" class="cta-btn">Get Started Today →</a>
    <p style="margin-top:14px;font-size:.82rem;color:#6B7280">Or call us: <a href="tel:+19036367511" style="color:#34D399">903-636-7511</a> · <a href="https://dominionreviewpro.com" style="color:#34D399">DominionReviewPro.com</a></p>
  </div>
</div>
<footer>
  <p style="margin-bottom:8px">© 2025 Dominion Review Pro · Part of the <a href="https://dominionaiagency.com">Dominion Brand Family</a></p>
  <p><a href="/index.html">Home</a> · <a href="https://dominionwebdesignpro.com">Web Design</a> · <a href="https://aivoiceagentpros.com">AI Voice</a> · <a href="https://dominionaiagency.com">AI Agency</a></p>
</footer>
</body>
</html>'''


def build_aiagency_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    b = BRANDS["aiagency"]
    slug = make_slug(city, abbr)
    url = f"https://{b['domain']}/{folder_slug}/{slug}.html"
    info = get_state_info(abbr)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{folder_name} in {city}, {state} | {b["name"]}</title>
<meta name="description" content="{folder_name} for {city}, {state} businesses. Full AI automation — voice agents, CRM, lead generation, and reputation management. Starting at {b['starting_price']}.">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="geo.region" content="US-{abbr}">
<meta name="geo.placename" content="{city}, {state}">
<meta name="geo.position" content="{lat};{lng}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"{folder_name} for businesses in {city}, {state}. Full AI automation starting at $497/month."}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"What does an {folder_name.lower()} do for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Dominion AI Agency provides full AI automation for {city} businesses — AI voice agents, CRM automation, lead generation, review management, and more. Starting at $497/month."}}}},{{"@type":"Question","name":"How do I get started with AI automation in {city}?","acceptedAnswer":{{"@type":"Answer","text":"Call 903-636-7511 or visit DominionAIAgency.com to get a free consultation for your {city} business. Most clients are up and running within one week."}}}}]}}
</script>
<style>
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
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/index.html"><span class="logo">👑 <span>Dominion AI Agency</span></span></a>
    <a href="/index.html#pricing" class="nav-cta">Get Started</a>
  </div>
</nav>
<div class="hero">
  <div class="breadcrumb"><a href="/index.html">Home</a> → <a href="/{folder_slug}">{folder_name}</a> → {city}, {state}</div>
  <div class="eyebrow">👑 {folder_name}</div>
  <h1>{info['emoji']} {folder_name} in <span>{city}, {state}</span></h1>
  <p class="sub">Full AI automation for {city} businesses. Voice agents, CRM, lead generation, and reputation management — all under one roof starting at {b['starting_price']}.</p>
  <div class="btns">
    <a href="/index.html#pricing" class="btn-p">Get Started — {b['starting_price']} →</a>
    <a href="tel:+19036367511" class="btn-o">📞 Call 903-636-7511</a>
  </div>
</div>
<div class="section">
  <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:8px">Full AI Automation for {city} Businesses</h2>
  <p style="color:#8B9AB0;font-size:.92rem;max-width:680px">Dominion AI Agency brings enterprise-level AI automation to {city} small businesses. Instead of hiring staff for every role, our AI handles your calls, CRM, lead generation, and reviews — automatically, around the clock.</p>
  <div class="grid-3">
    <div class="card"><div class="card-icon">📞</div><h3>AI Voice Agents</h3><p>AI receptionist answers every call to your {city} business 24/7. Qualifies leads, books appointments, takes messages. Never miss a customer.</p></div>
    <div class="card"><div class="card-icon">🤖</div><h3>CRM Automation</h3><p>Your CRM runs itself. Contacts auto-created, pipeline stages auto-updated, follow-up sequences auto-triggered. No manual data entry.</p></div>
    <div class="card"><div class="card-icon">🎯</div><h3>Lead Generation</h3><p>Automated lead scraping, outreach, and follow-up for {city} area prospects. New leads flowing into your pipeline every day on autopilot.</p></div>
    <div class="card"><div class="card-icon">⭐</div><h3>Review Management</h3><p>Automated Google review requests after every job. Most {city} clients double their review count in 60 days.</p></div>
    <div class="card"><div class="card-icon">💰</div><h3>From {b['starting_price']}</h3><p>Everything your {city} business needs to run on AI — for less than the cost of a single part-time employee. No long contracts.</p></div>
    <div class="card"><div class="card-icon">⚡</div><h3>Up and Running Fast</h3><p>Most {city} businesses are fully onboarded within one week. We handle all the setup — you just run your business.</p></div>
  </div>
  <div class="local-box">
    <h2>Serving <span>{city}, {state}</span> Businesses</h2>
    <p>{city} is a growing community in {region}, {state}. Local businesses in {county} are increasingly competing with larger companies that have full marketing and sales teams. Dominion AI Agency gives {city} small businesses access to the same AI tools that big companies use — at a fraction of the cost.</p>
    <p>Whether you're a contractor, a service business, a restaurant, or a professional office in {city}, our AI automation stack handles your customer communication, follow-up, and reputation management so you can focus on delivering great work.</p>
    <p style="font-size:.85rem;color:#8B9AB0">📍 {info['emoji']} Fun fact: {info['fact']}.</p>
  </div>
  <div class="cta-box">
    <h2>Ready to Automate Your {city} Business?</h2>
    <p>Free consultation. Up and running in one week. Starting at {b['starting_price']}.</p>
    <a href="/index.html#pricing" class="cta-btn">Get Started Today →</a>
    <p style="margin-top:14px;font-size:.82rem;color:#8B9AB0">Or call us: <a href="tel:+19036367511" style="color:#E8C97A">903-636-7511</a> · <a href="https://dominionaiagency.com" style="color:#E8C97A">DominionAIAgency.com</a></p>
  </div>
</div>
<footer>
  <p style="margin-bottom:8px">© 2025 Dominion AI Agency · Part of the <a href="https://dominionaiagency.com">Dominion Brand Family</a></p>
  <p><a href="/index.html">Home</a> · <a href="https://dominionwebdesignpro.com">Web Design</a> · <a href="https://aivoiceagentpros.com">AI Voice</a> · <a href="https://dominionreviewpro.com">Review Pro</a></p>
</footer>
</body>
</html>'''


def build_webdesign_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    b = BRANDS["webdesign"]
    slug = make_slug(city, abbr)
    url = f"https://{b['domain']}/{folder_slug}/{slug}.html"
    info = get_state_info(abbr)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{folder_name} in {city}, {state} | {b["name"]}</title>
<meta name="description" content="Professional {folder_name.lower()} for {city}, {state} businesses. We build your site first — you only pay when you love it. SEO ready, mobile first, AI chat included. From {b['starting_price']}.">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="geo.region" content="US-{abbr}">
<meta name="geo.placename" content="{city}, {state}">
<meta name="geo.position" content="{lat};{lng}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Service","name":"{folder_name} in {city}, {state}","provider":{{"@type":"LocalBusiness","name":"{b['name']}","url":"https://{b['domain']}","telephone":"{b['phone']}","areaServed":{{"@type":"City","name":"{city}","containedInPlace":{{"@type":"State","name":"{state}"}}}}}},"description":"Professional {folder_name.lower()} for businesses in {city}, {state}. Custom websites from $497 — we build it first, you pay when you love it."}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"How much does {folder_name.lower()} cost in {city}?","acceptedAnswer":{{"@type":"Answer","text":"Dominion Web Design Pro builds professional websites for {city} businesses starting at $497. We build your demo site first — you only pay when you love it. Call 903-636-7511 or visit DominionWebDesignPro.com."}}}},{{"@type":"Question","name":"Do you build websites for {city} businesses?","acceptedAnswer":{{"@type":"Answer","text":"Yes! We serve businesses in {city}, {state} and all across the US. Every site includes SEO optimization, mobile design, and an AI chat widget. Get your free demo today."}}}}]}}
</script>
<style>
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
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/index.html"><span class="logo">🌐 <span>Dominion Web Design Pro</span></span></a>
    <a href="/index.html#pricing" class="nav-cta">Get Free Demo</a>
  </div>
</nav>
<div class="hero">
  <div class="breadcrumb"><a href="/index.html">Home</a> → <a href="/{folder_slug}">{folder_name}</a> → {city}, {state}</div>
  <div class="eyebrow">🌐 {folder_name}</div>
  <h1>{info['emoji']} {folder_name} in <span>{city}, {state}</span></h1>
  <p class="sub">We build your {city} business website first — you only pay when you love it. SEO ready, mobile first, AI chat included. Starting at {b['starting_price']}.</p>
  <div class="btns">
    <a href="/index.html#pricing" class="btn-p">Get Your Free Demo →</a>
    <a href="tel:+19036367511" class="btn-o">📞 Call 903-636-7511</a>
  </div>
</div>
<div class="section">
  <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:8px">Professional {folder_name} for {city} Businesses</h2>
  <p style="color:#9CA3AF;font-size:.92rem;max-width:680px">Your website is your most important marketing tool. {city} customers are searching for your services online right now. If your site looks outdated, loads slowly, or isn't mobile friendly — they're going to your competitor.</p>
  <div class="grid-3">
    <div class="card"><div class="card-icon">🎨</div><h3>Built First, Pay Later</h3><p>We build your complete {city} business website before you pay a single dollar. No risk, no guessing. Love it or we keep working until you do.</p></div>
    <div class="card"><div class="card-icon">📱</div><h3>Mobile First Design</h3><p>Over 70% of your {city} customers are on mobile. Every site we build looks and works perfectly on phones, tablets, and desktop.</p></div>
    <div class="card"><div class="card-icon">🔍</div><h3>SEO Optimized</h3><p>Built from the ground up to rank in {city} local search. Schema markup, fast load times, proper meta tags — everything Google loves.</p></div>
    <div class="card"><div class="card-icon">🤖</div><h3>AI Chat Included</h3><p>Every website includes an AI chat widget that answers questions and captures leads from your {city} visitors — even when you're busy.</p></div>
    <div class="card"><div class="card-icon">💰</div><h3>From {b['starting_price']}</h3><p>Professional website for less than most people spend on one month of ads. No monthly fees on base package. You own it outright.</p></div>
    <div class="card"><div class="card-icon">⚡</div><h3>Fast Turnaround</h3><p>Most {city} business sites are ready for your review within 5-7 days. We move fast so you can start getting online leads quickly.</p></div>
  </div>
  <div class="local-box">
    <h2>Serving <span>{city}, {state}</span> Businesses</h2>
    <p>{city} is a thriving community in {region}, {state}. Businesses in {county} need a strong online presence to compete in today's market. Whether you're a contractor, restaurant, law firm, medical office, or any other local business in {city} — your website is the foundation of all your marketing.</p>
    <p>Dominion Web Design Pro has built websites for businesses across Texas and all 50 states. We understand what local {city} customers are looking for and we build sites that convert visitors into calls and appointments.</p>
    <p style="font-size:.85rem;color:#6B7280">📍 {info['emoji']} Fun fact: {info['fact']}.</p>
  </div>
  <div class="cta-box">
    <h2>Get Your Free {city} Website Demo</h2>
    <p>We build it first. You pay only when you love it. Starting at {b['starting_price']}.</p>
    <a href="/index.html#pricing" class="cta-btn">Get Your Free Demo →</a>
    <p style="margin-top:14px;font-size:.82rem;color:#6B7280">Or call us: <a href="tel:+19036367511" style="color:#60A5FA">903-636-7511</a> · <a href="https://dominionwebdesignpro.com" style="color:#60A5FA">DominionWebDesignPro.com</a></p>
  </div>
</div>
<footer>
  <p style="margin-bottom:8px">© 2025 Dominion Web Design Pro · Part of the <a href="https://dominionaiagency.com">Dominion Brand Family</a></p>
  <p><a href="/index.html">Home</a> · <a href="https://aivoiceagentpros.com">AI Voice</a> · <a href="https://dominionreviewpro.com">Review Pro</a> · <a href="https://dominionaiagency.com">AI Agency</a></p>
</footer>
</body>
</html>'''
def build_hardmoney_page(city, state, abbr, region, county, lat, lng, folder_slug, folder_name):
    slug = make_slug(city, abbr)
    state_info = get_state_info(abbr)
    title = folder_name + ' in ' + city + ', ' + state + ' | Dominion Hard Money'
    desc = 'Need a ' + folder_name.lower() + ' in ' + city + ', ' + state + '? Dominion Hard Money funds fix and flip, DSCR rental, and bridge loans fast. Apply today.'
    html = '<!DOCTYPE html>'
    html += '<html lang=en><head>'
    html += '<meta charset=UTF-8>'
    html += '<title>' + title + '</title>'
    html += '<meta name=description content=' + desc + '>'
    html += '</head><body>'
    html += '<h1>' + folder_name + ' in ' + city + ', ' + state + '</h1>'
    html += '<p>' + desc + '</p>'
    html += '<p>Call us: 903-636-8811</p>'
    html += '<p>Serving ' + city + ', ' + county + ' County, ' + state + '</p>'
    html += '<p>' + state_info['emoji'] + ' ' + state_info['fact'] + '</p>'
    html += '</body></html>'
    return html

PAGE_BUILDERS = {
    "aivoice": build_aivoice_page,
    "reviewpro": build_reviewpro_page,
    "aiagency": build_aiagency_page,
    "webdesign": build_webdesign_page,
    "hardmoney": build_hardmoney_page,
}

# ============================================================
# BUILD + PUSH LOGIC
# ============================================================

def get_existing_slugs(brand_key):
    brand = BRANDS[brand_key]
    existing = set()
    first_folder = brand["service_folders"][0][0]
    pattern = os.path.join(brand["work_dir"], first_folder, "*.html")
    for f in glob.glob(pattern):
        existing.add(os.path.basename(f).replace('.html',''))
    return existing

def update_sitemap(brand_key):
    brand = BRANDS[brand_key]
    base = f"https://{brand['domain']}"
    pages = [f"{base}/", f"{base}/index.html", f"{base}/service-areas.html"]
    for folder_slug, _ in brand["service_folders"]:
        for f in sorted(glob.glob(os.path.join(brand["work_dir"], folder_slug, "*.html"))):
            pages.append(f"{base}/{folder_slug}/{os.path.basename(f)}")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        priority = '1.0' if p.endswith('/') or p.endswith('index.html') else '0.8'
        xml += f'<url><loc>{p}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>\n'
    xml += '</urlset>'
    with open(os.path.join(brand["work_dir"], "sitemap.xml"), 'w') as f:
        f.write(xml)
    return len(pages)

def git_push(brand_key, count_built, total):
    brand = BRANDS[brand_key]
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{brand['repo']}.git"
    os.chdir(brand["work_dir"])
    today = datetime.now().strftime('%Y-%m-%d')
    subprocess.run(['git','config','user.email','build@dominion.com'])
    subprocess.run(['git','config','user.name','Dominion Builder'])
    subprocess.run(['git','add','-A'])
    result = subprocess.run(['git','commit','-m',f'Daily build {today}: +{count_built} cities ({total} total) — {brand["name"]}'], capture_output=True, text=True)
    if 'nothing to commit' in result.stdout:
        print(f"  {brand['name']}: nothing new")
        return
    subprocess.run(['git','push', repo_url,'main'])
    print(f"  ✅ {brand['name']}: +{count_built} cities pushed ({total} total)")

def build_brand(brand_key):
    brand = BRANDS[brand_key]
    builder = PAGE_BUILDERS[brand_key]
    existing = get_existing_slugs(brand_key)
    seen = set()
    unbuilt = []
    for city_data in ALL_US_CITIES:
        city, state, abbr, region, county, lat, lng = city_data
        slug = make_slug(city, abbr)
        if slug not in existing and slug not in seen:
            seen.add(slug)
            unbuilt.append(city_data)
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
    total = len(existing) + built
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
