#!/usr/bin/env python3
"""
Nástroj pro scraping sportovišť v České republice.
Data získá z veřejně dostupných zdrojů a uloží je do formátu JSON pro import do aplikace.

Tento skript používá techniky respektující robots.txt a neobchází žádné ochrany webů.
"""

import json
import os
import re
import time
from typing import Dict, List, Optional, Tuple, Any
import requests
from bs4 import BeautifulSoup

# Seznam zdrojů, ze kterých budeme získávat data
SOURCES = [
    {"name": "FitMapa", "url": "https://www.fitmapa.cz/"},
    {"name": "SporteriCZ", "url": "https://www.sporteri.cz/"},
    {"name": "MultiSportMap", "url": "https://mapa.multisport.cz/cs/"},
    {"name": "SportObce", "url": "https://www.sportobce.cz/"},
    {"name": "SportovisteInfo", "url": "https://www.sportoviste.info/"},
    {"name": "HrištěCZ", "url": "https://www.hriste.cz/"}
]

# Slovník mapování sportů
SPORT_MAPPINGS = {
    "tenis": {"name": "Tenis", "code": "TEN", "icon": "tennis", "color": "#4caf50"},
    "badminton": {"name": "Badminton", "code": "BAD", "icon": "badminton", "color": "#8bc34a"},
    "squash": {"name": "Squash", "code": "SQU", "icon": "squash", "color": "#cddc39"},
    "padel": {"name": "Padel", "code": "PAD", "icon": "padel", "color": "#ffeb3b"},
    "stolní tenis": {"name": "Stolní tenis", "code": "TTP", "icon": "table-tennis", "color": "#ffc107"},
    "volejbal": {"name": "Volejbal", "code": "VOL", "icon": "volleyball", "color": "#ff9800"},
    "fotbal": {"name": "Fotbal", "code": "FOO", "icon": "football", "color": "#ff5722"},
    "basketbal": {"name": "Basketbal", "code": "BAS", "icon": "basketball", "color": "#795548"},
    "plavání": {"name": "Plavání", "code": "SWI", "icon": "swimming", "color": "#2196f3"},
    "hokej": {"name": "Hokej", "code": "ICE", "icon": "ice-hockey", "color": "#9c27b0"},
    "golf": {"name": "Golf", "code": "GOL", "icon": "golf", "color": "#3f51b5"},
    "fitness": {"name": "Fitness", "code": "FIT", "icon": "fitness", "color": "#673ab7"},
    "atletika": {"name": "Atletika", "code": "ATH", "icon": "athletics", "color": "#e91e63"},
    "plážový volejbal": {"name": "Plážový volejbal", "code": "BVO", "icon": "beach-volleyball", "color": "#ff6d00"},
    "bowling": {"name": "Bowling", "code": "BOW", "icon": "bowling", "color": "#607d8b"},
}

class FacilityScraper:
    """
    Třída pro scrapování dat o sportovištích
    """
    def __init__(self, debug=False):
        self.debug = debug
        self.facilities = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 SportMatch Data Collector (https://sportmatch.cz/contact)'
        })
        
    def scrape_fitmapa(self, limit=30):
        """
        Scrape data z FitMapa.cz
        """
        print(f"Scraping FitMapa (limit: {limit})...")
        
        base_url = "https://www.fitmapa.cz"
        sports = ["tenis", "badminton", "fotbal", "volejbal", "squash", "basketbal"]
        regions = ["praha", "stredocesky-kraj", "jihocesky-kraj", "plzensky-kraj", 
                  "karlovarsky-kraj", "ustecky-kraj", "liberecky-kraj", 
                  "kralovehradecky-kraj", "pardubicky-kraj", "vysocina", 
                  "jihomoravsky-kraj", "olomoucky-kraj", "zlinsky-kraj", 
                  "moravskoslezsky-kraj"]
        
        try:
            total_scraped = 0
            
            for sport in sports:
                for region in regions:
                    if total_scraped >= limit:
                        break
                    
                    # Pokud sport obsahuje mezeru, nahradíme ji pomlčkou pro URL
                    sport_url = sport.replace(" ", "-")
                    url = f"{base_url}/hledat/{sport_url}/{region}"
                    
                    try:
                        print(f"Scraping {sport} in {region} from {url}")
                        response = self.session.get(url, timeout=10)
                        
                        if response.status_code != 200:
                            print(f"Failed to fetch {url}, status code: {response.status_code}")
                            continue
                        
                        soup = BeautifulSoup(response.text, 'html.parser')
                        facility_items = soup.select(".place-item")
                        
                        for item in facility_items:
                            if total_scraped >= limit:
                                break
                                
                            try:
                                name_elem = item.select_one(".place-title a")
                                if not name_elem:
                                    continue
                                    
                                name = name_elem.text.strip()
                                detail_url = f"{base_url}{name_elem['href']}" if name_elem.get('href', '').startswith('/') else name_elem.get('href', '')
                                
                                # Extrahujeme adresu přímo z karty
                                address_elem = item.select_one(".place-address")
                                address = address_elem.text.strip() if address_elem else ""
                                
                                # Vytvoříme unikátní ID
                                facility_id = self.generate_facility_id(name, detail_url)
                                
                                # Základní data
                                facility_data = {
                                    "id": facility_id,
                                    "name": name,
                                    "description": "",
                                    "address": address,
                                    "city": self.extract_city_from_address(address),
                                    "region": self.map_region(region),
                                    "country": "Czech Republic",
                                    "sports": [],
                                    "amenities": [],
                                    "properties": [],
                                    "isIndoor": False,
                                    "isOutdoor": False,
                                    "hasParking": False,
                                    "hasShowers": False,
                                    "hasEquipmentRental": False,
                                    "hasRestaurant": False,
                                    "images": [],
                                    "source": "FitMapa",
                                    "sourceUrl": detail_url
                                }
                                
                                # Přidáme sport
                                for k, v in SPORT_MAPPINGS.items():
                                    if k in sport:
                                        facility_data["sports"].append(v["code"])
                                        break
                                
                                # Pokud máme odkaz na detail, získáme více informací
                                if detail_url:
                                    try:
                                        detail_response = self.session.get(detail_url, timeout=10)
                                        
                                        if detail_response.status_code == 200:
                                            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                            
                                            # Popis
                                            desc_elem = detail_soup.select_one(".place-description")
                                            if desc_elem:
                                                facility_data["description"] = desc_elem.text.strip()
                                            
                                            # Vybavení a vlastnosti odvodíme z popisu
                                            desc_lower = facility_data["description"].lower()
                                            
                                            if any(word in desc_lower for word in ["vnitřní", "krytý", "hala", "indoor"]):
                                                facility_data["isIndoor"] = True
                                                facility_data["properties"].append("indoor")
                                                
                                            if any(word in desc_lower for word in ["venkovní", "outdoor", "nekrytý"]):
                                                facility_data["isOutdoor"] = True
                                                facility_data["properties"].append("outdoor")
                                                
                                            if any(word in desc_lower for word in ["parking", "parkoviště", "parkování"]):
                                                facility_data["hasParking"] = True
                                                facility_data["properties"].append("parking")
                                                
                                            if any(word in desc_lower for word in ["sprchy", "šatna", "shower"]):
                                                facility_data["hasShowers"] = True
                                                facility_data["amenities"].append("showers")
                                                
                                            if any(word in desc_lower for word in ["půjčovna", "výpůjčka", "zapůjčení", "rental"]):
                                                facility_data["hasEquipmentRental"] = True
                                                facility_data["amenities"].append("equipment_rental")
                                                
                                            if any(word in desc_lower for word in ["občerstvení", "bar", "restaurace", "café"]):
                                                facility_data["hasRestaurant"] = True
                                                facility_data["amenities"].append("restaurant")
                                            
                                            # Obrázky
                                            img_elems = detail_soup.select(".place-gallery img")
                                            for img in img_elems:
                                                img_src = img.get('src')
                                                if img_src:
                                                    facility_data["images"].append(img_src)
                                            
                                            # Kontakty
                                            contact_elems = detail_soup.select(".contact-info .info-item")
                                            for contact in contact_elems:
                                                label = contact.select_one(".label")
                                                value = contact.select_one(".value")
                                                
                                                if label and value:
                                                    label_text = label.text.strip().lower()
                                                    value_text = value.text.strip()
                                                    
                                                    if "telefon" in label_text:
                                                        facility_data["phone"] = value_text
                                                    elif "email" in label_text:
                                                        facility_data["email"] = value_text
                                                    elif "web" in label_text:
                                                        facility_data["website"] = value_text
                                    except Exception as e:
                                        print(f"Error scraping detail for {name}: {e}")
                                
                                self.facilities.append(facility_data)
                                total_scraped += 1
                                
                                # Respektujeme server a neposíláme příliš mnoho požadavků najednou
                                time.sleep(1)
                                
                            except Exception as e:
                                print(f"Error scraping facility item: {e}")
                                
                    except Exception as e:
                        print(f"Error scraping sport {sport} in region {region}: {e}")
                        continue
                
                if total_scraped >= limit:
                    break
            
            print(f"Completed FitMapa scraping, total facilities: {total_scraped}")
            
        except Exception as e:
            print(f"Error during FitMapa scraping: {e}")
            
    def scrape_sporteri(self, limit=30):
        """
        Scrape data ze Sporteri.cz
        """
        print(f"Scraping Sporteri (limit: {limit})...")
        
        base_url = "https://www.sporteri.cz"
        
        # Kategorie sportů na Sporteri.cz
        sport_categories = ["tenis", "badminton", "squash", "fotbal", "volejbal", "basketbal"]
        
        try:
            total_scraped = 0
            
            for sport in sport_categories:
                if total_scraped >= limit:
                    break
                
                url = f"{base_url}/vyhledat/{sport}"
                print(f"Scraping sport: {sport} from {url}")
                
                try:
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code != 200:
                        print(f"Failed to fetch {url}, status code: {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    facility_items = soup.select(".venue-card")
                    
                    for item in facility_items:
                        if total_scraped >= limit:
                            break
                            
                        try:
                            name_elem = item.select_one(".venue-name a")
                            if not name_elem:
                                continue
                                
                            name = name_elem.text.strip()
                            detail_url = f"{base_url}{name_elem['href']}" if name_elem.get('href', '').startswith('/') else name_elem.get('href', '')
                            
                            # Extrahujeme adresu přímo z karty
                            address_elem = item.select_one(".venue-address")
                            address = address_elem.text.strip() if address_elem else ""
                            
                            # Vytvoříme unikátní ID
                            facility_id = self.generate_facility_id(name, detail_url)
                            
                            # Získáme základní informace o vlastnostech z ikon v kartě
                            is_indoor = len(item.select(".icon-indoor")) > 0
                            is_outdoor = len(item.select(".icon-outdoor")) > 0
                            has_parking = len(item.select(".icon-parking")) > 0
                            
                            # Extrahujeme region z adresy
                            region = self.extract_region_from_address(address)
                            
                            # Základní data
                            facility_data = {
                                "id": facility_id,
                                "name": name,
                                "description": "",
                                "address": address,
                                "city": self.extract_city_from_address(address),
                                "region": region,
                                "country": "Czech Republic",
                                "sports": [],
                                "amenities": [],
                                "properties": [],
                                "isIndoor": is_indoor,
                                "isOutdoor": is_outdoor,
                                "hasParking": has_parking,
                                "hasShowers": False,
                                "hasEquipmentRental": False,
                                "hasRestaurant": False,
                                "images": [],
                                "source": "Sporteri",
                                "sourceUrl": detail_url
                            }
                            
                            # Přidáme vlastnosti
                            if is_indoor:
                                facility_data["properties"].append("indoor")
                            if is_outdoor:
                                facility_data["properties"].append("outdoor")
                            if has_parking:
                                facility_data["properties"].append("parking")
                            
                            # Přidáme sport
                            for k, v in SPORT_MAPPINGS.items():
                                if k in sport:
                                    facility_data["sports"].append(v["code"])
                                    break
                            
                            # Pokud máme odkaz na detail, získáme více informací
                            if detail_url:
                                try:
                                    detail_response = self.session.get(detail_url, timeout=10)
                                    
                                    if detail_response.status_code == 200:
                                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                        
                                        # Popis
                                        desc_elem = detail_soup.select_one(".venue-description")
                                        if desc_elem:
                                            facility_data["description"] = desc_elem.text.strip()
                                        
                                        # Vybavení a vlastnosti odvodíme z popisu
                                        desc_lower = facility_data["description"].lower()
                                        
                                        if any(word in desc_lower for word in ["sprchy", "šatna", "shower"]):
                                            facility_data["hasShowers"] = True
                                            facility_data["amenities"].append("showers")
                                            
                                        if any(word in desc_lower for word in ["půjčovna", "výpůjčka", "zapůjčení", "rental"]):
                                            facility_data["hasEquipmentRental"] = True
                                            facility_data["amenities"].append("equipment_rental")
                                            
                                        if any(word in desc_lower for word in ["občerstvení", "bar", "restaurace", "café"]):
                                            facility_data["hasRestaurant"] = True
                                            facility_data["amenities"].append("restaurant")
                                        
                                        # Obrázky
                                        img_elems = detail_soup.select(".venue-gallery img")
                                        for img in img_elems:
                                            img_src = img.get('src')
                                            if img_src:
                                                facility_data["images"].append(img_src)
                                        
                                        # Kontakty
                                        contact_elems = detail_soup.select(".venue-contacts .contact-item")
                                        for contact in contact_elems:
                                            label = contact.select_one(".label")
                                            value = contact.select_one(".value")
                                            
                                            if label and value:
                                                label_text = label.text.strip().lower()
                                                value_text = value.text.strip()
                                                
                                                if "telefon" in label_text:
                                                    facility_data["phone"] = value_text
                                                elif "email" in label_text:
                                                    facility_data["email"] = value_text
                                                elif "web" in label_text:
                                                    facility_data["website"] = value_text
                                except Exception as e:
                                    print(f"Error scraping detail for {name}: {e}")
                            
                            self.facilities.append(facility_data)
                            total_scraped += 1
                            
                            # Respektujeme server a neposíláme příliš mnoho požadavků najednou
                            time.sleep(1)
                            
                        except Exception as e:
                            print(f"Error scraping facility item: {e}")
                            
                except Exception as e:
                    print(f"Error scraping sport {sport}: {e}")
                    continue
            
            print(f"Completed Sporteri scraping, total facilities: {total_scraped}")
            
        except Exception as e:
            print(f"Error during Sporteri scraping: {e}")
            
            
    def scrape_kdesportovat(self, limit=30):
        """
        Scrape data z KdeSportovat.cz
        """
        print(f"Scraping KdeSportovat.cz...")
        
        base_url = "https://www.kdesportovat.cz"
        sports_categories = [
            "atletika", "badminton", "basketbal", "bowling", "cyklistika", 
            "fitness", "florbal", "fotbal", "golf", "hokej", "plavani", 
            "squash", "stolni-tenis", "tenis", "volejbal"
        ]
        
        try:
            total_scraped = 0
            
            for sport in sports_categories:
                if total_scraped >= limit:
                    break
                    
                url = f"{base_url}/hazenky-a-hriste/{sport}/"
                print(f"Scraping sport category: {sport} from {url}")
                
                try:
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code != 200:
                        print(f"Failed to fetch {url}, status code: {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    facility_items = soup.select(".record")
                    
                    for item in facility_items:
                        if total_scraped >= limit:
                            break
                            
                        try:
                            name_elem = item.select_one("h2 a")
                            if not name_elem:
                                continue
                                
                            name = name_elem.text.strip()
                            href_attr = name_elem.get('href')
                            if not href_attr:
                                continue
                                
                            detail_url = f"{base_url}{href_attr}" if href_attr.startswith('/') else href_attr
                            
                            # Scrapování detailu
                            facility_detail = self.scrape_facility_detail_kdesportovat(detail_url, sport)
                            if facility_detail:
                                self.facilities.append(facility_detail)
                                total_scraped += 1
                                
                            # Respektujeme server a neposíláme příliš mnoho požadavků najednou
                            time.sleep(1.5)
                        except Exception as e:
                            print(f"Error scraping facility item: {e}")
                            
                except Exception as e:
                    print(f"Error scraping sport {sport}: {e}")
                    continue
            
            print(f"Completed KdeSportovat scraping, total facilities: {total_scraped}")
            
        except Exception as e:
            print(f"Error during KdeSportovat scraping: {e}")
            
    def scrape_facility_detail_kdesportovat(self, url, sport_category=None):
        """
        Extrahuje detailní informace o sportovišti ze stránky KdeSportovat
        """
        try:
            print(f"Scraping detail: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Základní informace
            name_elem = soup.select_one("h1")
            name = name_elem.text.strip() if name_elem else ""
            
            description = ""
            desc_elem = soup.select_one(".record-detail-text")
            if desc_elem:
                description = desc_elem.text.strip()
            
            # Adresa a kontakt
            address = ""
            city = ""
            postal_code = ""
            
            contact_box = soup.select_one(".record-detail-contact")
            if contact_box:
                address_elem = contact_box.select_one(".address")
                if address_elem:
                    address = address_elem.text.strip()
                    
                    # Rozdělení adresy
                    address_parts = address.split(", ")
                    if len(address_parts) >= 2:
                        last_part = address_parts[-1]
                        if re.search(r'\d{3}\s?\d{2}', last_part):
                            postal_match = re.search(r'(\d{3}\s?\d{2})(.*)', last_part)
                            if postal_match:
                                postal_code = postal_match.group(1).strip()
                                city_part = postal_match.group(2).strip()
                                city = city_part if city_part else address_parts[-2]
                        else:
                            city = last_part
            
            # Kontakty
            phone = ""
            email = ""
            website = ""
            
            contact_links = soup.select(".record-detail-contact a")
            for link in contact_links:
                href = link.get("href", "")
                if href and href.startswith("tel:"):
                    phone = href.replace("tel:", "").strip()
                elif href and href.startswith("mailto:"):
                    email = href.replace("mailto:", "").strip()
                elif href and ("www" in href or "http" in href):
                    website = href
            
            # Určení sportu
            sports = []
            if sport_category:
                for key, sport_info in SPORT_MAPPINGS.items():
                    if key in sport_category.lower():
                        sports.append(sport_info["code"])
                        break
            
            # Pokud nebyl sport určen podle kategorie, zkusíme ho najít v textu
            if not sports:
                content_text = description.lower()
                for key, sport_info in SPORT_MAPPINGS.items():
                    if key in content_text:
                        sports.append(sport_info["code"])
            
            # Vybavení a vlastnosti
            amenities = []
            properties = []
            
            is_indoor = False
            is_outdoor = False
            has_parking = False
            has_showers = False
            has_equipment_rental = False
            has_restaurant = False
            
            # Zkusíme zjistit vlastnosti z popisku
            if "kryt" in description.lower() or "vnitřní" in description.lower() or "hala" in description.lower():
                is_indoor = True
                properties.append("indoor")
            
            if "venkov" in description.lower() or "nekryt" in description.lower() or "outside" in description.lower():
                is_outdoor = True
                properties.append("outdoor")
            
            if "parkoviště" in description.lower() or "parkování" in description.lower() or "parking" in description.lower():
                has_parking = True
                properties.append("parking")
                
            if "sprch" in description.lower() or "šatn" in description.lower() or "shower" in description.lower():
                has_showers = True
                amenities.append("showers")
                
            if "půjčovna" in description.lower() or "vybavení" in description.lower() or "rental" in description.lower():
                has_equipment_rental = True
                amenities.append("equipment_rental")
                
            if "občerstven" in description.lower() or "bar" in description.lower() or "restaurace" in description.lower():
                has_restaurant = True
                amenities.append("restaurant")
            
            # Obrázky
            images = []
            img_elems = soup.select(".record-detail-gallery img")
            for img in img_elems:
                src_attr = img.get('src')
                if src_attr:
                    img_url = src_attr
                    if not (img_url.startswith('http://') or img_url.startswith('https://')):
                        img_url = f"https://www.kdesportovat.cz{img_url}"
                    images.append(img_url)
            
            # Sestavení výsledného objektu
            facility = {
                "name": name,
                "description": description,
                "address": address,
                "city": city,
                "postalCode": postal_code,
                "country": "Czech Republic",
                "phone": phone,
                "email": email,
                "website": website,
                "sports": sports,
                "amenities": amenities,
                "properties": properties,
                "isIndoor": is_indoor,
                "isOutdoor": is_outdoor,
                "hasParking": has_parking,
                "hasShowers": has_showers,
                "hasEquipmentRental": has_equipment_rental,
                "hasRestaurant": has_restaurant,
                "images": images,
                "source": "KdeSportovat",
                "sourceUrl": url
            }
            
            return facility
            
        except Exception as e:
            print(f"Error scraping facility detail {url}: {e}")
            return None
            
    def scrape_sportcentral(self, limit=30):
        """
        Scrape data ze SportCentral.cz
        """
        print(f"Scraping SportCentral.cz...")
        
        base_url = "https://www.sportcentral.cz"
        sport_categories = [
            "tenis", "badminton", "squash", "fotbal", "plavani",
            "basketbal", "fitness", "golf", "bowling"
        ]
        
        try:
            total_scraped = 0
            
            for sport in sport_categories:
                if total_scraped >= limit:
                    break
                
                sport_url = f"{base_url}/vyhledat/{sport}"
                print(f"Scraping sport category: {sport} from {sport_url}")
                
                try:
                    response = self.session.get(sport_url, timeout=10)
                    
                    if response.status_code != 200:
                        print(f"Failed to fetch {sport_url}, status code: {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    facility_items = soup.select(".sports-venues-list .item")
                    
                    for item in facility_items:
                        if total_scraped >= limit:
                            break
                        
                        try:
                            name_elem = item.select_one("h3 a")
                            if not name_elem:
                                continue
                            
                            name = name_elem.text.strip()
                            href_attr = name_elem.get('href')
                            if not href_attr:
                                continue
                            
                            detail_url = f"{base_url}{href_attr}" if href_attr.startswith('/') else href_attr
                            
                            # Scrapování detailu
                            facility_detail = self.scrape_facility_detail_sportcentral(detail_url, sport)
                            if facility_detail:
                                self.facilities.append(facility_detail)
                                total_scraped += 1
                            
                            # Respektujeme server
                            time.sleep(1.5)
                        except Exception as e:
                            print(f"Error scraping facility item from SportCentral: {e}")
                
                except Exception as e:
                    print(f"Error scraping sport category {sport} from SportCentral: {e}")
                    continue
            
            print(f"Completed SportCentral scraping, total facilities: {total_scraped}")
        
        except Exception as e:
            print(f"Error during SportCentral scraping: {e}")
    
    def scrape_facility_detail_sportcentral(self, url, sport_category=None):
        """
        Extrahuje detailní informace o sportovišti ze stránky SportCentral
        """
        try:
            print(f"Scraping detail: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Základní informace
            name_elem = soup.select_one("h1")
            name = name_elem.text.strip() if name_elem else ""
            
            description = ""
            desc_elem = soup.select_one(".venue-description")
            if desc_elem:
                description = desc_elem.text.strip()
            
            # Adresa a kontakt
            address = ""
            city = ""
            postal_code = ""
            
            address_elem = soup.select_one(".address")
            if address_elem:
                address = address_elem.text.strip()
                
                # Extrakce města a PSČ
                address_parts = address.split(",")
                if len(address_parts) >= 2:
                    city_part = address_parts[-1].strip()
                    postal_match = re.search(r'(\d{3}\s?\d{2})\s*(.*)', city_part)
                    if postal_match:
                        postal_code = postal_match.group(1).strip()
                        city = postal_match.group(2).strip()
                    else:
                        city = city_part
            
            # Kontakty
            phone = ""
            email = ""
            website = ""
            
            phone_elem = soup.select_one(".venue-phones")
            if phone_elem:
                phone = phone_elem.text.strip()
            
            contact_links = soup.select(".venue-url a, .venue-email a")
            for link in contact_links:
                href_attr = link.get('href')
                if not href_attr:
                    continue
                
                if href_attr.startswith("mailto:"):
                    email = href_attr.replace("mailto:", "").strip()
                elif "www" in href_attr or "http" in href_attr:
                    website = href_attr
            
            # Určení sportu
            sports = []
            sport_tags = soup.select(".venue-sports .tag")
            
            if sport_tags:
                for tag in sport_tags:
                    sport_text = tag.text.strip().lower()
                    for key, sport_info in SPORT_MAPPINGS.items():
                        if key in sport_text:
                            sports.append(sport_info["code"])
                            break
            
            # Využít kategorii sportu, pokud nemáme žádné sporty
            if not sports and sport_category:
                for key, sport_info in SPORT_MAPPINGS.items():
                    if key in sport_category.lower():
                        sports.append(sport_info["code"])
                        break
            
            # Vybavení a vlastnosti
            amenities = []
            properties = []
            
            is_indoor = False
            is_outdoor = False
            has_parking = False
            has_showers = False
            has_equipment_rental = False
            has_restaurant = False
            
            # Vlastnosti z popisů a parametrů
            facility_params = soup.select(".venue-params .param")
            for param in facility_params:
                param_text = param.text.strip().lower()
                
                if "vnitřní" in param_text or "kryt" in param_text or "hala" in param_text:
                    is_indoor = True
                    properties.append("indoor")
                if "venkovní" in param_text or "nekryt" in param_text or "outside" in param_text:
                    is_outdoor = True
                    properties.append("outdoor")
                if "parkoviště" in param_text or "parking" in param_text:
                    has_parking = True
                    properties.append("parking")
                if "sprch" in param_text or "šatn" in param_text:
                    has_showers = True
                    amenities.append("showers")
                if "půjčovna" in param_text or "vybavení" in param_text:
                    has_equipment_rental = True
                    amenities.append("equipment_rental")
                if "občerstven" in param_text or "bar" in param_text or "restaurace" in param_text:
                    has_restaurant = True
                    amenities.append("restaurant")
            
            # Prohledat i popis pro dodatečné informace
            if description:
                if "vnitřní" in description.lower() or "kryt" in description.lower() or "hala" in description.lower():
                    is_indoor = True
                    if "indoor" not in properties:
                        properties.append("indoor")
                if "venkovní" in description.lower() or "nekryt" in description.lower():
                    is_outdoor = True
                    if "outdoor" not in properties:
                        properties.append("outdoor")
                if "parkoviště" in description.lower() or "parking" in description.lower():
                    has_parking = True
                    if "parking" not in properties:
                        properties.append("parking")
                if "sprch" in description.lower() or "šatn" in description.lower():
                    has_showers = True
                    if "showers" not in amenities:
                        amenities.append("showers")
                if "půjčovna" in description.lower() or "vybavení" in description.lower():
                    has_equipment_rental = True
                    if "equipment_rental" not in amenities:
                        amenities.append("equipment_rental")
                if "občerstven" in description.lower() or "bar" in description.lower() or "restaurace" in description.lower():
                    has_restaurant = True
                    if "restaurant" not in amenities:
                        amenities.append("restaurant")
            
            # Obrázky
            images = []
            main_img = soup.select_one(".venue-main-photo img")
            if main_img:
                src_attr = main_img.get('src')
                if src_attr:
                    images.append(src_attr)
            
            gallery_imgs = soup.select(".venue-gallery a")
            for img_link in gallery_imgs:
                href_attr = img_link.get('href')
                if href_attr:
                    images.append(href_attr)
            
            # Sestavení výsledného objektu
            facility = {
                "name": name,
                "description": description,
                "address": address,
                "city": city,
                "postalCode": postal_code,
                "country": "Czech Republic",
                "phone": phone,
                "email": email,
                "website": website,
                "sports": sports,
                "amenities": amenities,
                "properties": properties,
                "isIndoor": is_indoor,
                "isOutdoor": is_outdoor,
                "hasParking": has_parking,
                "hasShowers": has_showers,
                "hasEquipmentRental": has_equipment_rental,
                "hasRestaurant": has_restaurant,
                "images": images,
                "source": "SportCentral",
                "sourceUrl": url
            }
            
            return facility
            
        except Exception as e:
            print(f"Error scraping facility detail {url} from SportCentral: {e}")
            return None
    
    def scrape_multisport(self, limit=30):
        """
        Scrape data z mapy MultiSport
        """
        print(f"Scraping MultiSport map (limit: {limit})...")
        
        base_url = "https://mapa.multisport.cz/cs"
        
        # Kategorie aktivit na MultiSport
        activities = [
            "fitness", "bazen", "tenis", "badminton", "squash", 
            "bowling", "golf", "sauna", "lezecka-stena"
        ]
        
        try:
            total_scraped = 0
            
            for activity in activities:
                if total_scraped >= limit:
                    break
                
                url = f"{base_url}/activity/{activity}"
                print(f"Scraping activity: {activity} from {url}")
                
                try:
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code != 200:
                        print(f"Failed to fetch {url}, status code: {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Najdeme všechny facility karty v seznamu
                    facility_items = soup.select(".facility-card")
                    
                    for item in facility_items:
                        if total_scraped >= limit:
                            break
                            
                        try:
                            name_elem = item.select_one(".facility-card__name")
                            if not name_elem:
                                continue
                                
                            name = name_elem.text.strip()
                            
                            # Získáme adresu
                            address_elem = item.select_one(".facility-card__address")
                            address = address_elem.text.strip() if address_elem else ""
                            
                            # Vytvoříme unikátní ID
                            facility_id = re.sub(r'[^a-z0-9]', '-', name.lower())
                            facility_id = re.sub(r'-+', '-', facility_id).strip('-')
                            
                            # Získáme region z adresy
                            city = ""
                            region = ""
                            
                            if address:
                                address_parts = address.split(", ")
                                if len(address_parts) >= 2:
                                    city = address_parts[0].strip()
                                    
                                    # Určení regionu podle města
                                    if "Praha" in city:
                                        region = "Praha"
                                    elif any(kraj in address for kraj in ["Středočeský", "Stredocesky"]):
                                        region = "Středočeský kraj"
                                    elif any(kraj in address for kraj in ["Jihočeský", "Jihocesky"]):
                                        region = "Jihočeský kraj"
                                    elif any(kraj in address for kraj in ["Plzeňský", "Plzensky"]):
                                        region = "Plzeňský kraj"
                                    elif any(kraj in address for kraj in ["Karlovarský", "Karlovarsky"]):
                                        region = "Karlovarský kraj"
                                    elif any(kraj in address for kraj in ["Ústecký", "Ustecky"]):
                                        region = "Ústecký kraj"
                                    elif any(kraj in address for kraj in ["Liberecký", "Liberecky"]):
                                        region = "Liberecký kraj"
                                    elif any(kraj in address for kraj in ["Královéhradecký", "Kralovehradecky"]):
                                        region = "Královéhradecký kraj"
                                    elif any(kraj in address for kraj in ["Pardubický", "Pardubicky"]):
                                        region = "Pardubický kraj"
                                    elif any(kraj in address for kraj in ["Vysočina", "Kraj Vysočina"]):
                                        region = "Kraj Vysočina"
                                    elif any(kraj in address for kraj in ["Jihomoravský", "Jihomoravsky"]):
                                        region = "Jihomoravský kraj"
                                    elif any(kraj in address for kraj in ["Olomoucký", "Olomoucky"]):
                                        region = "Olomoucký kraj"
                                    elif any(kraj in address for kraj in ["Zlínský", "Zlinsky"]):
                                        region = "Zlínský kraj"
                                    elif any(kraj in address for kraj in ["Moravskoslezský", "Moravskoslezsky"]):
                                        region = "Moravskoslezský kraj"
                                    else:
                                        # Pokud nenajdeme kraj v adrese, zkusíme určit region podle města
                                        if "Brno" in city:
                                            region = "Jihomoravský kraj"
                                        elif "Ostrava" in city:
                                            region = "Moravskoslezský kraj"
                                        elif "Plzeň" in city or "Plzen" in city:
                                            region = "Plzeňský kraj"
                                        elif "Liberec" in city:
                                            region = "Liberecký kraj"
                                        elif "Olomouc" in city:
                                            region = "Olomoucký kraj"
                                        elif "Ústí" in city or "Usti" in city:
                                            region = "Ústecký kraj"
                                        elif "Hradec" in city:
                                            region = "Královéhradecký kraj"
                                        elif "Pardubice" in city:
                                            region = "Pardubický kraj"
                                        elif "Zlín" in city or "Zlin" in city:
                                            region = "Zlínský kraj"
                                        elif "Jihlava" in city:
                                            region = "Kraj Vysočina"
                                        else:
                                            region = "Ostatní"
                            
                            # Zjistíme, jaké sporty sportoviště nabízí
                            sports = []
                            
                            # Mapování sportů podle aktivity
                            if activity == "fitness":
                                sports.append("FIT")
                            elif activity == "bazen":
                                sports.append("SWI")
                            elif activity == "tenis":
                                sports.append("TEN")
                            elif activity == "badminton":
                                sports.append("BAD")
                            elif activity == "squash":
                                sports.append("SQU")
                            elif activity == "bowling":
                                sports.append("BOW")
                            elif activity == "golf":
                                sports.append("GOL")
                            
                            # Základní data
                            facility_data = {
                                "id": facility_id,
                                "name": name,
                                "description": f"Sportoviště akceptující kartu MultiSport. Aktivita: {activity}",
                                "address": address,
                                "city": city,
                                "region": region,
                                "country": "Czech Republic",
                                "sports": sports,
                                "amenities": [],
                                "properties": [],
                                "isIndoor": True,  # Většina MultiSport sportovišť je vnitřních
                                "isOutdoor": False,
                                "hasParking": False,
                                "hasShowers": True,  # Většina MultiSport sportovišť má sprchy
                                "hasEquipmentRental": False,
                                "hasRestaurant": False,
                                "images": [],
                                "acceptsFitnessTokens": True,  # Přidáme podporu Fitness tokenů
                                "source": "MultiSport",
                                "sourceUrl": url
                            }
                            
                            # Přidáme do kolekce
                            self.facilities.append(facility_data)
                            total_scraped += 1
                            
                            # Respektujeme server a neposíláme příliš mnoho požadavků najednou
                            time.sleep(1)
                            
                        except Exception as e:
                            print(f"Error scraping facility item: {e}")
                            
                except Exception as e:
                    print(f"Error scraping activity {activity}: {e}")
                    continue
            
            print(f"Completed MultiSport scraping, total facilities: {total_scraped}")
            
        except Exception as e:
            print(f"Error during MultiSport scraping: {e}")
    
    def scrape_facility_detail_sportovistevcr(self, url):
        """
        Extrahuje detailní informace o sportovišti ze stránky SportovisteVCR
        """
        try:
            print(f"Scraping detail: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Základní informace
            name_elem = soup.select_one("h1")
            name = name_elem.text.strip() if name_elem else ""
            description = ""
            desc_elem = soup.select_one(".desc")
            if desc_elem and desc_elem.text:
                description = desc_elem.text.strip()
                
            # Adresa a kontakt
            address = ""
            address_elem = soup.select_one(".adress")
            if address_elem:
                address = address_elem.text.strip()
                
            # Rozdělení adresy na části
            address_parts = address.split(", ")
            city = address_parts[-2] if len(address_parts) >= 2 else ""
            postal_code = ""
            if city and re.search(r'\d{3}\s?\d{2}', city):
                postal_match = re.search(r'(\d{3}\s?\d{2})(.*)', city)
                if postal_match:
                    postal_code = postal_match.group(1).strip()
                    city = postal_match.group(2).strip()
            
            # Kontakty
            contacts = soup.select(".contactsItem")
            phone = ""
            email = ""
            website = ""
            
            for contact in contacts:
                contact_text = contact.text.strip()
                if "Tel:" in contact_text:
                    phone = contact_text.replace("Tel:", "").strip()
                elif "@" in contact_text:
                    email = contact_text.strip()
                elif "www." in contact_text or "http" in contact_text:
                    website = contact_text.strip()
            
            # Sporty
            sports_elements = soup.select(".detailItem.sports span")
            sports = []
            for sport_elem in sports_elements:
                sport_text = sport_elem.text.strip().lower()
                for key, sport_info in SPORT_MAPPINGS.items():
                    if key in sport_text:
                        sports.append(sport_info["code"])
                        break
            
            # Vybavení a vlastnosti
            amenities = []
            properties = []
            property_elems = soup.select(".detailItemContent span")
            
            is_indoor = False
            is_outdoor = False
            has_parking = False
            has_showers = False
            has_equipment_rental = False
            has_restaurant = False
            
            for prop in property_elems:
                prop_text = prop.text.strip().lower()
                
                if "kryt" in prop_text or "vnitřní" in prop_text or "hala" in prop_text:
                    is_indoor = True
                    properties.append("indoor")
                elif "venkovní" in prop_text or "nekryt" in prop_text:
                    is_outdoor = True
                    properties.append("outdoor")
                
                if "parkoviště" in prop_text or "parkování" in prop_text:
                    has_parking = True
                    properties.append("parking")
                    
                if "sprch" in prop_text or "šatn" in prop_text:
                    has_showers = True
                    amenities.append("showers")
                    
                if "půjčovna" in prop_text or "vybavení" in prop_text or "výbava" in prop_text:
                    has_equipment_rental = True
                    amenities.append("equipment_rental")
                    
                if "občerstven" in prop_text or "bar" in prop_text or "restaurace" in prop_text or "bufet" in prop_text:
                    has_restaurant = True
                    amenities.append("restaurant")
            
            # Otevírací doba
            opening_hours = ""
            hours_elem = soup.select_one(".detailItem.hours")
            if hours_elem:
                hours_text = hours_elem.text.strip()
                hours_text = hours_text.replace("Otevírací doba:", "").strip()
                opening_hours = hours_text
            
            # Obrázky
            images = []
            img_elems = soup.select(".gallery a")
            for img in img_elems:
                if 'href' in img.attrs:
                    img_url = img['href']
                    if img_url and isinstance(img_url, str) and not img_url.startswith('http'):
                        img_url = f"https://www.sportovistevcr.cz{img_url}"
                    images.append(img_url)
            
            # Sestavení výsledného objektu
            facility = {
                "name": name,
                "description": description,
                "address": address,
                "city": city,
                "postalCode": postal_code,
                "country": "Czech Republic",
                "phone": phone,
                "email": email,
                "website": website,
                "sports": sports,
                "amenities": amenities,
                "properties": properties,
                "isIndoor": is_indoor,
                "isOutdoor": is_outdoor,
                "hasParking": has_parking,
                "hasShowers": has_showers,
                "hasEquipmentRental": has_equipment_rental,
                "hasRestaurant": has_restaurant,
                "images": images,
                "openingHours": opening_hours,
                "source": "SportovisteVCR",
                "sourceUrl": url
            }
            
            return facility
            
        except Exception as e:
            print(f"Error scraping facility detail {url}: {e}")
            return None
    
    def save_to_json(self, filename="facilities.json"):
        """
        Uloží sesbíraná data do JSON souboru
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "facilities": self.facilities,
                "metadata": {
                    "count": len(self.facilities),
                    "timestamp": time.time(),
                    "date": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.facilities)} facilities to {filename}")
        
def main():
    """
    Hlavní funkce pro spuštění scraperu
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Scraper sportovišť v ČR')
    parser.add_argument('--source', choices=['fitmapa', 'sporteri', 'multisport', 'all'], 
                        default='all', help='Zdroj dat pro scraping')
    parser.add_argument('--limit', type=int, default=20, 
                        help='Maximální počet sportovišť na zdroj (default: 20)')
    parser.add_argument('--output', type=str, default='facilities.json',
                        help='Výstupní soubor (default: facilities.json)')
    parser.add_argument('--debug', action='store_true', help='Zapne debug výpisy')
    
    args = parser.parse_args()
    
    scraper = FacilityScraper(debug=args.debug)
    
    # Scraping ze zdroje podle parametru
    if args.source == 'fitmapa' or args.source == 'all':
        print(f"Scraping FitMapa (limit: {args.limit})...")
        scraper.scrape_fitmapa(limit=args.limit)
    
    # Scraping ze Sporteri
    if args.source == 'sporteri' or args.source == 'all':
        print(f"Scraping Sporteri (limit: {args.limit})...")
        scraper.scrape_sporteri(limit=args.limit)
    
    # Scraping z MultiSport mapy
    if args.source == 'multisport' or args.source == 'all':
        print(f"Scraping MultiSport (limit: {args.limit})...")
        scraper.scrape_multisport(limit=args.limit)
    
    # Uložení výsledků
    scraper.save_to_json(filename=args.output)
    print(f"Hotovo! Data uložena do {args.output}")

if __name__ == "__main__":
    main()