import requests
import re
import sys

def main():
    try:
        # Domain aralığı (25–99)
        active_domain = None
        print("🔍 Aktif domain aranıyor...")
        
        for i in range(24, 1000):
            url = f"https://taraftarium{i}.xyz/"
            try:
                r = requests.head(url, timeout=5)
                if r.status_code == 200:
                    active_domain = url
                    print(f"✅ Aktif domain bulundu: {active_domain}")
                    break
            except Exception as e:
                continue
        
        if not active_domain:
            print("⚠️  Aktif domain bulunamadı. Boş M3U dosyası oluşturuluyor...")
            create_empty_m3u()
            return 0
        
        # İlk kanal ID'si al
        print("📡 Kanal ID'si alınıyor...")
        try:
            html = requests.get(active_domain, timeout=10).text
            m = re.search(r'<iframe[^>]+id="matchPlayer"[^>]+src="event\.html\?id=([^"]+)"', html)
            
            if not m:
                print("⚠️  Kanal ID bulunamadı. Boş M3U dosyası oluşturuluyor...")
                create_empty_m3u()
                return 0
            
            first_id = m.group(1)
            print(f"✅ Kanal ID bulundu: {first_id}")
            
        except Exception as e:
            print(f"⚠️  HTML alınırken hata: {str(e)}")
            create_empty_m3u()
            return 0
        
        # Base URL çek
        print("🔗 Base URL alınıyor...")
        try:
            event_source = requests.get(active_domain + "event.html?id=" + first_id, timeout=10).text
            b = re.search(r'const\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
            
            if not b:
                print("⚠️  Base URL bulunamadı. Boş M3U dosyası oluşturuluyor...")
                create_empty_m3u()
                return 0
            
            base_url = b.group(1)
            print(f"✅ Base URL bulundu: {base_url}")
            
        except Exception as e:
            print(f"⚠️  Event source alınırken hata: {str(e)}")
            create_empty_m3u()
            return 0
        
        # Kanal listesi
        channels = [
            { title: "BeIN Sports 1", url: "androstreamlivebs1" },
            { title: "BeIN Sports 2", url: "androstreamlivebs2" },
            { title: "BeIN Sports 3", url: "androstreamlivebs3" },
            { title: "BeIN Sports 4", url: "androstreamlivebs4" },
            { title: "BeIN Sports 5", url: "androstreamlivebs5" },
            { title: "BeIN Sports Max 1", url: "androstreamlivebsm1" },
            { title: "BeIN Sports Max 2", url: "androstreamlivebsm2" },
            { title: "S Sport", url: "androstreamlivess1" },
            { title: "S Sport 2", url: "androstreamlivess2" },
            { title: "S Sport Plus", url: "androstreamlivessplus1" },
            { title: "Tivibu Spor", url: "androstreamlivets" },
            { title: "Tivibu Spor 1", url: "androstreamlivets1" },
            { title: "Tivibu Spor 2", url: "androstreamlivets2" },
            { title: "Tivibu Spor 3", url: "androstreamlivets3" },
            { title: "Tivibu Spor 4", url: "androstreamlivets4" },
            { title: "Smart Spor 1", url: "androstreamlivesm1" },
            { title: "Smart Spor 2", url: "androstreamlivesm2" },
            { title: "Euro Sport 1", url: "androstreamlivees1" },
            { title: "Euro Sport 2", url: "androstreamlivees2" },
            { title: "iDMAN Tv", url: "androstreamliveidm" },
            { title: "Trt 1", url: "androstreamlivetrt1" },
            { title: "Trt Spor", url: "androstreamlivetrts" },
            { title: "Trt Spor YÄ±ldÄ±z", url: "androstreamlivetrtsy" },
            { title: "Atv", url: "androstreamliveatv" },
            { title: "A Spor", url: "androstreamliveas" },
            { title: "A2", url: "androstreamlivea2" },
            { title: "Tjk Tv", url: "androstreamlivetjk" },
            { title: "Ht Spor", url: "androstreamliveht" },
            { title: "Nba Tv", url: "androstreamlivenba" },
            { title: "Tv8", url: "androstreamlivetv8" },
            { title: "Tv8,5", url: "androstreamlivetv85" },
            { title: "Tabi Spor", url: "androstreamlivetb" },
            { title: "Tabi Spor 1", url: "androstreamlivetb1" },
            { title: "Tabi Spor 2", url: "androstreamlivetb2" },
            { title: "Tabi Spor 3", url: "androstreamlivetb3" },
            { title: "Tabi Spor 4", url: "androstreamlivetb4" },
            { title: "Tabi Spor 5", url: "androstreamlivetb5" },
            { title: "Tabi Spor 6", url: "androstreamlivetb6" },
            { title: "Tabi Spor 7", url: "androstreamlivetb7" },
            { title: "Tabi Spor 8", url: "androstreamlivetb8" },
            { title: "Fb Tv", url: "androstreamlivefb" },
            { title: "Cbc Sport", url: "androstreamlivecbcs" },
            { title: "Gs Tv", url: "androstreamlivegs" },
            { title: "Sports Tv", url: "androstreamlivesptstv" },
            { title: "Exxen Tv", url: "androstreamliveexn" },
            { title: "Exxen Sports 1", url: "androstreamliveexn1" },
            { title: "Exxen Sports 2", url: "androstreamliveexn2" },
            { title: "Exxen Sports 3", url: "androstreamliveexn3" },
            { title: "Exxen Sports 4", url: "androstreamliveexn4" },
            { title: "Exxen Sports 5", url: "androstreamliveexn5" },
            { title: "Exxen Sports 6", url: "androstreamliveexn6" },
            { title: "Exxen Sports 7", url: "androstreamliveexn7" },
            { title: "Exxen Sports 8", url: "androstreamliveexn8" }
        ];
        
        # M3U dosyası oluştur
        print("📝 M3U dosyası oluşturuluyor...")
        lines = [""]
        for channel in channels:
            title = channel["title"]
            cid = channel["url"]
            lines.append(f'#EXTINF:-1 tvg-id="sport.tr" tvg-name="TR:{name}" group-title="Andro TV" ,{name}')
            full_url = f"{base_url}{cid}.m3u8"
            lines.append(full_url)
        
        with open("androtv.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"✅ androtv.m3u başarıyla oluşturuldu ({len(channels)} kanal)")
        return 0
        
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {str(e)}")
        print("⚠️  Boş M3U dosyası oluşturuluyor...")
        create_empty_m3u()
        return 0

def create_empty_m3u():
    """Hata durumunda boş/placeholder M3U dosyası oluştur"""
    try:
        with open("androtv.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("# Kanal listesi şu anda kullanılamıyor\n")
        print("✅ Placeholder M3U dosyası oluşturuldu")
    except Exception as e:
        print(f"❌ M3U dosyası oluşturulamadı: {str(e)}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
