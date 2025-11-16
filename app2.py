from flask import Flask, render_template, request, jsonify
from transformers import pipeline

# --- 1. UYGULAMA VE MODELLERİN KURULUMU ---

app = Flask(__name__)

print("Hugging Face modeli yükleniyor...")
hf_classifier = pipeline("zero-shot-classification",
                         model="hazal/BioBERTurkcased-con-trM")
print("Hugging Face modeli yüklendi.")

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


# --- 3. WEB SAYFASI ROTALARI ---

@app.route("/")
def index():
    """Ana sayfayı yükler."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Sohbet mesajlarını işleyen ana fonksiyon.
    Artık sadece ilk mesajı alır, analiz eder ve en yüksek skoru döndürür.
    """
    user_message = request.json["message"]
    ai_response = ""


    # Doğrudan analiz yap
    scores = analyze_complaint(user_message)

    # En yüksek skorlu bölümü al
    top_department = scores[0][0]
    top_score = scores[0][1]  # Skoru da alabiliriz (isteğe bağlı)

    # Doğrudan sonucu döndür
    ai_response = f"Analizime göre şikayetiniz için en uygun bölüm **{top_department}** gibi görünüyor. (Güven Skoru: {top_score:.2f})"

    return jsonify({"response": ai_response})


if __name__ == "__main__":
    app.run(debug=True)