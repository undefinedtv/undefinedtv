import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

CHANNELS = [
    {"id": "bein1", "source_id": "selcukbeinsports1", "name": "BeIN Sports 1 A", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "Selcuk TV"},
    {"id": "bein1", "source_id": "selcukobs1", "name": "BeIN Sports 1 B", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "Selcuk TV"},
    {"id": "bein2", "source_id": "selcukbeinsports2", "name": "BeIN Sports 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/7uv6x71628799003.png", "group": "Selcuk TV"},
    {"id": "bein3", "source_id": "selcukbeinsports3", "name": "BeIN Sports 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/u3117i1628798857.png", "group": "Selcuk TV"},
    {"id": "bein4", "source_id": "selcukbeinsports4", "name": "BeIN Sports 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/2ktmcp1628798841.png", "group": "Selcuk TV"},
    {"id": "bein5", "source_id": "selcukbeinsports5", "name": "BeIN Sports 5", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/BeIn_Sports_5_US.png", "group": "Selcuk TV"},
    {"id": "beinmax1", "source_id": "selcukbeinsportsmax1", "name": "BeIN Sports Max 1", "logo": "https://assets.bein.com/mena/sites/3/2015/06/beIN_SPORTS_MAX1_DIGITAL_Mono.png", "group": "Selcuk TV"},
    {"id": "beinmax2", "source_id": "selcukbeinsportsmax2", "name": "BeIN Sports Max 2", "logo": "http://tvprofil.com/img/kanali-logo/beIN_Sports_MAX_2_TR_logo_v2.png?1734011568", "group": "Selcuk TV"},
    {"id": "ssport1", "source_id": "selcukssport", "name": "S Sport 1", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923239.png", "group": "Selcuk TV"},
    {"id": "ssport2", "source_id": "selcukssport2", "name": "S Sport 2", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923321.png", "group": "Selcuk TV"},
    {"id": "ssport", "source_id": "sssplus1", "name": "S Sport PLUS 1", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923321.png", "group": "Selcuk TV"},
    {"id": "ssport", "source_id": "sssplus2", "name": "S Sport PLUS 2", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923321.png", "group": "Selcuk TV"},
    {"id": "tivibu1", "source_id": "selcuktivibuspor1", "name": "Tivibu Spor 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/qadnsi1642604437.png", "group": "Selcuk TV"},
    {"id": "tivibu2", "source_id": "selcuktivibuspor2", "name": "Tivibu Spor 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/kuasdm1642604455.png", "group": "Selcuk TV"},
    {"id": "tivibu3", "source_id": "selcuktivibuspor3", "name": "Tivibu Spor 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/slwrz41642604502.png", "group": "Selcuk TV"},
    {"id": "tivibu4", "source_id": "selcuktivibuspor4", "name": "Tivibu Spor 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/59bqi81642604517.png", "group": "Selcuk TV"},
    {"id": "smart1", "source_id": "selcuksmartspor", "name": "Smart Spor 1", "logo": "https://dsmart-static-v2.ercdn.net//resize-width/1920/content/p/el/11909/Thumbnail.png", "group": "Selcuk TV"},
    {"id": "smart2", "source_id": "selcuksmartspor2", "name": "Smart Spor 2", "logo": "https://www.dsmart.com.tr/api/v1/public/images/kanallar/SPORSMART2-gri.png", "group": "Selcuk TV"},
    {"id": "eurosport1", "source_id": "seurosport1", "name": "Eurosport 1", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/54cad412-5f3a-4184-b5fc-d567a5de7160.png", "group": "Selcuk TV"},
    {"id": "eurosport2", "source_id": "seurosport2", "name": "Eurosport 2", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/a4cbdd15-1509-408f-a108-65b8f88f2066.png", "group": "Selcuk TV"},
]

def find_working_domain(start=6, end=100):
    print("sporcafe domainleri taranıyor")
    for i in range(start, end + 1):
        url = f"https://www.sporcafe{i}.xyz/"
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200 and "uxsyplayer" in res.text:
                print(f"Aktif domain: {url}")
                return res.text, url
        except:
            continue
    print(" Aktif domain bulunamadı.")
    return None, None

def find_stream_domain(html):
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', html)
    return f"https://{match.group(1)}" if match else None

def extract_base_url(html):
    match = re.search(r'this\.adsBaseUrl\s*=\s*[\'"]([^\'"]+)', html)
    return match.group(1) if match else None

def fetch_streams(domain, referer):
    result = []
    for ch in CHANNELS:
        full_url = f"{domain}/index.php?id={ch['source_id']}"
        try:
            r = requests.get(full_url, headers={**HEADERS, "Referer": referer}, timeout=5)
            if r.status_code == 200:
                base = extract_base_url(r.text)
                if base:
                    stream = f"{base}{ch['source_id']}/playlist.m3u8"
                    print(f" {ch['name']} → {stream}")
                    result.append((ch, stream))
        except:
            pass
    return result

def write_m3u(links, filename="selcuk.m3u", referer=""):
    print(f"\n M3U dosyası yazılıyor: {filename}")
    lines = [""]
    for ch, url in links:
        lines.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}')
        lines.append(f"#EXTVLCOPT:http-referrer={referer}")
        lines.append(url)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(" Tamamlandı. Kanal sayısı:", len(links))

def main():
    html, referer = find_working_domain()
    if not html:
        return
    stream_domain = find_stream_domain(html)
    if not stream_domain:
        print(" Yayın domaini bulunamadı.")
        return
    print(f"Yayın domaini: {stream_domain}")
    streams = fetch_streams(stream_domain, referer)
    if streams:
        write_m3u(streams, referer=referer)
    else:
        print("Hiçbir yayın alınamadı.")

if __name__ == "__main__":
    main()
