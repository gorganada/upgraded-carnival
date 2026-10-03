---
workflow: general-video
flow: automation
storyboard: no
message: "Claude bir soruyu parçalara ayırır, parçaların birbirine bakmasıyla anlar, düşünür, araç kullanır ve cevabı parça parça yazar."
destination: youtube
aspect: 1920x1080
language: tr
length: 36s
angle: concept
---

## Intent

"Claude'un beyni": Claude'un nasıl çalıştığını gösteren, After Effects tadında bir motion-graphics videosu.
Kullanıcının sözleriyle: "kendini video editör gibi düşün, beni şaşırtacak şeyler yap, Claude'un çalışma
şekli gibi beynini göster, yaratıcı olsun". Geçişler etkileyici olmalı (HyperFrames shader geçişleri).

Soru olarak, bu sohbetteki gerçek istek kullanılıyor: "Çanakkale Savaşı'nı 20 saniyede anlat."

## Customizations

- WebGL shader geçişleri (cinematic-zoom ana geçiş; gravitational-lens, glitch, light-leak vurgu).
- Kodla sentezlenmiş ses tasarımı (drone, klavye tıkları, whoosh, token "tık"ları, final akoru), sahne zamanlarına senkron.

## Notes

- Seslendirme yok; metin ekranda, Türkçe.
- Olasılık yüzdeleri ve token ID'leri temsilidir (gerçek model çıktısı değildir).
- CDN erişimi kapalı: GSAP ve shader-transitions `vendor/` altında yerel.
