# ESMValTool recipes

Recipes in this folder are run by `mkfigs.sh` next to the evaluation notebooks and shown on the same
website: the landing-page table lists a recipe like a notebook, its **Figures** page holds the plots
ESMValTool produced, and its **Recipe** page shows the recipe that ran (ESMValTool's resolved
`recipe_filled.yml`) with the tool versions.

*Status: draft. `om3_mlotst_basic` has run end to end on Gadi (ACCESS-OM3 25 km output, conda/analysis3-26.11:
ACCESS-MOPPy 1.9.0, ESMValTool 2.15.0). It is a pipeline test, not an evaluation recipe.*

## Adding a recipe

1. Put the recipe in this folder as `<name>.yml`. The file name (without `.yml`) is the stem used everywhere:
   the plot files (`<name>_01.png`, ...), the pages, the nav entry and the issue/category tables.
   Use a stem that is not a prefix of another notebook or recipe name, so figures are never attributed to the wrong one.
2. Add `<name>` to the `recipes` list in `../mkfigs.sh`.
3. Optionally add the stem to `ISSUES` / `CATEGORIES` in `../mkfigs_issues.py`, exactly as for a notebook.
4. Run it as a separate job (recipes usually need a different conda environment from the notebooks):

   ```bash
   cd notebooks
   qsub -v MKFIGS_KIND=recipes,MKFIGS_CONDA_MODULE=conda/analysis3-26.11 mkfigs.sh
   python3 -m mkfigs.pushit          # on a login node, once the job has finished
   ```

   Output goes to `mkfigs_output_<ENAME>/`, the same folder the notebooks use: plots as
   `mkmd/<name>_NN.png`, `mkmd/<name>.md`, `<name>_recipe_run.json` (the run marker) and
   `<name>_recipe_filled.yml`. Failures are listed in `mkmd/mkfigs_recipe_errors.log`.

## What the runner does

For each recipe it copies the file into `mkfigs_output_<ENAME>/recipes/`, CMORises the model output it needs
with ACCESS-MOPPy (only if `MOPPY_INPUT_ROOT` is set in `mkfigs.sh`), runs `esmvaltool run`, then collects the
plots. Extra `esmvaltool run` arguments can be passed with the `MKFIGS_ESMVALTOOL_ARGS` environment variable,
for example `qsub -v MKFIGS_KIND=recipes,MKFIGS_ESMVALTOOL_ARGS="--max-parallel-tasks 4" mkfigs.sh`.
Each `esmvaltool run` is limited to `RECIPE_TIMEOUT` minutes (default 120, `MKFIGS_RECIPE_TIMEOUT` to change, 0 for
no limit): ESMValTool can hang instead of exiting when a diagnostic script fails, so the run is killed, reported as
FAILED, and the next recipe starts.

CMORisation runs `python -m mkfigs.moppy_prepare`, which is MOPPy's `moppy-esmval-prepare` plus workarounds
for things MOPPy only supports for ACCESS-ESM1.6 so far (each one should become an upstream MOPPy fix):

| `mkfigs.sh` setting | Why |
|---|---|
| `MOPPY_MODEL_ID=ACCESS-OM3` | MOPPy only CMORises recipe datasets named ACCESS-ESM1-5/1-6, and the CMIP6 CV has no ACCESS-OM3 (mkfigs adds a provisional entry copied from ACCESS-OM2, with ACCESS-OM2's model descriptions replaced by a "provisional" note so the files' `source` attribute doesn't describe MOM5). |
| `MOPPY_PATTERNS` | MOPPy's default raw-file globs follow the ESM1.6 archive; ACCESS-OM3 writes `outputNNN/access-om3.mom6.2d.<var>.1mon.mean.<YYYY>.nc`. One `COMPOUND_NAME:GLOB` per variable, one per line (or `;`-separated). |
| `MOPPY_SUPERGRID`, `MOPPY_NOMINAL_RES` | MOPPy's bundled "25 km" supergrid is ACCESS-OM2's (1080 rows); ACCESS-OM3 25 km has 1152. Use the run's own `ocean_hgrid.nc`. |
| (automatic) | MOPPy writes a `<recipe>.moppy-pinned.yml` copy that pins `version:` on every ACCESS-ESM1-5/1-6 entry, so published ACCESS-ESM1-5 data used for comparison was looked up under the CMORisation date and not found. mkfigs turns the pinning off; ESMValCore already uses the newest version of each variable. |
| (automatic) | 3D fields: MOPPy's ACCESS-OM3 mapping knows MOM6's native vertical axis `zl`, not the `z_l`/`z_i` of the z-remapped `+z` output, so the depth axis stayed un-CMORised (and last) and ESMValCore rejected the files ("olevel: does not exist"). mkfigs reads `z_l`/`z_i` as `zl`/`zi`. The files still have no `lev_bnds` (MOPPy issue; ESMValCore accepts it). |
| `MOPPY_CACHE` | Where the CMORised files go. Default `/g/data/tm70/$USER/moppy-esmval-cache/<ENAME>`: one folder per experiment, because MOPPy writes every ACCESS-OM3 run to the same CMIP6 path (`ACCESS-OM3/omip2/r1i1p1f1/...`). |
| (automatic) | MOPPy asks for creator details on stdin if `~/.moppy/user.yml` is missing, which kills a batch job; mkfigs writes a generic profile to `mkfigs_output_<ENAME>/moppy_user.yml` instead (`MKFIGS_MOPPY_USER_CONFIG` to use your own). |

Only variables with a direct MOPPy mapping from raw ACCESS-OM3 output work today. Directly mapped monthly
`Omon` variables found in the test run: hfds, wfo, pbo, mlotst, tauuo, tauvo, pso, hfrainds, friver, sfdsi, thkcello.
(`zos` is mapped from a raw `SSH` field that ACCESS-OM3 doesn't write; there is no monthly-mean `tos`.)

## Still to confirm

- Institution: the CMIP6 CV has no ACCESS-NRI, so `om3_mlotst_basic.yml` uses `institute: CSIRO-COSIMA` as a placeholder.
- Which recipe to run next. The ACCESS-OM3/CM3 Southern Ocean comparison in `ACCESS-Evaluation-recipes`
  (`web/results/russell-1986-2005`) uses `recipe_russell18jgr`, which needs the Python port in ESMValTool PR 4612
  (not in the released ESMValTool 2.15.0).
