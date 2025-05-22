"""
Jednoduchá analýza aplikace SportMatch

Tento skript provádí analýzu aplikace SportMatch s důrazem na českou jazykovou verzi
a poskytuje doporučení pro další vývoj.
"""

import os
import sys
import re
import json
from typing import Dict, List, Any, Optional

def analyze_app_structure():
    """Analyzuje strukturu aplikace"""
    czech_pages = []
    english_pages = []
    
    # Hledání stránek
    for root, dirs, files in os.walk("./client/src/pages"):
        for file in files:
            if file.endswith(".tsx") or file.endswith(".jsx"):
                path = os.path.join(root, file)
                if "/cs/" in path:
                    czech_pages.append(path)
                elif "/en/" in path:
                    english_pages.append(path)
    
    # Analýza komponent
    components_dir = "./client/src/components"
    components_count = 0
    if os.path.exists(components_dir):
        for root, dirs, files in os.walk(components_dir):
            for file in files:
                if file.endswith(".tsx") or file.endswith(".jsx"):
                    components_count += 1
    
    return {
        "czech_pages": czech_pages,
        "czech_pages_count": len(czech_pages),
        "english_pages": english_pages,
        "english_pages_count": len(english_pages),
        "components_count": components_count
    }

def analyze_language_support():
    """Analyzuje podporu jazyků"""
    lang_components = []
    
    # Hledání jazykových komponent
    for root, dirs, files in os.walk("./client/src/components/language"):
        for file in files:
            if file.endswith(".tsx") or file.endswith(".jsx"):
                lang_components.append(os.path.join(root, file))
    
    # Kontrola i18n
    i18n_path = "./client/src/i18n.ts"
    supported_langs = []
    
    if os.path.exists(i18n_path):
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()
            langs_match = re.search(r"supportedLngs:\s*\[(.*?)\]", content, re.DOTALL)
            if langs_match:
                langs_str = langs_match.group(1)
                supported_langs = [l.strip().strip("'\"") for l in langs_str.split(",")]
    
    return {
        "language_components": lang_components,
        "supported_languages": supported_langs
    }

def analyze_czech_implementation():
    """Analyzuje implementaci české verze"""
    czech_routes = []
    czech_components = []
    
    # Hledání českých route
    routes_path = "./client/src/hooks/use-routes.ts"
    if os.path.exists(routes_path):
        with open(routes_path, "r", encoding="utf-8") as f:
            content = f.read()
            czech_routes_matches = re.findall(r"['\"]\/cs\/[^'\"]+['\"]", content)
            czech_routes = list(set(czech_routes_matches))
    
    # Hledání českých komponent
    for root, dirs, files in os.walk("./client/src/components"):
        for file in files:
            if file.endswith(".tsx") or file.endswith(".jsx"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "lang === 'cs'" in content or 'lang = "cs"' in content or 'cs?' in content:
                        czech_components.append(path)
    
    return {
        "czech_routes": czech_routes,
        "czech_components": czech_components
    }

def analyze_ui_consistency():
    """Analyzuje konzistenci uživatelského rozhraní"""
    design_system_usage = 0
    tailwind_usage = 0
    card_components = 0
    
    # Procházení souborů komponent
    for root, dirs, files in os.walk("./client/src/components"):
        for file in files:
            if file.endswith(".tsx") or file.endswith(".jsx"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Kontrola použití komponent a stylů
                    if "from \"@/components/ui/" in content:
                        design_system_usage += 1
                    if "className=" in content:
                        tailwind_usage += 1
                    if "Card" in content:
                        card_components += 1
    
    return {
        "design_system_usage": design_system_usage,
        "tailwind_usage": tailwind_usage,
        "card_components": card_components,
    }

def generate_recommendations(analysis_data):
    """Generuje doporučení na základě analýzy"""
    czech_ratio = analysis_data["structure"]["czech_pages_count"] / (analysis_data["structure"]["english_pages_count"] or 1)
    
    recommendations = []
    strengths = []
    
    # Silné stránky
    if czech_ratio >= 0.8:
        strengths.append("Dobrá úroveň překladů do češtiny (téměř stejný počet stránek jako v angličtině)")
    if len(analysis_data["language"]["supported_languages"]) >= 5:
        strengths.append(f"Široká podpora jazyků ({len(analysis_data['language']['supported_languages'])} jazyků)")
    if len(analysis_data["czech_impl"]["czech_routes"]) >= 5:
        strengths.append("Dostatečné množství českých routů v aplikaci")
    if analysis_data["ui"]["design_system_usage"] >= 15:
        strengths.append("Konzistentní použití designového systému")
    
    # Doporučení
    if czech_ratio < 0.8:
        recommendations.append({
            "title": "Rozšířit českou lokalizaci",
            "description": "Dokončit překlad všech stránek do češtiny pro lepší uživatelský zážitek lokálních uživatelů."
        })
    
    if analysis_data["ui"]["design_system_usage"] < 15:
        recommendations.append({
            "title": "Sjednotit designový systém",
            "description": "Zvýšit používání UI komponent z designového systému pro větší konzistenci."
        })
    
    if len(analysis_data["czech_impl"]["czech_components"]) < 10:
        recommendations.append({
            "title": "Vylepšit podmíněný rendering pro češtinu",
            "description": "Přidat více podmíněných renderovacích bloků založených na jazyku pro specifické české prvky."
        })
    
    # Obecná doporučení
    recommendations.extend([
        {
            "title": "Optimalizace načítání obrázků",
            "description": "Implementovat lazy loading a placeholdery pro všechny obrázky v aplikaci včetně sportovišť."
        },
        {
            "title": "Uživatelské testování české verze",
            "description": "Provést testování s českými uživateli pro identifikaci problémů s UX specifických pro českou lokalizaci."
        },
        {
            "title": "Propojení funkcí",
            "description": "Lépe propojit různé funkce aplikace, například sportovní zařízení s rezervačním systémem a matchmakingem."
        }
    ])
    
    return {
        "strengths": strengths,
        "recommendations": recommendations
    }

def main():
    """Hlavní funkce"""
    print("Analyzuji aplikaci SportMatch...", file=sys.stderr)
    
    # Provedení analýz
    structure_analysis = analyze_app_structure()
    language_analysis = analyze_language_support()
    czech_implementation = analyze_czech_implementation()
    ui_consistency = analyze_ui_consistency()
    
    # Sestavení výsledků
    analysis_data = {
        "structure": structure_analysis,
        "language": language_analysis,
        "czech_impl": czech_implementation,
        "ui": ui_consistency
    }
    
    # Generování doporučení
    recommendations = generate_recommendations(analysis_data)
    
    # Výsledná zpráva
    result = {
        "title": "Analýza SportMatch aplikace",
        "summary": f"Aplikace má {structure_analysis['components_count']} komponent, {structure_analysis['czech_pages_count']} českých stránek a {structure_analysis['english_pages_count']} anglických stránek.",
        "strengths": recommendations["strengths"],
        "recommendations": recommendations["recommendations"],
        "timestamp": "2025-05-15"
    }
    
    # Výstup jako JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()