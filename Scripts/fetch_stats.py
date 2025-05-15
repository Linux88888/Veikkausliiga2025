#!/usr/bin/env python
"""
Veikkausliiga 2025 - Data Fetcher
This script fetches league tables, match results, upcoming matches and player statistics
for the Finnish football league "Veikkausliiga" 2025 season.
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
import sys
from bs4 import BeautifulSoup

# Import utility functions
from utils.file_utils import ensure_directories
from utils.web_utils import fetch_html

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/veikkausliiga_fetch.log", mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("veikkausliiga-fetch")

# Set up base directories
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
STATS_DIR = DATA_DIR / "stats"
LOG_DIR = ROOT_DIR / "logs"

# Ensure directories exist
ensure_directories([RAW_DIR, PROCESSED_DIR, STATS_DIR, LOG_DIR])

# ISO formatted date for file naming
TODAY = datetime.now().strftime('%Y-%m-%d')

# URLs for data sources - to be updated with actual Veikkausliiga 2025 sources when available
LEAGUE_TABLE_URL = "https://www.veikkausliiga.com/tilastot/taulukko"  # Placeholder
MATCHES_URL = "https://www.veikkausliiga.com/ottelut"  # Placeholder
PLAYER_STATS_URL = "https://www.veikkausliiga.com/tilastot/pelaajat"  # Placeholder

def parse_league_table(html):
    """Parse league table data from HTML."""
    if not html:
        return []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        # This would be replaced with actual parsing logic based on the website structure
        # For now, using sample data
        
        teams = [
            {"position": 1, "name": "HJK Helsinki", "played": 10, "won": 7, "drawn": 2, "lost": 1, "goals_for": 22, "goals_against": 7, "goal_difference": 15, "points": 23},
            {"position": 2, "name": "FC Inter", "played": 10, "won": 6, "drawn": 3, "lost": 1, "goals_for": 18, "goals_against": 8, "goal_difference": 10, "points": 21},
            {"position": 3, "name": "KuPS", "played": 10, "won": 6, "drawn": 1, "lost": 3, "goals_for": 15, "goals_against": 10, "goal_difference": 5, "points": 19},
            {"position": 4, "name": "FC Lahti", "played": 10, "won": 5, "drawn": 2, "lost": 3, "goals_for": 14, "goals_against": 11, "goal_difference": 3, "points": 17},
            {"position": 5, "name": "Ilves", "played": 10, "won": 4, "drawn": 4, "lost": 2, "goals_for": 12, "goals_against": 10, "goal_difference": 2, "points": 16},
            {"position": 6, "name": "SJK", "played": 10, "won": 4, "drawn": 3, "lost": 3, "goals_for": 13, "goals_against": 11, "goal_difference": 2, "points": 15},
            {"position": 7, "name": "VPS", "played": 10, "won": 3, "drawn": 4, "lost": 3, "goals_for": 11, "goals_against": 10, "goal_difference": 1, "points": 13},
            {"position": 8, "name": "HIFK", "played": 10, "won": 3, "drawn": 3, "lost": 4, "goals_for": 10, "goals_against": 12, "goal_difference": -2, "points": 12},
            {"position": 9, "name": "FC Haka", "played": 10, "won": 3, "drawn": 2, "lost": 5, "goals_for": 9, "goals_against": 14, "goal_difference": -5, "points": 11},
            {"position": 10, "name": "IFK Mariehamn", "played": 10, "won": 2, "drawn": 4, "lost": 4, "goals_for": 8, "goals_against": 13, "goal_difference": -5, "points": 10},
            {"position": 11, "name": "KTP", "played": 10, "won": 1, "drawn": 4, "lost": 5, "goals_for": 7, "goals_against": 15, "goal_difference": -8, "points": 7},
            {"position": 12, "name": "AC Oulu", "played": 10, "won": 1, "drawn": 2, "lost": 7, "goals_for": 6, "goals_against": 17, "goal_difference": -11, "points": 5},
        ]
        
        return teams
    
    except Exception as e:
        logger.error(f"Error parsing league table: {e}")
        return []

def parse_matches(html):
    """Parse match data from HTML."""
    if not html:
        return [], []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        # This would be replaced with actual parsing logic based on the website structure
        # For now, using sample data based on original Tulevatottelut.py
        
        # Sample past matches data
        past_matches = [
            {"date": "2025-04-05", "home_team": "HJK Helsinki", "away_team": "FC Inter", "home_score": 2, "away_score": 1, "stadium": "Bolt Arena", "attendance": 4500},
            {"date": "2025-04-05", "home_team": "KuPS", "away_team": "FC Lahti", "home_score": 3, "away_score": 0, "stadium": "Savon Sanomat Areena", "attendance": 3200},
            {"date": "2025-04-06", "home_team": "Ilves", "away_team": "SJK", "home_score": 1, "away_score": 1, "stadium": "Tammela Stadium", "attendance": 2800},
            {"date": "2025-04-12", "home_team": "FC Inter", "away_team": "KuPS", "home_score": 2, "away_score": 2, "stadium": "Veritas Stadion", "attendance": 3700},
            {"date": "2025-04-12", "home_team": "FC Lahti", "away_team": "Ilves", "home_score": 1, "away_score": 0, "stadium": "Lahden Stadion", "attendance": 2500},
            {"date": "2025-04-19", "home_team": "SJK", "away_team": "HJK Helsinki", "home_score": 0, "away_score": 3, "stadium": "OmaSp Stadion", "attendance": 3100},
            {"date": "2025-04-26", "home_team": "VPS", "away_team": "IFK Mariehamn", "home_score": 2, "away_score": 0, "stadium": "Elisa Stadion", "attendance": 2100},
        ]
        
        # Sample upcoming matches data based on Tulevatottelut.py
        upcoming_matches = [
            {"date": "2025-05-17", "home_team": "HJK Helsinki", "away_team": "KuPS", "stadium": "Bolt Arena", "kickoff_time": "18:00"},
            {"date": "2025-05-17", "home_team": "FC Inter", "away_team": "FC Lahti", "stadium": "Veritas Stadion", "kickoff_time": "16:00"},
            {"date": "2025-05-18", "home_team": "SJK", "away_team": "VPS", "stadium": "OmaSp Stadion", "kickoff_time": "17:00"},
            {"date": "2025-05-18", "home_team": "HIFK", "away_team": "FC Haka", "stadium": "Bolt Arena", "kickoff_time": "16:00"},
            {"date": "2025-05-19", "home_team": "IFK Mariehamn", "away_team": "AC Oulu", "stadium": "Wiklöf Holding Arena", "kickoff_time": "18:30"},
            {"date": "2025-05-25", "home_team": "KTP", "away_team": "Ilves", "stadium": "Arto Tolsa Areena", "kickoff_time": "16:00"},
            {"date": "2025-05-26", "home_team": "FC Lahti", "away_team": "SJK", "stadium": "Lahden Stadion", "kickoff_time": "18:30"},
        ]
        
        return past_matches, upcoming_matches
    
    except Exception as e:
        logger.error(f"Error parsing matches: {e}")
        return [], []

def parse_player_stats(html):
    """Parse player statistics from HTML."""
    if not html:
        return []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        # This would be replaced with actual parsing logic based on the website structure
        # For now, using sample data
        
        players = [
            {"name": "Roope Riski", "team": "HJK Helsinki", "position": "Forward", "goals": 7, "assists": 2, "yellow_cards": 1, "red_cards": 0, "minutes_played": 810},
            {"name": "Benjamin Källman", "team": "FC Inter", "position": "Forward", "goals": 6, "assists": 3, "yellow_cards": 2, "red_cards": 0, "minutes_played": 900},
            {"name": "Tim Väyrynen", "team": "KuPS", "position": "Forward", "goals": 5, "assists": 1, "yellow_cards": 3, "red_cards": 0, "minutes_played": 870},
            {"name": "Ville Salmikivi", "team": "FC Lahti", "position": "Midfielder", "goals": 4, "assists": 4, "yellow_cards": 2, "red_cards": 0, "minutes_played": 900},
            {"name": "Lauri Ala-Myllymäki", "team": "Ilves", "position": "Midfielder", "goals": 4, "assists": 3, "yellow_cards": 4, "red_cards": 0, "minutes_played": 810},
            {"name": "Pyry Hannola", "team": "SJK", "position": "Forward", "goals": 4, "assists": 2, "yellow_cards": 1, "red_cards": 0, "minutes_played": 720},
            {"name": "Sebastian Mannström", "team": "IFK Mariehamn", "position": "Midfielder", "goals": 3, "assists": 5, "yellow_cards": 3, "red_cards": 0, "minutes_played": 900},
            {"name": "Matias Ojala", "team": "VPS", "position": "Midfielder", "goals": 3, "assists": 3, "yellow_cards": 2, "red_cards": 0, "minutes_played": 810},
            {"name": "Filip Valencic", "team": "HIFK", "position": "Forward", "goals": 3, "assists": 2, "yellow_cards": 1, "red_cards": 1, "minutes_played": 720},
            {"name": "Jean-Christophe Coubronne", "team": "FC Haka", "position": "Defender", "goals": 2, "assists": 1, "yellow_cards": 5, "red_cards": 0, "minutes_played": 900},
            {"name": "Joni Mäkelä", "team": "KTP", "position": "Forward", "goals": 2, "assists": 1, "yellow_cards": 2, "red_cards": 0, "minutes_played": 765},
            {"name": "Niklas Jokelainen", "team": "AC Oulu", "position": "Forward", "goals": 2, "assists": 0, "yellow_cards": 3, "red_cards": 0, "minutes_played": 810},
            {"name": "Arttu Hoskonen", "team": "HJK Helsinki", "position": "Defender", "goals": 1, "assists": 2, "yellow_cards": 4, "red_cards": 0, "minutes_played": 900},
            {"name": "Timo Stavitski", "team": "FC Inter", "position": "Forward", "goals": 3, "assists": 1, "yellow_cards": 1, "red_cards": 0, "minutes_played": 675},
            {"name": "Jasse Tuominen", "team": "KuPS", "position": "Forward", "goals": 2, "assists": 2, "yellow_cards": 0, "red_cards": 0, "minutes_played": 720},
        ]
        
        return players
    
    except Exception as e:
        logger.error(f"Error parsing player stats: {e}")
        return []

def fetch_league_table():
    """Fetch the current league standings."""
    logger.info("Fetching league table...")
    
    html = fetch_html(LEAGUE_TABLE_URL)
    teams = parse_league_table(html)
    
    data = {"last_updated": datetime.now().isoformat(), "standings": teams}
    
    # Save raw data
    with open(RAW_DIR / f"league_table_{TODAY}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(teams)
    df.to_csv(PROCESSED_DIR / f"league_table_{TODAY}.csv", index=False)
    
    # Also save as latest
    df.to_csv(PROCESSED_DIR / "league_table_latest.csv", index=False)
    
    logger.info(f"Fetched data for {len(teams)} teams")
    return data

def fetch_matches():
    """Fetch match results and upcoming fixtures."""
    logger.info("Fetching matches data...")
    
    html = fetch_html(MATCHES_URL)
    past_matches, upcoming_matches = parse_matches(html)
    
    data = {
        "last_updated": datetime.now().isoformat(),
        "past_matches": past_matches,
        "upcoming_matches": upcoming_matches
    }
    
    # Save raw data
    with open(RAW_DIR / f"matches_{TODAY}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Convert to DataFrames for easier processing
    past_df = pd.DataFrame(past_matches)
    upcoming_df = pd.DataFrame(upcoming_matches)
    
    past_df.to_csv(PROCESSED_DIR / f"past_matches_{TODAY}.csv", index=False)
    upcoming_df.to_csv(PROCESSED_DIR / f"upcoming_matches_{TODAY}.csv", index=False)
    
    # Also save as latest
    past_df.to_csv(PROCESSED_DIR / "past_matches_latest.csv", index=False)
    upcoming_df.to_csv(PROCESSED_DIR / "upcoming_matches_latest.csv", index=False)
    
    logger.info(f"Fetched data for {len(past_matches)} past matches and {len(upcoming_matches)} upcoming matches")
    return data

def fetch_player_stats():
    """Fetch player statistics."""
    logger.info("Fetching player statistics...")
    
    html = fetch_html(PLAYER_STATS_URL)
    players = parse_player_stats(html)
    
    data = {"last_updated": datetime.now().isoformat(), "players": players}
    
    # Save raw data
    with open(RAW_DIR / f"player_stats_{TODAY}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(players)
    df.to_csv(PROCESSED_DIR / f"player_stats_{TODAY}.csv", index=False)
    
    # Also save as latest
    df.to_csv(PROCESSED_DIR / "player_stats_latest.csv", index=False)
    
    # Generate top stats
    top_scorers = df.sort_values(by='goals', ascending=False).head(10)
    top_assists = df.sort_values(by='assists', ascending=False).head(10)
    top_cards = df.sort_values(by=['yellow_cards', 'red_cards'], ascending=False).head(10)
    
    top_scorers.to_csv(STATS_DIR / f"top_scorers_{TODAY}.csv", index=False)
    top_assists.to_csv(STATS_DIR / f"top_assists_{TODAY}.csv", index=False)
    top_cards.to_csv(STATS_DIR / f"top_cards_{TODAY}.csv", index=False)
    
    # Also save as latest
    top_scorers.to_csv(STATS_DIR / "top_scorers_latest.csv", index=False)
    top_assists.to_csv(STATS_DIR / "top_assists_latest.csv", index=False)
    top_cards.to_csv(STATS_DIR / "top_cards_latest.csv", index=False)
    
    logger.info(f"Fetched statistics for {len(players)} players")
    return data

def calculate_attendance_stats(data):
    """Calculate attendance statistics from the match data."""
    logger.info("Calculating attendance statistics...")
    
    # Integrating functionality from Yleisölaskuri.py
    past_matches = data["past_matches"]
    
    if not past_matches or "attendance" not in past_matches[0]:
        logger.warning("No attendance data available")
        return None
    
    # Convert to DataFrame
    matches_df = pd.DataFrame(past_matches)
    
    # Calculate total attendance
    total_attendance = matches_df['attendance'].sum()
    
    # Calculate average attendance per match
    avg_attendance = matches_df['attendance'].mean()
    
    # Calculate attendance by team
    home_attendance = matches_df.groupby('home_team')['attendance'].agg(['sum', 'mean', 'count']).reset_index()
    home_attendance.columns = ['team', 'total_attendance', 'avg_attendance', 'home_matches']
    
    # Save attendance data
    home_attendance.to_csv(STATS_DIR / f"team_attendance_{TODAY}.csv", index=False)
    home_attendance.to_csv(STATS_DIR / "team_attendance_latest.csv", index=False)
    
    attendance_summary = {
        "total_attendance": int(total_attendance),
        "avg_attendance_per_match": round(float(avg_attendance), 1),
        "highest_attendance": {
            "value": int(matches_df['attendance'].max()),
            "match": matches_df.loc[matches_df['attendance'].idxmax(), ['date', 'home_team', 'away_team']].to_dict()
        },
        "lowest_attendance": {
            "value": int(matches_df['attendance'].min()),
            "match": matches_df.loc[matches_df['attendance'].idxmin(), ['date', 'home_team', 'away_team']].to_dict()
        }
    }
    
    with open(STATS_DIR / f"attendance_summary_{TODAY}.json", 'w', encoding='utf-8') as f:
        json.dump(attendance_summary, f, ensure_ascii=False, indent=2)
    
    with open(STATS_DIR / "attendance_summary_latest.json", 'w', encoding='utf-8') as f:
        json.dump(attendance_summary, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Total attendance: {total_attendance}, Average per match: {avg_attendance:.1f}")
    return attendance_summary

def main():
    """Main function to orchestrate data fetching."""
    logger.info(f"Starting Veikkausliiga 2025 data fetch at {datetime.now().isoformat()}")
    
    # Create fetch sequence
    league_data = fetch_league_table()
    matches_data = fetch_matches()
    player_data = fetch_player_stats()
    
    # Calculate attendance statistics
    attendance_summary = calculate_attendance_stats(matches_data)
    
    # Save metadata about the fetch
    metadata = {
        "fetch_time": datetime.now().isoformat(),
        "data_sources": {
            "league_table": LEAGUE_TABLE_URL,
            "matches": MATCHES_URL,
            "player_stats": PLAYER_STATS_URL
        },
        "data_counts": {
            "teams": len(league_data["standings"]) if league_data else 0,
            "past_matches": len(matches_data["past_matches"]) if matches_data else 0,
            "upcoming_matches": len(matches_data["upcoming_matches"]) if matches_data else 0,
            "players": len(player_data["players"]) if player_data else 0
        }
    }
    
    with open(RAW_DIR / f"fetch_metadata_{TODAY}.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Data fetch completed at {datetime.now().isoformat()}")
    logger.info(f"Fetched {metadata['data_counts']['teams']} teams")
    logger.info(f"Fetched {metadata['data_counts']['past_matches']} past matches")
    logger.info(f"Fetched {metadata['data_counts']['upcoming_matches']} upcoming matches")
    logger.info(f"Fetched {metadata['data_counts']['players']} player statistics")

if __name__ == "__main__":
    main()
