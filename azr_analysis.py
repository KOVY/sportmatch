#!/usr/bin/env python3
# coding: utf-8

from azr.absolute_zero_reasoner import AbsoluteZeroReasoner

# Inicializace AZR
azr = AbsoluteZeroReasoner()

# Vytvořit textový vstup pro AZR
query = """
# SportMatch: Analýza architektury a UX/UI optimalizace

## Kontext projektu
SportMatch je komplexní sportovní platforma, která propojuje hráče, trenéry, sportoviště a sportovní komunitu. Aplikace je vyvíjena v React.js s TypeScript a používá TailwindCSS pro styling. Platforma podporuje více jazyků, začínaje angličtinou a češtinou.

## Hlavní komponenty

### Layouty
- AppLayout: Hlavní layout, který poskytuje základní strukturu stránky, včetně navigace a zápatí
- SportLayout: Specializovaný layout pro sportovní sekce s vlastní navigací pro sportovní stránky
- CzechLayout: Layout pro české stránky
- EnglishLayout: Layout pro anglické stránky

### Problémy
1. Duplicitní vykreslování komponent (Navbar, Footer) - některé komponenty jsou importovány a vykreslovány vícekrát v různých layoutech
2. Nedostatečná standardizace cest a URL struktur mezi různými jazykovými verzemi
3. Neoptimalizovaný mobilní UX

## Otázky
1. Jaká je optimální struktura layoutů pro eliminaci duplicitního vykreslování?
2. Jak nejlépe organizovat vícejazyčný obsah z pohledu UX/UI?
3. Jaké výkonnostní optimalizace bys doporučil pro tuto aplikaci?
4. Jak vylepšit responsivní design aplikace?
5. Jaký je ideální workflow pro vývoj nových funkcí v tomto kontextu?
"""

# Analýza pomocí AZR
result = azr.reason(query)

# Vypsat myšlenkový proces
print("=" * 50)
print("ANALÝZA AZR:")
print("=" * 50)
print(result["thinking"])
print("\n\n")

# Vypsat odpověď
print("=" * 50)
print("ODPOVĚĎ AZR:")
print("=" * 50)
print(result["answer"])