import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

def find_active_domain(start=1825, end=1880):
    for i in range(start, end+1):
        url = f"https://www.selcuksportshd{i}.xyz/"
        try:
            req = Request(url, headers=headers)
            html = urlopen(req, timeout=5).read().decode()

            if "uxsyplayer" in html:
                print(f"✅ Aktif domain bulundu: {url}")
                return url, html
        except:
            continue
    return None, None

def get_player_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", attrs={"data-url": True}):
        data_url = a["data-url"].strip()

        # relative URL ise düzelt
        if data_url.startswith("/"):
            data_url = "https://" + data_url.lstrip("/")

        name = a.text.strip()
        if not name:
            # fallback
            if "id=" in data_url:
                name = data_url.split("id=")[-1]
            else:
                name = "Kanal"

        links.append({"url": data_url, "name": name})

    return links

def get_m3u8_url(player_url, referer):
    try:
        req = Request(player_url, headers={"User-Agent": headers["User-Agent"], "Referer": referer})
        html = urlopen(req, timeout=10).read().decode()

        # baseStreamUrl bul
        patterns = [
            r'this\.baseStreamUrl\s*=\s*"([^"]+)"',
            r"this\.baseStreamUrl\s*=\s*'([^']+)'",
            r'baseStreamUrl\s*:\s*"([^"]+)"',
            r"baseStreamUrl\s*:\s*'([^']+)'"
        ]

        base_url = None
        for p in patterns:
            m = re.search(p, html)
            if m:
                base_url = m.group(1)
                break

        if not base_url:
            print(f"❌ baseStreamUrl bulunamadı: {player_url}")
            return None

        # ID'yi çek
        m_id = re.search(r"id=([a-zA-Z0-9]+)", player_url)
        if not m_id:
            print(f"❌ stream ID bulunamadı: {player_url}")
            return None

        stream_id = m_id.group(1)

        # sonunda / yoksa ekle
        if not base_url.endswith("/"):
            base_url += "/"

        final_m3u8 = f"{base_url}{stream_id}/playlist.m3u8"
        print(f"🎯 M3U8 bulundu: {final_m3u8}")
        return final_m3u8

    except Exception as e:
        print(f"❌ Player okunamadı: {e}")
        return None

def normalize_tvg_id(name):
    rep = {
        'ç':'c','Ç':'C','ş':'s','Ş':'S','ı':'i','İ':'I','ğ':'g','Ğ':'G',
        'ü':'u','Ü':'U','ö':'o','Ö':'O'
    }
    for k,v in rep.items():
        name = name.replace(k, v)
    name = name.replace(" ", "-").replace(":", "-")
    name = re.sub(r"[^a-zA-Z0-9\-]", "", name)
    return name.lower()

def create_m3u(filename="selcuk.m3u"):
    print("🔍 Domain aranıyor...")
    domain, html = find_active_domain()

    if not html:
        print("❌ Çalışan domain bulunamadı!")
        return

    referer = domain
    players = get_player_links(html)

    if not players:
        print("❌ Player link yok!")
        return

    print(f"📺 {len(players)} kanal bulundu")

    m3u = [""]
    ok = 0

    for ch in players:
        print(f"⏳ İşleniyor: {ch['name']}")

        m3u8 = get_m3u8_url(ch["url"], referer)
        if not m3u8:
            continue

        tvg_id = normalize_tvg_id(ch["name"])

        m3u.append(f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="Spor",{ch["name"]}')
        m3u.append(f"#EXTVLCOPT:http-referrer={referer}")
        m3u.append(f"#EXTVLCOPT:http-user-agent={headers['User-Agent']}")
        m3u.append(m3u8)

        ok += 1

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    print(f"\n✅ M3U oluşturuldu: {filename}")
    print(f"📊 Başarılı: {ok}/{len(players)}")

if __name__ == "__main__":
    create_m3u()
