# access-om3-paper-1

A collaborative project to create and discuss figures for a description and assessment paper(s) for [ACCESS-OM3](https://github.com/ACCESS-NRI/access-om3-configs). Help is _very_ welcome! Please see `How it works` below to get started.

The paper is being written [here on Overleaf](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c). Please ask Andrew if you'd like edit access (the [link](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c) is "view only"). 

A list of experiments which can be analysed is at in the [Config Docs - Experiments](https://access-om3-configs.access-hive.org.au/Experiments/)


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
 5. When ready to upload, do `git add <path to your notebook>`, `git commit -m "A helpful message"` and `git push -u REMOTE_NAME branch_name` (where `REMOTE_NAME` is the name of your GitHub remote, this defaults to `origin`);
 6. Make a PR on github to merge it into main
 7. Add your authorship details to the [citation file](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/CITATION.cff)

(This assumes you have write access to the repo, if you don't you'll need to [ask for it](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=add-user-request-to--access-om3-paper-1--repository-.md).)


### Guidelines for creating Figures
 - Create an issue (one per figure) for Figure you are looking to create and add it as a sub-issue to the [mega-issue  here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23).
 - When posting in the issue, **please include path to notebook and the commit hash that created the Figure** (also gives run information but you can include this in the post for convenience).
 - Try to include OM2 comparison!
 - Average over the last 10 years of the RYF run
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
esm_file = "/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test3v2-00532b88/datastore.json"

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
