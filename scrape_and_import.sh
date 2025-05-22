#!/bin/bash
# Script pro automatické stažení dat sportovišť a jejich import do databáze
# Použití: ./scrape_and_import.sh [source] [limit]

# Výchozí hodnoty
SOURCE=${1:-"all"}
LIMIT=${2:-30}
OUTPUT_FILE="facilities.json"

echo "🔍 Scraping sportovišť - zdroj: $SOURCE, limit: $LIMIT"

# Spuštění scraperu pro získání dat
python scrape_facilities.py --source $SOURCE --limit $LIMIT --output $OUTPUT_FILE

# Kontrola, zda scraper proběhl úspěšně
if [ $? -ne 0 ]; then
  echo "❌ Scraping selhal, import nebude proveden."
  exit 1
fi

echo "✅ Scraping dokončen, data uložena do $OUTPUT_FILE"
echo "-------------------------------------------------"
echo "📥 Importuji data do databáze"

# Import dat do databáze
node import_scraped_facilities.js $OUTPUT_FILE

# Kontrola, zda import proběhl úspěšně
if [ $? -ne 0 ]; then
  echo "❌ Import selhal."
  exit 1
fi

echo "✅ Import dokončen"
echo "-------------------------------------------------"
echo "🎉 Proces kompletně dokončen. Sportoviště jsou dostupná v databázi."