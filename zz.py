import requests
import re
import os
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# SSL uyarılarını gizle (verify=False kullanıldığında)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KONFIGÜRASYON ---
BASE_DOMAIN_PATTERN = "zeustv{}.cfd"   # Ana desen
ALT_DOMAIN_PATTERN = "zeus{}.cfd"      # Alternatif desen
START_INDEX = 269
END_INDEX = 300
REQUEST_TIMEOUT = 10                   # Daha uzun timeout
MASTER_M3U_FILENAME = "zz.m3u"

# Güncel kanal ID listesi (JSON'dan alındı)
CHANNEL_IDS = [
    'b1', 'b1local', 'b2', 'b3', 'b4', 'bein5', 'b1max', 'b2max',
    's1', 's2', 'smart1', 'smart2', 'tivibu', 'tivibu1', 'tivibu2', 'tivibu3',
    'xtrtspor', 'trtyildiz', 'xtrt1', 'xaspor', 'xatv', 'xtv8', 'xtv85',
    'sifirtv', 'euro1', 'euro2', 'tabiispor', 'tabii1', 'tabii2', 'tabii3',
    'tabii4', 'tabii5', 'tabii6', 'xexxen', 'xexxen1', 'tabiiyedek',
    'trt1yedek', 'xahaber', 'tv100'
]

# HTTP başlıkları
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
    'Referer': 'https://www.google.com/'
}

def log(message, level="INFO"):
    """Basit loglama fonksiyonu"""
    print(f"[{level}] {message}")

def get_session():
    """Yeniden deneme özellikli bir HTTP oturumu oluşturur."""
    session = requests.Session()
    retry = Retry(
        total=3,                    # Toplam 3 deneme
        backoff_factor=1,           # Denemeler arası bekleme (1, 2, 4 sn)
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]     # Sadece GET isteklerinde tekrar dene
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(HEADERS) # Oturuma başlıkları ekle
    return session

def get_base_url_from_page(session, active_domain, channel_id='b1'):
    page_url = f"{active_domain}/ch.html?id={channel_id}"
    log(f"Sayfa kaynağı inceleniyor: {page_url}", "DEBUG")
    try:
        response = session.get(page_url, timeout=REQUEST_TIMEOUT, verify=False)
        log(f"HTTP Durum Kodu: {response.status_code}", "DEBUG")
        response.raise_for_status()
        html_content = response.text

        # Regex: streamUrl değişkeninin değerini bul
        match = re.search(r'var\s+streamUrl\s*=\s*["\']([^"\']+)["\']', html_content)

        if match:
            base_video_url = match.group(1).strip()
            if not base_video_url.endswith('/'):
                base_video_url += '/'
            log(f"✅ Çözülen URL: {base_video_url}", "SUCCESS")
            return base_video_url
        else:
            # Alternatif: Sayfadaki herhangi bir http URL'sini yakala
            log("Regex eşleşmedi, alternatif tarama yapılıyor...", "WARNING")
            alt_match = re.search(r'https?://[^\s"\']+/', html_content)
            if alt_match:
                base_video_url = alt_match.group(0)
                if not base_video_url.endswith('/'):
                    base_video_url += '/'
                log(f"✅ Alternatif yöntemle bulundu: {base_video_url}", "SUCCESS")
                return base_video_url
            else:
                log("❌ Sayfa kaynağında hiçbir URL bulunamadı.", "ERROR")
                return None

    except requests.exceptions.SSLError as e:
        log(f"SSL Hatası: {e}", "ERROR")
        return None
    except requests.exceptions.ConnectionError as e:
        log(f"Bağlantı Hatası: {e}", "ERROR")
        return None
    except requests.exceptions.Timeout as e:
        log(f"Zaman Aşımı: {e}", "ERROR")
        return None
    except requests.exceptions.RequestException as e:
        log(f"Genel İstek Hatası: {e}", "ERROR")
        return None
    except Exception as e:
        log(f"Beklenmeyen Hata: {e}", "ERROR")
        return None

def find_working_domain_and_url(session):
    log(f"Domain taraması başlıyor: {BASE_DOMAIN_PATTERN.format(START_INDEX)} - {BASE_DOMAIN_PATTERN.format(END_INDEX)}", "INFO")
    log(f"Ayrıca alternatif desen: {ALT_DOMAIN_PATTERN.format(START_INDEX)} - {ALT_DOMAIN_PATTERN.format(END_INDEX)}", "INFO")

    patterns = [BASE_DOMAIN_PATTERN, ALT_DOMAIN_PATTERN]

    for pattern in patterns:
        log(f"--- Desen deneniyor: {pattern} ---", "INFO")
        for i in range(START_INDEX, END_INDEX + 1):
            domain = pattern.format(i)
            url = f"https://{domain}"
            log(f"Test ediliyor: {url}", "DEBUG")

            try:
                response = session.get(url + "/", timeout=REQUEST_TIMEOUT, allow_redirects=True, verify=False)
                status = response.status_code
                log(f"  -> HTTP {status}", "DEBUG")

                if status == 200:
                    log(f"✅ Aktif domain bulundu: {url}", "SUCCESS")
                    base_video_url = get_base_url_from_page(session, url, 'b1')

                    if base_video_url:
                        log(f"🎯 Kullanılacak domain: {url}, Base URL: {base_video_url}", "SUCCESS")
                        return url, base_video_url
                    else:
                        log(f"⚠️ Domain aktif ({url}) fakat streamUrl alınamadı. Sonraki domaine geçiliyor...", "WARNING")
                else:
                    log(f"ℹ️ {url} durum kodu: {status} (atlanıyor)", "DEBUG")

            except requests.exceptions.SSLError as e:
                log(f"SSL Hatası ({url}): {e}", "WARNING")
            except requests.exceptions.ConnectionError as e:
                log(f"Bağlantı Hatası ({url}): {e}", "DEBUG")
            except requests.exceptions.Timeout:
                log(f"Timeout ({url})", "DEBUG")
            except Exception as e:
                log(f"Beklenmeyen Hata ({url}): {e}", "DEBUG")

    log("❌ Hiçbir aktif domain bulunamadı.", "ERROR")
    return None, None

def create_master_m3u(base_video_url):
    log(f"'{MASTER_M3U_FILENAME}' dosyası oluşturuluyor...", "INFO")
    try:
        with open(MASTER_M3U_FILENAME, 'w', encoding='utf-8') as f:
            f.write("\n")
            for channel_id in CHANNEL_IDS:
                stream_url = f"{base_video_url}{channel_id}/index.txt"
                channel_name = channel_id.upper()
                f.write(f'#EXTINF:-1 group-title="Zeus Tv", {channel_name}\n')
                f.write(f'{stream_url}\n')
        log(f"✅ {MASTER_M3U_FILENAME} başarıyla oluşturuldu!", "SUCCESS")
    except Exception as e:
        log(f"❌ Dosya oluşturma hatası: {e}", "ERROR")

def main():
    log("🤖 Zeus TV M3U8 Botu Başlıyor...", "INFO")
    session = get_session()
    active_domain, base_video_url = find_working_domain_and_url(session)

    if not base_video_url:
        log("❌ Video base URL'si alınamadığı için işlem durduruldu.", "ERROR")
        return

    create_master_m3u(base_video_url)
    log("🚀 Tüm işlemler sorunsuz tamamlandı!", "SUCCESS")

if __name__ == "__main__":
    main()
