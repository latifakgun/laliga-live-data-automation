import pandas as pd
import requests
from io import StringIO
import time
import os
import sys
from kaggle.api.kaggle_api_extended import KaggleApi

def scrape_fbref_laliga():
    print("--- FBref Sitesinden Veri Çekiliyor ---")
    
    # La Liga 2025-2026 Fikstür Sayfası URL'i
    # (Sezon değiştikçe buradaki yılı değiştirmek yeterli olur)
    url = "https://fbref.com/en/comps/12/schedule/La-Liga-Scores-and-Fixtures"
    
    # Kendimizi tarayıcı gibi tanıtıyoruz (Yoksa site bizi engeller)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Hata varsa durdur
        
        # HTML içindeki tabloları oku
        # match="Scores & Fixtures" diyerek doğru tabloyu hedefliyoruz
        dfs = pd.read_html(StringIO(response.text), match="Scores & Fixtures")
        
        if not dfs:
            print("HATA: Tablo bulunamadı.")
            return []
            
        df = dfs[0]
        
        # --- VERİ TEMİZLEME ---
        # 1. Sadece oynanmış maçları al (Skoru belli olanlar)
        # 'Score' sütunu boş olmayanları seçiyoruz
        df_filtered = df[df['Score'].notna()].copy()
        
        # 2. Gereksiz sütunları at (Varsa)
        # Genelde 'Match Report' ve 'Notes' gibi boş sütunlar gelir
        cols_to_keep = ['Wk', 'Day', 'Date', 'Time', 'Home', 'Score', 'Away', 'Attendance', 'Venue', 'Referee']
        # Sadece mevcut olan sütunları seçelim (Hata almamak için)
        available_cols = [c for c in cols_to_keep if c in df_filtered.columns]
        df_final = df_filtered[available_cols]
        
        # 3. Skoru ayır (İsteğe bağlı - Daha temiz analiz için)
        # Score "2–1" şeklindedir. Bunu Home_Goal: 2, Away_Goal: 1 diye bölelim
        try:
            df_final[['Home_Goals', 'Away_Goals']] = df_final['Score'].str.split('–', expand=True)
        except:
            pass # Ayıramazsa sorun yok, Score sütunu kalsın

        print(f"Başarılı! Toplam {len(df_final)} oynanmış maç çekildi.")
        return df_final

    except Exception as e:
        print(f"Scraping Hatası: {e}")
        sys.exit(1)

def save_and_upload(df):
    if df is None or len(df) == 0:
        print("Veri yok, işlem iptal.")
        return

    print("--- CSV Kaydediliyor ---")
    filename = "laliga_2025_2026_stats.csv"
    df.to_csv(filename, index=False)
    print(f"Dosya oluşturuldu: {filename}")

    print("--- Kaggle Yüklemesi ---")
    if not os.path.exists("dataset-metadata.json"):
        print("HATA: Metadata dosyası yok!")
        sys.exit(1)

    try:
        api = KaggleApi()
        api.authenticate()
        
        api.dataset_create_version(
            folder=".",
            version_notes=f"Weekly Update (FBref): {pd.Timestamp.now().strftime('%Y-%m-%d')}",
            dir_mode='zip'
        )
        print("--- BAŞARILI: Kaggle Güncellendi! ---")
    except Exception as e:
        print(f"Kaggle Hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 1. Veriyi Çek
    data_frame = scrape_fbref_laliga()
    
    # 2. Kaydet ve Yükle
    save_and_upload(data_frame)
