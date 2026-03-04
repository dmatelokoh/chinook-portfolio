"""
generate_synthetic_data.py
==========================
Reads chinook.db and produces chinook_expanded.db with:
  - All original data preserved exactly
  - ~4,941 new synthetic customers (total ~5,000)
  - ~50,000+ invoices with seasonality and YoY growth
  - ~200,000+ invoice lines with genre affinity and price evolution

Run from the project root:
    python data_generation/generate_synthetic_data.py

See data_generation/assumptions.md for every design decision documented.
"""

import sqlite3
import shutil
import random
import math
import datetime
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# 0. Seeds — must be set before any random call
# ---------------------------------------------------------------------------
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DB = PROJECT_ROOT / "chinook.db"
DST_DB = PROJECT_ROOT / "chinook_expanded.db"

# ---------------------------------------------------------------------------
# 2. Name / address data (replaces faker — no network dependency)
#    Structured by country with culturally appropriate names.
# ---------------------------------------------------------------------------

# fmt: off
COUNTRY_DATA = {
    "USA": {
        "locale": "en_US",
        "first_names": ["James","John","Robert","Michael","William","David","Richard","Joseph","Thomas","Charles",
                        "Mary","Patricia","Jennifer","Linda","Barbara","Elizabeth","Susan","Jessica","Sarah","Karen",
                        "Emily","Matthew","Daniel","Anthony","Mark","Donald","Paul","Andrew","Joshua","Kevin",
                        "Ashley","Amanda","Stephanie","Melissa","Rebecca","Laura","Sharon","Cynthia","Kathleen","Amy"],
        "last_names": ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Taylor",
                       "Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Moore","Young","Allen",
                       "King","Wright","Scott","Torres","Nguyen","Hill","Flores","Green","Adams","Nelson"],
        "cities": ["New York","Los Angeles","Chicago","Houston","Phoenix","Philadelphia","San Antonio","San Diego",
                   "Dallas","San Jose","Austin","Jacksonville","Fort Worth","Columbus","Charlotte","Indianapolis",
                   "Seattle","Denver","Nashville","Portland","Las Vegas","Memphis","Louisville","Baltimore"],
        "states": ["NY","CA","IL","TX","AZ","PA","TX","CA","TX","CA","TX","FL","TX","OH","NC","IN","WA","CO","TN","OR","NV","TN","KY","MD"],
        "postal_fmt": lambda: f"{random.randint(10000,99999)}",
        "phone_fmt": lambda: f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
    },
    "Canada": {
        "locale": "en_CA",
        "first_names": ["Liam","Emma","Noah","Olivia","William","Ava","James","Isabella","Oliver","Sophia",
                        "Benjamin","Mia","Elijah","Charlotte","Lucas","Amelia","Mason","Harper","Logan","Evelyn",
                        "Ethan","Abigail","Jackson","Emily","Aiden","Elizabeth","Sebastian","Sofia","Jack","Avery"],
        "last_names": ["Smith","Brown","Tremblay","Martin","Roy","Wilson","MacDonald","Gagnon","Johnson","Taylor",
                       "Anderson","Leblanc","Lee","Bouchard","Thomas","Lavoie","Robinson","Fortin","Clarke","Cote"],
        "cities": ["Toronto","Montreal","Calgary","Ottawa","Edmonton","Mississauga","Winnipeg","Vancouver",
                   "Brampton","Hamilton","Surrey","Laval","Halifax","London","Markham","Vaughan","Gatineau","Saskatoon"],
        "states": ["ON","QC","AB","ON","AB","ON","MB","BC","ON","ON","BC","QC","NS","ON","ON","ON","QC","SK","ON","BC"],
        "postal_fmt": lambda: f"{random.choice('ABCEGHJKLMNPRSTVXY')}{random.randint(0,9)}{random.choice('ABCEGHJKLMNPRSTVWXYZ')} {random.randint(0,9)}{random.choice('ABCEGHJKLMNPRSTVWXYZ')}{random.randint(0,9)}",
        "phone_fmt": lambda: f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
    },
    "Brazil": {
        "locale": "pt_BR",
        "first_names": ["Miguel","Arthur","Heitor","Theo","Davi","Gabriel","Pedro","Matheus","Lucas","Benjamin",
                        "Maria","Sofia","Alice","Manuela","Isabela","Julia","Helena","Valentina","Laura","Beatriz",
                        "Rafael","Felipe","Gustavo","Rodrigo","Eduardo","Leonardo","Diego","Andre","Caio","Bruno"],
        "last_names": ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Alves","Pereira","Lima","Gomes",
                       "Costa","Ribeiro","Martins","Carvalho","Almeida","Lopes","Sousa","Fernandes","Vieira","Barbosa"],
        "cities": ["São Paulo","Rio de Janeiro","Brasília","Salvador","Fortaleza","Belo Horizonte","Manaus",
                   "Curitiba","Recife","Porto Alegre","Goiânia","Belém","Guarulhos","Campinas","São Luís"],
        "states": ["SP","RJ","DF","BA","CE","MG","AM","PR","PE","RS","GO","PA","SP","SP","MA"],
        "postal_fmt": lambda: f"{random.randint(10000,99999)}-{random.randint(100,999)}",
        "phone_fmt": lambda: f"+55 ({random.randint(11,99)}) {random.randint(90000,99999)}-{random.randint(1000,9999)}",
    },
    "France": {
        "locale": "fr_FR",
        "first_names": ["Gabriel","Leo","Raphael","Louis","Lucas","Hugo","Adam","Liam","Ethan","Nathan",
                        "Emma","Jade","Louise","Alice","Chloe","Inès","Lea","Manon","Camille","Zoe",
                        "Pierre","Antoine","Nicolas","Julien","Thomas","Alexandre","Maxime","Clement","Baptiste","Romain"],
        "last_names": ["Martin","Bernard","Thomas","Petit","Robert","Richard","Durand","Dubois","Moreau","Simon",
                       "Laurent","Lefebvre","Michel","Garcia","David","Bertrand","Roux","Vincent","Fournier","Morel"],
        "cities": ["Paris","Marseille","Lyon","Toulouse","Nice","Nantes","Strasbourg","Montpellier","Bordeaux",
                   "Lille","Rennes","Reims","Le Havre","Saint-Étienne","Toulon","Grenoble","Dijon","Angers","Nîmes"],
        "states": [None]*19,
        "postal_fmt": lambda: f"{random.randint(1,95):05d}",
        "phone_fmt": lambda: f"+33 {random.randint(1,9)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
    },
    "Germany": {
        "locale": "de_DE",
        "first_names": ["Luca","Finn","Leon","Jonas","Paul","Ben","Elias","Noah","Felix","Maximilian",
                        "Mia","Emma","Hannah","Sofia","Lena","Anna","Lea","Laura","Sara","Lina",
                        "Lukas","Jan","Tim","Markus","Stefan","Andreas","Michael","Klaus","Dieter","Wolfgang"],
        "last_names": ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Schulz","Hoffmann",
                       "Schäfer","Koch","Bauer","Richter","Klein","Wolf","Schröder","Neumann","Schwarz","Zimmermann"],
        "cities": ["Berlin","Hamburg","Munich","Cologne","Frankfurt","Stuttgart","Düsseldorf","Leipzig","Dortmund",
                   "Essen","Bremen","Dresden","Hanover","Nuremberg","Duisburg","Bochum","Wuppertal","Bielefeld"],
        "states": [None]*18,
        "postal_fmt": lambda: f"{random.randint(10000,99999)}",
        "phone_fmt": lambda: f"+49 {random.randint(30,9999)} {random.randint(100000,9999999)}",
    },
    "United Kingdom": {
        "locale": "en_GB",
        "first_names": ["Oliver","George","Harry","Jack","Noah","Charlie","Jacob","Alfie","Freddie","Oscar",
                        "Olivia","Amelia","Isla","Ava","Emily","Isabella","Mia","Poppy","Ella","Lily",
                        "James","William","Thomas","Samuel","Henry","Alexander","Edward","Daniel","Joshua","Benjamin"],
        "last_names": ["Smith","Jones","Williams","Taylor","Brown","Davies","Evans","Wilson","Thomas","Roberts",
                       "Johnson","Lewis","Walker","Robinson","Wood","Thompson","White","Watson","Jackson","Wright"],
        "cities": ["London","Birmingham","Leeds","Glasgow","Sheffield","Bradford","Manchester","Edinburgh",
                   "Liverpool","Bristol","Cardiff","Leicester","Sunderland","Belfast","Coventry","Brighton"],
        "states": [None]*16,
        "postal_fmt": lambda: f"{random.choice(['SW','SE','EC','WC','W','N','NW','E'])}{random.randint(1,20)} {random.randint(1,9)}{random.choice('ABCDEFGHJKLMNPQRSTUVWXY')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXY')}",
        "phone_fmt": lambda: f"+44 {random.randint(20,1999)} {random.randint(100000,9999999)}",
    },
    "Portugal": {
        "locale": "pt_PT",
        "first_names": ["João","Miguel","Tiago","Pedro","André","Ricardo","Bruno","Nuno","Hugo","Diogo",
                        "Ana","Maria","Sofia","Inês","Beatriz","Catarina","Mariana","Filipa","Joana","Rita"],
        "last_names": ["Silva","Santos","Ferreira","Pereira","Oliveira","Costa","Rodrigues","Martins","Jesus","Sousa",
                       "Fernandes","Gonçalves","Gomes","Lopes","Marques","Alves","Almeida","Ribeiro","Pinto","Carvalho"],
        "cities": ["Lisbon","Porto","Amadora","Braga","Setúbal","Coimbra","Funchal","Almada","Agualva-Cacém","Viseu"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000,9999)}-{random.randint(100,999)}",
        "phone_fmt": lambda: f"+351 {random.randint(200,999)} {random.randint(100000,9999999)}",
    },
    "Czech Republic": {
        "locale": "cs_CZ",
        "first_names": ["Jakub","Jan","Tomáš","Lukáš","Martin","Petr","Ondřej","David","Michal","Pavel",
                        "Tereza","Lucie","Jana","Petra","Eva","Kateřina","Martina","Veronika","Lenka","Monika"],
        "last_names": ["Novák","Svoboda","Novotný","Dvořák","Černý","Procházka","Krejčí","Blažek","Beneš","Pospíšil",
                       "Zelenka","Fiala","Kratochvíl","Horák","Nový","Horáček","Marek","Pokorný","Hájek","Šimánek"],
        "cities": ["Prague","Brno","Ostrava","Plzeň","Liberec","Olomouc","Ústí nad Labem","České Budějovice","Hradec Králové"],
        "states": [None]*9,
        "postal_fmt": lambda: f"{random.randint(100,799)} {random.randint(0,99):02d}",
        "phone_fmt": lambda: f"+420 {random.randint(600,999)} {random.randint(100,999)} {random.randint(100,999)}",
    },
    "India": {
        "locale": "en_IN",
        "first_names": ["Aarav","Vihaan","Sai","Arjun","Reyansh","Ayaan","Krishna","Ishaan","Shaurya","Atharv",
                        "Saanvi","Aadya","Kiara","Diya","Pari","Ananya","Riya","Anika","Aadhya","Myra",
                        "Rahul","Amit","Priya","Neha","Rohit","Vikram","Sunita","Deepak","Kavya","Suresh"],
        "last_names": ["Sharma","Verma","Patel","Singh","Kumar","Gupta","Shah","Mehta","Joshi","Nair",
                       "Reddy","Rao","Agarwal","Choudhary","Pandey","Mishra","Srivastava","Bose","Das","Malhotra"],
        "cities": ["Mumbai","Delhi","Bangalore","Hyderabad","Ahmedabad","Chennai","Kolkata","Surat","Pune","Jaipur",
                   "Lucknow","Kanpur","Nagpur","Indore","Thane","Bhopal","Visakhapatnam","Patna","Vadodara","Ghaziabad"],
        "states": ["MH","DL","KA","TS","GJ","TN","WB","GJ","MH","RJ","UP","UP","MH","MP","MH","MP","AP","BR","GJ","UP"],
        "postal_fmt": lambda: f"{random.randint(100000,999999)}",
        "phone_fmt": lambda: f"+91 {random.randint(70000,99999)}{random.randint(10000,99999)}",
    },
    "Australia": {
        "locale": "en_AU",
        "first_names": ["Oliver","William","Noah","Jack","Leo","Liam","Lucas","Henry","Ethan","James",
                        "Charlotte","Olivia","Ava","Amelia","Mia","Isla","Zoe","Grace","Sophie","Chloe"],
        "last_names": ["Smith","Jones","Williams","Brown","Wilson","Taylor","Johnson","White","Martin","Anderson",
                       "Thompson","Scott","Walker","Young","Harris","King","Clarke","Wright","Mitchell","Lee"],
        "cities": ["Sydney","Melbourne","Brisbane","Perth","Adelaide","Gold Coast","Newcastle","Canberra",
                   "Sunshine Coast","Wollongong","Hobart","Geelong","Townsville","Cairns","Darwin"],
        "states": ["NSW","VIC","QLD","WA","SA","QLD","NSW","ACT","QLD","NSW","TAS","VIC","QLD","QLD","NT"],
        "postal_fmt": lambda: f"{random.randint(2000,7999)}",
        "phone_fmt": lambda: f"+61 {random.randint(2,9)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
    },
    "Argentina": {
        "locale": "es_AR",
        "first_names": ["Mateo","Santiago","Thiago","Lautaro","Agustín","Benjamín","Nicolás","Franco","Tomás","Joaquín",
                        "Valentina","Camila","Sofia","Isabella","Florencia","Luciana","Martina","Paula","Micaela","Agustina"],
        "last_names": ["González","Rodríguez","Gómez","Fernández","López","Díaz","Martínez","Pérez","García","Sánchez",
                       "Romero","Sosa","Torres","Álvarez","Ruiz","Ramírez","Flores","Acosta","Medina","Aguirre"],
        "cities": ["Buenos Aires","Córdoba","Rosario","Mendoza","La Plata","Tucumán","Mar del Plata","Salta","Santa Fe","San Juan"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.randint(1000,9999)}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}",
        "phone_fmt": lambda: f"+54 11 {random.randint(3000,7999)}-{random.randint(1000,9999)}",
    },
    "Spain": {
        "locale": "es_ES",
        "first_names": ["Hugo","Mateo","Lucas","Alejandro","Daniel","Pablo","Álvaro","Adrián","Diego","Sergio",
                        "Lucía","Sofía","María","Martina","Paula","Valeria","Alba","Sara","Noa","Emma"],
        "last_names": ["García","González","Rodríguez","Fernández","López","Martínez","Sánchez","Pérez","Gómez","Martín",
                       "Jiménez","Ruiz","Hernández","Díaz","Moreno","Álvarez","Romero","Alonso","Gutiérrez","Navarro"],
        "cities": ["Madrid","Barcelona","Valencia","Seville","Zaragoza","Málaga","Murcia","Palma","Las Palmas","Bilbao"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1,52):05d}",
        "phone_fmt": lambda: f"+34 {random.randint(600,699)} {random.randint(100,999)} {random.randint(100,999)}",
    },
    "Italy": {
        "locale": "it_IT",
        "first_names": ["Leonardo","Francesco","Lorenzo","Alessandro","Mattia","Andrea","Gabriele","Tommaso","Riccardo","Edoardo",
                        "Sofia","Giulia","Aurora","Ginevra","Alice","Beatrice","Emma","Martina","Chiara","Sara"],
        "last_names": ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
                       "Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti"],
        "cities": ["Rome","Milan","Naples","Turin","Palermo","Genoa","Bologna","Florence","Bari","Catania","Venice","Verona"],
        "states": [None]*12,
        "postal_fmt": lambda: f"{random.randint(10000,99999)}",
        "phone_fmt": lambda: f"+39 {random.randint(2,99)} {random.randint(1000000,9999999)}",
    },
    "Netherlands": {
        "locale": "nl_NL",
        "first_names": ["Liam","Noah","Oliver","Lucas","Finn","Daan","Sem","Jesse","Luuk","Tim",
                        "Emma","Olivia","Ava","Mila","Nora","Sophie","Lotte","Julia","Anna","Fleur"],
        "last_names": ["De Jong","Jansen","De Vries","Van den Berg","Van Dijk","Bakker","Janssen","Visser","Smit","Meijer",
                       "De Boer","Mulder","De Groot","Bos","Vos","Peters","Hendriks","Van Leeuwen","Dekker","Brouwer"],
        "cities": ["Amsterdam","Rotterdam","The Hague","Utrecht","Eindhoven","Groningen","Tilburg","Almere","Breda","Nijmegen"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000,9999)} {random.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}",
        "phone_fmt": lambda: f"+31 {random.randint(6,88)} {random.randint(1000000,9999999)}",
    },
    "Chile": {
        "locale": "es_CL",
        "first_names": ["Mateo","Santiago","Benjamin","Nicolás","Diego","Sebastián","Ignacio","Tomás","Joaquín","Maximiliano",
                        "Sofía","Isabella","Valentina","Camila","Martina","Florencia","Isidora","Antonia","Catalina","Amanda"],
        "last_names": ["González","Muñoz","Rojas","Díaz","Pérez","Soto","Contreras","Silva","Martínez","Sepúlveda",
                       "Morales","Rodríguez","López","Fuentes","Hernández","Torres","Araya","Flores","Espinoza","Valenzuela"],
        "cities": ["Santiago","Valparaíso","Concepción","La Serena","Antofagasta","Temuco","Rancagua","Talca","Arica","Chillán"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000000,9999999)}",
        "phone_fmt": lambda: f"+56 9 {random.randint(10000000,99999999)}",
    },
    "Poland": {
        "locale": "pl_PL",
        "first_names": ["Jakub","Kacper","Filip","Mateusz","Bartosz","Michał","Piotr","Dawid","Łukasz","Kamil",
                        "Julia","Zofia","Zuzanna","Maja","Natalia","Aleksandra","Wiktoria","Klaudia","Martyna","Patrycja"],
        "last_names": ["Nowak","Kowalski","Wiśniewski","Wójcik","Kowalczyk","Kamiński","Lewandowski","Zieliński","Szymański","Woźniak",
                       "Dąbrowski","Kozłowski","Jankowski","Mazur","Wojciechowski","Kwiatkowski","Krawczyk","Piotrowiak","Grabowski","Nowakowski"],
        "cities": ["Warsaw","Kraków","Łódź","Wrocław","Poznań","Gdańsk","Szczecin","Bydgoszcz","Lublin","Katowice"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(10,99)}-{random.randint(100,999)}",
        "phone_fmt": lambda: f"+48 {random.randint(500,799)} {random.randint(100,999)} {random.randint(100,999)}",
    },
    "Ireland": {
        "locale": "en_IE",
        "first_names": ["Jack","James","Conor","Liam","Sean","Patrick","Daniel","Cian","Finn","Oisín",
                        "Emily","Sophie","Emma","Aoife","Sarah","Ciara","Niamh","Roisín","Saoirse","Caoimhe"],
        "last_names": ["Murphy","Kelly","O'Sullivan","Walsh","Smith","O'Brien","Byrne","Ryan","O'Connor","O'Neill",
                       "O'Reilly","Doyle","McCarthy","Gallagher","O'Doherty","Kennedy","Lynch","Murray","Quinn","Moore"],
        "cities": ["Dublin","Cork","Limerick","Galway","Waterford","Drogheda","Dundalk","Swords","Bray","Navan"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.choice('ACDEFHKNPRTVWXY')}{random.randint(10,99)} {random.choice('ACDEFHKNPRTVWXY')}{random.choice('ACDEFHKNPRTVWXY')}{random.randint(10,99)}",
        "phone_fmt": lambda: f"+353 {random.randint(1,99)} {random.randint(1000000,9999999)}",
    },
    "Sweden": {
        "locale": "sv_SE",
        "first_names": ["Lucas","Liam","Noah","William","Elias","Oliver","Oscar","Hugo","Alexander","Viktor",
                        "Emma","Alice","Maja","Elsa","Ella","Wilma","Ebba","Molly","Klara","Linnea"],
        "last_names": ["Johansson","Andersson","Karlsson","Nilsson","Eriksson","Larsson","Olsson","Persson","Svensson","Gustafsson",
                       "Pettersson","Jonsson","Jansson","Hansson","Bengtsson","Jönsson","Lindström","Jakobsson","Magnusson","Lindqvist"],
        "cities": ["Stockholm","Gothenburg","Malmö","Uppsala","Västerås","Örebro","Linköping","Helsingborg","Jönköping","Norrköping"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(10000,99999)}",
        "phone_fmt": lambda: f"+46 {random.randint(8,90)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}",
    },
    "Belgium": {
        "locale": "fr_BE",
        "first_names": ["Liam","Louis","Noah","Lucas","Nathan","Tom","Mathis","Rayan","Adam","Théo",
                        "Emma","Jade","Léa","Chloé","Lucie","Manon","Inès","Camille","Zoé","Maëlys"],
        "last_names": ["Peeters","Janssen","Maes","Jacobs","Willems","Claes","Goossens","Wouters","De Smedt","Claeys",
                       "Thomas","Dubois","Simon","Laurent","Michel","Lecomte","Renard","Dupont","Lambert","Henry"],
        "cities": ["Brussels","Antwerp","Ghent","Charleroi","Liège","Bruges","Namur","Leuven","Mons","Aalst"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000,9999)}",
        "phone_fmt": lambda: f"+32 {random.randint(2,99)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}",
    },
    "Norway": {
        "locale": "no_NO",
        "first_names": ["Oliver","Lucas","Liam","William","Filip","Emil","Isak","Mathias","Jakob","Noah",
                        "Emma","Nora","Sara","Sofie","Olivia","Maja","Emilie","Ingrid","Astrid","Sigrid"],
        "last_names": ["Hansen","Johansen","Olsen","Larsen","Andersen","Pedersen","Nilsen","Kristiansen","Jensen","Karlsen",
                       "Johnsen","Pettersen","Eriksen","Berg","Haugen","Hagen","Johannessen","Andreassen","Jacobsen","Dahl"],
        "cities": ["Oslo","Bergen","Trondheim","Stavanger","Drammen","Fredrikstad","Kristiansand","Sandnes","Tromsø","Sarpsborg"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000,9999)}",
        "phone_fmt": lambda: f"+47 {random.randint(40,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
    },
    "Finland": {
        "locale": "fi_FI",
        "first_names": ["Eino","Väinö","Onni","Oliver","Elias","Mikael","Aleksi","Lauri","Matias","Juhani",
                        "Emma","Aino","Sofia","Emilia","Olivia","Ella","Iida","Aada","Siiri","Hanna"],
        "last_names": ["Korhonen","Virtanen","Mäkinen","Nieminen","Mäkinen","Hämäläinen","Laine","Heikkinen","Koskinen","Järvinen",
                       "Lehtinen","Lehtonen","Saarinen","Salminen","Heinonen","Niemi","Heikkilä","Kinnunen","Turunen","Salo"],
        "cities": ["Helsinki","Espoo","Tampere","Vantaa","Oulu","Turku","Jyväskylä","Lahti","Kuopio","Pori"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(10000,99999)}",
        "phone_fmt": lambda: f"+358 {random.randint(40,50)} {random.randint(1000000,9999999)}",
    },
    "Denmark": {
        "locale": "da_DK",
        "first_names": ["William","Noah","Oscar","Liam","Oliver","Lucas","Emil","Alfred","Elias","Valdemar",
                        "Emma","Ida","Freja","Clara","Laura","Sofia","Anna","Maja","Ella","Astrid"],
        "last_names": ["Jensen","Nielsen","Hansen","Pedersen","Andersen","Christensen","Larsen","Sørensen","Rasmussen","Jørgensen",
                       "Petersen","Madsen","Kristensen","Olsen","Thomsen","Christiansen","Poulsen","Johansen","Møller","Mortensen"],
        "cities": ["Copenhagen","Aarhus","Odense","Aalborg","Frederiksberg","Esbjerg","Randers","Kolding","Horsens","Vejle"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000,9999)}",
        "phone_fmt": lambda: f"+45 {random.randint(20,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
    },
    "Austria": {
        "locale": "de_AT",
        "first_names": ["Luca","Jonas","Lukas","Felix","David","Niklas","Tobias","Florian","Manuel","Stefan",
                        "Hannah","Sophie","Lena","Anna","Laura","Lea","Lisa","Sarah","Julia","Marie"],
        "last_names": ["Gruber","Huber","Bauer","Wagner","Müller","Pichler","Steiner","Moser","Mayer","Hofer",
                       "Leitner","Berger","Fuchs","Auer","Ortner","Wimmer","Mayr","Schwarz","Brandstätter","Eder"],
        "cities": ["Vienna","Graz","Linz","Salzburg","Innsbruck","Klagenfurt","Villach","Wels","Sankt Pölten","Dornbirn"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1010,9999)}",
        "phone_fmt": lambda: f"+43 {random.randint(1,720)} {random.randint(100000,9999999)}",
    },
    "Hungary": {
        "locale": "hu_HU",
        "first_names": ["Bence","Péter","Dávid","Ádám","Máté","Balázs","László","Zsolt","Gábor","Tamás",
                        "Anna","Éva","Katalin","Zsófia","Réka","Nóra","Borbála","Erzsébet","Judit","Ágnes"],
        "last_names": ["Nagy","Kovács","Tóth","Szabó","Horváth","Varga","Kiss","Molnár","Németh","Farkas",
                       "Balogh","Papp","Takács","Juhász","Lakatos","Mészáros","Oláh","Simon","Rácz","Fekete"],
        "cities": ["Budapest","Debrecen","Miskolc","Pécs","Győr","Nyíregyháza","Kecskemét","Székesfehérvár","Szombathely","Érd"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000,9999)}",
        "phone_fmt": lambda: f"+36 {random.randint(20,70)} {random.randint(1000000,9999999)}",
    },
    "Mexico": {
        "locale": "es_MX",
        "first_names": ["Santiago","Mateo","Sebastián","Nicolás","Diego","Andrés","Emiliano","Daniel","Alejandro","Ricardo",
                        "Valentina","Regina","Mariana","Sofía","Isabella","Camila","Fernanda","Natalia","Andrea","Daniela"],
        "last_names": ["García","Rodríguez","Martínez","Hernández","López","González","Pérez","Sánchez","Ramírez","Cruz",
                       "Flores","Reyes","Rivera","Torres","Morales","Ortiz","Gutiérrez","Chávez","Ramos","Mendoza"],
        "cities": ["Mexico City","Guadalajara","Monterrey","Puebla","Tijuana","Juárez","León","Zapopan","Nezahualcóyotl","Mérida"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(1000,99999):05d}",
        "phone_fmt": lambda: f"+52 {random.randint(55,999)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
    },
    "Japan": {
        "locale": "ja_JP",
        "first_names": ["Haruto","Yuto","Sota","Yuki","Hayato","Ryusei","Kento","Shota","Daiki","Ren",
                        "Hina","Yuna","Riko","Mio","Sakura","Aoi","Haruka","Nana","Yui","Akari"],
        "last_names": ["Sato","Suzuki","Takahashi","Tanaka","Watanabe","Ito","Yamamoto","Nakamura","Kobayashi","Kato",
                       "Yoshida","Yamada","Sasaki","Yamaguchi","Saito","Matsumoto","Inoue","Kimura","Hayashi","Shimizu"],
        "cities": ["Tokyo","Yokohama","Osaka","Nagoya","Sapporo","Fukuoka","Kawasaki","Kobe","Kyoto","Saitama"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(100,999)}-{random.randint(1000,9999)}",
        "phone_fmt": lambda: f"+81 {random.randint(3,90)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
    },
    "Colombia": {
        "locale": "es_CO",
        "first_names": ["Santiago","Sebastián","Mateo","Samuel","Daniel","Nicolás","Alejandro","Andrés","Valentin","Esteban",
                        "Valentina","Isabella","Mariana","Sofía","Gabriela","Camila","Natalia","Sara","Juliana","Laura"],
        "last_names": ["García","Rodríguez","Martínez","González","López","Sánchez","Pérez","Vargas","Herrera","Castillo",
                       "Torres","Morales","Jiménez","Ruiz","Ramírez","Gómez","Díaz","Álvarez","Cruz","Ramos"],
        "cities": ["Bogotá","Medellín","Cali","Barranquilla","Cartagena","Cúcuta","Bucaramanga","Pereira","Santa Marta","Ibagué"],
        "states": [None]*10,
        "postal_fmt": lambda: f"{random.randint(100000,999999)}",
        "phone_fmt": lambda: f"+57 {random.randint(300,320)} {random.randint(1000000,9999999)}",
    },
}
# fmt: on

# Country weights (must sum to 1.0) — from assumptions.md Section 4a
COUNTRY_WEIGHTS = {
    "USA": 0.220, "Canada": 0.100, "Brazil": 0.085, "France": 0.080,
    "Germany": 0.070, "United Kingdom": 0.060, "Portugal": 0.035,
    "Czech Republic": 0.030, "India": 0.030, "Australia": 0.025,
    "Argentina": 0.020, "Spain": 0.020, "Italy": 0.020,
    "Netherlands": 0.015, "Chile": 0.015, "Poland": 0.015,
    "Ireland": 0.015, "Sweden": 0.015, "Belgium": 0.015,
    "Norway": 0.015, "Finland": 0.010, "Denmark": 0.010,
    "Austria": 0.010, "Hungary": 0.010,
    "Mexico": 0.007, "Japan": 0.007, "Colombia": 0.006,
}

COUNTRIES = list(COUNTRY_WEIGHTS.keys())
COUNTRY_WEIGHT_VALUES = [COUNTRY_WEIGHTS[c] for c in COUNTRIES]

# Year join-date weights — from assumptions.md Section 4c
YEAR_JOIN_WEIGHTS = {2019: 0.08, 2020: 0.10, 2021: 0.13, 2022: 0.16,
                     2023: 0.19, 2024: 0.20, 2025: 0.14}

# Seasonality multipliers — from assumptions.md Section 5c
SEASONALITY = {1: 0.95, 2: 0.85, 3: 0.90, 4: 0.90, 5: 0.95, 6: 0.80,
               7: 0.75, 8: 0.80, 9: 0.90, 10: 1.00, 11: 1.25, 12: 1.35}
MAX_SEASONALITY = max(SEASONALITY.values())  # 1.35

# YoY volume multipliers — from assumptions.md Section 5d
YEAR_VOLUME = {2019: 0.70, 2020: 0.80, 2021: 0.90, 2022: 1.00,
               2023: 1.05, 2024: 1.10, 2025: 1.10}

# Price evolution — from assumptions.md Section 8
PRICE_AUDIO = {2019: 0.99, 2020: 0.99, 2021: 0.99, 2022: 1.09, 2023: 1.19, 2024: 1.29, 2025: 1.49}
PRICE_VIDEO = {2019: 1.99, 2020: 1.99, 2021: 1.99, 2022: 2.19, 2023: 2.29, 2024: 2.39, 2025: 2.49}

# Employee support rep IDs from original data
SUPPORT_REP_IDS = [3, 4, 5]

DATA_END = datetime.date(2025, 12, 31)
DATA_START = datetime.date(2019, 1, 1)


# ---------------------------------------------------------------------------
# 3. Helpers
# ---------------------------------------------------------------------------

def weighted_choice(population, weights):
    """random.choices wrapper that returns a single item."""
    return random.choices(population, weights=weights, k=1)[0]


def random_date_in_year(year):
    """Return a random date within the given year (Jan 1 – Dec 28)."""
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 28)
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))


def generate_invoice_date(after: datetime.date, before: datetime.date) -> datetime.date:
    """
    Generate a random invoice date between after and before (exclusive),
    accepting/rejecting based on the seasonality multiplier and YoY volume.
    Returns None if no valid date found within max_attempts.
    """
    max_attempts = 200
    window = (before - after).days
    if window <= 1:
        return None
    for _ in range(max_attempts):
        delta = random.randint(1, window - 1)
        candidate = after + datetime.timedelta(days=delta)
        season_prob = SEASONALITY[candidate.month] / MAX_SEASONALITY
        year_prob = YEAR_VOLUME.get(candidate.year, 1.0)
        combined = season_prob * year_prob
        if random.random() < combined:
            return candidate
    return None


def generate_spaced_dates(join_date: datetime.date, n_invoices: int,
                          churn_date: datetime.date) -> list:
    """
    Generate n_invoices dates between join_date and churn_date using
    log-normal inter-purchase intervals with seasonal/YoY filtering.
    """
    dates = []
    current = join_date
    attempts = 0
    max_total_attempts = n_invoices * 50

    while len(dates) < n_invoices and attempts < max_total_attempts:
        attempts += 1
        # Log-normal interval: mean~3.5, sigma~0.6 in log-space → ~30-40 day gaps
        interval_days = int(np.random.lognormal(mean=3.5, sigma=0.6))
        interval_days = max(1, interval_days)
        candidate = current + datetime.timedelta(days=interval_days)

        if candidate > churn_date or candidate > DATA_END:
            break

        # Seasonal + YoY acceptance
        season_prob = SEASONALITY[candidate.month] / MAX_SEASONALITY
        year_prob = YEAR_VOLUME.get(candidate.year, 1.0)
        if random.random() < (season_prob * year_prob):
            # Keep day within valid range (1-28)
            candidate = candidate.replace(day=min(candidate.day, 28))
            dates.append(candidate)
            current = candidate

    return dates[:n_invoices]


def get_unit_price(base_price: float, year: int) -> float:
    """Return the evolved InvoiceLine unit price for a given year."""
    if base_price <= 1.0:
        return PRICE_AUDIO[year]
    else:
        return PRICE_VIDEO[year]


def make_email(first: str, last: str, country: str) -> str:
    """Generate a plausible email address."""
    domains = {
        "USA": ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com"],
        "Canada": ["gmail.com", "yahoo.ca", "outlook.com", "hotmail.ca"],
        "Brazil": ["gmail.com", "hotmail.com", "yahoo.com.br", "uol.com.br"],
        "France": ["gmail.com", "orange.fr", "free.fr", "sfr.fr", "laposte.net"],
        "Germany": ["gmail.com", "gmx.de", "web.de", "t-online.de", "yahoo.de"],
        "United Kingdom": ["gmail.com", "hotmail.co.uk", "outlook.com", "yahoo.co.uk", "btinternet.com"],
    }
    domain_list = domains.get(country, ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"])
    domain = random.choice(domain_list)
    sep = random.choice([".", "_", ""])
    suffix = str(random.randint(1, 999)) if random.random() < 0.4 else ""
    # Sanitise: lowercase, strip spaces, remove accents the simple way
    def clean(s):
        replacements = {
            'á':'a','à':'a','ã':'a','â':'a','ä':'a','å':'a',
            'é':'e','è':'e','ê':'e','ë':'e',
            'í':'i','ì':'i','î':'i','ï':'i',
            'ó':'o','ò':'o','õ':'o','ô':'o','ö':'o','ø':'o',
            'ú':'u','ù':'u','û':'u','ü':'u',
            'ý':'y','ÿ':'y','ñ':'n','ç':'c','ß':'ss','ł':'l',
            'ę':'e','ś':'s','ź':'z','ż':'z','ć':'c','ń':'n',
            'ő':'o','ű':'u','ă':'a','â':'a','î':'i','ș':'s','ț':'t',
        }
        s = s.lower()
        for k, v in replacements.items():
            s = s.replace(k, v)
        return ''.join(c for c in s if c.isalnum())
    f = clean(first)
    l = clean(last)
    local = f"{f}{sep}{l}{suffix}" if sep else f"{f}{l}{suffix}"
    return f"{local}@{domain}"


# ---------------------------------------------------------------------------
# 4. Genre affinity data
# ---------------------------------------------------------------------------

# Built after loading the DB — see build_genre_structures()
GENRE_NAMES = []          # list of genre names
GENRE_WEIGHTS = []        # primary genre selection weights
GENRE_NAME_TO_ID = {}     # name → GenreId
GENRE_TRACKS = {}         # GenreId → [TrackId, ...]
GENRE_TRACK_PRICES = {}   # TrackId → base UnitPrice

# Genre affinity matrix — from assumptions.md Section 7b
# Keys are genre names; values are lists of adjacent genre names.
# Genres not listed here fall through to "Others" (proportional draw).
AFFINITY_MAP = {
    "Rock":                ["Metal", "Alternative & Punk", "Blues"],
    "Metal":               ["Rock", "Alternative & Punk"],
    "Alternative & Punk":  ["Rock", "Metal", "Pop"],
    "Latin":               ["Pop", "R&B/Soul", "Reggae", "World"],
    "Jazz":                ["Blues", "Bossa Nova", "R&B/Soul"],
    "Blues":               ["Rock", "Jazz", "R&B/Soul"],
    "Pop":                 ["Rock", "R&B/Soul", "Latin", "Electronica/Dance"],
    "R&B/Soul":            ["Pop", "Jazz", "Hip Hop/Rap", "Latin"],
    "TV Shows":            ["Drama", "Sci Fi & Fantasy", "Comedy"],
    "Drama":               ["TV Shows", "Sci Fi & Fantasy"],
    "Classical":           ["Soundtrack", "Jazz", "Easy Listening"],
    "Electronica/Dance":   ["Pop", "Alternative & Punk", "Hip Hop/Rap"],
}

# Primary genre target weights (boosted for Rock per assumptions Section 7a)
PRIMARY_GENRE_WEIGHTS_RAW = {
    # Rock boosted to 46 (was 38) to hit 30-40% revenue share after price
    # evolution dilutes audio-track revenue in later years relative to video.
    "Rock": 46.0, "Latin": 14.0, "Metal": 10.0, "Alternative & Punk": 9.0,
    "TV Shows": 3.5, "Jazz": 3.0, "Blues": 2.8, "Drama": 2.2,
    "R&B/Soul": 2.2, "Classical": 1.5, "Electronica/Dance": 1.3,
    "Reggae": 1.0, "Pop": 1.0, "Hip Hop/Rap": 0.8, "Soundtrack": 0.7,
    "Sci Fi & Fantasy": 0.7, "World": 0.6, "Heavy Metal": 0.6,
    "Comedy": 0.5, "Easy Listening": 0.4, "Bossa Nova": 0.4,
    "Alternative": 0.4, "Rock And Roll": 0.3, "Science Fiction": 0.2,
}


def build_genre_structures(conn):
    """Populate module-level genre lookup tables from the database."""
    global GENRE_NAMES, GENRE_WEIGHTS, GENRE_NAME_TO_ID, GENRE_TRACKS, GENRE_TRACK_PRICES

    genres = conn.execute("SELECT GenreId, Name FROM Genre ORDER BY GenreId").fetchall()
    tracks = conn.execute("SELECT TrackId, GenreId, UnitPrice FROM Track").fetchall()

    GENRE_NAME_TO_ID = {name: gid for gid, name in genres}

    # Build track lists per genre
    GENRE_TRACKS = {gid: [] for gid, _ in genres}
    GENRE_TRACK_PRICES = {}
    for track_id, genre_id, price in tracks:
        GENRE_TRACKS[genre_id].append(track_id)
        GENRE_TRACK_PRICES[track_id] = price

    # Remove Opera from affinity targets (thin-catalog rule: 1 track)
    opera_id = GENRE_NAME_TO_ID.get("Opera")

    # Build ordered genre name/weight lists (skip Opera as primary)
    all_genre_names = []
    all_genre_raw_weights = []
    for gid, name in genres:
        if name == "Opera":
            continue  # Opera excluded from primary assignments
        track_count = len(GENRE_TRACKS.get(gid, []))
        if track_count == 0:
            continue
        all_genre_names.append(name)
        all_genre_raw_weights.append(PRIMARY_GENRE_WEIGHTS_RAW.get(name, 0.3))

    total_w = sum(all_genre_raw_weights)
    GENRE_NAMES = all_genre_names
    GENRE_WEIGHTS = [w / total_w for w in all_genre_raw_weights]


def pick_primary_genre() -> str:
    """Select a primary genre for a customer."""
    return weighted_choice(GENRE_NAMES, GENRE_WEIGHTS)


def pick_secondary_genre(primary: str) -> str:
    """Select a secondary genre based on the affinity matrix."""
    adjacents = AFFINITY_MAP.get(primary, [])
    # Filter to only genres that exist in our DB and have tracks
    valid = [g for g in adjacents
             if g in GENRE_NAME_TO_ID and len(GENRE_TRACKS.get(GENRE_NAME_TO_ID[g], [])) >= 10]
    if not valid:
        # Fallback: pick any genre proportionally (excluding primary)
        names = [g for g in GENRE_NAMES if g != primary]
        weights = [GENRE_WEIGHTS[GENRE_NAMES.index(g)] for g in names]
        return weighted_choice(names, weights)
    return random.choice(valid)


def pick_track_for_genre(genre_name: str) -> int:
    """Select a random track from the given genre."""
    gid = GENRE_NAME_TO_ID.get(genre_name)
    if not gid or not GENRE_TRACKS.get(gid):
        # Fallback to any track
        all_tracks = [tid for tracks in GENRE_TRACKS.values() for tid in tracks]
        return random.choice(all_tracks)
    return random.choice(GENRE_TRACKS[gid])


def pick_any_track() -> int:
    """Select a track from any genre proportionally (for the random-draw bucket)."""
    # Weighted by number of tracks in genre (more tracks → more likely to hit)
    all_tracks = [tid for tracks in GENRE_TRACKS.values() for tid in tracks]
    return random.choice(all_tracks)


def pick_track_for_invoice_line(primary_genre: str, secondary_genre: str) -> int:
    """
    Pick a track for one invoice line using the three-bucket affinity model:
    - 40–60% primary genre
    - 20–30% secondary genre
    - 15–35% any genre (random)
    """
    primary_pct = random.uniform(0.40, 0.60)
    secondary_pct = random.uniform(0.20, 0.30)
    # Normalise so the three buckets sum to 1
    total = primary_pct + secondary_pct + (1 - primary_pct - secondary_pct)
    roll = random.random()
    if roll < primary_pct:
        return pick_track_for_genre(primary_genre)
    elif roll < primary_pct + secondary_pct:
        return pick_track_for_genre(secondary_genre)
    else:
        return pick_any_track()


# ---------------------------------------------------------------------------
# 5. Customer generation
# ---------------------------------------------------------------------------

def generate_customer(customer_id: int) -> dict:
    """Generate one synthetic customer record."""
    country = weighted_choice(COUNTRIES, COUNTRY_WEIGHT_VALUES)
    cdata = COUNTRY_DATA[country]

    first = random.choice(cdata["first_names"])
    last = random.choice(cdata["last_names"])
    city = random.choice(cdata["cities"])

    # State: only set for countries that have them
    states = cdata.get("states", [None] * len(cdata["cities"]))
    city_idx = cdata["cities"].index(city) if city in cdata["cities"] else 0
    state = states[city_idx] if city_idx < len(states) else None

    postal = cdata["postal_fmt"]()
    phone = cdata["phone_fmt"]()
    street_num = random.randint(1, 9999)
    street_names = ["Main St","Oak Ave","Maple Dr","Park Blvd","Cedar Ln",
                    "Elm St","Pine Rd","Lake View","River Rd","Hill St",
                    "Church St","Market St","High St","Station Rd","King St"]
    address = f"{street_num} {random.choice(street_names)}"
    email = make_email(first, last, country)
    company = None
    if random.random() < 0.20:
        company_suffixes = ["Inc","LLC","Ltd","GmbH","S.A.","Corp","Co","Group","Solutions","Consulting"]
        company = f"{last} {random.choice(company_suffixes)}"
    support_rep = random.choice(SUPPORT_REP_IDS)

    # Join year
    years = list(YEAR_JOIN_WEIGHTS.keys())
    year_w = list(YEAR_JOIN_WEIGHTS.values())
    join_year = weighted_choice(years, year_w)
    join_date = random_date_in_year(join_year)

    # Churn type — from assumptions.md Section 9
    churn_roll = random.random()
    if churn_roll < 0.10:
        # Short-lived: churn 6–18 months after join
        churn_days = random.randint(180, 548)
        churn_date = join_date + datetime.timedelta(days=churn_days)
        churn_date = min(churn_date, DATA_END)
    elif churn_roll < 0.30:
        # At-risk: 50% chance of churning at a random point
        if random.random() < 0.50:
            active_days = (DATA_END - join_date).days
            churn_point = random.randint(int(active_days * 0.2), int(active_days * 0.9))
            churn_date = join_date + datetime.timedelta(days=churn_point)
        else:
            churn_date = DATA_END
    else:
        # Active: purchases until end of data
        churn_date = DATA_END

    # Purchase frequency — Gamma(shape=2.5, scale=5.5), clipped [1,55]
    # scale tuned to compensate for ~25% date-rejection from the seasonality
    # and YoY acceptance filter, targeting ~50k+ total invoices across 4,941
    # synthetic customers (requires ~10.2 accepted invoices/customer on average).
    raw_count = np.random.gamma(shape=2.5, scale=5.5)
    n_invoices = max(1, min(55, int(round(raw_count))))

    # Primary / secondary genre
    primary_genre = pick_primary_genre()
    secondary_genre = pick_secondary_genre(primary_genre)

    return {
        "CustomerId": customer_id,
        "FirstName": first,
        "LastName": last,
        "Company": company,
        "Address": address,
        "City": city,
        "State": state,
        "Country": country,
        "PostalCode": postal,
        "Phone": phone,
        "Fax": None,
        "Email": email,
        "SupportRepId": support_rep,
        # Internal — not written to DB
        "_join_date": join_date,
        "_churn_date": churn_date,
        "_n_invoices": n_invoices,
        "_primary_genre": primary_genre,
        "_secondary_genre": secondary_genre,
    }


# ---------------------------------------------------------------------------
# 6. Invoice + invoice line generation
# ---------------------------------------------------------------------------

def generate_invoices_for_customer(customer: dict, invoice_id_start: int,
                                   line_id_start: int):
    """
    Generate all invoices and invoice lines for a single customer.
    Returns (invoices_list, lines_list, next_invoice_id, next_line_id).
    """
    join_date = customer["_join_date"]
    churn_date = customer["_churn_date"]
    n_invoices = customer["_n_invoices"]
    primary = customer["_primary_genre"]
    secondary = customer["_secondary_genre"]
    cid = customer["CustomerId"]

    # Generate invoice dates
    dates = generate_spaced_dates(join_date, n_invoices, churn_date)
    if not dates:
        return [], [], invoice_id_start, line_id_start

    invoices = []
    lines = []
    inv_id = invoice_id_start
    line_id = line_id_start

    for inv_date in dates:
        year = inv_date.year

        # Lines per invoice: Poisson(4.5) + 1, capped at 14
        n_lines = min(14, max(1, int(np.random.poisson(4.5)) + 1))

        # Generate lines — track uniqueness within the invoice
        inv_lines = []
        used_tracks = set()
        for _ in range(n_lines):
            # Try to pick a unique track (max 10 attempts, then allow repeat)
            for attempt in range(10):
                track_id = pick_track_for_invoice_line(primary, secondary)
                if track_id not in used_tracks or attempt == 9:
                    break
            used_tracks.add(track_id)
            base_price = GENRE_TRACK_PRICES.get(track_id, 0.99)
            unit_price = get_unit_price(base_price, year)
            inv_lines.append({
                "InvoiceLineId": line_id,
                "InvoiceId": inv_id,
                "TrackId": track_id,
                "UnitPrice": round(unit_price, 2),
                "Quantity": 1,
            })
            line_id += 1

        total = round(sum(l["UnitPrice"] * l["Quantity"] for l in inv_lines), 2)

        invoices.append({
            "InvoiceId": inv_id,
            "CustomerId": cid,
            "InvoiceDate": inv_date.strftime("%Y-%m-%d %H:%M:%S"),
            "BillingAddress": customer["Address"],
            "BillingCity": customer["City"],
            "BillingState": customer["State"],
            "BillingCountry": customer["Country"],
            "BillingPostalCode": customer["PostalCode"],
            "Total": total,
        })
        lines.extend(inv_lines)
        inv_id += 1

    return invoices, lines, inv_id, line_id


# ---------------------------------------------------------------------------
# 7. Main — build the expanded database
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Chinook Synthetic Data Generator")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # Step 1: Copy original DB to destination
    # -----------------------------------------------------------------------
    print(f"\n[1/6] Copying {SRC_DB.name} → {DST_DB.name} ...")
    shutil.copy2(SRC_DB, DST_DB)
    print("      Done.")

    # -----------------------------------------------------------------------
    # Step 2: Load reference data from the new DB
    # -----------------------------------------------------------------------
    print("[2/6] Loading reference data from original database ...")
    conn = sqlite3.connect(DST_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    orig_max_customer = conn.execute("SELECT MAX(CustomerId) FROM Customer").fetchone()[0]
    orig_max_invoice = conn.execute("SELECT MAX(InvoiceId) FROM Invoice").fetchone()[0]
    orig_max_line = conn.execute("SELECT MAX(InvoiceLineId) FROM InvoiceLine").fetchone()[0]

    print(f"      Original: {orig_max_customer} customers, "
          f"{orig_max_invoice} invoices, {orig_max_line} invoice lines")

    build_genre_structures(conn)
    print(f"      Loaded {len(GENRE_NAMES)} genres, "
          f"{sum(len(v) for v in GENRE_TRACKS.values())} tracks")

    # -----------------------------------------------------------------------
    # Step 3: Generate customers
    # -----------------------------------------------------------------------
    N_NEW_CUSTOMERS = 4941  # brings total to exactly 5,000
    print(f"\n[3/6] Generating {N_NEW_CUSTOMERS} synthetic customers ...")

    customers = []
    for i in range(N_NEW_CUSTOMERS):
        cid = orig_max_customer + 1 + i
        customers.append(generate_customer(cid))
        if (i + 1) % 500 == 0:
            print(f"      {i + 1}/{N_NEW_CUSTOMERS} customers generated ...")

    print(f"      Done — {len(customers)} customers ready.")

    # -----------------------------------------------------------------------
    # Step 4: Generate invoices and invoice lines
    # -----------------------------------------------------------------------
    print(f"\n[4/6] Generating invoices and invoice lines ...")

    all_invoices = []
    all_lines = []
    inv_id = orig_max_invoice + 1
    line_id = orig_max_line + 1

    for idx, customer in enumerate(customers):
        invs, lns, inv_id, line_id = generate_invoices_for_customer(
            customer, inv_id, line_id
        )
        all_invoices.extend(invs)
        all_lines.extend(lns)
        if (idx + 1) % 500 == 0:
            print(f"      {idx + 1}/{N_NEW_CUSTOMERS} customers processed | "
                  f"{len(all_invoices):,} invoices | {len(all_lines):,} lines so far ...")

    print(f"      Done — {len(all_invoices):,} invoices, {len(all_lines):,} invoice lines.")

    # -----------------------------------------------------------------------
    # Step 5: Write to database
    # -----------------------------------------------------------------------
    print(f"\n[5/6] Writing synthetic data to {DST_DB.name} ...")

    # Insert customers
    customer_cols = ["CustomerId","FirstName","LastName","Company","Address","City",
                     "State","Country","PostalCode","Phone","Fax","Email","SupportRepId"]
    customer_rows = [tuple(c[col] for col in customer_cols) for c in customers]
    placeholders = ",".join(["?"] * len(customer_cols))
    conn.executemany(
        f"INSERT INTO Customer ({','.join(customer_cols)}) VALUES ({placeholders})",
        customer_rows
    )
    print(f"      Inserted {len(customer_rows):,} customers.")

    # Insert invoices in batches
    invoice_cols = ["InvoiceId","CustomerId","InvoiceDate","BillingAddress","BillingCity",
                    "BillingState","BillingCountry","BillingPostalCode","Total"]
    BATCH = 5000
    inv_rows = [tuple(inv[col] for col in invoice_cols) for inv in all_invoices]
    for start in range(0, len(inv_rows), BATCH):
        conn.executemany(
            f"INSERT INTO Invoice ({','.join(invoice_cols)}) VALUES ({','.join(['?']*len(invoice_cols))})",
            inv_rows[start:start + BATCH]
        )
    print(f"      Inserted {len(inv_rows):,} invoices.")

    # Insert invoice lines in batches
    line_cols = ["InvoiceLineId","InvoiceId","TrackId","UnitPrice","Quantity"]
    line_rows = [tuple(l[col] for col in line_cols) for l in all_lines]
    for start in range(0, len(line_rows), BATCH):
        conn.executemany(
            f"INSERT INTO InvoiceLine ({','.join(line_cols)}) VALUES ({','.join(['?']*len(line_cols))})",
            line_rows[start:start + BATCH]
        )
    print(f"      Inserted {len(line_rows):,} invoice lines.")

    conn.commit()

    # -----------------------------------------------------------------------
    # Step 6: Quick sanity checks before closing
    # -----------------------------------------------------------------------
    print(f"\n[6/6] Running quick sanity checks ...")

    total_customers = conn.execute("SELECT COUNT(*) FROM Customer").fetchone()[0]
    legacy_customers = conn.execute(
        f"SELECT COUNT(*) FROM Customer WHERE CustomerId <= {orig_max_customer}"
    ).fetchone()[0]
    total_invoices = conn.execute("SELECT COUNT(*) FROM Invoice").fetchone()[0]
    total_lines = conn.execute("SELECT COUNT(*) FROM InvoiceLine").fetchone()[0]
    fk_track = conn.execute(
        "SELECT COUNT(*) FROM InvoiceLine WHERE TrackId NOT IN (SELECT TrackId FROM Track)"
    ).fetchone()[0]
    fk_customer = conn.execute(
        "SELECT COUNT(*) FROM Invoice WHERE CustomerId NOT IN (SELECT CustomerId FROM Customer)"
    ).fetchone()[0]

    print(f"      Total customers  : {total_customers:,}  (expected ~5,000)")
    print(f"      Legacy customers : {legacy_customers}  (expected 59)")
    print(f"      Total invoices   : {total_invoices:,}  (expected 50,000+)")
    print(f"      Total lines      : {total_lines:,}  (expected 200,000+)")
    print(f"      FK violations (TrackId)   : {fk_track}  (expected 0)")
    print(f"      FK violations (CustomerId): {fk_customer}  (expected 0)")

    conn.close()

    print("\n" + "=" * 60)
    print(f"SUCCESS: {DST_DB.name} written.")
    print(f"Run the Data Validation Checklist (all 10 checks) to verify.")
    print("=" * 60)


if __name__ == "__main__":
    main()
