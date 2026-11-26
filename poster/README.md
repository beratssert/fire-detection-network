# Preliminary analyses and poster (archive)

> **Frozen archive.** This folder keeps the team's earlier work exactly as it was published; it is not changed and is
> not part of the automatic checks. In WP5 the model is copied to [`analysis/`](../analysis/) and run there with the
> measured values, so that the published results stay reproducible here.
>
> One difference from the published version: the contact e-mail address was removed from `poster.tex` before this
> repository was published. `params.py` and `notes/RESEARCH.md` refer to `REVIEW.md` and to the tag `baseline-v1`:
> these belong to the working notes of the preliminary work and are not part of this repository.

The team's preliminary model of a LoRa forest-fire sensor network for *Pinus brutia* forests, the results it produced
and the A0 poster built from them ("A security-aware model of a LoRa forest-fire sensor network", LightSec 2026).
This model is what the prototype project measures against.

- **How the results are computed:** [METHOD.md](METHOD.md)
- **Every input** is in [`params.py`](params.py), labelled as `SOURCE` (literature or datasheet), `VENDOR`,
  `ASSUMPTION` or `DERIVED`, with its source. The source table behind the labels is
  [`notes/RESEARCH.md`](notes/RESEARCH.md) (in Turkish).
- **Results:** [`results/`](results/) (CSV), [`figures/`](figures/). Everything here is a model output built on literature
  parameters, not a field measurement.

## Files

| File | Content |
|---|---|
| `params.py` | all inputs, one place, labelled |
| `lora.py` | LoRa time on air (Semtech AN1200.13) |
| `detect.py` | detection model: exact Poisson integral |
| `models.py` | radio range, multi-hop connectivity (Monte Carlo), detection, security overhead → `results/*.csv` |
| `reqdens.py` | density needed for 90 % detection within T minutes |
| `latency.py` | alarm delay over the mesh, relay duty-cycle load |
| `energy.py` | node energy budget, battery and PV/supercapacitor |
| `cost.py` | capital and 10-year cost per hectare |
| `macros.py` | writes `results/macros.tex`: every number printed on the poster, taken from the CSVs or `params.py` |
| `figures.py` | `figures/f1`–`f5` from the CSVs |
| `poster.tex`, `references.bib`, `posternat.bst` | the poster (tikzposter) and its bibliography |
| `tests/check_model.py` | independent checks: re-derives the main outputs from `params.py` without importing the model |
| `sources/companies.csv` | vendor claims used for comparison (not verified measurements) |

## Reproducing

Requirements: Python 3.9 with the pinned packages in `requirements.txt`; TeX Live with `tikzposter` (for the PDF).

```bash
cd poster
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_all.sh          # models -> reqdens -> latency -> energy -> cost -> macros -> figures -> pdflatex/bibtex -> checks
```

`run_all.sh` refuses to run unless the active Python is `poster/.venv`. The run is deterministic (fixed seeds):
`results/*.csv` and the PNG figures are byte-identical between runs; the PDF figures differ only in their creation date.
To run only the checks against the committed results: `python tests/check_model.py` (from this folder).
