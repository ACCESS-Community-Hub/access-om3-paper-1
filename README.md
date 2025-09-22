# access-om3-paper-1

A collaborative project to create and discuss figures for a description and assessment paper(s) for [ACCESS-OM3](https://github.com/ACCESS-NRI/access-om3-configs). Help is _very_ welcome! Please see `How it works` below to get started.

The paper is being written [here on Overleaf](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c). Please ask Andrew if you'd like edit access (the [link](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c) is "view only"). 

## How it works

All community members (and ACCESS-NRI staff) can get write write access to this repository (our preference over using forks). To get write access, you need to create an issue and request access, please [use this issue template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=add-user-request-to--access-om3-paper-1--repository-.md).

All aspects of the project are tracked through [issues](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/issues). Create an issue to represent each small task, _a single issue is used for each Figure_. Issues will develop to include discussion of analysis methods and figures associated with each task. [A mega-issue exists here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23) to track all the evaluation metrics. Feel free to add new Figure-issues as sub-issues.

To start contributing to the code, you have two options:
 1. push your code changes to `main` directly. 
 1. if you'd prefer for your code changes to be reviewed, you can create a new branch directly in this repository, make your changes there, and then open a pull request from your branch into `main`. 

### Detailed instructions 

For the first option above omit the branch steps below. This is option 2:

 1. Clone this repository locally;
 2. Make a new branch with your name `git checkout -b claire`;
 3. `cd` into `notebooks`;
 4. Copy the example notebook, and start hacking away;
 5. When ready to upload, do `git add <path to your notebook>`, `git commit -m "A helpful message"` and `git push -u REMOTE_NAME branch_name` (where `REMOTE_NAME` is the name of your GitHub remote, this defaults to `origin`);
 6. Make a PR on github to merge it into main

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

Notebooks for figures should be in the [notebooks folder](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/blob/main/notebooks). When starting a new notebook, please use the template [here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb). 

To allow us later to run all the notebooks at once, please use the boilerplate at the top of the script, namely this second cell:
```python
#parameters

### USER EDIT start
esm_file='/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json'
plotfolder='/g/data/tm70/cyb561/access-om3-paper-1/notebooks/mkfigs_output/2/'
dpi=300
### USER EDIT stop

import matplotlib as mpl
import os
%matplotlib inline
mpl.rcParams['figure.dpi']= dpi

os.makedirs(plotfolder, exist_ok=True)

 # a similar cell under this means it's being run in batch
print("ESM datastore path: ",esm_file)
print("Plot folder path: ",plotfolder)
```

It is important that you use `esm_file` and if needed `plotfolder` in your script as done in `00_template_notebook.ipynb` (this allows us to re-run your script later with different experiments), here's [examples](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb):
```python
datastore = intake.open_esm_datastore(
    esm_file,
    columns_with_iterables=[
        "variable",
        "variable_long_name",
        "variable_standard_name",
        "variable_cell_methods",
        "variable_units"
    ]
)
```
and `plt.savefig(plotfolder+'exampleout.png')`. This cell needs to have the tag `parameters`, copying this cell will copy the tag as well but [you can also set this on other cells](https://papermill.readthedocs.io/en/latest/usage-parameterize.html) should you wish to parameterize other parts of the script. This allows us to [pass in arguments externally using papermill](https://papermill.readthedocs.io/en/latest/usage-cli.html) (see [mkfigs.sh for details](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/mkfigs.sh))

Once you have finished your notebook, please add the name of your notebook to the `array` variable in [this script](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/8f636ad6862dd141378c0f0f470c4c8c895dea38/notebooks/mkfigs.sh#L62-L63). This allows us to run your new notebook as part of a suite of evaluation notebooks when assessing new simulations.

## TODO

TODO: As we figure out the main results and develop the storyline, we can add to the [Results_summary.md](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/blob/main/Results_summary.md) and [Figure_outline.md](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/blob/main/Figure_outline.md).

TODO: define common parameters - e.g. see [here]([https://github.com/pedrocol/basal_mom5-collaborative-project?tab=readme-ov-file#plotting-formatsdict](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/find_and_load_OM3_25km_ryf_1.0-beta.ipynb))
- experiment runs to use, and terminology for them
- line styles
- climatology start/end dates

