// Shared end card: book mockup + brand + CTA. Call ENDCARD.build(container, {title, brand, sub, cta}) at setup,
// ENDCARD.animate(tl, prefix, at) to add its entrance.
(function () {
  function build(el, o) {
    el.innerHTML =
      '<div class="book" id="' + o.p + '-book"><div class="spine"></div><div class="ttl" id="' + o.p + '-ttl"></div>' +
      '<svg width="460" height="470" viewBox="-230 -150 460 470">' + ART.kid(o.p + "-kid") + "</svg></div>" +
      '<div class="brand" id="' + o.p + '-brand"></div><div class="sub" id="' + o.p + '-sub"></div><div class="cta" id="' + o.p + '-cta"></div>';
    document.getElementById(o.p + "-ttl").textContent = o.title;
    document.getElementById(o.p + "-brand").textContent = o.brand;
    document.getElementById(o.p + "-sub").textContent = o.sub;
    document.getElementById(o.p + "-cta").textContent = o.cta;
    ART.paint(el.querySelector(".book svg"));
  }
  function animate(tl, p, at) {
    tl.fromTo("#" + p + "-book", { y: 160, rotation: -10, scale: 0.8, opacity: 0 }, { y: 0, rotation: -3, scale: 1, opacity: 1, duration: 0.8, ease: "back.out(1.6)" }, at);
    tl.fromTo("#" + p + "-brand", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }, at + 0.35);
    tl.fromTo("#" + p + "-sub", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }, at + 0.55);
    tl.fromTo("#" + p + "-cta", { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.55, ease: "back.out(2.4)" }, at + 0.8);
    tl.fromTo("#" + p + "-cta", { scale: 1 }, { scale: 1.07, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: 3 }, at + 1.5);
    tl.fromTo("#" + p + "-book", { rotation: -3 }, { rotation: 2, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: 1 }, at + 0.8);
  }
  window.ENDCARD = { build: build, animate: animate };
})();
