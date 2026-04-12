import requests
import re
import json

# AtomSporTV
START_URL   = "https://url24.link/AtomSporTV"
OUTPUT_FILE = "atom.m3u"

GREEN = "\033[92m"
RESET = "\033[0m"

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'tr-TR,tr;q=0.8',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    'Referer': 'https://url24.link/'
}

def get_base_domain():
    """Ana domain'i bul"""
    try:
        r = requests.get(START_URL, headers=headers, allow_redirects=False, timeout=10)
        if 'location' in r.headers:
            r2 = requests.get(r.headers['location'], headers=headers, allow_redirects=False, timeout=10)
            if 'location' in r2.headers:
                domain = r2.headers['location'].strip().rstrip('/')
                print(f"Ana Domain: {domain}")
                return domain
    except Exception as e:
        print(f"Domain hatası: {e}")
    return "https://www.atomsportv494.top"

def get_channel_m3u8(channel_id, base_domain):
    """
    1. {base_domain}/matches?id={channel_id} sayfasını çek
    2. Script içindeki fetch URL'lerini dinamik parse et
    3. GET veya POST ile stream URL'sini al
    """
    page_url = f"{base_domain}/matches?id={channel_id}"

    # Sayfayı çek
    try:
        h = headers.copy()
        h['Referer'] = base_domain + "/"
        resp = requests.get(page_url, headers=h, timeout=10)
        html = resp.text
    except Exception:
        return None

    # Tüm <script> bloklarını birleştir
    scripts = "\n".join(re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))

    api_headers = headers.copy()
    api_headers['Origin']  = base_domain
    api_headers['Referer'] = page_url

    # --- Kaynak 1: GET fetch ---
    # fetch("https://teletv3.top/load/yayinlink.php?id=" + encodeURIComponent(KANAL_ID), ...)
    get_match = re.search(r'fetch\(\s*["\']([^"\']+\?id=)["\']', scripts)
    if get_match:
        get_url = get_match.group(1) + channel_id
        try:
            r1 = requests.get(get_url, headers=api_headers, timeout=8)
            if r1.ok:
                data = r1.json()
                stream = data.get("deismackanal") or data.get("URL") or data.get("url") or ""
                if stream and "m3u8" in stream:
                    return re.sub(r'edge\d+', 'edge3', stream)
        except Exception:
            pass

    # --- Kaynak 2: POST fetch ---
    # fetch("https://streamsport365.com/cinema", { method: "POST", body: JSON.stringify({...}) })
    post_match = re.search(
        r'fetch\(\s*["\']([^"\']+)["\'],\s*\{[^}]*method\s*:\s*["\']POST["\']',
        scripts, re.DOTALL
    )
    if post_match:
        post_url    = post_match.group(1)
        post_origin = "/".join(post_url.split("/")[:3])

        # Body alanlarını script'ten topla
        body = {}
        for key in ("AppId", "AppVer", "VpcVer", "Language", "Token"):
            m = re.search(rf'["\']?{key}["\']?\s*:\s*["\']([^"\']*)["\']', scripts)
            if m:
                body[key] = m.group(1)
        body["VideoId"] = channel_id

        try:
            h2 = {
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Origin": post_origin,
                "Referer": post_origin + "/",
                "User-Agent": headers["User-Agent"]
            }
            r2 = requests.post(post_url, headers=h2, data=json.dumps(body), timeout=8)
            if r2.ok:
                data = r2.json()
                stream = data.get("URL") or data.get("url") or data.get("deismackanal") or ""
                if stream and "m3u8" in stream:
                    return re.sub(r'edge\d+', 'edge3', stream)
        except Exception:
            pass

    return None

def get_all_possible_channels():
    tv_channels = [
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
    channels = [{'id': cid, 'name': name, 'group': 'TV Kanalları'} for cid, name in tv_channels]
    print(f"Toplam {len(channels)} TV kanalı listelendi")
    return channels

def create_m3u_direct(channels, base_domain):
    print(f"\nM3U dosyası oluşturuluyor ({len(channels)} kanal)...")
    written = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")
        for i, channel in enumerate(channels):
            channel_id   = channel["id"]
            channel_name = channel["name"]
            print(f"{i+1:2d}. {channel_name}... ", end="", flush=True)

            m3u8_url = get_channel_m3u8(channel_id, base_domain)

            if not m3u8_url:
                m3u8_url = f"{base_domain}/stream/{channel_id}"
                print("(placeholder)")
            else:
                print(f"{GREEN}✓{RESET}")

            f.write(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{channel_name}" group-title="Atom TV",{channel_name}\n')
            f.write(f'#EXTVLCOPT:http-referrer={base_domain}\n')
            f.write(f'#EXTVLCOPT:http-user-agent={headers["User-Agent"]}\n')
            f.write(m3u8_url + "\n")
            written += 1

    print(f"\n{GREEN}[✓] M3U dosyası oluşturuldu: {OUTPUT_FILE}{RESET}")
    print(f"Toplam {written} kanal eklendi.")

def main():
    print(f"{GREEN}AtomSporTV M3U Oluşturucu{RESET}")
    print("=" * 60)

    print("\n1. Ana domain bulunuyor...")
    base_domain = get_base_domain()

    print("\n2. TV kanal listesi hazırlanıyor...")
    channels = get_all_possible_channels()

    print("\n3. M3U dosyası oluşturuluyor...")
    create_m3u_direct(channels, base_domain)

if __name__ == "__main__":
    main()
