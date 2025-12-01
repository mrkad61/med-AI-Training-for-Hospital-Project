import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

# --- AYARLAR ---
MODEL_PATH = "./model"  # İndirdiğin model klasörünün yolu


def main():
    print("=================================================")
    print("   HASTANE YAPAY ZEKA ASİSTANI - LOCAL TEST")
    print("=================================================")

    # 1. Modeli ve Tokenizer'ı Yükle
    print(f"Model yükleniyor: {MODEL_PATH} ...")
    try:
        # Local CPU'da çalıştıracağız (Hızlı ve sorunsuz)
        device = torch.device("cpu")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        model.to(device)
        model.eval()  # Modeli 'Test Moduna' al (Dropout'u kapatır)
        print("Model başarıyla yüklendi! Hazır.\n")
    except Exception as e:
        print(f"HATA: Model yüklenemedi. Klasör yolunu kontrol et.\nDetay: {e}")
        return

    # 2. Etiket Listesi (Modelin içinden okuyoruz)
    id2label = model.config.id2label

    # 3. Sonsuz Döngü (Soru-Cevap)
    while True:
        text = input("\nŞikayetiniz nedir? (Çıkış için 'q'): ")

        if text.lower() == 'q':
            print("Çıkış yapılıyor...")
            break

        if not text.strip():
            continue

        # --- TAHMİN İŞLEMİ (INFERENCE) ---
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128).to(device)

        with torch.no_grad():  # Eğitim yapmadığımız için gradyan hesaplama (RAM tasarrufu)
            outputs = model(**inputs)

        logits = outputs.logits

        # Softmax: Ham puanları (Logits) yüzdeye çevirir (Toplamı 100 olacak şekilde)
        probs = F.softmax(logits, dim=1)[0]

        # En yüksek 3 tahmini al
        # torch.topk -> SQL'deki "TOP 3 ORDER BY Score DESC" gibidir
        top_probs, top_indices = torch.topk(probs, 3)

        # --- SONUÇLARI YAZDIR ---
        print("\n---------------------------------")
        print(f"Girdi: '{text}'")
        print("---------------------------------")

        for i in range(3):
            score = top_probs[i].item() * 100  # Yüzdeye çevir
            label_index = top_indices[i].item()
            label_name = id2label[label_index]

            # Görsellik: Güven oranına göre renkli bar veya işaret
            bar = "▓" * int(score / 5)  # Her %5 için bir blok

            print(f"{i + 1}. {label_name:<25} : %{score:.2f}  {bar}")

        # Karar Destek Mantığı (Senin istediğin Soru Sorma özelliği buraya entegre edilir)
        en_yuksek_skor = top_probs[0].item()
        if en_yuksek_skor < 0.60:
            print("\n⚠️  UYARI: Model tam emin olamadı. Hastaya ek soru sorulmalı.")
        else:
            print(f"\n✅ Yönlendirme: {id2label[top_indices[0].item()]}")


if __name__ == "__main__":
    main()