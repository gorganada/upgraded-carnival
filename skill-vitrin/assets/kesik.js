// Paper cut-out ("sticker") art for the NeAlaka shorts.
// Every piece is built twice: a white paper border layer (thick cream stroke) behind the coloured layer,
// so figures read as hand-cut stickers. Ink details (eyes, mouths, seams) sit on top.
(function () {
  var PAPER = "#fffaf0", INK = "#2b211b";

  function B() { this.back = ""; this.front = ""; this.top = ""; }
  B.prototype.add = function (tag, a, fill, extra) {
    var s = "";
    for (var k in a) s += " " + k + '="' + a[k] + '"';
    this.back += "<" + tag + s + ' fill="' + PAPER + '" stroke="' + PAPER + '" stroke-width="20" stroke-linejoin="round" stroke-linecap="round"/>';
    this.front += "<" + tag + s + ' fill="' + fill + '"' + (extra || "") + "/>";
    return this;
  };
  B.prototype.ink = function (tag, a, w, fill) {
    var s = "";
    for (var k in a) s += " " + k + '="' + a[k] + '"';
    this.top += "<" + tag + s + ' fill="' + (fill || "none") + '" stroke="' + INK + '" stroke-width="' + (w || 5) + '" stroke-linecap="round" stroke-linejoin="round"/>';
    return this;
  };
  B.prototype.dot = function (x, y, r, c) { this.top += '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="' + (c || INK) + '"/>'; return this; };
  B.prototype.svg = function () { return "<g>" + this.back + "</g><g>" + this.front + "</g><g>" + this.top + "</g>"; };

  // ---------- people (origin = feet centre, ~ 300 tall) ----------
  var SIDES = {
    us: { coat: "#2f4e8a", trim: "#d8b65a", pants: "#3c5a96", hat: "kepi", hatc: "#25406f" },
    uk: { coat: "#c23b2e", trim: "#f2e3b3", pants: "#2b2b3a", hat: "shako", hatc: "#1f1f2a" },
    farmer: { coat: "#c7893e", trim: "#7b5a35", pants: "#4f6b8f", hat: "straw", hatc: "#e3c26a" },
    admiral: { coat: "#1f2b4d", trim: "#e3c25a", pants: "#1f2b4d", hat: "bicorne", hatc: "#151c33" },
  };
  function person(o) {
    o = o || {}; var s = SIDES[o.side || "us"], b = new B(), skin = o.skin || "#f0c49e";
    // legs
    b.add("rect", { x: -38, y: -110, width: 30, height: 110, rx: 12 }, s.pants).add("rect", { x: 8, y: -110, width: 30, height: 110, rx: 12 }, s.pants);
    b.add("rect", { x: -44, y: -14, width: 40, height: 18, rx: 8 }, "#2b211b").add("rect", { x: 4, y: -14, width: 40, height: 18, rx: 8 }, "#2b211b");
    // arms (behind/ in front of body depending)
    var armL = o.armL === undefined ? 10 : o.armL, armR = o.armR === undefined ? -10 : o.armR;
    b.add("rect", { x: -16, y: -6, width: 30, height: 98, rx: 14, transform: "translate(-52 -214) rotate(" + armL + ")" }, s.coat);
    // body
    b.add("path", { d: "M-54 -220 Q0 -236 54 -220 L60 -100 Q0 -88 -60 -100 Z" }, s.coat);
    b.add("rect", { x: -60, y: -118, width: 120, height: 16, rx: 6 }, s.trim);
    if (o.side === "uk") b.add("path", { d: "M-40 -222 L40 -110 M40 -222 L-40 -110" }, "none", ' stroke="' + s.trim + '" stroke-width="10"');
    else b.ink("path", { d: "M0 -224 V-122" }, 4);
    [-196, -170, -144].forEach(function (y) { b.dot(o.side === "uk" ? 0 : 10, y, 4, s.trim); });
    b.add("rect", { x: -16, y: -6, width: 30, height: 98, rx: 14, transform: "translate(52 -214) rotate(" + armR + ")" }, s.coat);
    if (o.rifle) b.add("rect", { x: -6, y: -150, width: 12, height: 190, rx: 5, transform: "translate(70 -170) rotate(" + (o.rifle === "aim" ? -70 : 8) + ")" }, "#6b4a2f");
    // head
    b.add("rect", { x: -14, y: -250, width: 28, height: 30 }, skin);
    b.add("circle", { cx: 0, cy: -282, r: 46 }, skin);
    b.dot(-15, -284, 5).dot(15, -284, 5);
    if (o.mood === "angry") b.ink("path", { d: "M-26 -300 L-6 -294 M26 -300 L6 -294" }, 5);
    if (o.mood === "smug") b.ink("path", { d: "M-24 -298 L-6 -298 M24 -298 L6 -298" }, 4);
    b.ink("path", { d: o.mood === "angry" ? "M-14 -256 Q0 -264 14 -256" : "M-14 -260 Q0 -248 14 -260" }, 4);
    if (o.beard) b.add("path", { d: "M-40 -272 Q0 -210 40 -272 Q20 -250 0 -252 Q-20 -250 -40 -272 Z" }, o.beard);
    if (o.mustache) b.add("path", { d: "M-24 -266 Q-10 -278 0 -268 Q10 -278 24 -266 Q10 -260 0 -264 Q-10 -260 -24 -266 Z" }, o.mustache);
    // hats
    if (s.hat === "kepi") { b.add("path", { d: "M-40 -318 L-34 -360 Q0 -372 34 -358 L40 -318 Z" }, s.hatc); b.add("rect", { x: -50, y: -324, width: 70, height: 12, rx: 6 }, "#151c2e"); }
    if (s.hat === "shako") { b.add("path", { d: "M-38 -318 L-34 -384 L34 -384 L38 -318 Z" }, s.hatc); b.add("rect", { x: -40, y: -330, width: 80, height: 12, rx: 4 }, "#d8b65a"); b.add("circle", { cx: 0, cy: -392, r: 12 }, "#f2e3b3"); }
    if (s.hat === "straw") { b.add("ellipse", { cx: 0, cy: -318, rx: 78, ry: 16 }, s.hatc); b.add("path", { d: "M-40 -318 Q-36 -366 0 -368 Q36 -366 40 -318 Z" }, s.hatc); b.add("rect", { x: -40, y: -334, width: 80, height: 12 }, "#b0452f"); }
    if (s.hat === "bicorne") { b.add("path", { d: "M-92 -316 Q0 -400 92 -316 Q0 -340 -92 -316 Z" }, s.hatc); b.add("circle", { cx: 0, cy: -350, r: 10 }, "#e3c25a"); }
    return b.svg();
  }

  // ---------- pig (origin = belly bottom centre) ----------
  function pig(o) {
    o = o || {}; var b = new B(), P = "#f4a7b0", D = "#e48896";
    b.add("path", { d: "M138 -96 q34 -10 26 -36 q-8 -20 -26 -6 q-14 14 8 22" }, "none", ' stroke="' + D + '" stroke-width="9" stroke-linecap="round"');
    [-92, -40, 40, 92].forEach(function (x) { b.add("rect", { x: x - 18, y: -60, width: 36, height: 64, rx: 14 }, D); });
    b.add("ellipse", { cx: 0, cy: -110, rx: 150, ry: 92 }, P);
    b.add("path", { d: "M-160 -190 L-196 -248 L-128 -214 Z" }, D).add("path", { d: "M-82 -196 L-70 -258 L-40 -200 Z" }, D);
    b.add("circle", { cx: -128, cy: -150, r: 76 }, P);
    b.add("ellipse", { cx: -188, cy: -136, rx: 34, ry: 28 }, D);
    b.dot(-200, -138, 7, "#b25d6a").dot(-176, -138, 7, "#b25d6a");
    if (o.xeyes) b.ink("path", { d: "M-156 -184 l16 16 m0 -16 l-16 16 M-114 -184 l16 16 m0 -16 l-16 16" }, 6);
    else b.dot(-148, -176, 8).dot(-106, -176, 8);
    b.ink("path", { d: "M-150 -112 q20 14 40 0" }, 5);
    if (o.tag) { b.add("rect", { x: 10, y: -232, width: 120, height: 70, rx: 10, transform: "rotate(8)" }, "#fffaf0"); }
    return b.svg();
  }

  // ---------- ship (origin = waterline centre, ~ 520 wide) ----------
  function ship(o) {
    o = o || {}; var b = new B();
    b.add("path", { d: "M-260 -60 L250 -60 L210 40 L-230 40 Z" }, "#3b2a22");
    b.add("rect", { x: -250, y: -80, width: 500, height: 26, rx: 6 }, "#5a3b2c");
    for (var i = -3; i <= 3; i++) b.add("rect", { x: i * 62 - 12, y: -40, width: 24, height: 18, rx: 3 }, "#1a120e");
    [-150, 0, 140].forEach(function (x, k) {
      b.add("rect", { x: x - 7, y: -330 + k * 20, width: 14, height: 260 - k * 20 }, "#4a3328");
      b.add("path", { d: "M" + (x - 70) + " " + (-300 + k * 20) + " Q" + x + " " + (-250 + k * 20) + " " + (x + 70) + " " + (-300 + k * 20) + " L" + (x + 60) + " " + (-200 + k * 20) + " Q" + x + " " + (-170 + k * 20) + " " + (x - 60) + " " + (-200 + k * 20) + " Z" }, "#f1e6cc");
    });
    b.add("rect", { x: -40, y: -170, width: 34, height: 90, rx: 4 }, "#2b211b");
    if (o.flag !== false) b.add("rect", { x: 140, y: -372, width: 70, height: 44 }, "#c23b2e").ink("path", { d: "M140 -372 l70 44 M210 -372 l-70 44 M175 -372 v44 M140 -350 h70" }, 7, "none");
    return b.svg();
  }

  function cannon() {
    var b = new B();
    b.add("rect", { x: -20, y: -40, width: 200, height: 56, rx: 26, transform: "rotate(-14)" }, "#3a3a40");
    b.add("circle", { cx: 0, cy: 0, r: 48 }, "#7b5a35");
    b.dot(0, 0, 12, "#2b211b");
    return b.svg();
  }

  // ---------- flags ----------
  function flagUS(w, h) {
    var s = '<rect x="0" y="0" width="' + w + '" height="' + h + '" fill="#fffaf0"/>';
    for (var i = 0; i < 13; i += 2) s += '<rect x="0" y="' + (i * h / 13).toFixed(1) + '" width="' + w + '" height="' + (h / 13).toFixed(1) + '" fill="#b8322a"/>';
    s += '<rect x="0" y="0" width="' + (w * 0.42) + '" height="' + (h * 7 / 13) + '" fill="#2f4e8a"/>';
    for (var r = 0; r < 4; r++) for (var c = 0; c < 5; c++) s += '<circle cx="' + (w * 0.05 + c * w * 0.08) + '" cy="' + (h * 0.07 + r * h * 0.12) + '" r="' + (w * 0.012) + '" fill="#fffaf0"/>';
    return s;
  }
  function flagUK(w, h) {
    return '<rect width="' + w + '" height="' + h + '" fill="#2f4e8a"/>' +
      '<path d="M0 0 L' + w + " " + h + " M" + w + ' 0 L0 ' + h + '" stroke="#fffaf0" stroke-width="' + h * 0.2 + '"/>' +
      '<path d="M0 0 L' + w + " " + h + " M" + w + ' 0 L0 ' + h + '" stroke="#c23b2e" stroke-width="' + h * 0.07 + '"/>' +
      '<path d="M' + w / 2 + " 0 V" + h + " M0 " + h / 2 + " H" + w + '" stroke="#fffaf0" stroke-width="' + h * 0.33 + '"/>' +
      '<path d="M' + w / 2 + " 0 V" + h + " M0 " + h / 2 + " H" + w + '" stroke="#c23b2e" stroke-width="' + h * 0.2 + '"/>';
  }

  function potatoPlant() {
    var b = new B();
    b.add("ellipse", { cx: 0, cy: -10, rx: 70, ry: 22 }, "#8a6240");
    [[-40, -90, -20], [0, -120, 0], [40, -86, 20]].forEach(function (q) { b.add("ellipse", { cx: q[0], cy: q[1], rx: 26, ry: 50, transform: "rotate(" + q[2] + " " + q[0] + " " + q[1] + ")" }, "#5f9a4a"); });
    return b.svg();
  }

  window.KESIK = { person: person, pig: pig, ship: ship, cannon: cannon, flagUS: flagUS, flagUK: flagUK, potatoPlant: potatoPlant, PAPER: PAPER, INK: INK };
})();
