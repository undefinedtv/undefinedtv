import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

# --- AYARLAR ---
OUTPUT_FILE = "vavoo.m3u"
MAX_WORKERS = 10  # Hız için aynı anda taranacak grup sayısı

# --- 1. SIRALAMA MANTIĞI (İstediğiniz kod bloğu) ---
def sort_key(tvg_name):
    """Sıralama önceliği belirleme: Bein Spor -> Diğer Spor -> Genel"""
    tvg_name_lower = tvg_name.lower()
    is_bein_spor = "bein" in tvg_name_lower and "spor" in tvg_name_lower
    is_spor = "spor" in tvg_name_lower or "sport" in tvg_name_lower
    
    if is_bein_spor:
        group_priority = 0
    elif is_spor:
        group_priority = 1
    else:
        group_priority = 2
    
    return (group_priority, tvg_name_lower)

# --- 2. VAVOO API İMZALARI (utils.py mantığı) ---
def get_auth_signature():
    """Katalog erişimi için gerekli imzayı alır."""
    headers = {
        "user-agent": "okhttp/4.11.0",
        "accept": "application/json",
        "content-type": "application/json; charset=utf-8",
        "accept-encoding": "gzip"
    }
    payload = {
        "token": "tosFwQCJMS8qrW_AjLoHPQ41646J5dRNha6ZWHnijoYQQQoADQoXYSo7ki7O5-CsgN4CH0uRk6EEoJ0728ar9scCRQW3ZkbfrPfeCXW2VgopSW2FWDqPOoVYIuVPAOnXCZ5g",
        "reason": "app-blur",
        "locale": "de",
        "theme": "dark",
        "metadata": {"device": {"type": "Handset", "brand": "google", "model": "Nexus", "name": "21081111RG", "uniqueId": "d10e5d99ab665233"}, "os": {"name": "android", "version": "7.1.2", "abis": ["arm64-v8a", "armeabi-v7a", "armeabi"], "host": "android"}, "app": {"platform": "android", "version": "3.1.20", "buildId": "289515000", "engine": "hbc85", "signatures": ["6e8a975e3cbf07d5de823a760d4c2547f86c1403105020adee5de67ac510999e"], "installer": "app.revanced.manager.flutter"}, "version": {"package": "tv.vavoo.app", "binary": "3.1.20", "js": "3.1.20"}},
        "appFocusTime": 0, "playerActive": False, "playDuration": 0, "devMode": False, "hasAddon": True, "castConnected": False, "package": "tv.vavoo.app", "version": "3.1.20", "process": "app", "firstAppStart": 1743962904623, "lastAppStart": 1743962904623, "ipLocation": "", "adblockEnabled": True, "proxy": {"supported": ["ss", "openvpn"], "engine": "ss", "ssVersion": 1, "enabled": True, "autoServer": True, "id": "pl-waw"}, "iap": {"supported": False}
    }
    try:
        response = requests.post('https://www.vavoo.tv/api/app/ping', json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("addonSig")
    except Exception as e:
        print(f"HATA: Auth Signature alınamadı: {e}")
        return None

def get_ts_signature():
    """Stream linklerinin sonuna eklenen yetki imzasını alır."""
    vec = {"vec": "9frjpxPjxSNilxJPCJ0XGYs6scej3dW/h/VWlnKUiLSG8IP7mfyDU7NirOlld+VtCKGj03XjetfliDMhIev7wcARo+YTU8KPFuVQP9E2DVXzY2BFo1NhE6qEmPfNDnm74eyl/7iFJ0EETm6XbYyz8IKBkAqPN/Spp3PZ2ulKg3QBSDxcVN4R5zRn7OsgLJ2CNTuWkd/h451lDCp+TtTuvnAEhcQckdsydFhTZCK5IiWrrTIC/d4qDXEd+GtOP4hPdoIuCaNzYfX3lLCwFENC6RZoTBYLrcKVVgbqyQZ7DnLqfLqvf3z0FVUWx9H21liGFpByzdnoxyFkue3NzrFtkRL37xkx9ITucepSYKzUVEfyBh+/3mtzKY26VIRkJFkpf8KVcCRNrTRQn47Wuq4gC7sSwT7eHCAydKSACcUMMdpPSvbvfOmIqeBNA83osX8FPFYUMZsjvYNEE3arbFiGsQlggBKgg1V3oN+5ni3Vjc5InHg/xv476LHDFnNdAJx448ph3DoAiJjr2g4ZTNynfSxdzA68qSuJY8UjyzgDjG0RIMv2h7DlQNjkAXv4k1BrPpfOiOqH67yIarNmkPIwrIV+W9TTV/yRyE1LEgOr4DK8uW2AUtHOPA2gn6P5sgFyi68w55MZBPepddfYTQ+E1N6R/hWnMYPt/i0xSUeMPekX47iucfpFBEv9Uh9zdGiEB+0P3LVMP+q+pbBU4o1NkKyY1V8wH1Wilr0a+q87kEnQ1LWYMMBhaP9yFseGSbYwdeLsX9uR1uPaN+u4woO2g8sw9Y5ze5XMgOVpFCZaut02I5k0U4WPyN5adQjG8sAzxsI3KsV04DEVymj224iqg2Lzz53Xz9yEy+7/85ILQpJ6llCyqpHLFyHq/kJxYPhDUF755WaHJEaFRPxUqbparNX+mCE9Xzy7Q/KTgAPiRS41FHXXv+7XSPp4cy9jli0BVnYf13Xsp28OGs/D8Nl3NgEn3/eUcMN80JRdsOrV62fnBVMBNf36+LbISdvsFAFr0xyuPGmlIETcFyxJkrGZnhHAxwzsvZ+Uwf8lffBfZFPRrNv+tgeeLpatVcHLHZGeTgWWml6tIHwWUqv2TVJeMkAEL5PPS4Gtbscau5HM+FEjtGS+KClfX1CNKvgYJl7mLDEf5ZYQv5kHaoQ6RcPaR6vUNn02zpq5/X3EPIgUKF0r/0ctmoT84B2J1BKfCbctdFY9br7JSJ6DvUxyde68jB+Il6qNcQwTFj4cNErk4x719Y42NoAnnQYC2/qfL/gAhJl8TKMvBt3Bno+va8ve8E0z8yEuMLUqe8OXLce6nCa+L5LYK1aBdb60BYbMeWk1qmG6Nk9OnYLhzDyrd9iHDd7X95OM6X5wiMVZRn5ebw4askTTc50xmrg4eic2U1w1JpSEjdH/u/hXrWKSMWAxaj34uQnMuWxPZEXoVxzGyuUbroXRfkhzpqmqqqOcypjsWPdq5BOUGL/Riwjm6yMI0x9kbO8+VoQ6RYfjAbxNriZ1cQ+AW1fqEgnRWXmjt4Z1M0ygUBi8w71bDML1YG6UHeC2cJ2CCCxSrfycKQhpSdI1QIuwd2eyIpd4LgwrMiY3xNWreAF+qobNxvE7ypKTISNrz0iYIhU0aKNlcGwYd0FXIRfKVBzSBe4MRK2pGLDNO6ytoHxvJweZ8h1XG8RWc4aB5gTnB7Tjiqym4b64lRdj1DPHJnzD4aqRixpXhzYzWVDN2kONCR5i2quYbnVFN4sSfLiKeOwKX4JdmzpYixNZXjLkG14seS6KR0Wl8Itp5IMIWFpnNokjRH76RYRZAcx0jP0V5/GfNNTi5QsEU98en0SiXHQGXnROiHpRUDXTl8FmJORjwXc0AjrEMuQ2FDJDmAIlKUSLhjbIiKw3iaqp5TVyXuz0ZMYBhnqhcwqULqtFSuIKpaW8FgF8QJfP2frADf4kKZG1bQ99MrRrb2A="}
    try:
        response = requests.post('https://www.vavoo.tv/api/box/ping2', data=vec)
        response.raise_for_status()
        return response.json()['response'].get('signed')
    except Exception as e:
        print(f"HATA: TS Signature alınamadı: {e}")
        return None

# --- 3. GRUPLAR VE KANALLAR ---
def get_turkey_groups():
    """Vavoo'dan sadece 'Turkey' içeren grupları çeker."""
    try:
        print("Gruplar çekiliyor...")
        response = requests.get("https://www2.vavoo.to/live2/index?output=json")
        data = response.json()
        groups = set()
        for channel in data:
            if "group" in channel:
                # Sadece içinde "Turkey" geçen grupları al (Case insensitive)
                if "turkey" in channel["group"].lower():
                    groups.add(channel["group"])
        return sorted(list(groups))
    except Exception as e:
        print(f"HATA: Gruplar alınamadı: {e}")
        return []

def get_channels_for_group(group, auth_sig, ts_sig):
    """Belirli bir grup için kanalları çeker."""
    print(f" Taranıyor: {group}")
    headers = {
        "user-agent": "okhttp/4.11.0",
        "accept": "application/json",
        "content-type": "application/json; charset=utf-8",
        "mediahubmx-signature": auth_sig
    }
    
    channels = []
    cursor = 0
    
    while cursor is not None:
        try:
            payload = {
                "language": "de", "region": "AT", "catalogId": "iptv", "id": "iptv", "adult": False, "search": "", "sort": "name",
                "filter": {"group": group}, "cursor": cursor, "clientVersion": "3.0.2"
            }
            res = requests.post("https://vavoo.to/mediahubmx-catalog.json", json=payload, headers=headers)
            if res.status_code != 200: break
                
            data = res.json()
            items = data.get("items", [])
            
            for item in items:
                name = item["name"]
                raw_url = item["url"]
                
                # URL oluşturma (vjlive.py mantığı)
                try:
                    modified_base = raw_url.replace("vavoo-iptv", "live2")
                    if len(modified_base) > 12: base_url = modified_base[:-12]
                    else: base_url = modified_base 

                    # Oynatılabilir imzalı link
                    final_url = f"{base_url}.ts?n=1&b=5&vavoo_auth={ts_sig}"
                    
                    channels.append({
                        "name": name,
                        "url": final_url,
                        # Sıralama anahtarı burada hesaplanıp saklanıyor
                        "sort_priority": sort_key(name)
                    })
                except: continue

            cursor = data.get("nextCursor")
        except Exception as e:
            print(f"HATA ({group}): {e}")
            break
            
    return channels

# --- 4. ANA İŞLEM ---
def main():
    print("--- Vavoo Turkey Özelleştirilmiş M3U Oluşturucu ---")
    
    # İmzaları al
    auth_sig = get_auth_signature()
    ts_sig = get_ts_signature()
    
    if not auth_sig or not ts_sig:
        print("İmza alınamadı, çıkılıyor.")
        return

    # Sadece Turkey gruplarını al
    turkey_groups = get_turkey_groups()
    if not turkey_groups:
        print("'Turkey' içeren grup bulunamadı.")
        return

    print(f"'Turkey' içeren {len(turkey_groups)} grup bulundu. Kanallar taranıyor...")

    all_channels = []
    
    # Kanalları çek
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(get_channels_for_group, group, auth_sig, ts_sig) for group in turkey_groups]
        for future in futures:
            result = future.result()
            if result:
                all_channels.extend(result)

    print(f"\nToplam {len(all_channels)} kanal bulundu. Sıralama uygulanıyor...")

    # --- SIRALAMA İŞLEMİ ---
    # sort_priority değerine göre sırala (0: Bein Spor, 1: Diğer Spor, 2: Genel)
    # sort_key fonksiyonu (priority, name) döndürdüğü için önce gruba, sonra isme göre sıralar.
    all_channels.sort(key=lambda x: x['sort_priority'])

    # İstatistikler
    bein_count = sum(1 for c in all_channels if c['sort_priority'][0] == 0)
    spor_count = sum(1 for c in all_channels if c['sort_priority'][0] == 1)
    gen_count = sum(1 for c in all_channels if c['sort_priority'][0] == 2)
    
    print(f"İstatistik: {bein_count} Bein Spor, {spor_count} Diğer Spor, {gen_count} Genel.")

    # --- M3U YAZMA ---
    print(f"M3U dosyası yazılıyor: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in all_channels:
            name = ch["name"].replace(",", " ").strip()
            url = ch["url"]
            
            # İsteğinize göre group-title her zaman "Vavoo TV" olacak
            f.write(f'#EXTINF:-1 group-title="Vavoo TV",{name}\n')
            f.write(f'#EXTVLCOPT:http-user-agent=VAVOO/2.6\n')
            f.write(f"{url}|User-Agent=VAVOO/2.6\n")

    print("İşlem tamamlandı!")

if __name__ == "__main__":
    main()
