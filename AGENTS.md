# AGENTS.md

Guidance for AI coding agents working in ACCESS-Community-Hub/access-om3-paper-1.

The [`README.md`](README.md) is the reference for how this repo works: read "How it works", "Guidelines for creating Figures" and "Notebooks" before making changes. The figure pipeline itself is documented in the [access-model-mkfigs README](https://github.com/ACCESS-NRI/access-model-mkfigs#readme) (also in `external/access-model-mkfigs/README.md`). This file only lists what an agent is likely to miss.

## How to help

Contributors are mostly scientists who want to get some new analysis done to improve the model. Most of what follows is optional for them, but each item saves the ACCESS-NRI team a clean-up later, because access-model-mkfigs runs every notebook against each new experiment. So do this housekeeping yourself, quietly, as part of the work: make the notebook fit the template, run the checks, add the `mkfigs.sh` and `mkfigs_issues.py` entries, and draft the citation entry. Don't turn it into a list of demands, and don't hold up a contributor's figure over it. Tell them briefly what you did, and ask only for what you can't work out yourself, such as their ORCID.

- **Analysis choices are the user's.** Observations, averaging periods, regions and metrics are their call. You can suggest one; say where it comes from (an issue, a paper, an existing notebook).
- **Keep changes focused.** Ideally, one notebook per PR. Leave other people's notebooks alone, even if they have check warnings; mention anything that looks wrong instead.
- **Be clear about what was run.** Say whether you ran `check_notebooks.py`, and whether the notebook itself was executed (and where: ARE, a PBS job, `mkfigs.sh`). Notebooks need Gadi and its data, so off Gadi you usually can't run them; say so rather than implying a figure is correct.

## Experiments

The experiments to analyse, and the path to each one's intake-esm datastore (the value for `esm_file`), are listed in the [Experiments table](https://access-om3-configs.access-hive.org.au/latest/Experiments/) of the ACCESS-OM3 configuration docs. Take paths from there rather than guessing them or copying them from an old notebook. The template's `esm_file` is usually the latest main run; the README's "Guidelines for creating Figures" says which run to use for the paper.

## Layout

- `notebooks/`: one notebook per figure or diagnostic, plus the pipeline files:
  - `00_template_notebook.ipynb`: the starting point for every notebook.
  - `mkfigs.sh`: the PBS script that runs the notebooks in its `array` against one experiment (`ENAME`, `ESMDIR`).
  - [`mkfigs_issues.py`](notebooks/mkfigs_issues.py): maps each notebook to its GitHub issue(s) (`ISSUES`), which are linked from the notebook's page on the website, and groups the notebooks into the categories of [#23](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23) (`CATEGORIES`). `check_mkfigs_issues.py` lists what it has for each notebook in the `mkfigs.sh` array.
  - `check_notebooks.py`: the static checks run in CI (see [Checks](#checks)).
  - `mkfigs_bootstrap.py`: puts the submodule on `sys.path` for interactive notebooks. Keep it.
- `external/access-model-mkfigs`: [ACCESS-NRI/access-model-mkfigs](https://github.com/ACCESS-NRI/access-model-mkfigs) as a git submodule, pinned to a commit.
- `documentation/`: the MkDocs site at https://access-om3-paper-1.readthedocs.io, mostly written by `mkfigs.pushit` (see [Generated files](#generated-files)).
- `CITATION.cff`: the contributors. It is also the author list on the website.

## Adding or changing a notebook

- **Each new diagnostic gets an issue.** If there isn't one already, offer to open it with the [figure issue template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=fig-issue-template.md), titled `Evaluation: <name of diagnostic>`, as a sub-issue of the mega-issue [#23](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23). Its number is what goes in `mkfigs_issues.py`.
- **Start from `00_template_notebook.ipynb`** and keep its first two code cells:
  - The first code cell is the only cell tagged `parameters`, and sets `esm_file`, `papermill`, `cwd` and `nbname`. Papermill replaces these values when `mkfigs.sh` runs the notebook.
  - The second cell creates `mkmd = MkmdWriter(...)`. Copy it unchanged.
- **Read model output through the datastore at `esm_file`** (intake-esm), not hard-coded paths to model output files. Then the same notebook runs on any experiment: other resolutions, RYF or IAF forcing, and ACCESS-CM3.
- **Settings a run might change go in the `parameters` cell**, e.g. `NYEARS` and `averaging_period`. Select times relative to the data (e.g. the last `NYEARS` years), not with calendar years: literal years such as `slice("1958", "1962")` break RYF runs (model years from 1900) and short runs.
- **Data must be readable by everyone.** Observations and other inputs must be on a shared `/g/data` project listed in `SHARED_PROJECTS` in `check_notebooks.py`.
- **Send results through `mkmd`.** At least one uncommented `mkmd.savefig(fig, title, caption, dpi=...)` or `mkmd.table(title, lines)` call, or nothing reaches the website. Don't save figures with `plt.savefig` for the website.
- **Clear figure outputs before committing.** The repo is already large, and more than 1 MB of saved images gets a warning. Text and table outputs are fine.
- **To run the notebook in the pipeline**, add its name without `.ipynb` to the `array` in `mkfigs.sh`, and add an entry for it to `ISSUES` in `mkfigs_issues.py`, in the same form as the others (e.g. `"SST": f"[#9]({_GH}/9) — Global SST bias",`). If the issue isn't in a `CATEGORIES` group yet, the notebook appears under "Miscellaneous"; add it to the group that matches #23 if one fits.
- **A notebook that isn't for the pipeline** (exploratory work, OM2-only analysis, a one-off script) gets `"mkfigs": {"skip": true, "reason": "..."}` in its notebook metadata instead. Don't add it to the `array`.
- **Leave the run settings in `mkfigs.sh` alone** unless asked: the `ENAME`/`ESMDIR` lines (the last uncommented pair wins), the `#PBS` header and the `conda/analysis3` module. These belong to whoever runs the pipeline.

## access-model-mkfigs

- Don't edit `external/access-model-mkfigs` here. Changes to the package go to [ACCESS-NRI/access-model-mkfigs](https://github.com/ACCESS-NRI/access-model-mkfigs) as a PR. It is shared with [access-cm3-paper-1](https://github.com/ACCESS-Community-Hub/access-cm3-paper-1), so a change must work for both.
- Bump the pinned commit only when asked, in a PR of its own (see "Upgrading the pinned version" in the mkfigs README). If the template's first two cells or the `MkmdWriter` calls change in mkfigs, update `00_template_notebook.ipynb`, the README's "Notebooks" section and `check_notebooks.py` in the same PR.
- A clone without the submodule fails with `ModuleNotFoundError: No module named 'mkfigs'`. Run `git submodule update --init --recursive`; don't install `mkfigs` some other way.

## Checks

The [Notebook checks](.github/workflows/notebook-checks.yml) workflow runs `notebooks/check_notebooks.py` on every PR that changes `notebooks/` and on every push to `main`. Errors fail the check. Warnings are posted as a PR comment and don't block. The rules are listed in the script.

- Run it before pushing. It needs only the Python standard library, no Gadi or data:

  ```shell
  cd notebooks
  python check_notebooks.py                       # all notebooks, and the mkfigs.sh array
  python check_notebooks.py MyNotebook.ipynb      # just these
  ```

- Errors fail the check, so fix any in the notebooks the PR changes. Fix their warnings too where it's quick; otherwise mention them. Findings in other notebooks aren't the PR's to fix.
- Don't edit `check_notebooks.py`, or mark a notebook to skip, just to make a finding go away.
- The workflow doesn't run on a PR that changes only `CITATION.cff` or the docs, so check those yourself (see below).

## Citation

Contributors are listed in `CITATION.cff`, which is also the author list on the website. If the user isn't in it yet, offer to add them in the same PR as their first contribution.

- Ask for whatever you can't find (name as they want it cited, affiliation, email, ORCID). Never guess an ORCID.
- Add a new entry at the end of `authors:`, in the same form as the existing ones. The entry must start with `- given-names:`, with `family-names:` on the next line. mkfigs reads this file line by line to build the website's author list, and an entry that starts with `- family-names:` is silently left out.
- Write the names plain or in double quotes, not single quotes: mkfigs strips only double quotes, so single quotes would appear on the website. The ORCID is the full URL, as in the other entries.
- Don't change, reorder or reformat other people's entries.
- Validate the file (the schema check doesn't catch the ordering rule above):

  ```shell
  pip install cffconvert
  cffconvert --validate -i CITATION.cff
  ```

## Pull requests

- Work on a branch in this repo rather than a fork. Contributors can ask for write access (see the README), and a PR from a fork doesn't get the checks comment.
- Prefer a PR to pushing to `main` (the README allows both), so the checks run before the change is merged.
- In the PR description, link the figure's issue (a sub-issue of [#23](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23)), give the datastore the notebook was run with, and say what was run (see [How to help](#how-to-help)). Say how AI tools were used.
- When posting a figure in its issue, include the path to the notebook and the commit that made the figure (README, "Guidelines for creating Figures").

## Generated files

These are written by `mkfigs.pushit` when an experiment is published. Don't edit them by hand:

- the `nav:` block of `documentation/mkdocs.yml`, the pages under `documentation/docs/pages/experiments/` and the top of `documentation/docs/pages/index.md`. Hand-written text in `index.md` must be inside `<!-- preamble-extra -->` ... `<!-- /preamble-extra -->` above the `<!-- experiments -->` anchor.
- notebooks as papermill ran them (with an injected `# Parameters` cell) and `mkfigs_output_<ENAME>/`. These never go on `main`: they are committed on `eval-<ENAME>` branches and tagged `<ENAME>-YYYY.MM.NNN`. Don't create, move or delete those branches and tags.

## Gadi

The notebooks run on Gadi at NCI, usually on ARE, and read data under `/g/data`.

- Python environment: `module use /g/data/xp65/public/modules && module load conda/analysis3-26.08`. Use the same version as `mkfigs.sh`.
- Clone with the submodule: `git clone --recurse-submodules git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git`.
