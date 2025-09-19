import os
import re
from datetime import datetime
from httpx import Client

# ---------------- Dengetv54Manager ----------------
class Dengetv54Manager:
    def __init__(self):
        self.httpx = Client(timeout=10, verify=False)
        self.base_stream_url = "https://four.zirvestream14.cfd/"
        self.channel_files = {
            1: "yayinzirve.m3u8", 2: "yayin1.m3u8", 3: "yayininat.m3u8", 4: "yayinb2.m3u8",
            5: "yayinb3.m3u8", 6: "yayinb4.m3u8", 7: "yayinb5.m3u8", 8: "yayinbm1.m3u8",
            9: "yayinbm2.m3u8", 10: "yayinss.m3u8", 11: "yayinss2.m3u8", 13: "yayint1.m3u8",
            14: "yayint2.m3u8", 15: "yayint3.m3u8", 16: "yayinsmarts.m3u8", 17: "yayinsms2.m3u8",
            18: "yayintrtspor.m3u8", 19: "yayintrtspor2.m3u8", 20: "yayintrt1.m3u8",
            21: "yayinas.m3u8", 22: "yayinatv.m3u8", 23: "yayintv8.m3u8", 24: "yayintv85.m3u8",
            25: "yayinf1.m3u8", 26: "yayinnbatv.m3u8", 27: "yayineu1.m3u8", 28: "yayineu2.m3u8",
            29: "yayinex1.m3u8", 30: "yayinex2.m3u8", 31: "yayinex3.m3u8", 32: "yayinex4.m3u8",
            33: "yayinex5.m3u8", 34: "yayinex6.m3u8", 35: "yayinex7.m3u8", 36: "yayinex8.m3u8"
        }

    def find_working_domain(self):
        headers = {"User-Agent": "Mozilla/5.0"}
        for i in range(54, 105):
            url = f"https://dengetv{i}.live/"
            try:
                r = self.httpx.get(url, headers=headers)
                if r.status_code == 200 and r.text.strip():
                    print(f"Dengetv: Çalışan domain bulundu -> {url}")
                    return url
            except Exception: continue
        print("Dengetv: Çalışan domain bulunamadı, varsayılan kullanılıyor.")
        return "https://dengetv58.live/"

    def calistir(self):
        referer = self.find_working_domain()
        m3u = []
        for _, file_name in self.channel_files.items():
            channel_name = file_name.replace(".m3u8", "").capitalize()
            m3u.append(f'#EXTINF:-1 group-title="Dengetv54",{channel_name}')
            m3u.append('#EXTVLCOPT:http-user-agent=Mozilla/5.0')
            m3u.append(f'#EXTVLCOPT:http-referrer={referer}')
            m3u.append(f'{self.base_stream_url}{file_name}')
        content = "\n".join(m3u)
        print(f"Dengetv54 içerik uzunluğu: {len(content)}")
        return content

# ---------------- XYZsportsManager ----------------
class XYZsportsManager:
    def __init__(self):
        self.httpx = Client(timeout=10, verify=False)
        self.channel_ids = [
            "bein-sports-1", "bein-sports-2", "bein-sports-3", "bein-sports-4", "bein-sports-5",
            "bein-sports-max-1", "bein-sports-max-2", "smart-spor", "smart-spor-2", "trt-spor",
            "trt-spor-2", "aspor", "s-sport", "s-sport-2", "s-sport-plus-1", "s-sport-plus-2"
        ]

    def find_working_domain(self, start=248, end=350):
        headers = {"User-Agent": "Mozilla/5.0"}
        for i in range(start, end + 1):
            url = f"https://www.xyzsports{i}.xyz/"
            try:
                r = self.httpx.get(url, headers=headers)
                if r.status_code == 200 and "uxsyplayer" in r.text:
                    print(f"XYZsports: Çalışan domain bulundu -> {url}")
                    return r.text, url
            except Exception: continue
        return None, None

    def find_dynamic_player_domain(self, html):
        m = re.search(r'https?://([a-z0-9\-]+\.[0-9a-z]+\.click)', html)
        return f"https://{m.group(1)}" if m else None

    def extract_base_stream_url(self, html):
        m = re.search(r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)', html)
        return m.group(1) if m else None

    def calistir(self):
        html, referer_url = self.find_working_domain()
        if not html:
            print("XYZsports: Çalışan domain bulunamadı!")
            return ""
        player_domain = self.find_dynamic_player_domain(html)
        if not player_domain:
            print("XYZsports: Player domain bulunamadı!")
            return ""
        try:
            r = self.httpx.get(f"{player_domain}/index.php?id={self.channel_ids[0]}", headers={"User-Agent": "Mozilla/5.0", "Referer": referer_url})
            base_url = self.extract_base_stream_url(r.text)
            if not base_url:
                print("XYZsports: Base stream URL bulunamadı!")
                return ""
            m3u = []
            for cid in self.channel_ids:
                channel_name = cid.replace("-", " ").title()
                m3u.append(f'#EXTINF:-1 group-title="XYZSport",{channel_name}')
                m3u.append('#EXTVLCOPT:http-user-agent=Mozilla/5.0')
                m3u.append(f'#EXTVLCOPT:http-referrer={referer_url}')
                m3u.append(f'{base_url}{cid}/playlist.m3u8')
            content = "\n".join(m3u)
            print(f"XYZsports içerik uzunluğu: {len(content)}")
            return content
        except Exception as e:
            print(f"XYZsports: Stream URL alınırken hata oluştu: {e}")
            return ""

# ---------------- TRGOALSManager ----------------
class TRGOALSManager:
    def __init__(self):
        self.httpx = Client(timeout=15, verify=False, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)'})

    def get_dynamic_urls(self):
        try:
            redirect_content = self.httpx.get('https://eniyiyayinci.github.io/redirect/index.html').text
            domain_match = re.search(r'URL=(https:\/\/[^"]+)', redirect_content or '')
            dynamic_domain = (domain_match.group(1) if domain_match else 'https://trgoals896.xyz').rstrip('/') + '/'
            print(f"TRGOALS: Dinamik domain bulundu -> {dynamic_domain}")

            channel_content = self.httpx.get(f"{dynamic_domain}channel.html").text
            base_match = re.search(r'const\s+baseurl\s*=\s*["\']([^"\']+)["\']', channel_content or '', re.IGNORECASE)
            base_url = (base_match.group(1) if base_match else 'https://iss.trgoalshls1.shop').rstrip('/') + '/'
            print(f"TRGOALS: Base URL bulundu -> {base_url}")

            return {'dynamic_domain': dynamic_domain, 'base_url': base_url}
        except Exception as e:
            print(f"TRGOALS: Dinamik URL'ler alınırken hata: {e}")
            return {'dynamic_domain': None, 'base_url': None}

    def calistir(self):
        urls = self.get_dynamic_urls()
        if not urls.get('dynamic_domain') or not urls.get('base_url'):
            return ""

        channels = {1: "BEIN SPORTS 1 (ZIRVE)", 2: "BEIN SPORTS 1 (1)", 3: "BEIN SPORTS 1 (INAT)", 4: "BEIN SPORTS 2", 5: "BEIN SPORTS 3", 6: "BEIN SPORTS 4", 7: "BEIN SPORTS 5", 8: "BEIN SPORTS MAX 1", 9: "BEIN SPORTS MAX 2", 10: "S SPORT PLUS 1", 11: "S SPORT PLUS 2", 13: "TIVIBU SPOR 1", 14: "TIVIBU SPOR 2", 15: "TIVIBU SPOR 3", 16: "SPOR SMART 1", 17: "SPOR SMART 2", 18: "TRT SPOR 1", 19: "TRT SPOR 2", 20: "TRT 1", 21: "A SPOR", 22: "ATV", 23: "TV 8", 24: "TV 8.5", 25: "FORMULA 1", 26: "NBA TV", 27: "EURO SPORT 1", 28: "EURO SPORT 2", 29: "EXXEN SPOR 1", 30: "EXXEN SPOR 2", 31: "EXXEN SPOR 3", 32: "EXXEN SPOR 4", 33: "EXXEN SPOR 5", 34: "EXXEN SPOR 6", 35: "EXXEN SPOR 7", 36: "EXXEN SPOR 8"}
        stream_paths = {1: "yayinzirve.m3u8", 2: "yayin1.m3u8", 3: "yayininat.m3u8", 4: "yayinb2.m3u8", 5: "yayinb3.m3u8", 6: "yayinb4.m3u8", 7: "yayinb5.m3u8", 8: "yayinbm1.m3u8", 9: "yayinbm2.m3u8", 10: "yayinss.m3u8", 11: "yayinss2.m3u8", 13: "yayint1.m3u8", 14: "yayint2.m3u8", 15: "yayint3.m3u8", 16: "yayinsmarts.m3u8", 17: "yayinsms2.m3u8", 18: "yayintrtspor.m3u8", 19: "yayintrtspor2.m3u8", 20: "yayintrt1.m3u8", 21: "yayinas.m3u8", 22: "yayinatv.m3u8", 23: "yayintv8.m3u8", 24: "yayintv85.m3u8", 25: "yayinf1.m3u8", 26: "yayinnbatv.m3u8", 27: "yayineu1.m3u8", 28: "yayineu2.m3u8", 29: "yayinex1.m3u8", 30: "yayinex2.m3u8", 31: "yayinex3.m3u8", 32: "yayinex4.m3u8", 33: "yayinex5.m3u8", 34: "yayinex6.m3u8", 35: "yayinex7.m3u8", 36: "yayinex8.m3u8"}

        m3u = []
        for channel_id, channel_name in channels.items():
            if channel_id in stream_paths:
                stream_url = f"{urls['base_url']}{stream_paths[channel_id]}"
                m3u.append(f'#EXTINF:-1 group-title="TRGOALS",{channel_name}')
                m3u.append('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)')
                m3u.append(f'#EXTVLCOPT:http-referrer={urls["dynamic_domain"]}')
                m3u.append(stream_url)

        content = "\n".join(m3u)
        print(f"TRGOALS içerik uzunluğu: {len(content)}")
        return content

# ---------------- SporcafeManager ----------------
class SporcafeManager:
    def __init__(self):
        self.httpx = Client(timeout=10, verify=False)
        self.HEADERS = {"User-Agent": "Mozilla/5.0"}
        self.CHANNELS = [
            {"id": "bein1", "source_id": "selcukbeinsports1", "name": "BeIN Sports 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "Spor"},
            {"id": "bein2", "source_id": "selcukbeinsports2", "name": "BeIN Sports 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/7uv6x71628799003.png", "group": "Spor"},
            {"id": "bein3", "source_id": "selcukbeinsports3", "name": "BeIN Sports 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/u3117i1628798857.png", "group": "Spor"},
            {"id": "bein4", "source_id": "selcukbeinsports4", "name": "BeIN Sports 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/2ktmcp1628798841.png", "group": "Spor"},
            {"id": "bein5", "source_id": "selcukbeinsports5", "name": "BeIN Sports 5", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/BeIn_Sports_5_US.png", "group": "Spor"},
            {"id": "beinmax1", "source_id": "selcukbeinsportsmax1", "name": "BeIN Sports Max 1", "logo": "https://assets.bein.com/mena/sites/3/2015/06/beIN_SPORTS_MAX1_DIGITAL_Mono.png", "group": "Spor"},
            {"id": "beinmax2", "source_id": "selcukbeinsportsmax2", "name": "BeIN Sports Max 2", "logo": "http://tvprofil.com/img/kanali-logo/beIN_Sports_MAX_2_TR_logo_v2.png?1734011568", "group": "Spor"},
            {"id": "tivibu1", "source_id": "selcuktivibuspor1", "name": "Tivibu Spor 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/qadnsi1642604437.png", "group": "Spor"},
            {"id": "tivibu2", "source_id": "selcuktivibuspor2", "name": "Tivibu Spor 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/kuasdm1642604455.png", "group": "Spor"},
            {"id": "tivibu3", "source_id": "selcuktivibuspor3", "name": "Tivibu Spor 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/slwrz41642604502.png", "group": "Spor"},
            {"id": "tivibu4", "source_id": "selcuktivibuspor4", "name": "Tivibu Spor 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/59bqi81642604517.png", "group": "Spor"},
            {"id": "ssport1", "source_id": "selcukssport", "name": "S Sport 1", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923239.png", "group": "Spor"},
            {"id": "ssport2", "source_id": "selcukssport2", "name": "S Sport 2", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923321.png", "group": "Spor"},
            {"id": "smart1", "source_id": "selcuksmartspor", "name": "Smart Spor 1", "logo": "https://dsmart-static-v2.ercdn.net//resize-width/1920/content/p/el/11909/Thumbnail.png", "group": "Spor"},
            {"id": "smart2", "source_id": "selcuksmartspor2", "name": "Smart Spor 2", "logo": "https://www.dsmart.com.tr/api/v1/public/images/kanallar/SPORSMART2-gri.png", "group": "Spor"},
            {"id": "aspor", "source_id": "selcukaspor", "name": "A Spor", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/9d28401f-2d4e-4862-85e2-69773f6f45f4.png", "group": "Spor"},
            {"id": "eurosport1", "source_id": "selcukeurosport1", "name": "Eurosport 1", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/54cad412-5f3a-4184-b5fc-d567a5de7160.png", "group": "Spor"},
            {"id": "eurosport2", "source_id": "selcukeurosport2", "name": "Eurosport 2", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/a4cbdd15-1509-408f-a108-65b8f88f2066.png", "group": "Spor"},
        ]

    def find_working_domain(self, start=6, end=100):
        print("Sporcafe: Domainler taranıyor...")
        for i in range(start, end + 1):
            url = f"https://www.sporcafe{i}.xyz/"
            try:
                res = self.httpx.get(url, headers=self.HEADERS, timeout=5)
                if res.status_code == 200 and "uxsyplayer" in res.text:
                    print(f"Sporcafe: Aktif domain bulundu -> {url}")
                    return res.text, url
            except Exception:
                continue
        print("Sporcafe: Aktif domain bulunamadı.")
        return None, None

    def find_stream_domain(self, html):
        match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', html)
        return f"https://{match.group(1)}" if match else None

    def extract_base_url(self, html):
        match = re.search(r'this\.adsBaseUrl\s*=\s*[\'"]([^\'"]+)', html)
        return match.group(1) if match else None

    def fetch_streams(self, domain, referer):
        result = []
        for ch in self.CHANNELS:
            full_url = f"{domain}/index.php?id={ch['source_id']}"
            try:
                r = self.httpx.get(full_url, headers={**self.HEADERS, "Referer": referer}, timeout=5)
                if r.status_code == 200:
                    base = self.extract_base_url(r.text)
                    if base:
                        stream = f"{base}{ch['source_id']}/playlist.m3u8"
                        print(f"Sporcafe: {ch['name']} -> Alındı")
                        result.append((ch, stream))
            except Exception:
                pass
        return result

    def calistir(self):
        html, referer = self.find_working_domain()
        if not html:
            return ""
        stream_domain = self.find_stream_domain(html)
        if not stream_domain:
            print("Sporcafe: Yayın domaini bulunamadı.")
            return ""
        print(f"Sporcafe: Yayın domaini -> {stream_domain}")

        streams = self.fetch_streams(stream_domain, referer)
        if not streams:
            print("Sporcafe: Hiçbir yayın alınamadı.")
            return ""

        m3u = []
        for ch, url in streams:
            m3u.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="Sporcafe",{ch["name"]}')
            m3u.append(f'#EXTVLCOPT:http-referrer={referer}')
            m3u.append(f'#EXTVLCOPT:http-user-agent={self.HEADERS["User-Agent"]}')
            m3u.append(url)

        content = "\n".join(m3u)
        print(f"Sporcafe içerik uzunluğu: {len(content)}")
        return content

# ---------------- SalamisTVManager ----------------
class SalamisTVManager:
    def __init__(self):
        self.referer_url = "https://salamistv15.online/"
        self.base_stream_url = "https://macarenatv5.com"
        self.logo_url = "https://i.hizliresim.com/b6xqz10.jpg"
        self.channels = [
            {"name": "BEIN Sport 1", "id": "701"}, {"name": "BEIN Sport 2", "id": "702"},
            {"name": "BEIN Sport 3", "id": "703"}, {"name": "BEIN Sport 4", "id": "704"},
            {"name": "S Spor", "id": "705"}, {"name": "S Spor 2", "id": "730"},
            {"name": "Tivibu Spor 1", "id": "706"}, {"name": "Tivibu Spor 2", "id": "711"},
            {"name": "Tivibu Spor 3", "id": "712"}, {"name": "Tivibu Spor 4", "id": "713"},
            {"name": "Spor Smart 1", "id": "707"}, {"name": "Spor Smart 2", "id": "708"},
            {"name": "A Spor", "id": "709"}, {"name": "NBA", "id": "nba"}, {"name": "SKYF1", "id": "skyf1"},
        ]

    def calistir(self):
        m3u = []
        for channel in self.channels:
            stream_url = f"{self.base_stream_url}/{channel['id']}/mono.m3u8"
            m3u.append(f'#EXTINF:-1 tvg-id="spor" tvg-logo="{self.logo_url}" group-title="SalamisTV",{channel["name"]}')
            m3u.append(f'#EXTVLCOPT:http-referer={self.referer_url}')
            m3u.append(stream_url)
        content = "\n".join(m3u)
        print(f"SalamisTV içerik uzunluğu: {len(content)}")
        return content

# ---------------- NexaTVManager ----------------
class NexaTVManager:
    def __init__(self):
        self.proxy_prefix = "https://api.codetabs.com/v1/proxy/?quest="
        self.base_stream_url = "https://andro.okan9gote10sokan.cfd/checklist/"
        self.logo_url = "https://i.hizliresim.com/8xzjgqv.jpg"
        self.group_title = "NexaTV"
        self.channels = [
            {"name": "TR:beIN Sport 1 HD", "path": "androstreamlivebs1.m3u8"},
            {"name": "TR:beIN Sport 2 HD", "path": "androstreamlivebs2.m3u8"},
            {"name": "TR:beIN Sport 3 HD", "path": "androstreamlivebs3.m3u8"},
            {"name": "TR:beIN Sport 4 HD", "path": "androstreamlivebs4.m3u8"},
            {"name": "TR:beIN Sport 5 HD", "path": "androstreamlivebs5.m3u8"},
            {"name": "TR:beIN Sport Max 1 HD", "path": "androstreamlivebsm1.m3u8"},
            {"name": "TR:beIN Sport Max 2 HD", "path": "androstreamlivebsm2.m3u8"},
            {"name": "TR:S Sport 1 HD", "path": "androstreamlivess1.m3u8"},
            {"name": "TR:S Sport 2 HD", "path": "androstreamlivess2.m3u8"},
            {"name": "TR:Tivibu Sport HD", "path": "androstreamlivets.m3u8"},
            {"name": "TR:Tivibu Sport 1 HD", "path": "androstreamlivets1.m3u8"},
            {"name": "TR:Tivibu Sport 2 HD", "path": "androstreamlivets2.m3u8"},
            {"name": "TR:Tivibu Sport 3 HD", "path": "androstreamlivets3.m3u8"},
            {"name": "TR:Tivibu Sport 4 HD", "path": "androstreamlivets4.m3u8"},
            {"name": "TR:Smart Sport 1 HD", "path": "androstreamlivesm1.m3u8"},
            {"name": "TR:Smart Sport 2 HD", "path": "androstreamlivesm2.m3u8"},
            {"name": "TR:Euro Sport 1 HD", "path": "androstreamlivees1.m3u8"},
            {"name": "TR:Euro Sport 2 HD", "path": "androstreamlivees2.m3u8"},
            {"name": "TR:Tabii HD", "path": "androstreamlivetb.m3u8"},
            {"name": "TR:Tabii 1 HD", "path": "androstreamlivetb1.m3u8"},
            {"name": "TR:Tabii 2 HD", "path": "androstreamlivetb2.m3u8"},
            {"name": "TR:Tabii 3 HD", "path": "androstreamlivetb3.m3u8"},
            {"name": "TR:Tabii 4 HD", "path": "androstreamlivetb4.m3u8"},
            {"name": "TR:Tabii 5 HD", "path": "androstreamlivetb5.m3u8"},
            {"name": "TR:Tabii 6 HD", "path": "androstreamlivetb6.m3u8"},
            {"name": "TR:Tabii 7 HD", "path": "androstreamlivetb7.m3u8"},
            {"name": "TR:Tabii 8 HD", "path": "androstreamlivetb8.m3u8"},
            {"name": "TR:Exxen HD", "path": "androstreamliveexn.m3u8"},
            {"name": "TR:Exxen 1 HD", "path": "androstreamliveexn1.m3u8"},
            {"name": "TR:Exxen 2 HD", "path": "androstreamliveexn2.m3u8"},
            {"name": "TR:Exxen 3 HD", "path": "androstreamliveexn3.m3u8"},
            {"name": "TR:Exxen 4 HD", "path": "androstreamliveexn4.m3u8"},
            {"name": "TR:Exxen 5 HD", "path": "androstreamliveexn5.m3u8"},
            {"name": "TR:Exxen 6 HD", "path": "androstreamliveexn6.m3u8"},
            {"name": "TR:Exxen 7 HD", "path": "androstreamliveexn7.m3u8"},
        ]

    def calistir(self):
        m3u = []
        for channel in self.channels:
            real_url = f"{self.base_stream_url}{channel['path']}"
            stream_url = f"{self.proxy_prefix}{real_url}"
            m3u.append(f'#EXTINF:-1 tvg-id="sport.tr" tvg-name="{channel["name"]}" tvg-logo="{self.logo_url}" group-title="{self.group_title}",{channel["name"]}')
            m3u.append(stream_url)
        content = "\n".join(m3u)
        print(f"NexaTV içerik uzunluğu: {len(content)}")
        return content

# ---------------- JustSportHDManager ----------------
class JustSportHDManager:
    def __init__(self):
        self.httpx = Client(timeout=10, verify=False)
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
        # Bu liste sadece gerçek kanalları içerir, tanıtım linkleri hariç tutulmuştur.
        self.CHANNELS = [
            {"name": "Bein Sports 1", "logo": "bein1.png", "path": "bein1.m3u8"},
            {"name": "Bein Sports 2", "logo": "bein2.png", "path": "bein2.m3u8"},
            {"name": "Bein Sports 3", "logo": "bein3.png", "path": "bein3.m3u8"},
            {"name": "Bein Sports 4", "logo": "bein4.png", "path": "bein4.m3u8"},
            {"name": "Bein Sports 5", "logo": "bein5.png", "path": "bein5.m3u8"},
            {"name": "Exxen Spor", "logo": "exxen.png", "path": "exxen.m3u8"},
            {"name": "S Sport", "logo": "ssport.png", "path": "ssport.m3u8"},
            {"name": "S Sport 2", "logo": "s2sport.png", "path": "ssport2.m3u8"},
            {"name": "S Spor Plus", "logo": "ssportplus.png", "path": "ssportplus.m3u8"},
            {"name": "Spor Smart", "logo": "sporsmart.png", "path": "sporsmart.m3u8"},
            {"name": "Tivibu Spor 1", "logo": "tivibuspor.png", "path": "tivibu1.m3u8"},
            {"name": "Tivibu Spor 2", "logo": "tivibuspor2.png", "path": "tivibu2.m3u8"},
            {"name": "Tivibu Spor 3", "logo": "tivibuspor3.png", "path": "tivibu3.m3u8"},
        ]

    def find_working_domain(self, start=40, end=100):
        headers = {"User-Agent": self.USER_AGENT}
        for i in range(start, end + 1):
            url = f"https://justsporthd{i}.xyz/"
            try:
                r = self.httpx.get(url, headers=headers, timeout=5)
                if r.status_code == 200 and "JustSportHD" in r.text:
                    print(f"JustSportHD: Çalışan domain bulundu -> {url}")
                    return r.text, url
            except Exception:
                continue
        print("JustSportHD: Çalışan domain bulunamadı.")
        return None, None

    def find_stream_domain(self, html):
        match = re.search(r'https?://(streamnet[0-9]+\.xyz)', html)
        return f"https://{match.group(1)}" if match else None

    def calistir(self):
        html, referer_url = self.find_working_domain()
        if not html or not referer_url:
            return ""

        stream_base_url = self.find_stream_domain(html)
        if not stream_base_url:
            print("JustSportHD: Yayın domaini (streamnet) bulunamadı.")
            return ""
        print(f"JustSportHD: Yayın domaini bulundu -> {stream_base_url}")

        m3u = []
        for channel in self.CHANNELS:
            channel_name = f"{channel['name']} JustSportHD"
            logo_url = f"{referer_url.strip('/')}/channel_logo/{channel['logo']}"
            stream_url = f"{stream_base_url}/?url=https://streamcdn.xyz/hls/{channel['path']}"
            
            m3u.append(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="JustSportHD Liste",{channel_name}')
            m3u.append(f'#EXTVLCOPT:http-referer={referer_url}')
            m3u.append(f'#EXTVLCOPT:http-user-agent={self.USER_AGENT}')
            m3u.append(stream_url)

        content = "\n".join(m3u)
        print(f"JustSportHD içerik uzunluğu: {len(content)}")
        return content

# ---------------- Main Execution ----------------
def gorevi_calistir():
    print(f"--- Görev Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    CIKTI_DOSYASI = "spor-karma.m3u"
    all_m3u = [""]

    kaynaklar = [
        Dengetv54Manager(),
        XYZsportsManager(),
        TRGOALSManager(),
        SporcafeManager(),
        SalamisTVManager(),
        NexaTVManager(),
        JustSportHDManager()
    ]

    for kaynak in kaynaklar:
        try:
            print(f"\n--- {kaynak.__class__.__name__} işleniyor... ---")
            m3u_icerigi = kaynak.calistir()
            if m3u_icerigi:
                all_m3u.append(m3u_icerigi)
        except Exception as e:
            print(f"{kaynak.__class__.__name__} işlenirken bir hata oluştu: {e}")

    all_m3u.append(f'\n# Generated: {datetime.utcnow().isoformat()}')

    try:
        with open(CIKTI_DOSYASI, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_m3u))
        print(f"\n✅ Birleşik M3U oluşturuldu: {CIKTI_DOSYASI}")
    except Exception as e:
        print(f"Dosya yazılırken bir hata oluştu: {e}")
    print("--- Görev Tamamlandı. ---")

if __name__ == "__main__":
    gorevi_calistir()
