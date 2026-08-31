/* ═══════════ Форма головы: знаковое поле расстояний ═══════════
   Ось Y — вверх, +Z — вперёд (лицо). Подбородок y=-0.50, темя y=+0.50. */
var HEAD = (function () {
"use strict";

function smin(a, b, k) { var h = Math.max(0, Math.min(1, 0.5 + 0.5 * (b - a) / k)); return b * (1 - h) + a * h - k * h * (1 - h); }
function smax(a, b, k) { return -smin(-a, -b, k); }

function ell(x, y, z, cx, cy, cz, rx, ry, rz) {
  var ax = (x - cx) / rx, ay = (y - cy) / ry, az = (z - cz) / rz;
  var k0 = Math.sqrt(ax * ax + ay * ay + az * az);
  if (k0 === 0) return -Math.min(rx, ry, rz);
  var bx = ax / rx, by = ay / ry, bz = az / rz;
  var k1 = Math.sqrt(bx * bx + by * by + bz * bz);
  return k0 * (k0 - 1) / k1;
}
function cap(x, y, z, ax, ay, az, bx, by, bz, r) {
  var px = x - ax, py = y - ay, pz = z - az;
  var dx = bx - ax, dy = by - ay, dz = bz - az;
  var t = (px * dx + py * dy + pz * dz) / (dx * dx + dy * dy + dz * dz);
  t = t < 0 ? 0 : t > 1 ? 1 : t;
  var qx = px - dx * t, qy = py - dy * t, qz = pz - dz * t;
  return Math.sqrt(qx * qx + qy * qy + qz * qz) - r;
}

function map(x, y, z) {
  var ax = Math.abs(x);

  var d = ell(x, y, z, 0, 0.132, -0.035, 0.306, 0.310, 0.330);            // черепная коробка
  d = smin(d, ell(x, y, z, 0, 0.020, 0.005, 0.292, 0.200, 0.326), 0.10);  // виски и орбиты
  d = smin(d, ell(ax, y, z, 0.168, -0.030, 0.176, 0.120, 0.100, 0.130), 0.12); // скулы
  d = smin(d, ell(x, y, z, 0, -0.148, 0.092, 0.212, 0.132, 0.266), 0.12); // средняя треть
  d = smin(d, ell(x, y, z, 0, -0.272, 0.018, 0.216, 0.124, 0.244), 0.13); // челюсть
  d = smin(d, ell(ax, y, z, 0.178, -0.256, -0.045, 0.032, 0.068, 0.108), 0.11); // углы челюсти
  d = smin(d, ell(x, y, z, 0, -0.376, 0.202, 0.092, 0.068, 0.112), 0.11); // подбородок
  d = smin(d, ell(x, y, z, 0, 0.086, 0.276, 0.178, 0.028, 0.050), 0.09);  // надбровье

  d = smin(d, cap(x, y, z, 0, 0.068, 0.288, 0, -0.100, 0.382, 0.022), 0.045);   // спинка носа
  d = smin(d, cap(x, y, z, 0, -0.092, 0.378, 0, -0.128, 0.404, 0.028), 0.035);  // кончик
  d = smin(d, ell(x, y, z, 0, -0.136, 0.408, 0.035, 0.029, 0.041), 0.030);
  d = smin(d, ell(ax, y, z, 0.045, -0.158, 0.370, 0.029, 0.024, 0.035), 0.030); // крылья носа

  d = smin(d, ell(x, y, z, 0, -0.268, 0.215, 0.152, 0.096, 0.120), 0.10);  // зубная дуга
  d = smin(d, ell(x, y, z, 0, -0.242, 0.306, 0.073, 0.026, 0.050), 0.026); // верхняя губа
  d = smin(d, ell(x, y, z, 0, -0.288, 0.306, 0.067, 0.032, 0.052), 0.026); // нижняя губа

  d = smin(d, ell(ax, y, z, 0.118, 0.014, 0.262, 0.080, 0.024, 0.050), 0.030); // закрытые веки
  d = smin(d, ell(ax, y, z, 0.302, -0.045, -0.050, 0.026, 0.088, 0.058), 0.040); // уши

  d = smin(d, cap(x, y, z, 0, -0.368, -0.020, 0, -0.860, -0.085, 0.150), 0.13); // шея
  d = smin(d, ell(x, y, z, 0, -1.020, -0.060, 0.720, 0.300, 0.300), 0.22);      // плечи

  d = smin(d, ell(x, y, z, 0, 0.150, -0.060, 0.318, 0.320, 0.342), 0.05);  // волосы
  d = smin(d, ell(x, y, z, 0, 0.075, -0.372, 0.152, 0.155, 0.125), 0.09);  // пучок

  // вычитаем: глазницы, складка века, щель рта, подгубная борозда, ноздри
  d = smax(d, -ell(ax, y, z, 0.116, 0.018, 0.262, 0.092, 0.044, 0.068), 0.045);
  d = smax(d, -ell(ax, y, z, 0.116, 0.040, 0.272, 0.076, 0.008, 0.044), 0.020);
  d = smax(d, -ell(x, y, z, 0, -0.265, 0.318, 0.064, 0.004, 0.032), 0.010);
  d = smax(d, -ell(x, y, z, 0, -0.336, 0.288, 0.098, 0.013, 0.030), 0.040);
  d = smax(d, -ell(ax, y, z, 0.042, -0.168, 0.380, 0.017, 0.014, 0.036), 0.018);
  return d;
}

/* 0 — кожа, 1 — волосы, 2 — веки (светятся), 3 — тень, 4 — бровь, 5 — область глаза */
function classify(x, y, z) {
  var ax = Math.abs(x);
  var ex = (ax - 0.118) / 0.084, ey = (y - 0.014) / 0.020, ez = (z - 0.262) / 0.058;
  if (z > 0.16 && ex * ex + ey * ey + ez * ez < 1) return 2;                 // веко
  var lx = x / 0.074, ly = (y + 0.265) / 0.034, lz = (z - 0.316) / 0.050;
  if (z > 0.22 && lx * lx + ly * ly + lz * lz < 1) return 3;                 // губы
  var nx = (ax - 0.042) / 0.023, ny = (y + 0.178) / 0.021;
  if (z > 0.33 && nx * nx + ny * ny < 1) return 3;                           // ноздри
  var arc = 0.073 + 0.85 * ax * ax;
  if (z > 0.20 && ax > 0.040 && ax < 0.188 && y > arc && y < arc + 0.026) return 4;
  var gx = (ax - 0.116) / 0.125, gy = (y - 0.014) / 0.075, gz = (z - 0.235) / 0.125;
  if (z > 0.08 && gx * gx + gy * gy + gz * gz < 1) return 5;                 // веко ловит свет
  var line = 0.276 - 0.30 * ax + 0.020 * Math.cos(x * 12);
  if (z > -0.02 ? y > line : y > -0.30) return 1;
  return 0;
}

var EPS = 0.0020;
function normalAt(x, y, z, out) {
  var nx = map(x + EPS, y, z) - map(x - EPS, y, z);
  var ny = map(x, y + EPS, z) - map(x, y - EPS, z);
  var nz = map(x, y, z + EPS) - map(x, y, z - EPS);
  var l = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
  out[0] = nx / l; out[1] = ny / l; out[2] = nz / l;
}
function trace(ox, oy, oz, dx, dy, dz) {
  var t = 0;
  for (var i = 0; i < 96; i++) {
    var d = map(ox + dx * t, oy + dy * t, oz + dz * t);
    if (d < 0.0008) return t;
    t += Math.max(d * 0.85, 0.0022);
    if (t > 3.6) break;
  }
  return -1;
}

/* Лучи из окружающей сферы садятся на поверхность — получается решётка из точек. */
function sample(rings, rows, sink) {
  var n3 = [0, 0, 0], i, j;
  for (i = 0; i < rings; i++) {
    var th = Math.PI * (i + 0.5) / rings, st = Math.sin(th), ct = Math.cos(th);
    var count = Math.max(8, Math.round(2.1 * rings * st));
    for (j = 0; j < count; j++) {
      var ph = 2 * Math.PI * (j + (i & 1) * 0.5) / count;
      var dx = st * Math.sin(ph), dy = ct, dz = st * Math.cos(ph), R = 2.4;
      var t = trace(dx * R, dy * R, dz * R, -dx, -dy, -dz);
      if (t < 0) continue;
      var x = dx * (R - t), y = dy * (R - t), z = dz * (R - t);
      normalAt(x, y, z, n3); sink(x, y, z, n3);
    }
  }
  for (i = 0; i < rows; i++) {                       // шея и плечи — винтовая раскладка
    var yy = -0.36 - i * 0.0080, COLS = 132;
    for (j = 0; j < COLS; j++) {
      var p2 = 2 * Math.PI * (j / COLS + i * 0.31);
      var ex = Math.sin(p2), ez = Math.cos(p2), R2 = 1.7;
      var t2 = trace(ex * R2, yy, ez * R2, -ex, 0, -ez);
      if (t2 < 0) continue;
      var x2 = ex * (R2 - t2), z2 = ez * (R2 - t2);
      normalAt(x2, yy, z2, n3); sink(x2, yy, z2, n3);
    }
  }
}

return { map: map, classify: classify, normalAt: normalAt, trace: trace, sample: sample };
})();
if (typeof module !== "undefined") module.exports = HEAD;
