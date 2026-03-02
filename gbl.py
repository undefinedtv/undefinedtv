import requests
from bs4 import BeautifulSoup
import re
import time
import json
import gzip
import os
from io import BytesIO
import subprocess

# CALMA OC

SOURCE_ORDER = ["legal", "uzun", "canak", "boncuktv","goldvod", "kablo", "smart"]

OUTPUT_FILENAME = "yeni.m3u"

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
# SMART KAYNAĞI
# =============================================================================
def get_smart_m3u():
    """Smart API'den m3u verisi çeker"""
    
    url = os.getenv("SMART_API")
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,tr;q=0.8",
        "apikey": "a8fbff0087d146ddbfa26a13ebbf83c6",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "langcode": "tr",
        "origin": "https://www.dsmartgo.com.tr",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.dsmartgo.com.tr/",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    }
    
    category_order = [
        "Ulusal", "Haber", "Belgesel", "Spor", "Film", "Dizi",  "Çocuk", 
         "Müzik", "Eğlence", "Uluslararası", "Eğitim", "Çoklu Kanallar"
    ]
    
    payload = {
        "displayCount": 150,
        "contentTypeIds": [27819],
        "customFilters": [],
        "sort": {
            "field": "CustomFieldOrder",
            "order": "asc",
            "namespace": "Order"
        },
        "include": ["customField"],
        "pageNumber": 1
    }
    
    try:
        print("📡 Smart API'den veri alınıyor...")
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"❌ Smart API Hatası: {response.status_code}")
            return False
        
        items = response.json().get("data", [])
        
        if not items:
            print("❌ Smart: Veri bulunamadı")
            return False
        
        print(f"✅ Smart: {len(items)} kanal bulundu")
        
        # Kanalları kategorilerine göre grupla
        grouped_channels = {cat: [] for cat in category_order}
        grouped_channels["Diğer"] = []
        
        for item in items:
            name = item.get("name", "Bilinmeyen Kanal")
            
            # Kategori bul
            group = "Diğer"
            for meta in item.get("customFields", []):
                if meta.get("namespace") == "genres":
                    val = meta.get("value")
                    if val in category_order:
                        group = val
                    else:
                        group = "Diğer"
                    break
            
            # Logo bul
            logo_url = ""
            for img in item.get("Images", []):
                if img.get("ImageType") == "Thumbnail":
                    logo_url = img.get('url')
                    break
            
            # Stream URL bul
            stream_url = ""
            for cdn in item.get("videos", []):
                if cdn.get("type") == 'HLS-Auto':
                    stream_url = cdn.get("url") + "?e=1772026853&rid=530176d0c648e51185fe5bce9e47bc23&st=gJ7G-sLtC62WAy48-xBY5g&userid=ed255453&sid=8740o1bzlcqk&app=4caf18fc-b51a-40c1-94d1-2940555a42f9&ce=2"
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
            f.write("")
            
            order_to_write = category_order + ["Diğer"]
            total_channels = 0
            
            for cat in order_to_write:
                channels = grouped_channels.get(cat, [])
                if channels:
                    for ch in channels:
                        f.write(f'#EXTINF:-1 group-title="{ch["group"]}" tvg-logo="{ch["logo"]}", {ch["name"]}\n')
                        f.write(f"{ch['url']}\n")
                        total_channels += 1
        
        print(f"✅ Smart: {OUTPUT_FILENAME} başarıyla oluşturuldu! ({total_channels} kanal)")
        return True
        
    except Exception as e:
        print(f"❌ Smart hatası: {e}")
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
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(
            "https://goldvod.site/get.php?username=hpgdisco&password=123456&type=m3u_plus",
            headers=headers,
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
# LEGAL YEDEK KAYNAĞI
# =============================================================================
def get_legal_m3u():
    """LEGAL yedek kaynağından m3u indirir"""
    
    try:
        print("📡 LEGAL yedek kaynağından indiriliyor...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(
            "https://raw.githubusercontent.com/undefinedtv/undefinedtv/refs/heads/main/legal.m3u",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        content = response.text
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ LEGAL: {OUTPUT_FILENAME} başarıyla indirildi!")
        return True
        
    except Exception as e:
        print(f"❌ LEGAL hatası: {e}")
        return False

# =============================================================================
# UZUN YEDEK KAYNAĞI
# =============================================================================
def get_uzun_m3u():
    """UZUN yedek kaynağından m3u indirir"""
    
    try:
        print("📡 UZUN yedek kaynağından indiriliyor...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(
            "https://streams.uzunmuhalefet.com/lists/tr.m3u",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        # İlk satırı atla
        lines = response.text.split('\n')
        content = '\n'.join(lines[1:]) if lines else response.text
        
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ UZUN: {OUTPUT_FILENAME} başarıyla indirildi!")
        return True
        
    except Exception as e:
        print(f"❌ UZUN hatası: {e}")
        return False
        
def get_canak_m3u():
    # ═══════════════════════════════════════════════════════════════
    # GRUP SIRASI VE KANAL EŞLEMESİ (Referans M3U yapısından)
    # ═══════════════════════════════════════════════════════════════

    GROUP_ORDER = [
        "Ulusal", "Haber", "Ekonomi","Spor","Belgesel", "Ulusal - Yurt Dışı", "Eğlence",
         "Müzik",  "Çocuk", "Dini", "Diğer", "Yerel",
        "Kurumlar", "Kıbrıs", "Müzik - Diğer", "7/24 Dizi"
    ]

    # CanakTV kategori → bilinmeyen kanallar için varsayılan grup
    CATEGORY_TO_GROUP = {
        "genel": "Diğer", "haber": "Haber", "spor": "Spor",
        "yerel": "Yerel", "cocuk": "Çocuk", "dini": "Dini",
        "muzik": "Müzik", "belgesel": "Belgesel"
    }

    # normalize(isim) → (Grup, Sıra)
    CHANNEL_MAP = {
        # ─────────────── Ulusal ───────────────
        "trt 1": ("Ulusal", 1), "trt1": ("Ulusal", 1),
        "atv": ("Ulusal", 2),
        "kanal d": ("Ulusal", 3),
        "now tv": ("Ulusal", 4), 
        "show tv": ("Ulusal", 5),
        "beyaz tv": ("Ulusal", 6),
        "kanal 7": ("Ulusal", 7),
        "tv8": ("Ulusal", 8), "tv 8": ("Ulusal", 8),
        "star tv": ("Ulusal", 9),
        "360 tv": ("Ulusal", 10),
        "tv 100": ("Ulusal", 11), "tv100": ("Ulusal", 11),
        "tyt turk": ("Ulusal", 12),
        "a2": ("Eğlence", 13), "a2 tv": ("Eğlence", 13),
        "teve2": ("Eğlence", 14), "teve 2": ("Eğlence", 14),

        # ─────────────── Haber ───────────────
        "trt haber": ("Haber", 1),
        "a haber": ("Haber", 2), "ahaber": ("Haber", 2),
        "cnn turk": ("Haber", 3),
        "tgrt haber": ("Haber", 4),
        "haberturk": ("Haber", 5), "haberturk tv": ("Haber", 5),
        "haber global": ("Haber", 6),
        "ulke tv": ("Haber", 7),
        "halk tv": ("Haber", 8),
        "ntv": ("Haber", 9),
        "24 tv": ("Haber", 10),
        "sozcu tv": ("Haber", 11),
        "ekol tv": ("Haber", 12),
        "tvnet": ("Haber", 13), "tv net": ("Haber", 13),
        "tele1": ("Haber", 14), "tele 1": ("Haber", 14),
        "akit tv": ("Haber", 15),
        "ulusal kanal": ("Haber", 16),
        "flash haber tv": ("Haber", 17), "flash tv": ("Haber", 17),
        "lider haber tv": ("Haber", 18), "lider haber": ("Haber", 18),
        "neo haber": ("Haber", 19),
        "tbmm tv": ("Haber", 20),
        "dha 1": ("Haber", 21), "dha": ("Haber", 21),
        "dha 2": ("Haber", 22),
        "iha 1": ("Haber", 23), "iha": ("Haber", 23),
        "iha 2": ("Haber", 24),
        "bha tv": ("Haber", 25),
        "benguturk tv": ("Haber", 26), "bengutay tv": ("Haber", 26),
        "turkhaber": ("Haber", 27), "turkhaber tv": ("Haber", 27),
        "tr24 tv": ("Haber", 28),

        # ─────────────── Ulusal - Yurt Dışı ───────────────
        "trt turk": ("Ulusal - Yurt Dışı", 1),
        "trt avaz": ("Ulusal - Yurt Dışı", 2),
        "atv avrupa": ("Ulusal - Yurt Dışı", 3),
        "euro d": ("Ulusal - Yurt Dışı", 4),
        "tgrt eu": ("Ulusal - Yurt Dışı", 5),
        "show turk": ("Ulusal - Yurt Dışı", 6),
        "kanal 7 avrupa": ("Ulusal - Yurt Dışı", 7),
        "kanal avrupa": ("Ulusal - Yurt Dışı", 8),
        "trt world": ("Ulusal - Yurt Dışı", 9),
        "trt arabi": ("Ulusal - Yurt Dışı", 10),

        # ─────────────── Ekonomi ───────────────
        "a para": ("Ekonomi", 1),
        "bloomberg ht": ("Ekonomi", 2),
        "ekoturk": ("Ekonomi", 3),
        "finans turk": ("Ekonomi", 4), "finans turk tv": ("Ekonomi", 4),
        "gunedogus tv": ("Ekonomi", 5),
        "cnbc-e": ("Ekonomi", 6), "cnbce": ("Ekonomi", 6), "cnbc e": ("Ekonomi", 6),

        # ─────────────── Eğlence ───────────────
        "trt 2": ("Eğlence", 1), "trt2": ("Eğlence", 1),
        "show max": ("Eğlence", 4), "showmax": ("Eğlence", 4),
        "tv 8.5": ("Eğlence", 5), "tv8,5": ("Eğlence", 5),
        "tv8 5": ("Eğlence", 5), "tv 8 5": ("Eğlence", 5),
        "tv 4": ("Eğlence", 8), "tv4": ("Eğlence", 8),
        "gzt tv": ("Eğlence", 9),
        "tivi6": ("Eğlence", 10), "tivi 6": ("Eğlence", 10),
        "dizi-film tv": ("Eğlence", 11), "dizi film tv": ("Eğlence", 11),
        "fashion one tv": ("Eğlence", 12), "fashion one": ("Eğlence", 12),
        "super turk tv": ("Eğlence", 13),
        "kuzeymax": ("Eğlence", 14),
        "rich tv": ("Eğlence", 15),

        # ─────────────── Spor ───────────────
        "trt spor": ("Spor", 1),
        "trt spor yildiz": ("Spor", 2), "trt spor 2": ("Spor", 2),
        "trt 3 spor": ("Spor", 3), "trt 3": ("Spor", 3),
        "a spor": ("Spor", 4), "aspor": ("Spor", 4),
        "ht spor": ("Spor", 5),
        "ekol sports": ("Spor", 6),
        "tivibu spor": ("Spor", 7),
        "sports tv": ("Spor", 8),
        "fb tv": ("Spor", 9), "fenerbahce tv": ("Spor", 9),
        "tjk tv": ("Spor", 10),
        "tjk tv 2": ("Spor", 11),
        "tay tv": ("Spor", 12),
        "bric ve satranc tv": ("Spor", 13),
        "ztk tv": ("Spor", 14),
        "denizlispor tv": ("Spor", 15),
        "gs tv": ("Spor", 16), "galatasaray tv": ("Spor", 16),
        "bjk tv": ("Spor", 17), "besiktas tv": ("Spor", 17),
        "bein sports haber": ("Spor", 18),
        "bein sports 1": ("Spor", 19),
        "s sport": ("Spor", 20), "s sport 2": ("Spor", 21),
        "nba tv": ("Spor", 22), "eurosport": ("Spor", 23),

        # ─────────────── Müzik ───────────────
        "trt muzik": ("Müzik", 1),
        "dream turk": ("Müzik", 2), "dream tv": ("Müzik", 2),
        "powerturk tv": ("Müzik", 3), "power turk tv": ("Müzik", 3),
        "power tv": ("Müzik", 4),
        "number 1 turk": ("Müzik", 5), "number1 turk": ("Müzik", 5),
        "number 1 tv": ("Müzik", 6), "number1 tv": ("Müzik", 6),
        "kral pop tv": ("Müzik", 7),
        "tmb tv": ("Müzik", 8),
        "powerturk taptaze": ("Müzik", 9),
        "powerturk slow": ("Müzik", 10),
        "powerturk akustik": ("Müzik", 11),
        "power love": ("Müzik", 12),
        "power dance": ("Müzik", 13),
        "number 1 ask": ("Müzik", 14), "number1 ask": ("Müzik", 14),
        "number 1 damar": ("Müzik", 15), "number1 damar": ("Müzik", 15),
        "number 1 dance": ("Müzik", 16), "number1 dance": ("Müzik", 16),
        "4 turk pop": ("Müzik", 17),
        "muzik tv": ("Müzik", 18),
        "chill tv": ("Müzik", 19),
        "kral tv": ("Müzik", 20),
        "joy turk": ("Müzik", 21), "joytürk": ("Müzik", 21),
        "tv em": ("Müzik", 22), "muzik tr": ("Müzik", 23),

        # ─────────────── Belgesel ───────────────
        "national geographic": ("Belgesel", 1),
        "nat geo wild": ("Belgesel", 2),
        "tlc": ("Eğlence", 3), "tlc tv": ("Eğlence", 3),
        "dmax": ("Eğlence", 4), "d-max": ("Eğlence", 4),
        "trt belgesel": ("Belgesel", 1),
        "tgrt belgesel": ("Belgesel", 2),
        "cgtn belgesel": ("Belgesel", 3),
        "yaban tv": ("Belgesel", 4),
        "ciftci tv": ("Belgesel", 5),
        "koy tv": ("Belgesel", 6),
        "toprak tv": ("Belgesel", 7),
        "discovery channel": ("Belgesel", 10),
        "animal planet": ("Belgesel", 11),
        "history channel": ("Belgesel", 12),
        "bbc earth": ("Belgesel", 13),

        # ─────────────── Çocuk ───────────────
        "trt cocuk": ("Çocuk", 1),
        "trt diyanet cocuk": ("Çocuk", 2),
        "trt eba": ("Çocuk", 3), "trt eba tv": ("Çocuk", 3),
        "trt eba tv ilkokul": ("Çocuk", 4),
        "trt eba tv ortaokul": ("Çocuk", 5),
        "trt eba tv lise": ("Çocuk", 6),
        "minika cocuk": ("Çocuk", 7),
        "minika go": ("Çocuk", 8),
        "cartoon network": ("Çocuk", 9),
        "cizgi film tv": ("Çocuk", 10),
        "cocuklara ozel tv": ("Çocuk", 11),
        "disney channel": ("Çocuk", 12),
        "baby tv": ("Çocuk", 13),
        "nick jr": ("Çocuk", 14), "nickelodeon": ("Çocuk", 15),
        "planet cocuk": ("Çocuk", 16), "kidz tv": ("Çocuk", 17),

        # ─────────────── Dini ───────────────
        "diyanet tv": ("Dini", 1),
        "vav tv": ("Dini", 2),
        "semerkand tv": ("Dini", 3),
        "semerkand way": ("Dini", 4),
        "dost tv": ("Dini", 5),
        "meltem tv": ("Dini", 6),
        "ikra tv": ("Dini", 7),
        "on4 tv": ("Dini", 8),
        "lalegul tv": ("Dini", 9),
        "kanal 12": ("Dini", 10),
        "rehber tv": ("Dini", 11),
        "asf tv": ("Dini", 12),
        "al zahra turkic": ("Dini", 13),
        "sat 7 turk": ("Dini", 14),
        "abn turkey": ("Dini", 15),
        "kanal hayat": ("Dini", 16),
        "ilmihal tv": ("Dini", 17),
        "asr-i saadet tv": ("Dini", 18), "asri saadet tv": ("Dini", 18),
        "asr-i serif tv": ("Dini", 19), "asri serif tv": ("Dini", 19),
        "ilahi tv": ("Dini", 20),
        "islam tv": ("Dini", 21),
        "kultur ve sanat tv": ("Dini", 22), "kultur sanat tv": ("Dini", 22),
        "kuran-i kerim dersleri": ("Dini", 23), "kurani kerim dersleri": ("Dini", 23),
        "aile tv": ("Dini", 24),
        "mukabele tv": ("Dini", 25),
        "belgesel tv": ("Dini", 26),
        "tarih tv": ("Dini", 27),
        "vaaz tv": ("Dini", 28),
        "cem tv": ("Dini", 29),
        "hicret tv": ("Dini", 30),
        "hilal tv": ("Dini", 31),
        "method tv": ("Dini", 32),
        "ikt tv": ("Dini", 33),
        "kanal 5 konya": ("Dini", 34),
        "kanal 42": ("Dini", 35),

        # ─────────────── Diğer (bilinen) ───────────────
        "1tvtr": ("Diğer", 1),
        "ahad tv": ("Diğer", 2),
        "akkon tv": ("Diğer", 3),
        "baska tv": ("Diğer", 4),
        "begen tv": ("Diğer", 5),
        "bizim ocak tv": ("Diğer", 6),
        "cansuyu tv": ("Diğer", 7),
        "can tempo tv": ("Diğer", 8),
        "can tv": ("Diğer", 9),
        "channel 6 tv": ("Diğer", 10),
        "ekonomik nokta tv": ("Diğer", 11),
        "espiye tv": ("Diğer", 12),
        "euro 90 tv": ("Diğer", 13),
        "fark turk tv": ("Diğer", 14),
        "fashion world": ("Diğer", 15),
        "fit yasa tv": ("Diğer", 16),
        "fortuna tv": ("Diğer", 17),
        "gopsen tv": ("Diğer", 18),
        "haber caddesi tv": ("Diğer", 19),
        "kdc tv": ("Diğer", 20),
        "kisisel gelisim tv": ("Diğer", 21),
        "lugat tv": ("Diğer", 22),
        "nef tv": ("Diğer", 23),
        "play tv": ("Diğer", 24),
        "saglik channel": ("Diğer", 25),
        "saglik tv": ("Diğer", 26),
        "siteler tv": ("Diğer", 27),
        "spirity tv": ("Diğer", 28),
        "tvmor": ("Diğer", 29), "tv mor": ("Diğer", 29),
        "uluslararasi tv": ("Diğer", 30),
        "ureten turkiye tv": ("Diğer", 31),
        "yenicag tv": ("Diğer", 32),
        "tivi16": ("Diğer", 33), "tivi 16": ("Diğer", 33),

        # ─────────────── Yerel ───────────────
        "61 saat tv": ("Yerel", 1),
        "ahi tv": ("Yerel", 2),
        "aksu tv": ("Yerel", 3),
        "alanya posta tv": ("Yerel", 4),
        "altas tv": ("Yerel", 5),
        "anadolu dost tv": ("Yerel", 6),
        "anadolu net tv": ("Yerel", 7),
        "anadolum tv": ("Yerel", 8),
        "aras tv": ("Yerel", 9),
        "art amasya": ("Yerel", 10),
        "art world tv": ("Yerel", 11),
        "as tv": ("Yerel", 12),
        "atv alanya": ("Yerel", 13),
        "ay tv": ("Yerel", 14),
        "balkan turk": ("Yerel", 15),
        "bir tv": ("Yerel", 16),
        "bizim bergama tv": ("Yerel", 17),
        "brtv": ("Yerel", 18),
        "bruksel turk": ("Yerel", 19),
        "bulturk tv": ("Yerel", 20),
        "cankiri tv": ("Yerel", 21),
        "cay tv": ("Yerel", 22),
        "deniz postasi tv": ("Yerel", 23),
        "dim tv": ("Yerel", 24),
        "duzce tv": ("Yerel", 25),
        "edirne tv": ("Yerel", 26),
        "ege live tv": ("Yerel", 27), "ege tv": ("Yerel", 27),
        "erciyes tv": ("Yerel", 28),
        "ert erbaa": ("Yerel", 29),
        "er tv": ("Yerel", 30),
        "es tv": ("Yerel", 31),
        "etv kayseri": ("Yerel", 32),
        "etv manisa": ("Yerel", 33),
        "euro news 34": ("Yerel", 34),
        "frt tv fethiye": ("Yerel", 35),
        "gemlikin sesi tv": ("Yerel", 36),
        "gozde tv": ("Yerel", 37),
        "grt tv": ("Yerel", 38),
        "guneydogu tv": ("Yerel", 39),
        "haber 61 tv": ("Yerel", 40), "haber61 tv": ("Yerel", 40),
        "haber rize": ("Yerel", 41),
        "hunat tv": ("Yerel", 42),
        "hur tv": ("Yerel", 43),
        "icel tv": ("Yerel", 44),
        "ilke tv": ("Yerel", 45),
        "isvicre tv": ("Yerel", 46),
        "izmir time 35 tv": ("Yerel", 47),
        "izmir turk tv": ("Yerel", 48),
        "kanal 13": ("Yerel", 49),
        "kanal 15": ("Yerel", 50),
        "kanal 19": ("Yerel", 51),
        "kanal 23": ("Yerel", 52),
        "kanal 26": ("Yerel", 53),
        "kanal 3": ("Yerel", 54),
        "kanal 32": ("Yerel", 55),
        "kanal 33": ("Yerel", 56),
        "kanal 34": ("Yerel", 57),
        "kanal 38": ("Yerel", 58),
        "kanal 53": ("Yerel", 59),
        "kanal 58": ("Yerel", 60),
        "kanal ada": ("Yerel", 61),
        "kanal firat": ("Yerel", 62),
        "kanal g": ("Yerel", 63),
        "kanal plus": ("Yerel", 64),
        "kanal urfa": ("Yerel", 65),
        "kanal v": ("Yerel", 66),
        "kanal z": ("Yerel", 67),
        "kanal s": ("Yerel", 68),
        "karadeniz tv": ("Yerel", 69),
        "karasu tv": ("Yerel", 70),
        "kardelen tv": ("Yerel", 71),
        "kastamonu tv": ("Yerel", 72),
        "kay tv": ("Yerel", 73),
        "kent 64 tv": ("Yerel", 74),
        "kent turk tv": ("Yerel", 75),
        "kocaeli tv": ("Yerel", 76),
        "kon tv": ("Yerel", 77),
        "konya olay tv": ("Yerel", 78),
        "konya un tv": ("Yerel", 79),
        "ktv konya": ("Yerel", 80),
        "krt": ("Yerel", 81),
        "kordon tv": ("Yerel", 82),
        "life tv": ("Yerel", 83),
        "line tv": ("Yerel", 84),
        "malatya pencere tv": ("Yerel", 85),
        "malatya vuslat tv": ("Yerel", 86),
        "mar tv": ("Yerel", 87),
        "medya tv": ("Yerel", 88),
        "mega tv iskenderun": ("Yerel", 89),
        "mercan tv": ("Yerel", 90),
        "merkez tv": ("Yerel", 91),
        "metropol tv": ("Yerel", 92),
        "metro turk tv": ("Yerel", 93),
        "mk tv": ("Yerel", 94),
        "olay turk tv": ("Yerel", 95), "olay tv": ("Yerel", 95),
        "on6 tv": ("Yerel", 96),
        "on medya": ("Yerel", 97),
        "ort tv ordu": ("Yerel", 98),
        "pusula tv tekirdag": ("Yerel", 99),
        "rize turk tv": ("Yerel", 100),
        "ruha tv": ("Yerel", 101),
        "rumeli turk tv": ("Yerel", 102),
        "salihli sonsoz tv": ("Yerel", 103),
        "serhat tv": ("Yerel", 104),
        "sonmez tv": ("Yerel", 105),
        "suduragi tv": ("Yerel", 106),
        "sun rtv": ("Yerel", 107),
        "surmanset haber tv": ("Yerel", 108),
        "tele news": ("Yerel", 109),
        "tokat super tv": ("Yerel", 110),
        "ton tv": ("Yerel", 111),
        "trt kurdi": ("Yerel", 112),
        "turkhaber tv": ("Yerel", 113),
        "tuzla haberleri tv": ("Yerel", 114),
        "tv1 kayseri": ("Yerel", 115),
        "tv 264": ("Yerel", 116),
        "tv 38": ("Yerel", 117),
        "tv 41": ("Yerel", 118),
        "tv 52": ("Yerel", 119),
        "tv den": ("Yerel", 120),
        "tv kayseri": ("Yerel", 121),
        "tv kentim": ("Yerel", 122),
        "urfanatik tv": ("Yerel", 123),
        "van golu tv": ("Yerel", 124),
        "viyana tv": ("Yerel", 125),
        "vrt tv": ("Yerel", 126),
        "world turk": ("Yerel", 127),
        "yagmurlu tv": ("Yerel", 128),
        "yol tv": ("Yerel", 129),
        "tv 5": ("Yerel", 130), "tv5": ("Yerel", 130),
        "tem tv": ("Yerel", 131),
        "erzurum tv": ("Yerel", 132),

        # ─────────────── Kurumlar ───────────────
        "erzurum web tv": ("Kurumlar", 1),
        "esenler sehir ekrani": ("Kurumlar", 2),
        "obb tv": ("Kurumlar", 3),
        "tbb web tv": ("Kurumlar", 4),
        "uu tv": ("Kurumlar", 5),
        "tursab tv": ("Kurumlar", 6),
        "milli piyango cekilis": ("Kurumlar", 7),

        # ─────────────── Kıbrıs ───────────────
        "brt 1": ("Kıbrıs", 1), "brt1": ("Kıbrıs", 1),
        "brt 2": ("Kıbrıs", 2), "brt2": ("Kıbrıs", 2),
        "ada tv": ("Kıbrıs", 3),
        "genc tv": ("Kıbrıs", 4),
        "kanal t": ("Kıbrıs", 5),
        "kibris tv": ("Kıbrıs", 6),
        "kuzey kibris tv": ("Kıbrıs", 7),
        "kanal sim": ("Kıbrıs", 8),
        "tv 2020": ("Kıbrıs", 9),
        "torba tv": ("Kıbrıs", 10),
        "okku tv": ("Kıbrıs", 11),
        "intisad tv": ("Kıbrıs", 12),

        # ─────────────── Müzik - Diğer ───────────────
        "arabesk tv": ("Müzik - Diğer", 1),
        "arma tv": ("Müzik - Diğer", 2),
        "aviva": ("Müzik - Diğer", 3),
        "damar tv": ("Müzik - Diğer", 4),
        "dost web tv": ("Müzik - Diğer", 5),
        "ezo tv": ("Müzik - Diğer", 6),
        "genc sms tv": ("Müzik - Diğer", 7),
        "guclu tv": ("Müzik - Diğer", 8),
        "rosa tv": ("Müzik - Diğer", 9),
        "sila tv": ("Müzik - Diğer", 10),
        "top pop tv": ("Müzik - Diğer", 11),
        "finest tv": ("Müzik - Diğer", 12),
        "fora muzik": ("Müzik - Diğer", 13),
        "slow karadeniz tv": ("Müzik - Diğer", 14),
        "yansima muzik tv": ("Müzik - Diğer", 15),

        # ─────────────── 7/24 Dizi ───────────────
        "siyah beyaz ask": ("7/24 Dizi", 1),
        "tatli intikam": ("7/24 Dizi", 2),
        "zalim istanbul": ("7/24 Dizi", 3),
    }

    try:
        print("📡 CanakTV kaynağından indiriliyor...")

        BASE_URL = "https://www.canaktv.net"
        CATEGORIES = ["genel", "haber", "spor", "yerel", "cocuk", "dini", "muzik", "belgesel"]

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": BASE_URL + "/"
        })

        # ── Yardımcı fonksiyonlar ────────────────────────────────────
        def normalize(name):
            """Türkçe karakterleri dönüştür, küçük harfe çevir, boşlukları sadeleştir"""
            name = name.strip()
            tr_map = {
                'Ç': 'c', 'ç': 'c', 'Ğ': 'g', 'ğ': 'g',
                'I': 'i', 'İ': 'i', 'ı': 'i',
                'Ö': 'o', 'ö': 'o', 'Ş': 's', 'ş': 's',
                'Ü': 'u', 'ü': 'u'
            }
            for tr_char, en_char in tr_map.items():
                name = name.replace(tr_char, en_char)
            name = name.lower()
            return re.sub(r'\s+', ' ', name).strip()

        def get_channel_info(channel_name, canaktv_category):
            """Kanal adından (grup, sıra) döndürür"""
            norm = normalize(channel_name)

            # 1) Tam eşleşme
            if norm in CHANNEL_MAP:
                return CHANNEL_MAP[norm]

            # 2) Kısmi eşleşme — en uzun anahtar kazanır
            best_match = None
            best_len = 0
            for key, info in CHANNEL_MAP.items():
                if len(key) < 3:
                    continue                       # çok kısa anahtarlarda yanlış eşleşme riski
                if key in norm or norm in key:
                    if len(key) > best_len:
                        best_match = info
                        best_len = len(key)
            if best_match:
                return best_match

            # 3) Varsayılan: CanakTV kategorisinden
            default_group = CATEGORY_TO_GROUP.get(canaktv_category, "Diğer")
            return (default_group, 9999)

        def extract_stream_url(html_text):
            # m3u8 dene
            for pattern in [
                r'''playerSourceM3U\s*=\s*["'](.*?\.m3u8[^"']*?)["']''',
                r'''playerSourceMPD\s*=\s*["'](.*?\.m3u8[^"']*?)["']''',
                r'''playerSourceWEB\s*=\s*["'](.*?\.m3u8[^"']*?)["']''',
                r'''(?:file|source|src|url)\s*[:=]\s*["'](https?:\\?/\\?/[^"']*?\.m3u8[^"']*?)["']''',
            ]:
                m = re.search(pattern, html_text, re.IGNORECASE)
                if m:
                    url = m.group(1).replace("\\/", "/")
                    return ("https:" + url) if url.startswith("//") else url, "m3u8"

            # Genel m3u8 regex
            hits = re.findall(r"""(?:https?:|)//[^\s'"<>\)\\]+\.m3u8[^\s'"<>\)\\]*""", html_text)
            if hits:
                url = hits[0]
                return ("https:" + url) if url.startswith("//") else url, "m3u8"

            # YouTube dene
            for yt_pattern in [
                r'''youtube\.com/embed/([a-zA-Z0-9_-]{11})''',
                r'''youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})''',
                r'''youtu\.be/([a-zA-Z0-9_-]{11})''',
            ]:
                m = re.search(yt_pattern, html_text)
                if m:
                    url = f"https://www.youtube.com/watch?v={m.group(1)}"
                    url = youtube_to_m3u8(url)
                    print(url)
                    return url, "youtube"

            return None, None

        # ── Kategorileri tara ────────────────────────────────────────
        all_entries = []
        seen_paths = set()
        m3u8_count = 0
        youtube_count = 0

        for category in CATEGORIES:
            payload = {"ara": "", "country": "", "category": category}

            try:
                resp = session.post(f"{BASE_URL}/actions/get-channels.php",
                                    data=payload, timeout=15)
                soup = BeautifulSoup(resp.text, "html.parser")
            except:
                continue

            for a in soup.find_all("a", href=re.compile(r"^/watch/")):
                path = a["href"]
                if path in seen_paths:
                    continue
                seen_paths.add(path)

                name_span = a.find("span", class_="tv-name")
                name = (name_span.get_text(strip=True) if name_span
                        else a.get("title", path.split("/")[-1])
                              .replace(" canlı izle", ""))

                try:
                    r = session.get(BASE_URL + path, timeout=15)
                    stream_url, stream_type = extract_stream_url(r.text)

                    if stream_url:
                        group, position = get_channel_info(name, category)
                        all_entries.append({
                            "name": name,
                            "url": stream_url,
                            "group": group,
                            "position": position,
                            "type": stream_type
                        })
                        if stream_type == "youtube":
                            youtube_count += 1
                        else:
                            m3u8_count += 1
                        print(f"  ✓ {name}  →  {group}")
                except:
                    pass

                time.sleep(0.3)

        if not all_entries:
            print("❌ CanakTV: Hiç kanal bulunamadı!")
            return False

        # ── Sıralama: Grup sırası → Grup-içi sıra → Kanal adı ───────
        all_entries.sort(key=lambda x: (
            GROUP_ORDER.index(x["group"]) if x["group"] in GROUP_ORDER else len(GROUP_ORDER),
            x["position"],
            x["name"]
        ))

        # ── M3U dosyası oluştur ──────────────────────────────────────
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 OUTPUT_FILENAME)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n")
            for entry in all_entries:
                f.write(
                    f'#EXTINF:-1 group-title="{entry["group"]}",{entry["name"]}\n'
                    f'{entry["url"]}\n'
                )

        print(f"\n✅ CanakTV: {len(all_entries)} kanal "
              f"({m3u8_count} m3u8, {youtube_count} YouTube)")
        print(f"   📁 {OUTPUT_FILENAME} dosyasına yazıldı!")

        # ── Grup bazlı özet ──────────────────────────────────────────
        from collections import Counter
        grp_counts = Counter(e["group"] for e in all_entries)
        print("\n   📊 Grup dağılımı:")
        for g in GROUP_ORDER:
            if g in grp_counts:
                print(f"      {g}: {grp_counts[g]}")

        return True

    except Exception as e:
        print(f"❌ CanakTV hatası: {e}")
        return False


def youtube_to_m3u8(youtube_url):
    """YouTube URL'sini doğrudan m3u8 linkine çevirir - GitHub Actions uyumlu"""
    import subprocess
    import os
    
    # GitHub Actions için cache dizini
    cache_dir = os.environ.get('RUNNER_TEMP', '/tmp') + '/yt-dlp-cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    # Retry mekanizması
    for attempt in range(3):
        try:
            result = subprocess.run(
                [
                    'yt-dlp',
                    '--no-warnings',
                    '--no-check-certificate',
                    '--no-playlist',
                    '-f', 'best',
                    '-g',
                    '--cache-dir', cache_dir,
                    youtube_url
                ],
                capture_output=True,
                text=True,
                timeout=45
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            # Rate limit kontrolü
            if "429" in result.stderr or "Too Many Requests" in result.stderr:
                import time
                time.sleep((attempt + 1) * 5)
                continue
                
        except subprocess.TimeoutExpired:
            if attempt < 2:
                continue
        except Exception as e:
            print(f"⚠️ Hata: {e}")
            if attempt < 2:
                continue
    
    return None
    
# =============================================================================
# ANA FONKSİYON
# =============================================================================
def main():
    """Belirlenen sıraya göre kaynakları dener"""
    
    sources = {
        "kablo": get_kablo_m3u,
        "smart": get_smart_m3u,
        "boncuktv": get_boncuktv_m3u,
        "goldvod": get_goldvod_m3u,
        "uzun": get_uzun_m3u,
        "canak": get_canak_m3u,
        "legal": get_legal_m3u
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
