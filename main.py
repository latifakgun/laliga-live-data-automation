import requests
import os

# GitHub'dan şifreyi al
API_KEY = os.environ.get("FOOTBALL_API_KEY")

def test_api():
    print("--- API TESTİ BAŞLIYOR ---")
    
    # 1. API KEY KONTROLÜ
    if not API_KEY:
        print("HATA: API Key yok! Secret ayarlarını kontrol et.")
        return
    else:
        # Güvenlik için sadece ilk 5 karakteri gösterelim
        print(f"API Key Algılandı: {API_KEY[:5]}**************")

    # 2. İSTEK ATMA
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }
    
    # Test için 2024 sezonunu (geçen sene) deneyelim, kesin veri vardır.
    params = {
        "league": 140,  # La Liga
        "season": 2024, # Geçen sezon (Garanti olsun)
        "status": "FT"  # Biten maçlar
    }

    print(f"İstek Yapılıyor: Lig=140, Sezon=2024...")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        print(f"HTTP Durum Kodu: {response.status_code}")
        print("--- API CEVABI (HAM VERİ) ---")
        print(response.text) # API ne diyorsa ekrana bas
        print("-----------------------------")
        
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")

if __name__ == "__main__":
    test_api()
