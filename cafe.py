import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

CHANNELS = [
        {"id": "sbeinsports-1", "name": "BeIN Sports 1", "tvg_id": "bein1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "BEIN SPORTS"},
        {"id": "sbeinsports-2", "name": "BeIN Sports 2", "tvg_id": "bein2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/7uv6x71628799003.png", "group": "BEIN SPORTS"},
        {"id": "sbeinsports-3", "name": "BeIN Sports 3", "tvg_id": "bein3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/u3117i1628798857.png", "group": "BEIN SPORTS"},
        {"id": "sbeinsports-4", "name": "BeIN Sports 4", "tvg_id": "bein4", "logo": "https://i.postimg.cc/0yjyF10x/bein4.png", "group": "BEIN SPORTS"},
        {"id": "sbeinsports-5", "name": "BeIN Sports 5", "tvg_id": "bein5", "logo": "https://i.postimg.cc/BvjF7hx5/bein5.png", "group": "BEIN SPORTS"},
        {"id": "sssport", "name": "S Sport", "tvg_id": "ssport", "logo": "https://i.postimg.cc/TYcZT4zR/ssport.png", "group": "S SPORT"},
        {"id": "sssport2", "name": "S Sport 2", "tvg_id": "ssport2", "logo": "https://i.postimg.cc/WbftnShM/ssport2.png", "group": "S SPORT"},
        {"id": "sssplus1", "name": "S Sport Plus 1", "tvg_id": "ssportplus", "logo": "https://i.postimg.cc/rmK04Jxr/ssportplus.png", "group": "S SPORT"},
        {"id": "sssplus2", "name": "S Sport Plus 2", "tvg_id": "ssportplus", "logo": "https://i.postimg.cc/rmK04Jxr/ssportplus.png", "group": "S SPORT"},
        {"id": "stivibuspor-1", "name": "Tivibu Spor 1", "tvg_id": "tivibu1", "logo": "https://i.postimg.cc/G2xMf9Gn/tivibu.png", "group": "TİVİBU"},
        {"id": "stivibuspor-2", "name": "Tivibu Spor 2", "tvg_id": "tivibu2", "logo": "https://i.postimg.cc/G2xMf9Gn/tivibu.png", "group": "TİVİBU"},
        {"id": "stivibuspor-3", "name": "Tivibu Spor 3", "tvg_id": "tivibu3", "logo": "https://i.postimg.cc/G2xMf9Gn/tivibu.png", "group": "TİVİBU"},
        {"id": "stivibuspor-4", "name": "Tivibu Spor 4", "tvg_id": "tivibu4", "logo": "https://i.postimg.cc/G2xMf9Gn/tivibu.png", "group": "TİVİBU"},
        {"id": "ssmartspor", "name": "Smart Spor", "tvg_id": "smartspor", "logo": "https://i.postimg.cc/7YNxxHgM/smartspor.png", "group": "DİĞER"},
        {"id": "ssmartspor2", "name": "Smart Spor 2", "tvg_id": "smartspor2", "logo": "https://i.postimg.cc/7YNxxHgM/smartspor.png", "group": "DİĞER"},
        {"id": "sexxen-1", "name": "Exxen Spor 1", "tvg_id": "exxen1", "logo": "https://i.postimg.cc/B6t4z1d3/exxen.png", "group": "EXXEN"},
        {"id": "sexxen-2", "name": "Exxen Spor 2", "tvg_id": "exxen2", "logo": "https://i.postimg.cc/B6t4z1d3/exxen.png", "group": "EXXEN"},
        {"id": "sexxen-3", "name": "Exxen Spor 3", "tvg_id": "exxen2", "logo": "https://i.postimg.cc/B6t4z1d3/exxen.png", "group": "EXXEN"},
        {"id": "sexxen-4", "name": "Exxen Spor 4", "tvg_id": "exxen2", "logo": "https://i.postimg.cc/B6t4z1d3/exxen.png", "group": "EXXEN"},
        {"id": "sexxen-5", "name": "Exxen Spor 5", "tvg_id": "exxen2", "logo": "https://i.postimg.cc/B6t4z1d3/exxen.png", "group": "EXXEN"},
        {"id": "sexxen-6", "name": "Exxen Spor 6", "tvg_id": "exxen2", "logo": "https://i.postimg.cc/B6t4z1d3/exxen.png", "group": "EXXEN"},
        {"id": "stabiispor-1", "name": "Tabii Spor 1", "tvg_id": "tabii1", "logo": "https://i.postimg.cc/9MpztRQF/tabii.png", "group": "TABII"},
        {"id": "stabiispor-2", "name": "Tabii Spor 2", "tvg_id": "tabii2", "logo": "https://i.postimg.cc/9MpztRQF/tabii.png", "group": "TABII"},
        {"id": "stabiispor-3", "name": "Tabii Spor 3", "tvg_id": "tabii3", "logo": "https://i.postimg.cc/9MpztRQF/tabii.png", "group": "TABII"},
        {"id": "stabiispor-4", "name": "Tabii Spor 4", "tvg_id": "tabii4", "logo": "https://i.postimg.cc/9MpztRQF/tabii.png", "group": "TABII"},
        {"id": "stabiispor-5", "name": "Tabii Spor 5", "tvg_id": "tabii5", "logo": "https://i.postimg.cc/9MpztRQF/tabii.png", "group": "TABII"},
        {"id": "strt1", "name": "TRT 1", "tvg_id": "trt1", "logo": "https://i.postimg.cc/XYJkFyqV/trt1.png", "group": "TRT"},
        {"id": "strtspor", "name": "TRT Spor", "tvg_id": "trtspor", "logo": "https://i.postimg.cc/jjTfdSTL/trtspor.png", "group": "TRT"},
        {"id": "strtspor2", "name": "TRT Spor 2", "tvg_id": "trtspor2", "logo": "https://i.postimg.cc/wvsvstyn/trtspor2.png", "group": "TRT"},
        {"id": "saspor", "name": "A Spor", "tvg_id": "aspor", "logo": "https://i.postimg.cc/gJMK4kTN/aspor.png", "group": "YEREL SPOR"},
        {"id": "stv8", "name": "TV8", "tvg_id": "tv8", "logo": "https://i.postimg.cc/CLpftN9Y/tv8.png", "group": "DİĞER"},
        {"id": "sdazn1", "name": "DAZN 1", "tvg_id": "dazn1", "logo": "https://i.postimg.cc/QMgmHh7x/dazn1.png", "group": "DAZN"},
        {"id": "sdazn2", "name": "DAZN 2", "tvg_id": "dazn2", "logo": "https://i.postimg.cc/XY5YQvSd/dazn2.png", "group": "DAZN"},
        {"id": "sbeinsportshaber", "name": "BeIN Sports Haber", "tvg_id": "beinhd", "logo": "https://i.postimg.cc/x14Fs2kw/beinhd.png", "group": "BEIN SPORTS"},
]

def find_working_domain(start=14, end=100):
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
        full_url = f"{domain}/index.php?id={ch['id']}"
        try:
            r = requests.get(full_url, headers={**HEADERS, "Referer": referer}, timeout=5)
            if r.status_code == 200:
                base = extract_base_url(r.text)
                if base:
                    stream = f"{base}{ch['id']}/playlist.m3u8"
                    print(f" {ch['name']} → {stream}")
                    result.append((ch, stream))
        except:
            pass
    return result

def write_m3u(links, filename="sporcafe.m3u", referer=""):
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
