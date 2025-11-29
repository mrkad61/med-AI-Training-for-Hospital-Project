# med-AI-Training-for-Hospital-Project

## Projede Yapılacak İşlerin Sıralaması Şu şekildedir
#### 1.Fine-Tune edilecek ve projeye en uygun hazır bir model belirlemek.
#### 2.Seçilen model için veri seti hazırlamak
#### 3.Modeli eğitip gerçek uygulamada performansını test etmek.

## 1. Fine-Tune edliecek ve projeye en uygun hazır bir model belirlemek.

Bu aşamada bir kaç model üzerinde durdum ve en son BioBERTurk modeli üzerinde durdum. Bu model Türkçe tıbbi makaleler ile BERTurk modeli eğitilerek geliştirilmiş. Bende bu modeli Text-Classification yapabilmek için tekrardan eğitmeye karar verdim.

## 2. Seçilen model için veri seti hazırlamak

https://www.doktorsitesi.com sitesi üzerinden bölüm bazında yazılan hasta şikayetlerini yazdığım python script'i ile otomatik olarak çekiyorum. Yaklaşık 10 bölüm için var olan verileri toplayacağım. Hesaplarıma göre 300.000+ etiketli veri ile modeli eğitmeyi düşünüyorum.

## 3.Modeli eğitip gerçek uygulamada performansını test etmek.

Bu aşamada en önemli kısım nasıl eğitileceği. Veri toplama aşamasında gördüğüm kadarıyla veri seti dengesiz olacak. Bu yüzden Ağırlıklı Hesaplama mantığını kullanacağım. Böylece modelin az veriye sahip etiketleride aynı oranda dikkate almasını sağlamak istiyorum. Modeli eğitmeye başladıktan sonra performansına göre metotlarımı geliştirecek/değiştireceğim.
