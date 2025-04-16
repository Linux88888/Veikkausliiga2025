import requests
import re
import os
import datetime
import random
import math

# Aiemmat funktiot pysyvät samoina...

# Lisätään kehittyneempi analysointifunktio
def advanced_analyze_matches(ottelut, teams_data):
    results = []
    for ottelu in ottelut:
        koti = ottelu['koti']
        vieras = ottelu['vieras']
        
        koti_key = find_matching_team(koti, teams_data)
        vieras_key = find_matching_team(vieras, teams_data)
        
        koti_maaleja = teams_data.get(koti_key, {}).get('koti_maaleja', 0) if koti_key else 0
        vieras_maaleja = teams_data.get(vieras_key, {}).get('vieras_maaleja', 0) if vieras_key else 0
        koti_yli_2_5 = teams_data.get(koti_key, {}).get('koti_yli_2_5', 'Ei tietoa') if koti_key else 'Ei tietoa'
        vieras_yli_2_5 = teams_data.get(vieras_key, {}).get('vieras_yli_2_5', 'Ei tietoa') if vieras_key else 'Ei tietoa'
        
        # Lasketaan Poisson-jakaumaan perustuvat todennäköisyydet
        home_goals_exp = float(koti_maaleja) if isinstance(koti_maaleja, (int, float)) else 0
        away_goals_exp = float(vieras_maaleja) if isinstance(vieras_maaleja, (int, float)) else 0
        
        # Painotetaan kotiedulla/vierasedulla (30% vaikutus)
        home_boost = 1.3
        away_penalty = 0.9
        
        adjusted_home_goals = home_goals_exp * home_boost
        adjusted_away_goals = away_goals_exp * away_penalty
        
        # Lasketaan todennäköisyydet eri lopputuloksille
        home_win_prob = calculate_win_probability(adjusted_home_goals, adjusted_away_goals)
        away_win_prob = calculate_win_probability(adjusted_away_goals, adjusted_home_goals)
        draw_prob = max(0, 1 - home_win_prob - away_win_prob)
        
        # Yli 2.5 maalia todennäköisyys
        over_2_5_prob = calculate_over_probability(adjusted_home_goals, adjusted_away_goals, 2.5)
        
        # Lasketaan todennäköisin lopputulos
        most_likely_score = calculate_most_likely_score(adjusted_home_goals, adjusted_away_goals)
        
        result = {
            'ottelu': f"{koti} vs {vieras}",
            'paiva': ottelu['paiva'],
            'aika': ottelu['aika'],
            'koti_maaleja': koti_maaleja,
            'vieras_maaleja': vieras_maaleja,
            'koti_yli_2_5': koti_yli_2_5,
            'vieras_yli_2_5': vieras_yli_2_5,
            'koti_voitto_tod': round(home_win_prob * 100, 1),
            'vieras_voitto_tod': round(away_win_prob * 100, 1),
            'tasapeli_tod': round(draw_prob * 100, 1),
            'yli_2_5_tod': round(over_2_5_prob * 100, 1),
            'todennakoisin_tulos': most_likely_score
        }
        results.append(result)
    
    return results

# Laskee Poisson-todennäköisyyksiä
def poisson_probability(mean, k):
    return math.exp(-mean) * (mean ** k) / math.factorial(k)

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

# Päivitetty tulostus markdown-tiedostoon
def save_advanced_results_to_markdown(ottelut, results, filename):
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
            # Yhteenveto kaikista otteluista
            file.write("### Yhteenveto Ennusteista\n")
            file.write("| Ottelu | Päivämäärä | Aika | Kotivoitto | Tasapeli | Vierasvoitto | Todennäköisin tulos | Yli 2.5 maalia |\n")
            file.write("|--------|-----------|------|-----------|---------|-------------|-------------------|---------------|\n")
            
            for tulos in results:
                file.write(f"| {tulos['ottelu']} | {tulos['paiva']} | {tulos['aika']} | {tulos['koti_voitto_tod']}% | {tulos['tasapeli_tod']}% | {tulos['vieras_voitto_tod']}% | {tulos['todennakoisin_tulos']} | {tulos['yli_2_5_tod']}% |\n")
            
            file.write("\n")
            
            # Yksityiskohtaiset analyysit
            file.write("### Yksityiskohtaiset Analyysit\n\n")
            
            for tulos in results:
                file.write(f"#### {tulos['ottelu']} - {tulos['paiva']} klo {tulos['aika']}\n\n")
                
                # Perustilastot
                file.write("**Perustilastot:**\n")
                file.write(f"- Koti joukkueen keskiarvo maalit: {tulos['koti_maaleja']}\n")
                file.write(f"- Vieras joukkueen keskiarvo maalit: {tulos['vieras_maaleja']}\n")
                file.write(f"- Kotiotteluiden yli 2.5 maalia pelissä: {tulos['koti_yli_2_5']}\n")
                file.write(f"- Vierasotteluiden yli 2.5 maalia pelissä: {tulos['vieras_yli_2_5']}\n\n")
                
                # Todennäköisyydet
                file.write("**Lopputuloksen todennäköisyydet:**\n")
                file.write(f"- Kotivoitto: {tulos['koti_voitto_tod']}%\n")
                file.write(f"- Tasapeli: {tulos['tasapeli_tod']}%\n")
                file.write(f"- Vierasvoitto: {tulos['vieras_voitto_tod']}%\n\n")
                
                # Ennusteet
                file.write("**Maaliennusteet:**\n")
                file.write(f"- Todennäköisin lopputulos: {tulos['todennakoisin_tulos']}\n")
                file.write(f"- Yli 2.5 maalia: {tulos['yli_2_5_tod']}% todennäköisyys\n")
                
                # ASCII-grafiikka visualisoimaan tulosta
                file.write("\n**Voittotodennäköisyys:**\n```\n")
                koti_chars = int(tulos['koti_voitto_tod'] / 5)
                tasa_chars = int(tulos['tasapeli_tod'] / 5)
                vieras_chars = int(tulos['vieras_voitto_tod'] / 5)
                
                file.write(f"Kotivoitto  {'█' * koti_chars} {tulos['koti_voitto_tod']}%\n")
                file.write(f"Tasapeli   {'█' * tasa_chars} {tulos['tasapeli_tod']}%\n")
                file.write(f"Vierasvoitto {'█' * vieras_chars} {tulos['vieras_voitto_tod']}%\n")
                file.write("```\n\n")
                
                # Ylimääräinen kommentti
                koti_team = tulos['ottelu'].split(" vs ")[0]
                vieras_team = tulos['ottelu'].split(" vs ")[1]
                
                if tulos['koti_voitto_tod'] > 60:
                    file.write(f"**Huomio:** {koti_team} on selkeä suosikki tässä ottelussa.\n\n")
                elif tulos['vieras_voitto_tod'] > 60:
                    file.write(f"**Huomio:** {vieras_team} on selkeä suosikki tässä ottelussa.\n\n")
                elif tulos['tasapeli_tod'] > 30:
                    file.write("**Huomio:** Tasapeliä voidaan pitää todennäköisenä tässä tasaväkisessä ottelussa.\n\n")
                
                file.write("---\n\n")

# Käytetään kehittyneempää analyysia
analysoidut_tulokset = advanced_analyze_matches(ottelut, teams_data)
save_advanced_results_to_markdown(ottelut, analysoidut_tulokset, 'AnalysoidutOttelut.md')
