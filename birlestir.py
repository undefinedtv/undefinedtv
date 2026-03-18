from github import Github

# GitHub Token
TOKEN = "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"
REPO = "undefinedtv/undefined_tv"
HEDEF_DOSYA = "test.m3u"

# Birleştirilecek dosya adları
empty = 'empty.m3u'
karsilasmalar = 'karsilasmalar.m3u'
rec = 'rec.m3u'
rec2 = 'rec2.m3u'
inattv = 'inattv.m3u'
selcuk = 'selcuk.m3u'
andro = 'androtv.m3u'
tabii = 'tabii.m3u'
yeni = 'yeni.m3u'
vavoo = 'vavoo.m3u'
atom = 'atom.m3u'
zz = 'zz.m3u'
gold = 'gold.m3u'
xsportv = 'xsportv.m3u'

# M3U dosyalarının içeriğini oku
def oku_m3u(dosya_adi):
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        return [satir.strip() for satir in f if satir.strip()]

# İçerikleri oku
empty_icerik = oku_m3u(empty)
karsilasmalar_icerik = oku_m3u(karsilasmalar)
rec_icerik = oku_m3u(rec)
rec2_icerik = oku_m3u(rec2)
inattv_icerik = oku_m3u(inattv)
selcuk_icerik = oku_m3u(selcuk)
andro_icerik = oku_m3u(andro)
tabii_icerik = oku_m3u(tabii)
yeni_icerik = oku_m3u(yeni)
vavoo_icerik = oku_m3u(vavoo)
atom_icerik = oku_m3u(atom)
zz_icerik = oku_m3u(zz)
gold_icerik = oku_m3u(gold)
xsportv_icerik = oku_m3u(xsportv)

# Birleştir
birlesik_icerik = (
    empty_icerik + karsilasmalar_icerik + zz_icerik +
    atom_icerik + andro_icerik + selcuk_icerik + xsportv_icerik + gold_icerik +
    tabii_icerik 
)

# GitHub'a yaz
g = Github(TOKEN)
repo = g.get_repo(REPO)

yeni_icerik_str = '\n'.join(birlesik_icerik) + '\n'

try:
    # Dosya zaten varsa güncelle
    mevcut = repo.get_contents(HEDEF_DOSYA)
    repo.update_file(
        path=HEDEF_DOSYA,
        message="test.m3u güncellendi",
        content=yeni_icerik_str,
        sha=mevcut.sha,
        branch="main"
    )
    print(f"✅ {HEDEF_DOSYA} güncellendi.")
except Exception:
    # Dosya yoksa oluştur
    repo.create_file(
        path=HEDEF_DOSYA,
        message="test.m3u oluşturuldu",
        content=yeni_icerik_str,
        branch="main"
    )
    print(f"✅ {HEDEF_DOSYA} oluşturuldu.")
