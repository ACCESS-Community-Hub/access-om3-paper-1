# access-om3-paper-1

A collaborative project to create and discuss figures for a description and assessment paper(s) for [ACCESS-OM3](https://github.com/ACCESS-NRI/access-om3-configs). Help is _very_ welcome! Please see `How it works` below to get started.

The paper is being written [here on Overleaf](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c). Please ask Andrew if you'd like edit access (the [link](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c) is "view only"). 

A list of experiments which can be analysed is in the OM3 configuration docs [Experiments](https://access-om3-configs.access-hive.org.au/latest/Experiments/) table, the latest run should also be in [the template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb). You can navigate to the evaluation of each of these simulations by clicking on the `Evaluation` links. 

Want to browse evaluation of our latest simulation? See:
https://access-om3-paper-1.readthedocs.io/latest/
See something interesting and want to share your thoughts? Click on the related GitHub issue and leave a comment. 

## How it works

All community members (and ACCESS-NRI staff) can get write access to this repository (our preference over using forks). To get write access, you need to create an issue and request access, please [use this issue template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=add-user-request-to--access-om3-paper-1--repository-.md).

All aspects of the project are tracked through [issues](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/issues). Create an issue to represent each small task, _a single issue is used for each Figure_. Issues will develop to include discussion of analysis methods and figures associated with each task. [A mega-issue exists here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23) to track all the evaluation metrics. Feel free to add new Figure-issues as sub-issues.

To start contributing to the code, you have two options:
 1. push your code changes to `main` directly. 
 1. if you'd prefer for your code changes to be reviewed, you can create a new branch directly in this repository, make your changes there, and then open a pull request from your branch into `main`. 

### ⚠️ This repo uses a git submodule

The `notebooks/mkfigs.sh` workflow and the evaluation notebooks depend on the [`access-model-mkfigs`](https://github.com/chrisb13/access-model-mkfigs) package, provided here as a git submodule at `external/access-model-mkfigs`. If you skip the submodule setup, notebooks will fail with `ModuleNotFoundError: No module named 'mkfigs'` and `mkfigs.sh` will fail the same way.

- **Cloning for the first time?** Use `--recurse-submodules`:
```
  git clone --recurse-submodules git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git
```
- **Already have the repo cloned?** Initialise the submodule:
```
  git submodule update --init --recursive
```

### Detailed instructions 

For the first option above omit the branch steps below. This is option 2:

 1. Clone this repository recursively locally (see the note on git submodules above);
 2. Make a new branch with your name `git checkout -b claire`;
 3. `cd` into `notebooks`;
 4. Copy the example notebook, and start hacking away (see `Notebooks` section below for the details);
 5. When ready to upload, do `git add <path to your notebook>`, `git commit -m "A helpful message"` and `git push -u REMOTE_NAME branch_name` (where `REMOTE_NAME` is the name of your GitHub remote, this defaults to `origin`). This repository is getting very large so please do not upload notebooks with lots of embedded figures (on JupyterLab one can right-click and clear output on figure cells);
 6. Make a PR on github to merge it into main
 7. Add your authorship details to the [citation file](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/CITATION.cff)

(This assumes you have write access to the repo, if you don't you'll need to [ask for it](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=add-user-request-to--access-om3-paper-1--repository-.md).)


### Guidelines for creating Figures
 - Create an issue (one per figure) for Figure you are looking to create and add it as a sub-issue to the [mega-issue  here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23).
 - When posting in the issue, **please include path to notebook and the commit hash that created the Figure** (also gives run information but you can include this in the post for convenience).
 - Use the latest 25km IAF run (starting with `MC_25km_jra_iaf` [here](https://access-om3-configs.access-hive.org.au/latest/Experiments/)), averaging over the final decade or more
 - Try to include comparison with the OM2 run `025deg_jra55_iaf_omip2_cycle1`
 - Suggestion: pcolor / contourf will handle NaNs in coordinate arrays (if you need pcolormesh/xgcm, use the hack)
 - Once you've created your Figure / uploaded your notebook, please tick off your assigned task in [the list](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23#issue-3308829506).
 - If it turns out it is not currently possible to complete the metric due to missing diagnostics. [Please note that here](https://github.com/ACCESS-NRI/access-om3-configs/issues/718) so we can continue the existing run with the needed output.
([Source](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23#issue-3308829506))


## Notebooks

Notebooks for figures should be in the [notebooks folder](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks). When starting a new notebook, please use the template [here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb).

To allow us to run all the notebooks at once (interactively or via `mkfigs.sh`/papermill), every notebook must start with the two cells from the template. The first cell needs the tag `parameters` so papermill can inject `esm_file`/`cwd`/`nbname` externally, here are the two cells:

```python
# These first two cells must be in all notebooks!
# It allows us to run all the notebooks at once, this cell has a tag "parameters" which allows us to pass in
# arguments externally using papermill (see mkfigs.sh for details)

# Set esm_file to the datastore for the main experiment of interest
esm_file = "/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test5.1-8f50b769/datastore.json"

# papermill settings. *No need to modify these if running interactively.*
papermill = False                      # `cwd` and `nbname` will be populated by papermill.
cwd = None                             # current working directory
nbname = None                          # notebook name
```

```python
if not papermill:
    import nci_ipynb, os  # requires conda/analysis3-26.03 or later
    cwd = nci_ipynb.dir()
    nbname = nci_ipynb.name()
    os.chdir(cwd)
import mkfigs_bootstrap  # noqa: adds external/access-model-mkfigs/src to sys.path (stop-gap)
from mkfigs import MkmdWriter
mkmd = MkmdWriter(esm_file, nbname, str(cwd), pm=papermill)
```

Rather than saving figures manually, please use the `mkmd` object created above to save figures and add them to the notebook's markdown summary:

```python
# mkmd.savefig(fig, title, caption, dpi=100)
# Save figure and append to markdown summary.
mkmd.savefig(fig, "Template notebook", "Example figure of ACCESS-OM3 sea surface height (m).", dpi=150)
```

Tables can be added the same way:

```python
# mkmd.table(title, table)
# Append a markdown table (list of strings, one per line) to the summary.
mkmd.table("example title", available_variables(datastore_filtered).to_markdown().split('\n'))
```

See [`00_template_notebook.ipynb`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb) for a complete working example.

Once you have finished your notebook, please add its name to the `array` variable in [`mkfigs.sh`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/mkfigs.sh). This allows us to run your new notebook as part of a suite of evaluation notebooks when assessing new simulations.

## For maintainers: running the notebooks and publishing with GitHub Actions

_Most contributors can skip this: it is for the few people who render and publish the figures website._

The **mkfigs** workflow (in the [Actions tab](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/actions/workflows/mkfigs.yml))
runs `notebooks/mkfigs.sh` on Gadi and attaches a **preview** of the figures website to the run. Nothing goes
to Figshare until a second, separate approval. It does the same as running `mkfigs.sh` and `mkfigs-pushit`
by hand; the details and the one-off set-up are in
[access-model-mkfigs](https://github.com/ACCESS-NRI/access-model-mkfigs#running-from-github-actions).

Anyone with write access can start a run, but nothing happens on Gadi until one of the approvers of the
`mkfigs` environment approves it, and publishing needs a second person, from the `mkfigs-publish` environment
(both are listed under **Settings → Environments**). Runs only ever use branches of this repo, never forks.

### Starting a run

**Actions → mkfigs → Run workflow** opens a form. The first field, **mode**, says what to do:

| Mode | Use workflow from | What it does |
|---|---|---|
| `new experiment` | `main` | First run of an experiment: runs the notebooks, then can publish it |
| `update a published experiment` | `main` | Re-runs or adds **only the notebooks you list**, taken from `main`; everything else stays as published. Then can publish them as a new version |
| `preview a branch` | the branch to try, e.g. a PR's | Runs the listed notebooks from that branch on one or more experiments, to look at. **Never publishes** |

The other fields:

| Field | What to put |
|---|---|
| `ename` | The experiment name. It becomes the Figshare article title, the website pages and the `eval-<ename>` branch and tag. For a preview, one or more names, space-separated; an experiment that isn't published yet is written `NAME=/g/data/.../datastore.json` |
| `esm_file` | The experiment's datastore `.json` on Gadi. Needed for a new experiment; for an update, leave blank to use the one it was published with; not used for a preview |
| `notebooks` | Space-separated (e.g. `MLD SST`). For an update or a preview, exactly these run. For a new experiment, blank runs every notebook in `mkfigs.sh` |
| `parameters` | Optional extra [papermill parameters](https://papermill.readthedocs.io/en/latest/usage-parameterize.html) for every notebook in the run, space-separated `NAME=VALUE` (e.g. `NYEARS=5` for the notebooks that average over the last N years). A notebook without that parameter ignores it. Blank means none for a new experiment, and the experiment's published ones for an update or preview. They are recorded in `mkfigs.sh` with the experiment, and shown in the run summary and on the preview page |
| `pick_up_jobs` | Tick only to pick up the jobs of an earlier run that stopped waiting (see below) |
| `mkfigs_version` | Which [access-model-mkfigs](https://github.com/ACCESS-NRI/access-model-mkfigs) (the code that runs the notebooks and builds the pages) to use. `pinned`, the default, keeps a published experiment consistent: an update or preview uses **the version the experiment was published with**; a new experiment uses the one in this branch's `external/access-model-mkfigs`. `latest release` or `master` (unreleased) use something newer, and an update then records the newer version on `eval-<ename>`. Experiments published before this workflow existed need `latest release`. The run's summary says which version ran |

From a terminal, the same thing is e.g.
`gh workflow run mkfigs -R ACCESS-Community-Hub/access-om3-paper-1 -f mode="new experiment" -f ename=<name> -f esm_file=<path>`.

Once approved, the notebooks run as PBS jobs on Gadi (one job per notebook where this repo's
`access-model-mkfigs` supports it, otherwise one job for all). When they finish, the run's summary page links,
for each experiment:

* **the preview page**, which opens straight in the browser: the website's landing page and every figure and
  caption for the experiment. It is reduced: no rendered notebooks, links to other pages don't work, and the
  figures are compressed;
* **the whole website** as a zip, rendered notebooks included, with the two commands to view it locally;
* a table of which notebooks ran and which failed.

Both are kept for 10 days.

### Making the website for a new experiment

1. Start a run from `main` with mode `new experiment`, `esm_file` and `ename` filled in and `notebooks` left blank.
2. Once it is approved and finished, open the preview and check the figures.
3. If they look right, ask a `mkfigs-publish` approver to approve **publish**. That creates and publishes the
   Figshare article (this cannot be undone), then pushes the `eval-<ename>` branch and tag, from which Read the
   Docs builds the website. If something is wrong, reject it: nothing has been published.

### Adding to or re-running a published experiment

1. Start a run from `main` with mode `update a published experiment`, the experiment's `ename`, and in
   `notebooks` the ones to add or re-run. Leave `esm_file` blank to use the datastore it was published with.
2. The run starts from the experiment's published `eval-<ename>` branch and takes **only those notebooks** from
   `main`; everything else (including `mkfigs.sh`) stays as published. The earlier results are restored from
   Figshare, so the preview shows the whole experiment with the new results in it.
3. If it looks right, a `mkfigs-publish` approver approves **publish**: the new results are added to the same
   Figshare article as a new version, committed on top of `eval-<ename>`, and tagged with the next number.

If an updated notebook needs something else that only changed on `main` (a helper file, or a newer conda
module in `mkfigs.sh`), the run fails and shows it in the preview, before anything is published.

### Previewing a branch (e.g. a PR)

To see what a PR's notebooks produce before merging it:

1. The PR's branch has to be in this repo (contributors with write access already work this way). A PR from a
   fork isn't run: push its branch to this repo first, after reading it.
2. Start a run with **Use workflow from** set to the PR's branch, mode `preview a branch`, in `notebooks` the
   ones the PR adds or changes, and in `ename` the experiments to try them on, e.g.
   `MC_25km_jra_iaf+wombatlite-test5.1-8f50b769 MC_100km_jra_iaf+wombatlite-test1-e1de2a94`. Each experiment gets its own job and its own preview page; a published one shows the
   whole experiment with the PR's notebooks re-run.
3. An approver approves the run. Approving runs the PR's code on Gadi under the workflow's NCI account, so
   approvers should read the PR first.
4. Link the preview pages in the PR review. Nothing is published.

### Trying a notebook on any run

To see what a notebook makes of a run (say one that has just finished) without logging in to Gadi: start a
run from `main` with mode `preview a branch`, `notebooks` set to the notebook (e.g. `MLD`), and in `ename`
a name for the run with its datastore, e.g. `my-test-run=/g/data/.../datastore.json`. The preview page and
the zip appear on the run as usual, and nothing is published. The workflow's NCI account needs read access to
the datastore's project.

### If a run stops waiting

GitHub stops a run after 6 hours, so the workflow stops waiting for the PBS jobs after 5. The jobs keep going on
Gadi: start the workflow again with the same `mode` and `ename`, on the same branch, with **pick_up_jobs** ticked,
and it picks them up instead of submitting again.
