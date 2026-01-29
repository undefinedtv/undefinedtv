import requests
import re
import sys

# --- AYARLAR ---
LOGOS = {
    "one_cikanlar": "https://img.icons8.com/color/48/000000/star.png",
    "futbol": "https://img.icons8.com/color/48/000000/football2.png",
    "basketbol": "https://img.icons8.com/color/48/000000/basketball.png",
    "voleybol": "https://img.icons8.com/color/48/000000/volleyball.png",
    "tenis": "https://img.icons8.com/color/48/000000/tennis.png",
    "tv": "https://img.icons8.com/color/48/000000/tv.png"
}

def parse_js_objects(text_content):
    """
    JS array içeriğini (text) alır ve dictionary listesine çevirir.
    Tek bir regex yerine her özelliği ayrı ayrı arar, böylece format farklarından etkilenmez.
    """
    objects = []
    # Süslü parantezlerle ayrılmış her bir objeyi bul (basit split mantığı)
    # Bu yöntem iç içe parantez yoksa çalışır ki bu veri yapısında yok.
    raw_objects = re.findall(r'\{[^\}]+\}', text_content)
    
    for obj_str in raw_objects:
        item = {}
        
        # Regex ile değerleri çek
        time_match = re.search(r'"time":\s*"([^"]*)"', obj_str)
        league_match = re.search(r'"league":\s*"([^"]*)"', obj_str)
        title_match = re.search(r'"title":\s*"([^"]*)"', obj_str)
        url_match = re.search(r'"url":\s*"([^"]*)"', obj_str)
        
        # Sadece URL'si olanları al
        if url_match:
            item['url'] = url_match.group(1)
            item['time'] = time_match.group(1) if time_match else ""
            item['league'] = league_match.group(1) if league_match else ""
            item['title'] = title_match.group(1) if title_match else ""
            
            # Türkçe karakter düzeltmesi
            for key in ['league', 'title']:
                try:
                    item[key] = item[key].encode('cp1252').decode('utf-8')
                except:
                    pass
            
            objects.append(item)
            
    return objects

def main():
    try:
        # 1. Aktif Domain Bulma
        active_domain = None
        print("🔍 Aktif domain aranıyor...")
        
        for i in range(24, 1000):
            url = f"https://taraftarium{i}.xyz/"
            print(f"deniyor -> {url}")
            try:
                r = requests.head(url, timeout=3)
                print(f"r.status_code -> {r.status_code}")
                if r.status_code == 200:
                    active_domain = url
                    print(f"✅ Aktif domain bulundu: {active_domain}")
                    break
            except Exception as e:
                print(f"| Hata: {type(e).__name__}")
                continue
        
        if not active_domain:
            print("⚠️  Aktif domain bulunamadı.")
            return 1

        # 2. Base URL (Yayın sunucusu) Bulma
        print("🔗 Base URL alınıyor...")
        base_url = None
        eventsource_domain = None
        
        # Birazcikspor domain taraması
        for i in range(43, 1000):
            url = f"https://birazcikspor{i}.xyz/"
            try:
                r = requests.head(url, timeout=3)
                if r.status_code == 200:
                    eventsource_domain = url
                    break
            except:
                continue

        if eventsource_domain:
            try:
                # Rastgele bir ID ile event sayfasını çekip baseurl'i regex ile alıyoruz
                event_source = requests.get(eventsource_domain + "event.html?id=androstreamlivebs2", timeout=10).text
                b = re.search(r'const\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
                if b:
                    base_url = b.group(1)
                    print(f"✅ Base URL bulundu: {base_url}")
            except Exception as e:
                print(f"⚠️  Event source okunurken hata: {str(e)}")

        if not base_url:
            print("⚠️  Base URL bulunamadı, işlem iptal.")
            return 1
        
        # 3. Script.js Çekme ve Parse Etme
        print("⚽ Script dosyası indiriliyor...")
        try:
            script_url = active_domain + "script2.js"
            script_response = requests.get(script_url, timeout=10)
            script_response.encoding = 'utf-8'
            script_content = script_response.text
        except Exception as e:
            print(f"⚠️  Script indirilemedi: {str(e)}")
            return 1

        # İşlenecek kategorilerin tanımlanması
        # (JS Değişken Adı, M3U Grup Adı, Logo Key)
        categories = [
            # Önce karsilasmalar (Genelde günün önemli maçları/karışık)
            ("karsilasmalar", "Günün Öne Çıkanları", "one_cikanlar"),
            # Futbol
            ("futbolMatches", "Futbol", "futbol"),
            # Basketbol
            ("basketbolMatches", "Basketbol", "basketbol"),
            # Voleybol
            ("voleybolMatches", "Voleybol", "voleybol"),
            # Tenis
            ("tenisMatches", "Tenis", "tenis"),
            # Kanallar (Script içinde channels değişkeni varsa)
            ("channels", "TV Kanalları", "tv")
        ]

        all_m3u_lines = ["#EXTM3U"]
        total_matches = 0

        for js_var, group_title, logo_key in categories:
            print(f"📂 {group_title} işleniyor...")
            
            # İlgili array'i regex ile çek: const degisken = [ ... ];
            # Köşeli parantez içini alır.
            pattern = rf'const\\s+{js_var}\\s*=\s*(\\[[\s\S]*?\\]);'
            match_array = re.search(pattern, script_content)
            
            if match_array:
                array_content = match_array.group(1)
                matches = parse_js_objects(array_content)
                
                logo_url = LOGOS.get(logo_key, "")
                
                for m in matches:
                    title = m.get('title', 'Bilinmeyen Maç')
                    time = m.get('time', '')
                    league = m.get('league', '')
                    url_partial = m.get('url', '')
                    
                    # URL'den ID'yi çıkar
                    id_match = re.search(r'\?id=([^&"]+)', url_partial)
                    if not id_match:
                        continue
                    
                    stream_id = id_match.group(1)
                    full_stream_url = f"{base_url}{stream_id}.m3u8"
                    
                    # Başlık formatı
                    display_title = f"{time} | {title}"
                    if league:
                        display_title += f" | {league}"
                    
                    # M3U satırını oluştur
                    # group-title: Spor dalı
                    # tvg-logo: İlgili ikon
                    inf_line = f'#EXTINF:-1 group-title="{group_title}" tvg-logo="{logo_url}",{display_title}'
                    
                    all_m3u_lines.append(inf_line)
                    all_m3u_lines.append(full_stream_url)
                    total_matches += 1
            else:
                print(f"ℹ️  '{js_var}' değişkeni bulunamadı veya boş.")

        # 4. Dosyayı Kaydetme
        if total_matches > 0:
            with open("karsilasmalar.m3u", "w", encoding="utf-8") as f:
                f.write("\n".join(all_m3u_lines))
            print(f"✅ karsilasmalar.m3u başarıyla oluşturuldu. ({total_matches} yayın)")
        else:
            print("⚠️  Hiçbir yayın bulunamadı.")
            return 1

        return 0
        
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
