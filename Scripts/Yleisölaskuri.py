import requests
import re
import os
import datetime
import math
import numpy as np
from collections import defaultdict

# Nykyinen päivämäärä ja aika
CURRENT_DATE = "2025-05-07 09:52:44"
CURRENT_USER = "Linux88888"

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
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
        return ""

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
    lines = data.splitlines()
    played_matches = []
    for line in lines:
        # Esimerkki: Riviformaatti "15.04.2025 HJK 2-1 KuPS"
        match = re.search(r'(\d+\.\d+\.\d{4})\s+(\w+)\s+(\d+)-(\d+)\s+(\w+)', line)
        if match:
            date, home, home_goals, away_goals, away = match.groups()
            home_goals, away_goals = int(home_goals), int(away_goals)
            
            # Päivitä joukkueiden tilastoja
            if home in teams_data:
                teams_data[home]['koti_maaleja'] = teams_data[home].get('koti_maaleja', 0) + home_goals
                teams_data[home]['koti_paastetty'] = teams_data[home].get('koti_paastetty', 0) + away_goals
                teams_data[home]['koti_ottelut'] = teams_data[home].get('koti_ottelut', 0) + 1
            
            if away in teams_data:
                teams_data[away]['vieras_maaleja'] = teams_data[away].get('vieras_maaleja', 0) + away_goals
                teams_data[away]['vieras_paastetty'] = teams_data[away].get('vieras_paastetty', 0) + home_goals
                teams_data[away]['vieras_ottelut'] = teams_data[away].get('vieras_ottelut', 0) + 1

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
        for match in matches:
            file.write(f"{match}\n")

# Funktio yleisödatasta
def parse_yleiso_data(data):
    """Esimerkkinä funktio yleisötilastojen käsittelyyn"""
    teams_data = {}
    for team in teams:
        teams_data[team] = {
            "koti_maaleja": 0,
            "vieras_maaleja": 0,
            "koti_ottelut": 0,
            "vieras_ottelut": 0,
        }
    # Lisää logiikka yleisödatan käsittelyyn
    return teams_data

# Parsitaan ja päivitetään tiedot pelatuista otteluista
print("Parsing team statistics...")
teams_data = parse_yleiso_data(yleiso_data)
print("Parsing played matches...")
teams_data, played_matches = parse_pelatut_ottelut(pelatut_ottelut_data, teams_data)

# Tallennetaan pelatut ottelut tiedostoon
save_played_matches_to_file(played_matches)

# Debug-tulostus
print("\n\nJOUKKUETIEDOT PÄIVITETTY:")
for team, data in teams_data.items():
    print(f"{team}: {data}")
