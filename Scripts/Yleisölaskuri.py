import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
import sys

# Ota käyttöön testausmoodi
DEBUG = True

def get_current_season_matches():
    # Päivitä tämä URL oikeaan kauteen
    url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
    
    # Päivitetty User-Agent ja headerit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "fi-FI,fi;q=0.9",
        "Referer": "https://www.veikkausliiga.com/",
    }

    try:
        print(f"🔄 Yritetään hakea dataa osoitteesta: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        if DEBUG:
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Debug-sivu tallennettu: debug_page.html")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Etsi kaikki mahdolliset ottelukontit
        possible_match_containers = [
            *soup.find_all('div', class_='match-card'),  # Uusi rakenne
            *soup.find_all('tr', class_='match-row'),     # Vanha taulukkorakenne
            *soup.find_all('div', class_='event-item')    # Vaihtoehtoinen luokka
        ]

        if not possible_match_containers:
            raise ValueError(
                "❌ Ei löydetty otteluita. Syyt voivat olla:\n"
                "1. Kausi 2025 ei ole alkanut\n"
                "2. Sivuston rakenne on muuttunut\n"
                "3. Data haetaan JavaScriptillä\n"
                "➡️ Tarkista debug_page.html tiedosto"
            )

        print(f"🔍 Löytyi {len(possible_match_containers)} mahdollista ottelua")

        # Analysoi debug_page.html sisältö manuaalisesti
        print("\n⛑️ ONGELMANRATKAISUOHJE:")
        print("1. Avaa debug_page.html selaimessa")
        print("2. Etsi ottelutiedot")
        print("3. Tarkista seuraavat elementit:")
        print("   - Löytyykö 'match-card', 'match-row' tai 'event-item' luokkia?")
        print("   - Mikä on oikea CSS-selektori?")
        print("4. Päivitä koodi löydettyjen tietojen mukaan")

        return []

    except Exception as e:
        print(f"❌ Kriittinen virhe: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    matches = get_current_season_matches()
    print(f"✅ Prosessoitu {len(matches)} ottelua")
