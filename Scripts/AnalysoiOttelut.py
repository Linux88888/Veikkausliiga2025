import requests
import re
import os
import datetime
import math
import numpy as np
from collections import defaultdict
import sys

# Lisätään Scripts-kansio Python-polkuun, jos se ei ole jo siellä
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Nyt importataan suhteellisesti
try:
    from Yleisölaskuri import parse_yleiso_data, parse_pelatut_ottelut
except ImportError:
    # Jos edelleen ei toimi, yritetään suoraa importtia
    print("Trying direct import...")
    from Scripts.Yleisölaskuri import parse_yleiso_data, parse_pelatut_ottelut

# Nykyinen päivämäärä ja aika
CURRENT_DATE = "2025-05-13 09:49:05"
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

# Funktio tulevien otteluiden parsimiseen
def parse_tulevat_ottelut(data):
    """Parsii tulevat ottelut markdown-datasta"""
    if not data:
        print("Error: tulevat_ottelut_data is empty or invalid.")
        return []
    
    upcoming_matches = []
    lines = data.splitlines()
    for line in lines:
        # Lisää tähän logiikka tulevien otteluiden parsimiseen
        upcoming_matches.append(line)
    return upcoming_matches

# Kehittynyt analysointifunktio
def advanced_analyze_matches(teams_data, upcoming_matches):
    """Analysoi joukkueiden tilastot ja tulevat ottelut"""
    analysis_results = {}
    for team in teams:
        if team in teams_data:
            team_stats = teams_data[team]
            # Lisää tähän analyysilogiikka
            analysis_results[team] = {
                "stats": team_stats,
                "analysis": "Analyysi perustuu saatavilla oleviin tietoihin"
            }
    return analysis_results

# Parsitaan ja päivitetään tiedot
print("Parsing team statistics...")
if yleiso_data:
    teams_data = parse_yleiso_data(yleiso_data)
else:
    print("Error: yleiso_data is empty or invalid.")
    teams_data = {}
    # Initialize empty data for teams
    for team in teams:
        teams_data[team] = {
            "koti_maaleja": 0,
            "vieras_maaleja": 0,
            "koti_ottelut": 0,
            "vieras_ottelut": 0,
            "koti_paastetty": 0,
            "vieras_paastetty": 0,
        }

print("Parsing played matches...")
# Käsitellään oikein Yleisölaskuri.py:n palauttama tuple
teams_data, played_matches = parse_pelatut_ottelut(pelatut_ottelut_data, teams_data)

print("Parsing upcoming matches...")
upcoming_matches = parse_tulevat_ottelut(tulevat_ottelut_data)

# Suoritetaan analyysit
analysis_results = advanced_analyze_matches(teams_data, upcoming_matches)

# Debug-tulostus
print("\n\nJOUKKUETIEDOT PÄIVITETTY:")
for team, data in teams_data.items():
    print(f"{team}: {data}")

# Tallennetaan analysoidut ottelut tiedostoon
with open('AnalysoidutOttelut.md', 'w', encoding='utf-8') as f:
    f.write("# Analysoidut Ottelut\n\n")
    f.write(f"Päivitetty: {CURRENT_DATE} käyttäjän {CURRENT_USER} toimesta\n\n")
    
    f.write("## Joukkuetilastot\n\n")
    for team, data in teams_data.items():
        f.write(f"### {team}\n")
        for key, value in data.items():
            f.write(f"- {key}: {value}\n")
        f.write("\n")
    
    f.write("## Analyysi\n\n")
    for team, analysis in analysis_results.items():
        f.write(f"### {team}\n")
        f.write(f"{analysis['analysis']}\n\n")
    
    f.write("## Tulevat ottelut\n\n")
    for match in upcoming_matches:
        f.write(f"- {match}\n")

print("Analysis complete and saved to AnalysoidutOttelut.md")
