import requests
import json
import gzip
import os
from io import BytesIO

# =============================================================================
# KAYNAK SIRALAMA AYARI - İstediğiniz sırayı buradan değiştirebilirsiniz
# =============================================================================
# Kullanılabilir kaynaklar: "kablo", "dsmart", "boncuktv", "goldvod"
# İlk kaynak başarısız olursa sırayla diğerlerine geçer

SOURCE_ORDER = ["dsmart", "kablo", "boncuktv", "goldvod"]

# =============================================================================
# GENEL AYARLAR
# =============================================================================
OUTPUT_FILENAME = "yeni.m3u"

# =============================================================================
# KABLO (CanliTV) KAYNAĞI
# =============================================================================
def get_kablo_m3u():
    """CanliTV API'den m3u verisi çeker"""
    
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJjZ2QiOiIwOTNkNzIwYS01MDJjLTQxZWQtYTgwZi0yYjgxNjk4NGZiOTUiLCJkaSI6IjBmYTAzNTlkLWExOWItNDFiMi05ZTczLTI5ZWNiNjk2OTY0MCIsImFwdiI6IjEuMC4wIiwiZW52IjoiTElWRSIsImFibiI6IjEwMDAiLCJzcGdkIjoiYTA5MDg3ODQtZDEyOC00NjFmLWI3NmItYTU3ZGViMWI4MGNjIiwiaWNoIjoiMCIsInNnZCI6ImViODc3NDRjLTk4NDItNDUwNy05YjBhLTQ0N2RmYjg2NjJhZCIsImlkbSI6IjAiLCJkY3QiOiIzRUY3NSIsImlhIjoiOjpmZmZmOjEwLjAuMC41IiwiY3NoIjoiVFJLU1QiLCJpcGIiOiIwIn0.bT8PK2SvGy2CdmbcCnwlr8RatdDiBe_08k7YlnuQqJE"
    }
    params = {"checkip": "false"}
    
    try:
        print("📡 Kablo (CanliTV) API'den veri alınıyor...")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        # Gzip decode
        try:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
                content = gz.read().decode('utf-8')
        except:
            content = response.content.decode('utf-8')
        
        data = json.loads(content)
        
        if not data.get('IsSucceeded') or not data.get('Data', {}).get('AllChannels'):
            print("❌ Kablo: Geçerli veri alınamadı!")
            return False
        
        channels = data['Data']['AllChannels']
        print(f"✅ Kablo: {len(channels)} kanal bulundu")
        
        # M3U dosyası oluştur
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
            
            kanal_sayisi = 0
            kanal_index = 1
            
            for channel in channels:
                name = channel.get('Name')
                stream_data = channel.get('StreamData', {})
                hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
                logo = channel.get('PrimaryLogoImageUrl', '')
                categories = channel.get('Categories', [])
                
                if not name or not hls_url:
                    continue
                
                group = categories[0].get('Name', 'Genel') if categories else 'Genel'
                
                # Bilgilendirme kategorisini atla
                if group == "Bilgilendirme":
                    continue
                
                tvg_id = str(kanal_index)
                
                f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{hls_url}\n')
                
                kanal_sayisi += 1
                kanal_index += 1
        
        print(f"✅ Kablo: {OUTPUT_FILENAME} başarıyla oluşturuldu! ({kanal_sayisi} kanal)")
        return True
        
    except Exception as e:
        print(f"❌ Kablo hatası: {e}")
        return False

# =============================================================================
# DSMART KAYNAĞI
# =============================================================================
def get_dsmart_m3u():
    """DSmart API'den m3u verisi çeker"""
    
    api_url = "https://service-dsmartv2.erstream.com/api/GetFilteredVideos"
    image_base_url = "https://dsmart-static-v2.ercdn.net//resize-width/500"
    
    category_order = [
        "Ulusal", "Film", "Dizi", "Spor", "Çocuk", "Belgesel",
        "Haber", "Müzik", "Eğlence", "Uluslararası", "Eğitim", "Çoklu Kanallar"
    ]
    
    payload = {
        "Categories": [118],
        "PageSize": 200,
        "PageIndex": 0,
        "Language": "",
        "ContentTypes": [7],
        "CustomFilters": [],
        "SortDirection": "ASC",
        "SortType": "Custom",
        "CustomSortField": "order"
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("📡 DSmart API'den veri alınıyor...")
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ DSmart API Hatası: {response.status_code}")
            return False
        
        items = response.json().get("Items", [])
        
        if not items:
            print("❌ DSmart: Veri bulunamadı")
            return False
        
        print(f"✅ DSmart: {len(items)} kanal bulundu")
        
        # Kanalları kategorilerine göre grupla
        grouped_channels = {cat: [] for cat in category_order}
        grouped_channels["Diğer"] = []
        
        for item in items:
            name = item.get("Name", "Bilinmeyen Kanal")
            
            # Kategori bul
            group = "Diğer"
            for meta in item.get("Metadata", []):
                if meta.get("NameSpace") == "genres":
                    val = meta.get("Value")
                    if val in category_order:
                        group = val
                    else:
                        group = "Diğer"
                    break
            
            # Logo bul
            logo_url = ""
            for img in item.get("Images", []):
                if img.get("ImageType") == "Thumbnail":
                    logo_url = f"{image_base_url}{img.get('ImageUrl', '')}"
                    break
            
            # Stream URL bul
            stream_url = ""
            for cdn in item.get("CdnUrls", []):
                if cdn.get("ContentType") == 7:
                    stream_url = cdn.get("ContentUrl", "")
                    break
            
            if stream_url:
                channel_data = {
                    "name": name,
                    "group": group,
                    "logo": logo_url,
                    "url": stream_url
                }
                grouped_channels[group].append(channel_data)
        
        # M3U dosyası oluştur
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            order_to_write = category_order + ["Diğer"]
            total_channels = 0
            
            for cat in order_to_write:
                channels = grouped_channels.get(cat, [])
                if channels:
                    for ch in channels:
                        f.write(f'#EXTINF:-1 group-title="{ch["group"]}" tvg-logo="{ch["logo"]}", {ch["name"]}\n')
                        f.write(f"{ch['url']}\n")
                        total_channels += 1
        
        print(f"✅ DSmart: {OUTPUT_FILENAME} başarıyla oluşturuldu! ({total_channels} kanal)")
        return True
        
    except Exception as e:
        print(f"❌ DSmart hatası: {e}")
        return False

# =============================================================================
# BONCUKTV YEDEK KAYNAĞI
# =============================================================================
def get_boncuktv_m3u():
    """BoncukTV yedek kaynağından m3u indirir"""
    
    try:
        print("📡 BoncukTV yedek kaynağından indiriliyor...")
        
        response = requests.get("https://mth.tc/boncuktv", timeout=30)
        response.raise_for_status()
        
        # İlk satırı atla
        lines = response.text.split('\n')
        content = '\n'.join(lines[1:]) if lines else response.text
        
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ BoncukTV: {OUTPUT_FILENAME} başarıyla indirildi!")
        return True
        
    except Exception as e:
        print(f"❌ BoncukTV hatası: {e}")
        return False

# =============================================================================
# GOLDVOD YEDEK KAYNAĞI
# =============================================================================
def get_goldvod_m3u():
    """GoldVOD yedek kaynağından m3u indirir"""
    
    try:
        print("📡 GoldVOD yedek kaynağından indiriliyor...")
        
        response = requests.get(
            "https://goldvod.org/get.php?username=hpgdisco&password=123456&type=m3u_plus",
            timeout=30
        )
        response.raise_for_status()
        
        # İlk satırı atla
        lines = response.text.split('\n')
        content = '\n'.join(lines[1:]) if lines else response.text
        
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ GoldVOD: {OUTPUT_FILENAME} başarıyla indirildi!")
        return True
        
    except Exception as e:
        print(f"❌ GoldVOD hatası: {e}")
        return False

# =============================================================================
# ANA FONKSİYON
# =============================================================================
def main():
    """Belirlenen sıraya göre kaynakları dener"""
    
    # Kaynak fonksiyonları mapping
    sources = {
        "kablo": get_kablo_m3u,
        "dsmart": get_dsmart_m3u,
        "boncuktv": get_boncuktv_m3u,
        "goldvod": get_goldvod_m3u
    }
    
    print("=" * 60)
    print("🎬 M3U Dosyası Oluşturucu")
    print("=" * 60)
    print(f"📋 Kaynak sıralaması: {' → '.join(SOURCE_ORDER)}")
    print("=" * 60)
    print()
    
    # Sırayla kaynakları dene
    for source_name in SOURCE_ORDER:
        if source_name not in sources:
            print(f"⚠️ Bilinmeyen kaynak atlandı: {source_name}")
            continue
        
        print(f"\n{'=' * 60}")
        print(f"🔄 Denenen kaynak: {source_name.upper()}")
        print(f"{'=' * 60}")
        
        success = sources[source_name]()
        
        if success:
            print(f"\n{'=' * 60}")
            print(f"🎉 BAŞARILI! {source_name.upper()} kaynağından m3u oluşturuldu")
            print(f"📁 Dosya: {OUTPUT_FILENAME}")
            print(f"{'=' * 60}")
            return
        else:
            print(f"\n⚠️ {source_name.upper()} kaynağı başarısız, sonraki kaynağa geçiliyor...")
    
    # Tüm kaynaklar başarısız
    print("\n" + "=" * 60)
    print("❌ TÜM KAYNAKLAR BAŞARISIZ OLDU!")
    print("=" * 60)

if __name__ == "__main__":
    main()
