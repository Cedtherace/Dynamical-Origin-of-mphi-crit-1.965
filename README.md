# Dynamical Origin of mφ,crit — Robustness and Rotational Maximum

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17635746.svg)](https://zenodo.org/records/17635746)

This repository contains the main paper on the critical phase mass (~1.965) in a CPT-symmetric “Siamese Universes” framework, plus a prose-only supplement explaining the shallow rotational maximum around `k_rot ≈ 0.33`. Results are reproducible with the included scripts and figure assets.

## Files
- `Dynamical_Origin_of_mphi_crit_v7_2.pdf` — main paper (10 pp., figs 1–7).
- `Rotational_Maximum_Section_v1_TEXT.pdf` — prose-only supplement (no LaTeX needed).
- `figs/` — final figures:
  - `PA_vs_mphi.png`, `PA_map_mphi_krot_with_mcrit.png`,
  - `mphi_crit_vs_krot.png`, `mphi_crit_vs_krot_fit.png`,
  - `phase_sector_map_delta.png`, `sectorB_trajectories.png`,
  - `crit_phase_portrait.png`, `crit_trajectories.png`
- `scripts/` — code used to generate the figures (see script headers for usage).

## Reproducibility (brief)
- Initial phases: uniform in `[0, π)`, zero initial velocity.
- Background: radiation-like; effective friction `3 + ξ(N)`.
- Rotational source: transient, decaying with e-folds.
- Sector criteria: late-time averages with thresholds close to `(0.1, 0.1, 0.05)`.
- `mφ,crit(k_rot)`: linear interpolation at `P_A = 0.5` (optional quadratic fit).

## How to cite
CosmicThinker & ChatGPT (Toko). *Dynamical Origin of mφ,crit — Robustness and Rotational Maximum*. Zenodo (2025). https://doi.org/10.5281/zenodo.17635746

