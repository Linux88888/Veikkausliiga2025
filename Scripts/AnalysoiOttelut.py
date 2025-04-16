import requests
import re
import os
import datetime
import math
import numpy as np
from collections import defaultdict

# Nykyinen päivämäärä ja aika
CURRENT_DATE = "2025-04-16 19:38:56"
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

# Joukkuenimen normalisointifunktio
def normalize_team_name(team_name):
    """Normalisoi joukkueen nimen viralliseen muotoon"""
    # Tarkista suoraan aliakset
    if team_name in team_aliases:
        return team_aliases[team_name]
    
    # Tarkista täsmällinen osuma
    for team in teams:
        if team.lower() == team_name.lower():
            return team
    
    # Tarkista osittaiset osumat
    for team in teams:
        if team.lower() in team_name.lower() or team_name.lower() in team.lower():
            return team
            
    # Erikoistapaukset ja aliakset
    if "gnistan" in team_name.lower():
        return "IF Gnistan"
        
    return team_name  # Jos ei löydy vastaavuutta

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
                    koti = normalize_team_name(parts[1].strip())
                    vieras = normalize_team_name(parts[2].strip())
                    
                # Formaatti 2: "14 - - 17:00 - 17:00 - FC Haka - AC Oulu - Seuranta"
                elif len(parts) >= 6 and is_time_format(parts[3]):
                    aika = parts[3].strip()
                    koti = normalize_team_name(parts[4].strip())
                    vieras = normalize_team_name(parts[5].strip())
                else:
                    continue
                
                # Tarkista, että löydetyt joukkueet ovat valideja
                if koti in teams and vieras in teams:
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

# Parannettu funktio, joka parsii joukkueiden tilastot
def parse_yleiso_data(data):
    teams_data = {}
    current_team = None
    kotipelit_mode = False
    vieraspelit_mode = False
    
    # Alusta kaikki joukkueet tyhjillä tiedoilla
    for team in teams:
        teams_data[team] = {}
        # Aseta oletusasema
        teams_data[team]['position'] = team_default_values.get(team, {}).get('expected_position', 6)
    
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        
        # Etsi joukkueen nimeä
        if line.startswith('### '):
            found_team = False
            team_name_raw = line.replace('### ', '').strip()
            team_name = normalize_team_name(team_name_raw)
            
            if team_name in teams:
                current_team = team_name
                print(f"Löytyi joukkue: {current_team}")
                found_team = True
            
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
    
    # Aseta joukkueiden viimeisimmät muodot vain tiedoksi (ei muuta analytiikkaa)
    for team in teams_data:
        # Käytä "NAAAA" (Not Available) osoittamaan, että todellisia viimeisiä pelejä ei ole tiedossa
        teams_data[team]['form'] = "NAAAA"  # Not Available
    
    return teams_data

# Apufunktio numeroiden poimintaan
def extract_number(text):
    match = re.search(r':\s*(\d+)', text)
    if match:
        return float(match.group(1))
    return 0

# Monte Carlo -simulaatio
def monte_carlo_simulation(home_goals_exp, away_goals_exp, simulations=10000):
    """Suorittaa Monte Carlo -simulaation ottelutuloksille realistisella jakaumalla"""
    home_wins = 0
    away_wins = 0
    draws = 0
    over_2_5 = 0
    score_counts = {}
    
    # Korjaa ääritapaukset realistisemmiksi
    if home_goals_exp > 3.0: home_goals_exp = 3.0
    if away_goals_exp > 2.5: away_goals_exp = 2.5
    if home_goals_exp < 0.5: home_goals_exp = 0.5
    if away_goals_exp < 0.3: away_goals_exp = 0.3
    
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

# Realistiset Expected Goals (xG) arvot
def calculate_realistic_xg(home_team, away_team, teams_data):
    """Laskee expected goals arvot joukkueille olemassa olevasta datasta"""
    
    # Käytä olemassa olevaa dataa
    home_team_data = teams_data.get(home_team, {})
    away_team_data = teams_data.get(away_team, {})
    
    # Käytä vain olemassa olevaa maalidataa
    home_xg = home_team_data.get('koti_maaleja', 1.0)
    away_xg = away_team_data.get('vieras_maaleja', 0.8)
    
    # Jos ei ole dataa, käytä maltillista oletusarvoa
    if 'koti_maaleja' not in home_team_data:
        home_xg = 1.0
        
    if 'vieras_maaleja' not in away_team_data:
        away_xg = 0.8
    
    return home_xg, away_xg

# Maltillinen kotietu
def calculate_home_advantage():
    """Laskee maltillisen kotiedun"""
    home_boost = 1.15  # 15% etu kotijoukkueelle
    away_penalty = 0.95  # 5% haitta vierasjoukkueelle
    
    return home_boost, away_penalty

# KORJATTU: Sarjataulukon ennustaminen
def predict_final_standings(teams, remaining_matches, teams_data):
    """Ennustaa sarjan loppusijoitukset olemassa olevan datan perusteella"""
    # Veikkausliiga: 12 joukkuetta, jokainen pelaa 22 ottelua kaudessa
    total_matches = 22
    
    # Arvioi paljonko otteluita on pelattu (tässä tapauksessa noin 2 kierrosta)
    played_round_estimate = 2
    
    # Arvioi nykyiset pisteet joukkueittain
    current_points = {}
    
    for team in teams:
        # Käytetään joukkueen oletettua vahvuutta pisteiden arviointiin
        position = teams_data.get(team, {}).get('position', 6)
        expected_points_per_match = max(0.8, min(2.0, 2.2 - position * 0.1))
        
        # Arvioidut pisteet tältä ja aiemmilta kierroksilta
        current_points[team] = round(expected_points_per_match * played_round_estimate)
        
        # Korjaus: tarkista että pisteet ovat järkevän suuruiset
        if current_points[team] < 1:
            current_points[team] = 1
    
    # Simuloi kaikki jäljellä olevat kauden ottelut
    simulations = 500
    final_points = {team: [current_points[team]] * simulations for team in teams}
    
    # Simuloi tulevat ottelut (mukaan lukien repositoryssä luetteloidut)
    for sim in range(simulations):
        for match in remaining_matches:
            home_team = match['koti']
            away_team = match['vieras']
            
            # Käytä vahvuutta perustuen oletettuun sarjasijoitukseen
            home_pos = teams_data.get(home_team, {}).get('position', 6)
            away_pos = teams_data.get(away_team, {}).get('position', 6)
            
            home_strength = 10.0 - min(12, home_pos)
            away_strength = 10.0 - min(12, away_pos)
            
            # Kotiedun huomiointi
            home_strength *= 1.15
            
            # Arvo tulos
            total_strength = home_strength + away_strength
            home_win_prob = home_strength / total_strength * 0.85
            away_win_prob = away_strength / total_strength * 0.7
            draw_prob = 1.0 - home_win_prob - away_win_prob
            
            # Rajoita arvot realistisiksi
            if home_win_prob > 0.7: home_win_prob = 0.7
            if away_win_prob > 0.5: away_win_prob = 0.5
            if home_win_prob < 0.2: home_win_prob = 0.2
            if away_win_prob < 0.1: away_win_prob = 0.1
            draw_prob = 1.0 - home_win_prob - away_win_prob
            
            # Arvo tulos ja päivitä pisteet
            rand = np.random.random()
            if rand < home_win_prob:
                final_points[home_team][sim] += 3
            elif rand < home_win_prob + draw_prob:
                final_points[home_team][sim] += 1
                final_points[away_team][sim] += 1
            else:
                final_points[away_team][sim] += 3
        
        # KORJAUS: Simuloi myös ne jäljellä olevat ottelut, jotka eivät ole 
        # tiedossa tulevissa otteluissa
        matches_to_simulate = total_matches - played_round_estimate - len(remaining_matches)
        
        if matches_to_simulate > 0:
            for _ in range(matches_to_simulate):
                # Arvo satunnainen koti- ja vierasjoukkue
                all_teams = list(teams)
                np.random.shuffle(all_teams)
                home_team = all_teams[0]
                away_team = all_teams[1]
                
                # Käytä samaa logiikkaa kuin ylempänä
                home_pos = teams_data.get(home_team, {}).get('position', 6)
                away_pos = teams_data.get(away_team, {}).get('position', 6)
                
                home_strength = 10.0 - min(12, home_pos)
                away_strength = 10.0 - min(12, away_pos)
                home_strength *= 1.15
                
                total_strength = home_strength + away_strength
                home_win_prob = home_strength / total_strength * 0.85
                away_win_prob = away_strength / total_strength * 0.7
                draw_prob = 1.0 - home_win_prob - away_win_prob
                
                # Rajoita arvot
                if home_win_prob > 0.7: home_win_prob = 0.7
                if away_win_prob > 0.5: away_win_prob = 0.5
                if home_win_prob < 0.2: home_win_prob = 0.2
                if away_win_prob < 0.1: away_win_prob = 0.1
                draw_prob = 1.0 - home_win_prob - away_win_prob
                
                # Arvo tulos
                rand = np.random.random()
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

# Poisson-todennäköisyys
def poisson_probability(mean, k):
    try:
        return math.exp(-mean) * (mean ** k) / math.factorial(k)
    except:
        return 0

# Todennäköisin tulos
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

# Kehittynyt analysointifunktio
def advanced_analyze_matches(ottelut, teams_data):
    results = []
    
    # Analysoi jokainen ottelu
    for ottelu in ottelut:
        koti = ottelu['koti']
        vieras = ottelu['vieras']
        
        # Normalisoi joukkuenimet
        koti = normalize_team_name(koti)
        vieras = normalize_team_name(vieras)
        
        print(f"Ottelu: {koti} vs {vieras}")
        
        # Perustilastot
        koti_maaleja = teams_data.get(koti, {}).get('koti_maaleja', 1.0)
        vieras_maaleja = teams_data.get(vieras, {}).get('vieras_maaleja', 0.8)
        koti_yli_2_5 = teams_data.get(koti, {}).get('koti_yli_2_5', '0 (0.0%)')
        vieras_yli_2_5 = teams_data.get(vieras, {}).get('vieras_yli_2_5', '0 (0.0%)')
        
        # Kotietu (maltillinen)
        home_boost, away_penalty = calculate_home_advantage()
        
        # Expected goals
        home_xg, away_xg = calculate_realistic_xg(koti, vieras, teams_data)
        
        # Painotetut maaliennusteet
        adjusted_home_goals = koti_maaleja * home_boost
        adjusted_away_goals = vieras_maaleja * away_penalty
        
        # Monte Carlo -simulaatio
        monte_carlo_results = monte_carlo_simulation(adjusted_home_goals, adjusted_away_goals)
        
        # Varmista, että arvot eivät ole nollia
        if adjusted_home_goals < 0.3:
            adjusted_home_goals = 0.3
        if adjusted_away_goals < 0.2:
            adjusted_away_goals = 0.2
            
        # Analyysitulokset
        result = {
            'ottelu': f"{koti} vs {vieras}",
            'paiva': ottelu['paiva'],
            'aika': ottelu['aika'],
            'koti_maaleja': koti_maaleja,
            'vieras_maaleja': vieras_maaleja,
            'koti_yli_2_5': koti_yli_2_5,
            'vieras_yli_2_5': vieras_yli_2_5,
            'koti_form': teams_data.get(koti, {}).get('form', 'NAAAA'),
            'vieras_form': teams_data.get(vieras, {}).get('form', 'NAAAA'),
            'koti_voitto_tod': round(monte_carlo_results['koti_voitto_tod'], 1),
            'vieras_voitto_tod': round(monte_carlo_results['vieras_voitto_tod'], 1),
            'tasapeli_tod': round(monte_carlo_results['tasapeli_tod'], 1),
            'yli_2_5_tod': round(monte_carlo_results['yli_2_5_tod'], 1),
            'todennakoisin_tulos': calculate_most_likely_score(adjusted_home_goals, adjusted_away_goals),
            'yleisimmat_tulokset': monte_carlo_results['yleisimmat_tulokset'],
            'xg_koti': round(home_xg, 2),
            'xg_vieras': round(away_xg, 2),
        }
            
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
        file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Analysoitu: {CURRENT_USER} / {CURRENT_DATE}\n\n")
        file.write("**HUOMIO**: Analyysi perustuu vain kahden pelatun kierroksen dataan, joten tuloksia tulee tulkita varoen.\n\n")
        
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
            if len(teams) > 8:  # Jos on tarpeeksi joukkueita
                file.write("## Kauden 2025 Sarjataulukkoennuste\n\n")
                file.write("**HUOMIO**: Sarjataulukkoennuste huomioi joukkueiden oletetun vahvuuden.\n\n")
                
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
                if tulos['koti_form'] == "NAAAA":
                    file.write(f"- **Koti:** {koti_team} - Viimeisimmät ottelut: Ei tietoa\n")
                else:
                    file.write(f"- **Koti:** {koti_team} - Viimeisimmät ottelut: {tulos['koti_form']}\n")
                    
                if tulos['vieras_form'] == "NAAAA":
                    file.write(f"- **Vieras:** {vieras_team} - Viimeisimmät ottelut: Ei tietoa\n")
                else:
                    file.write(f"- **Vieras:** {vieras_team} - Viimeisimmät ottelut: {tulos['vieras_form']}\n")
                
                file.write(f"- Kotijoukkueen keskimääräiset maalit kotona: **{tulos['koti_maaleja']}**\n")
                file.write(f"- Vierasjoukkueen keskimääräiset maalit vieraissa: **{tulos['vieras_maaleja']}**\n")
                
                # Expected Goals -tilastot
                file.write("\n#### Expected Goals (xG) -ennuste\n")
                file.write(f"- {koti_team}: **{tulos['xg_koti']}**\n")
                file.write(f"- {vieras_team}: **{tulos['xg_vieras']}**\n")
                
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
                
                # Analyysikeskuspuhe
                file.write("#### Analyysikeskuspuhe\n")
                
                # Varoitushuomautus alkukaudesta
                file.write("**Huom! Analyysi perustuu vain kahden kierroksen tilastoihin, joten tuloksiin kannattaa suhtautua varauksella.**\n\n")
                
                if tulos['koti_voitto_tod'] > 60:
                    file.write(f"**Kotietu**: {koti_team} vaikuttaa vahvalta tässä ottelussa. Kotijoukkue on tehnyt keskimäärin {tulos['koti_maaleja']} maalia kotiotteluissaan.\n\n")
                elif tulos['vieras_voitto_tod'] > 55:
                    file.write(f"**Vierasjoukkue vahvoilla**: {vieras_team} näyttää tilastojen valossa vahvalta. Vierasjoukkue on tehnyt keskimäärin {tulos['vieras_maaleja']} maalia vieraskentällä.\n\n")
                elif tulos['tasapeli_tod'] > 30:
                    file.write(f"**Tasaväkinen kohtaaminen**: Ottelu {koti_team} ja {vieras_team} välillä vaikuttaa tasaiselta. Tasapelin todennäköisyys on melko korkea.\n\n")
                else:
                    file.write(f"**Tiukka ottelu**: {koti_team} ja {vieras_team} ovat melko tasaväkisiä joukkueita nykyisten tilastojen perusteella.\n\n")
                
                if tulos['yli_2_5_tod'] > 65:
                    file.write(f"**Maalirikasta peliä odotettavissa**: Tilastojen valossa on todennäköistä, että ottelussa nähdään vähintään kolme maalia. Yli 2.5 maalin todennäköisyys on {round(tulos['yli_2_5_tod'], 1)}%.\n\n")
                elif tulos['yli_2_5_tod'] < 40:
                    file.write(f"**Todennäköisesti vähämaalinen**: Yli 2.5 maalin todennäköisyys on vain {round(tulos['yli_2_5_tod'], 1)}%.\n\n")
                
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
