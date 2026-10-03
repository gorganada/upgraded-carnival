# Seslendirme metinleri (ElevenLabs)

Her satırın zamanı videodaki ekrana denk gelir. Satırları ayrı ayrı üretip ilgili saniyeye yerleştirmek en temiz sonucu verir.
Öneri: Türkçe için `eleven_multilingual_v2` (ya da v3), sıcak ve gülümseyen bir ses; stability ≈ 0.45, style ≈ 0.3.
Videolardaki müzik seslendirme için alan bırakacak seviyede; konuşma sırasında müziği 6–8 dB kısmak yeterli.

"Boyama Kitabım" yer tutucu marka adıdır; gerçek markanla değiştir.

## Reklam 1 — Fotoğraftan Sayfaya (15 sn)

| Zaman | Metin |
|---|---|
| 0.2 – 2.2 | Bu, sıradan bir fotoğraf. |
| 2.5 – 5.5 | Ama biz onu… çocuğunuza özel bir boyama sayfasına dönüştürüyoruz. |
| 5.9 – 10.8 | Şimdi sıra onda: kendi fotoğrafını, kendi renkleriyle boyuyor. |
| 11.7 – 14.8 | Boyama Kitabım. Fotoğrafınızı yükleyin, kitabı kapınıza gelsin. |

## Reklam 2 — Kahraman Sensin (15 sn)

| Zaman | Metin |
|---|---|
| 0.1 – 2.8 | Bu kitabın kahramanı… sizin çocuğunuz! |
| 3.2 – 6.8 | Kapağında onun adı, her sayfasında kendisi. |
| 7.0 – 11.0 | Ay'a gidiyor, dinozora biniyor, hazine buluyor. |
| 11.7 – 14.8 | İsmi, yüzü, hikâyesi: ona özel. Boyama Kitabım. |

## Reklam 3 — 3 Adımda Hediye (15 sn)

| Zaman | Metin |
|---|---|
| 0.1 – 2.6 | Doğum günü hediyesi mi arıyorsunuz? |
| 3.0 – 5.3 | Bir: fotoğrafınızı yükleyin. |
| 5.6 – 7.8 | İki: hikâyeyi seçin. |
| 8.1 – 10.1 | Üç: kitap kapınıza gelsin. |
| 10.5 – 14.8 | Unutulmaz bir hediye. Boyama Kitabım'da hemen oluşturun. |

## Kişiselleştirme

Her reklamda çocuğun adı ve marka değişken olarak tanımlı. Örnek:

```bash
cd reklam-2
npx hyperframes render --variables '{"marka":"Minik Ressam","cocuk_iyelik":"Deniz'in"}' -o ../renders/reklam-2-deniz.mp4
```

Değişkenler: `marka`, `cocuk`, `cocuk_iyelik` (Ela'nın), `cocuk_yonelme` (Ela'ya, sadece reklam 3), `evcil` (sadece reklam 1).
Ortak dosyaları (`ortak/`) değiştirdikten sonra `./sync.sh` çalıştır; sesleri yeniden üretmek için `python3 tools/muzik.py`.
