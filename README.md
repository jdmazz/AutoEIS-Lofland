[![DOI](https://joss.theoj.org/papers/10.21105/joss.06256/status.svg)](https://doi.org/10.21105/joss.06256)
![example workflow](https://github.com/AUTODIAL/AutoEIS/actions/workflows/nightly.yml/badge.svg)

> [!NOTE]
> This is a fork of [AUTODIAL/AutoEIS](https://github.com/AUTODIAL/AutoEIS), forked and modified by Jason Mazzaroth for Dr. Lofland's lab at Rowan University. For the upstream project and original documentation, see the source repository above. The citation details (from the original lab) are below and should be used if your journal publication uses this software.
>

# AutoEIS

## What is AutoEIS?

AutoEIS (Auto ee-eye-ess) is a Python package that automatically proposes statistically plausible equivalent circuit models (ECMs) for electrochemical impedance spectroscopy (EIS) analysis. The package is designed for researchers and practitioners in the fields of electrochemical analysis, including but not limited to explorations of electrocatalysis, battery design, and investigations of material degradation.

## Installation

### Installing with conda

You need conda before the install steps below. If you already have it, skip this.

**Windows**

1. Download the installer: https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
2. Double-click it and click through the prompts, accepting the defaults.
3. From the Start menu, open **Anaconda Prompt**; run all later commands there, not in regular Command Prompt.
4. Confirm it worked: `conda --version`.

**Linux**

1. Download and run the installer:
```bash
   curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh
```
   (On ARM machines such as a Raspberry Pi or Graviton instance, replace `x86_64` with `aarch64` in both places.)
2. Accept the license and the default install location, and answer `yes` when it offers to initialize conda.
3. Close and reopen your terminal; you should see `(base)` at the start of the prompt.
4. Confirm it worked: `conda --version`.

### Run from the repository root:

```bash
conda env create -f environment.yml
conda activate autoeis-lofland
python -m autoeis install
```

The install step fetches Julia 1.10 and the pinned `EquivalentCircuits.jl` automatically; no separate Julia install is required. Do not run `pip install -U autoeis`; that installs the upstream package from PyPI and ignores this fork's pin.

## Usage

> [!WARNING]
> AutoEIS's circuit search and inference are built for interactive use. Run the example below in a Jupyter notebook (Jupyter Lab, VS Code, etc.), not a plain Python REPL or a bare `python script.py` — it may not behave as expected outside a notebook-like environment.

`perform_full_analysis` (the single-call entry point) is currently disabled upstream, so the supported path is the step-by-step pipeline: preprocess, generate candidate circuits, filter, then run Bayesian inference. This mirrors `examples/validation_synthetic.ipynb`, which validates each of these steps against synthetic data with known answers.

```python
import autoeis as ae

# 1. Load impedance data as (freq, Z) — see data/Trial 2/ for a real example dataset,
#    or ae.io.load_test_dataset() for the bundled sample.
freq, Z = ae.io.load_test_dataset()

# 2. Preprocess: drops points that fail Kramers-Kronig validation
freq, Z = ae.utils.preprocess_impedance_data(freq, Z, tol_linKK=5e-2)

# 3. Generate candidate equivalent circuits (runs the Julia search; slow on first call)
circuits = ae.generate_equivalent_circuits(freq, Z, iters=100, seed=0)

# 4. Filter out physically implausible circuits
circuits = ae.filter_implausible_circuits(circuits)

# 5. Bayesian inference on the surviving circuits' parameters
results = ae.perform_bayesian_inference(circuits, freq, Z, num_warmup=2500, num_samples=1000)
```

`results` is a list of `InferenceResult` objects — one per surviving circuit, each carrying its fitted parameters, convergence status, and divergence count.

# Citations

> AutoEIS is now published in the Journal of Open Source Software (JOSS). You can find the paper [here](https://doi.org/10.21105/joss.06256).
>
> > Sadeghi et al., (2025). AutoEIS: Automated equivalent circuit modeling from electrochemical impedance spectroscopy data using statistical machine learning. _Journal of Open Source Software_, 10(109), 6256, https://doi.org/10.21105/joss.06256
>
> > Zhang, Runze, et al. "Editors’ choice—AutoEIS: automated bayesian model selection and analysis for electrochemical impedance spectroscopy." _Journal of The Electrochemical Society_ 170.8 (2023): 086502. https://doi.org/10.1149/1945-7111/aceab2
