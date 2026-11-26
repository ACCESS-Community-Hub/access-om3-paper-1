# access-om3-paper-1

A collaborative project to create and discuss figures for description and assessment paper(s) for [ACCESS-OM3](https://github.com/ACCESS-NRI/access-om3-configs). Help is _very_ welcome!

To get started, see the _How it works_ section below.

The paper is being written [here on Overleaf](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c). The link is "view only": please ask Andrew Kiss if you'd like edit access.

## Experiment descriptions

The experiments that can be analysed are listed in the [Experiments](https://access-om3-configs.access-hive.org.au/latest/Experiments/) table of the OM3 configuration docs. The latest run should also be in [the template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb). You can navigate to the evaluation of each of these simulations by clicking on the `Evaluation` links.

Want to browse the evaluation of our latest simulation? See https://access-om3-paper-1.readthedocs.io/latest/. See something interesting and want to share your thoughts? Click on the related GitHub issue and leave a comment.

## How it works

All community members (and ACCESS-NRI staff) can get write access to this repository (our preference over using forks). To get write access, you need to create an issue requesting access using [this template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=add-user-request-to--access-om3-paper-1--repository-.md).

All aspects of the project are tracked through [issues](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues), where each small task is captured in a separate issue, i.e., a single issue for each Figure. Issues will develop to include discussion of analysis methods and figures associated with each task.

The [mega-issue](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23) is used to track all evaluation metrics. Please create new Figures as sub-issues of the mega-issue, and follow the checklist in the [issue template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=fig-issue-template.md).

### ⚠️ This repo uses a git submodule

The `notebooks/mkfigs.sh` workflow and the evaluation notebooks depend on the [`access-model-mkfigs`](https://github.com/ACCESS-NRI/access-model-mkfigs) package, provided here as a git submodule at `external/access-model-mkfigs`. If you skip the submodule setup, notebooks will fail with `ModuleNotFoundError: No module named 'mkfigs'` and `mkfigs.sh` will fail the same way.

- **Cloning for the first time?** Use `--recurse-submodules` (see step 1 below).
- **Already have the repo cloned?** Initialise the submodule:
  ```bash
  git submodule update --init --recursive
  ```
- **Cloned before the submodule moved to ACCESS-NRI?** Update its URL in your clone:
  ```bash
  git submodule sync --recursive
  ```

### How to copy the `access-om3-paper-1` repo and create a notebook

To start contributing to the code, you can either:
 * Push your code changes to the `main` branch directly (i.e., follow the steps below, _omitting_ the branch steps), or
 * Create a new branch directly in this repository, make your changes there, and then open a pull request from your branch into `main` to request review (i.e., carry out _all_ steps below).

The second option is recommended: the [notebook checks](#checks) run on every pull request, so problems are found before they reach `main`.

 1. Clone the `access-om3-paper-1` repository, including its submodule. Go to the directory where you want to store the project, e.g. `/g/data/$PROJECT/$USER/`:
    ```bash
    cd /g/data/$PROJECT/$USER/
    git clone --recurse-submodules git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git
    cd access-om3-paper-1
    ```
    This uses [SSH keys for authentication with GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh), which you will also need to push your changes.

 2. Make a new branch called `YOUR-USERNAME` and switch to it:
    ```bash
    git checkout -b YOUR-USERNAME
    ```
    To list all branches (the `*` shows the branch you're on), type `git branch -vv`.

 3. Change into the `notebooks` directory:
    ```bash
    cd notebooks
    ```

 4. Copy the [template notebook](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb) as `YOUR-NOTEBOOK.ipynb` and start hacking away. See the [Notebooks](#notebooks) section below for the details.
    ```bash
    cp 00_template_notebook.ipynb YOUR-NOTEBOOK.ipynb
    ```

 5. Before committing, clear the figure outputs (in JupyterLab, right-click a cell and choose "Clear Outputs of All Cells"). This repository is getting very large, so please don't commit notebooks with lots of embedded figures. Then add and commit the notebook with a short, meaningful message:
    ```bash
    git add YOUR-NOTEBOOK.ipynb
    git commit -m "Notebook for xx evaluation of ACCESS-OM3"
    ```

 6. If this is your first contribution, add your authorship details to the [citation file](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/CITATION.cff) on the same branch. Start your entry with `- given-names:`, followed by `family-names:`, as the existing entries do, or your name won't appear in the author list on the website.

 7. If your notebook follows the template, add it to `mkfigs.sh` and `mkfigs_issues.py` (see [Notebooks](#notebooks)), then commit those changes too.

 8. Push your branch. The first time, you need to set the upstream branch:
    ```bash
    git push --set-upstream origin YOUR-USERNAME
    ```
    If successful, you should see a _branch 'YOUR-USERNAME' set up to track 'origin/YOUR-USERNAME'_ message.

 9. Open a [_New pull request_](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/pulls) for your branch and follow the prompts. Check that the [notebook checks](#checks) pass. Once the pull request has been reviewed and merged into `main`, you can delete your branch.

 10. When you share a Figure in its issue, _include the path to the notebook and the Git hash_ (also known as the _commit hash_) of the commit that created it, as described in [Guidelines for creating Figures](#guidelines-for-creating-figures). The hash is a 40-character string that uniquely identifies a commit, e.g. `b7a4f2c10903c989efe3694481c9325d2040ed2b`; `git rev-parse HEAD` prints the hash of your latest commit.

(This assumes you have write access to the repo. If you don't, you'll need to [ask for it](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=add-user-request-to--access-om3-paper-1--repository-.md).)

### Guidelines for creating Figures
 - Create an issue for the Figure you are looking to create (i.e., one issue per figure), using the [issue template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=fig-issue-template.md).
 - Add it as a sub-issue to [the mega-issue](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23).
 - When posting in the issue, **please include the path to the notebook and the commit hash that created the Figure**. The commit hash also gives run information, which you can also include in the issue for convenience.
 - Use the latest 25km IAF run (starting with `MC_25km_jra_iaf` [here](https://access-om3-configs.access-hive.org.au/latest/Experiments/)), averaging over the final decade or more.
 - If possible, include a comparison with the OM2 run `025deg_jra55_iaf_omip2_cycle1`.
 - Suggestion: pcolor / contourf will handle NaNs in coordinate arrays (if you need pcolormesh/xgcm, use the hack).
 - Once you've created your Figure and uploaded your notebook, please tick off your assigned task in the [mega-issue list](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23#issue-3308829506).
 - If it's not currently possible to complete the metric due to missing diagnostics, please note that in [this issue](https://github.com/ACCESS-NRI/access-om3-configs/issues/718) so we can continue the existing run with the needed output.

([Source](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23#issue-3308829506))

## Notebooks

* Notebooks for figures should be in the [notebooks folder](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks).

* When starting a new notebook, please use [this template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb).

* To allow us to run all the notebooks at once (interactively or via `mkfigs.sh`/papermill), **every notebook must start with the two cells from the template**. The first cell needs the tag `parameters` so papermill can inject `esm_file`/`cwd`/`nbname` externally. Copying the cell from the template copies the tag as well. Here are the two cells:

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

* To allow notebooks to be re-run with different experiments, load the data through the `esm_file` datastore (not hard-coded file paths), and put settings that a run might change, such as `NYEARS` or `averaging_period`, in the `parameters` cell.

* Rather than saving figures manually, please use the `mkmd` object created above to save figures and add them to the notebook's markdown summary:

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

* Once you have finished your notebook, **please add its name (without `.ipynb`) to the `array` variable** in [`mkfigs.sh`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/mkfigs.sh), and its GitHub issue to `ISSUES` in [`mkfigs_issues.py`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/mkfigs_issues.py). This allows us to run your notebook as part of a suite of evaluation notebooks when assessing new simulations, and links it to its issue on the website. If your notebook isn't meant to be run this way (e.g. exploratory or OM2-only analysis), mark it to be skipped instead (see [Checks](#checks)).

### Checks

The [Notebook checks](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/actions/workflows/notebook-checks.yml) workflow checks every pull request that changes a notebook. Errors fail the check; warnings are posted as a comment on the pull request and don't block it. It checks, for example, that:

 - the `parameters` cell and the `MkmdWriter` cell from the template are there, and there is at least one `mkmd.savefig` or `mkmd.table` call;
 - settings such as `NYEARS` and `averaging_period` are in the `parameters` cell, and times aren't selected with calendar years (these break RYF and short runs);
 - data paths are on a shared `/g/data` project that other contributors can read (not `/scratch` or your own project);
 - saved figure outputs are cleared;
 - every notebook in the `mkfigs.sh` `array` exists and has an issue in `mkfigs_issues.py`.

You can run the same checks yourself before pushing (no Gadi or data needed):

```bash
cd notebooks
python check_notebooks.py YOUR-NOTEBOOK.ipynb
```

To exclude a notebook that isn't meant for the `mkfigs.sh` pipeline, add `"mkfigs": {"skip": true, "reason": "OM2-only analysis"}` to its notebook metadata (JupyterLab: Property Inspector > Advanced Tools > Notebook metadata). See [`check_notebooks.py`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/check_notebooks.py) for all the rules.
