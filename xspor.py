import requests
import re
import concurrent.futures

class XSportScraper:
    def __init__(self):
        self.base_pattern = "https://www.xsportv{}.xyz/"
        self.active_domain = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.channel_ids = [
            "xbeinsports-1", "xbeinsports-2", "xbeinsports-3", "xbeinsports-4", "xbeinsports-5",
            "xbeinsportsmax-1", "xbeinsportsmax-2", "xtivibuspor-1", "xtivibuspor-2",
            "xtivibuspor-3", "xtivibuspor-4", "xssport", "xssport2", "xtabiispor1",
            "xtabiispor2", "xtabiispor3", "xtabiispor4", "xtabiispor5", "xtabiispor6", "xtabiispor7"
        ]
        self.logo = "https://i.hizliresim.com/b6xqz10.jpg"

    def check_domain(self, index):
        url = self.base_pattern.format(index)
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return url
        except:
            return None

    def find_active_domain(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self.check_domain, i) for i in range(56, 1000)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self.active_domain = result
                    return result
        return None

    def get_stream_url(self, player_url, stream_id):
        try:
            res = requests.get(player_url, headers=self.headers, timeout=5)
            match = re.search(r"this\.baseStreamUrl\s*=\s*'(.*?)'", res.text)
            if match:
                base = match.group(1)
                return f"{base}{stream_id}/playlist.m3u8"
        except:
            pass
        return None

    def run(self):
        domain = self.find_active_domain()
        if not domain:
            print("Active domain not found.")
            return

        response = requests.get(domain, headers=self.headers)
        m3u_content = "#EXTM3U\n"

        for cid in self.channel_ids:
            pattern = rf'data-url="(.*?id={cid}.*?)"'
            match = re.search(pattern, response.text)
            
            if match:
                player_link = match.group(1)
                final_url = self.get_stream_url(player_link, cid)
                
                if final_url:
                    name = cid.replace("x", "").replace("-", "").upper()
                    m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="TR: {name} HD" tvg-logo="{self.logo}" group-title="xsportv",TR: {name} HD\n'
                    m3u_content += f"#EXTVLCOPT:http-referer={domain}\n"
                    m3u_content += f"{final_url}\n"

        filename = "xsportv.m3u"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print(f"{filename} kaydedildi")

if __name__ == "__main__":
    bot = XSportScraper()
    bot.run()
          
