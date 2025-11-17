"""
phase_sector_probabilities.py
-----------------------------

Explora el espacio de parámetros (m_phi, k_rot) y calcula, para cada punto,
las probabilidades de terminar en los sectores A, B o C en función de
las condiciones iniciales de fase Δphi_ini.

Para cada (m_phi, k_rot):
  - Se muestrean N_delta condiciones iniciales Δphi_ini en [0, π]
  - Se integra Δphi(a) con run_phase_evolution
  - Se clasifica la trayectoria en A, B o C
  - Se calcula P_A, P_B, P_C

Resultados:
  - CSV: results_phase_sectors/phase_sector_probabilities.csv
  - Figura: results_phase_sectors/phase_sector_probabilities.png
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

from phase_evolution_ode import run_phase_evolution

# ================================================================
# Clasificador de sectores (mismo criterio que en phase_classifier)
# ================================================================

def classify_sector(delta_phi_arr,
                    tail_fraction=0.2,
                    tol_A=0.1,
                    tol_B=0.1):
    """
    Clasifica una trayectoria Δphi(a) en sectores A, B o C según su
    comportamiento asintótico.

    - Sector A: sincronía (Δphi -> 0)
    - Sector B: antipodal (Δphi -> π, módulo 2π)
    - Sector C: escape / régimen oscilante

    Parámetros
    ----------
    delta_phi_arr : array-like
        Valores de Δphi(a) a lo largo de la integración.
    tail_fraction : float
        Fracción final del array usada para estimar el comportamiento asintótico.
    tol_A : float
        Umbral de proximidad a 0 para considerar Sector A.
    tol_B : float
        Umbral de proximidad a π (mód 2π) para considerar Sector B.

    Devuelve
    --------
    str : 'A', 'B' o 'C'
    """

    dphi = np.unwrap(delta_phi_arr)  # desenrollar por si hay saltos 2π
    n = len(dphi)
    if n < 10:
        return "C"

    n_tail = max(int(n * tail_fraction), 5)
    tail = dphi[-n_tail:]

    mean_tail = np.mean(tail)
    std_tail = np.std(tail)

    # Proximidad a 0
    if abs(mean_tail) < tol_A and std_tail < tol_A:
        return "A"

    # Proximidad a π (mód 2π)
    # Llevamos mean_tail a la ventana más cercana a π
    mod_2pi = np.mod(mean_tail, 2.0 * np.pi)
    dist_to_pi = min(abs(mod_2pi - np.pi),
                     abs(mod_2pi - 3.0 * np.pi))

    if dist_to_pi < tol_B and std_tail < tol_B:
        return "B"

    # Si no es ni A ni B de forma clara, lo consideramos C
    return "C"


# ================================================================
# Parámetros del escaneo
# ================================================================

# Rejilla de m_phi y k_rot (ajustable)
M_GRID = np.linspace(0.3, 3.0, 7)   # 7 valores de m_phi
K_GRID = np.linspace(0.0, 0.5, 7)   # 7 valores de k_rot

N_DELTA = 40  # número de condiciones iniciales Δphi_ini por punto (m,k)

DELTA_MIN = 0.0
DELTA_MAX = np.pi   # exploramos Δphi_ini en [0, π]

A_INI = 1e-3
A_MAX = 10.0

# Directorio de salida
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_PATH, "results_phase_sectors")
os.makedirs(OUT_DIR, exist_ok=True)


# ================================================================
# Bucle principal
# ================================================================

rows = []

m_list = list(M_GRID)
k_list = list(K_GRID)
total_points = len(m_list) * len(k_list)
point_counter = 0

print("\n===============================================")
print(" PHASE SECTOR PROBABILITIES SCAN")
print(" Grid: {} m_phi × {} k_rot = {} puntos"
      .format(len(m_list), len(k_list), total_points))
print(" N_delta = {} condiciones iniciales por punto".format(N_DELTA))
print("===============================================\n")

for m_phi in m_list:
    for k_rot in k_list:
        point_counter += 1
        print(f"→ Punto {point_counter}/{total_points} : m_phi={m_phi:.3f}, k_rot={k_rot:.3f}")

        # Muestreo de condiciones iniciales
        delta_inis = np.linspace(DELTA_MIN, DELTA_MAX, N_DELTA)

        count_A = 0
        count_B = 0
        count_C = 0

        for i, d0 in enumerate(delta_inis):
            # Pequeña impresión de progreso interno (opcional)
            # print(f"   Δphi_ini {i+1}/{N_DELTA} = {d0:.3f}", end="\r")

            a_arr, dphi_arr, dphidot_arr = run_phase_evolution(
                m_phi=m_phi,
                k_rot=k_rot,
                q=1.0,
                delta_phi_ini=d0,
                delta_phidot_ini=0.0,
                a_ini=A_INI,
                a_max=A_MAX,
                n_steps=1500,
                H0=1.0,
                rtol=1e-7,
                atol=1e-9,
            )

            sector = classify_sector(dphi_arr)

            if sector == "A":
                count_A += 1
            elif sector == "B":
                count_B += 1
            else:
                count_C += 1

        N_tot = count_A + count_B + count_C
        if N_tot == 0:
            P_A = P_B = P_C = 0.0
        else:
            P_A = count_A / N_tot
            P_B = count_B / N_tot
            P_C = count_C / N_tot

        rows.append({
            "m_phi": m_phi,
            "k_rot": k_rot,
            "N_total": N_tot,
            "N_A": count_A,
            "N_B": count_B,
            "N_C": count_C,
            "P_A": P_A,
            "P_B": P_B,
            "P_C": P_C,
        })

        print(f"   Resultados: P_A={P_A:.2f}, P_B={P_B:.2f}, P_C={P_C:.2f}\n")

# ================================================================
# Guardar CSV
# ================================================================

df = pd.DataFrame(rows)
out_csv = os.path.join(OUT_DIR, "phase_sector_probabilities.csv")
df.to_csv(out_csv, index=False)

print("===============================================")
print(f" CSV guardado → {out_csv}")
print("===============================================")


# ================================================================
# Figuras: mapas de calor de P_A y P_C
# ================================================================

# Intentamos reorganizar en m × k para hacer mapas bonitos
m_unique = np.sort(df["m_phi"].unique())
k_unique = np.sort(df["k_rot"].unique())

M_mesh, K_mesh = np.meshgrid(m_unique, k_unique, indexing="ij")

PA_mesh = np.zeros_like(M_mesh)
PC_mesh = np.zeros_like(M_mesh)

for i, m in enumerate(m_unique):
    for j, k in enumerate(k_unique):
        sub = df[(df["m_phi"] == m) & (df["k_rot"] == k)]
        if len(sub) == 1:
            PA_mesh[i, j] = sub["P_A"].values[0]
            PC_mesh[i, j] = sub["P_C"].values[0]
        else:
            PA_mesh[i, j] = np.nan
            PC_mesh[i, j] = np.nan

fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

im0 = axes[0].imshow(
    PA_mesh,
    origin="lower",
    extent=[k_unique.min(), k_unique.max(), m_unique.min(), m_unique.max()],
    aspect="auto"
)
axes[0].set_title(r"$P_A$ (Synchrony)")
axes[0].set_xlabel(r"$k_{\rm rot}$")
axes[0].set_ylabel(r"$m_\phi$")
fig.colorbar(im0, ax=axes[0])

im1 = axes[1].imshow(
    PC_mesh,
    origin="lower",
    extent=[k_unique.min(), k_unique.max(), m_unique.min(), m_unique.max()],
    aspect="auto"
)
axes[1].set_title(r"$P_C$ (Escape / oscillatory)")
axes[1].set_xlabel(r"$k_{\rm rot}$")
axes[1].set_ylabel(r"$m_\phi$")
fig.colorbar(im1, ax=axes[1])

out_fig = os.path.join(OUT_DIR, "phase_sector_probabilities.png")
plt.savefig(out_fig, dpi=200)
plt.close()

print(f" Figura de probabilidades guardada → {out_fig}")
print("\n===============================================")
print(" DONE — Phase sector probability mapping")
print("===============================================\n")
