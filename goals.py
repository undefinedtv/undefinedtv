import requests
import re

# M3U içeriği
m3u_content = "#EXTM3U\n"

# Trgoals domain kontrol
base = "https://trgoals"
domain = ""

for i in range(1470, 2101):
    test_domain = f"{base}{i}.xyz"
    try:
        response = requests.head(test_domain, timeout=3)
        if response.status_code == 200:
            domain = test_domain
            break
    except:
        continue

if not domain:
    print("Çalışır bir domain bulunamadı.")
    exit()

# YAPILAN DEĞİŞİKLİK BURADA:
# Artık formatımız şu şekilde -> "id": ["Kanal İsmi", "Grup İsmi"]
channel_ids = {
    "yayinzirve": ["beIN Sports 1 A", "BEIN SPORTS"],
    "yayininat":  ["beIN Sports 1 B", "BEIN SPORTS"],
    "yayin1":     ["beIN Sports 1 C️", "BEIN SPORTS"],
    "yayinb2":    ["beIN Sports 2", "BEIN SPORTS"],
    "yayinb3":    ["beIN Sports 3", "BEIN SPORTS"],
    "yayinb4":    ["beIN Sports 4", "BEIN SPORTS"],
    "yayinb5":    ["beIN Sports 5", "BEIN SPORTS"],
    "yayinbm1":   ["beIN Sports 1 Max", "BEIN SPORTS"],
    "yayinbm2":   ["beIN Sports 2 Max", "BEIN SPORTS"],
    "yayinss":    ["S Sports 1", "S SPORTS"],
    "yayinss2":   ["S Sports 2", "S SPORTS"],
    "yayint1":    ["Tivibu Sports 1", "TIVIBU SPORTS"],
    "yayint2":    ["Tivibu Sports 2", "TIVIBU SPORTS"],
    "yayint3":    ["Tivibu Sports 3", "TIVIBU SPORTS"],
    "yayint4":    ["Tivibu Sports 4", "TIVIBU SPORTS"],
    "yayinsmarts":["Smart Sports", "SPOR__"],
    "yayinsms2":  ["Smart Sports 2", "SPOR__"],
    "yayineu1":  ["Euro Sport 1", "SPOR__"],
    "yayineu2":  ["Euro Sport 2", "SPOR__"],
    "yayinex1":   ["Tâbii 1", "SPOR__"],
    "yayinex2":   ["Tâbii 2", "SPOR__"],
    "yayinex3":   ["Tâbii 3", "SPOR__"],
    "yayinex4":   ["Tâbii 4", "SPOR__"],
    "yayinex5":   ["Tâbii 5", "SPOR__"],
    "yayinex6":   ["Tâbii 6", "SPOR__"],
    "yayinex7":   ["Tâbii 7", "SPOR__"],
    "yayinex8":   ["Tâbii 8", "SPOR__"]
}

# Kanalları çek
# YAPILAN DEĞİŞİKLİK: Döngü artık (details) adında bir liste alıyor
for channel_id, details in channel_ids.items():
    channel_name = details[0]  # Listenin ilk elemanı İsim
    group_title = details[1]   # Listenin ikinci elemanı Grup
    
    channel_url = f"{domain}/channel.html?id={channel_id}"
    try:
        r = requests.get(channel_url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        match = re.search(r'const baseurl = "(.*?)"', r.text)
        if match:
            baseurl = match.group(1)
            full_url = f"{baseurl}{channel_id}.m3u8"
            
            # group-title kısmına yukarıdan gelen değişkeni koyduk
            m3u_content += f'#EXTINF:-1 group-title="{group_title}", {channel_name}\n'
            m3u_content += f'{full_url}\n'
            m3u_content += f'#EXTVLCOPT:http-referrer={domain}/n'
    except:
        continue

# Dosyaya kaydet
with open("goals.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("goals.m3u oluşturuldu.")
