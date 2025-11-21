import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- 1. AYARLAR BÖLÜMÜ ---
BOLUM_ADI = "Beyin ve Sinir Cerrahisi"
BASE_URL = "https://www.doktorsitesi.com/blog/sorular/beyin-ve-sinir-cerrahisi"

BASLANGIC_SAYFASI = 1
BITIS_SAYFASI = 450

# Her liste sayfası arasında bekleyeceğimiz min/max saniye
LISTE_BEKLEME_MIN = 4
LISTE_BEKLEME_MAX = 8

# Her bir soru detayına girerken bekleyeceğimiz min/max saniye
DETAY_BEKLEME_MIN = 1
DETAY_BEKLEME_MAX = 2

# İnsan Taklidi için Tarayıcı Kimlikleri
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
]


# ---------------------------------

def get_question_detail(session, question_url):
    """
    (AŞAMA 2) Soru detay sayfasına girer ve sorunun tam metnini çeker.
    """
    try:
        # Rastgele bir tarayıcı kimliği seç
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

        # Detay sayfasına istek at
        response = session.get(question_url, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Tam metnin bulunduğu div'in class'ı güncellendi.
            question_div = soup.find('div', class_='prose prose-lg max-w-none mb-6 text-gray-700')

            if question_div:
                return question_div.get_text(strip=True)
            else:
                print(f"   [Detay Hatası] Soru metni div'i ('prose prose-lg...') bulunamadı. URL: {question_url}")
                return None
        else:
            print(f"   [Detay Hatası] Soru sayfası açılamadı. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"   [Detay Hatası] Detay çekilirken hata: {e}")
        return None


def veri_cekme_islemini_baslat():
    """(AŞAMA 1) Liste sayfalarını gezen ve detayları toplayan ana fonksiyon."""

    toplanan_veriler = []

    with requests.Session() as session:

        print(f"'{BOLUM_ADI}' bölümü için veri çekme işlemi başlıyor...")
        print(f"Sayfa {BASLANGIC_SAYFASI} ile {BITIS_SAYFASI} arası çekilecek...")
        print("-" * 40)

        for sayfa_numarasi in range(BASLANGIC_SAYFASI, BITIS_SAYFASI + 1):

            session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

            url = f"{BASE_URL}?sayfa={sayfa_numarasi}"
            print(f"[Sayfa {sayfa_numarasi}] Çekiliyor... URL: {url}")

            try:
                response = session.get(url, timeout=15)

                if response.status_code != 200:
                    print(f"[HATA] Liste sayfası çekilemedi. Status Code: {response.status_code}")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')

                # Her bir soru kartını (article) bul
                soru_kartlari = soup.find_all('article', class_='bg-white border border-[#E6E9EE] rounded-md overflow-hidden transition-all duration-300 ease-in-out shadow-sm hover:border-primary hover:-translate-y-0.5 hover:shadow-lg p-4 w-full')

                if not soru_kartlari:
                    print(f"[Sayfa {sayfa_numarasi}] Bu sayfada soru kartı ('article') bulunamadı. İşlem durduruluyor.")
                    break

                print(f"[Sayfa {sayfa_numarasi}] {len(soru_kartlari)} adet soru kartı bulundu. Detaylar çekiliyor...")

                for kart in soru_kartlari:
                    # --- DÜZELTME (SİZİN BULGUNUZA GÖRE) ---
                    # H2 (Başlık) linki yerine "Yanıtı Gör" butonunun linkini bul.
                    link_etiketi = kart.find('a', class_='text-xs text-white bg-primary px-2.5 py-1.5 rounded-md')

                    if not link_etiketi or not link_etiketi.has_attr('href'):
                        print("   [Hata] Kart içinde 'Yanıtı Gör' linki bulunamadı, atlanıyor.")
                        continue

                    # Linkin 'href' özelliğini al (örn: /blog/soru/sackiran-4/...)
                    relative_url = link_etiketi.get('href')

                    # Linkin sonundaki "#first-answer" kısmını temizle
                    if '#' in relative_url:
                        relative_url = relative_url.split('#')[0]

                    # Tam URL'yi oluştur (örn: https://www.doktorsitesi.com/...)
                    full_question_url = requests.compat.urljoin(BASE_URL, relative_url)

                    # --- ETİK KURAL 2 ---
                    # Her bir soru detayına girmeden önce rastgele bekle
                    bekleme = random.uniform(DETAY_BEKLEME_MIN, DETAY_BEKLEME_MAX)
                    print(f"   Detay için {bekleme:.1f} sn bekleniyor... URL: {relative_url[:50]}...")
                    time.sleep(bekleme)

                    # AŞAMA 2'yi çağır: Detay sayfasına git ve tam metni al
                    tam_soru_metni = get_question_detail(session, full_question_url)

                    if tam_soru_metni:
                        toplanan_veriler.append({
                            "text": tam_soru_metni,
                            "label": BOLUM_ADI
                        })

            except requests.exceptions.RequestException as e:
                print(f"[HATA] Sayfa {sayfa_numarasi} çekilirken bir ağ hatası oluştu: {e}")
                print("İşlem durduruluyor.")
                break

                # --- ETİK KURAL 1 ---
            # Bir sonraki liste sayfasına geçmeden önce UZUN ve RASTGELE bekle
            if sayfa_numarasi < BITIS_SAYFASI:
                bekleme = random.uniform(LISTE_BEKLEME_MIN, LISTE_BEKLEME_MAX)
                print(f"[Sayfa {sayfa_numarasi}] Tamamlandı. Bir sonraki sayfa için {bekleme:.1f} saniye bekleniyor...")
                print("-" * 30)
                time.sleep(bekleme)

    print("-" * 40)
    print("Veri çekme işlemi tamamlandı.")

    if not toplanan_veriler:
        print("Hiç veri toplanamadı.")
        return

    print("Veriler CSV dosyasına dönüştürülüyor...")

    df = pd.DataFrame(toplanan_veriler)
    dosya_adi = f"{BOLUM_ADI.lower().replace(' ', '_')}_{BASLANGIC_SAYFASI}-{BITIS_SAYFASI}.csv"

    df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')

    print(f"İşlem BAŞARILI! Toplam {len(df)} adet tam soru metni '{dosya_adi}' dosyasına kaydedildi.")


if __name__ == "__main__":
    veri_cekme_islemini_baslat()