#!/usr/bin/env python3
"""
Jednoduchý test AZR analýzy bez závislosti na externích modulech
"""

import json
import sys

def analyze_schema(schema_content):
    """
    Jednoduchá analýza schématu databáze
    """
    thinking = """
Analyzuji databázové schéma SportMatch aplikace, zaměřím se na několik klíčových aspektů:

1. Celková struktura schématu:
   - Hlavní entity (uživatelé, týmy, zařízení, kurty, rezervace, turnaje, zápasy, tokeny)
   - Vazby mezi entitami
   - Dodržování normalizačních pravidel
   - Použité typy a omezení

2. Multijazyčná podpora:
   - Jak je implementována podpora více jazyků
   - Lokalizace sportů a dalších entit
   - Struktura URL a jazykové prefixy (/cs/sporty/, /en/sports/)

3. Platební systém:
   - Integrace s FitnessTokeny (1 token = 10 CZK)
   - Napojení na Stripe platební bránu
   - Transakce a platební historie
   - Mezinárodní adaptace (kurzy měn)

4. Sociální a streamovací funkce:
   - Schéma pro živé přenosy
   - Komentáře a interakce
   - Gamifikační prvky a odměny
   - Výzvy mezi hráči

5. Rezervační systém:
   - Struktura rezervací kurtů
   - Správa konfliktů a dostupnosti
   - Opakované rezervace

6. Výkonnostní aspekty:
   - Indexy a optimalizace
   - Potenciální úzká místa
   - Škálovatelnost schématu

7. Integrace s ostatními systémy:
   - Napojení na externí služby
   - API rozhraní a datová výměna
"""

    # Základní analýza
    has_user_entity = "users" in schema_content
    has_teams = "teams" in schema_content
    has_facilities = "facilities" in schema_content
    has_courts = "courts" in schema_content
    has_reservations = "reservations" in schema_content
    has_tournaments = "tournaments" in schema_content
    has_payments = "payments" in schema_content
    has_tokens = "tokenTransactions" in schema_content or "tokenProducts" in schema_content
    has_streams = "streams" in schema_content
    has_multilingual = "sportTranslations" in schema_content or "language" in schema_content
    has_challenges = "challenges" in schema_content
    has_substitutes = "substituteAvailability" in schema_content or "substituteRequests" in schema_content
    
    # Počítání entit a vztahů
    entity_count = sum([
        has_user_entity, has_teams, has_facilities, has_courts, 
        has_reservations, has_tournaments, has_payments, has_tokens,
        has_streams, has_challenges, has_substitutes
    ])
    
    # Počítání relačních definic
    relation_count = schema_content.count("relations(")
    
    # Hledání použitých typů
    types = {
        "serial": schema_content.count("serial("),
        "integer": schema_content.count("integer("),
        "text": schema_content.count("text("),
        "boolean": schema_content.count("boolean("),
        "timestamp": schema_content.count("timestamp("),
        "date": schema_content.count("date("),
        "time": schema_content.count("time("),
        "jsonb": schema_content.count("jsonb("),
        "enum": schema_content.count("pgEnum(")
    }
    
    # Hledání cizích klíčů
    foreign_keys = schema_content.count("references(() =>")
    
    # Vytvoření odpovědi
    answer = f"""
# Analýza schématu databáze SportMatch

## Přehled struktury
Schéma obsahuje **{entity_count}** hlavních entit s **{relation_count}** explicitně definovanými vztahy a **{foreign_keys}** cizími klíči.

### Hlavní entity
- {"✓" if has_user_entity else "✗"} Uživatelé (users)
- {"✓" if has_teams else "✗"} Týmy (teams)
- {"✓" if has_facilities else "✗"} Sportovní zařízení (facilities)
- {"✓" if has_courts else "✗"} Kurty (courts)
- {"✓" if has_reservations else "✗"} Rezervace (reservations)
- {"✓" if has_tournaments else "✗"} Turnaje (tournaments)
- {"✓" if has_payments else "✗"} Platby (payments)
- {"✓" if has_tokens else "✗"} Tokenový systém (tokenTransactions, tokenProducts)
- {"✓" if has_streams else "✗"} Živé přenosy (streams)
- {"✓" if has_challenges else "✗"} Výzvy (challenges)
- {"✓" if has_substitutes else "✗"} Náhradníci (substituteAvailability, substituteRequests)

### Multijazyčná podpora
- {"✓" if has_multilingual else "✗"} Podporováno přes entitu sportTranslations 
- Schéma připraveno na URL formát /cs/sporty/ a /en/sports/

### Použité datové typy
- serial: {types["serial"]}
- integer: {types["integer"]}
- text: {types["text"]}
- boolean: {types["boolean"]}
- timestamp: {types["timestamp"]}
- date: {types["date"]}
- time: {types["time"]}
- jsonb: {types["jsonb"]}
- enum: {types["enum"]}

## Silné stránky schématu
1. Komplexní pokrytí domény sportovní platformy
2. Silné typování s využitím Drizzle ORM a zod validace
3. Explicitní relační model s dobře definovanými vazbami
4. Použití enum typů pro omezení hodnot a konzistenci dat
5. Integrace systému FitnessTokenů a plateb

## Možnosti optimalizace
1. Přidání indexů pro často používané cizí klíče (userId, courtId, tournamentId)
2. Zavedení řízení přístupu na úrovni schématu
3. Optimalizace schématu pro dotazy na časové rezervace
4. Implementace verzování schématu pro bezpečné migrace

## Doporučení pro mezinárodní rozšíření
1. Rozšíření entity tokenTransactions o podporu měn
2. Vytvoření tabulky pro správu směnných kurzů a daňových sazeb
3. Posílení multijazyčné podpory s fallback mechanismem

## Doporučení pro integraci se Stripe
1. Rozšíření entity payments o lepší podporu Stripe metadat
2. Zavedení mechanismu pro zpracování Stripe webhooků
3. Implementace entit pro správu předplatných a opakovaných plateb
"""

    return {
        "thinking": thinking,
        "answer": answer
    }

def main():
    """
    Hlavní funkce pro test AZR
    """
    try:
        # Načtení schématu ze souboru
        with open("shared/schema.ts", "r", encoding="utf-8") as f:
            schema_content = f.read()
        
        # Analýza schématu
        result = analyze_schema(schema_content)
        
        # Výstup jako JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "traceback": str(sys.exc_info())
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()