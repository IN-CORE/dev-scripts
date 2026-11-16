# pyincore utils

Helpers for testing pyincore, pyincore-viz and pyincore-data:

| Script | What it runs |
|---|---|
| `run_analysis_scripts.sh` | every `tests/pyincore/analyses/*/test_*.py` in a pyincore checkout, as a plain Python script |
| `run_docs_notebooks.py` | every notebook in an incore-docs checkout (including the zipped testbeds), one kernel per notebook, with a pass/fail report |

Both run against whatever pyincore is installed in the active conda environment.
This guide shows the two ways to set that environment up:

- **A. From conda packages:** test a published release or release candidate (RC)
- **B. From source:** test your local pyincore / pyincore-viz / pyincore-data checkouts, installed with `pip -e` into a conda env

Use one environment per version you test (e.g. `incore-1.22.0`, `incore-1.23.0rc2`, `incore-dev`) so the setups don't interfere with each other.

## Channels and versions

| What | Conda channel |
|---|---|
| Releases | `in-core` |
| Release candidates | `in-core/label/rc` |
| Dependencies (geopandas, rasterio, ...) | `conda-forge` |

To see which versions are published:

```bash
conda search -c in-core --override-channels pyincore
conda search -c in-core/label/rc --override-channels pyincore
```

Swap in `pyincore-viz` or `pyincore-data` to check those packages. pyincore 1.22+ needs Python 3.11 or newer.

## A. Install a release or RC from conda

### Release

```bash
conda create -n incore-1.22.0 -c in-core -c conda-forge \
    python=3.11 pyincore=1.22.0 pyincore-viz pyincore-data
conda activate incore-1.22.0
```

### Release candidate

Put `in-core/label/rc` **first**, so its versions take priority over the released ones:

```bash
conda create -n incore-1.23.0rc2 -c in-core/label/rc -c in-core -c conda-forge \
    python=3.11 pyincore=1.23.0rc2 pyincore-viz=1.13.0rc1 pyincore-data=1.1.0rc1
conda activate incore-1.23.0rc2
```

If you leave out a package's version, conda picks the newest one it can solve for. Pin all three
packages when you need to test one exact combination.

## B. Install from your local checkouts (pip, editable)

Use this to test a branch or unreleased changes. Conda installs the heavy geospatial
dependencies, which are painful to install with pip. Then `pip install -e` installs each
checkout without its dependencies, so your edits take effect without reinstalling.

The examples assume the repos sit side by side:

```
INCORE-2.0/
├── pyincore/
├── pyincore-viz/
├── pyincore-data/
├── incore-docs/
└── dev-scripts/
```

### 1. Create the conda env from pyincore's environment file

```bash
conda env create -n incore-dev -f ../pyincore/environment.yml
conda activate incore-dev
```

### 2. (optional) Add pyincore-viz / pyincore-data dependencies

Only needed if you test those packages too, or run notebooks that use them. The simplest way to
get their dependencies is to install the published packages, which step 3 then swaps for your
checkouts:

```bash
conda install -n incore-dev -c in-core/label/rc -c in-core -c conda-forge pyincore-viz pyincore-data
```

This also pulls in the conda package of pyincore; step 3 removes it again.

Don't use `pyincore-viz/environment.yml` or `pyincore-data/environment.yaml` for this. They pin
`pyincore>=1.23.0`, which is only published as an RC, and the viz file doesn't list the
`in-core/label/rc` channel, so it won't solve until 1.23.0 is released.

### 3. Install the checkouts in editable mode

```bash
conda remove -n incore-dev --force -y pyincore pyincore-viz pyincore-data 2>/dev/null
pip install --no-deps -e ../pyincore
pip install --no-deps -e ../pyincore-viz    # optional
pip install --no-deps -e ../pyincore-data   # optional
```

- `--no-deps` stops pip from replacing conda's packages with pip wheels.
- `conda remove --force` removes only those packages and leaves their dependencies in place. That
  way there's only one copy of each package, and it's your checkout.
- If you add a new dependency to a checkout's `requirements.txt`, install it with conda as well
  (`conda install -c conda-forge <pkg>`).

### 4. Check that the env uses your checkout

```bash
python -c "import pyincore; print(pyincore.__file__)"
pip show pyincore | grep -i location
```

Both should point into `../pyincore`, not into `site-packages`. If they point into `site-packages`,
repeat step 3.

## Extra packages for the runners

`run_analysis_scripts.sh` needs nothing beyond pyincore.

`run_docs_notebooks.py` executes notebooks, so it also needs:

```bash
conda install -c conda-forge nbclient nbformat ipykernel pyyaml
```

## Running

### Log in once

Both scripts use pyincore's cached token (`~/.incore/`). The first `IncoreClient()` asks for your
IN-CORE username and password and caches the token for later runs.

- The tokens are per service. Most analysis test scripts connect to the **dev** service
  (`IncoreClient(pyglobals.INCORE_API_DEV_URL)`), and the incore-docs notebooks connect to
  **prod**. Expect to log in to each once.
- `run_analysis_scripts.sh` runs the test files as plain scripts, so they log in with the cached
  token or a terminal prompt. pytest instead reads `tests/pyincore/.incorepw` in the pyincore
  checkout; the scripts don't use that file.
- `run_docs_notebooks.py` checks for the token before it starts and prompts in your terminal if
  needed. Set `INCORE_TOKEN` to skip the prompt, e.g. in CI.
- Notebooks that need other keys read them from the environment, e.g. `CENSUS_API_KEY` for
  `social_vulnerability_score.ipynb`. Export them before you run.

### Analysis scripts

```bash
./utils/pyincore_utils/run_analysis_scripts.sh --pyincore-root ../pyincore
./utils/pyincore_utils/run_analysis_scripts.sh --pyincore-root ../pyincore bridgedamage buildingdamage
./utils/pyincore_utils/run_analysis_scripts.sh --pyincore-root ../pyincore --log logs/analysis_tests.log
```

### incore-docs notebooks

```bash
# what would run / be skipped
./utils/pyincore_utils/run_docs_notebooks.py --docs-root ../incore-docs --list

# everything, two at a time
./utils/pyincore_utils/run_docs_notebooks.py --docs-root ../incore-docs --jobs 2

# a subset (globs on notebook ids; zipped ones look like "<zip>/<path inside>")
./utils/pyincore_utils/run_docs_notebooks.py --docs-root ../incore-docs building_dmg.ipynb "*_testbed*"
```

Results go to `logs/docs_notebooks/<timestamp>/`:

- `report.md`: a pass/fail table showing the failing cell and error for each notebook
- `results.json`: the same results, machine-readable
- `executed/`: every notebook with its outputs, for debugging

`docs_notebooks_skip.yml` lists the notebooks that are skipped by default and the ones that get
longer timeouts. It skips the `create_*` how-tos because they create datasets and hazards on the
IN-CORE services; pass `--run-skipped` to include them.

The report header records the Python path and the pyincore / pyincore-viz / pyincore-data versions.
Check them to confirm a run used the environment you meant to test.
