// Line-art library for the coloring-book ads.
// Every colorable shape gets class "rg" and data-c="<crayon color>". In line mode its fill is paper white;
// in color mode it is painted with data-c. Ink details (eyes, mouth) are never colorable.
(function () {
  var INK = "#231c18", PAPER = "#fffdf8";
  var C = { skin: "#f6c9a4", hair: "#7a4a2b", shirt: "#3f88c5", star: "#f6c445", cheek: "#f49cbb", dog: "#f3e3c3", ear: "#c98b55",
    grass: "#7cc46b", sky: "#bfe3f7", sun: "#f6c445", suit: "#e8eef4", helmet: "#cfe9f9", rocket: "#e94f37", fin: "#3f88c5",
    flame: "#f6a13a", planet: "#a77bd6", ring: "#f49cbb", dino: "#44bba4", plate: "#f6c445", chest: "#b0703a", gold: "#f6c445", bandana: "#e94f37" };

  function rg(tag, attrs, color, id) {
    var s = "<" + tag + ' class="rg" data-c="' + color + '"' + (id ? ' id="' + id + '"' : "");
    for (var k in attrs) s += " " + k + '="' + attrs[k] + '"';
    return s + ' fill="' + PAPER + '" stroke="' + INK + '" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>';
  }
  function ink(tag, attrs) {
    var s = "<" + tag;
    for (var k in attrs) s += " " + k + '="' + attrs[k] + '"';
    return s + ' stroke="' + INK + '" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"' + (attrs.fill ? "" : ' fill="none"') + "/>";
  }

  // Child bust/standing figure. Origin: head centre at (0,0), roughly 360 wide, 520 tall.
  function kid(p, o) {
    o = o || {};
    var s = "";
    if (!o.noPigtails) { s += rg("circle", { cx: -108, cy: -18, r: 42 }, C.hair, p + "-pt1") + rg("circle", { cx: 108, cy: -18, r: 42 }, C.hair, p + "-pt2"); }
    if (o.body !== false) {
      s += rg("rect", { x: -22, y: 70, width: 44, height: 60, rx: 10 }, C.skin, p + "-neck");
      s += rg("path", { d: "M-80 120 Q0 92 80 120 L135 235 L96 252 L78 200 L78 330 L-78 330 L-78 200 L-96 252 L-135 235 Z" }, o.shirt || C.shirt, p + "-shirt");
      s += rg("path", { d: "M0 175 L12 200 L40 202 L18 220 L26 248 L0 232 L-26 248 L-18 220 L-40 202 L-12 200 Z" }, C.star, p + "-star");
    }
    s += rg("circle", { cx: 0, cy: 0, r: 92 }, C.skin, p + "-face");
    if (o.bandana) s += rg("path", { d: "M-92 -18 Q0 -110 92 -18 Q0 -48 -92 -18 Z" }, C.bandana, p + "-bandana");
    else s += rg("path", { d: "M-92 -6 Q-90 -98 0 -100 Q90 -98 92 -6 Q60 -50 18 -40 Q-10 -70 -40 -36 Q-70 -40 -92 -6 Z" }, C.hair, p + "-hair");
    s += ink("circle", { cx: -32, cy: 8, r: 9, fill: INK }) + ink("circle", { cx: 32, cy: 8, r: 9, fill: INK });
    s += rg("circle", { cx: -55, cy: 38, r: 14 }, C.cheek, p + "-ch1") + rg("circle", { cx: 55, cy: 38, r: 14 }, C.cheek, p + "-ch2");
    s += ink("path", { d: "M-30 42 Q0 74 30 42" });
    return s;
  }

  function dog(p) {
    var s = "";
    s += rg("path", { d: "M120 120 Q170 80 175 30" }, C.dog, p + "-tail");
    s += rg("ellipse", { cx: 40, cy: 150, rx: 120, ry: 70 }, C.dog, p + "-body");
    s += rg("rect", { x: -40, y: 180, width: 34, height: 70, rx: 14 }, C.dog, p + "-leg1") + rg("rect", { x: 90, y: 180, width: 34, height: 70, rx: 14 }, C.dog, p + "-leg2");
    s += rg("circle", { cx: -60, cy: 40, r: 78 }, C.dog, p + "-head");
    s += rg("ellipse", { cx: -128, cy: 40, rx: 28, ry: 56 }, C.ear, p + "-ear1") + rg("ellipse", { cx: 8, cy: 40, rx: 28, ry: 56 }, C.ear, p + "-ear2");
    s += ink("circle", { cx: -84, cy: 28, r: 8, fill: INK }) + ink("circle", { cx: -36, cy: 28, r: 8, fill: INK });
    s += ink("ellipse", { cx: -60, cy: 62, rx: 14, ry: 10, fill: INK }) + ink("path", { d: "M-60 72 Q-60 92 -40 92 M-60 72 Q-60 92 -80 92" });
    return s;
  }

  function astronaut(p) {
    var s = "";
    s += rg("path", { d: "M-110 120 Q0 80 110 120 L150 300 L100 312 L90 260 L90 380 L-90 380 L-90 260 L-100 312 L-150 300 Z" }, C.suit, p + "-suit");
    s += rg("rect", { x: -50, y: 170, width: 100, height: 70, rx: 12 }, C.rocket, p + "-panel");
    s += rg("circle", { cx: 0, cy: 0, r: 128 }, C.helmet, p + "-helmet");
    s += kid(p + "k", { body: false, noPigtails: true });
    return s;
  }

  function rocket(p) {
    var s = "";
    s += rg("path", { d: "M-40 150 Q0 260 40 150 Z" }, C.flame, p + "-flame");
    s += rg("path", { d: "M-55 60 L-110 160 L-50 140 Z" }, C.fin, p + "-fin1") + rg("path", { d: "M55 60 L110 160 L50 140 Z" }, C.fin, p + "-fin2");
    s += rg("path", { d: "M0 -170 Q75 -80 60 150 L-60 150 Q-75 -80 0 -170 Z" }, C.rocket, p + "-body");
    s += rg("circle", { cx: 0, cy: -20, r: 32 }, C.helmet, p + "-win");
    return s;
  }

  function planet(p) {
    return rg("circle", { cx: 0, cy: 0, r: 80 }, C.planet, p + "-pl") + rg("ellipse", { cx: 0, cy: 8, rx: 140, ry: 30, transform: "rotate(-14)" }, C.ring, p + "-ring") +
      rg("circle", { cx: -25, cy: -25, r: 16 }, C.ring, p + "-crater");
  }

  function star(p, x, y, r) {
    var d = "", i;
    for (i = 0; i < 10; i++) { var a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; d += (i ? "L" : "M") + (x + Math.cos(a) * rr).toFixed(1) + " " + (y + Math.sin(a) * rr).toFixed(1) + " "; }
    return rg("path", { d: d + "Z" }, C.star, p);
  }

  function dino(p) {
    var s = "";
    s += rg("path", { d: "M170 40 Q320 60 360 140 Q260 110 170 110 Z" }, C.dino, p + "-tail");
    [[-120, 0], [-60, -40], [0, -60], [60, -50], [120, -20]].forEach(function (q, i) {
      s += rg("path", { d: "M" + (q[0] - 34) + " " + (q[1] + 30) + " L" + q[0] + " " + (q[1] - 50) + " L" + (q[0] + 34) + " " + (q[1] + 30) + " Z" }, C.plate, p + "-pl" + i);
    });
    s += rg("ellipse", { cx: 20, cy: 70, rx: 190, ry: 110 }, C.dino, p + "-body");
    [[-120, 150], [-40, 160], [60, 160], [140, 150]].forEach(function (q, i) { s += rg("rect", { x: q[0] - 26, y: q[1], width: 52, height: 90, rx: 18 }, C.dino, p + "-leg" + i); });
    s += rg("path", { d: "M-160 40 Q-230 -40 -300 -10 Q-330 40 -280 70 Q-220 80 -170 100 Z" }, C.dino, p + "-head");
    s += ink("circle", { cx: -270, cy: 10, r: 8, fill: INK }) + ink("path", { d: "M-315 45 Q-290 60 -260 52" });
    return s;
  }

  function chest(p) {
    var s = "";
    s += rg("rect", { x: -150, y: 0, width: 300, height: 170, rx: 14 }, C.chest, p + "-box");
    s += rg("path", { d: "M-150 0 Q0 -130 150 0 Z" }, C.chest, p + "-lid");
    s += rg("rect", { x: -26, y: -10, width: 52, height: 70, rx: 8 }, C.gold, p + "-lock");
    [[-100, -40], [-40, -70], [30, -64], [95, -38], [-5, -110]].forEach(function (q, i) { s += rg("circle", { cx: q[0], cy: q[1], r: 26 }, C.gold, p + "-coin" + i); });
    return s;
  }

  // Paint every .rg inside root with its crayon color immediately (for "photo" versions).
  function paint(root) { root.querySelectorAll(".rg").forEach(function (e) { e.setAttribute("fill", e.getAttribute("data-c")); }); }

  window.ART = { INK: INK, PAPER: PAPER, C: C, kid: kid, dog: dog, astronaut: astronaut, rocket: rocket, planet: planet, star: star, dino: dino, chest: chest, paint: paint };
})();
