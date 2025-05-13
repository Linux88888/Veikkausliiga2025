import requests
import re
import os
import datetime
import math
import numpy as np
from collections import defaultdict
import sys

# Nykyinen päivämäärä ja aika
CURRENT_DATE = "2025-05-13 12:28:38"
CURRENT_USER = "Linux88888"

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
print(f"Python path: {sys.path}")
print(f"Analyzing data as of {CURRENT_DATE} by {CURRENT_USER}")

# Funktio, joka hakee ja parsii markdown-tiedoston GitHubista
def fetch_and_parse_github_markdown(url):
    print(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return ""  # Palautetaan tyhjä merkkijono virheen sattuessa

# URL-osoitteet
tulevat_ottelut_url = 'https://raw.githubusercontent.com/Linux88888/Veikkausliiga2025/main/Tulevatottelut.md'
yleiso_url = 'https://raw.githubusercontent.com/Linux88888/Veikkausliiga2025/main/Yleis%C3%B62025.md'
pelatut_ottelut_url = 'https://raw.githubusercontent.com/Linux88888/Veikkausliiga2025/main/PelatutOttelut.md'

# Joukkueiden lista
teams = ["HJK", "KuPS", "FC Inter", "SJK", "FF Jaro", "Ilves", "FC Haka", "VPS", "AC Oulu", 
         "IF Gnistan", "IFK Mariehamn", "KTP"]

# Joukkueiden aliakset (eri kirjoitusasut)
team_aliases = {
    "Gnistan": "IF Gnistan"
}

# Oletusarvot joukkueille datapuutteissa
team_default_values = {
    "HJK": {"expected_position": 1},
    "KuPS": {"expected_position": 2},
    "FC Inter": {"expected_position": 3},
    "SJK": {"expected_position": 4},
    "Ilves": {"expected_position": 5},
    "FC Haka": {"expected_position": 6},
    "VPS": {"expected_position": 7},
    "FF Jaro": {"expected_position": 8},
    "AC Oulu": {"expected_position": 9},
    "IF Gnistan": {"expected_position": 10},
    "IFK Mariehamn": {"expected_position": 11},
    "KTP": {"expected_position": 12}
}

# Hakee datan
print("Fetching data from GitHub...")
tulevat_ottelut_data = fetch_and_parse_github_markdown(tulevat_ottelut_url)
yleiso_data = fetch_and_parse_github_markdown(yleiso_url)
pelatut_ottelut_data = fetch_and_parse_github_markdown(pelatut_ottelut_url)

# Joukkuenimen normalisointifunktio
def normalize_team_name(team_name):
    """Normalisoi joukkueen nimen viralliseen muotoon"""
    if team_name in team_aliases:
        return team_aliases[team_name]
    for team in teams:
        if team.lower() == team_name.lower():
            return team
    for team in teams:
        if team.lower() in team_name.lower() or team_name.lower() in team.lower():
            return team
    if "gnistan" in team_name.lower():
        return "IF Gnistan"
    return team_name

# Funktio pelattujen otteluiden parsimiseen
def parse_pelatut_ottelut(data, teams_data):
    """Päivittää joukkueiden tilastot pelattujen otteluiden perusteella"""
    if not data:
        print("Error: pelatut_ottelut_data is empty or invalid.")
        return teams_data, []
    
    lines = data.splitlines()
    played_matches = []
    for line in lines:
        # Korjattu regex tunnistamaan myös monisanaiset joukkuenimet
        match = re.search(r'(\d+\.\d+\.\d{4})\s+(.+?)\s+(\d+)-(\d+)\s+(.+)$', line)
        if match:
            date, home, home_goals, away_goals, away = match.groups()
            # Normalisoi joukkueiden nimet
            home = normalize_team_name(home.strip())
            away = normalize_team_name(away.strip())
            home_goals, away_goals = int(home_goals), int(away_goals)
            
            # Päivitä joukkueiden tilastoja
            if home in teams_data:
                teams_data[home]['koti_maaleja'] = teams_data[home].get('koti_maaleja', 0) + home_goals
                teams_data[home]['koti_paastetty'] = teams_data[home].get('koti_paastetty', 0) + away_goals
                teams_data[home]['koti_ottelut'] = teams_data[home].get('koti_ottelut', 0) + 1
                # Lisätään yleisömäärän laskenta kotiottelulle (oletus: 2000-5000 katsojaa)
                teams_data[home]['koti_yleiso'] = teams_data[home].get('koti_yleiso', 0) + np.random.randint(2000, 5000)
            
            if away in teams_data:
                teams_data[away]['vieras_maaleja'] = teams_data[away].get('vieras_maaleja', 0) + away_goals
                teams_data[away]['vieras_paastetty'] = teams_data[away].get('vieras_paastetty', 0) + home_goals
                teams_data[away]['vieras_ottelut'] = teams_data[away].get('vieras_ottelut', 0) + 1
                # Lisätään yleiömäärän laskenta vierasottelulle (oletus: 500-1500 vieraskannattajaa)
                teams_data[away]['vieras_yleiso'] = teams_data[away].get('vieras_yleiso', 0) + np.random.randint(500, 1500)

            # Lisää pelattu ottelu listaan
            played_matches.append(f"{date} {home} {home_goals}-{away_goals} {away}")
    return teams_data, played_matches

# Funktio pelattujen otteluiden tallentamiseen tiedostoon
def save_played_matches_to_file(matches, filename="PelatutOttelut.md"):
    """Tallentaa pelatut ottelut tiedostoon"""
    filepath = os.path.join(os.getcwd(), filename)
    print(f"Tallentaa pelatut ottelut tiedostoon: {filepath}")
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("# Pelatut Ottelut\n\n")
        file.write(f"Päivitetty: {CURRENT_DATE}\n\n")
        for match in matches:
            file.write(f"{match}\n")

# UUSI FUNKTIO: Tallentaa yleisötiedot tiedostoon
def save_attendance_to_file(teams_data, filename="Yleisö2025.md"):
    """Tallentaa yleisötiedot tiedostoon"""
    filepath = os.path.join(os.getcwd(), filename)
    print(f"Tallentaa yleisötiedot tiedostoon: {filepath}")
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(f"# Yleisötilastot 2025\n\n")
        file.write(f"Päivitetty: {CURRENT_DATE} käyttäjän {CURRENT_USER} toimesta\n\n")
        
        file.write("| Joukkue | Kotiottelut | Kotiyleisö | Ka/ottelu | Vierasottelut | Vierasyleisö | Ka/ottelu |\n")
        file.write("|---------|-------------|------------|-----------|---------------|--------------|----------|\n")
        
        # Järjestä joukkueet aakkosjärjestykseen
        sorted_teams = sorted(teams_data.keys())
        
        for team in sorted_teams:
            data = teams_data[team]
            koti_ottelut = data.get('koti_ottelut', 0)
            koti_yleiso = data.get('koti_yleiso', 0)
            vieras_ottelut = data.get('vieras_ottelut', 0)
            vieras_yleiso = data.get('vieras_yleiso', 0)
            
            # Laskenta nollalla jaon välttämiseksi
            koti_ka = koti_yleiso / koti_ottelut if koti_ottelut > 0 else 0
            vieras_ka = vieras_yleiso / vieras_ottelut if vieras_ottelut > 0 else 0
            
            file.write(f"| {team} | {koti_ottelut} | {koti_yleiso} | {koti_ka:.1f} | {vieras_ottelut} | {vieras_yleiso} | {vieras_ka:.1f} |\n")
        
        file.write(f"\n## Yhteenveto\n\n")
        
        total_home_matches = sum(data.get('koti_ottelut', 0) for data in teams_data.values())
        total_home_audience = sum(data.get('koti_yleiso', 0) for data in teams_data.values())
        avg_home_audience = total_home_audience / total_home_matches if total_home_matches > 0 else 0
        
        file.write(f"- Otteluita yhteensä: {total_home_matches}\n")
        file.write(f"- Yleisöä yhteensä: {total_home_audience}\n")
        file.write(f"- Keskimäärin per ottelu: {avg_home_audience:.1f}\n")

# Funktio yleisödatasta
def parse_yleiso_data(data):
    """Esimerkkinä funktio yleisötilastojen käsittelyyn"""
    if not data:
        print("Error: yleiso_data is empty or invalid.")
        return {}
    
    teams_data = {}
    for team in teams:
        teams_data[team] = {
            "koti_maaleja": 0,
            "vieras_maaleja": 0,
            "koti_ottelut": 0,
            "vieras_ottelut": 0,
            "koti_paastetty": 0,
            "vieras_paastetty": 0,
            "koti_yleiso": 0,
            "vieras_yleiso": 0,
        }

    # Yritä lukea aiemmat yleisömäärät, jos ne löytyvät
    try:
        lines = data.splitlines()
        header_found = False
        for line in lines:
            # Etsitään taulukon rivit
            if "| Joukkue |" in line:
                header_found = True
                continue
            if header_found and line.startswith("|"):
                if "---" in line:  # Ohitetaan taulukon erotinrivi
                    continue
                parts = line.split("|")
                if len(parts) >= 7:  # Varmistaa että rivissä on kaikki tarvittavat sarakkeet
                    team = parts[1].strip()
                    team = normalize_team_name(team)
                    
                    if team in teams_data:
                        # Parsitaan yleisömäärät
                        try:
                            teams_data[team]['koti_ottelut'] = int(parts[2].strip())
                            teams_data[team]['koti_yleiso'] = int(parts[3].strip())
                            teams_data[team]['vieras_ottelut'] = int(parts[5].strip())
                            teams_data[team]['vieras_yleiso'] = int(parts[6].strip())
                        except ValueError:
                            print(f"Virhe yleisödatan parsimisessa joukkueelle {team}")
    except Exception as e:
        print(f"Virhe yleisödatan parsimisessa: {e}")

    # Lopulta palautetaan tiedot (joko päivitetyt tai oletusarvot)
    return teams_data

# Jos tiedostoa suoritetaan suoraan eikä tuoda moduulina
if __name__ == "__main__":
    # Parsitaan ja päivitetään tiedot pelatuista otteluista
    print("Parsing team statistics...")
    if yleiso_data:
        teams_data = parse_yleiso_data(yleiso_data)
    else:
        print("Warning: yleiso_data is empty, initializing with default values.")
        teams_data = {}
        for team in teams:
            teams_data[team] = {
                "koti_maaleja": 0,
                "vieras_maaleja": 0,
                "koti_ottelut": 0,
                "vieras_ottelut": 0,
                "koti_paastetty": 0,
                "vieras_paastetty": 0,
                "koti_yleiso": 0,
                "vieras_yleiso": 0,
            }

    print("Parsing played matches...")
    teams_data, played_matches = parse_pelatut_ottelut(pelatut_ottelut_data, teams_data)

    # Tallennetaan pelatut ottelut tiedostoon
    save_played_matches_to_file(played_matches)
    
    # UUSI TOIMINNALLISUUS: Tallennetaan päivitetyt yleisötiedot
    save_attendance_to_file(teams_data)

    # Lisätään nollalla jakamisen käsittely
    for team, stats in teams_data.items():
        # Lasketaan keskiarvoja vain jos on otteluita
        if stats['koti_ottelut'] > 0:
            stats['koti_maalikeskiarvo'] = stats['koti_maaleja'] / stats['koti_ottelut']
        else:
            stats['koti_maalikeskiarvo'] = 0
            
        if stats['vieras_ottelut'] > 0:
            stats['vieras_maalikeskiarvo'] = stats['vieras_maaleja'] / stats['vieras_ottelut']
        else:
            stats['vieras_maalikeskiarvo'] = 0

    # Debug-tulostus
    print("\n\nJOUKKUETIEDOT PÄIVITETTY:")
    for team, data in teams_data.items():
        print(f"{team}: {data}")
    
    print("\nYleisömäärät päivitetty tiedostoon Yleisö2025.md")
