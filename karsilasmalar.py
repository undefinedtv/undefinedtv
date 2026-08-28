import requests
import re
import sys

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'tr-TR,tr;q=0.8',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    'Referer': 'https://url24.link/'
}

# Spor dallarına göre logo URL'leri
LOGO_MAP = {
    'futbol': 'https://www.citypng.com/public/uploads/preview/classic-football-ball-icon-701751694971327nyrhdxj8hy.png',
    'basketbol': 'https://www.citypng.com/public/uploads/preview/hd-realistic-basketball-ball-png-704081694878791vsyyyp96la.png',
    'voleybol': 'https://www.citypng.com/public/uploads/preview/hd-yellow-blue-and-white-volleyball-ball-png-70408169487874060mrdnzifk.png',
    'tenis': 'https://www.citypng.com/public/uploads/preview/hd-green-tennis-ball-transparent-png-704081694878789ibeew9de6z.png'
}

CHANNEL_ID_MAP = {
    "androstreamlivebirazb2": "androstreamlivebs2",
    "androstreamlivebirazb3": "androstreamlivebs3",
    "androstreamlivebirazb4": "androstreamlivebs4",
    "androstreamlivebirazb5": "androstreamlivebs5",
    "androstreamlivebirazbsm1": "androstreamlivebsm1",
    "androstreamlivebirazbsm2": "androstreamlivebsm2",
    "androstreamlivebirazss1": "androstreamlivess1",
    "androstreamlivebirazss2": "androstreamlivess2",
    "androstreamlivebirazts": "androstreamlivets",
    "androstreamlivebirazts1": "androstreamlivets1",
    "androstreamlivebirazts2": "androstreamlivets2",
    "androstreamlivebirazts3": "androstreamlivets3",
    "androstreamlivebirazts4": "androstreamlivets4",
    "androstreamlivebirazsm1": "androstreamlivesm1",
    "androstreamlivebirazsm2": "androstreamlivesm2",
    "androstreamlivebiraztrt1": "androstreamlivetrt1",
    "androstreamlivebiraztrtspor": "androstreamlivetrts",
    "androstreamlivebiraztv8": "androstreamlivetv8"
}

def get_active_domain():
    """Aktif domain'i bulur."""
    print("🔍 Aktif domain aranıyor...")
    for i in range(43, 45):
        url = f"https://birazcikspor44.xyz/"
        try:
            r = requests.get(url, timeout=5, headers=headers)
            if r.status_code == 200:
                print(f"✅ Aktif domain bulundu: {url}")
                return url
        except:
            continue
    print("⚠️ Aktif domain bulunamadı.")
    return None

def get_sport_from_league(league):
    """Lig adından spor dalını tahmin eder."""
    league_lower = league.lower()
    if any(k in league_lower for k in ['fiba', 'basketbol', 'nba', 'basket']):
        return 'basketbol'
    elif any(k in league_lower for k in ['voleybol', 'volley', 'voley']):
        return 'voleybol'
    elif any(k in league_lower for k in ['atp', 'wta', 'tenis', 'tenn']):
        return 'tenis'
    else:
        return 'futbol'  # Varsayılan olarak futbol

def get_karsilasmalar(active_domain):
    """
    script.js içindeki 'karsilasmalar' dizisini parse eder.
    Her maça 'sport' alanı eklenir.
    """
    print("📥 script.js indiriliyor...")
    try:
        r = requests.get(active_domain + "script.js", timeout=10, headers=headers)
        r.encoding = 'utf-8'  # Türkçe karakterlerin düzgün gelmesi için
        js_content = r.text
    except Exception as e:
        print(f"❌ script.js alınamadı: {e}")
        return []

    # karsilasmalar dizisini yakala
    pattern = r'const\s+karsilasmalar\s*=\s*\[(.*?)\];'
    m = re.search(pattern, js_content, re.DOTALL)
    if not m:
        print("⚠️ karsilasmalar dizisi bulunamadı.")
        return []

    content = m.group(1)
    objects = re.findall(r'\{.*?\}', content, re.DOTALL)

    matches = []
    for obj in objects:
        def get_field(field):
            f = re.search(rf'"{field}"\s*:\s*"([^"]*)"', obj)
            return f.group(1) if f else ""

        def get_bool(field):
            f = re.search(rf'"{field}"\s*:\s*(true|false)', obj)
            return True if f and f.group(1) == "true" else False

        time = get_field("time")
        league = get_field("league")
        title = get_field("title")
        url = get_field("url")
        live = get_bool("live")

        if url:
            matches.append({
                "time": time,
                "league": league,
                "title": title,
                "url": url,
                "live": live,
                "sport": get_sport_from_league(league)  # Spor dalını tahmin et
            })

    print(f"✅ {len(matches)} maç bulundu (karsilasmalar).")
    return matches

def get_base_url(active_domain, first_match):
    """İlk maçın event.html sayfasından base_url'i çıkarır."""
    print("🔗 Base URL alınıyor...")
    try:
        match_url = first_match.get("url", "")
        if "id=" not in match_url:
            print("⚠️ Maç url'sinde id parametresi yok.")
            return None
        first_id = match_url.split("id=")[1]

        event_url = active_domain + "event.html?id=" + first_id
        r = requests.get(event_url, timeout=10, headers=headers)
        r.encoding = 'utf-8'
        event_source = r.text

        b = re.search(r'const\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
        if not b:
            print("⚠️ Base URL bulunamadı.")
            return None

        base_url = b.group(1)
        if not base_url.endswith('/'):
            base_url += '/'
        print(f"✅ Base URL bulundu: {base_url}")
        return base_url
    except Exception as e:
        print(f"❌ Base URL alınırken hata: {e}")
        return None

def create_m3u(matches, base_url):
    """Maç listesinden M3U dosyası oluşturur."""
    print("📝 M3U dosyası oluşturuluyor...")
    lines = [""]

    for match in matches:
        time = match.get("time", "")
        league = match.get("league", "")
        title = match.get("title", "")
        url = match.get("url", "")
        sport = match.get("sport", "futbol")

        if "id=" not in url:
            continue

        match_id = url.split("id=")[1]
        match_id = CHANNEL_ID_MAP.get(match_id, match_id)
        
        # Başlık: saat | takım1 - takım2 | lig
        display_title = f"{time} | {title} | {league}"

        # Spor dalına göre logo seç
        logo = LOGO_MAP.get(sport, "")

        # EXTINF satırını oluştur
        extinf = f'#EXTINF:-1 '
        if logo:
            extinf += f' tvg-logo="{logo}"'
        extinf += f' group-title="Maç Yayınları",{display_title}'

        lines.append(extinf)
        lines.append(f'#EXTVLCOPT:http-user-agent={headers["User-Agent"]}')
        lines.append(f'{base_url}{match_id}.m3u8')

    with open("karsilasmalar.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ karsilasmalar.m3u başarıyla oluşturuldu ({len(matches)} maç)")

def create_empty_m3u():
    """Hata durumunda boş/placeholder M3U dosyası oluşturur."""
    try:
        with open("karsilasmalar.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("# Maç listesi şu anda kullanılamıyor\n")
        print("✅ Placeholder M3U dosyası oluşturuldu")
    except Exception as e:
        print(f"❌ M3U dosyası oluşturulamadı: {e}")

def main():
    try:
        active_domain = get_active_domain()
        if not active_domain:
            create_empty_m3u()
            return 1

        # Sadece karsilasmalar dizisini kullan
        matches = get_karsilasmalar(active_domain)
        if not matches:
            print("⚠️ Maç listesi alınamadı, placeholder oluşturuluyor...")
            create_empty_m3u()
            return 1

        base_url = get_base_url(active_domain, matches[0])
        if not base_url:
            print("⚠️ Base URL alınamadı, placeholder oluşturuluyor...")
            create_empty_m3u()
            return 1

        create_m3u(matches, base_url)
        return 0

    except Exception as e:
        print(f"❌ Beklenmeyen hata: {str(e)}")
        create_empty_m3u()
        return 1

if __name__ == "__main__":
    sys.exit(main())
