import requests
import re
import os

# --- KONFIGÜRASYON ---
BASE_DOMAIN_PATTERN = "zeustv{}.vip"
START_INDEX = 262
END_INDEX = 500
REQUEST_TIMEOUT = 5  
MASTER_M3U_FILENAME = "zz.m3u" 

CHANNEL_IDS = [
    'b1', 'b1local', 'b2', 'b3', 'b4', 'bein5', 'b1max', 'b2max',
    's1', 's2', 'smart1', 'smart2', 'tivibu', 'tivibu1', 'tivibu2', 'tivibu3',
    'sifirtv', 'euro1', 'euro2', 'tabiiyedek', 'tabii1', 'tabii2', 'tabii3',
    'tabii4', 'tabii5', 'tabii6', 'xexxen', 'xexxen1'
]

def get_base_url_from_page(active_domain, channel_id='b1'):
    page_url = f"{active_domain}/ch.html?id={channel_id}"
    print(f"  📄 Sayfa kaynağı inceleniyor: {page_url}")
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        html_content = response.text

        match = re.search(r'var\s+streamUrl\s*=\s*["\']([^"\']+)["\']', html_content)

        if match:
            base_video_url = match.group(1)
            if not base_video_url.endswith('/'):
                base_video_url += '/'
            print(f"    ✅ Çözülen URL: {base_video_url}")
            return base_video_url
        else:
            print("    ❌ Sayfa kaynağında URL bulunamadı.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"    ❌ Sayfaya erişilemedi: {e}")
        return None

def find_working_domain_and_url():
    print(f"🔍 {BASE_DOMAIN_PATTERN.format(START_INDEX)} ile {BASE_DOMAIN_PATTERN.format(END_INDEX)} arasında aktif domain taranıyor...")
    
    for i in range(START_INDEX, END_INDEX + 1):
        domain = BASE_DOMAIN_PATTERN.format(i)
        url = f"https://{domain}"
        
        try:
            response = requests.get(url + "/", timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if response.status_code == 200:
                print(f"\n✅ Aktif domain bulundu: {url}")
                base_video_url = get_base_url_from_page(url, 'b1')
                
                if base_video_url:
                    return url, base_video_url
                else:
                    print(f"  ⚠️ Domain aktif ama aranan kod yok! Bir sonraki domaine geçiliyor...\n")
            else:
                pass 
                
        except requests.ConnectionError:
            pass
        except requests.Timeout:
            pass
        except Exception:
            pass

    print("❌ Gerekli kodu içeren hiçbir aktif domain bulunamadı.")
    return None, None

def create_master_m3u(base_video_url):
    print(f"\n📋 '{MASTER_M3U_FILENAME}' dosyası sıfırdan oluşturuluyor...")
    try:
        with open(MASTER_M3U_FILENAME, 'w', encoding='utf-8') as f:
            f.write("\n")
            for channel_id in CHANNEL_IDS:
                stream_url = f"{base_video_url}{channel_id}/index.txt"
                channel_name = channel_id.upper()
                f.write(f'#EXTINF:-1 group-title="Zeus Tv", {channel_name}\n')
                f.write(f'{stream_url}\n')
                
        print(f"  ✅ {MASTER_M3U_FILENAME} başarıyla güncellendi/oluşturuldu!")
    except Exception as e:
        print(f"  ❌ {MASTER_M3U_FILENAME} oluşturulurken hata oluştu: {e}")

def main():
    print("🤖 Zeus TV M3U8 Botu Başlıyor...\n")

    active_domain, base_video_url = find_working_domain_and_url()
    
    if not base_video_url:
        print("❌ Video base URL'si alınamadığı için işlem durduruldu.")
        return
    
    create_master_m3u(base_video_url)
    
    print("\n🚀 Tüm işlemler sorunsuz tamamlandı!")

if __name__ == "__main__":
    main()
