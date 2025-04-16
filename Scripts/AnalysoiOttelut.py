import requests
import re
import os
import datetime
import math
import random
import numpy as np
from collections import defaultdict

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

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
# Voimme simuloida historiaa ja sarjataulukon tietoja
history_data = {}  # Tässä olisi todellisessa toteutuksessa historiadata

# Joukkueiden lista
teams = ["HJK", "KuPS", "FC Inter", "SJK", "FF Jaro", "Ilves", "FC Haka", "VPS", "AC Oulu", 
         "Gnistan", "IF Gnistan", "IFK Mariehamn", "KTP"]

# Hakee datan
print("Fetching data from GitHub...")
tulevat_ottelut_data = fetch_and_parse_github_markdown(tulevat_ottelut_url)
yleiso_data = fetch_and_parse_github_markdown(yleiso_url)

# Täysin uudistettu funktio, joka parsii tulevat ottelut datan
def parse_tulevat_ottelut(data):
    ottelut = []
    lines = data.splitlines()
    
    current_date = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Etsi päivämäärä
        date_match = re.search(r'(\d+\.\d+\.\d{4})', line)
        if date_match:
            current_date = date_match.group(1)
            print(f"Found date: {current_date}")
            
        # Etsi Seuranta-sanalla merkityt ottelurivit
        if "Seuranta" in line:
            # Tarkista eri formaatit
            if " - " in line:
                parts = line.split(" - ")
                
                # Formaatti 1: "15:00 - VPS - FC Inter - Seuranta"
                if len(parts) >= 4 and is_time_format(parts[0]):
                    aika = parts[0].strip()
                    koti = parts[1].strip()
                    vieras = parts[2].strip()
                    
                # Formaatti 2: "14 - - 17:00 - 17:00 - FC Haka - AC Oulu - Seuranta"
                elif len(parts) >= 6 and is_time_format(parts[3]):
                    aika = parts[3].strip()
                    koti = parts[4].strip()
                    vieras = parts[5].strip()
                else:
                    continue
                
                # Tarkista, että löydetyt joukkueet ovat valideja
                if is_valid_team(koti) and is_valid_team(vieras):
                    ottelu = {
                        'paiva': current_date,
                        'aika': aika,
                        'koti': koti,
                        'vieras': vieras,
                    }
                    print(f"Lisätty ottelu: {ottelu}")
                    ottelut.append(ottelu)
                else:
                    print(f"Ei kelvollinen joukkue: {koti} vs {vieras}")
    
    return ottelut

# Apufunktio ajan formaatin tarkistamiseen
def is_time_format(s):
    return re.match(r'\d{1,2}:\d{2}', s) is not None

# Apufunktio joukkueen validoinnille
def is_valid_team(team_name):
    for team in teams:
        if team in team_name:
            return True
    return False

# Parannettu funktio, joka parsii joukkueiden tilastot
def parse_yleiso_data(data):
    teams_data = {}
    current_team = None
    kotipelit_mode = False
    vieraspelit_mode = False
    
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        
        # Etsi joukkueen nimeä
        if line.startswith('### '):
            found_team = False
            team_name = line.replace('### ', '').strip()
            # Normalisoi joukkueen nimi
            for team in teams:
                if team in team_name:
                    current_team = team
                    teams_data[current_team] = {}
                    print(f"Löytyi joukkue: {current_team}")
                    found_team = True
                    break
            if not found_team:
                current_team = None
            kotipelit_mode = False
            vieraspelit_mode = False
        
        # Tunnista osiota
        elif current_team and line.startswith('#### Kotipelit'):
            kotipelit_mode = True
            vieraspelit_mode = False
            print(f"Kotipelit-osio: {current_team}")
        
        elif current_team and line.startswith('#### Vieraspelit'):
            kotipelit_mode = False
            vieraspelit_mode = True
            print(f"Vieraspelit-osio: {current_team}")
        
        # Kerää tilastoja
        elif current_team and line.startswith('- '):
            if kotipelit_mode:
                if "Tehdyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['koti_maaleja'] = value
                    print(f"{current_team} koti_maaleja: {value}")
                    
                elif "Päästetyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['koti_paastetty'] = value
                    
                elif "Otteluita:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['koti_ottelut'] = value
                    
                elif "Yli 2.5 maalia:" in line:
                    match = re.search(r'Yli 2.5 maalia:\s*(\d+)\s*\(([^)]+)\)', line)
                    if match:
                        value = f"{match.group(1)} ({match.group(2)})"
                        teams_data[current_team]['koti_yli_2_5'] = value
                        print(f"{current_team} koti_yli_2_5: {value}")
                    
            elif vieraspelit_mode:
                if "Tehdyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['vieras_maaleja'] = value
                    print(f"{current_team} vieras_maaleja: {value}")
                    
                elif "Päästetyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['vieras_paastetty'] = value
                
                elif "Otteluita:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['vieras_ottelut'] = value
                    
                elif "Yli 2.5 maalia:" in line:
                    match = re.search(r'Yli 2.5 maalia:\s*(\d+)\s*\(([^)]+)\)', line)
                    if match:
                        value = f"{match.group(1)} ({match.group(2)})"
                        teams_data[current_team]['vieras_yli_2_5'] = value
                        print(f"{current_team} vieras_yli_2_5: {value}")
    
    # Lisää joukkueen "muoto" ja suhteellinen sijoitus
    generate_team_form_and_positions(teams_data)
    
    return teams_data

# UUSI: Lisää joukkueille simuloitu muoto ja sarjataulukon sijoitus
def generate_team_form_and_positions(teams_data):
    """Generoi joukkueille simuloitua muototietoa ja sarjataulukon sijoituksia"""
    
    # Laske kokonaispisteet oikeiden maalitietojen perusteella
    points = {}
    for team, data in teams_data.items():
        koti_maalit = data.get('koti_maaleja', 0) * data.get('koti_ottelut', 1)
        vieras_maalit = data.get('vieras_maaleja', 0) * data.get('vieras_ottelut', 1)
        koti_paastetyt = data.get('koti_paastetty', 0) * data.get('koti_ottelut', 1)
        vieras_paastetyt = data.get('vieras_paastetty', 0) * data.get('vieras_ottelut', 1)
        
        # Yksinkertainen pisteiden simulointi maalieron perusteella
        maalisuhde = (koti_maalit + vieras_maalit) / max(1, koti_paastetyt + vieras_paastetyt)
        points[team] = max(0, maalisuhde * 10)  # Skaalataan järkeviksi pisteiksi
    
    # Aseta joukkueiden sarjataulukon sijoitukset
    positions = {team: i+1 for i, (team, _) in enumerate(sorted(points.items(), key=lambda x: x[1], reverse=True))}
    
    # Lisää simuloitu "muoto" (WDLWW jne.) ja sijoitus joukkueille
    for team in teams_data:
        # Sijoitus
        teams_data[team]['position'] = positions.get(team, len(teams_data))
        
        # Simuloi muoto pisteiden pohjalta (parempi joukkue = parempi muoto)
        position = positions.get(team, 10)
        win_prob = max(0.2, 1.0 - (position / 15.0))
        
        form_results = []
        for _ in range(5):
            rand = random.random()
            if rand < win_prob:
                form_results.append('W')
            elif rand < win_prob + 0.3:
                form_results.append('D')
            else:
                form_results.append('L')
                
        teams_data[team]['form'] = ''.join(form_results)
        teams_data[team]['form_factor'] = calculate_form_factor(form_results)

# UUSI: Laske muotokerroin
def calculate_form_factor(form_results):
    """Laskee joukkueen muotokertoimen viimeisten tulosten perusteella"""
    weights = [1.0, 0.8, 0.6, 0.4, 0.2]  # Uudemmat ottelut painotetumpia
    
    weighted_sum = 0
    for i, result in enumerate(form_results[:5]):  # Käytä enintään 5 viimeisintä ottelua
        if result == 'W':
            weighted_sum += 3 * weights[i]
        elif result == 'D':
            weighted_sum += 1 * weights[i]
    
    max_points = sum(3 * w for w in weights[:len(form_results)])
    return weighted_sum / max_points if max_points > 0 else 0.5

# UUSI: Simuloi joukkueiden keskinäisten otteluiden historia
def simulate_head_to_head(home_team, away_team):
    """Simuloi joukkueiden keskinäiset kohtaamiset historiatietojen puuttuessa"""
    # Tässä käytettäisiin todellista historiadataa jos saatavilla
    matches = []
    
    # Simuloi 3-5 keskinäistä ottelua
    for _ in range(random.randint(3, 5)):
        home_score = max(0, round(random.gauss(1.5, 1.0)))
        away_score = max(0, round(random.gauss(1.2, 0.8)))
        
        if home_score > away_score:
            winner = home_team
        elif away_score > home_score:
            winner = away_team
        else:
            winner = None
            
        matches.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_goals': home_score,
            'away_goals': away_score,
            'winner': winner
        })
    
    return matches

# UUSI: Analysoi joukkueiden keskinäiset kohtaamiset
def analyze_head_to_head(home_team, away_team):
    """Analysoi joukkueiden keskinäiset kohtaamiset"""
    # Todellisessa toteutuksessa haettaisiin oikeaa dataa
    h2h_matches = simulate_head_to_head(home_team, away_team)
    
    if not h2h_matches:
        return None
        
    home_wins = sum(1 for match in h2h_matches if match['winner'] == home_team)
    away_wins = sum(1 for match in h2h_matches if match['winner'] == away_team)
    draws = len(h2h_matches) - home_wins - away_wins
    
    avg_home_goals = sum(match['home_goals'] for match in h2h_matches) / len(h2h_matches)
    avg_away_goals = sum(match['away_goals'] for match in h2h_matches) / len(h2h_matches)
    
    return {
        'home_win_ratio': home_wins / len(h2h_matches),
        'draw_ratio': draws / len(h2h_matches), 
        'away_win_ratio': away_wins / len(h2h_matches),
        'avg_home_goals': avg_home_goals,
        'avg_away_goals': avg_away_goals,
        'matches_analyzed': len(h2h_matches),
        'matches': h2h_matches
    }

# UUSI: Monte Carlo -simulaatio
def monte_carlo_simulation(home_goals_exp, away_goals_exp, simulations=10000):
    """Suorittaa Monte Carlo -simulaation ottelutuloksille"""
    home_wins = 0
    away_wins = 0
    draws = 0
    over_2_5 = 0
    score_counts = {}
    
    for _ in range(simulations):
        # Generoi satunnainen tulos Poisson-jakaumasta
        home_score = np.random.poisson(home_goals_exp)
        away_score = np.random.poisson(away_goals_exp)
        
        # Laske tulokset
        if home_score > away_score:
            home_wins += 1
        elif away_score > home_score:
            away_wins += 1
        else:
            draws += 1
            
        # Yli 2.5 maalia
        if home_score + away_score > 2.5:
            over_2_5 += 1
            
        # Tuloksen esiintymiskerrat
        score_key = f"{home_score}-{away_score}"
        score_counts[score_key] = score_counts.get(score_key, 0) + 1
    
    # Järjestä yleisimmät tulokset
    most_common_scores = sorted(score_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'koti_voitto_tod': home_wins / simulations * 100,
        'tasapeli_tod': draws / simulations * 100,
        'vieras_voitto_tod': away_wins / simulations * 100,
        'yli_2_5_tod': over_2_5 / simulations * 100,
        'yleisimmat_tulokset': most_common_scores
    }

# UUSI: Simuloi expected goals arvot
def simulate_expected_goals(home_team, away_team, teams_data):
    """Simuloi expected goals arvot datan puuttuessa"""
    home_key = find_matching_team(home_team, teams_data)
    away_key = find_matching_team(away_team, teams_data)
    
    home_avg_goals = teams_data.get(home_key, {}).get('koti_maaleja', 1.0) if home_key else 1.0
    away_avg_goals = teams_data.get(away_key, {}).get('vieras_maaleja', 0.8) if away_key else 0.8
    
    # Lisätään satunnaisuutta xG-arvoihin
    home_xg = max(0.3, home_avg_goals * random.uniform(0.8, 1.2))
    away_xg = max(0.2, away_avg_goals * random.uniform(0.8, 1.2))
    
    return home_xg, away_xg

# Apufunktio numeroiden poimintaan
def extract_number(text):
    match = re.search(r':\s*(\d+)', text)
    if match:
        return float(match.group(1))
    return 0

# Laskee Poisson-todennäköisyyksiä
def poisson_probability(mean, k):
    try:
        return math.exp(-mean) * (mean ** k) / math.factorial(k)
    except:
        return 0

# Laskee voittotodennäköisyyden
def calculate_win_probability(team_a_goals, team_b_goals):
    prob = 0
    for i in range(0, 10):  # Iteroi todennäköisiä maalimääriä
        for j in range(0, i):  # Joukkue A voittaa kun sen maalit > B:n maalit
            prob += poisson_probability(team_a_goals, i) * poisson_probability(team_b_goals, j)
    return prob

# Laskee yli X maalia todennäköisyyden
def calculate_over_probability(team_a_goals, team_b_goals, limit):
    prob = 0
    for i in range(0, 15):
        for j in range(0, 15):
            if i + j > limit:
                prob += poisson_probability(team_a_goals, i) * poisson_probability(team_b_goals, j)
    return prob

# Laskee todennäköisimmän tuloksen
def calculate_most_likely_score(team_a_goals, team_b_goals):
    highest_prob = 0
    likely_score = (0, 0)
    
    for i in range(0, 6):
        for j in range(0, 6):
            prob = poisson_probability(team_a_goals, i) * poisson_probability(team_b_goals, j)
            if prob > highest_prob:
                highest_prob = prob
                likely_score = (i, j)
                
    return f"{likely_score[0]}-{likely_score[1]}"

# Apufunktio joukkueen nimen täsmäämiseen
def find_matching_team(team_name, teams_data):
    # Täsmällinen osuma
    if team_name in teams_data:
        return team_name
    
    # Osittainen osuma
    for team in teams_data.keys():
        if team in team_name or team_name in team:
            return team
    
    # Erikoistapaukset
    if "Gnistan" in team_name:
        if "IF Gnistan" in teams_data:
            return "IF Gnistan"
        elif "Gnistan" in teams_data:
            return "Gnistan"
    
    return None

# UUSI: Ennusta sarjan loppusijoitukset
def predict_final_standings(teams, remaining_matches, teams_data):
    """Ennustaa sarjan loppusijoitukset simuloimalla jäljellä olevat ottelut"""
    # Laske nykyiset pisteet (estimaatti joukkueiden tietojen perusteella)
    current_points = {}
    for team in teams:
        team_key = find_matching_team(team, teams_data)
        if team_key:
            position = teams_data[team_key].get('position', random.randint(1, len(teams)))
            # Estimoi pisteet sijoituksen perusteella
            current_points[team] = max(1, 40 - (position * 2.5))
        else:
            current_points[team] = random.randint(10, 30)
            
    simulations = 500
    final_points = {team: [current_points[team]] * simulations for team in teams}
    
    # Simuloi jäljellä olevat ottelut
    for sim in range(simulations):
        for match in remaining_matches:
            home_team = match['koti']
            away_team = match['vieras']
            
            home_key = find_matching_team(home_team, teams_data)
            away_key = find_matching_team(away_team, teams_data)
            
            home_strength = 1.0
            away_strength = 1.0
            
            if home_key and home_key in teams_data:
                home_strength = 1.5 - (teams_data[home_key].get('position', 6) / 12.0)
                
            if away_key and away_key in teams_data:
                away_strength = 1.5 - (teams_data[away_key].get('position', 6) / 12.0)
            
            # Arvo tulos vahvuuksien perusteella
            home_win_prob = 0.45 * home_strength / (home_strength + away_strength)
            away_win_prob = 0.35 * away_strength / (home_strength + away_strength)
            draw_prob = 1.0 - home_win_prob - away_win_prob
            
            rand = random.random()
            if rand < home_win_prob:
                final_points[home_team][sim] += 3
            elif rand < home_win_prob + draw_prob:
                final_points[home_team][sim] += 1
                final_points[away_team][sim] += 1
            else:
                final_points[away_team][sim] += 3
    
    # Laske lopputulokset
    avg_points = {team: sum(points)/simulations for team, points in final_points.items()}
    standings = sorted(avg_points.items(), key=lambda x: x[1], reverse=True)
    
    # Laske mestaruustodennäköisyydet
    championship_odds = {}
    top_4_odds = {}
    relegation_odds = {}
    
    for team in teams:
        wins = 0
        top_4 = 0
        relegation = 0
        
        for sim in range(simulations):
            sim_standings = {}
            for t in teams:
                sim_standings[t] = final_points[t][sim]
                
            sorted_teams = sorted(sim_standings.items(), key=lambda x: x[1], reverse=True)
            team_position = [t[0] for t in sorted_teams].index(team) + 1
            
            if team_position == 1:
                wins += 1
            if team_position <= 4:
                top_4 += 1
            if team_position > len(teams) - 2:  # 2 viimeistä putoaa
                relegation += 1
                
        championship_odds[team] = wins / simulations * 100
        top_4_odds[team] = top_4 / simulations * 100
        relegation_odds[team] = relegation / simulations * 100
    
    return {
        'standings': standings,
        'championship_odds': championship_odds,
        'top_4_odds': top_4_odds, 
        'relegation_odds': relegation_odds
    }

# Kehittynyt analysointifunktio
def advanced_analyze_matches(ottelut, teams_data):
    results = []
    
    # Analysoi jokainen ottelu
    for ottelu in ottelut:
        koti = ottelu['koti']
        vieras = ottelu['vieras']
        
        koti_key = find_matching_team(koti, teams_data)
        vieras_key = find_matching_team(vieras, teams_data)
        
        print(f"Ottelu: {koti} vs {vieras}")
        print(f"Löydetty joukkueet: {koti_key} ja {vieras_key}")
        
        koti_maaleja = teams_data.get(koti_key, {}).get('koti_maaleja', 0) if koti_key else 0
        vieras_maaleja = teams_data.get(vieras_key, {}).get('vieras_maaleja', 0) if vieras_key else 0
        koti_yli_2_5 = teams_data.get(koti_key, {}).get('koti_yli_2_5', 'Ei tietoa') if koti_key else 'Ei tietoa'
        vieras_yli_2_5 = teams_data.get(vieras_key, {}).get('vieras_yli_2_5', 'Ei tietoa') if vieras_key else 'Ei tietoa'
        
        # 1. Huomioi joukkueiden muoto ja trendi
        koti_form_factor = teams_data.get(koti_key, {}).get('form_factor', 0.5) if koti_key else 0.5
        vieras_form_factor = teams_data.get(vieras_key, {}).get('form_factor', 0.5) if vieras_key else 0.5
        
        koti_form = teams_data.get(koti_key, {}).get('form', 'DDDDD') if koti_key else 'DDDDD'
        vieras_form = teams_data.get(vieras_key, {}).get('form', 'DDDDD') if vieras_key else 'DDDDD'
        
        # 2. Käsittele keskinäisiä otteluita
        h2h_stats = analyze_head_to_head(koti, vieras)
        
        # 3. Huomioi kotietukerroin ja sarjataulukon ero
        home_boost = 1.3  # Kotijoukkue tekee keskimäärin 30% enemmän maaleja
        away_penalty = 0.9  # Vierasjoukkue tekee keskimäärin 10% vähemmän
        
        # Sarjataulukon vaikutus
        pos_diff_factor = 1.0
        if koti_key and vieras_key and 'position' in teams_data.get(koti_key, {}) and 'position' in teams_data.get(vieras_key, {}):
            home_pos = teams_data[koti_key]['position']
            away_pos = teams_data[vieras_key]['position']
            pos_diff = home_pos - away_pos
            
            # Parempi joukkue sarjataulukossa saa etua
            if pos_diff < 0:  # Kotijoukkue korkeammalla
                pos_diff_factor = 1.0 + min(0.3, abs(pos_diff) * 0.03)
            elif pos_diff > 0:  # Vierasjoukkue korkeammalla
                pos_diff_factor = 1.0 - min(0.2, pos_diff * 0.02)
        
        # 4. Simuloi expected goals arvot
        home_xg, away_xg = simulate_expected_goals(koti, vieras, teams_data)
        
        # 5. Painota ennusteita huomioiden kaikki tekijät
        adjusted_home_goals = koti_maaleja * home_boost * pos_diff_factor * (0.7 + 0.3 * koti_form_factor)
        adjusted_away_goals = vieras_maaleja * away_penalty * (1/pos_diff_factor) * (0.7 + 0.3 * vieras_form_factor)
        
        # Keskinäiset kohtaamiset (jos niitä on)
        if h2h_stats:
            adjusted_home_goals = adjusted_home_goals * 0.8 + h2h_stats['avg_home_goals'] * 0.2
            adjusted_away_goals = adjusted_away_goals * 0.8 + h2h_stats['avg_away_goals'] * 0.2
            
        # 6. Monte Carlo -simulaatio
        monte_carlo_results = monte_carlo_simulation(adjusted_home_goals, adjusted_away_goals)
        
        # Nolladivisioiden välttäminen
        if adjusted_home_goals == 0:
            adjusted_home_goals = 0.5
        if adjusted_away_goals == 0:
            adjusted_away_goals = 0.3
            
        # Lopulliset analyysitulokset
        result = {
            'ottelu': f"{koti} vs {vieras}",
            'paiva': ottelu['paiva'],
            'aika': ottelu['aika'],
            'koti_maaleja': koti_maaleja,
            'vieras_maaleja': vieras_maaleja,
            'koti_yli_2_5': koti_yli_2_5,
            'vieras_yli_2_5': vieras_yli_2_5,
            'koti_form': koti_form,
            'vieras_form': vieras_form,
            'koti_voitto_tod': round(monte_carlo_results['koti_voitto_tod'], 1),
            'vieras_voitto_tod': round(monte_carlo_results['vieras_voitto_tod'], 1),
            'tasapeli_tod': round(monte_carlo_results['tasapeli_tod'], 1),
            'yli_2_5_tod': round(monte_carlo_results['yli_2_5_tod'], 1),
            'todennakoisin_tulos': calculate_most_likely_score(adjusted_home_goals, adjusted_away_goals),
            'yleisimmat_tulokset': monte_carlo_results['yleisimmat_tulokset'],
            'xg_koti': round(home_xg, 2),
            'xg_vieras': round(away_xg, 2),
        }
        
        # Lisää head-to-head tiedot jos niitä on
        if h2h_stats:
            result['h2h'] = h2h_stats
            
        results.append(result)
    
    return results

# Funktio, joka generoi Markdown-kuvaajan
def generate_bar_chart(label, value, max_value=25, bar_char='█'):
    bar_length = int((value / max_value) * 25)
    return f"{label} {bar_char * bar_length} {value}%"

# Päivitetty tulostus markdown-tiedostoon visualisointeineen
def save_advanced_results_to_markdown(ottelut, results, teams_data, filename):
    filepath = os.path.join(os.getcwd(), filename)
    print(f"Tallentaa tulokset tiedostoon: {filepath}")
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("# Analysoidut Ottelut\n\n")
        file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Tulostetaan ottelut
        file.write("## Tulevat Ottelut\n")
        if not ottelut:
            file.write("Ei tulevia otteluita.\n\n")
        else:
            for ottelu in ottelut:
                paiva_info = f"{ottelu['paiva']}" if ottelu['paiva'] else ""
                aika_info = f"{ottelu['aika']}" if ottelu['aika'] else ""
                file.write(f"- {ottelu['koti']} vs {ottelu['vieras']} ({paiva_info} klo {aika_info})\n")
        
        file.write("\n## Otteluiden Ennusteet\n")
        if not results:
            file.write("Ei analysoitavia otteluita.\n")
        else:
            # Yhteenveto kaikista otteluista taulukossa
            file.write("### Yhteenveto Ennusteista\n")
            file.write("| Ottelu | Päivämäärä | Aika | 1 | X | 2 | Todennäköisin tulos | Yli 2.5 maalia | xG (Koti-Vieras) |\n")
            file.write("|--------|-----------|------|---|---|---|-------------------|---------------|----------------|\n")
            
            for tulos in results:
                koti_team = tulos['ottelu'].split(" vs ")[0]
                vieras_team = tulos['ottelu'].split(" vs ")[1]
                file.write(f"| {koti_team} v {vieras_team} | {tulos['paiva']} | {tulos['aika']} | ")
                file.write(f"{tulos['koti_voitto_tod']}% | {tulos['tasapeli_tod']}% | {tulos['vieras_voitto_tod']}% | ")
                file.write(f"{tulos['todennakoisin_tulos']} | {tulos['yli_2_5_tod']}% | {tulos['xg_koti']}-{tulos['xg_vieras']} |\n")
            
            file.write("\n")
            
            # Ennusta sarjataulukko
            if len(teams_data) > 8:  # Jos on tarpeeksi joukkueita
                file.write("## Kauden 2025 Sarjataulukkoennuste\n\n")
                
                # Ennusta lopputaulukko
                standings_prediction = predict_final_standings(teams, ottelut, teams_data)
                
                file.write("### Ennustetut loppusijoitukset\n")
                file.write("| Sija | Joukkue | Ennustetut pisteet | Mestaruus% | Top 4% | Putoamisvaara% |\n")
                file.write("|------|---------|-------------------|-----------|--------|---------------|\n")
                
                for i, (team, points) in enumerate(standings_prediction['standings']):
                    mestaruus = round(standings_prediction['championship_odds'].get(team, 0), 1)
                    top4 = round(standings_prediction['top_4_odds'].get(team, 0), 1)
                    putoaminen = round(standings_prediction['relegation_odds'].get(team, 0), 1)
                    
                    file.write(f"| {i+1} | {team} | {round(points, 1)} | {mestaruus}% | {top4}% | {putoaminen}% |\n")
                
                file.write("\n")
                
                # Mestaruuskuvaaja
                file.write("#### Mestaruustodennäköisyydet\n```\n")
                for team, odds in sorted(standings_prediction['championship_odds'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    if odds > 0.5:
                        file.write(generate_bar_chart(f"{team:12}", round(odds, 1)) + "\n")
                file.write("```\n\n")
            
            # Yksityiskohtaiset analyysit otteluista
            file.write("## Yksityiskohtaiset Otteluanalyysit\n\n")
            
            for tulos in results:
                koti_team = tulos['ottelu'].split(" vs ")[0]
                vieras_team = tulos['ottelu'].split(" vs ")[1]
                
                file.write(f"### {koti_team} vs {vieras_team} - {tulos['paiva']} klo {tulos['aika']}\n\n")
                
                # Perustilastot
                file.write("#### Perustilastot\n")
                file.write(f"- **Koti:** {koti_team} - Viimeisimmät ottelut: {tulos['koti_form']}\n")
                file.write(f"- **Vieras:** {vieras_team} - Viimeisimmät ottelut: {tulos['vieras_form']}\n")
                file.write(f"- Kotijoukkueen keskimääräiset maalit kotona: **{tulos['koti_maaleja']}**\n")
                file.write(f"- Vierasjoukkueen keskimääräiset maalit vieraissa: **{tulos['vieras_maaleja']}**\n")
                
                # Expected Goals -tilastot
                file.write("\n#### Expected Goals (xG) -ennuste\n")
                file.write(f"- {koti_team}: **{tulos['xg_koti']}**\n")
                file.write(f"- {vieras_team}: **{tulos['xg_vieras']}**\n")
                
                # Keskinäiset kohtaamiset
                if 'h2h' in tulos:
                    h2h = tulos['h2h']
                    file.write("\n#### Keskinäiset kohtaamiset\n")
                    file.write(f"- Keskinäisiä otteluita analysoitu: {h2h['matches_analyzed']}\n")
                    file.write(f"- {koti_team} voittanut: {round(h2h['home_win_ratio']*100, 1)}%\n")
                    file.write(f"- Tasapelit: {round(h2h['draw_ratio']*100, 1)}%\n")
                    file.write(f"- {vieras_team} voittanut: {round(h2h['away_win_ratio']*100, 1)}%\n")
                    file.write(f"- Keskimääräiset maalit {koti_team}: {round(h2h['avg_home_goals'], 1)}\n")
                    file.write(f"- Keskimääräiset maalit {vieras_team}: {round(h2h['avg_away_goals'], 1)}\n\n")
                    
                    # Näytä keskinäiset ottelut
                    file.write("**Edelliset kohtaamiset:**\n")
                    for match in h2h['matches'][:3]:  # Näytä viimeisimmät 3
                        result = f"{match['home_goals']}-{match['away_goals']}"
                        winner = f" ({match['winner']} voitti)" if match['winner'] else " (Tasapeli)"
                        file.write(f"- {match['home_team']} vs {match['away_team']}: **{result}**{winner}\n")
                    
                # Todennäköisyydet
                file.write("\n#### Todennäköisyydet\n")
                
                # ASCII-kuvaaja
                file.write("```\n")
                file.write(generate_bar_chart(f"{koti_team} voittaa:", round(tulos['koti_voitto_tod'], 1)) + "\n")
                file.write(generate_bar_chart("Tasapeli:", round(tulos['tasapeli_tod'], 1)) + "\n")
                file.write(generate_bar_chart(f"{vieras_team} voittaa:", round(tulos['vieras_voitto_tod'], 1)) + "\n")
                file.write(generate_bar_chart("Yli 2.5 maalia:", round(tulos['yli_2_5_tod'], 1)) + "\n")
                file.write("```\n\n")
                
                # Todennäköisimmät tulokset
                file.write("#### Todennäköisimmät lopputulokset\n")
                file.write("```\n")
                for score_str, count in tulos['yleisimmat_tulokset'][:3]:
                    prob = count / 10000 * 100
                    file.write(f"{score_str}: {round(prob, 1)}%\n")
                file.write("```\n\n")
                
                # Älykkäät kommentit
                file.write("#### Analyysikeskuspuhe\n")
                if tulos['koti_voitto_tod'] > 60:
                    file.write(f"**Selkeä kotietu**: {koti_team} on vahva suosikki tässä ottelussa. Kotijoukkue on tehnyt keskimäärin {tulos['koti_maaleja']} maalia kotiotteluissaan ja on ennusteen mukaan todennäköinen voittaja.\n\n")
                elif tulos['vieras_voitto_tod'] > 60:
                    file.write(f"**Vierasjoukkue suosikki**: Yllättävä tilanne, sillä {vieras_team} on selkeä suosikki vieraskentällä. Vierasjoukkue on onnistunut tekemään keskimäärin {tulos['vieras_maaleja']} maalia vieraskentällä, mikä viittaa vahvaan hyökkäyskykyyn.\n\n")
                elif tulos['tasapeli_tod'] > 30:
                    file.write(f"**Tasaväkinen kohtaaminen**: Ottelu {koti_team} ja {vieras_team} välillä vaikuttaa erittäin tasaiselta. Kumpi tahansa joukkue voi viedä voiton, mutta tasapelin todennäköisyys on huomattavan korkea.\n\n")
                
                if tulos['yli_2_5_tod'] > 70:
                    file.write(f"**Odotettavissa runsasmaalinen ottelu**: Tilastojen valossa on todennäköistä, että ottelussa nähdään vähintään kolme maalia. Yli 2.5 maalin todennäköisyys on peräti {round(tulos['yli_2_5_tod'], 1)}%.\n\n")
                elif tulos['yli_2_5_tod'] < 40:
                    file.write(f"**Vähämaalinen ottelu**: Tämä ottelu saattaa päättyä melko vähämaalisena. Yli 2.5 maalin todennäköisyys on vain {round(tulos['yli_2_5_tod'], 1)}%.\n\n")
                
                file.write("---\n\n")

# Suoritetaan koko prosessi
print("Parsing upcoming matches...")
ottelut = parse_tulevat_ottelut(tulevat_ottelut_data)
print("Parsing team statistics...")
teams_data = parse_yleiso_data(yleiso_data)

# Debug output
print("\n\nOTTELUT LÖYDETTY:")
for ottelu in ottelut:
    print(f"{ottelu['koti']} vs {ottelu['vieras']} ({ottelu['paiva']} {ottelu['aika']})")
print("\n\nJOUKKUETIEDOT:")
for team, data in teams_data.items():
    print(f"{team}: {data}")

# Käytetään kehittyneempää analyysia
print("Analyzing matches...")
analysoidut_tulokset = advanced_analyze_matches(ottelut, teams_data)
print("Saving results...")
save_advanced_results_to_markdown(ottelut, analysoidut_tulokset, teams_data, 'AnalysoidutOttelut.md')

print("Analyysi valmis ja tulokset tallennettu tiedostoon 'AnalysoidutOttelut.md'.")
