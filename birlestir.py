# Birleştirilecek dosya adları
#goals = 'goals.m3u'
inattv = 'inattv.m3u'
selcuk = 'selcuk.m3u'
andro = 'androtv.m3u'
sabit = 'sabit.m3u'
yeni = 'yeni.m3u'
vavoo = 'vavoo.m3u'
cikis_dosyasi = 'karisik.m3u'

# M3U dosyalarının içeriğini oku
def oku_m3u(dosya_adi):
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        return [satir.strip() for satir in f if satir.strip()]

# İçerikleri oku
inattv_icerik = oku_m3u(inattv)
selcuk_icerik = oku_m3u(selcuk)
andro_icerik = oku_m3u(andro)
sabit_icerik = oku_m3u(sabit)
yeni_icerik = oku_m3u(yeni)
vavoo_icerik = oku_m3u(vavoo)

# Birleştir
birlesik_icerik = sabit_icerik + vavoo_icerik + inattv_icerik + selcuk_icerik + andro_icerik + yeni_icerik

# Yeni dosyaya yaz
with open(cikis_dosyasi, 'w', encoding='utf-8') as f:
    for satir in birlesik_icerik:
        f.write(satir + '\n')

print(f"{cikis_dosyasi} dosyası başarıyla oluşturuldu.")
