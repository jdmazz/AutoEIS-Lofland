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

Run from the repository root:

```bash
conda env create -f environment.yml
conda activate autoeis-lofland
python -m autoeis install
```

The install step fetches Julia 1.10 and the pinned `EquivalentCircuits.jl` automatically; no separate Julia install is required. Do not run `pip install -U autoeis`; that installs the upstream package from PyPI and ignores this fork's pin.

## Usage

TODO

> [!WARNING]
> The examples are designed to be run interactively, so you should use a Jupyter notebook-like environment like Jupyter Lab, IPython Notebook, or VSCode. The examples may not work as expected if you run them in a non-interactive environment like a Python REPL. For a smooth experience, please use a supported environment.

# Citations

> AutoEIS is now published in the Journal of Open Source Software (JOSS). You can find the paper [here](https://doi.org/10.21105/joss.06256).
>
> > Sadeghi et al., (2025). AutoEIS: Automated equivalent circuit modeling from electrochemical impedance spectroscopy data using statistical machine learning. _Journal of Open Source Software_, 10(109), 6256, https://doi.org/10.21105/joss.06256
>
> > Zhang, Runze, et al. "Editors’ choice—AutoEIS: automated bayesian model selection and analysis for electrochemical impedance spectroscopy." _Journal of The Electrochemical Society_ 170.8 (2023): 086502. https://doi.org/10.1149/1945-7111/aceab2

# Acknowledgement

Thanks to Prof. Jason Hattrick-Simpers, Dr. Robert Black, Dr. Debashish Sur, Dr. Parisa Karimi, Dr. Brian DeCost, Dr. Kangming Li, and Prof. John R. Scully for their guidance and support. Also, thanks to Dr. Shijing Sun, Prof. Keryn Lian, Dr. Alvin Virya, Dr. Austin McDannald, Dr. Fuzhan Rahmanian, and Prof. Helge Stein for their feedback and discussions. Special shoutout to Prof. John R. Scully and Dr. Debashish Sur for letting us use their corrosion data to showcase the functionality of AutoEIS—your help has been invaluable!
