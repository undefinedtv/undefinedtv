# Birleştirilecek dosya adları
dosya1 = 'legal.m3u'
dosya2 = 'selcuk.m3u'
cikis_dosyasi = 'karisik.m3u'

# M3U dosyalarının içeriğini oku
def oku_m3u(dosya_adi):
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        return [satir.strip() for satir in f if satir.strip()]

# İçerikleri oku
icerik1 = oku_m3u(dosya1)
icerik2 = oku_m3u(dosya2)

# Birleştir
birlesik_icerik = icerik1 + icerik2

# Yeni dosyaya yaz
with open(cikis_dosyasi, 'w', encoding='utf-8') as f:
    #f.write('#EXTM3U\n')  # Başlık
    for satir in birlesik_icerik:
        print(f"satır okunuyor")
        f.write(satir + '\n')

print(f"{cikis_dosyasi} dosyası başarıyla oluşturuldu.")
