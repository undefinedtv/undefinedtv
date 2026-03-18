import requests
import os
import re

OUTPUT_FILENAME = "gold.m3u"

def get_goldvod_m3u():
    """GoldVOD'dan m3u indirir, 'spor' group-title içeren kanalları Gold TV olarak kaydeder"""
    
    try:
        print("📡 GoldVOD kaynağından indiriliyor...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(
            "https://goldvod.site/get.php?username=hpgdisco&password=123456&type=m3u_plus",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        lines = response.text.split('\n')
        
        filtered_entries = []
        i = 0
        
        # İlk satır #EXTM3U başlığıysa atla
        if lines and lines[0].strip().startswith('#EXTM3U'):
            i = 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith(''):
                # group-title değerini kontrol et (büyük/küçük harf duyarsız)
                match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
                
                if match and 'spor' in match.group(1).lower():
                    # group-title değerini "Gold TV" ile değiştir
                    modified_line = re.sub(
                        r'group-title="[^"]*"',
                        'group-title="Gold TV"',
                        line,
                        flags=re.IGNORECASE
                    )
                    
                    # Sonraki satır URL olmalı
                    url_line = lines[i + 1].strip() if (i + 1) < len(lines) else ""
                    
                    if url_line and not url_line.startswith('#'):
                        filtered_entries.append(modified_line)
                        filtered_entries.append(url_line)
                        i += 2
                        continue
            
            i += 1
        
        if not filtered_entries:
            print("⚠️  'Spor' içeren kanal bulunamadı!")
            return False
        
        # Dosyayı yaz
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write('\n'.join(filtered_entries))
            f.write('\n')
        
        print(f"✅ {len(filtered_entries) // 2} spor kanalı bulundu.")
        print(f"✅ '{OUTPUT_FILENAME}' başarıyla oluşturuldu → {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


if __name__ == "__main__":
    get_goldvod_m3u()
