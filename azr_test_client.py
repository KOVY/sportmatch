import requests
import json
import sys
import os

# URL AZR serveru
AZR_URL = "https://2c6c3603-088c-42f0-bdaa-7060ac52f4a8-00-oj4o4gixcson.kirk.replit.dev/en/azr-assistant"

def send_query_to_azr(query):
    """
    Posílá dotaz na AZR server a vrací odpověď.
    """
    try:
        # Příprava dat pro požadavek
        payload = {"query": query}
        headers = {"Content-Type": "application/json"}

        # Odeslání POST požadavku na AZR
        response = requests.post(AZR_URL, json=payload, headers=headers, timeout=20)

        # Kontrola, zda požadavek proběhl úspěšně
        if response.status_code == 200:
            result = response.json().get("response", "AZR vrátil prázdnou odpověď.")
            return {"response": result, "status": "success"}
        else:
            error_msg = f"Chyba: AZR vrátil status {response.status_code}. Text: {response.text}"
            return {"response": error_msg, "status": "error"}
    except requests.exceptions.RequestException as e:
        error_msg = f"Chyba při komunikaci s AZR: {str(e)}"
        return {"response": error_msg, "status": "error"}

def main():
    # Použití dotazu z příkazové řádky, pokud je k dispozici
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        # Testovací dotaz
        query = "Napiš Python funkci, která vrátí součet seznamu čísel. Vrať pouze kód, žádné vysvětlení."
    
    # Posílání dotazu do AZR
    result = send_query_to_azr(query)
    
    # Výstup jako JSON pro snazší zpracování v nodejs
    print(json.dumps(result))
    
    # Návratový kód 0 pro úspěch, 1 pro chybu (použitelné při volání z nodejs)
    sys.exit(0 if result["status"] == "success" else 1)

if __name__ == "__main__":
    main()