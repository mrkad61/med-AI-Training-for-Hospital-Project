from flask import Flask, render_template, request, jsonify, session
from transformers import pipeline
import google.generativeai as genai

# --- 1. UYGULAMA VE MODELLERİN KURULUMU ---

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-session'

print("Hugging Face modeli yükleniyor...")
hf_classifier = pipeline("zero-shot-classification",
                         model="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
print("Hugging Face modeli yüklendi.")

# Gemini API anahtarını yapılandır
try:
    genai.configure(api_key="GEMİNİ_API_KEY_BURAYA")
    gemini_model = genai.GenerativeModel('gemini-pro')
    print("Gemini modeli başarıyla yapılandırıldı.")
except Exception as e:
    print(f"Gemini yapılandırma hatası: {e}")
    gemini_model = None

# Hastanemizdeki bölümler (etiketler)
BOLUM_ETIKETLERI = [
    "Kardiyoloji (Kalp ve Damar Hastalıkları)",
    "Dahiliye (Mide, Bağırsak ve İç Hastalıkları)",
    "Göğüs Hastalıkları (Akciğer ve Solunum)",
    "Nöroloji (Beyin ve Sinir Sistemi)",
    "Ortopedi (Kemik ve Eklem Hastalıkları)",
    "Kulak Burun Boğaz",
    "Psikiyatri (Ruh Sağlığı)",
    "Dermatoloji (Cilt Hastalıkları)"
]


# --- 2. YARDIMCI FONKSİYONLAR ---

def analyze_complaint(text):
    """Hugging Face modelini kullanarak metni analiz eder ve skorları döndürür."""
    print(f"Analiz ediliyor: '{text}'")
    results = hf_classifier(text, BOLUM_ETIKETLERI, multi_label=True)

    sorted_scores = sorted(zip(results['labels'], results['scores']), key=lambda x: x[1], reverse=True)
    print(f"Analiz sonuçları: {sorted_scores}")
    return sorted_scores


def ask_clarifying_question(complaint, top_departments):
    """Gemini modelini kullanarak belirsizliği giderecek bir soru sorar."""
    if not gemini_model:
        return "Üzgünüm, şu an ek soru soramıyorum. Lütfen şikayetinizi biraz daha detaylandırın."


    prompt = f"""
    Bir hastanın şikayeti şu: "{complaint}"
    İlk analizime göre bu durum şu bölümlerle ilgili olabilir: {', '.join(top_departments)}.
    Bu bölümleri birbirinden ayırt etmek için hastaya sorulacak, basit ve net, 'evet/hayır' veya kısa cevaplı TEK BİR TANE soru oluştur.
    Sadece soruyu yaz. Örneğin: 'Ağrınız hareket edince artıyor mu?' gibi.
    """
    print("Gemini'ye soru sorması için istek gönderiliyor...")
    try:
        response = gemini_model.generate_content(prompt)
        question = response.text
        print(f"Gemini'nin ürettiği soru: {question}")
        return question
    except Exception as e:
        print(f"Gemini hatası: {e}")
        return "Şikayetinizi daha iyi anlamam için biraz daha detay verebilir misiniz?"


# --- 3. WEB SAYFASI ROTALARI ---

@app.route("/")
def index():
    """Ana sayfayı yükler ve sohbet geçmişini temizler."""
    session.clear()  # Her yeni ziyarette oturumu temizle
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Sohbet mesajlarını işleyen ana fonksiyon."""
    user_message = request.json["message"]


    if 'initial_complaint' in session:
        # Eski şikayet ile yeni cevabı birleştir
        full_context = session['initial_complaint'] + ". Sorduğunuz soruya cevabım: " + user_message
        session.clear()  # Döngüyü bitir, oturumu temizle

        scores = analyze_complaint(full_context)
        top_department = scores[0][0]
        ai_response = f"Verdiğiniz ek bilgi için teşekkürler. Değerlendirmeme göre **{top_department}** bölümünden randevu almanız en uygunu olacaktır."


    else:
        session['initial_complaint'] = user_message
        scores = analyze_complaint(user_message)

        top_score = scores[0][1]
        second_score = scores[1][1]

        # KARAR MOTORU: Skorlar net mi, yoksa belirsiz mi?
        # Eğer en yüksek skor 0.85'ten büyükse veya ikinci skordan 0.25'ten fazla fark varsa, durumu net kabul et.
        if top_score > 0.85 and (top_score - second_score) > 0.25:
            top_department = scores[0][0]
            ai_response = f"Anladığım kadarıyla şikayetiniz için en uygun bölüm **{top_department}** gibi görünüyor. Dilerseniz bu bölümden randevu alabilirsiniz."
            session.clear()  # İşlem bitti, oturumu temizle
        else:
            # Durum belirsiz, Gemini'ye soru sordur.
            ambiguous_departments = [scores[0][0], scores[1][0]]
            ai_response = ask_clarifying_question(user_message, ambiguous_departments)

    return jsonify({"response": ai_response})



if __name__ == "__main__":
    app.run(debug=True)