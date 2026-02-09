import json
import base64
import asyncio
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import aiohttp
import os
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class InatBox:
    def __init__(self):
        self.aes_key = os.getenv("INAT_AES_KEY")
        self.main_page_url = os.getenv("INAT_MAIN_URL")
        self.worker_url = os.getenv("WORKER_URL")
        
    # ── Yardımcı Metodlar ─────────────────────────────────────────────

    @staticmethod
    def _try_decode_base64(text: str) -> str:
        """Base64 decode dener, başarısız olursa orijinal metni döner"""
        try:
            return base64.b64decode(text).decode('utf-8')
        except Exception:
            return text

    def _decrypt_aes(self, encrypted_data: str, key: str) -> str:
        """AES-128-CBC ile şifre çözer (IV = Key)"""
        try:
            key_bytes = key.encode('utf-8')
            if len(key_bytes) > 16:
                key_bytes = key_bytes[:16]
            elif len(key_bytes) < 16:
                key_bytes = key_bytes.ljust(16, b'\0')

            iv = key_bytes
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv)

            try:
                encrypted_bytes = base64.b64decode(encrypted_data.strip())
            except Exception as e:
                logger.error(f"Base64 decode hatası: {e}")
                return ""

            try:
                decrypted = cipher.decrypt(encrypted_bytes)
                try:
                    decrypted = unpad(decrypted, AES.block_size)
                except ValueError:
                    if len(decrypted) > 0:
                        pad_len = decrypted[-1]
                        if isinstance(pad_len, int) and 0 < pad_len <= AES.block_size:
                            if all(x == pad_len for x in decrypted[-pad_len:]):
                                decrypted = decrypted[:-pad_len]
                            else:
                                decrypted = decrypted.rstrip(b'\0')
                        else:
                            decrypted = decrypted.rstrip(b'\0')
            except Exception as e:
                logger.error(f"Decrypt hatası: {e}")
                return ""

            try:
                return decrypted.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return decrypted.decode('latin-1')
                except Exception:
                    return ""
        except Exception as e:
            logger.error(f"AES hatası: {e}")
            return ""

    def _decrypt_response(self, response: str, default_key: Optional[str] = None) -> Optional[str]:
        """İki katmanlı şifreli yanıtı çözer"""
        if default_key is None:
            default_key = self.aes_key

        try:
            response = response.strip()

            # ── Katman 1 ──
            last_colon = response.rfind(":")
            if last_colon != -1:
                cipher1 = response[:last_colon].strip()
                key1 = self._try_decode_base64(response[last_colon + 1:].strip())
            else:
                cipher1 = response
                key1 = default_key

            decrypted1 = self._decrypt_aes(cipher1, key1)
            if not decrypted1:
                return None

            # ── Katman 2 ──
            last_colon2 = decrypted1.rfind(":")
            if last_colon2 != -1:
                cipher2 = decrypted1[:last_colon2].strip()
                key2 = self._try_decode_base64(decrypted1[last_colon2 + 1:].strip())
                return self._decrypt_aes(cipher2, key2)
            else:
                return decrypted1

        except Exception as e:
            logger.error(f"Yanıt çözme hatası: {e}")
            return None

    # ── HTTP İstek ────────────────────────────────────────────────────

    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        url: str,
        key: Optional[str] = None
    ) -> Optional[str]:
        """Şifreli API'ye POST isteği atar ve çözülmüş yanıtı döner"""
        if key is None:
            key = self.aes_key

        try:
            parsed = urlparse(url)
            host = parsed.netloc
            if not host:
                logger.error(f"Geçersiz URL: {url}")
                return None

            body = f"1={key}&0={key}"

            headers = {
                "Cache-Control": "no-cache",
                "Content-Length": str(len(body)),
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": host,
                "Referer": "https://speedrestapi.com/",
                "X-Requested-With": "com.bp.box",
                "User-Agent": "speedrestapi"
            }
            
            request_url = f"{self.worker_url}{url}"
            async with session.post(
                request_url,
                headers=headers,
                data=body,
                timeout=aiohttp.ClientTimeout(total=60),
                ssl=False
            ) as resp:
                if resp.status == 200:
                    encrypted = await resp.text()
                    return self._decrypt_response(encrypted, default_key=key)
                else:
                    logger.error(f"HTTP {resp.status}")
                    return None

        except asyncio.TimeoutError:
            logger.error(f"Zaman aşımı")
            return None
        except Exception as e:
            logger.error(f"İstek hatası: {e}")
            return None

    # ── Kanal Verisi Parse ────────────────────────────────────────────

    @staticmethod
    def _parse_headers(ch_headers_raw) -> dict:
        """chHeaders alanından UserAgent ve Referer çıkarır"""
        user_agent = ""
        referer = ""

        try:
            # String olarak gelirse parse et
            if isinstance(ch_headers_raw, str):
                if ch_headers_raw in ("null", "", "[]"):
                    return {"user_agent": user_agent, "referer": referer}
                ch_headers_raw = json.loads(ch_headers_raw)

            # Liste ise ilk elemanı al
            if isinstance(ch_headers_raw, list) and len(ch_headers_raw) > 0:
                h = ch_headers_raw[0]
                user_agent = h.get("UserAgent", "")
                referer = h.get("Referer", "")
        except Exception:
            pass

        return {"user_agent": user_agent, "referer": referer}

    @staticmethod
    def _parse_regex1(ch_reg_raw) -> Optional[str]:
        """chReg alanından Regex1 (AES key) çıkarır"""
        try:
            if isinstance(ch_reg_raw, str):
                if ch_reg_raw in ("null", "", "[]"):
                    return None
                ch_reg_raw = json.loads(ch_reg_raw)

            if isinstance(ch_reg_raw, list) and len(ch_reg_raw) > 0:
                return ch_reg_raw[0].get("Regex1", None)
        except Exception:
            pass
        return None

    @staticmethod
    def _is_content_allowed(item: dict) -> bool:
        """link / web türlerini filtreler"""
        ch_type = item.get("chType", "")
        if ch_type in ("link", "web"):
            return False
        return True

    # ── M3U Üretimi ──────────────────────────────────────────────────

    async def generate_m3u(self):
        """Tüm kanalları çeker, stream URL'lerini alır ve inat.m3u olarak kaydeder"""

        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:

            # ── Adım 1: Ana kanal listesini al ──
            logger.info("Kanal listesi alınıyor...")
            request_url = f"{self.worker_url}{self.main_page_url}"
            json_response = await self._make_request(session, request_url)

            if not json_response:
                logger.error("Kanal listesi alınamadı!")
                return

            try:
                channels = json.loads(json_response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse hatası: {e}")
                return

            if not isinstance(channels, list):
                logger.error("Beklenen JSON array değil!")
                return

            total = len(channels)
            logger.info(f"Toplam {total} kanal bulundu")

            m3u_lines = ["#EXTM3U"]
            success_count = 0
            fail_count = 0

            # ── Adım 2: Her kanal için stream URL'sini al ──
            for idx, channel in enumerate(channels, start=1):

                # Filtre
                if not self._is_content_allowed(channel):
                    continue

                ch_name = channel.get("chName", "Unknown")
                ch_url = channel.get("chUrl", "")
                ch_img = channel.get("chImg", "")
                ch_headers_raw = channel.get("chHeaders", [])
                ch_reg_raw = channel.get("chReg", [])

                if not ch_url:
                    fail_count += 1
                    continue

                # VK düzeltme
                if ch_url.startswith("act"):
                    ch_url = f"https://vk.com/al_video.php?{ch_url}"

                # Header bilgilerini çıkar
                hdr = self._parse_headers(ch_headers_raw)
                user_agent = hdr["user_agent"]
                referer = hdr["referer"]

                # Regex1 key'i çıkar
                regex1_key = self._parse_regex1(ch_reg_raw)

                # Stream URL'yi al
                logger.info(f"[{idx}/{total}] → stream alınıyor...")

                stream_json = await self._make_request(session, ch_url, key=regex1_key)

                if not stream_json:
                    fail_count += 1
                    continue

                # Stream yanıtını parse et
                try:
                    # Bazen obje, bazen array gelebilir
                    stream_data = json.loads(stream_json)

                    if isinstance(stream_data, list):
                        # Array ise ilk elemanı al
                        if len(stream_data) == 0:
                            fail_count += 1
                            continue
                        stream_data = stream_data[0]

                    actual_url = stream_data.get("chUrl", "")

                    if not actual_url:
                        fail_count += 1
                        continue

                except json.JSONDecodeError:
                    fail_count += 1
                    continue

                # ── Adım 3: M3U satırını oluştur ──
                extinf = f'#EXTINF:-1 tvg-name="{ch_name}" tvg-logo="{ch_img}" group-title="Inat TV",{ch_name}'
                m3u_lines.append(extinf)

                if user_agent:
                    m3u_lines.append(f'#EXTVLCOPT:http-user-agent={user_agent}')
                if referer:
                    m3u_lines.append(f'#EXTVLCOPT:http-referrer={referer}')

                m3u_lines.append(actual_url)
                success_count += 1

            # ── Adım 4: Dosyaya kaydet ──
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "inat.m3u"
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(m3u_lines) + "\n")

            logger.info("")
            logger.info("=" * 55)
            logger.info(f"  M3U dosyası kaydedildi : {output_path}")
            logger.info(f"  Başarılı               : {success_count}")
            logger.info(f"  Başarısız              : {fail_count}")
            logger.info(f"  Toplam kanal           : {total}")
            logger.info("=" * 55)


# ── Giriş Noktası ────────────────────────────────────────────────────

async def main():
    provider = InatBox()
    await provider.generate_m3u()


if __name__ == "__main__":
    asyncio.run(main())
