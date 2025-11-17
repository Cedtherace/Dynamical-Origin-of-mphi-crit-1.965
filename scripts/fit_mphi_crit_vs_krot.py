"""
fit_mphi_crit_vs_krot.py
------------------------

Ajuste matemático fino de m_phi,crit(k_rot) a partir de:

    results_phase_sectors/mphi_crit_vs_krot.json

Hace:
  1) Carga los pares (k_rot, m_phi_crit) válidos.
  2) Ajusta una parábola: m_phi,crit(k) = a k^2 + b k + c
  3) Calcula el máximo de la parábola (k_peak, m_peak).
  4) Calcula R^2 del ajuste.
  5) Guarda un resumen en JSON:
         mphi_crit_vs_krot_fit_summary.json
  6) Genera figura:
         mphi_crit_vs_krot_fit.png

Usa rutas relativas dentro de 'limite de martin'.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# 0. Rutas base
# ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results_phase_sectors")

json_path = os.path.join(RESULTS_DIR, "mphi_crit_vs_krot.json")
if not os.path.isfile(json_path):
    raise FileNotFoundError(
        f"No se encontró el archivo JSON con los datos:\n  {json_path}\n"
        "Asegúrate de haber ejecutado antes analyse_mphi_krot_critical.py."
    )

print("🔹 [1/3] Cargando datos desde:", json_path)

with open(json_path, "r") as f:
    data = json.load(f)

entries = data.get("data", [])
k_vals = []
mcrit_vals = []

for entry in entries:
    k = entry.get("k_rot", None)
    mcrit = entry.get("m_phi_crit", None)
    if k is None or mcrit is None:
        continue
    k_vals.append(float(k))
    mcrit_vals.append(float(mcrit))

k_vals = np.array(k_vals)
mcrit_vals = np.array(mcrit_vals)

if k_vals.size < 3:
    raise RuntimeError(
        "No hay suficientes puntos válidos para ajustar una parábola "
        f"(puntos válidos: {k_vals.size})."
    )

print(f"   → Puntos válidos: {k_vals.size}")
print("     k_rot   =", k_vals)
print("     m_phi_c =", mcrit_vals)

# ---------------------------------------------------------------------
# 1. Ajuste parabólico m_phi,crit(k) = a k^2 + b k + c
# ---------------------------------------------------------------------
print("🔹 [2/3] Ajustando parábola m_phi,crit(k_rot) ...")

coeffs = np.polyfit(k_vals, mcrit_vals, 2)  # grado 2
a, b, c = coeffs
# vértice de la parábola
k_peak = -b / (2 * a)
m_peak = np.polyval(coeffs, k_peak)

# Predicción y R^2
mcrit_fit = np.polyval(coeffs, k_vals)
ss_res = np.sum((mcrit_vals - mcrit_fit) ** 2)
ss_tot = np.sum((mcrit_vals - np.mean(mcrit_vals)) ** 2)
r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

# Estadísticas simples
m_mean = float(np.mean(mcrit_vals))
m_std = float(np.std(mcrit_vals))

print("\n📈 Resultados del ajuste:")
print(f"   a = {a:.6f}")
print(f"   b = {b:.6f}")
print(f"   c = {c:.6f}")
print(f"   k_peak   ≈ {k_peak:.4f}")
print(f"   m_peak   ≈ {m_peak:.4f}")
print(f"   R^2      ≈ {r2:.4f}")
print(f"   <m_phi_c> = {m_mean:.4f} ± {m_std:.4f}")

# ---------------------------------------------------------------------
# 2. Guardar resumen en JSON
# ---------------------------------------------------------------------
fit_summary = {
    "parabola_coeffs": {
        "a": float(a),
        "b": float(b),
        "c": float(c),
        "form": "m_phi_crit(k) = a*k^2 + b*k + c"
    },
    "k_peak": float(k_peak),
    "m_phi_peak": float(m_peak),
    "R2": float(r2),
    "stats": {
        "mean_m_phi_crit": m_mean,
        "std_m_phi_crit": m_std,
        "num_points": int(k_vals.size)
    },
    "source_file": os.path.basename(json_path),
}

fit_json_path = os.path.join(RESULTS_DIR, "mphi_crit_vs_krot_fit_summary.json")
with open(fit_json_path, "w") as f:
    json.dump(fit_summary, f, indent=2)

print("\n💾 Resumen del ajuste guardado en:")
print("   ", fit_json_path)

# ---------------------------------------------------------------------
# 3. Figura m_phi,crit(k_rot) con ajuste
# ---------------------------------------------------------------------
print("🔹 [3/3] Generando figura del ajuste...")

k_min, k_max = np.min(k_vals), np.max(k_vals)
k_smooth = np.linspace(k_min, k_max, 400)
m_fit_smooth = np.polyval(coeffs, k_smooth)

fig, ax = plt.subplots(figsize=(6.0, 4.5))

# Datos originales
ax.plot(k_vals, mcrit_vals, "o", label="Datos (m_phi,crit)", alpha=0.9)

# Curva ajustada
ax.plot(k_smooth, m_fit_smooth, "-", label="Ajuste parabólico", linewidth=1.5)

# Pico
ax.axvline(k_peak, linestyle="--", linewidth=1.0, label=f"k_peak ≈ {k_peak:.3f}")
ax.axhline(m_peak, linestyle=":", linewidth=1.0, label=f"m_peak ≈ {m_peak:.3f}")

ax.set_xlabel(r"$k_{\mathrm{rot}}$")
ax.set_ylabel(r"$m_{\phi,\mathrm{crit}}$")
ax.set_title(r"Ajuste de $m_{\phi,\mathrm{crit}}(k_{\mathrm{rot}})$")
ax.grid(alpha=0.3)
ax.legend(fontsize=9)

fig.tight_layout()

fig_path = os.path.join(RESULTS_DIR, "mphi_crit_vs_krot_fit.png")
fig.savefig(fig_path, dpi=150)
plt.close(fig)

print("🖼  Figura del ajuste guardada en:")
print("   ", fig_path)

print("\n✅ Ajuste completado.")
