import requests
import re
import sys

def main():
    try:
        # Domain aralığı (25–1000)
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
            print("⚠️  Aktif domain bulunamadı.")
            return 1
        """
        # İlk karşılaşma ID'si al
        print("📡 Karşılaşma ID'si alınıyor...")
        try:
            html = requests.get(active_domain, timeout=10).text
            m = re.search(r'<iframe[^>]+id="customIframe"[^>]+src="event\.html\?id=([^"]+)"', html)
            
            if not m:
                print("⚠️  Karşılaşma ID bulunamadı.")
                return 1
            
            first_id = m.group(1)
            print(f"✅ Karşılaşma ID bulundu: {first_id}")
            
        except Exception as e:
            print(f"⚠️  HTML alınırken hata: {str(e)}")
            return 1
        """
        # Base URL çek
        print("🔗 Base URL alınıyor...")
        try:
            for i in range(24, 1000):
            url = f"https://taraftarium{i}.xyz/"
            try:
                r = requests.head(url, timeout=5)
                if r.status_code == 200:
                    eventsource_domain = url
                    print(f"✅ Aktif domain bulundu: {active_domain}")
                    break
            except Exception as e:
                continue
            event_source = requests.get(eventsource_domain + "event.html?id=" + "androstreamlivebs2", timeout=10).text
            b = re.search(r'const\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
            
            if not b:
                print("⚠️  Base URL bulunamadı.")
                return 1
            
            base_url = b.group(1)
            print(f"✅ Base URL bulundu: {base_url}")
            
        except Exception as e:
            print(f"⚠️  Event source alınırken hata: {str(e)}")
            return 1
        
        # Script.js'den karşılaşmalar listesini çek
        print("⚽ Karşılaşmalar listesi alınıyor...")
        try:
            script_url = active_domain + "script2.js"
            script_response = requests.get(script_url, timeout=10)
            script_response.encoding = 'utf-8'
            script_content = script_response.text
            
            # karsilasmalar array'ini bul
            karsilasmalar_match = re.search(
                r'const\s+karsilasmalar\s*=\s*(\[[\s\S]*?\n\];)',
                script_content
            )
            
            if not karsilasmalar_match:
                print("⚠️  Karşılaşmalar listesi bulunamadı.")
                return 1
            
            karsilasmalar_text = karsilasmalar_match.group(1)
            
            # JavaScript object'lerini manuel olarak parse et
            karsilasmalar = []
            # Her object bloğunu bul - daha esnek pattern
            object_pattern = r'\{\s*"tarih":\s*"([^"]*)",\s*"time":\s*"([^"]*)",\s*"league":\s*"([^"]*)",\s*"title":\s*"([^"]*)",\s*"url":\s*"([^"]*)",\s*"live":\s*(true|false)\s*\}'
            
            for match in re.finditer(object_pattern, karsilasmalar_text):
                tarih = match.group(1)
                time = match.group(2)
                league = match.group(3)
                title = match.group(4)
                url = match.group(5)
                live = match.group(6) == 'true'
                
                # Türkçe karakter sorununu çöz
                try:
                    league = league.encode('cp1252').decode('utf-8')
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
                
                try:
                    title = title.encode('cp1252').decode('utf-8')
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
                
                karsilasmalar.append({
                    'tarih': tarih,
                    'time': time,
                    'league': league,
                    'title': title,
                    'url': url,
                    'live': live
                })
            
            if not karsilasmalar:
                print("⚠️  Karşılaşma bulunamadı.")
                return 1
            
            print(f"✅ {len(karsilasmalar)} karşılaşma bulundu")
            
        except Exception as e:
            print(f"⚠️  Karşılaşmalar listesi alınırken hata: {str(e)}")
            return 1
        
        # M3U dosyası oluştur
        print("📝 M3U dosyası oluşturuluyor...")
        lines = [""]
        
        for match in karsilasmalar:
            try:
                time = match.get('time', '')
                title = match.get('title', '')
                league = match.get('league', '')
                url = match.get('url', '')
                
                # URL'den ID'yi çıkar: /event.html?id=androstreamlivebirazb5 -> androstreamlivebirazb5
                id_match = re.search(r'\?id=([^&"]+)', url)
                if not id_match:
                    print(f"⚠️  '{title}' için ID bulunamadı, atlanıyor...")
                    continue
                
                match_id = id_match.group(1)
                
                # M3U title formatı: time | title | league
                m3u_title = f"{time} | {title} | {league}"
                
                # M3U satırlarını ekle
                lines.append(f'#EXTINF:-1 group-title="Maç Yayınları" ,{m3u_title}')
                full_url = f"{base_url}{match_id}.m3u8"
                lines.append(full_url)
                
            except Exception as e:
                print(f"⚠️  Karşılaşma işlenirken hata ({title}): {str(e)}")
                continue
        
        with open("karsilasmalar.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        match_count = (len(lines) - 1) // 2  # Başlık satırını çıkar ve her karşılaşma 2 satır
        print(f"✅ karsilasmalar.m3u başarıyla oluşturuldu ({match_count} karşılaşma)")
        return 0
        
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
