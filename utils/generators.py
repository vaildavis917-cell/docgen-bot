"""
Генераторы данных:
- Адреса
- Карты
- Антидетект данные
"""

import random
import string
import hashlib
import uuid
import json
from datetime import datetime, timedelta


# === ГЕНЕРАТОР АДРЕСОВ ===

# Базы данных адресов по странам
ADDRESS_DATA = {
    "us": {
        "country": "США",
        "flag": "🇺🇸",
        "cities": [
            {"city": "New York", "state": "NY", "zip_format": "100##"},
            {"city": "Los Angeles", "state": "CA", "zip_format": "900##"},
            {"city": "Chicago", "state": "IL", "zip_format": "606##"},
            {"city": "Houston", "state": "TX", "zip_format": "770##"},
            {"city": "Phoenix", "state": "AZ", "zip_format": "850##"},
            {"city": "Philadelphia", "state": "PA", "zip_format": "191##"},
            {"city": "San Antonio", "state": "TX", "zip_format": "782##"},
            {"city": "San Diego", "state": "CA", "zip_format": "921##"},
            {"city": "Dallas", "state": "TX", "zip_format": "752##"},
            {"city": "San Jose", "state": "CA", "zip_format": "951##"},
        ],
        "streets": ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St", "Washington Blvd", "Park Ave", "Lake Dr", "Hill Rd", "River St", "Forest Ave", "Sunset Blvd", "Broadway", "Market St"],
        "phone_format": "+1 (###) ###-####"
    },
    "uk": {
        "country": "Великобритания",
        "flag": "🇬🇧",
        "cities": [
            {"city": "London", "state": "England", "zip_format": "SW1A #AA"},
            {"city": "Manchester", "state": "England", "zip_format": "M1 #AA"},
            {"city": "Birmingham", "state": "England", "zip_format": "B1 #AA"},
            {"city": "Liverpool", "state": "England", "zip_format": "L1 #AA"},
            {"city": "Edinburgh", "state": "Scotland", "zip_format": "EH1 #AA"},
            {"city": "Glasgow", "state": "Scotland", "zip_format": "G1 #AA"},
            {"city": "Bristol", "state": "England", "zip_format": "BS1 #AA"},
            {"city": "Leeds", "state": "England", "zip_format": "LS1 #AA"},
        ],
        "streets": ["High Street", "Church Road", "Station Road", "Main Street", "Park Road", "London Road", "Victoria Street", "Green Lane", "Manor Road", "Kings Road"],
        "phone_format": "+44 ## #### ####"
    },
    "de": {
        "country": "Германия",
        "flag": "🇩🇪",
        "cities": [
            {"city": "Berlin", "state": "Berlin", "zip_format": "10###"},
            {"city": "Hamburg", "state": "Hamburg", "zip_format": "20###"},
            {"city": "München", "state": "Bayern", "zip_format": "80###"},
            {"city": "Köln", "state": "NRW", "zip_format": "50###"},
            {"city": "Frankfurt", "state": "Hessen", "zip_format": "60###"},
            {"city": "Stuttgart", "state": "BW", "zip_format": "70###"},
            {"city": "Düsseldorf", "state": "NRW", "zip_format": "40###"},
        ],
        "streets": ["Hauptstraße", "Bahnhofstraße", "Schulstraße", "Gartenstraße", "Dorfstraße", "Bergstraße", "Kirchstraße", "Waldstraße", "Ringstraße", "Lindenstraße"],
        "phone_format": "+49 ### #######"
    },
    "ua": {
        "country": "Украина",
        "flag": "🇺🇦",
        "cities": [
            {"city": "Київ", "state": "Київська обл.", "zip_format": "01###"},
            {"city": "Харків", "state": "Харківська обл.", "zip_format": "61###"},
            {"city": "Одеса", "state": "Одеська обл.", "zip_format": "65###"},
            {"city": "Дніпро", "state": "Дніпропетровська обл.", "zip_format": "49###"},
            {"city": "Львів", "state": "Львівська обл.", "zip_format": "79###"},
            {"city": "Запоріжжя", "state": "Запорізька обл.", "zip_format": "69###"},
        ],
        "streets": ["вул. Шевченка", "вул. Лесі Українки", "вул. Франка", "вул. Грушевського", "вул. Соборна", "вул. Центральна", "вул. Незалежності", "просп. Миру", "вул. Садова"],
        "phone_format": "+380 ## ### ## ##"
    },
    "ru": {
        "country": "Россия",
        "flag": "🇷🇺",
        "cities": [
            {"city": "Москва", "state": "Московская обл.", "zip_format": "1#####"},
            {"city": "Санкт-Петербург", "state": "Ленинградская обл.", "zip_format": "19####"},
            {"city": "Новосибирск", "state": "Новосибирская обл.", "zip_format": "63####"},
            {"city": "Екатеринбург", "state": "Свердловская обл.", "zip_format": "62####"},
            {"city": "Казань", "state": "Татарстан", "zip_format": "42####"},
            {"city": "Нижний Новгород", "state": "Нижегородская обл.", "zip_format": "60####"},
        ],
        "streets": ["ул. Ленина", "ул. Мира", "ул. Советская", "ул. Пушкина", "ул. Гагарина", "ул. Кирова", "просп. Победы", "ул. Центральная", "ул. Садовая"],
        "phone_format": "+7 (###) ###-##-##"
    },
    "pl": {
        "country": "Польша",
        "flag": "🇵🇱",
        "cities": [
            {"city": "Warszawa", "state": "Mazowieckie", "zip_format": "00-###"},
            {"city": "Kraków", "state": "Małopolskie", "zip_format": "30-###"},
            {"city": "Łódź", "state": "Łódzkie", "zip_format": "90-###"},
            {"city": "Wrocław", "state": "Dolnośląskie", "zip_format": "50-###"},
            {"city": "Poznań", "state": "Wielkopolskie", "zip_format": "60-###"},
            {"city": "Gdańsk", "state": "Pomorskie", "zip_format": "80-###"},
        ],
        "streets": ["ul. Główna", "ul. Kościelna", "ul. Szkolna", "ul. Ogrodowa", "ul. Polna", "ul. Leśna", "ul. Krótka", "ul. Parkowa", "ul. Słoneczna"],
        "phone_format": "+48 ### ### ###"
    },
    "fr": {
        "country": "Франция",
        "flag": "🇫🇷",
        "cities": [
            {"city": "Paris", "state": "Île-de-France", "zip_format": "75###"},
            {"city": "Marseille", "state": "PACA", "zip_format": "13###"},
            {"city": "Lyon", "state": "Auvergne-Rhône-Alpes", "zip_format": "69###"},
            {"city": "Toulouse", "state": "Occitanie", "zip_format": "31###"},
            {"city": "Nice", "state": "PACA", "zip_format": "06###"},
            {"city": "Nantes", "state": "Pays de la Loire", "zip_format": "44###"},
            {"city": "Bordeaux", "state": "Nouvelle-Aquitaine", "zip_format": "33###"},
        ],
        "streets": ["Rue de la Paix", "Avenue des Champs-Élysées", "Boulevard Saint-Germain", "Rue du Faubourg", "Place de la République", "Rue Victor Hugo", "Avenue de la Liberté", "Rue Nationale"],
        "phone_format": "+33 # ## ## ## ##"
    },
    "it": {
        "country": "Италия",
        "flag": "🇮🇹",
        "cities": [
            {"city": "Roma", "state": "Lazio", "zip_format": "00###"},
            {"city": "Milano", "state": "Lombardia", "zip_format": "20###"},
            {"city": "Napoli", "state": "Campania", "zip_format": "80###"},
            {"city": "Torino", "state": "Piemonte", "zip_format": "10###"},
            {"city": "Firenze", "state": "Toscana", "zip_format": "50###"},
            {"city": "Venezia", "state": "Veneto", "zip_format": "30###"},
            {"city": "Bologna", "state": "Emilia-Romagna", "zip_format": "40###"},
        ],
        "streets": ["Via Roma", "Via Garibaldi", "Via Dante", "Via Mazzini", "Corso Italia", "Via Nazionale", "Via Verdi", "Piazza del Duomo", "Via della Repubblica"],
        "phone_format": "+39 ### ### ####"
    },
    "es": {
        "country": "Испания",
        "flag": "🇪🇸",
        "cities": [
            {"city": "Madrid", "state": "Madrid", "zip_format": "28###"},
            {"city": "Barcelona", "state": "Cataluña", "zip_format": "08###"},
            {"city": "Valencia", "state": "Valencia", "zip_format": "46###"},
            {"city": "Sevilla", "state": "Andalucía", "zip_format": "41###"},
            {"city": "Zaragoza", "state": "Aragón", "zip_format": "50###"},
            {"city": "Málaga", "state": "Andalucía", "zip_format": "29###"},
            {"city": "Bilbao", "state": "País Vasco", "zip_format": "48###"},
        ],
        "streets": ["Calle Mayor", "Calle Real", "Avenida de la Constitución", "Paseo de Gracia", "Gran Vía", "Calle de Alcalá", "Rambla", "Plaza Mayor", "Calle del Carmen"],
        "phone_format": "+34 ### ### ###"
    },
    "ca": {
        "country": "Канада",
        "flag": "🇨🇦",
        "cities": [
            {"city": "Toronto", "state": "Ontario", "zip_format": "M#A #A#"},
            {"city": "Montreal", "state": "Quebec", "zip_format": "H#A #A#"},
            {"city": "Vancouver", "state": "British Columbia", "zip_format": "V#A #A#"},
            {"city": "Calgary", "state": "Alberta", "zip_format": "T#A #A#"},
            {"city": "Ottawa", "state": "Ontario", "zip_format": "K#A #A#"},
            {"city": "Edmonton", "state": "Alberta", "zip_format": "T#A #A#"},
        ],
        "streets": ["Main Street", "King Street", "Queen Street", "Yonge Street", "Bay Street", "Maple Avenue", "Oak Street", "Cedar Lane", "Pine Road"],
        "phone_format": "+1 (###) ###-####"
    },
    "au": {
        "country": "Австралия",
        "flag": "🇦🇺",
        "cities": [
            {"city": "Sydney", "state": "NSW", "zip_format": "2###"},
            {"city": "Melbourne", "state": "VIC", "zip_format": "3###"},
            {"city": "Brisbane", "state": "QLD", "zip_format": "4###"},
            {"city": "Perth", "state": "WA", "zip_format": "6###"},
            {"city": "Adelaide", "state": "SA", "zip_format": "5###"},
            {"city": "Gold Coast", "state": "QLD", "zip_format": "42##"},
        ],
        "streets": ["George Street", "King Street", "Queen Street", "Elizabeth Street", "Collins Street", "Bourke Street", "Pitt Street", "Market Street"],
        "phone_format": "+61 # #### ####"
    },
    "jp": {
        "country": "Япония",
        "flag": "🇯🇵",
        "cities": [
            {"city": "Tokyo", "state": "Tokyo", "zip_format": "1##-####"},
            {"city": "Osaka", "state": "Osaka", "zip_format": "5##-####"},
            {"city": "Kyoto", "state": "Kyoto", "zip_format": "6##-####"},
            {"city": "Yokohama", "state": "Kanagawa", "zip_format": "2##-####"},
            {"city": "Nagoya", "state": "Aichi", "zip_format": "4##-####"},
            {"city": "Sapporo", "state": "Hokkaido", "zip_format": "0##-####"},
        ],
        "streets": ["Shibuya", "Shinjuku", "Ginza", "Akihabara", "Harajuku", "Roppongi", "Ikebukuro", "Ueno"],
        "phone_format": "+81 ##-####-####"
    },
    "cn": {
        "country": "Китай",
        "flag": "🇨🇳",
        "cities": [
            {"city": "Beijing", "state": "Beijing", "zip_format": "100###"},
            {"city": "Shanghai", "state": "Shanghai", "zip_format": "200###"},
            {"city": "Guangzhou", "state": "Guangdong", "zip_format": "510###"},
            {"city": "Shenzhen", "state": "Guangdong", "zip_format": "518###"},
            {"city": "Chengdu", "state": "Sichuan", "zip_format": "610###"},
            {"city": "Hangzhou", "state": "Zhejiang", "zip_format": "310###"},
        ],
        "streets": ["Nanjing Road", "Wangfujing Street", "Huaihai Road", "Beijing Road", "Zhongshan Road", "Jiefang Road", "Renmin Road"],
        "phone_format": "+86 ### #### ####"
    },
    "br": {
        "country": "Бразилия",
        "flag": "🇧🇷",
        "cities": [
            {"city": "São Paulo", "state": "SP", "zip_format": "01###-###"},
            {"city": "Rio de Janeiro", "state": "RJ", "zip_format": "20###-###"},
            {"city": "Brasília", "state": "DF", "zip_format": "70###-###"},
            {"city": "Salvador", "state": "BA", "zip_format": "40###-###"},
            {"city": "Fortaleza", "state": "CE", "zip_format": "60###-###"},
            {"city": "Belo Horizonte", "state": "MG", "zip_format": "30###-###"},
        ],
        "streets": ["Avenida Paulista", "Rua Augusta", "Avenida Brasil", "Rua das Flores", "Avenida Atlântica", "Rua XV de Novembro", "Avenida Presidente Vargas"],
        "phone_format": "+55 ## #####-####"
    },
    "mx": {
        "country": "Мексика",
        "flag": "🇲🇽",
        "cities": [
            {"city": "Ciudad de México", "state": "CDMX", "zip_format": "0####"},
            {"city": "Guadalajara", "state": "Jalisco", "zip_format": "44###"},
            {"city": "Monterrey", "state": "Nuevo León", "zip_format": "64###"},
            {"city": "Puebla", "state": "Puebla", "zip_format": "72###"},
            {"city": "Tijuana", "state": "Baja California", "zip_format": "22###"},
            {"city": "Cancún", "state": "Quintana Roo", "zip_format": "77###"},
        ],
        "streets": ["Avenida Reforma", "Calle Juárez", "Avenida Insurgentes", "Calle Hidalgo", "Paseo de la Reforma", "Calle Morelos", "Avenida Revolución"],
        "phone_format": "+52 ## #### ####"
    },
    "in": {
        "country": "Индия",
        "flag": "🇮🇳",
        "cities": [
            {"city": "Mumbai", "state": "Maharashtra", "zip_format": "400###"},
            {"city": "Delhi", "state": "Delhi", "zip_format": "110###"},
            {"city": "Bangalore", "state": "Karnataka", "zip_format": "560###"},
            {"city": "Chennai", "state": "Tamil Nadu", "zip_format": "600###"},
            {"city": "Kolkata", "state": "West Bengal", "zip_format": "700###"},
            {"city": "Hyderabad", "state": "Telangana", "zip_format": "500###"},
        ],
        "streets": ["MG Road", "Brigade Road", "Park Street", "Linking Road", "Commercial Street", "Anna Salai", "Connaught Place"],
        "phone_format": "+91 ##### #####"
    },
    "kr": {
        "country": "Южная Корея",
        "flag": "🇰🇷",
        "cities": [
            {"city": "Seoul", "state": "Seoul", "zip_format": "0####"},
            {"city": "Busan", "state": "Busan", "zip_format": "4####"},
            {"city": "Incheon", "state": "Incheon", "zip_format": "2####"},
            {"city": "Daegu", "state": "Daegu", "zip_format": "4####"},
            {"city": "Daejeon", "state": "Daejeon", "zip_format": "3####"},
            {"city": "Gwangju", "state": "Gwangju", "zip_format": "6####"},
        ],
        "streets": ["Gangnam-daero", "Teheran-ro", "Jongno", "Myeongdong-gil", "Itaewon-ro", "Hongdae", "Apgujeong-ro"],
        "phone_format": "+82 ##-####-####"
    },
    "nl": {
        "country": "Нидерланды",
        "flag": "🇳🇱",
        "cities": [
            {"city": "Amsterdam", "state": "Noord-Holland", "zip_format": "10## AA"},
            {"city": "Rotterdam", "state": "Zuid-Holland", "zip_format": "30## AA"},
            {"city": "Den Haag", "state": "Zuid-Holland", "zip_format": "25## AA"},
            {"city": "Utrecht", "state": "Utrecht", "zip_format": "35## AA"},
            {"city": "Eindhoven", "state": "Noord-Brabant", "zip_format": "56## AA"},
        ],
        "streets": ["Kalverstraat", "Damrak", "Leidsestraat", "Prinsengracht", "Herengracht", "Keizersgracht", "Rokin"],
        "phone_format": "+31 # ########"
    },
    "se": {
        "country": "Швеция",
        "flag": "🇸🇪",
        "cities": [
            {"city": "Stockholm", "state": "Stockholm", "zip_format": "1## ##"},
            {"city": "Göteborg", "state": "Västra Götaland", "zip_format": "4## ##"},
            {"city": "Malmö", "state": "Skåne", "zip_format": "2## ##"},
            {"city": "Uppsala", "state": "Uppsala", "zip_format": "7## ##"},
        ],
        "streets": ["Drottninggatan", "Kungsgatan", "Sveavagen", "Storgatan", "Vasagatan", "Birger Jarlsgatan"],
        "phone_format": "+46 ## ### ## ##"
    },
    "ch": {
        "country": "Швейцария",
        "flag": "🇨🇭",
        "cities": [
            {"city": "Zürich", "state": "Zürich", "zip_format": "80##"},
            {"city": "Geneva", "state": "Genève", "zip_format": "12##"},
            {"city": "Basel", "state": "Basel-Stadt", "zip_format": "40##"},
            {"city": "Bern", "state": "Bern", "zip_format": "30##"},
            {"city": "Lausanne", "state": "Vaud", "zip_format": "10##"},
        ],
        "streets": ["Bahnhofstrasse", "Rue du Rhône", "Freie Strasse", "Marktgasse", "Kramgasse", "Spitalgasse"],
        "phone_format": "+41 ## ### ## ##"
    },
    "at": {
        "country": "Австрия",
        "flag": "🇦🇹",
        "cities": [
            {"city": "Wien", "state": "Wien", "zip_format": "1###"},
            {"city": "Graz", "state": "Steiermark", "zip_format": "80##"},
            {"city": "Linz", "state": "Oberösterreich", "zip_format": "40##"},
            {"city": "Salzburg", "state": "Salzburg", "zip_format": "50##"},
            {"city": "Innsbruck", "state": "Tirol", "zip_format": "60##"},
        ],
        "streets": ["Kärntner Straße", "Mariahilfer Straße", "Graben", "Ringstraße", "Herrengasse", "Landstraße"],
        "phone_format": "+43 ### #######"
    },
    "be": {
        "country": "Бельгия",
        "flag": "🇧🇪",
        "cities": [
            {"city": "Brussels", "state": "Brussels", "zip_format": "1###"},
            {"city": "Antwerp", "state": "Antwerpen", "zip_format": "2###"},
            {"city": "Ghent", "state": "Oost-Vlaanderen", "zip_format": "9###"},
            {"city": "Bruges", "state": "West-Vlaanderen", "zip_format": "8###"},
            {"city": "Liège", "state": "Liège", "zip_format": "4###"},
        ],
        "streets": ["Grand Place", "Rue Neuve", "Avenue Louise", "Meir", "Veldstraat", "Rue de la Loi"],
        "phone_format": "+32 ### ## ## ##"
    },
    "pt": {
        "country": "Португалия",
        "flag": "🇵🇹",
        "cities": [
            {"city": "Lisboa", "state": "Lisboa", "zip_format": "1###-###"},
            {"city": "Porto", "state": "Porto", "zip_format": "4###-###"},
            {"city": "Braga", "state": "Braga", "zip_format": "47##-###"},
            {"city": "Coimbra", "state": "Coimbra", "zip_format": "30##-###"},
            {"city": "Faro", "state": "Faro", "zip_format": "80##-###"},
        ],
        "streets": ["Avenida da Liberdade", "Rua Augusta", "Rua de Santa Catarina", "Avenida dos Aliados", "Rua Garrett"],
        "phone_format": "+351 ### ### ###"
    },
    "no": {
        "country": "Норвегия",
        "flag": "🇳🇴",
        "cities": [
            {"city": "Oslo", "state": "Oslo", "zip_format": "0###"},
            {"city": "Bergen", "state": "Vestland", "zip_format": "5###"},
            {"city": "Trondheim", "state": "Trøndelag", "zip_format": "7###"},
            {"city": "Stavanger", "state": "Rogaland", "zip_format": "4###"},
        ],
        "streets": ["Karl Johans gate", "Storgata", "Torggata", "Grünerløkka", "Bogstadveien"],
        "phone_format": "+47 ### ## ###"
    },
    "dk": {
        "country": "Дания",
        "flag": "🇩🇰",
        "cities": [
            {"city": "Copenhagen", "state": "Hovedstaden", "zip_format": "1###"},
            {"city": "Aarhus", "state": "Midtjylland", "zip_format": "8###"},
            {"city": "Odense", "state": "Syddanmark", "zip_format": "5###"},
            {"city": "Aalborg", "state": "Nordjylland", "zip_format": "9###"},
        ],
        "streets": ["Strøget", "Nørrebrogade", "Vesterbrogade", "Østerbrogade", "Amagerbrogade"],
        "phone_format": "+45 ## ## ## ##"
    },
    "fi": {
        "country": "Финляндия",
        "flag": "🇫🇮",
        "cities": [
            {"city": "Helsinki", "state": "Uusimaa", "zip_format": "00###"},
            {"city": "Espoo", "state": "Uusimaa", "zip_format": "02###"},
            {"city": "Tampere", "state": "Pirkanmaa", "zip_format": "33###"},
            {"city": "Turku", "state": "Varsinais-Suomi", "zip_format": "20###"},
        ],
        "streets": ["Mannerheimintie", "Aleksanterinkatu", "Esplanadi", "Hämeenkatu", "Keskuskatu"],
        "phone_format": "+358 ## ### ####"
    },
    "cz": {
        "country": "Чехия",
        "flag": "🇨🇿",
        "cities": [
            {"city": "Praha", "state": "Praha", "zip_format": "1## ##"},
            {"city": "Brno", "state": "Jihomoravský", "zip_format": "6## ##"},
            {"city": "Ostrava", "state": "Moravskoslezský", "zip_format": "7## ##"},
            {"city": "Plzeň", "state": "Plzeňský", "zip_format": "3## ##"},
        ],
        "streets": ["Václavské náměstí", "Národní třída", "Karlova", "Pražská", "Masarykova"],
        "phone_format": "+420 ### ### ###"
    },
    "tr": {
        "country": "Турция",
        "flag": "🇹🇷",
        "cities": [
            {"city": "Istanbul", "state": "Istanbul", "zip_format": "34###"},
            {"city": "Ankara", "state": "Ankara", "zip_format": "06###"},
            {"city": "Izmir", "state": "Izmir", "zip_format": "35###"},
            {"city": "Antalya", "state": "Antalya", "zip_format": "07###"},
            {"city": "Bursa", "state": "Bursa", "zip_format": "16###"},
        ],
        "streets": ["Istiklal Caddesi", "Bağdat Caddesi", "Atatürk Bulvarı", "Cumhuriyet Caddesi", "Koreşehitler Caddesi"],
        "phone_format": "+90 ### ### ## ##"
    },
    "ae": {
        "country": "ОАЭ",
        "flag": "🇦🇪",
        "cities": [
            {"city": "Dubai", "state": "Dubai", "zip_format": "#####"},
            {"city": "Abu Dhabi", "state": "Abu Dhabi", "zip_format": "#####"},
            {"city": "Sharjah", "state": "Sharjah", "zip_format": "#####"},
            {"city": "Ajman", "state": "Ajman", "zip_format": "#####"},
        ],
        "streets": ["Sheikh Zayed Road", "Jumeirah Beach Road", "Al Wasl Road", "Corniche Road", "Hamdan Street"],
        "phone_format": "+971 ## ### ####"
    },
    "sg": {
        "country": "Сингапур",
        "flag": "🇸🇬",
        "cities": [
            {"city": "Singapore", "state": "Central", "zip_format": "######"},
        ],
        "streets": ["Orchard Road", "Marina Bay", "Raffles Place", "Chinatown", "Little India", "Clarke Quay", "Sentosa"],
        "phone_format": "+65 #### ####"
    },
    "nz": {
        "country": "Новая Зеландия",
        "flag": "🇳🇿",
        "cities": [
            {"city": "Auckland", "state": "Auckland", "zip_format": "1###"},
            {"city": "Wellington", "state": "Wellington", "zip_format": "6###"},
            {"city": "Christchurch", "state": "Canterbury", "zip_format": "8###"},
            {"city": "Hamilton", "state": "Waikato", "zip_format": "3###"},
        ],
        "streets": ["Queen Street", "Lambton Quay", "Colombo Street", "Victoria Street", "Cuba Street"],
        "phone_format": "+64 ## ### ####"
    },
    "za": {
        "country": "ЮАР",
        "flag": "🇿🇦",
        "cities": [
            {"city": "Johannesburg", "state": "Gauteng", "zip_format": "2###"},
            {"city": "Cape Town", "state": "Western Cape", "zip_format": "8###"},
            {"city": "Durban", "state": "KwaZulu-Natal", "zip_format": "4###"},
            {"city": "Pretoria", "state": "Gauteng", "zip_format": "0###"},
        ],
        "streets": ["Long Street", "Adderley Street", "Commissioner Street", "Church Street", "West Street"],
        "phone_format": "+27 ## ### ####"
    },
    "il": {
        "country": "Израиль",
        "flag": "🇮🇱",
        "cities": [
            {"city": "Tel Aviv", "state": "Tel Aviv", "zip_format": "6#####"},
            {"city": "Jerusalem", "state": "Jerusalem", "zip_format": "9#####"},
            {"city": "Haifa", "state": "Haifa", "zip_format": "3#####"},
            {"city": "Eilat", "state": "South", "zip_format": "88#####"},
        ],
        "streets": ["Dizengoff Street", "Rothschild Boulevard", "Ben Yehuda Street", "Allenby Street", "Jaffa Road"],
        "phone_format": "+972 ## ### ####"
    },
    "ar": {
        "country": "Аргентина",
        "flag": "🇦🇷",
        "cities": [
            {"city": "Buenos Aires", "state": "CABA", "zip_format": "C1###AAA"},
            {"city": "Córdoba", "state": "Córdoba", "zip_format": "X5###AAA"},
            {"city": "Rosario", "state": "Santa Fe", "zip_format": "S2###AAA"},
            {"city": "Mendoza", "state": "Mendoza", "zip_format": "M5###AAA"},
        ],
        "streets": ["Avenida 9 de Julio", "Calle Florida", "Avenida Corrientes", "Avenida Santa Fe", "Calle Lavalle"],
        "phone_format": "+54 ## ####-####"
    },
    "cl": {
        "country": "Чили",
        "flag": "🇨🇱",
        "cities": [
            {"city": "Santiago", "state": "Metropolitana", "zip_format": "#######"},
            {"city": "Valparaíso", "state": "Valparaíso", "zip_format": "#######"},
            {"city": "Concepción", "state": "Biobío", "zip_format": "#######"},
        ],
        "streets": ["Avenida Libertador", "Paseo Ahumada", "Calle Estado", "Avenida Providencia", "Calle Huerfanos"],
        "phone_format": "+56 # #### ####"
    },
    "co": {
        "country": "Колумбия",
        "flag": "🇨🇴",
        "cities": [
            {"city": "Bogotá", "state": "Cundinamarca", "zip_format": "1#####"},
            {"city": "Medellín", "state": "Antioquia", "zip_format": "05####"},
            {"city": "Cali", "state": "Valle del Cauca", "zip_format": "76####"},
            {"city": "Cartagena", "state": "Bolívar", "zip_format": "13####"},
        ],
        "streets": ["Carrera Séptima", "Calle 72", "Avenida El Dorado", "Carrera 15", "Calle 100"],
        "phone_format": "+57 ### ### ####"
    },
    "th": {
        "country": "Таиланд",
        "flag": "🇹🇭",
        "cities": [
            {"city": "Bangkok", "state": "Bangkok", "zip_format": "10###"},
            {"city": "Chiang Mai", "state": "Chiang Mai", "zip_format": "50###"},
            {"city": "Phuket", "state": "Phuket", "zip_format": "83###"},
            {"city": "Pattaya", "state": "Chonburi", "zip_format": "20###"},
        ],
        "streets": ["Sukhumvit Road", "Silom Road", "Khao San Road", "Ratchadamri Road", "Wireless Road"],
        "phone_format": "+66 ## ### ####"
    },
    "my": {
        "country": "Малайзия",
        "flag": "🇲🇾",
        "cities": [
            {"city": "Kuala Lumpur", "state": "Kuala Lumpur", "zip_format": "5####"},
            {"city": "George Town", "state": "Penang", "zip_format": "10###"},
            {"city": "Johor Bahru", "state": "Johor", "zip_format": "80###"},
            {"city": "Kota Kinabalu", "state": "Sabah", "zip_format": "88###"},
        ],
        "streets": ["Jalan Bukit Bintang", "Jalan Sultan Ismail", "Jalan Ampang", "Jalan Tun Razak", "Jalan Imbi"],
        "phone_format": "+60 ##-### ####"
    },
    "ph": {
        "country": "Филиппины",
        "flag": "🇵🇭",
        "cities": [
            {"city": "Manila", "state": "Metro Manila", "zip_format": "1###"},
            {"city": "Quezon City", "state": "Metro Manila", "zip_format": "11##"},
            {"city": "Cebu City", "state": "Cebu", "zip_format": "6###"},
            {"city": "Davao City", "state": "Davao", "zip_format": "8###"},
        ],
        "streets": ["Ayala Avenue", "EDSA", "Roxas Boulevard", "Makati Avenue", "Ortigas Avenue"],
        "phone_format": "+63 ### ### ####"
    },
    "id": {
        "country": "Индонезия",
        "flag": "🇮🇩",
        "cities": [
            {"city": "Jakarta", "state": "DKI Jakarta", "zip_format": "1####"},
            {"city": "Surabaya", "state": "East Java", "zip_format": "6####"},
            {"city": "Bandung", "state": "West Java", "zip_format": "4####"},
            {"city": "Bali", "state": "Bali", "zip_format": "80###"},
        ],
        "streets": ["Jalan Sudirman", "Jalan Thamrin", "Jalan Gatot Subroto", "Jalan Rasuna Said", "Jalan Kuningan"],
        "phone_format": "+62 ### #### ####"
    },
    "vn": {
        "country": "Вьетнам",
        "flag": "🇻🇳",
        "cities": [
            {"city": "Ho Chi Minh City", "state": "Ho Chi Minh", "zip_format": "7#####"},
            {"city": "Hanoi", "state": "Hanoi", "zip_format": "1#####"},
            {"city": "Da Nang", "state": "Da Nang", "zip_format": "5#####"},
            {"city": "Nha Trang", "state": "Khanh Hoa", "zip_format": "65####"},
        ],
        "streets": ["Nguyen Hue", "Le Loi", "Dong Khoi", "Tran Hung Dao", "Hai Ba Trung"],
        "phone_format": "+84 ### ### ####"
    },
    "eg": {
        "country": "Египет",
        "flag": "🇪🇬",
        "cities": [
            {"city": "Cairo", "state": "Cairo", "zip_format": "#####"},
            {"city": "Alexandria", "state": "Alexandria", "zip_format": "#####"},
            {"city": "Giza", "state": "Giza", "zip_format": "#####"},
            {"city": "Sharm El Sheikh", "state": "South Sinai", "zip_format": "#####"},
        ],
        "streets": ["Tahrir Square", "Talaat Harb Street", "26th of July Street", "Corniche El Nil", "Salah Salem Road"],
        "phone_format": "+20 ### ### ####"
    },
    "ng": {
        "country": "Нигерия",
        "flag": "🇳🇬",
        "cities": [
            {"city": "Lagos", "state": "Lagos", "zip_format": "1#####"},
            {"city": "Abuja", "state": "FCT", "zip_format": "9#####"},
            {"city": "Kano", "state": "Kano", "zip_format": "7#####"},
            {"city": "Ibadan", "state": "Oyo", "zip_format": "2#####"},
        ],
        "streets": ["Broad Street", "Marina", "Awolowo Road", "Adeola Odeku", "Victoria Island"],
        "phone_format": "+234 ### ### ####"
    },
    "ke": {
        "country": "Кения",
        "flag": "🇰🇪",
        "cities": [
            {"city": "Nairobi", "state": "Nairobi", "zip_format": "00###"},
            {"city": "Mombasa", "state": "Coast", "zip_format": "80###"},
            {"city": "Kisumu", "state": "Nyanza", "zip_format": "40###"},
        ],
        "streets": ["Kenyatta Avenue", "Moi Avenue", "Uhuru Highway", "Tom Mboya Street", "Kimathi Street"],
        "phone_format": "+254 ### ### ###"
    }
}

FIRST_NAMES_MALE = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Alexander", "Daniel", "Matthew", "Anthony", "Mark"]
FIRST_NAMES_FEMALE = ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]


def generate_phone(format_str):
    """Генерация номера телефона по формату"""
    result = ""
    for char in format_str:
        if char == "#":
            result += str(random.randint(0, 9))
        else:
            result += char
    return result


def generate_zip(format_str):
    """Генерация почтового индекса по формату"""
    result = ""
    for char in format_str:
        if char == "#":
            result += str(random.randint(0, 9))
        elif char == "A":
            result += random.choice(string.ascii_uppercase)
        else:
            result += char
    return result


def generate_address(country_code="us"):
    """Генерация случайного адреса"""
    if country_code not in ADDRESS_DATA:
        country_code = "us"
    
    data = ADDRESS_DATA[country_code]
    city_data = random.choice(data["cities"])
    street = random.choice(data["streets"])
    house_num = random.randint(1, 999)
    apt = random.randint(1, 200) if random.random() > 0.5 else None
    
    # Генерация имени
    gender = random.choice(["male", "female"])
    first_name = random.choice(FIRST_NAMES_MALE if gender == "male" else FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    
    address = {
        "country": data["country"],
        "flag": data["flag"],
        "city": city_data["city"],
        "state": city_data["state"],
        "zip": generate_zip(city_data["zip_format"]),
        "street": f"{house_num} {street}",
        "apartment": f"Apt {apt}" if apt else None,
        "phone": generate_phone(data["phone_format"]),
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{'gmail.com' if random.random() > 0.5 else 'outlook.com'}"
    }
    
    return address


def format_address(addr):
    """Форматирование адреса для отображения"""
    text = f"{addr['flag']} **{addr['country']}**\n\n"
    text += f"👤 **Имя:** {addr['full_name']}\n"
    text += f"📧 **Email:** `{addr['email']}`\n"
    text += f"📱 **Телефон:** `{addr['phone']}`\n\n"
    text += f"🏠 **Адрес:**\n"
    text += f"   {addr['street']}\n"
    if addr['apartment']:
        text += f"   {addr['apartment']}\n"
    text += f"   {addr['city']}, {addr['state']} {addr['zip']}\n"
    text += f"   {addr['country']}"
    return text


# === ГЕНЕРАТОР КАРТ ===

CARD_BINS = {
    "visa": {
        "name": "Visa",
        "icon": "💳",
        "bins": ["4", "4532", "4556", "4916", "4539", "4485", "4716"],
        "length": 16,
        "cvv_length": 3
    },
    "mastercard": {
        "name": "Mastercard",
        "icon": "💳",
        "bins": ["51", "52", "53", "54", "55", "2221", "2720"],
        "length": 16,
        "cvv_length": 3
    },
    "amex": {
        "name": "American Express",
        "icon": "💳",
        "bins": ["34", "37"],
        "length": 15,
        "cvv_length": 4
    },
    "discover": {
        "name": "Discover",
        "icon": "💳",
        "bins": ["6011", "644", "645", "646", "647", "648", "649", "65"],
        "length": 16,
        "cvv_length": 3
    },
    "unionpay": {
        "name": "UnionPay",
        "icon": "💳",
        "bins": ["62", "621", "622", "623", "624", "625", "626"],
        "length": 16,
        "cvv_length": 3
    },
    "jcb": {
        "name": "JCB",
        "icon": "💳",
        "bins": ["3528", "3529", "353", "354", "355", "356", "357", "358"],
        "length": 16,
        "cvv_length": 3
    },
    "maestro": {
        "name": "Maestro",
        "icon": "💳",
        "bins": ["5018", "5020", "5038", "5893", "6304", "6759", "6761", "6762", "6763"],
        "length": 16,
        "cvv_length": 3
    },
    "mir": {
        "name": "MIR",
        "icon": "💳",
        "bins": ["2200", "2201", "2202", "2203", "2204"],
        "length": 16,
        "cvv_length": 3
    },
    "diners": {
        "name": "Diners Club",
        "icon": "💳",
        "bins": ["300", "301", "302", "303", "304", "305", "36", "38"],
        "length": 14,
        "cvv_length": 3
    },
    "elo": {
        "name": "Elo",
        "icon": "💳",
        "bins": ["4011", "4312", "4389", "5041", "5066", "5067", "509", "6277", "6362", "6363", "650", "651", "652", "653", "654", "655", "656", "657", "658"],
        "length": 16,
        "cvv_length": 3
    },
    "hipercard": {
        "name": "Hipercard",
        "icon": "💳",
        "bins": ["384", "606282"],
        "length": 16,
        "cvv_length": 3
    },
    "rupay": {
        "name": "RuPay",
        "icon": "💳",
        "bins": ["60", "65", "81", "82", "508"],
        "length": 16,
        "cvv_length": 3
    },
    "troy": {
        "name": "Troy",
        "icon": "💳",
        "bins": ["9792"],
        "length": 16,
        "cvv_length": 3
    },
    "verve": {
        "name": "Verve",
        "icon": "💳",
        "bins": ["506", "507", "650"],
        "length": 16,
        "cvv_length": 3
    }
}


def luhn_checksum(card_number):
    """Вычисление контрольной суммы по алгоритму Луна"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    
    return checksum % 10


def generate_card_number(card_type="visa"):
    """Генерация номера карты с валидной контрольной суммой"""
    if card_type not in CARD_BINS:
        card_type = "visa"
    
    card_data = CARD_BINS[card_type]
    bin_prefix = random.choice(card_data["bins"])
    length = card_data["length"]
    
    # Генерируем номер без последней цифры
    remaining_length = length - len(bin_prefix) - 1
    number = bin_prefix + ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
    
    # Вычисляем контрольную цифру
    checksum = luhn_checksum(int(number + '0'))
    check_digit = (10 - checksum) % 10
    
    return number + str(check_digit)


def generate_card(card_type="visa"):
    """Генерация полных данных карты"""
    if card_type not in CARD_BINS:
        card_type = "visa"
    
    card_data = CARD_BINS[card_type]
    
    # Генерация даты истечения (1-5 лет вперёд)
    exp_month = random.randint(1, 12)
    exp_year = datetime.now().year + random.randint(1, 5)
    
    # Генерация CVV
    cvv = ''.join([str(random.randint(0, 9)) for _ in range(card_data["cvv_length"])])
    
    # Генерация имени держателя
    first_name = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    
    card = {
        "type": card_type,
        "type_name": card_data["name"],
        "icon": card_data["icon"],
        "number": generate_card_number(card_type),
        "exp_month": f"{exp_month:02d}",
        "exp_year": str(exp_year),
        "exp_short": f"{exp_month:02d}/{str(exp_year)[-2:]}",
        "cvv": cvv,
        "holder": f"{first_name.upper()} {last_name.upper()}"
    }
    
    return card


def format_card_number(number):
    """Форматирование номера карты с пробелами"""
    if len(number) == 15:  # Amex
        return f"{number[:4]} {number[4:10]} {number[10:]}"
    else:
        return ' '.join([number[i:i+4] for i in range(0, len(number), 4)])


def format_card(card):
    """Форматирование карты для отображения"""
    text = f"{card['icon']} **{card['type_name']}**\n\n"
    text += f"💳 **Номер:** `{format_card_number(card['number'])}`\n"
    text += f"📅 **Срок:** `{card['exp_short']}`\n"
    text += f"🔐 **CVV:** `{card['cvv']}`\n"
    text += f"👤 **Держатель:** `{card['holder']}`\n\n"
    text += f"⚠️ _Тестовые данные для разработки_"
    return text


# === ГЕНЕРАТОР АНТИДЕТЕКТ ДАННЫХ ===

USER_AGENTS = {
    "chrome_win": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ],
    "chrome_mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ],
    "firefox_win": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ],
    "safari_mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ],
    "mobile_android": [
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    ],
    "mobile_ios": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    ]
}

SCREEN_RESOLUTIONS = [
    {"width": 1920, "height": 1080, "name": "Full HD"},
    {"width": 2560, "height": 1440, "name": "2K QHD"},
    {"width": 3840, "height": 2160, "name": "4K UHD"},
    {"width": 1366, "height": 768, "name": "HD"},
    {"width": 1536, "height": 864, "name": "HD+"},
    {"width": 1440, "height": 900, "name": "WXGA+"},
    {"width": 1680, "height": 1050, "name": "WSXGA+"},
]

TIMEZONES = [
    {"name": "America/New_York", "offset": -5},
    {"name": "America/Los_Angeles", "offset": -8},
    {"name": "America/Chicago", "offset": -6},
    {"name": "Europe/London", "offset": 0},
    {"name": "Europe/Paris", "offset": 1},
    {"name": "Europe/Berlin", "offset": 1},
    {"name": "Europe/Moscow", "offset": 3},
    {"name": "Europe/Kiev", "offset": 2},
    {"name": "Asia/Tokyo", "offset": 9},
    {"name": "Asia/Shanghai", "offset": 8},
]

LANGUAGES = ["en-US", "en-GB", "de-DE", "fr-FR", "es-ES", "it-IT", "ru-RU", "uk-UA", "pl-PL", "ja-JP", "zh-CN"]

WEBGL_VENDORS = ["Google Inc. (NVIDIA)", "Google Inc. (Intel)", "Google Inc. (AMD)", "Intel Inc.", "NVIDIA Corporation"]
WEBGL_RENDERERS = [
    "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
]


def generate_fingerprint():
    """Генерация уникального fingerprint"""
    # Canvas fingerprint
    canvas_hash = hashlib.md5(str(random.random()).encode()).hexdigest()
    
    # WebGL fingerprint
    webgl_hash = hashlib.md5(str(random.random()).encode()).hexdigest()
    
    # Audio fingerprint
    audio_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    
    return {
        "canvas": canvas_hash,
        "webgl": webgl_hash,
        "audio": audio_hash
    }


def generate_antidetect_profile(platform="chrome_win"):
    """Генерация полного антидетект профиля"""
    if platform not in USER_AGENTS:
        platform = "chrome_win"
    
    user_agent = random.choice(USER_AGENTS[platform])
    screen = random.choice(SCREEN_RESOLUTIONS)
    timezone = random.choice(TIMEZONES)
    language = random.choice(LANGUAGES)
    fingerprint = generate_fingerprint()
    
    profile = {
        "user_agent": user_agent,
        "platform": platform,
        "screen": screen,
        "timezone": timezone,
        "language": language,
        "languages": [language, language.split("-")[0]],
        "webgl_vendor": random.choice(WEBGL_VENDORS),
        "webgl_renderer": random.choice(WEBGL_RENDERERS),
        "fingerprint": fingerprint,
        "hardware_concurrency": random.choice([4, 8, 12, 16]),
        "device_memory": random.choice([4, 8, 16, 32]),
        "do_not_track": random.choice(["1", None]),
        "cookies_enabled": True,
        "java_enabled": False,
        "pdf_viewer_enabled": True,
        "plugins_count": random.randint(3, 7),
        "color_depth": 24,
        "pixel_ratio": random.choice([1, 1.25, 1.5, 2]),
        "session_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat()
    }
    
    return profile


def format_antidetect_profile(profile):
    """Форматирование профиля для отображения"""
    text = "🤖 **Антидетект профиль**\n\n"
    
    text += "📱 **User-Agent:**\n"
    text += f"`{profile['user_agent']}`\n\n"
    
    text += f"🖥 **Экран:** {profile['screen']['width']}x{profile['screen']['height']} ({profile['screen']['name']})\n"
    text += f"🌍 **Timezone:** {profile['timezone']['name']} (UTC{profile['timezone']['offset']:+d})\n"
    text += f"🗣 **Язык:** {profile['language']}\n\n"
    
    text += "🎮 **WebGL:**\n"
    text += f"   Vendor: `{profile['webgl_vendor']}`\n"
    text += f"   Renderer: `{profile['webgl_renderer'][:50]}...`\n\n"
    
    text += "🔑 **Fingerprints:**\n"
    text += f"   Canvas: `{profile['fingerprint']['canvas'][:16]}...`\n"
    text += f"   WebGL: `{profile['fingerprint']['webgl'][:16]}...`\n"
    text += f"   Audio: `{profile['fingerprint']['audio']}`\n\n"
    
    text += f"⚙️ **Hardware:**\n"
    text += f"   CPU Cores: {profile['hardware_concurrency']}\n"
    text += f"   RAM: {profile['device_memory']} GB\n"
    text += f"   Pixel Ratio: {profile['pixel_ratio']}\n\n"
    
    text += f"🆔 **Session ID:** `{profile['session_id'][:8]}...`"
    
    return text


def export_antidetect_profile(profile):
    """Экспорт профиля в JSON"""
    return json.dumps(profile, indent=2, ensure_ascii=False)
