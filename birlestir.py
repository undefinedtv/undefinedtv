# Birleştirilecek dosya adları
goals = 'goals.m3u'
selcuk = 'selcuk.m3u'
andro = 'androtv.m3u'
tabii = 'tabii.m3u'
yeni = 'yeni.m3u'
cikis_dosyasi = 'karisik.m3u'

# M3U dosyalarının içeriğini oku
def oku_m3u(dosya_adi):
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        return [satir.strip() for satir in f if satir.strip()]

# İçerikleri oku
icerik1 = oku_m3u(goals)
icerik2 = oku_m3u(selcuk)
icerik3 = oku_m3u(andro)
icerik4 = oku_m3u(tabii)
icerik5 = oku_m3u(yeni)

# Birleştir
birlesik_icerik = icerik1 + icerik2 + icerik3 + icerik4 + icerik5

# Yeni dosyaya yaz
with open(cikis_dosyasi, 'w', encoding='utf-8') as f:
    for satir in birlesik_icerik:
        f.write(satir + '\n')

print(f"{cikis_dosyasi} dosyası başarıyla oluşturuldu.")
