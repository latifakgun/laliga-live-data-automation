import requests
import pandas as pd
import os
import json
from kaggle.api.kaggle_api_extended import KaggleApi

# --- AYARLAR ---
# GitHub Secrets'tan alınacak API anahtarları
API_KEY = os.environ.get("FOOTBALL_API_KEY") 
LEAGUE_ID = 140  # La Liga
SEASON = 2025    # 2025-2026 Sezonu için '2025' yazılır.

def get_la_liga_stats():
    print(f"La Liga {SEASON}-{SEASON+1} sezonu verileri çekiliyor...")
    url = "https://v3.football.api-sports.io/fixtures"
    
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }
    
    # Sadece bitmiş (FT) maçları istiyoruz
    params = {
        "league": LEAGUE_ID,
        "season": SEASON,
        "status": "FT"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # Hata varsa durdur
        data = response.json()
    except Exception as e:
        print(f"API Bağlantı Hatası: {e}")
        return []
    
    match_list = []
    
    if 'response' in data:
        for match in data['response']:
            fixture = match['fixture']
            teams = match['teams']
            goals = match['goals']
            league = match['league']
            
            match_data = {
                'season': f"{league['season']}-{league['season']+1}", # Örn: 2025-2026
                'round': league['round'],
                'date': fixture['date'],
                'timestamp': fixture['timestamp'],
                'home_team': teams['home']['name'],
                'away_team': teams['away']['name'],
                'home_goals': goals['home'],
                'away_goals': goals['away'],
                'home_win': teams['home']['winner'],
                'away_win': teams['away']['winner'],
                'venue': fixture['venue']['name'],
                'referee': fixture['referee'],
                'status': fixture['status']['long']
            }
            match_list.append(match_data)
        return match_list
    else:
        print("API yanıtında veri bulunamadı:", data)
        return []

def save_and_upload(data):
    if not data:
        print("Veri boş, Kaggle güncellemesi iptal edildi.")
        return

    # 1. CSV Olarak Kaydet
    filename = "laliga_2025_2026_stats.csv"
    df = pd.DataFrame(data)
    
    # Veriyi tarihe göre sıralayalım (Eskiden yeniye)
    if 'date' in df.columns:
        df = df.sort_values(by='date')
        
    df.to_csv(filename, index=False)
    print(f"CSV oluşturuldu: {filename} ({len(df)} maç)")

    # 2. Kaggle'a Yükle
    print("Kaggle dataset versiyonu güncelleniyor...")
    try:
        api = KaggleApi()
        api.authenticate()
        
        # Bulunduğumuz klasördeki dosyayı yükle
        api.dataset_create_version(
            folder=".",
            version_notes=f"Week Update: {pd.Timestamp.now().strftime('%Y-%m-%d')}",
            dir_mode='zip'
        )
        print("BAŞARILI: Kaggle dataset güncellendi!")
    except Exception as e:
        print(f"HATA: Kaggle yüklemesi başarısız oldu. Sebep: {e}")

if __name__ == "__main__":
    stats = get_la_liga_stats()
    save_and_upload(stats)