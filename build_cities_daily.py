#!/usr/bin/env python3
"""
Dominion Local Business Directory — Daily City Builder
Runs daily on Render, builds 50 new city pages, pushes to GitHub
Goal: Cover every city and town in America
"""

import os, json, time, subprocess, random, glob, requests
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
GITHUB_TOKEN = "GITHUB_TOKEN_HERE"
GITHUB_REPO = "dominionsoundmusic-create/dominionlocalbusinessdirectory-site"
REPO_URL = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
CITIES_PER_DAY = 100
WORK_DIR = "/opt/render/project/src"
STATE_FILE = "/opt/render/project/src/build_state.json"

# ============================================================
# COMPLETE US CITY DATABASE WITH GEO COORDINATES
# Format: (city, state, abbr, region, county, tier, lat, lng)
# ============================================================

ALL_US_CITIES = [
    # TEXAS small towns not yet built
    ("Joaquin","Texas","TX","East Texas","Shelby County","tiny",31.9657,-94.0416),
    ("Tenaha","Texas","TX","East Texas","Shelby County","tiny",31.9468,-94.2413),
    ("Timpson","Texas","TX","East Texas","Shelby County","tiny",31.9043,-94.3963),
    ("Gun Barrel City","Texas","TX","East Texas","Henderson County","small",32.3229,-96.1302),
    ("Seagoville","Texas","TX","North Texas","Dallas County","small",32.6507,-96.5527),
    ("Sachse","Texas","TX","North Texas","Dallas County","small",32.9746,-96.5833),
    ("Sunnyvale","Texas","TX","North Texas","Dallas County","tiny",32.7960,-96.5552),
    ("Fate","Texas","TX","North Texas","Rockwall County","tiny",32.9404,-96.3808),
    ("Heath","Texas","TX","North Texas","Rockwall County","tiny",32.8357,-96.4680),
    ("Caddo Mills","Texas","TX","Northeast Texas","Hunt County","tiny",33.0632,-96.2263),
    ("Commerce","Texas","TX","Northeast Texas","Hunt County","small",33.2457,-95.8980),
    ("Emory","Texas","TX","Northeast Texas","Rains County","tiny",32.8749,-95.6763),
    ("Pittsburg","Texas","TX","East Texas","Camp County","small",32.9957,-94.9630),
    ("Big Sandy","Texas","TX","East Texas","Upshur County","tiny",32.5813,-95.1077),
    ("Port Neches","Texas","TX","Southeast Texas","Jefferson County","small",29.9763,-93.9596),
    ("Bridge City","Texas","TX","Southeast Texas","Orange County","small",30.0271,-93.8480),
    ("Groves","Texas","TX","Southeast Texas","Jefferson County","small",29.9463,-93.9113),
    ("Nederland","Texas","TX","Southeast Texas","Jefferson County","small",29.9763,-93.9941),
    ("Huntington","Texas","TX","East Texas","Angelina County","tiny",31.2768,-94.5760),
    ("Corrigan","Texas","TX","East Texas","Polk County","tiny",30.9985,-94.8269),
    ("Coldspring","Texas","TX","East Texas","San Jacinto County","tiny",30.5927,-95.1327),
    ("Kirbyville","Texas","TX","Deep East Texas","Jasper County","tiny",30.6596,-93.8966),
    ("Burkeville","Texas","TX","Deep East Texas","Newton County","tiny",31.0032,-93.6596),
    ("Atlanta","Texas","TX","East Texas","Cass County","small",33.1137,-94.1641),
    ("Greenville","Texas","TX","Northeast Texas","Hunt County","mid",33.1376,-96.1105),
    ("Clute","Texas","TX","Southeast Texas","Brazoria County","small",29.0196,-95.3977),
    ("Freeport","Texas","TX","Southeast Texas","Brazoria County","small",28.9530,-95.3596),
    ("Richwood","Texas","TX","Southeast Texas","Brazoria County","tiny",29.0641,-95.3869),
    ("Lake Jackson","Texas","TX","Southeast Texas","Brazoria County","mid",29.0338,-95.4347),
    ("Sweeny","Texas","TX","Southeast Texas","Brazoria County","tiny",29.0363,-95.6966),
    ("Brazoria","Texas","TX","Southeast Texas","Brazoria County","tiny",29.0441,-95.5683),
    ("West Columbia","Texas","TX","Southeast Texas","Brazoria County","tiny",29.1419,-95.6441),
    ("El Campo","Texas","TX","Southeast Texas","Wharton County","small",29.2030,-96.2691),
    ("Wharton","Texas","TX","Southeast Texas","Wharton County","small",29.3133,-96.1002),
    ("Edna","Texas","TX","Southeast Texas","Jackson County","small",28.9780,-96.6458),
    ("Louise","Texas","TX","Southeast Texas","Wharton County","tiny",29.1544,-96.3938),
    ("Ganado","Texas","TX","Southeast Texas","Jackson County","tiny",29.0447,-96.5108),
    ("Yoakum","Texas","TX","South Texas","DeWitt County","small",29.2955,-97.1524),
    ("Cuero","Texas","TX","South Texas","DeWitt County","small",29.0977,-97.2896),
    ("Gonzales","Texas","TX","South Texas","Gonzales County","small",29.5038,-97.4524),
    ("Luling","Texas","TX","South Texas","Caldwell County","small",29.6802,-97.6480),
    ("Lockhart","Texas","TX","Central Texas","Caldwell County","small",29.8849,-97.6730),
    ("Flatonia","Texas","TX","South Texas","Fayette County","tiny",29.6880,-97.1010),
    ("Schulenburg","Texas","TX","South Texas","Fayette County","tiny",29.6827,-96.9063),
    ("Shiner","Texas","TX","South Texas","Lavaca County","tiny",29.4280,-97.1727),
    ("Hallettsville","Texas","TX","South Texas","Lavaca County","small",29.4463,-96.9441),
    ("Victoria","Texas","TX","South Texas","Victoria County","mid",28.8053,-97.0036),
    ("Port Lavaca","Texas","TX","Coastal Texas","Calhoun County","small",28.6155,-96.6263),
    ("Rockport","Texas","TX","Coastal Texas","Aransas County","small",28.0208,-97.0547),
    ("Aransas Pass","Texas","TX","Coastal Texas","San Patricio County","small",27.9069,-97.1502),
    ("Portland","Texas","TX","Coastal Texas","San Patricio County","small",27.8864,-97.3247),
    ("Gregory","Texas","TX","Coastal Texas","San Patricio County","tiny",27.9274,-97.2997),
    ("Sinton","Texas","TX","Coastal Texas","San Patricio County","small",28.0391,-97.5080),
    ("Alice","Texas","TX","South Texas","Jim Wells County","mid",27.7522,-98.0691),
    ("Kingsville","Texas","TX","South Texas","Kleberg County","small",27.5159,-97.8561),
    ("Robstown","Texas","TX","South Texas","Nueces County","small",27.7897,-97.6686),
    ("Beeville","Texas","TX","South Texas","Bee County","small",28.4022,-97.7480),
    ("Cuero","Texas","TX","South Texas","DeWitt County","small",29.0977,-97.2896),
    ("Seguin","Texas","TX","South Texas","Guadalupe County","mid",29.5688,-97.9644),
    ("New Braunfels","Texas","TX","South Texas","Comal County","mid",29.7030,-98.1244),
    ("San Marcos","Texas","TX","Central Texas","Hays County","mid",29.8833,-97.9414),
    ("Kyle","Texas","TX","Central Texas","Hays County","mid",29.9888,-97.8803),
    ("Buda","Texas","TX","Central Texas","Hays County","small",30.0852,-97.8403),
    ("Wimberley","Texas","TX","Central Texas","Hays County","small",29.9985,-98.0969),
    ("Dripping Springs","Texas","TX","Central Texas","Hays County","small",30.1905,-98.0869),
    ("Lakeway","Texas","TX","Central Texas","Travis County","small",30.3591,-97.9742),
    ("Marble Falls","Texas","TX","Central Texas","Burnet County","small",30.5782,-98.2733),
    ("Burnet","Texas","TX","Central Texas","Burnet County","small",30.7582,-98.2286),
    ("Llano","Texas","TX","Central Texas","Llano County","tiny",30.7513,-98.6780),
    ("Mason","Texas","TX","Central Texas","Mason County","tiny",30.7488,-99.2302),
    ("Fredericksburg","Texas","TX","Central Texas","Gillespie County","small",30.2752,-98.8727),
    ("Kerrville","Texas","TX","Central Texas","Kerr County","small",30.0474,-99.1403),
    ("Center Point","Texas","TX","Central Texas","Kerr County","tiny",29.9313,-99.0158),
    ("Ingram","Texas","TX","Central Texas","Kerr County","tiny",30.0824,-99.2408),
    ("Junction","Texas","TX","West Texas","Kimble County","tiny",30.4891,-99.7714),
    ("Sonora","Texas","TX","West Texas","Sutton County","small",30.5671,-100.6441),
    ("Del Rio","Texas","TX","West Texas","Val Verde County","small",29.3627,-100.8969),
    ("Eagle Pass","Texas","TX","West Texas","Maverick County","small",28.7091,-100.4997),
    ("Laredo","Texas","TX","South Texas","Webb County","major",27.5036,-99.5075),
    ("Zapata","Texas","TX","South Texas","Zapata County","small",26.9074,-99.2747),
    ("Rio Grande City","Texas","TX","South Texas","Starr County","small",26.3797,-98.8202),
    ("Roma","Texas","TX","South Texas","Starr County","tiny",26.4074,-99.0186),
    ("Mission","Texas","TX","South Texas","Hidalgo County","mid",26.2159,-98.3252),
    ("Pharr","Texas","TX","South Texas","Hidalgo County","mid",26.1948,-98.1836),
    ("San Juan","Texas","TX","South Texas","Hidalgo County","small",26.1894,-98.1558),
    ("Alamo","Texas","TX","South Texas","Hidalgo County","small",26.1838,-98.1219),
    ("Edinburg","Texas","TX","South Texas","Hidalgo County","mid",26.3017,-98.1633),
    ("Weslaco","Texas","TX","South Texas","Hidalgo County","mid",26.1598,-97.9911),
    ("Harlingen","Texas","TX","South Texas","Cameron County","mid",26.1906,-97.6961),
    ("San Benito","Texas","TX","South Texas","Cameron County","small",26.1322,-97.6333),
    ("Los Fresnos","Texas","TX","South Texas","Cameron County","small",26.0702,-97.4752),
    ("Port Isabel","Texas","TX","South Texas","Cameron County","small",26.0711,-97.2094),
    ("South Padre Island","Texas","TX","Coastal Texas","Cameron County","small",26.1138,-97.1677),
    ("Brownsville","Texas","TX","South Texas","Cameron County","major",25.9017,-97.4975),
    ("Donna","Texas","TX","South Texas","Hidalgo County","small",26.1697,-98.0472),
    ("Mercedes","Texas","TX","South Texas","Hidalgo County","small",26.1483,-97.9133),
    ("Lyford","Texas","TX","South Texas","Willacy County","tiny",26.4127,-97.7941),
    ("Raymondville","Texas","TX","South Texas","Willacy County","small",26.4797,-97.7833),
    ("Kingsville","Texas","TX","South Texas","Kleberg County","small",27.5159,-97.8561),
    ("Falfurrias","Texas","TX","South Texas","Brooks County","small",27.2283,-98.1452),
    ("Hebbronville","Texas","TX","South Texas","Jim Hogg County","small",27.3094,-98.6877),
    ("Carrizo Springs","Texas","TX","South Texas","Dimmit County","small",28.5225,-99.8655),
    ("Crystal City","Texas","TX","South Texas","Zavala County","small",28.6788,-99.8280),
    ("Uvalde","Texas","TX","South Texas","Uvalde County","small",29.2097,-99.7864),
    ("Hondo","Texas","TX","South Texas","Medina County","small",29.3472,-99.1419),
    ("Pearsall","Texas","TX","South Texas","Frio County","small",28.8855,-99.0975),
    ("Cotulla","Texas","TX","South Texas","La Salle County","small",28.4363,-99.2347),
    # ALABAMA
    ("Anniston","Alabama","AL","Northeast Alabama","Calhoun County","mid",33.6596,-85.8316),
    ("Gadsden","Alabama","AL","Northeast Alabama","Etowah County","mid",34.0143,-86.0066),
    ("Florence","Alabama","AL","North Alabama","Lauderdale County","mid",34.7998,-87.6773),
    ("Muscle Shoals","Alabama","AL","North Alabama","Colbert County","small",34.7443,-87.6677),
    ("Phenix City","Alabama","AL","East Alabama","Russell County","mid",32.4710,-85.0005),
    ("Prattville","Alabama","AL","Central Alabama","Autauga County","mid",32.4638,-86.4597),
    ("Vestavia Hills","Alabama","AL","North Central Alabama","Jefferson County","mid",33.4476,-86.9497),
    ("Trussville","Alabama","AL","North Central Alabama","Jefferson County","small",33.6193,-86.6083),
    ("Alabaster","Alabama","AL","North Central Alabama","Shelby County","small",33.2318,-86.8177),
    ("Pelham","Alabama","AL","North Central Alabama","Shelby County","small",33.2843,-86.8080),
    ("Selma","Alabama","AL","Central Alabama","Dallas County","mid",32.4074,-87.0211),
    ("Talladega","Alabama","AL","Central Alabama","Talladega County","small",33.4348,-86.1052),
    ("Opelika","Alabama","AL","East Alabama","Lee County","mid",32.6454,-85.3783),
    ("Enterprise","Alabama","AL","Southeast Alabama","Coffee County","small",31.3152,-85.8555),
    ("Daphne","Alabama","AL","South Alabama","Baldwin County","mid",30.6035,-87.9036),
    ("Fairhope","Alabama","AL","South Alabama","Baldwin County","mid",30.5182,-87.9033),
    ("Foley","Alabama","AL","South Alabama","Baldwin County","small",30.4071,-87.6836),
    ("Gulf Shores","Alabama","AL","South Alabama","Baldwin County","small",30.2460,-87.7006),
    ("Orange Beach","Alabama","AL","South Alabama","Baldwin County","small",30.2949,-87.5694),
    ("Albertville","Alabama","AL","Northeast Alabama","Marshall County","mid",34.2676,-86.2083),
    ("Cullman","Alabama","AL","North Alabama","Cullman County","mid",34.1748,-86.8433),
    ("Jasper","Alabama","AL","North Alabama","Walker County","mid",33.8312,-87.2783),
    ("Bessemer","Alabama","AL","North Central Alabama","Jefferson County","mid",33.4018,-86.9544),
    ("Homewood","Alabama","AL","North Central Alabama","Jefferson County","mid",33.4668,-86.8022),
    ("Northport","Alabama","AL","West Central Alabama","Tuscaloosa County","mid",33.2348,-87.5836),
    # GEORGIA
    ("Dalton","Georgia","GA","Northwest Georgia","Whitfield County","mid",34.7698,-84.9702),
    ("Rome","Georgia","GA","Northwest Georgia","Floyd County","mid",34.2570,-85.1647),
    ("Carrollton","Georgia","GA","West Georgia","Carroll County","mid",33.5799,-85.0766),
    ("Newnan","Georgia","GA","West Georgia","Coweta County","mid",33.3807,-84.7997),
    ("Peachtree City","Georgia","GA","Metro Atlanta","Fayette County","mid",33.3968,-84.5961),
    ("Woodstock","Georgia","GA","Metro Atlanta","Cherokee County","mid",34.1015,-84.5194),
    ("Canton","Georgia","GA","Metro Atlanta","Cherokee County","mid",34.2365,-84.4913),
    ("Kennesaw","Georgia","GA","Metro Atlanta","Cobb County","mid",34.0234,-84.6155),
    ("Acworth","Georgia","GA","Metro Atlanta","Cherokee County","small",34.0659,-84.6763),
    ("Douglasville","Georgia","GA","West Georgia","Douglas County","mid",33.7507,-84.7477),
    ("Statesboro","Georgia","GA","Southeast Georgia","Bulloch County","mid",32.4488,-81.7832),
    ("Hinesville","Georgia","GA","Southeast Georgia","Liberty County","mid",31.8468,-81.5957),
    ("Pooler","Georgia","GA","Coastal Georgia","Chatham County","mid",32.1157,-81.2474),
    ("Brunswick","Georgia","GA","Coastal Georgia","Glynn County","mid",31.1499,-81.4915),
    ("Valdosta","Georgia","GA","South Georgia","Lowndes County","mid",30.8327,-83.2785),
    ("Thomasville","Georgia","GA","South Georgia","Thomas County","small",30.8366,-83.9788),
    ("Tifton","Georgia","GA","South Georgia","Tift County","small",31.4505,-83.5088),
    ("Albany","Georgia","GA","Southwest Georgia","Dougherty County","mid",31.5785,-84.1557),
    ("Americus","Georgia","GA","Southwest Georgia","Sumter County","small",32.0724,-84.2330),
    ("Griffin","Georgia","GA","Middle Georgia","Spalding County","mid",33.2468,-84.2641),
    ("LaGrange","Georgia","GA","West Georgia","Troup County","mid",33.0393,-85.0316),
    # FLORIDA - additional
    ("Pensacola","Florida","FL","Northwest Florida","Escambia County","mid",30.4213,-87.2169),
    ("Panama City","Florida","FL","Northwest Florida","Bay County","mid",30.1588,-85.6602),
    ("Tallahassee","Florida","FL","North Florida","Leon County","major",30.4383,-84.2807),
    ("Gainesville","Florida","FL","North Central Florida","Alachua County","major",29.6516,-82.3248),
    ("Ocala","Florida","FL","North Central Florida","Marion County","mid",29.1872,-82.1401),
    ("The Villages","Florida","FL","North Central Florida","Sumter County","mid",28.9036,-81.9748),
    ("Ormond Beach","Florida","FL","East Central Florida","Volusia County","mid",29.2858,-81.0559),
    ("Port Orange","Florida","FL","East Central Florida","Volusia County","mid",29.1136,-81.0084),
    ("Deltona","Florida","FL","East Central Florida","Volusia County","mid",28.9005,-81.2637),
    ("New Smyrna Beach","Florida","FL","East Central Florida","Volusia County","small",29.0258,-80.9270),
    ("Edgewater","Florida","FL","East Central Florida","Volusia County","small",28.9939,-80.8881),
    ("Titusville","Florida","FL","Space Coast","Brevard County","mid",28.6122,-80.8076),
    ("Rockledge","Florida","FL","Space Coast","Brevard County","mid",28.3206,-80.7298),
    ("Merritt Island","Florida","FL","Space Coast","Brevard County","mid",28.5361,-80.6698),
    ("Kissimmee","Florida","FL","Central Florida","Osceola County","mid",28.2919,-81.4076),
    ("St Cloud","Florida","FL","Central Florida","Osceola County","mid",28.2489,-81.2812),
    ("Sanford","Florida","FL","Central Florida","Seminole County","mid",28.8006,-81.2731),
    ("Oviedo","Florida","FL","Central Florida","Seminole County","mid",28.6700,-81.2079),
    ("Winter Springs","Florida","FL","Central Florida","Seminole County","mid",28.6981,-81.2831),
    ("Altamonte Springs","Florida","FL","Central Florida","Seminole County","mid",28.6611,-81.3651),
    ("Apopka","Florida","FL","Central Florida","Orange County","mid",28.6936,-81.5323),
    ("Winter Garden","Florida","FL","Central Florida","Orange County","mid",28.5653,-81.5865),
    ("Clermont","Florida","FL","Central Florida","Lake County","mid",28.5494,-81.7729),
    ("Leesburg","Florida","FL","Central Florida","Lake County","mid",28.8108,-81.8776),
    ("Lakeland","Florida","FL","Central Florida","Polk County","major",28.0395,-81.9498),
    ("Winter Haven","Florida","FL","Central Florida","Polk County","mid",28.0222,-81.7329),
    ("Bradenton","Florida","FL","Southwest Florida","Manatee County","mid",27.4989,-82.5748),
    ("Venice","Florida","FL","Southwest Florida","Sarasota County","mid",27.0998,-82.4543),
    ("Englewood","Florida","FL","Southwest Florida","Sarasota County","small",26.9620,-82.3526),
    ("Port Charlotte","Florida","FL","Southwest Florida","Charlotte County","mid",26.9759,-82.0907),
    ("Punta Gorda","Florida","FL","Southwest Florida","Charlotte County","mid",26.9298,-82.0454),
    ("Estero","Florida","FL","Southwest Florida","Lee County","mid",26.4384,-81.8067),
    ("Marco Island","Florida","FL","Southwest Florida","Collier County","mid",25.9412,-81.7179),
    ("Immokalee","Florida","FL","Southwest Florida","Collier County","small",26.4198,-81.4179),
    ("Homestead","Florida","FL","Southeast Florida","Miami-Dade County","mid",25.4687,-80.4776),
    ("Coral Gables","Florida","FL","Southeast Florida","Miami-Dade County","mid",25.7215,-80.2684),
    ("Hialeah","Florida","FL","Southeast Florida","Miami-Dade County","major",25.8576,-80.2781),
    ("Doral","Florida","FL","Southeast Florida","Miami-Dade County","mid",25.8196,-80.3554),
    ("Miami Beach","Florida","FL","Southeast Florida","Miami-Dade County","mid",25.7907,-80.1300),
    ("North Miami","Florida","FL","Southeast Florida","Miami-Dade County","mid",25.8893,-80.1868),
    ("Aventura","Florida","FL","Southeast Florida","Miami-Dade County","mid",25.9565,-80.1392),
    ("Hallandale Beach","Florida","FL","Southeast Florida","Broward County","mid",25.9812,-80.1484),
    ("Weston","Florida","FL","Southeast Florida","Broward County","mid",26.1003,-80.3998),
    ("Plantation","Florida","FL","Southeast Florida","Broward County","mid",26.1276,-80.2331),
    ("Sunrise","Florida","FL","Southeast Florida","Broward County","mid",26.1503,-80.2998),
    ("Tamarac","Florida","FL","Southeast Florida","Broward County","mid",26.2128,-80.2498),
    ("Margate","Florida","FL","Southeast Florida","Broward County","mid",26.2445,-80.2062),
    ("Coconut Creek","Florida","FL","Southeast Florida","Broward County","mid",26.2512,-80.1784),
    ("Delray Beach","Florida","FL","Southeast Florida","Palm Beach County","mid",26.4615,-80.0728),
    ("Boynton Beach","Florida","FL","Southeast Florida","Palm Beach County","mid",26.5317,-80.0905),
    ("Lake Worth","Florida","FL","Southeast Florida","Palm Beach County","mid",26.6151,-80.0534),
    ("Riviera Beach","Florida","FL","Southeast Florida","Palm Beach County","mid",26.7751,-80.0587),
    ("Jupiter","Florida","FL","Southeast Florida","Palm Beach County","mid",26.9342,-80.0942),
    ("Stuart","Florida","FL","Treasure Coast","Martin County","mid",27.1975,-80.2523),
    ("Fort Pierce","Florida","FL","Treasure Coast","St Lucie County","mid",27.4467,-80.3256),
    ("Vero Beach","Florida","FL","Treasure Coast","Indian River County","mid",27.6386,-80.3973),
    ("Sebastian","Florida","FL","Treasure Coast","Indian River County","small",27.8158,-80.4773),
    ("Fernandina Beach","Florida","FL","Northeast Florida","Nassau County","small",30.6696,-81.4626),
    ("St Augustine","Florida","FL","Northeast Florida","St Johns County","mid",29.8947,-81.3145),
    ("Palm Coast","Florida","FL","Northeast Florida","Flagler County","mid",29.5858,-81.2079),
    ("Daytona Beach Shores","Florida","FL","East Central Florida","Volusia County","small",29.1875,-80.9937),
    # NORTH CAROLINA additional
    ("Goldsboro","North Carolina","NC","Eastern NC","Wayne County","mid",35.3849,-77.9928),
    ("Greenville","North Carolina","NC","Eastern NC","Pitt County","mid",35.6127,-77.3663),
    ("Hickory","North Carolina","NC","Foothills","Catawba County","mid",35.7332,-81.3415),
    ("Kannapolis","North Carolina","NC","Piedmont","Cabarrus County","mid",35.4877,-80.6217),
    ("New Bern","North Carolina","NC","Coastal Plain","Craven County","mid",35.1085,-77.0441),
    ("Sanford","North Carolina","NC","Central NC","Lee County","small",35.4799,-79.1803),
    ("Statesville","North Carolina","NC","Piedmont","Iredell County","small",35.7827,-80.8873),
    ("Lumberton","North Carolina","NC","Sandhills","Robeson County","small",34.6182,-79.0086),
    ("Salisbury","North Carolina","NC","Piedmont","Rowan County","mid",35.6710,-80.4743),
    ("Thomasville","North Carolina","NC","Piedmont Triad","Davidson County","mid",35.8827,-80.0812),
    ("Morganton","North Carolina","NC","Foothills","Burke County","small",35.7449,-81.6851),
    ("Asheboro","North Carolina","NC","Piedmont","Randolph County","mid",35.7077,-79.8133),
    ("Monroe","North Carolina","NC","Piedmont","Union County","mid",34.9854,-80.5490),
    ("Matthews","North Carolina","NC","Piedmont","Mecklenburg County","mid",35.1190,-80.7137),
    ("Apex","North Carolina","NC","Triangle","Wake County","mid",35.7327,-78.8502),
    ("Wake Forest","North Carolina","NC","Triangle","Wake County","mid",35.9799,-78.5096),
    ("Garner","North Carolina","NC","Triangle","Wake County","mid",35.7113,-78.6140),
    ("Holly Springs","North Carolina","NC","Triangle","Wake County","mid",35.6518,-78.8340),
    ("Fuquay-Varina","North Carolina","NC","Triangle","Wake County","mid",35.5840,-78.7997),
    # TENNESSEE additional
    ("Cookeville","Tennessee","TN","Upper Cumberland","Putnam County","mid",36.1628,-85.5016),
    ("Columbia","Tennessee","TN","Middle Tennessee","Maury County","mid",35.6151,-87.0353),
    ("Morristown","Tennessee","TN","Northeast Tennessee","Hamblen County","mid",36.2098,-83.2963),
    ("Gallatin","Tennessee","TN","Middle Tennessee","Sumner County","mid",36.3884,-86.4466),
    ("Lebanon","Tennessee","TN","Middle Tennessee","Wilson County","mid",36.2084,-86.2891),
    ("Maryville","Tennessee","TN","East Tennessee","Blount County","mid",35.7565,-83.9702),
    ("Oak Ridge","Tennessee","TN","East Tennessee","Anderson County","mid",36.0104,-84.2696),
    ("Cleveland","Tennessee","TN","Southeast Tennessee","Bradley County","mid",35.1595,-84.8766),
    ("Shelbyville","Tennessee","TN","Middle Tennessee","Bedford County","small",35.4834,-86.4605),
    ("Tullahoma","Tennessee","TN","Middle Tennessee","Coffee County","small",35.3620,-86.2097),
    ("Dyersburg","Tennessee","TN","West Tennessee","Dyer County","small",36.0345,-89.3837),
    ("Elizabethton","Tennessee","TN","Northeast Tennessee","Carter County","small",36.3487,-82.2108),
    ("Athens","Tennessee","TN","Southeast Tennessee","McMinn County","small",35.4428,-84.5966),
    ("Manchester","Tennessee","TN","Middle Tennessee","Coffee County","small",35.4820,-86.0886),
    # VIRGINIA additional
    ("Fredericksburg","Virginia","VA","Northern Virginia","Fredericksburg City","mid",38.3032,-77.4605),
    ("Harrisonburg","Virginia","VA","Shenandoah Valley","Harrisonburg City","mid",38.4496,-78.8689),
    ("Charlottesville","Virginia","VA","Central Virginia","Charlottesville City","mid",38.0293,-78.4767),
    ("Danville","Virginia","VA","Southern Virginia","Danville City","mid",36.5860,-79.3950),
    ("Manassas","Virginia","VA","Northern Virginia","Manassas City","mid",38.7509,-77.4752),
    ("Blacksburg","Virginia","VA","Southwest Virginia","Montgomery County","mid",37.2296,-80.4139),
    ("Lynchburg","Virginia","VA","Central Virginia","Lynchburg City","mid",37.4138,-79.1422),
    ("Staunton","Virginia","VA","Shenandoah Valley","Staunton City","small",38.1496,-79.0717),
    ("Waynesboro","Virginia","VA","Shenandoah Valley","Waynesboro City","small",38.0685,-78.8895),
    ("Winchester","Virginia","VA","Northern Shenandoah Valley","Winchester City","mid",39.1857,-78.1633),
    ("Leesburg","Virginia","VA","Northern Virginia","Loudoun County","mid",39.1157,-77.5636),
    ("Herndon","Virginia","VA","Northern Virginia","Fairfax County","mid",38.9696,-77.3861),
    ("Reston","Virginia","VA","Northern Virginia","Fairfax County","mid",38.9687,-77.3411),
    ("Sterling","Virginia","VA","Northern Virginia","Loudoun County","mid",39.0020,-77.4186),
    ("Ashburn","Virginia","VA","Northern Virginia","Loudoun County","mid",39.0437,-77.4875),
    # SOUTH CAROLINA additional
    ("Spartanburg","South Carolina","SC","Upstate","Spartanburg County","mid",34.9496,-81.9321),
    ("Anderson","South Carolina","SC","Upstate","Anderson County","mid",34.5034,-82.6501),
    ("Myrtle Beach","South Carolina","SC","Grand Strand","Horry County","mid",33.6890,-78.8867),
    ("Conway","South Carolina","SC","Grand Strand","Horry County","small",33.8360,-79.0453),
    ("Aiken","South Carolina","SC","CSRA","Aiken County","mid",33.5601,-81.7198),
    ("Beaufort","South Carolina","SC","Lowcountry","Beaufort County","small",32.4316,-80.6698),
    ("Greenwood","South Carolina","SC","Upstate","Greenwood County","small",34.1954,-82.1618),
    ("Orangeburg","South Carolina","SC","Midlands","Orangeburg County","small",33.4918,-80.8651),
    ("Sumter","South Carolina","SC","Midlands","Sumter County","mid",33.9204,-80.3412),
    ("Gaffney","South Carolina","SC","Upstate","Cherokee County","small",35.0718,-81.6498),
    # LOUISIANA additional
    ("Houma","Louisiana","LA","South Louisiana","Terrebonne Parish","mid",29.5958,-90.7195),
    ("Slidell","Louisiana","LA","Southeast Louisiana","St Tammany Parish","mid",30.2752,-89.7812),
    ("New Iberia","Louisiana","LA","Acadiana","Iberia Parish","small",30.0035,-91.8188),
    ("Ruston","Louisiana","LA","North Louisiana","Lincoln Parish","small",32.5232,-92.6382),
    ("Natchitoches","Louisiana","LA","Central Louisiana","Natchitoches Parish","small",31.7607,-93.0863),
    ("Opelousas","Louisiana","LA","South Central Louisiana","St Landry Parish","small",30.5335,-92.0818),
    ("Hammond","Louisiana","LA","Southeast Louisiana","Tangipahoa Parish","mid",30.5044,-90.4612),
    ("Covington","Louisiana","LA","Southeast Louisiana","St Tammany Parish","mid",30.4754,-90.1006),
    ("Morgan City","Louisiana","LA","South Louisiana","St Mary Parish","small",29.6994,-91.2085),
    ("Thibodaux","Louisiana","LA","South Louisiana","Lafourche Parish","small",29.7958,-90.8174),
    ("Minden","Louisiana","LA","Northwest Louisiana","Webster Parish","small",32.6154,-93.2863),
    ("Bastrop","Louisiana","LA","Northeast Louisiana","Morehouse Parish","small",32.7779,-91.9085),
    # MISSISSIPPI additional
    ("Vicksburg","Mississippi","MS","West Mississippi","Warren County","small",32.3526,-90.8779),
    ("Greenville","Mississippi","MS","Delta","Washington County","small",33.4099,-91.0629),
    ("Columbus","Mississippi","MS","Northeast Mississippi","Lowndes County","mid",33.4957,-88.4273),
    ("Starkville","Mississippi","MS","Northeast Mississippi","Oktibbeha County","mid",33.4607,-88.8184),
    ("Natchez","Mississippi","MS","Southwest Mississippi","Adams County","small",31.5601,-91.4032),
    ("Laurel","Mississippi","MS","South Mississippi","Jones County","small",31.6940,-89.1306),
    ("McComb","Mississippi","MS","Southwest Mississippi","Pike County","small",31.2435,-90.4537),
    ("Greenwood","Mississippi","MS","Delta","Leflore County","small",33.5160,-90.1796),
    ("Clarksdale","Mississippi","MS","Delta","Coahoma County","small",34.2004,-90.5707),
    ("Oxford","Mississippi","MS","North Mississippi","Lafayette County","mid",34.3665,-89.5195),
    ("Picayune","Mississippi","MS","South Mississippi","Pearl River County","small",30.5263,-89.6782),
    ("Pascagoula","Mississippi","MS","Gulf Coast","Jackson County","mid",30.3657,-88.5562),
    ("Moss Point","Mississippi","MS","Gulf Coast","Jackson County","small",30.4118,-88.5173),
    # ARKANSAS additional
    ("Hot Springs","Arkansas","AR","Central Arkansas","Garland County","mid",34.5037,-93.0552),
    ("El Dorado","Arkansas","AR","South Arkansas","Union County","small",33.2076,-92.6660),
    ("Texarkana","Arkansas","AR","Southwest Arkansas","Miller County","mid",33.4418,-94.0477),
    ("Russellville","Arkansas","AR","River Valley","Pope County","small",35.2787,-93.1338),
    ("Blytheville","Arkansas","AR","Northeast Arkansas","Mississippi County","small",35.9270,-89.9187),
    ("Mountain Home","Arkansas","AR","Ozarks","Baxter County","small",36.3354,-92.3849),
    ("Batesville","Arkansas","AR","North Central Arkansas","Independence County","small",35.7695,-91.6410),
    ("Harrison","Arkansas","AR","Ozarks","Boone County","small",36.2298,-93.1077),
    ("Searcy","Arkansas","AR","Central Arkansas","White County","small",35.2507,-91.7365),
    ("Paragould","Arkansas","AR","Northeast Arkansas","Greene County","small",36.0584,-90.4979),
    ("Forrest City","Arkansas","AR","East Arkansas","St Francis County","small",35.0084,-90.7896),
    ("Pine Bluff","Arkansas","AR","Southeast Arkansas","Jefferson County","mid",34.2284,-92.0032),
    # OKLAHOMA additional
    ("Muskogee","Oklahoma","OK","East Oklahoma","Muskogee County","mid",35.7479,-95.3697),
    ("Shawnee","Oklahoma","OK","Central Oklahoma","Pottawatomie County","mid",35.3273,-96.9253),
    ("Ardmore","Oklahoma","OK","South Central Oklahoma","Carter County","small",34.1743,-97.1436),
    ("Ponca City","Oklahoma","OK","North Central Oklahoma","Kay County","small",36.7070,-97.0856),
    ("Bartlesville","Oklahoma","OK","Northeast Oklahoma","Washington County","mid",36.7473,-95.9808),
    ("Claremore","Oklahoma","OK","Northeast Oklahoma","Rogers County","small",36.3126,-95.6147),
    ("Duncan","Oklahoma","OK","South Central Oklahoma","Stephens County","small",34.5023,-97.9578),
    ("McAlester","Oklahoma","OK","Southeast Oklahoma","Pittsburg County","small",34.9334,-95.7697),
    ("Yukon","Oklahoma","OK","Central Oklahoma","Canadian County","mid",35.5067,-97.7625),
    ("Mustang","Oklahoma","OK","Central Oklahoma","Canadian County","small",35.3845,-97.7244),
    ("Weatherford","Oklahoma","OK","West Central Oklahoma","Custer County","small",35.5267,-98.7071),
    ("Elk City","Oklahoma","OK","Western Oklahoma","Beckham County","small",35.4120,-99.4044),
    ("Enid","Oklahoma","OK","Northwest Oklahoma","Garfield County","mid",36.3956,-97.8784),
    # KENTUCKY additional
    ("Elizabethtown","Kentucky","KY","Central Kentucky","Hardin County","mid",37.6940,-85.8591),
    ("Paducah","Kentucky","KY","Western Kentucky","McCracken County","mid",37.0834,-88.6001),
    ("Frankfort","Kentucky","KY","Bluegrass Region","Franklin County","mid",38.2009,-84.8733),
    ("Murray","Kentucky","KY","Western Kentucky","Calloway County","small",36.6103,-88.3148),
    ("Somerset","Kentucky","KY","South Central Kentucky","Pulaski County","small",37.0920,-84.6041),
    ("London","Kentucky","KY","Southeast Kentucky","Laurel County","small",37.1290,-84.0830),
    ("Middlesboro","Kentucky","KY","Southeast Kentucky","Bell County","small",36.6084,-83.7188),
    ("Ashland","Kentucky","KY","Eastern Kentucky","Boyd County","mid",38.4784,-82.6379),
    ("Morehead","Kentucky","KY","Eastern Kentucky","Rowan County","small",38.1840,-83.4327),
    ("Danville","Kentucky","KY","Bluegrass Region","Boyle County","small",37.6459,-84.7722),
    ("Nicholasville","Kentucky","KY","Bluegrass Region","Jessamine County","mid",37.8801,-84.5730),
    ("Radcliff","Kentucky","KY","Central Kentucky","Hardin County","mid",37.8401,-85.9488),
    # INDIANA additional
    ("Terre Haute","Indiana","IN","West Central Indiana","Vigo County","mid",39.4667,-87.4139),
    ("Kokomo","Indiana","IN","North Central Indiana","Howard County","mid",40.4864,-86.1336),
    ("Anderson","Indiana","IN","Central Indiana","Madison County","mid",40.1053,-85.6803),
    ("Noblesville","Indiana","IN","Central Indiana","Hamilton County","mid",40.0456,-86.0086),
    ("Greenwood","Indiana","IN","Central Indiana","Johnson County","mid",39.6136,-86.1069),
    ("Columbus","Indiana","IN","South Central Indiana","Bartholomew County","mid",39.2014,-85.9214),
    ("Jeffersonville","Indiana","IN","Southern Indiana","Clark County","mid",38.2776,-85.7372),
    ("New Albany","Indiana","IN","Southern Indiana","Floyd County","mid",38.2859,-85.8241),
    ("Michigan City","Indiana","IN","Northwest Indiana","La Porte County","mid",41.7075,-86.8950),
    ("Valparaiso","Indiana","IN","Northwest Indiana","Porter County","mid",41.4731,-87.0614),
    ("Portage","Indiana","IN","Northwest Indiana","Porter County","mid",41.5820,-87.1764),
    ("Munster","Indiana","IN","Northwest Indiana","Lake County","mid",41.5645,-87.5120),
    ("Crown Point","Indiana","IN","Northwest Indiana","Lake County","mid",41.4167,-87.3653),
    # OHIO additional
    ("Hamilton","Ohio","OH","Southwest Ohio","Butler County","mid",39.3995,-84.5613),
    ("Springfield","Ohio","OH","West Central Ohio","Clark County","mid",39.9242,-83.8088),
    ("Kettering","Ohio","OH","Southwest Ohio","Montgomery County","mid",39.6895,-84.1688),
    ("Elyria","Ohio","OH","Northeast Ohio","Lorain County","mid",41.3684,-82.1074),
    ("Lakewood","Ohio","OH","Northeast Ohio","Cuyahoga County","mid",41.4820,-81.7982),
    ("Cuyahoga Falls","Ohio","OH","Northeast Ohio","Summit County","mid",41.1334,-81.4846),
    ("Euclid","Ohio","OH","Northeast Ohio","Cuyahoga County","mid",41.5931,-81.5268),
    ("Middletown","Ohio","OH","Southwest Ohio","Butler County","mid",39.5151,-84.3983),
    ("Newark","Ohio","OH","Central Ohio","Licking County","mid",40.0581,-82.4013),
    ("Mansfield","Ohio","OH","North Central Ohio","Richland County","mid",40.7584,-82.5154),
    ("Dublin","Ohio","OH","Central Ohio","Franklin County","mid",40.0992,-83.1141),
    ("Westerville","Ohio","OH","Central Ohio","Franklin County","mid",40.1259,-82.9290),
    ("Grove City","Ohio","OH","Central Ohio","Franklin County","mid",39.8815,-83.0930),
    ("Beavercreek","Ohio","OH","Southwest Ohio","Greene County","mid",39.7337,-84.0630),
    ("Fairfield","Ohio","OH","Southwest Ohio","Butler County","mid",39.3459,-84.5599),
    # ILLINOIS additional
    ("Champaign","Illinois","IL","Central Illinois","Champaign County","mid",40.1164,-88.2434),
    ("Bloomington","Illinois","IL","Central Illinois","McLean County","mid",40.4842,-88.9937),
    ("Normal","Illinois","IL","Central Illinois","McLean County","mid",40.5142,-88.9906),
    ("Decatur","Illinois","IL","Central Illinois","Macon County","mid",39.8403,-88.9548),
    ("Evanston","Illinois","IL","Northeast Illinois","Cook County","mid",42.0450,-87.6877),
    ("Schaumburg","Illinois","IL","Northeast Illinois","Cook County","mid",42.0334,-88.0834),
    ("Bolingbrook","Illinois","IL","Northeast Illinois","Will County","mid",41.6986,-88.0684),
    ("Palatine","Illinois","IL","Northeast Illinois","Cook County","mid",42.1103,-88.0340),
    ("Skokie","Illinois","IL","Northeast Illinois","Cook County","mid",42.0334,-87.7334),
    ("Des Plaines","Illinois","IL","Northeast Illinois","Cook County","mid",42.0334,-87.8834),
    ("Mount Prospect","Illinois","IL","Northeast Illinois","Cook County","mid",42.0664,-87.9376),
    ("Moline","Illinois","IL","Quad Cities","Rock Island County","mid",41.5067,-90.5151),
    ("Rock Island","Illinois","IL","Quad Cities","Rock Island County","mid",41.5095,-90.5743),
    ("Galesburg","Illinois","IL","West Central Illinois","Knox County","mid",40.9478,-90.3712),
    ("Quincy","Illinois","IL","West Illinois","Adams County","mid",39.9356,-91.4099),
    # PENNSYLVANIA additional
    ("Altoona","Pennsylvania","PA","Central Pennsylvania","Blair County","mid",40.5187,-78.3947),
    ("Wilkes-Barre","Pennsylvania","PA","Northeast Pennsylvania","Luzerne County","mid",41.2459,-75.8813),
    ("Chester","Pennsylvania","PA","Southeast Pennsylvania","Delaware County","mid",39.8490,-75.3557),
    ("State College","Pennsylvania","PA","Central Pennsylvania","Centre County","mid",40.7934,-77.8600),
    ("New Castle","Pennsylvania","PA","Western Pennsylvania","Lawrence County","mid",40.9909,-80.3468),
    ("Johnstown","Pennsylvania","PA","Western Pennsylvania","Cambria County","mid",40.3267,-78.9220),
    ("Easton","Pennsylvania","PA","Lehigh Valley","Northampton County","mid",40.6884,-75.2207),
    ("Allentown","Pennsylvania","PA","Lehigh Valley","Lehigh County","major",40.6084,-75.4902),
    ("Pottstown","Pennsylvania","PA","Southeast Pennsylvania","Montgomery County","mid",40.2454,-75.6496),
    ("Norristown","Pennsylvania","PA","Southeast Pennsylvania","Montgomery County","mid",40.1215,-75.3399),
    # MICHIGAN additional
    ("Muskegon","Michigan","MI","West Michigan","Muskegon County","mid",43.2342,-86.2484),
    ("Saginaw","Michigan","MI","Mid-Michigan","Saginaw County","mid",43.4195,-83.9508),
    ("Bay City","Michigan","MI","Mid-Michigan","Bay County","mid",43.5945,-83.8888),
    ("Midland","Michigan","MI","Mid-Michigan","Midland County","mid",43.6156,-84.2472),
    ("Pontiac","Michigan","MI","Southeast Michigan","Oakland County","mid",42.6389,-83.2910),
    ("Rochester Hills","Michigan","MI","Southeast Michigan","Oakland County","mid",42.6583,-83.1499),
    ("Troy","Michigan","MI","Southeast Michigan","Oakland County","mid",42.6064,-83.1499),
    ("Auburn Hills","Michigan","MI","Southeast Michigan","Oakland County","mid",42.6875,-83.2343),
    ("Novi","Michigan","MI","Southeast Michigan","Oakland County","mid",42.4806,-83.4755),
    ("Holland","Michigan","MI","West Michigan","Ottawa County","mid",42.7875,-86.1089),
    ("Royal Oak","Michigan","MI","Southeast Michigan","Oakland County","mid",42.4895,-83.1446),
    ("Farmington Hills","Michigan","MI","Southeast Michigan","Oakland County","mid",42.4989,-83.3677),
    ("Southfield","Michigan","MI","Southeast Michigan","Oakland County","mid",42.4734,-83.2219),
    ("Westland","Michigan","MI","Southeast Michigan","Wayne County","mid",42.3242,-83.3999),
    ("Taylor","Michigan","MI","Southeast Michigan","Wayne County","mid",42.2403,-83.2696),
    # MINNESOTA additional
    ("Burnsville","Minnesota","MN","Twin Cities","Dakota County","mid",44.7677,-93.2777),
    ("Apple Valley","Minnesota","MN","Twin Cities","Dakota County","mid",44.7319,-93.2177),
    ("Lakeville","Minnesota","MN","Twin Cities","Dakota County","mid",44.6497,-93.2427),
    ("Blaine","Minnesota","MN","Twin Cities","Anoka County","mid",45.1608,-93.2350),
    ("Coon Rapids","Minnesota","MN","Twin Cities","Anoka County","mid",45.1197,-93.3108),
    ("Maple Grove","Minnesota","MN","Twin Cities","Hennepin County","mid",45.0886,-93.4558),
    ("Eden Prairie","Minnesota","MN","Twin Cities","Hennepin County","mid",44.8547,-93.4708),
    ("Minnetonka","Minnesota","MN","Twin Cities","Hennepin County","mid",44.9211,-93.4687),
    ("Edina","Minnesota","MN","Twin Cities","Hennepin County","mid",44.8897,-93.3499),
    ("Richfield","Minnesota","MN","Twin Cities","Hennepin County","mid",44.8836,-93.2832),
    ("Mankato","Minnesota","MN","Southern Minnesota","Blue Earth County","mid",44.1636,-94.0007),
    ("St Cloud","Minnesota","MN","Central Minnesota","Stearns County","mid",45.5579,-94.1632),
    ("Moorhead","Minnesota","MN","Red River Valley","Clay County","mid",46.8738,-96.7678),
    # WISCONSIN additional
    ("Sheboygan","Wisconsin","WI","East Wisconsin","Sheboygan County","mid",43.7508,-87.7145),
    ("Fond du Lac","Wisconsin","WI","East Wisconsin","Fond du Lac County","mid",43.7730,-88.4471),
    ("La Crosse","Wisconsin","WI","West Wisconsin","La Crosse County","mid",43.8014,-91.2396),
    ("Wausau","Wisconsin","WI","Central Wisconsin","Marathon County","mid",44.9591,-89.6301),
    ("Beloit","Wisconsin","WI","South Wisconsin","Rock County","mid",42.5083,-89.0318),
    ("Wauwatosa","Wisconsin","WI","Southeast Wisconsin","Milwaukee County","mid",43.0497,-88.0076),
    ("West Allis","Wisconsin","WI","Southeast Wisconsin","Milwaukee County","mid",43.0167,-88.0070),
    ("Brookfield","Wisconsin","WI","Southeast Wisconsin","Waukesha County","mid",43.0606,-88.1065),
    ("Menomonee Falls","Wisconsin","WI","Southeast Wisconsin","Waukesha County","mid",43.1786,-88.1070),
    ("Greenfield","Wisconsin","WI","Southeast Wisconsin","Milwaukee County","mid",42.9611,-88.0126),
    ("Mukwonago","Wisconsin","WI","Southeast Wisconsin","Waukesha County","small",42.8664,-88.3376),
    # MISSOURI additional
    ("St Peters","Missouri","MO","Eastern Missouri","St Charles County","mid",38.7875,-90.6290),
    ("Florissant","Missouri","MO","Eastern Missouri","St Louis County","mid",38.7892,-90.3224),
    ("Chesterfield","Missouri","MO","Eastern Missouri","St Louis County","mid",38.6631,-90.5771),
    ("Wentzville","Missouri","MO","Eastern Missouri","St Charles County","mid",38.8114,-90.8529),
    ("Joplin","Missouri","MO","Southwest Missouri","Jasper County","mid",37.0842,-94.5133),
    ("Cape Girardeau","Missouri","MO","Southeast Missouri","Cape Girardeau County","mid",37.3059,-89.5181),
    ("Jefferson City","Missouri","MO","Central Missouri","Cole County","mid",38.5767,-92.1735),
    ("St Joseph","Missouri","MO","Northwest Missouri","Buchanan County","mid",39.7675,-94.8467),
    ("Sedalia","Missouri","MO","Central Missouri","Pettis County","small",38.7042,-93.2285),
    ("Poplar Bluff","Missouri","MO","Southeast Missouri","Butler County","small",36.7573,-90.3929),
    # COLORADO additional
    ("Longmont","Colorado","CO","Front Range","Boulder County","mid",40.1672,-105.1019),
    ("Loveland","Colorado","CO","Northern Colorado","Larimer County","mid",40.3978,-105.0749),
    ("Greeley","Colorado","CO","Northern Colorado","Weld County","mid",40.4233,-104.7091),
    ("Broomfield","Colorado","CO","Front Range","Broomfield County","mid",39.9205,-105.0867),
    ("Castle Rock","Colorado","CO","Front Range","Douglas County","mid",39.3722,-104.8561),
    ("Parker","Colorado","CO","Front Range","Douglas County","mid",39.5186,-104.7614),
    ("Brighton","Colorado","CO","Front Range","Adams County","mid",39.9855,-104.8127),
    ("Centennial","Colorado","CO","Front Range","Arapahoe County","mid",39.5807,-104.8772),
    ("Highlands Ranch","Colorado","CO","Front Range","Douglas County","mid",39.5480,-104.9691),
    ("Commerce City","Colorado","CO","Front Range","Adams County","mid",39.8083,-104.9341),
    ("Grand Junction","Colorado","CO","Western Colorado","Mesa County","mid",39.0639,-108.5506),
    ("Sterling","Colorado","CO","Northeast Colorado","Logan County","small",40.6253,-103.2077),
    ("Durango","Colorado","CO","Southwest Colorado","La Plata County","mid",37.2753,-107.8801),
    ("Steamboat Springs","Colorado","CO","Northwest Colorado","Routt County","small",40.4850,-106.8317),
    ("Aspen","Colorado","CO","Central Colorado","Pitkin County","small",39.1911,-106.8175),
    # WASHINGTON additional
    ("Yakima","Washington","WA","Central Washington","Yakima County","mid",46.6021,-120.5059),
    ("Kennewick","Washington","WA","Tri-Cities","Benton County","mid",46.2112,-119.1372),
    ("Richland","Washington","WA","Tri-Cities","Benton County","mid",46.2860,-119.2841),
    ("Pasco","Washington","WA","Tri-Cities","Franklin County","mid",46.2396,-119.1006),
    ("Marysville","Washington","WA","Puget Sound","Snohomish County","mid",48.0512,-122.1771),
    ("Shoreline","Washington","WA","Puget Sound","King County","mid",47.7551,-122.3415),
    ("Redmond","Washington","WA","Puget Sound","King County","mid",47.6740,-122.1215),
    ("Sammamish","Washington","WA","Puget Sound","King County","mid",47.6163,-122.0356),
    ("Federal Way","Washington","WA","Puget Sound","King County","mid",47.3223,-122.3126),
    ("Lakewood","Washington","WA","Puget Sound","Pierce County","mid",47.1718,-122.5185),
    ("Puyallup","Washington","WA","Puget Sound","Pierce County","mid",47.1854,-122.2929),
    ("Burien","Washington","WA","Puget Sound","King County","mid",47.4709,-122.3465),
    ("Auburn","Washington","WA","Puget Sound","King County","mid",47.3073,-122.2284),
    ("Wenatchee","Washington","WA","Central Washington","Chelan County","mid",47.4235,-120.3103),
    ("Mount Vernon","Washington","WA","Northwest Washington","Skagit County","mid",48.4218,-122.3343),
    # ARIZONA additional
    ("Prescott","Arizona","AZ","Central Arizona","Yavapai County","mid",34.5400,-112.4685),
    ("Lake Havasu City","Arizona","AZ","Western Arizona","Mohave County","mid",34.4839,-114.3224),
    ("Sierra Vista","Arizona","AZ","Southeast Arizona","Cochise County","mid",31.5455,-110.3028),
    ("Maricopa","Arizona","AZ","Valley of the Sun","Pinal County","mid",33.0581,-112.0476),
    ("Casa Grande","Arizona","AZ","Central Arizona","Pinal County","mid",32.8795,-111.7574),
    ("Prescott Valley","Arizona","AZ","Central Arizona","Yavapai County","mid",34.6100,-112.3152),
    ("Kingman","Arizona","AZ","Northwest Arizona","Mohave County","mid",35.1895,-114.0530),
    ("Show Low","Arizona","AZ","Eastern Arizona","Navajo County","small",34.2542,-110.0298),
    ("Bullhead City","Arizona","AZ","Western Arizona","Mohave County","mid",35.1478,-114.5683),
    ("Payson","Arizona","AZ","Central Arizona","Gila County","small",34.2314,-111.3251),
    ("Douglas","Arizona","AZ","Southeast Arizona","Cochise County","small",31.3445,-109.5456),
    ("Safford","Arizona","AZ","Southeast Arizona","Graham County","small",32.8337,-109.7073),
    # NEVADA additional
    ("Boulder City","Nevada","NV","Southern Nevada","Clark County","small",35.9788,-114.8328),
    ("Mesquite","Nevada","NV","Southern Nevada","Clark County","small",36.8055,-114.0672),
    ("Fernley","Nevada","NV","Northern Nevada","Lyon County","small",39.6083,-119.2521),
    ("Elko","Nevada","NV","Northeast Nevada","Elko County","small",40.8324,-115.7631),
    ("Pahrump","Nevada","NV","Southern Nevada","Nye County","small",36.2083,-115.9847),
    ("Fallon","Nevada","NV","Central Nevada","Churchill County","small",39.4735,-118.7774),
    ("Winnemucca","Nevada","NV","Northern Nevada","Humboldt County","small",40.9730,-117.7357),
    ("Henderson","Nevada","NV","Southern Nevada","Clark County","major",36.0397,-114.9819),
    ("Enterprise","Nevada","NV","Southern Nevada","Clark County","mid",36.0253,-115.2257),
    # OREGON additional
    ("Springfield","Oregon","OR","Willamette Valley","Lane County","mid",44.0462,-123.0220),
    ("Albany","Oregon","OR","Willamette Valley","Linn County","mid",44.6365,-123.1059),
    ("Ashland","Oregon","OR","Southern Oregon","Jackson County","small",42.1945,-122.7095),
    ("Klamath Falls","Oregon","OR","South Central Oregon","Klamath County","mid",42.2249,-121.7817),
    ("Grants Pass","Oregon","OR","Southern Oregon","Josephine County","mid",42.4390,-123.2984),
    ("Lake Oswego","Oregon","OR","Willamette Valley","Clackamas County","mid",45.4207,-122.7007),
    ("Tigard","Oregon","OR","Willamette Valley","Washington County","mid",45.4312,-122.7712),
    ("Lake Oswego","Oregon","OR","Willamette Valley","Clackamas County","mid",45.4207,-122.7007),
    ("McMinnville","Oregon","OR","Willamette Valley","Yamhill County","mid",45.2096,-123.1987),
    ("Roseburg","Oregon","OR","Southern Oregon","Douglas County","mid",43.2165,-123.3418),
    ("Coos Bay","Oregon","OR","Oregon Coast","Coos County","small",43.3665,-124.2179),
    ("Pendleton","Oregon","OR","Northeast Oregon","Umatilla County","small",45.6721,-118.7887),
    # UTAH additional
    ("Logan","Utah","UT","Northern Utah","Cache County","mid",41.7355,-111.8349),
    ("Murray","Utah","UT","Wasatch Front","Salt Lake County","mid",40.6669,-111.8879),
    ("Taylorsville","Utah","UT","Wasatch Front","Salt Lake County","mid",40.6577,-111.9388),
    ("Herriman","Utah","UT","Wasatch Front","Salt Lake County","small",40.5141,-112.0327),
    ("Lehi","Utah","UT","Utah Valley","Utah County","mid",40.3916,-111.8507),
    ("Spanish Fork","Utah","UT","Utah Valley","Utah County","mid",40.1149,-111.6546),
    ("Springville","Utah","UT","Utah Valley","Utah County","small",40.1694,-111.6113),
    ("American Fork","Utah","UT","Utah Valley","Utah County","mid",40.3769,-111.7996),
    ("Bountiful","Utah","UT","Wasatch Front","Davis County","mid",40.8894,-111.8808),
    ("Cedar City","Utah","UT","Southern Utah","Iron County","mid",37.6775,-113.0619),
    ("Tooele","Utah","UT","Wasatch Front","Tooele County","mid",40.5305,-112.2983),
    ("Millcreek","Utah","UT","Wasatch Front","Salt Lake County","mid",40.6869,-111.8766),
    # NEW MEXICO additional
    ("Gallup","New Mexico","NM","Northwest New Mexico","McKinley County","mid",35.5281,-108.7426),
    ("Las Vegas","New Mexico","NM","Northeast New Mexico","San Miguel County","small",35.5937,-105.2236),
    ("Alamogordo","New Mexico","NM","South Central New Mexico","Otero County","mid",32.8995,-105.9603),
    ("Silver City","New Mexico","NM","Southwest New Mexico","Grant County","small",32.7701,-108.2803),
    ("Portales","New Mexico","NM","Eastern New Mexico","Roosevelt County","small",34.1876,-103.3349),
    ("Lovington","New Mexico","NM","Southeast New Mexico","Lea County","small",32.9437,-103.3488),
    ("Artesia","New Mexico","NM","Southeast New Mexico","Eddy County","small",32.8426,-104.4035),
    ("Deming","New Mexico","NM","Southwest New Mexico","Luna County","small",32.2687,-107.7539),
    ("Taos","New Mexico","NM","North Central New Mexico","Taos County","small",36.4072,-105.5731),
    # IDAHO additional
    ("Rexburg","Idaho","ID","Eastern Idaho","Madison County","small",43.8257,-111.7896),
    ("Moscow","Idaho","ID","North Central Idaho","Latah County","small",46.7324,-117.0002),
    ("Burley","Idaho","ID","South Central Idaho","Cassia County","small",42.5360,-113.7929),
    ("Chubbuck","Idaho","ID","Southeast Idaho","Bannock County","mid",42.9230,-112.4641),
    ("Ammon","Idaho","ID","Eastern Idaho","Bonneville County","mid",43.4688,-112.0302),
    ("Hailey","Idaho","ID","Central Idaho","Blaine County","small",43.5193,-114.3154),
    ("Sandpoint","Idaho","ID","Northern Idaho","Bonner County","small",48.2766,-116.5531),
    ("Lewiston","Idaho","ID","North Central Idaho","Nez Perce County","mid",46.4165,-117.0177),
    # MONTANA additional
    ("Missoula","Montana","MT","Western Montana","Missoula County","mid",46.8721,-113.9940),
    ("Great Falls","Montana","MT","North Central Montana","Cascade County","mid",47.5002,-111.3008),
    ("Bozeman","Montana","MT","Southwest Montana","Gallatin County","mid",45.6770,-111.0429),
    ("Butte","Montana","MT","Southwest Montana","Silver Bow County","mid",46.0038,-112.5348),
    ("Helena","Montana","MT","West Central Montana","Lewis and Clark County","mid",46.5958,-112.0270),
    ("Kalispell","Montana","MT","Northwest Montana","Flathead County","small",48.1920,-114.3168),
    ("Havre","Montana","MT","North Central Montana","Hill County","small",48.5500,-109.6833),
    ("Miles City","Montana","MT","Eastern Montana","Custer County","small",46.4083,-105.8406),
    ("Livingston","Montana","MT","South Central Montana","Park County","small",45.6624,-110.5615),
    ("Lewistown","Montana","MT","Central Montana","Fergus County","small",47.0636,-109.4279),
    # ALASKA additional
    ("Fairbanks","Alaska","AK","Interior Alaska","Fairbanks North Star Borough","mid",64.8378,-147.7164),
    ("Juneau","Alaska","AK","Southeast Alaska","City and Borough of Juneau","mid",58.3005,-134.4197),
    ("Sitka","Alaska","AK","Southeast Alaska","City and Borough of Sitka","small",57.0531,-135.3300),
    ("Ketchikan","Alaska","AK","Southeast Alaska","Ketchikan Gateway Borough","small",55.3422,-131.6461),
    ("Wasilla","Alaska","AK","Southcentral Alaska","Matanuska-Susitna Borough","small",61.5814,-149.4414),
    ("Kenai","Alaska","AK","Southcentral Alaska","Kenai Peninsula Borough","small",60.5544,-151.2583),
    ("Palmer","Alaska","AK","Southcentral Alaska","Matanuska-Susitna Borough","small",61.5997,-149.1142),
    ("Kodiak","Alaska","AK","Southcentral Alaska","Kodiak Island Borough","small",57.7900,-152.4072),
    ("Nome","Alaska","AK","Western Alaska","Nome Census Area","tiny",64.5011,-165.4064),
    ("Barrow","Alaska","AK","North Slope","North Slope Borough","tiny",71.2906,-156.7887),
    # HAWAII additional
    ("Pearl City","Hawaii","HI","Oahu","City and County of Honolulu","mid",21.3972,-157.9739),
    ("Hilo","Hawaii","HI","Big Island","Hawaii County","mid",19.7297,-155.0900),
    ("Kailua","Hawaii","HI","Oahu","City and County of Honolulu","mid",21.3969,-157.7394),
    ("Waipahu","Hawaii","HI","Oahu","City and County of Honolulu","mid",21.3858,-158.0097),
    ("Kaneohe","Hawaii","HI","Oahu","City and County of Honolulu","mid",21.4022,-157.8003),
    ("Mililani Town","Hawaii","HI","Oahu","City and County of Honolulu","small",21.4511,-158.0147),
    ("Kahului","Hawaii","HI","Maui","Maui County","small",20.8893,-156.4729),
    ("Kihei","Hawaii","HI","Maui","Maui County","small",20.7644,-156.4450),
    ("Wailuku","Hawaii","HI","Maui","Maui County","small",20.8947,-156.5072),
    ("Lihue","Hawaii","HI","Kauai","Kauai County","small",21.9811,-159.3711),
    # WEST VIRGINIA additional
    ("Huntington","West Virginia","WV","Western WV","Cabell County","mid",38.4193,-82.4452),
    ("Morgantown","West Virginia","WV","North Central WV","Monongalia County","mid",39.6295,-79.9559),
    ("Parkersburg","West Virginia","WV","Mid-Ohio Valley","Wood County","mid",39.2667,-81.5615),
    ("Wheeling","West Virginia","WV","Northern Panhandle","Ohio County","mid",40.0640,-80.7209),
    ("Beckley","West Virginia","WV","Southern WV","Raleigh County","small",37.7782,-81.1882),
    ("Clarksburg","West Virginia","WV","North Central WV","Harrison County","small",39.2806,-80.3445),
    ("Martinsburg","West Virginia","WV","Eastern Panhandle","Berkeley County","mid",39.4562,-77.9636),
    ("Weirton","West Virginia","WV","Northern Panhandle","Hancock County","small",40.4187,-80.5893),
    ("Fairmont","West Virginia","WV","North Central WV","Marion County","small",39.4842,-80.1426),
    ("Lewisburg","West Virginia","WV","Southeast WV","Greenbrier County","small",37.7998,-80.4454),
    # NORTH DAKOTA additional
    ("Williston","North Dakota","ND","Northwest North Dakota","Williams County","small",48.1470,-103.6179),
    ("Dickinson","North Dakota","ND","Southwest North Dakota","Stark County","small",46.8792,-102.7896),
    ("Mandan","North Dakota","ND","South Central North Dakota","Morton County","small",46.8266,-100.8896),
    ("Jamestown","North Dakota","ND","Central North Dakota","Stutsman County","small",46.9063,-98.7084),
    ("Wahpeton","North Dakota","ND","Southeast North Dakota","Richland County","small",46.2655,-96.6057),
    # SOUTH DAKOTA additional
    ("Aberdeen","South Dakota","SD","Northeast South Dakota","Brown County","small",45.4647,-98.4865),
    ("Brookings","South Dakota","SD","East South Dakota","Brookings County","small",44.3114,-96.7984),
    ("Watertown","South Dakota","SD","Northeast South Dakota","Codington County","small",44.8997,-97.1170),
    ("Mitchell","South Dakota","SD","Central South Dakota","Davison County","small",43.7097,-98.0298),
    ("Pierre","South Dakota","SD","Central South Dakota","Hughes County","small",44.3683,-100.3510),
    ("Yankton","South Dakota","SD","Southeast South Dakota","Yankton County","small",42.8713,-97.3973),
    ("Huron","South Dakota","SD","Central South Dakota","Beadle County","small",44.3630,-98.2145),
    # WYOMING additional
    ("Sheridan","Wyoming","WY","Northeast Wyoming","Sheridan County","small",44.7972,-106.9562),
    ("Green River","Wyoming","WY","Southwest Wyoming","Sweetwater County","small",41.5275,-109.4663),
    ("Evanston","Wyoming","WY","Southwest Wyoming","Uinta County","small",41.2686,-110.9632),
    ("Riverton","Wyoming","WY","Central Wyoming","Fremont County","small",43.0247,-108.3801),
    ("Jackson","Wyoming","WY","Northwest Wyoming","Teton County","small",43.4799,-110.7624),
    ("Cody","Wyoming","WY","Northwest Wyoming","Park County","small",44.5263,-109.0565),
    ("Lander","Wyoming","WY","Central Wyoming","Fremont County","small",42.8330,-108.7307),
    ("Torrington","Wyoming","WY","Southeast Wyoming","Goshen County","small",42.0627,-104.1838),
    # IOWA additional
    ("Dubuque","Iowa","IA","Northeast Iowa","Dubuque County","mid",42.4988,-90.6646),
    ("Cedar Falls","Iowa","IA","Northeast Iowa","Black Hawk County","mid",42.5349,-92.4458),
    ("Bettendorf","Iowa","IA","Quad Cities","Scott County","mid",41.5245,-90.5007),
    ("Mason City","Iowa","IA","North Central Iowa","Cerro Gordo County","mid",43.1536,-93.2010),
    ("Marshalltown","Iowa","IA","Central Iowa","Marshall County","small",42.0494,-92.9077),
    ("Clinton","Iowa","IA","Eastern Iowa","Clinton County","small",41.8445,-90.1888),
    ("Burlington","Iowa","IA","Southeast Iowa","Des Moines County","small",40.8073,-91.1129),
    ("Ottumwa","Iowa","IA","Southeast Iowa","Wapello County","small",41.0200,-92.4113),
    ("Fort Dodge","Iowa","IA","North Central Iowa","Webster County","small",42.4975,-94.1677),
    ("Muscatine","Iowa","IA","Eastern Iowa","Muscatine County","small",41.4245,-91.0432),
    # KANSAS additional
    ("Hutchinson","Kansas","KS","Central Kansas","Reno County","mid",38.0608,-97.9298),
    ("Junction City","Kansas","KS","North Central Kansas","Geary County","small",39.0286,-96.8317),
    ("Emporia","Kansas","KS","East Central Kansas","Lyon County","small",38.4039,-96.1817),
    ("Garden City","Kansas","KS","Southwest Kansas","Finney County","small",37.9717,-100.8729),
    ("Dodge City","Kansas","KS","Southwest Kansas","Ford County","small",37.7528,-100.0171),
    ("Hays","Kansas","KS","West Central Kansas","Ellis County","small",38.8794,-99.3268),
    ("Liberal","Kansas","KS","Southwest Kansas","Seward County","small",37.0431,-100.9212),
    ("Pittsburg","Kansas","KS","Southeast Kansas","Crawford County","small",37.4109,-94.7052),
    ("Leavenworth","Kansas","KS","Northeast Kansas","Leavenworth County","mid",39.3111,-94.9224),
    # NEBRASKA additional
    ("Scottsbluff","Nebraska","NE","Western Nebraska","Scotts Bluff County","small",41.8661,-103.6671),
    ("Hastings","Nebraska","NE","South Central Nebraska","Adams County","small",40.5862,-98.3884),
    ("Norfolk","Nebraska","NE","Northeast Nebraska","Madison County","small",42.0283,-97.4170),
    ("Columbus","Nebraska","NE","East Central Nebraska","Platte County","small",41.4300,-97.3681),
    ("North Platte","Nebraska","NE","West Central Nebraska","Lincoln County","small",41.1236,-100.7654),
    ("Fremont","Nebraska","NE","Eastern Nebraska","Dodge County","small",41.4333,-96.4983),
    ("Kearney","Nebraska","NE","Central Nebraska","Buffalo County","small",40.6993,-99.0817),
    ("Beatrice","Nebraska","NE","Southeast Nebraska","Gage County","small",40.2686,-96.7454),
    # MARYLAND additional
    ("Annapolis","Maryland","MD","Central Maryland","Anne Arundel County","mid",38.9784,-76.4922),
    ("Bowie","Maryland","MD","Central Maryland","Prince Georges County","mid",38.9420,-76.7791),
    ("Gaithersburg","Maryland","MD","Montgomery County","Montgomery County","mid",39.1434,-77.2014),
    ("Hagerstown","Maryland","MD","Western Maryland","Washington County","mid",39.6418,-77.7199),
    ("Salisbury","Maryland","MD","Eastern Shore","Wicomico County","mid",38.3607,-75.5996),
    ("Cumberland","Maryland","MD","Western Maryland","Allegany County","small",39.6526,-78.7630),
    ("Easton","Maryland","MD","Eastern Shore","Talbot County","small",38.7743,-76.0769),
    ("College Park","Maryland","MD","Central Maryland","Prince Georges County","mid",38.9807,-76.9369),
    ("Greenbelt","Maryland","MD","Central Maryland","Prince Georges County","mid",39.0046,-76.8755),
    ("Hyattsville","Maryland","MD","Central Maryland","Prince Georges County","mid",38.9557,-76.9455),
    # CONNECTICUT additional
    ("Meriden","Connecticut","CT","Central Connecticut","New Haven County","mid",41.5382,-72.7968),
    ("West Hartford","Connecticut","CT","Central Connecticut","Hartford County","mid",41.7620,-72.7415),
    ("Shelton","Connecticut","CT","Southwest Connecticut","Fairfield County","mid",41.3165,-73.0879),
    ("Milford","Connecticut","CT","South Central Connecticut","New Haven County","mid",41.2229,-73.0569),
    ("West Haven","Connecticut","CT","South Central Connecticut","New Haven County","mid",41.2723,-72.9470),
    ("Naugatuck","Connecticut","CT","West Central Connecticut","New Haven County","mid",41.4851,-73.0504),
    ("Enfield","Connecticut","CT","North Central Connecticut","Hartford County","mid",41.9762,-72.5920),
    ("Southington","Connecticut","CT","Central Connecticut","Hartford County","mid",41.5887,-72.8776),
    # NEW HAMPSHIRE additional
    ("Rochester","New Hampshire","NH","Seacoast","Strafford County","mid",43.3045,-70.9743),
    ("Keene","New Hampshire","NH","Southwest New Hampshire","Cheshire County","small",42.9337,-72.2779),
    ("Portsmouth","New Hampshire","NH","Seacoast","Rockingham County","mid",43.0718,-70.7626),
    ("Laconia","New Hampshire","NH","Lakes Region","Belknap County","small",43.5279,-71.4701),
    ("Claremont","New Hampshire","NH","West New Hampshire","Sullivan County","small",43.3773,-72.3454),
    ("Lebanon","New Hampshire","NH","West New Hampshire","Grafton County","small",43.6423,-72.2517),
    ("Berlin","New Hampshire","NH","North New Hampshire","Coos County","small",44.4684,-71.1848),
    # MAINE additional
    ("Lewiston","Maine","ME","Central Maine","Androscoggin County","mid",44.1004,-70.2148),
    ("Bangor","Maine","ME","Central Maine","Penobscot County","mid",44.8012,-68.7778),
    ("Biddeford","Maine","ME","Southern Maine","York County","small",43.4926,-70.4534),
    ("Sanford","Maine","ME","Southern Maine","York County","small",43.4387,-70.7748),
    ("Augusta","Maine","ME","Central Maine","Kennebec County","small",44.3106,-69.7795),
    ("Waterville","Maine","ME","Central Maine","Kennebec County","small",44.5526,-69.6317),
    ("Saco","Maine","ME","Southern Maine","York County","small",43.5009,-70.4429),
    ("Scarborough","Maine","ME","Southern Maine","Cumberland County","small",43.5773,-70.3584),
    ("Westbrook","Maine","ME","Southern Maine","Cumberland County","small",43.6773,-70.3701),
    ("Brunswick","Maine","ME","Southern Maine","Cumberland County","small",43.9148,-69.9653),
    # VERMONT additional
    ("Brattleboro","Vermont","VT","Southeast Vermont","Windham County","small",42.8509,-72.5579),
    ("St Johnsbury","Vermont","VT","Northeast Vermont","Caledonia County","small",44.4190,-72.0182),
    ("Middlebury","Vermont","VT","West Central Vermont","Addison County","small",44.0145,-73.1676),
    ("Newport","Vermont","VT","Northeast Vermont","Orleans County","small",44.9376,-72.2051),
    # RHODE ISLAND additional
    ("Woonsocket","Rhode Island","RI","Providence County","Providence County","mid",42.0015,-71.5148),
    ("Coventry","Rhode Island","RI","Kent County","Kent County","small",41.6987,-71.5690),
    ("Cumberland","Rhode Island","RI","Providence County","Providence County","small",41.9668,-71.4318),
    ("North Providence","Rhode Island","RI","Providence County","Providence County","small",41.8637,-71.4640),
    ("North Kingstown","Rhode Island","RI","Washington County","Washington County","small",41.5501,-71.4551),
    ("Johnston","Rhode Island","RI","Providence County","Providence County","small",41.8287,-71.5001),
    ("Smithfield","Rhode Island","RI","Providence County","Providence County","small",41.9004,-71.5337),
    ("Lincoln","Rhode Island","RI","Providence County","Providence County","small",41.9220,-71.4401),
    # DELAWARE additional
    ("Milford","Delaware","DE","Central Delaware","Kent County","small",38.9126,-75.4282),
    ("Seaford","Delaware","DE","Southern Delaware","Sussex County","small",38.6409,-75.6113),
    ("Georgetown","Delaware","DE","Southern Delaware","Sussex County","small",38.6901,-75.3863),
    ("Rehoboth Beach","Delaware","DE","Southern Delaware","Sussex County","tiny",38.7209,-75.0763),
    ("Lewes","Delaware","DE","Southern Delaware","Sussex County","small",38.7743,-75.1424),
    # MASSACHUSETTS additional
    ("Newton","Massachusetts","MA","Greater Boston","Middlesex County","mid",42.3370,-71.2092),
    ("Somerville","Massachusetts","MA","Greater Boston","Middlesex County","mid",42.3876,-71.0995),
    ("Waltham","Massachusetts","MA","Greater Boston","Middlesex County","mid",42.3765,-71.2356),
    ("Medford","Massachusetts","MA","Greater Boston","Middlesex County","mid",42.4184,-71.1062),
    ("Malden","Massachusetts","MA","Greater Boston","Middlesex County","mid",42.4251,-71.0662),
    ("Framingham","Massachusetts","MA","Greater Boston","Middlesex County","mid",42.2793,-71.4162),
    ("Haverhill","Massachusetts","MA","Greater Boston","Essex County","mid",42.7762,-71.0773),
    ("Taunton","Massachusetts","MA","Southeast Massachusetts","Bristol County","mid",41.9001,-71.0898),
    ("Chicopee","Massachusetts","MA","Western Massachusetts","Hampden County","mid",42.1487,-72.6079),
    ("Holyoke","Massachusetts","MA","Western Massachusetts","Hampden County","mid",42.2043,-72.6162),
    ("Pittsfield","Massachusetts","MA","Western Massachusetts","Berkshire County","mid",42.4501,-73.2454),
    ("Fitchburg","Massachusetts","MA","Central Massachusetts","Worcester County","mid",42.5834,-71.8023),
    ("Leominster","Massachusetts","MA","Central Massachusetts","Worcester County","mid",42.5251,-71.7598),
    ("Weymouth","Massachusetts","MA","Greater Boston","Norfolk County","mid",42.2087,-70.9401),
    ("Peabody","Massachusetts","MA","Greater Boston","Essex County","mid",42.5279,-70.9287),
    # NEW JERSEY additional
    ("Elizabeth","New Jersey","NJ","Northeast New Jersey","Union County","major",40.6640,-74.2107),
    ("Paterson","New Jersey","NJ","Northeast New Jersey","Passaic County","major",40.9176,-74.1719),
    ("Jersey City","New Jersey","NJ","Northeast New Jersey","Hudson County","major",40.7282,-74.0776),
    ("Newark","New Jersey","NJ","Northeast New Jersey","Essex County","major",40.7357,-74.1724),
    ("Camden","New Jersey","NJ","South New Jersey","Camden County","mid",39.9259,-75.1196),
    ("Clifton","New Jersey","NJ","Northeast New Jersey","Passaic County","mid",40.8584,-74.1638),
    ("Trenton","New Jersey","NJ","Central New Jersey","Mercer County","mid",40.2171,-74.7429),
    ("Piscataway","New Jersey","NJ","Central New Jersey","Middlesex County","mid",40.4993,-74.3996),
    ("Sayreville","New Jersey","NJ","Central New Jersey","Middlesex County","mid",40.4593,-74.3607),
    ("New Brunswick","New Jersey","NJ","Central New Jersey","Middlesex County","mid",40.4862,-74.4518),
    ("Perth Amboy","New Jersey","NJ","Central New Jersey","Middlesex County","mid",40.5068,-74.2654),
    ("Bayonne","New Jersey","NJ","Northeast New Jersey","Hudson County","mid",40.6688,-74.1132),
    ("Union City","New Jersey","NJ","Northeast New Jersey","Hudson County","mid",40.7651,-74.0268),
    ("Passaic","New Jersey","NJ","Northeast New Jersey","Passaic County","mid",40.8568,-74.1282),
    # NEW YORK additional
    ("Buffalo","New York","NY","Western New York","Erie County","major",42.8864,-78.8784),
    ("Rochester","New York","NY","Finger Lakes","Monroe County","major",43.1566,-77.6088),
    ("Syracuse","New York","NY","Central New York","Onondaga County","major",43.0481,-76.1474),
    ("Albany","New York","NY","Capital Region","Albany County","mid",42.6526,-73.7562),
    ("Utica","New York","NY","Mohawk Valley","Oneida County","mid",43.1009,-75.2327),
    ("Schenectady","New York","NY","Capital Region","Schenectady County","mid",42.8142,-73.9396),
    ("Troy","New York","NY","Capital Region","Rensselaer County","mid",42.7284,-73.6918),
    ("Binghamton","New York","NY","Southern Tier","Broome County","mid",42.0987,-75.9180),
    ("Ithaca","New York","NY","Finger Lakes","Tompkins County","mid",42.4440,-76.5021),
    ("Poughkeepsie","New York","NY","Hudson Valley","Dutchess County","mid",41.7004,-73.9209),
    ("Newburgh","New York","NY","Hudson Valley","Orange County","mid",41.5034,-74.0104),
    ("Middletown","New York","NY","Hudson Valley","Orange County","mid",41.4459,-74.4229),
    ("White Plains","New York","NY","New York Metro","Westchester County","mid",41.0340,-73.7629),
    ("Peekskill","New York","NY","Hudson Valley","Westchester County","mid",41.2948,-73.9218),
    # CALIFORNIA additional
    ("Fresno","California","CA","Central California","Fresno County","major",36.7378,-119.7871),
    ("Bakersfield","California","CA","Central California","Kern County","major",35.3733,-119.0187),
    ("Sacramento","California","CA","Central California","Sacramento County","major",38.5816,-121.4944),
    ("Stockton","California","CA","Central California","San Joaquin County","major",37.9577,-121.2908),
    ("Riverside","California","CA","Southern California","Riverside County","major",33.9533,-117.3962),
    ("Santa Ana","California","CA","Southern California","Orange County","major",33.7455,-117.8677),
    ("Anaheim","California","CA","Southern California","Orange County","major",33.8366,-117.9143),
    ("Irvine","California","CA","Southern California","Orange County","major",33.6839,-117.7947),
    ("Chula Vista","California","CA","Southern California","San Diego County","major",32.6401,-117.0842),
    ("Long Beach","California","CA","Southern California","Los Angeles County","major",33.7701,-118.1937),
    ("Oakland","California","CA","Northern California","Alameda County","major",37.8044,-122.2712),
    ("San Jose","California","CA","Northern California","Santa Clara County","major",37.3382,-121.8863),
    ("Fremont","California","CA","Northern California","Alameda County","major",37.5485,-121.9886),
    ("Modesto","California","CA","Central California","Stanislaus County","major",37.6391,-120.9969),
    ("Oxnard","California","CA","Southern California","Ventura County","major",34.1975,-119.1771),
    ("Moreno Valley","California","CA","Southern California","Riverside County","major",33.9425,-117.2297),
    ("Fontana","California","CA","Southern California","San Bernardino County","major",34.0922,-117.4350),
    ("Rancho Cucamonga","California","CA","Southern California","San Bernardino County","major",34.1064,-117.5931),
    ("Ontario","California","CA","Southern California","San Bernardino County","major",34.0633,-117.6509),
    ("Garden Grove","California","CA","Southern California","Orange County","major",33.7743,-117.9378),
    ("Oceanside","California","CA","Southern California","San Diego County","major",33.1959,-117.3795),
    ("Elk Grove","California","CA","Central California","Sacramento County","major",38.4088,-121.3716),
    ("Corona","California","CA","Southern California","Riverside County","major",33.8753,-117.5664),
    ("Salinas","California","CA","Central California","Monterey County","major",36.6777,-121.6555),
    ("Pomona","California","CA","Southern California","Los Angeles County","major",34.0551,-117.7500),
    ("Hayward","California","CA","Northern California","Alameda County","major",37.6688,-122.0808),
    ("Escondido","California","CA","Southern California","San Diego County","major",33.1192,-117.0864),
    ("Santa Rosa","California","CA","Northern California","Sonoma County","major",38.4404,-122.7141),
    ("Torrance","California","CA","Southern California","Los Angeles County","major",33.8358,-118.3406),
    ("Pasadena","California","CA","Southern California","Los Angeles County","major",34.1478,-118.1445),
    ("Fullerton","California","CA","Southern California","Orange County","major",33.8703,-117.9242),
    ("Orange","California","CA","Southern California","Orange County","major",33.7879,-117.8531),
    ("Santa Clarita","California","CA","Southern California","Los Angeles County","major",34.3917,-118.5426),
    ("Thousand Oaks","California","CA","Southern California","Ventura County","major",34.1706,-118.8376),
    ("Simi Valley","California","CA","Southern California","Ventura County","major",34.2694,-118.7815),
    ("Sunnyvale","California","CA","Northern California","Santa Clara County","major",37.3688,-122.0363),
    ("Visalia","California","CA","Central California","Tulare County","major",36.3302,-119.2921),
    # ILLINOIS additional
    ("Champaign","Illinois","IL","Central Illinois","Champaign County","mid",40.1164,-88.2434),
    ("Bloomington","Illinois","IL","Central Illinois","McLean County","mid",40.4842,-88.9937),
    ("Normal","Illinois","IL","Central Illinois","McLean County","mid",40.5142,-88.9906),
    ("Decatur","Illinois","IL","Central Illinois","Macon County","mid",39.8403,-88.9548),
    ("Moline","Illinois","IL","Quad Cities","Rock Island County","mid",41.5067,-90.5151),
    ("Rock Island","Illinois","IL","Quad Cities","Rock Island County","mid",41.5095,-90.5743),
    ("Galesburg","Illinois","IL","West Central Illinois","Knox County","mid",40.9478,-90.3712),
    ("Quincy","Illinois","IL","West Illinois","Adams County","mid",39.9356,-91.4099),
    ("Pekin","Illinois","IL","Central Illinois","Tazewell County","mid",40.5678,-89.6462),
    ("Kankakee","Illinois","IL","Northeast Illinois","Kankakee County","mid",41.1200,-87.8612),
    ("Danville","Illinois","IL","East Central Illinois","Vermilion County","mid",40.1242,-87.6300),
    ("Belleville","Illinois","IL","Southwest Illinois","St Clair County","mid",38.5200,-89.9840),
    ("East St Louis","Illinois","IL","Southwest Illinois","St Clair County","mid",38.6245,-90.1368),
    ("Collinsville","Illinois","IL","Southwest Illinois","Madison County","mid",38.6706,-89.9845),
]

print(f"Total cities in database: {len(ALL_US_CITIES)}")

# ============================================================
# STATE INFO FOR PAGES
# ============================================================

STATE_INFO = {
    'TX':{'emoji':'🤠','attraction1':'The Alamo in San Antonio','attraction2':'Space Center Houston','attraction3':'Big Bend National Park','food':'BBQ brisket, Tex-Mex, and kolaches','fact':'Texas was an independent republic from 1836 to 1846'},
    'FL':{'emoji':'🌴','attraction1':'Walt Disney World Resort','attraction2':'Everglades National Park','attraction3':'Kennedy Space Center Visitor Complex','food':'Key lime pie, Cuban sandwiches, and fresh stone crab','fact':'Florida has more golf courses per capita than any other state'},
    'GA':{'emoji':'🍑','attraction1':'Georgia Aquarium in Atlanta','attraction2':'World of Coca-Cola Museum','attraction3':'Savannah Historic District','food':'Georgia peaches, shrimp and grits, and sweet tea','fact':'Atlanta is home to more Fortune 500 companies than any other Southern city'},
    'NC':{'emoji':'🏔️','attraction1':'Great Smoky Mountains National Park','attraction2':'Blue Ridge Parkway','attraction3':'Outer Banks barrier islands','food':'Eastern style pulled pork BBQ and Krispy Kreme doughnuts','fact':'North Carolina is the birthplace of powered flight — the Wright Brothers flew at Kitty Hawk in 1903'},
    'TN':{'emoji':'🎸','attraction1':'Grand Ole Opry in Nashville','attraction2':'Dollywood theme park in Pigeon Forge','attraction3':'Graceland in Memphis','food':'Nashville hot chicken and Memphis dry-rub BBQ ribs','fact':'Tennessee is home to more than 3,900 documented caves and caverns'},
    'VA':{'emoji':'🏛️','attraction1':'Colonial Williamsburg living history museum','attraction2':'Shenandoah National Park','attraction3':'Arlington National Cemetery','food':'Virginia country ham and Chesapeake blue crab','fact':'Eight US Presidents were born in Virginia — more than any other state'},
    'AZ':{'emoji':'🌵','attraction1':'Grand Canyon National Park','attraction2':'Sedona Red Rocks formations','attraction3':'Antelope Canyon slot canyon tours','food':'Sonoran hot dogs and green chile dishes','fact':'Arizona is one of only two states that does not observe daylight saving time'},
    'CO':{'emoji':'⛰️','attraction1':'Rocky Mountain National Park','attraction2':'Red Rocks Amphitheatre near Denver','attraction3':'Mesa Verde National Park cliff dwellings','food':'Green chile and Colorado craft beer','fact':'Colorado has 58 mountain peaks over 14,000 feet — known as Fourteeners'},
    'WA':{'emoji':'🌲','attraction1':'Mount Rainier National Park','attraction2':'Pike Place Market in Seattle','attraction3':'Olympic National Park rainforest','food':'Dungeness crab, Pacific salmon, and Rainier cherries','fact':'Washington state produces more apples than any other state in America'},
    'MI':{'emoji':'🚗','attraction1':'Sleeping Bear Dunes National Lakeshore','attraction2':'Mackinac Island — no cars allowed','attraction3':'Henry Ford Museum of American Innovation','food':'Coney Island hot dogs and Vernors ginger ale','fact':'Michigan is the only state that touches four of the five Great Lakes'},
    'OH':{'emoji':'🏈','attraction1':'Rock and Roll Hall of Fame in Cleveland','attraction2':'Cedar Point amusement park in Sandusky','attraction3':'National Museum of the US Air Force','food':'Skyline chili and pierogies','fact':'Ohio has produced more US Presidents than any other state — eight total'},
    'IL':{'emoji':'🌆','attraction1':'Millennium Park and the Bean in Chicago','attraction2':'Navy Pier on Lake Michigan','attraction3':'Art Institute of Chicago','food':'Chicago deep dish pizza and Chicago-style hot dogs','fact':'Chicago is considered the birthplace of the modern skyscraper — built in 1885'},
    'PA':{'emoji':'🔔','attraction1':'Liberty Bell and Independence Hall in Philadelphia','attraction2':'Gettysburg National Military Park','attraction3':'Fallingwater by Frank Lloyd Wright','food':'Philly cheesesteak sandwiches and soft Amish pretzels','fact':'Pennsylvania was the site of the first commercial oil well in the world — drilled in 1859'},
    'IN':{'emoji':'🏎️','attraction1':'Indianapolis Motor Speedway — home of the Indy 500','attraction2':'Indiana Dunes National Park on Lake Michigan','attraction3':'Conner Prairie Interactive History Park','food':'Sugar cream pie and breaded pork tenderloin sandwiches','fact':'The Indianapolis 500 is the largest single-day sporting event in the entire world'},
    'MA':{'emoji':'🦞','attraction1':'Freedom Trail walking tour in Boston','attraction2':'Cape Cod National Seashore','attraction3':'Plymouth Rock and Mayflower II replica','food':'Boston cream pie, clam chowder, and lobster rolls','fact':'Massachusetts was home to the first public school in America — Boston Latin School, founded in 1635'},
    'MN':{'emoji':'❄️','attraction1':'Mall of America in Bloomington — the largest mall in the US','attraction2':'Boundary Waters Canoe Area Wilderness','attraction3':'Minnehaha Falls in Minneapolis','food':'Hotdish casseroles and the Juicy Lucy stuffed burger','fact':'Minnesota has over 11,000 lakes — earning its nickname Land of 10,000 Lakes'},
    'MO':{'emoji':'🌉','attraction1':'Gateway Arch in St Louis — tallest monument in the US','attraction2':'Branson entertainment district','attraction3':'Lake of the Ozarks resort area','food':'Kansas City BBQ burnt ends and St Louis toasted ravioli','fact':'Missouri is called the Gateway to the West — the historic jumping-off point for westward expansion'},
    'NV':{'emoji':'🎰','attraction1':'Las Vegas Strip entertainment corridor','attraction2':'Hoover Dam on the Nevada-Arizona border','attraction3':'Red Rock Canyon National Conservation Area','food':'Prime rib buffets and the original shrimp cocktail','fact':'Las Vegas has more hotel rooms than any other city in America'},
    'OR':{'emoji':'🌲','attraction1':'Crater Lake National Park — deepest lake in the US','attraction2':'Columbia River Gorge National Scenic Area','attraction3':'Haystack Rock at Cannon Beach','food':'Dungeness crab, Tillamook cheese, and Marionberry pie','fact':'Oregon is home to Crater Lake — at 1,943 feet it is the deepest lake in the United States'},
    'LA':{'emoji':'🎺','attraction1':'French Quarter in New Orleans','attraction2':'Garden District historic mansions','attraction3':'Bayou swamp tours near New Orleans','food':'Gumbo, jambalaya, crawfish etouffee, and beignets','fact':'New Orleans is widely considered the birthplace of jazz music'},
    'KY':{'emoji':'🏇','attraction1':'Mammoth Cave National Park — world\'s longest known cave system','attraction2':'Churchill Downs — home of the Kentucky Derby','attraction3':'Kentucky Bourbon Trail distillery tours','food':'Hot Brown open-faced sandwich and bourbon balls','fact':'Kentucky produces approximately 95 percent of the world\'s supply of bourbon whiskey'},
    'OK':{'emoji':'🌪️','attraction1':'Oklahoma City National Memorial and Museum','attraction2':'Gilcrease Museum of American Western art','attraction3':'Route 66 historic highway corridor','food':'Chicken fried steak and onion burgers','fact':'Oklahoma has more man-made lakes than any other state in America'},
    'SC':{'emoji':'🌺','attraction1':'Myrtle Beach Grand Strand resort area','attraction2':'Historic Charleston downtown district','attraction3':'Congaree National Park old-growth forest','food':'She-crab soup and Carolina pulled pork BBQ','fact':'South Carolina was the site of the first battle of the Civil War at Fort Sumter in 1861'},
    'AL':{'emoji':'🌹','attraction1':'US Space and Rocket Center in Huntsville','attraction2':'Gulf Shores and Orange Beach coastline','attraction3':'Birmingham Civil Rights Institute and District','food':'Conecuh sausage and white BBQ sauce','fact':'Alabama was the birthplace of the American Civil Rights Movement'},
    'MD':{'emoji':'🦀','attraction1':'National Harbor waterfront complex','attraction2':'Chesapeake Bay — largest estuary in America','attraction3':'Antietam National Battlefield Civil War site','food':'Maryland blue crab and Old Bay crab cakes','fact':'Maryland is home to the United States Naval Academy in Annapolis'},
    'WI':{'emoji':'🧀','attraction1':'Wisconsin Dells water park capital','attraction2':'Door County peninsula and islands','attraction3':'Lambeau Field in Green Bay — home of the Packers','food':'Squeaky cheese curds and Friday night fish fry','fact':'Wisconsin produces over 3 billion pounds of cheese annually — more than any other state'},
    'AR':{'emoji':'💎','attraction1':'Hot Springs National Park and Bathhouse Row','attraction2':'Crystal Bridges Museum of American Art','attraction3':'Buffalo National River — first national river in the US','food':'Fried catfish and delta tamales','fact':'Arkansas is the only US state with an active diamond mine open to the public'},
    'MS':{'emoji':'🎵','attraction1':'Mississippi Blues Trail historic markers','attraction2':'Natchez Trace Parkway scenic drive','attraction3':'Vicksburg National Military Park','food':'Mississippi mud pie and fried catfish','fact':'Mississippi is widely recognized as the birthplace of the blues music genre'},
    'IA':{'emoji':'🌽','attraction1':'Field of Dreams movie site in Dyersville','attraction2':'Iowa State Fair in Des Moines','attraction3':'Effigy Mounds National Monument','food':'Sweet corn on the cob and loose meat Maidrite sandwiches','fact':'Iowa produces more corn than any other state in America'},
    'KS':{'emoji':'🌾','attraction1':'Tallgrass Prairie National Preserve','attraction2':'Monument Rocks chalk formations','attraction3':'Flint Hills Scenic Byway','food':'Kansas City style BBQ and wheat-based foods','fact':'Kansas produces enough wheat annually to feed the entire world for two weeks'},
    'NJ':{'emoji':'🏖️','attraction1':'Jersey Shore boardwalks and beaches','attraction2':'Atlantic City casino boardwalk','attraction3':'Liberty State Park with Statue of Liberty views','food':'Taylor ham pork roll breakfast sandwiches','fact':'New Jersey is the most densely populated state in all of America'},
    'NY':{'emoji':'🗽','attraction1':'Statue of Liberty and Ellis Island','attraction2':'Times Square in Manhattan','attraction3':'Niagara Falls State Park','food':'New York pizza by the slice and everything bagels','fact':'New York City alone has more people than 40 of the 50 US states'},
    'CA':{'emoji':'🌞','attraction1':'Golden Gate Bridge in San Francisco','attraction2':'Yosemite National Park','attraction3':'Hollywood Walk of Fame in Los Angeles','food':'Fish tacos, avocado toast, and In-N-Out Burger','fact':'California has the fifth largest economy in the world — larger than the UK'},
    'UT':{'emoji':'🏜️','attraction1':'Zion National Park canyon hikes','attraction2':'Bryce Canyon National Park hoodoos','attraction3':'Arches National Park natural stone arches','food':'Funeral potatoes cheesy casserole and fry sauce','fact':'Utah has the highest literacy rate of any state in America'},
    'NM':{'emoji':'🌶️','attraction1':'White Sands National Park white dunes','attraction2':'Carlsbad Caverns National Park bat flights','attraction3':'Albuquerque International Balloon Fiesta','food':'Green chile cheeseburgers and sopaipillas with honey','fact':'New Mexico has more PhD scientists per capita than any other state in America'},
    'ID':{'emoji':'🥔','attraction1':'Craters of the Moon National Monument','attraction2':'Sun Valley world-class ski resort','attraction3':'Shoshone Falls — taller than Niagara Falls','food':'Idaho potatoes and fresh huckleberry products','fact':'Idaho produces about one-third of all potatoes grown in the United States'},
    'MT':{'emoji':'🦌','attraction1':'Glacier National Park going-to-the-sun road','attraction2':'Yellowstone National Park northern sections','attraction3':'Little Bighorn Battlefield National Monument','food':'Rocky Mountain oysters and huckleberry everything','fact':'Montana has more cattle than people — by a 3-to-1 ratio'},
    'AK':{'emoji':'🐻','attraction1':'Denali National Park and Preserve','attraction2':'Kenai Fjords National Park glaciers','attraction3':'Northern Lights aurora borealis viewing','food':'King salmon, Dungeness crab, and reindeer sausage','fact':'Alaska is larger than the next three biggest states combined — Texas, California, and Montana'},
    'HI':{'emoji':'🌺','attraction1':'Hawaii Volcanoes National Park active lava','attraction2':'Pearl Harbor National Memorial on Oahu','attraction3':'Na Pali Coast State Wilderness Park on Kauai','food':'Spam musubi, poke bowls, and shave ice','fact':'Hawaii is the only US state that is entirely composed of islands'},
    'WV':{'emoji':'🏔️','attraction1':'New River Gorge National Park','attraction2':'Harpers Ferry National Historical Park','attraction3':'Seneca Rocks rock climbing area','food':'Pepperoni rolls and buckwheat pancakes','fact':'West Virginia is the only state formed by seceding from a Confederate state during the Civil War'},
    'ND':{'emoji':'🦅','attraction1':'Theodore Roosevelt National Park badlands','attraction2':'International Peace Garden on the Canadian border','attraction3':'Fort Abraham Lincoln State Park','food':'Kuchen German cake and fleischkuechle fried meat pies','fact':'North Dakota produces more honey and sunflowers than any other state'},
    'SD':{'emoji':'🗿','attraction1':'Mount Rushmore National Memorial','attraction2':'Badlands National Park formations','attraction3':'Crazy Horse Memorial in progress','food':'Chislic fried lamb and Indian fry bread','fact':'South Dakota is home to the largest known indoor roller coaster collection in the world'},
    'WY':{'emoji':'🐃','attraction1':'Yellowstone National Park geysers and wildlife','attraction2':'Grand Teton National Park mountain views','attraction3':'Devils Tower National Monument','food':'Rocky Mountain trout and buffalo burgers','fact':'Wyoming was the first state to grant women the right to vote in 1869'},
    'NE':{'emoji':'🌽','attraction1':'Chimney Rock National Historic Site','attraction2':'Scotts Bluff National Monument','attraction3':'Henry Doorly Zoo and Aquarium in Omaha','food':'Runza pocket sandwiches and Valentino\'s pizza','fact':'Nebraska is the only state in America with a unicameral — single-chamber — state legislature'},
    'CT':{'emoji':'🏛️','attraction1':'Mark Twain House and Museum in Hartford','attraction2':'Yale University campus in New Haven','attraction3':'Mystic Seaport Museum','food':'New Haven style pizza and lobster rolls','fact':'Connecticut was the first state to enact laws governing the use of automobiles'},
    'NH':{'emoji':'🍂','attraction1':'Mount Washington — highest peak in Northeast','attraction2':'White Mountain National Forest','attraction3':'Hampton Beach boardwalk on the Atlantic','food':'Apple cider donuts and maple syrup products','fact':'New Hampshire was the first colony to establish its own government independent of Britain'},
    'ME':{'emoji':'🦞','attraction1':'Acadia National Park on Mount Desert Island','attraction2':'Portland Head Light historic lighthouse','attraction3':'Baxter State Park with Mount Katahdin','food':'Maine lobster rolls and wild blueberry pie','fact':'Maine produces 99 percent of all blueberries commercially grown in the United States'},
    'VT':{'emoji':'🍁','attraction1':'Ben and Jerry\'s factory tour in Waterbury','attraction2':'Stowe Mountain Resort ski area','attraction3':'Church Street Marketplace in Burlington','food':'Vermont maple syrup and artisan cheddar cheese','fact':'Vermont produces more maple syrup than any other state in America'},
    'RI':{'emoji':'⚓','attraction1':'The Breakers Vanderbilt mansion in Newport','attraction2':'Cliff Walk along Newport beaches','attraction3':'WaterFire Providence art installation','food':'Coffee milk, clam cakes, and chowder','fact':'Rhode Island is the smallest state in America but has the longest official state name'},
    'DE':{'emoji':'🦅','attraction1':'Dogfish Head Brewery craft beer tours','attraction2':'Cape Henlopen State Park beaches','attraction3':'Winterthur Museum and Garden','food':'Scrapple and boardwalk Thrasher\'s French fries','fact':'Delaware was the first state to ratify the US Constitution in 1787 — earning its nickname The First State'},
}

def get_state_info(abbr):
    return STATE_INFO.get(abbr, {
        'emoji': '📍',
        'attraction1': f'State parks and outdoor recreation areas',
        'attraction2': f'Historic downtown districts and museums',
        'attraction3': f'Local festivals and farmers markets',
        'food': f'Local cuisine and regional specialties',
        'fact': f'A wonderful place to live, work, and build a business'
    })

def make_slug(text):
    return text.lower().replace(' ','_').replace("'","").replace('.','').replace(',','').replace('/','')

def make_file_slug(city, abbr):
    city_slug = city.lower().replace(' ','-').replace("'","").replace('.','').replace(',','').replace('/','')
    return f"{city_slug}-{abbr.lower()}"

def get_state_slug(state):
    return state.lower().replace(' ','-')

# ============================================================
# PAGE TEMPLATE — maximum SEO, unique per city
# ============================================================

def build_page(city, state, abbr, region, county, tier, lat, lng):
    info = get_state_info(abbr)
    file_slug = make_file_slug(city, abbr)
    state_slug = get_state_slug(state)
    filename = f"{file_slug}.html"
    base_url = "https://dominionlocalbusinessdirectory.com"
    page_url = f"{base_url}/cities/{filename}"
    
    # Tier-based descriptors
    size_desc = {
        'major': 'one of the largest metropolitan areas',
        'mid': 'a thriving mid-size community',
        'small': 'a growing community',
        'tiny': 'a close-knit small town'
    }.get(tier, 'a community')
    
    # Unique intro paragraph per city
    intro = f"""{city} is {size_desc} in {region}, {state}. Located in {county}, {city} is home to thousands of local businesses serving residents, workers, and visitors across the area. From HVAC and plumbing contractors to restaurants, law firms, auto shops, and professional services — businesses in {city} rely on local visibility to attract new customers. The {region} area has a unique character shaped by its history, geography, and the people who call it home. Whether you are looking for a trusted local contractor, a great place to eat, or a professional service provider, Dominion Local Business Directory connects you to the businesses that make {city} thrive."""

    # LocalBusiness schema for featured Dominion listings
    lb_schema = json.dumps([
        {"@context":"https://schema.org","@type":"LocalBusiness","name":"Dominion Web Design Pro","url":"https://dominionwebdesignpro.com","telephone":"","address":{"@type":"PostalAddress","addressLocality":city,"addressRegion":abbr,"addressCountry":"US"},"geo":{"@type":"GeoCoordinates","latitude":lat,"longitude":lng},"aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"127"},"description":f"Professional websites for {city} businesses from $497. Custom design, SEO, mobile-ready, AI chat widget included.","priceRange":"$$","servesCuisine":"","sameAs":["https://dominionwebdesignpro.com"]},
        {"@context":"https://schema.org","@type":"LocalBusiness","name":"Dominion AI Agency","url":"https://dominionaiagency.com","telephone":"","address":{"@type":"PostalAddress","addressLocality":city,"addressRegion":abbr,"addressCountry":"US"},"geo":{"@type":"GeoCoordinates","latitude":lat,"longitude":lng},"aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"143"},"description":f"AI automation for {city} businesses — voice agents, CRM, lead generation, and digital marketing from $497/month.","priceRange":"$$"},
        {"@context":"https://schema.org","@type":"LocalBusiness","name":"AI Voice Agent Pros","url":"https://aivoiceagentpros.com","telephone":"","address":{"@type":"PostalAddress","addressLocality":city,"addressRegion":abbr,"addressCountry":"US"},"geo":{"@type":"GeoCoordinates","latitude":lat,"longitude":lng},"aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"98"},"description":f"AI voice agents that answer every call for {city} businesses 24 hours a day, 7 days a week. Never miss a lead again. From $297/month.","priceRange":"$$"}
    ], separators=(',',':'))

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{city} Business Directory | Local Businesses in {city}, {state} | Dominion</title>
<meta name="description" content="Find trusted local businesses in {city}, {state}. Browse HVAC, plumbing, restaurants, web design, AI services, and 50+ categories. Claim your free listing today at Dominion Local Business Directory.">
<meta name="keywords" content="{city} businesses, {city} {state} directory, local businesses {city}, HVAC {city}, restaurants {city}, web design {city}">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="canonical" href="{page_url}">
<meta property="og:title" content="{city}, {state} Business Directory | Dominion Local Business Directory">
<meta property="og:description" content="Find trusted local businesses in {city}, {state}. 50+ categories. Claim your free listing today.">
<meta property="og:url" content="{page_url}">
<meta property="og:type" content="website">
<meta property="og:image" content="{base_url}/og-image.png">
<meta name="geo.region" content="US-{abbr}">
<meta name="geo.placename" content="{city}, {state}">
<meta name="geo.position" content="{lat};{lng}">
<meta name="ICBM" content="{lat}, {lng}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"CollectionPage","name":"{city} Business Directory","description":"Find trusted local businesses in {city}, {state} across 50+ categories","url":"{page_url}","breadcrumb":{{"@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{base_url}"}},{{"@type":"ListItem","position":2,"name":"{state} Directory","item":"{base_url}/states/{state_slug}.html"}},{{"@type":"ListItem","position":3,"name":"{city}","item":"{page_url}"}}]}},"isPartOf":{{"@type":"WebSite","name":"Dominion Local Business Directory","url":"{base_url}"}}}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"How do I list my {city} business in the directory?","acceptedAnswer":{{"@type":"Answer","text":"Claiming your free listing in {city} is fast, easy, and completely free. Visit DominionLocalBusinessDirectory.com, click Claim Your Listing, and fill out your business info. No credit card required. Featured upgrades available from $97/month."}}}},{{"@type":"Question","name":"What local businesses are listed in {city}, {state}?","acceptedAnswer":{{"@type":"Answer","text":"We list HVAC contractors, plumbers, electricians, roofers, restaurants, auto repair shops, dentists, law firms, real estate agents, web designers, AI services, solar companies, and 50+ more local business categories in {city}, {state}."}}}},{{"@type":"Question","name":"How do I find the best HVAC company in {city}?","acceptedAnswer":{{"@type":"Answer","text":"Search the {city} directory for HVAC companies, review ratings and customer reviews, and claim your free listing if you own an HVAC business in {city}, {state}."}}}}]}}
</script>
<script type="application/ld+json">
{lb_schema}
</script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--navy:#0A1628;--navy2:#0F1E35;--gold:#C9A84C;--gold-light:#E8C97A;--gold-dark:#A8832A;--text:#F5F0E8;--muted:#8B9AB0;--border:#1E3050}}
body{{font-family:'Inter',system-ui,sans-serif;background:var(--navy);color:var(--text);line-height:1.6}}
a{{color:inherit;text-decoration:none}}
nav{{background:rgba(10,22,40,.98);border-bottom:1px solid rgba(201,168,76,.15);position:sticky;top:0;z-index:100;padding:0 24px}}
.nav-inner{{max-width:1400px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:68px}}
.logo-text{{font-family:'Playfair Display',serif;font-size:.95rem;font-weight:700;color:var(--gold-light)}}
.nav-cta{{background:linear-gradient(135deg,var(--gold),var(--gold-dark));color:var(--navy);font-weight:700;padding:9px 20px;border-radius:8px;font-size:.85rem}}
.hero{{background:linear-gradient(160deg,#0A1628,#0F1E35 50%,#0A1628);padding:64px 24px 48px;text-align:center}}
.breadcrumb{{font-size:.78rem;color:var(--muted);margin-bottom:14px}}
.breadcrumb a{{color:var(--gold)}}
h1{{font-family:'Playfair Display',serif;font-size:clamp(1.8rem,4vw,3rem);font-weight:900;margin-bottom:10px}}
h1 span{{color:var(--gold)}}
.hero-sub{{color:var(--muted);font-size:.9rem;margin-bottom:6px}}
.hero-coords{{color:rgba(139,154,176,.5);font-size:.72rem}}
.section{{max-width:1400px;margin:0 auto;padding:48px 24px}}
.sec-title{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;margin-bottom:8px}}
.sec-title span{{color:var(--gold)}}
.divider{{width:44px;height:3px;background:linear-gradient(90deg,var(--gold),var(--gold-dark));margin:10px 0 24px;border-radius:2px}}
.cat-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px;margin-bottom:36px}}
.cat-card{{background:var(--navy2);border:1px solid var(--border);border-radius:10px;padding:14px 10px;text-align:center;transition:.3s;cursor:pointer}}
.cat-card:hover{{border-color:var(--gold);transform:translateY(-2px)}}
.cat-icon{{font-size:1.5rem;margin-bottom:6px;display:block}}
.cat-name{{font-size:.75rem;font-weight:600}}
.biz-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}
.biz-card{{background:var(--navy2);border:1px solid var(--border);border-radius:14px;padding:20px;transition:.3s}}
.biz-card:hover{{border-color:var(--gold);transform:translateY(-3px)}}
.biz-card.premium{{border-color:rgba(201,168,76,.4)}}
.biz-category{{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--gold);margin-bottom:5px}}
.biz-name{{font-size:1rem;font-weight:700;margin-bottom:4px}}
.biz-location{{font-size:.8rem;color:var(--muted);margin-bottom:8px}}
.stars{{color:var(--gold);font-size:.82rem}}
.rating-row{{display:flex;align-items:center;gap:6px;margin-bottom:10px}}
.rating-num{{font-weight:700;font-size:.82rem}}
.review-count{{color:var(--muted);font-size:.75rem}}
.premium-tag{{display:inline-block;background:linear-gradient(135deg,var(--gold),var(--gold-dark));color:var(--navy);font-size:.65rem;font-weight:800;padding:2px 8px;border-radius:10px;margin-bottom:6px}}
.unclaimed-tag{{display:inline-block;background:rgba(255,255,255,.04);border:1px solid var(--border);color:var(--muted);font-size:.65rem;padding:2px 8px;border-radius:10px;margin-bottom:6px}}
.biz-desc{{color:var(--muted);font-size:.82rem;line-height:1.5;margin-bottom:12px}}
.biz-btn{{display:block;text-align:center;padding:9px;border-radius:7px;font-weight:700;font-size:.82rem;background:linear-gradient(135deg,var(--gold),var(--gold-dark));color:var(--navy);transition:.2s}}
.local-info{{background:var(--navy2);border:1px solid rgba(201,168,76,.15);border-radius:14px;padding:28px;margin-top:40px}}
.local-info h2{{font-family:'Playfair Display',serif;font-size:1.3rem;margin-bottom:14px}}
.local-info h2 span{{color:var(--gold)}}
.local-info p{{color:var(--muted);font-size:.9rem;margin-bottom:14px;line-height:1.8}}
.att-list{{list-style:none;display:flex;flex-direction:column;gap:6px;margin-bottom:16px}}
.att-list li{{display:flex;gap:8px;color:var(--muted);font-size:.86rem;line-height:1.5}}
.att-list li::before{{content:'★';color:var(--gold);flex-shrink:0}}
.claim-box{{background:linear-gradient(135deg,rgba(201,168,76,.08),rgba(201,168,76,.03));border:1px solid rgba(201,168,76,.2);border-radius:14px;padding:32px;text-align:center;margin-top:32px}}
.claim-box h2{{font-family:'Playfair Display',serif;font-size:1.4rem;margin-bottom:8px}}
.claim-box h2 span{{color:var(--gold)}}
.claim-box p{{color:var(--muted);margin-bottom:18px;font-size:.9rem}}
.claim-btn{{display:inline-block;background:linear-gradient(135deg,var(--gold),var(--gold-dark));color:var(--navy);font-weight:800;padding:13px 30px;border-radius:9px;font-size:.95rem}}
.tagline-bar{{background:linear-gradient(135deg,rgba(201,168,76,.08),rgba(201,168,76,.03));border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:24px 20px;text-align:center;margin-top:36px}}
footer{{background:var(--navy2);border-top:1px solid var(--border);padding:36px 24px 20px}}
.footer-inner{{max-width:1400px;margin:0 auto}}
.footer-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:24px;margin-bottom:20px}}
.footer-col h4{{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--gold);margin-bottom:10px}}
.footer-col a{{display:block;color:var(--muted);font-size:.82rem;margin-bottom:7px}}
.footer-col a:hover{{color:var(--gold)}}
.footer-bottom{{border-top:1px solid var(--border);padding-top:14px;font-size:.76rem;color:var(--muted);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="../index.html"><span class="logo-text">👑 Dominion Local Business Directory</span></a>
    <a href="../claim.html" class="nav-cta">List Your Business Free</a>
  </div>
</nav>
<div class="hero">
  <div class="breadcrumb"><a href="../index.html">Home</a> → <a href="../states/{state_slug}.html">{state}</a> → {city}</div>
  <h1>{info['emoji']} {city}, <span>{state}</span></h1>
  <p class="hero-sub">{region} · {county} · Local Business Directory</p>
  <p class="hero-coords">Latitude {lat:.4f} · Longitude {lng:.4f}</p>
</div>
<div class="section">
  <div class="sec-title">Browse <span>{city}</span> by Category</div>
  <div class="divider"></div>
  <div class="cat-grid">
    <div class="cat-card"><span class="cat-icon">🌡️</span><div class="cat-name">HVAC</div></div>
    <div class="cat-card"><span class="cat-icon">🔧</span><div class="cat-name">Plumbing</div></div>
    <div class="cat-card"><span class="cat-icon">⚡</span><div class="cat-name">Electrical</div></div>
    <div class="cat-card"><span class="cat-icon">🏠</span><div class="cat-name">Roofing</div></div>
    <div class="cat-card"><span class="cat-icon">🍽️</span><div class="cat-name">Restaurants</div></div>
    <div class="cat-card"><span class="cat-icon">🚗</span><div class="cat-name">Auto Repair</div></div>
    <div class="cat-card"><span class="cat-icon">🦷</span><div class="cat-name">Dentists</div></div>
    <div class="cat-card"><span class="cat-icon">⚖️</span><div class="cat-name">Law Firms</div></div>
    <div class="cat-card"><span class="cat-icon">🏡</span><div class="cat-name">Real Estate</div></div>
    <div class="cat-card"><span class="cat-icon">🌐</span><div class="cat-name">Web Design</div></div>
    <div class="cat-card"><span class="cat-icon">🤖</span><div class="cat-name">AI Services</div></div>
    <div class="cat-card"><span class="cat-icon">☀️</span><div class="cat-name">Solar</div></div>
    <div class="cat-card"><span class="cat-icon">💇</span><div class="cat-name">Salons</div></div>
    <div class="cat-card"><span class="cat-icon">🏥</span><div class="cat-name">Medical</div></div>
    <div class="cat-card"><span class="cat-icon">🐾</span><div class="cat-name">Veterinary</div></div>
    <div class="cat-card"><span class="cat-icon">🏋️</span><div class="cat-name">Fitness</div></div>
  </div>
  <div class="sec-title">Featured Businesses <span>in {city}</span></div>
  <div class="divider"></div>
  <div class="biz-grid">
    <div class="biz-card premium">
      <div class="premium-tag">⭐ PREMIUM MEMBER</div>
      <div class="biz-category">🌐 Web Design & Development</div>
      <div class="biz-name">Dominion Web Design Pro</div>
      <div class="biz-location">📍 Serving {city}, {abbr} & All 50 States</div>
      <div class="rating-row"><span class="stars">★★★★★</span><span class="rating-num">5.0</span><span class="review-count">(127 reviews)</span></div>
      <div class="biz-desc">Professional business websites from $497. We build your custom site first — you only pay when you love it. SEO ready, mobile first, AI chat included. Serving {city} businesses nationwide.</div>
      <a href="https://dominionwebdesignpro.com" target="_blank" rel="noopener" class="biz-btn">Visit Website →</a>
    </div>
    <div class="biz-card premium">
      <div class="premium-tag">⭐ PREMIUM MEMBER</div>
      <div class="biz-category">🤖 AI Automation Agency</div>
      <div class="biz-name">Dominion AI Agency</div>
      <div class="biz-location">📍 Serving {city}, {abbr} & All 50 States</div>
      <div class="rating-row"><span class="stars">★★★★★</span><span class="rating-num">5.0</span><span class="review-count">(143 reviews)</span></div>
      <div class="biz-desc">Full AI automation for {city} businesses — AI voice agents, CRM integration, automated lead generation, and reputation management. Everything from $497/month.</div>
      <a href="https://dominionaiagency.com" target="_blank" rel="noopener" class="biz-btn">Visit Website →</a>
    </div>
    <div class="biz-card premium">
      <div class="premium-tag">⭐ PREMIUM MEMBER</div>
      <div class="biz-category">📞 AI Voice Agents</div>
      <div class="biz-name">AI Voice Agent Pros</div>
      <div class="biz-location">📍 Serving {city}, {abbr} & All 50 States</div>
      <div class="rating-row"><span class="stars">★★★★★</span><span class="rating-num">5.0</span><span class="review-count">(98 reviews)</span></div>
      <div class="biz-desc">AI that answers every call for your {city} business — 24 hours a day, 7 days a week, 365 days a year. Qualifies leads, books appointments, takes messages. From $297/month.</div>
      <a href="https://aivoiceagentpros.com" target="_blank" rel="noopener" class="biz-btn">Visit Website →</a>
    </div>
    <div class="biz-card premium">
      <div class="premium-tag">⭐ PREMIUM MEMBER</div>
      <div class="biz-category">⭐ Review Management</div>
      <div class="biz-name">Dominion Review Pro</div>
      <div class="biz-location">📍 Serving {city}, {abbr} & All 50 States</div>
      <div class="rating-row"><span class="stars">★★★★★</span><span class="rating-num">5.0</span><span class="review-count">(76 reviews)</span></div>
      <div class="biz-desc">Automated Google review generation for {city} businesses. Get more 5-star reviews on autopilot — without begging customers. Proven system from $197/month.</div>
      <a href="https://dominionreviewpro.com" target="_blank" rel="noopener" class="biz-btn">Visit Website →</a>
    </div>
    <div class="biz-card premium">
      <div class="premium-tag">⭐ PREMIUM MEMBER</div>
      <div class="biz-category">☀️ Solar Energy</div>
      <div class="biz-name">Dominion Solar Pro</div>
      <div class="biz-location">📍 Serving {city}, {abbr} & All 50 States</div>
      <div class="rating-row"><span class="stars">★★★★★</span><span class="rating-num">5.0</span><span class="review-count">(54 reviews)</span></div>
      <div class="biz-desc">Solar panel installation for {city} homeowners and businesses. Reduce your energy bills with clean solar power. Free quotes, financing available, federal tax credits apply.</div>
      <a href="https://dominionsolarpro.com" target="_blank" rel="noopener" class="biz-btn">Visit Website →</a>
    </div>
    <div class="biz-card">
      <div class="unclaimed-tag">⚠️ Unclaimed Listing</div>
      <div class="biz-category">🌡️ HVAC Services</div>
      <div class="biz-name">{city} HVAC Professionals</div>
      <div class="biz-location">📍 {city}, {abbr}</div>
      <div class="rating-row"><span class="stars">★★★★★</span><span class="rating-num">4.8</span><span class="review-count">(94 reviews)</span></div>
      <div class="biz-desc">Is this your HVAC business in {city}? Claim this listing free and take control of how local customers find you online. No credit card required.</div>
      <a href="../claim.html" class="biz-btn">Claim This Listing Free →</a>
    </div>
    <div class="biz-card">
      <div class="unclaimed-tag">⚠️ Unclaimed Listing</div>
      <div class="biz-category">🔧 Plumbing Services</div>
      <div class="biz-name">{city} Plumbing Masters</div>
      <div class="biz-location">📍 {city}, {abbr}</div>
      <div class="rating-row"><span class="stars">★★★★½</span><span class="rating-num">4.7</span><span class="review-count">(67 reviews)</span></div>
      <div class="biz-desc">Is this your plumbing company in {city}? Claim this free listing and connect with customers searching for plumbers in {city}, {state} right now.</div>
      <a href="../claim.html" class="biz-btn">Claim This Listing Free →</a>
    </div>
    <div class="biz-card">
      <div class="unclaimed-tag">⚠️ Unclaimed Listing</div>
      <div class="biz-category">🍽️ Restaurants</div>
      <div class="biz-name">{city} Local Restaurant</div>
      <div class="biz-location">📍 {city}, {abbr}</div>
      <div class="rating-row"><span class="stars">★★★★★</span><span class="rating-num">4.9</span><span class="review-count">(203 reviews)</span></div>
      <div class="biz-desc">Own a restaurant in {city}? Get found by hungry locals searching online. Claim your free listing and start showing up where your customers are looking.</div>
      <a href="../claim.html" class="biz-btn">Claim This Listing Free →</a>
    </div>
  </div>
  <div class="local-info">
    <h2>About <span>{city}, {state}</span></h2>
    <p>{intro}</p>
    <p>Businesses in {city} that claim their free listing on Dominion Local Business Directory get visibility across search engines, the ability to showcase ratings and reviews, and direct connection to customers who are actively searching for local services. Featured listings receive premium placement, enhanced profiles, and priority visibility in {city} search results.</p>
    <h3 style="font-size:.95rem;font-weight:700;margin:18px 0 10px;color:var(--gold-light)">⭐ Top {state} Attractions Near {city}</h3>
    <ul class="att-list">
      <li>{info['attraction1']}</li>
      <li>{info['attraction2']}</li>
      <li>{info['attraction3']}</li>
    </ul>
    <p><strong style="color:var(--gold-light)">Local flavor:</strong> <span style="color:var(--muted)">{state} is known for {info['food']}.</span></p>
    <p style="margin-top:10px"><strong style="color:var(--gold-light)">Did you know?</strong> <span style="color:var(--muted)">{info['fact']}.</span></p>
  </div>
  <div class="claim-box">
    <h2>Own a Business in <span>{city}?</span></h2>
    <p>Join thousands of local business owners who have claimed their free listing. Get found by customers in {city} searching for your services — no credit card required to get started.</p>
    <a href="../claim.html" class="claim-btn">Claim Your Free {city} Listing →</a>
  </div>
  <div class="tagline-bar">
    <p style="font-size:1rem;font-weight:800;color:var(--text);margin-bottom:6px">👑 Want Dominion Over Your Market? Join Us.</p>
    <p style="color:var(--muted);font-size:.82rem;margin-bottom:10px">The Dominion family of brands helps local businesses grow through professional websites, AI automation, and reputation management.</p>
    <a href="../claim.html" style="color:var(--gold);font-size:.85rem;font-weight:600">Get Started Free — No Credit Card Required →</a>
  </div>
</div>
<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-col">
        <h4>Directory</h4>
        <a href="../index.html">Home</a>
        <a href="../states/{state_slug}.html">{state} Directory</a>
        <a href="../states.html">All 50 States</a>
        <a href="../categories.html">All Categories</a>
        <a href="../claim.html">Claim Your Listing</a>
      </div>
      <div class="footer-col">
        <h4>Dominion Brands</h4>
        <a href="https://dominionwebdesignpro.com" target="_blank" rel="noopener">Dominion Web Design Pro</a>
        <a href="https://dominionaiagency.com" target="_blank" rel="noopener">Dominion AI Agency</a>
        <a href="https://aivoiceagentpros.com" target="_blank" rel="noopener">AI Voice Agent Pros</a>
        <a href="https://dominionreviewpro.com" target="_blank" rel="noopener">Dominion Review Pro</a>
        <a href="https://dominionsolarpro.com" target="_blank" rel="noopener">Dominion Solar Pro</a>
      </div>
      <div class="footer-col">
        <h4>Popular Searches</h4>
        <a href="../categories.html">HVAC Companies</a>
        <a href="../categories.html">Plumbers</a>
        <a href="../categories.html">Restaurants</a>
        <a href="../categories.html">Auto Repair</a>
        <a href="../categories.html">Dentists</a>
      </div>
      <div class="footer-col">
        <h4>Resources</h4>
        <a href="../articles.html">Local Business Guides</a>
        <a href="../articles/texas.html">Texas Business Guide</a>
        <a href="https://dominionwebdesignpro.com" target="_blank" rel="noopener">Get a Website</a>
        <a href="https://aivoiceagentpros.com" target="_blank" rel="noopener">AI Receptionist</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2025 Dominion Local Business Directory · East Texas, USA</span>
      <span><a href="https://dominionaiagency.com" target="_blank" rel="noopener" style="color:var(--muted)">Part of the Dominion Brand Family</a></span>
    </div>
  </div>
</footer>
</body>
</html>'''

# ============================================================
# BUILD LOGIC
# ============================================================

def get_existing_slugs():
    existing = set()
    pattern = os.path.join(WORK_DIR, 'cities', '*.html')
    for f in glob.glob(pattern):
        existing.add(os.path.basename(f).replace('.html',''))
    return existing

def get_build_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"built_slugs": [], "total_built": 0, "last_run": None}

def save_build_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def update_sitemap():
    base = "https://dominionlocalbusinessdirectory.com"
    pages = [
        f"{base}/",
        f"{base}/claim.html",
        f"{base}/states.html",
        f"{base}/categories.html",
        f"{base}/articles.html",
        f"{base}/articles/texas.html",
    ]
    for f in sorted(glob.glob(os.path.join(WORK_DIR, 'states/*.html'))):
        rel = os.path.basename(f)
        pages.append(f"{base}/states/{rel}")
    for f in sorted(glob.glob(os.path.join(WORK_DIR, 'cities/*.html'))):
        rel = os.path.basename(f)
        pages.append(f"{base}/cities/{rel}")
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        depth = p.count('/')
        priority = '1.0' if p == f"{base}/" else '0.9' if depth <= 4 else '0.7'
        xml += f'<url><loc>{p}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>\n'
    xml += '</urlset>'
    
    with open(os.path.join(WORK_DIR, 'sitemap.xml'), 'w') as f:
        f.write(xml)
    
    print(f"Sitemap updated: {len(pages)} URLs")
    return len(pages)

def git_push(count_built, total):
    os.chdir(WORK_DIR)
    today = datetime.now().strftime('%Y-%m-%d')
    subprocess.run(['git', 'config', 'user.email', 'build@dominion.com'])
    subprocess.run(['git', 'config', 'user.name', 'Dominion Builder'])
    subprocess.run(['git', 'add', '-A'])
    result = subprocess.run(
        ['git', 'commit', '-m', f'Daily build {today}: +{count_built} city pages ({total} total)'],
        capture_output=True, text=True
    )
    if 'nothing to commit' in result.stdout:
        print("Nothing new to commit")
        return
    subprocess.run(['git', 'push', REPO_URL, 'main'])
    print(f"Pushed to GitHub: +{count_built} pages, {total} total")

def main():
    print(f"\n{'='*60}")
    print(f"Dominion City Builder — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    os.makedirs(os.path.join(WORK_DIR, 'cities'), exist_ok=True)
    
    existing_slugs = get_existing_slugs()
    print(f"Existing pages: {len(existing_slugs)}")
    
    # Find unbuilt cities
    unbuilt = []
    seen = set()
    for city_data in ALL_US_CITIES:
        city, state, abbr, region, county, tier, lat, lng = city_data
        slug = make_file_slug(city, abbr)
        if slug not in existing_slugs and slug not in seen:
            seen.add(slug)
            unbuilt.append(city_data)
    
    print(f"Unbuilt cities remaining: {len(unbuilt)}")
    
    if not unbuilt:
        print("All cities built! Database complete.")
        return
    
    # Build next batch
    batch = unbuilt[:CITIES_PER_DAY]
    built_count = 0
    
    for city_data in batch:
        city, state, abbr, region, county, tier, lat, lng = city_data
        slug = make_file_slug(city, abbr)
        filename = f"{slug}.html"
        filepath = os.path.join(WORK_DIR, 'cities', filename)
        
        try:
            html = build_page(city, state, abbr, region, county, tier, lat, lng)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            built_count += 1
            print(f"  ✓ {city}, {state}")
        except Exception as e:
            print(f"  ✗ {city}, {state}: {e}")
    
    total_pages = len(existing_slugs) + built_count
    sitemap_count = update_sitemap()
    git_push(built_count, total_pages)
    
    remaining = len(unbuilt) - built_count
    days_left = remaining // CITIES_PER_DAY + 1
    
    print(f"\n{'='*60}")
    print(f"Built today: {built_count}")
    print(f"Total city pages: {total_pages}")
    print(f"Sitemap URLs: {sitemap_count}")
    print(f"Remaining cities: {remaining}")
    print(f"Est. days to completion: {days_left}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
