import re
import sys
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urljoin
from playwright.sync_api import sync_playwright

# Constants
JUSTINTV_DOMAIN = "https://tvjustin.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
FIXED_GROUP_TITLE = "Maç Yayınları"

def adjust_time_in_text(text, hours_to_add=5):
    """Finds HH:MM patterns in text and adds specified hours."""
    def time_replacer(match):
        time_str = match.group(0)
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            new_time = time_obj + timedelta(hours=hours_to_add)
            return new_time.strftime("%H:%M")
        except ValueError:
            return time_str

    return re.sub(r'\d{2}:\d{2}', time_replacer, text)

def scrape_default_channel_info(page):
    try:
        page.goto(JUSTINTV_DOMAIN, timeout=25000, wait_until='domcontentloaded')
        iframe_selector = "iframe#customIframe"
        page.wait_for_selector(iframe_selector, timeout=15000)
        iframe_element = page.query_selector(iframe_selector)
        if not iframe_element: return None, None
        
        iframe_src = iframe_element.get_attribute('src')
        event_url = urljoin(JUSTINTV_DOMAIN, iframe_src)
        parsed_event_url = urlparse(event_url)
        query_params = parse_qs(parsed_event_url.query)
        stream_id = query_params.get('id', [None])[0]
        return event_url, stream_id
    except Exception:
        return None, None

def extract_base_m3u8_url(page, event_url):
    try:
        page.goto(event_url, timeout=20000, wait_until="domcontentloaded")
        content = page.content()
        base_url_match = re.search(r"['\"](https?://[^'\"]+/checklist/)['\"]", content)
        return base_url_match.group(1) if base_url_match else None
    except Exception:
        return None

def is_link_working(url):
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": JUSTINTV_DOMAIN,
        "Origin": JUSTINTV_DOMAIN.rstrip('/')
    }
    try:
        response = requests.head(url, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def scrape_all_channels(page):
    print(f"\n📡 Collecting channels from {JUSTINTV_DOMAIN}...")
    channels = []
    seen_ids = set()
    
    try:
        page.goto(JUSTINTV_DOMAIN, timeout=45000, wait_until='networkidle')
        page.wait_for_timeout(3000)
        channel_elements = page.query_selector_all(".mac[data-url]")
        
        for element in channel_elements:
            data_url = element.get_attribute('data-url')
            if not data_url: continue
            
            parsed_data_url = urlparse(data_url)
            stream_id = parse_qs(parsed_data_url.query).get('id', [None])[0]
            
            if stream_id and stream_id not in seen_ids:
                name_element = element.query_selector(".takimlar")
                channel_name = name_element.inner_text().replace('CANLI', '').strip() if name_element else "Unknown"
                
                time_element = element.query_selector(".saat")
                time_str = time_element.inner_text().strip() if time_element else ""
                
                # Apply the +5 hours offset and format the title with time first
                if time_str and time_str != "CANLI":
                    adjusted_time = adjust_time_in_text(time_str, 5)
                    final_name = f"[{adjusted_time}] {channel_name}"
                else:
                    final_name = channel_name
                
                channels.append({
                    'name': final_name,
                    'id': stream_id
                })
                seen_ids.add(stream_id)

        # Sort alphabetically (which now effectively sorts by time for match entries)
        channels.sort(key=lambda x: x['name'])
        return channels
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        default_event_url, _ = scrape_default_channel_info(page)
        if not default_event_url: 
            sys.exit(1)

        base_m3u8_url = extract_base_m3u8_url(page, default_event_url)
        if not base_m3u8_url: 
            sys.exit(1)

        channels = scrape_all_channels(page)
        
        output_filename = "karsilasmalar.m3u"
        count = 0
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")
            
            for c in channels:
                stream_url = f"{base_m3u8_url}{c['id']}.m3u8"
                
                print(f"🔍 Validating: {c['name']}...", end=" ", flush=True)
                
                if is_link_working(stream_url):
                    print("✅ 200 OK")
                    f.write(f'#EXTINF:-1 tvg-name="{c["name"]}" group-title="{FIXED_GROUP_TITLE}",{c["name"]}\n')
                    f.write(f"#EXT-X-USER-AGENT:{USER_AGENT}\n")
                    f.write(f"#EXT-X-REFERER:{JUSTINTV_DOMAIN}\n")
                    f.write(f"#EXT-X-ORIGIN:{JUSTINTV_DOMAIN.rstrip('/')}\n")
                    f.write(f"{stream_url}\n\n")
                    count += 1
                else:
                    print("❌ Offline")
        
        print(f"\n✅ Finished! {count} live channels saved. Format: [TIME] NAME.")
        browser.close()

if __name__ == "__main__":
    main()
