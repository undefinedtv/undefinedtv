import requests
import re
import sys
import base64

def main():
    try:
        ## ÇALMAAA OÇ ##
        
        # Domain aralığı (25–99)
        active_domain = None
        print("🔍 Aktif domain aranıyor...")
        
        for i in range(238, 2000):
            url = f"https://zeustv{i}.vip/"
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
            return 0
        
        print("🔗 Base URL alınıyor...")
        try:
            event_source = requests.get(active_domain + "ch.html?id=b1", timeout=10).text
            all_b64 = re.findall(r'["\']([A-Za-z0-9+/]{20,}={0,2})["\']', event_source)
            print("Bulunan base64 adayları:")
            for s in all_b64:
                try:
                    decoded = base64.b64decode(s).decode("utf-8")
                    if decoded.startswith("http"): 
                        base_url = decoded
                except:
                    pass

        except Exception as e:
            print(f"⚠️  Event source alınırken hata: {str(e)}")
            return 0
        
        channel_ids = {}
        try:
            response = requests.get(active_domain + "/api/channels.php", timeout=10).json()
            for ch in response.get("channels", []):
                embed = ch.get("embed_code", "")
                name = ch.get("name", "")
                
                # id=b1 gibi değeri çek
                id_match = re.search(r"id=([a-zA-Z0-9_]+)", embed)
                
                if id_match:
                    ch_id = id_match.group(1)
                    channel_ids[ch_id] = [name, "Zeus TV"]

        except Exception as e:
            print(f"⚠️  API hatası: {e} — Manuel liste kullanılıyor.")
            channel_ids = {
                                'b1': ['Bein 1', 'Zeus TV'], 'b2': ['Bein 2', 'Zeus TV'], 'b3': ['Bein 3', 'Zeus TV'],
                                'b4': ['Bein 4', 'Zeus TV'], 'bein5': ['Bein 5', 'Zeus TV'], 'b1max': ['Bein 1 Max', 'Zeus TV'],
                                'b2max': ['Bein 2 Max', 'Zeus TV'], 's1': ['S Spor 1', 'Zeus TV'], 's2': ['S Spor 2', 'Zeus TV'],
                                'smart1': ['Smart Spor 1', 'Zeus TV'], 'smart2': ['Smart Spor 2', 'Zeus TV'],
                                'tivibu': ['Tivibu Spor 1', 'Zeus TV'], 'tivibu1': ['Tivibu Spor 2', 'Zeus TV'],
                                'tivibu2': ['Tivibu Spor 3', 'Zeus TV'], 'tivibu3': ['Tivibu Spor 4', 'Zeus TV'],
                                'xtrtspor': ['TRT Spor', 'Zeus TV'], 'trtyildiz': ['TRT Spor Yıldız', 'Zeus TV'],
                                'trt1yedek': ['TRT 1 Yedek', 'Zeus TV'], 'xaspor': ['A Spor', 'Zeus TV'],
                                'xatv': ['ATV', 'Zeus TV'], 'xtv8': ['Tv 8', 'Zeus TV'], 'xtv85': ['Tv 8,5', 'Zeus TV'],
                                'sifirtv': ['Sıfır Tv', 'Zeus TV'], 'euro1': ['Euro Sport 1', 'Zeus TV'],
                                'euro2': ['Euro Sport 2', 'Zeus TV'], 'tabiiyedek': ['Tabi Yedek', 'Zeus TV'],
                                'tabii1': ['Tabii Spor 1', 'Zeus TV'], 'tabii2': ['Tabii Spor 2', 'Zeus TV'],
                                'tabii3': ['Tabii Spor 3', 'Zeus TV'], 'tabii4': ['Tabii Spor 4', 'Zeus TV'],
                                'tabii5': ['Tabii Spor 5', 'Zeus TV'], 'tabii6': ['Tabii Spor 6', 'Zeus TV'],
                                'xexxen': ['Exxen', 'Zeus TV'], 'xexxen1': ['Exxen 1', 'Zeus TV'],
                                'b1local': ['Bein Yedek 2', 'Zeus TV'], 'xahaber': ['A Haber', 'Zeus TV']
                            }
        
        # M3U dosyası oluştur
        print("📝 M3U dosyası oluşturuluyor...")
        lines = ["\n"]
        for cid, details in channel_ids.items():
            name = details[0]  # Listenin ilk elemanı: Kanal Adı (Örn: beIN Sports 1 A)
            title = details[1] # Listenin ikinci elemanı: Grup (Örn: Zeus TV)
            
            # EXTM3U satırını oluştur
            lines.append(f'#EXTINF:-1 group-title="Zeus TV" ,{name}')
            
            # URL satırını oluştur (Sözlük anahtarı olan 'cid' kullanılıyor)
            full_url = f'{base_url}{cid}/index.m3u8'
            lines.append(full_url)
        
        with open("zz.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"✅ zz.m3u başarıyla oluşturuldu ({len(channel_ids)} kanal)")
        return 0
        
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {str(e)}")
        print("⚠️  Boş M3U dosyası oluşturuluyor...")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
















