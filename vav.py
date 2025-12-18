import requests
import json

# Ülke isimlerini Türkçeye çevirme eşleme tablosu
country_mapping = {
    "Germany": ("Almanya", "Almanca"),
    "United Kingdom": ("Birleşik Krallık", "İngilizce"),
    "France": ("Fransa", "Fransızca"),
    "Turkey": ("Türkiye", "Türkçe"),
    "Italy": ("İtalya", "İtalanca"),
    "Spain": ("İspanya", "İspanyolca"),
    "Albania": ("Arnavutluk", "Arnavutça"),
    "Arabia": ("Arabistan", "Arapça"),
    "Balkans": ("Balkanlar", "Türkçe"),
    "Bulgaria": ("Bulgaristan", "Bulgarca"),
    "Netherlands": ("Hollanda", "Felemenkçe"),
    "Poland": ("Polonya", "Lehçe"),
    "Portugal": ("Portekiz", "Portekizce"),
    "Russia": ("Rusya", "Rusça"),
}

# JSON verisini çek
url = "https://www2.vavoo.to/live2/index?countries=all&output=json"
response = requests.get(url)
channels = response.json()

# M3U dosya içeriği oluştur
m3u_content = "#EXTM3U\n"

for channel in channels:
    group = channel["group"]
    
    # Sadece Turkey (Türkiye) kategorisindeki kanalları işle
    if group != "Turkey":
        continue
    
    logo = channel["logo"]
    name = channel["name"]
    url = channel["url"]
    
    # Ülke adına göre tvg-country ve tvg-language belirleme
    country_name, language_code = country_mapping.get(group, (group, "xx"))
    
    # tvg-id oluşturma (kanal adı + ülke kodu)
    tvg_id = f"{name.lower().replace(' ', '').replace('.', '')}.{language_code}"
    
    # URL formatını değiştirme
    stream_url = url.replace("live2/play", "play").replace(".ts", "/index.m3u8")
    
    # M3U formatında satır ekleme
    m3u_content += f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{country_name}" tvg-country="{country_name}" tvg-language="{language_code}", {name}\n{stream_url}\n'

# Dosyayı bulunduğu dizine kaydet
with open("vavoo.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("M3U listesi oluşturuldu: vavoo.m3u")
