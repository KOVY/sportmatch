# Scraping sportovišť pro SportMatch

Tento nástroj umožňuje automatický sběr dat o sportovištích v České republice z veřejně dostupných zdrojů. Získaná data je možné importovat přímo do databáze SportMatch.

## Podporované zdroje

1. **SportovisteVCR.cz** - kompletní scraper
2. **KdeSportovat.cz** - kompletní scraper
3. **SportCentral.cz** - kompletní scraper

## Použití

### Jednoduchý způsob (scraping + import)

Pro stažení dat a jejich automatický import do databáze použijte připravený skript:

```bash
./scrape_and_import.sh [zdroj] [limit]
```

Parametry:
- `zdroj` - sportovistevcr, kdesportovat, sportcentral nebo all (default: all)
- `limit` - maximální počet sportovišť na zdroj (default: 30)

Příklady:
```bash
# Stáhne max. 30 sportovišť z každého zdroje
./scrape_and_import.sh

# Stáhne pouze data z SportovisteVCR (max. 50 sportovišť)
./scrape_and_import.sh sportovistevcr 50

# Stáhne max. 10 sportovišť z KdeSportovat
./scrape_and_import.sh kdesportovat 10
```

### Pokročilé použití (samostatné kroky)

#### 1. Scraping dat

```bash
python scrape_facilities.py --source [zdroj] --limit [počet] --output [soubor.json] --debug
```

Parametry:
- `--source` - sportovistevcr, kdesportovat, sportcentral nebo all (default: all)
- `--limit` - maximální počet sportovišť na zdroj (default: 20)
- `--output` - název výstupního souboru (default: facilities.json)
- `--debug` - zapnutí debug výpisů

#### 2. Import dat do databáze

```bash
node import_scraped_facilities.js [soubor.json]
```

Parametr:
- `soubor.json` - cesta k souboru s daty (default: ./facilities.json)

## Struktura dat

Každé sportoviště obsahuje následující informace:

```json
{
  "name": "Název sportoviště",
  "description": "Popis sportoviště",
  "address": "Plná adresa",
  "city": "Město",
  "postalCode": "PSČ",
  "country": "Czech Republic",
  "phone": "Telefon",
  "email": "E-mail",
  "website": "Web",
  "sports": ["TEN", "BAD"],
  "amenities": ["showers", "equipment_rental"],
  "properties": ["indoor", "parking"],
  "isIndoor": true,
  "isOutdoor": false,
  "hasParking": true,
  "hasShowers": true,
  "hasEquipmentRental": true,
  "hasRestaurant": false,
  "images": ["url1", "url2"],
  "source": "SportovisteVCR",
  "sourceUrl": "http://..."
}
```

## Aktualizace a rozšíření

Scraper podporuje 15 sportů v aktuální verzi. Při importu dochází automaticky k deduplikaci dat, takže je možné scraper spouštět opakovaně a získávat tak aktuální data. Pokud sportoviště již existuje v databázi, dojde k aktualizaci jeho informací.

## Poznámky

- Scraper respektuje pravidla robots.txt
- Scraper používá uměřené časové prodlevy mezi dotazy (1-1.5 sekundy)
- Scraper neobchází žádné ochrany webů
- Data jsou získávána pouze z veřejně dostupných zdrojů