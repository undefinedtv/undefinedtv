import requests
import re

# Domain aralığı (25–99)
active_domain = None
for i in range(25, 1000):
    url = f"https://birazcikspor{i}.xyz/"
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            active_domain = url
            break
    except:
        continue

if not active_domain:
    print("Aktif domain bulunamadı.")

# İlk kanal ID'si al
print(active_domain)
html = requests.get(active_domain, timeout=10).text
m = re.search(r'<iframe[^>]+id="matchPlayer"[^>]+src="event\.html\?id=([^"]+)"', html)
if not m:
    print("Kanal ID bulunamadı.")
first_id = m.group(1)

# Base URL çek
event_source = requests.get(active_domain + "event.html?id=" + first_id, timeout=10).text
print(event_source)
b = re.search(r'const\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
if not b:
    print("Base URL bulunamadı.")
base_url = b.group(1)

# Kanal listesi
channels = [
    ("beIN Sport 1 HD","androstreamlivebs1","Andro TV"),
    ("beIN Sport 2 HD","androstreamlivebs2","Andro TV"),
    ("beIN Sport 3 HD","androstreamlivebs3","Andro TV"),
    ("beIN Sport 4 HD","androstreamlivebs4","Andro TV"),
    ("beIN Sport 5 HD","androstreamlivebs5","Andro TV"),
    ("beIN Sport Max 1 HD","androstreamlivebsm1","Andro TV"),
    ("beIN Sport Max 2 HD","androstreamlivebsm2","Andro TV"),
    ("S Sport 1 HD","androstreamlivess1","Andro TV"),
    ("S Sport 2 HD","androstreamlivess2","Andro TV"),
    ("Tivibu Sport HD","androstreamlivets","Andro TV"),
    ("Tivibu Sport 1 HD","androstreamlivets1","Andro TV"),
    ("Tivibu Sport 2 HD","androstreamlivets2","Andro TV"),
    ("Tivibu Sport 3 HD","androstreamlivets3","Andro TV"),
    ("Tivibu Sport 4 HD","androstreamlivets4","Andro TV"),
    ("Smart Sport 1 HD","androstreamlivesm1","Andro TV"),
    ("Smart Sport 2 HD","androstreamlivesm2","Andro TV"),
    ("Euro Sport 1 HD","androstreamlivees1","Andro TV"),
    ("Euro Sport 2 HD","androstreamlivees2","Andro TV"),
    ("Tabii HD","androstreamlivetb","Andro TV"),
    ("Tabii 1 HD","androstreamlivetb1","Andro TV"),
    ("Tabii 2 HD","androstreamlivetb2","Andro TV"),
    ("Tabii 3 HD","androstreamlivetb3","Andro TV"),
    ("Tabii 4 HD","androstreamlivetb4","Andro TV"),
    ("Tabii 5 HD","androstreamlivetb5","Andro TV"),
    ("Tabii 6 HD","androstreamlivetb6","Andro TV"),
    ("Tabii 7 HD","androstreamlivetb7","Andro TV"),
    ("Tabii 8 HD","androstreamlivetb8","Andro TV"),
    ("Exxen HD","androstreamliveexn","Andro TV"),
    ("Exxen 1 HD","androstreamliveexn1","Andro TV"),
    ("Exxen 2 HD","androstreamliveexn2","Andro TV"),
    ("Exxen 3 HD","androstreamliveexn3","Andro TV"),
    ("Exxen 4 HD","androstreamliveexn4","Andro TV"),
    ("Exxen 5 HD","androstreamliveexn5","Andro TV"),
    ("Exxen 6 HD","androstreamliveexn6","Andro TV"),
    ("Exxen 7 HD","androstreamliveexn7","Andro TV"),
    ("Exxen 8 HD","androstreamliveexn8","Andro TV"),
]

# M3U dosyası oluştur
lines = ["#EXTM3U"]
for name, cid, title in channels:
    lines.append(f'#EXTINF:-1 tvg-id="sport.tr" tvg-name="TR:{name}" group-title="{title}" ,TR:{name}')
    full_url = f"{base_url}{cid}.m3u8"
    lines.append(full_url)

with open("androtv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("✅ androtv.m3u oluşturuldu.")
