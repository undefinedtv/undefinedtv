import requests
import re
from bs4 import BeautifulSoup

# ─────────────────────────────────────────────
#  AtomSporTV  –  Canlı Maç + TV Kanalları M3U
# ─────────────────────────────────────────────
START_URL    = "https://url24.link/AtomSporTV"
MATCHES_URL  = "https://teletv3.top/load/matches.php"
LOGO_BASE    = "https://im.mackolik.com/img/logo/buyuk"
OUTPUT_FILE  = "atom.m3u"

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'tr-TR,tr;q=0.8',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://url24.link/'
}

TV_CHANNELS = [
        ("bein-sports-1",     "BEIN SPORTS 1"),
        ("bein-sports-2",     "BEIN SPORTS 2"),
        ("bein-sports-3",     "BEIN SPORTS 3"),
        ("bein-sports-4",     "BEIN SPORTS 4"),
        ("bein-sports-5",     "BEIN SPORTS 5"),
        ("bein-sports-max-1", "BEIN SPORTS MAX 1"),
        ("bein-sports-max-2", "BEIN SPORTS MAX 2"),
        ("s-sport",           "S SPORT"),
        ("s-sport-2",         "S SPORT 2"),
        ("tivibu-spor-1",     "TİVİBU SPOR 1"),
        ("tivibu-spor-2",     "TİVİBU SPOR 2"),
        ("tivibu-spor-3",     "TİVİBU SPOR 3"),
        ("trt-spor",          "TRT SPOR"),
        ("trt-yildiz",        "TRT YILDIZ"),
        ("trt-1",              "TRT 1"),
        ("a-spor",             "ASPOR"),
]

def get_base_domain():
    try:
        r1 = requests.get(START_URL, headers=headers, allow_redirects=False, timeout=10)
        if 'location' in r1.headers:
            r2 = requests.get(r1.headers['location'], headers=headers, allow_redirects=False, timeout=10)
            if 'location' in r2.headers:
                domain = r2.headers['location'].strip().rstrip('/')
                return domain
    except Exception:
        pass
    return "https://atomsportv492.top"

def normalize_logo(src):
    if not src: return ""
    if src.startswith("http"): return src
    if src.startswith("//"): return "https:" + src
    return LOGO_BASE + "/" + src.lstrip("/")

def get_matches():
    print(f"Maçlar çekiliyor → {MATCHES_URL}")
    try:
        resp = requests.get(MATCHES_URL, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        matches = []
        skip_words = {'futbol', 'futbol tr', 'futboi', 'günün maçı'}

        for a in soup.find_all('a', href=True):
            href = a['href']
            mid = re.search(r'matches\?id=([a-f0-9]+)', href)
            if not mid: continue
            match_id = mid.group(1)

            imgs = a.find_all('img')
            home_logo = normalize_logo(imgs[0]['src']) if len(imgs) >= 1 else ""
            away_logo = normalize_logo(imgs[1]['src']) if len(imgs) >= 2 else ""
            
            lines = [l.strip() for l in a.get_text('\n').splitlines() if l.strip() and l.strip().lower() not in skip_words]
            saat, lig, home_team, away_team = '', '', '', ''
            for line in lines:
                if '|' in line and not saat:
                    parts = line.split('|', 1)
                    saat, lig = parts[0].strip(), parts[1].strip()
                elif saat and not home_team: home_team = line
                elif saat and home_team and not away_team: away_team = line

            matches.append({
                'id': match_id,
                'home': home_team or "Ev Sahibi",
                'away': away_team or "Deplasman",
                'home_logo': home_logo,
                'away_logo': away_logo,
                'logo': home_logo or away_logo,
                'time': saat,
                'league': lig or "Diğer Maçlar"
            })
        return matches
    except Exception as e:
        print(f"Hata: {e}")
        return []

def get_stream_from_id(video_id):
    """Sadece ID döndüğünde streamsport365'ten gerçek URL'i çek."""
    try:
        resp = requests.post(
            "https://streamsport365.com/cinema",
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'Origin': {base_domain},
                'Referer': {base_domain},
            },
            json={
                "AppId": "5000",
                "AppVer": "1",
                "VpcVer": "1.0.12",
                "Language": "en",
                "Token": "",
                "VideoId": str(video_id)
            },
            timeout=10
        )
        data = resp.json()
        url = data.get("URL", "").replace('\\/', '/')
        return url if url else None
    except Exception as e:
        print(f"  [DEBUG] streamsport365 hatası: {e}")
        return None

def get_m3u8(resource_id, base_domain):
    try:
        h = headers.copy()
        h['Referer'] = f"{base_domain}/"
        resp = requests.get(f"{base_domain}/matches?id={resource_id}", headers=h, timeout=10)
        fetch_m = re.search(r'fetch\(\s*["\']([^"\']+)["\']', resp.text)
        if not fetch_m: return None

        fetch_url = fetch_m.group(1).strip()
        if not fetch_url.endswith(resource_id): fetch_url += resource_id

        h['Origin'] = base_domain
        resp2 = requests.get(fetch_url, headers=h, timeout=10)
        data = resp2.text

        for pat in [r'"deismackanal":"(.*?)"', r'"stream":\s*"(.*?)"', r'"url":\s*"(.*?\.m3u8[^"]*)"', r'(https?://[^\s"\']+\.m3u8[^\s"\']*)']:
            mm = re.search(pat, data)
            if mm:
                result = mm.group(1).replace('\\/', '/').replace('\\', '')
                # Sadece ID döndüyse (http içermiyorsa) ikinci API'ye sor
                if result and not result.startswith('http'):
                    result = get_stream_from_id(result)
                return result
        return None
    except Exception as e:
        print(f"  [DEBUG] Exception: {e}")
        return None

def build_m3u(working_matches, working_channels, base_domain):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        # ── CANLI MAÇLAR (Yeni Format)
        for m in working_matches:
            display_name = f"{m['home']} - {m['away']} [{m['time']}]"
            group_title = f"CANLI MAÇLAR - {m['league']}"
            
            f.write(f'#EXTINF:-1 group-title="Atom TV",{display_name}\n')
            f.write(f'#EXTVLCOPT:http-user-agent={headers["User-Agent"]}\n')
            f.write(f'#EXTVLCOPT:http-referrer={base_domain}/\n')
            f.write(f"{m['url']}\n")
            f.write(f"# İki logo: {m['home_logo']} | {m['away_logo']}\n\n")

        # ── TV KANALLARI
        for ch in working_channels:
            f.write(f'#EXTINF:-1 group-title="Atom TV",{ch["name"]}\n')
            f.write(f'#EXTVLCOPT:http-user-agent={headers["User-Agent"]}\n')
            f.write(f'#EXTVLCOPT:http-referrer={base_domain}/\n')
            f.write(f"{ch['url']}\n\n")

    print(f"\n{GREEN}[✓] {OUTPUT_FILE} başarıyla oluşturuldu.{RESET}")

def main():
    print(f"\n{GREEN}AtomSporTV M3U Oluşturucu Başlatıldı...{RESET}")
    base_domain = get_base_domain()
    print(f"Ana Domain: {base_domain}")
    
    matches = get_matches()
    working_matches = []
    print(f"\n{YELLOW}Maçlar test ediliyor...{RESET}")
    for m in matches:
        url = get_m3u8(m['id'], base_domain)
        if url:
            m['url'] = url
            working_matches.append(m)
            print(f"  ✓ {m['home']} vs {m['away']}")
        else:
            print(f"  ✗ {m['home']} vs {m['away']}")

    tv_items = []
    print(f"\n{YELLOW}Kanallar test ediliyor...{RESET}")
    for cid, name in TV_CHANNELS:
        url = get_m3u8(cid, base_domain)
        if url:
            tv_items.append({'name': name, 'url': url})
            print(f"  ✓ {name}")

    build_m3u(working_matches, tv_items, base_domain)

if __name__ == "__main__":
    main()
