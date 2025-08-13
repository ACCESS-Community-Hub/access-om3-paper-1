# access-om3-paper-1

A collaborative project to create and discuss figures for a description and assessment paper for [ACCESS-OM3](https://github.com/ACCESS-NRI/access-om3-configs).

All community members (and ACCESS-NRI staff) can get write write access to this repository. To get write access, you need to create an issue and request access, please [use this issue template](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/new?template=add-user-request-to--access-om3-paper-1--repository-.md).

The paper is being written [here on Overleaf](https://www.overleaf.com/read/pygvjbmmghsv#b18c9c). Please ask if you'd like edit access.

## How it works

All aspects of the project are tracked through [issues](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/issues). Create an issue to represent each small task, _a single issue is used for each Figure_. Issues will develop to include discussion of analysis methods and figures associated with each task. [A mega-issue is exists here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23) to track all the evaluation metrics. Feel free to add new Figure-issues as sub-issues.

To start contributing to the code, make your own branch directly in this repository, edit away on your branch, and then submit pull requests between your branch and the main branch.

### Guidelines for creating Figures
 - Create issue (one issue per figure) for Figure you are looking to create and add it as a sub-issue to the [mega-issue  here](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23).
 - When posting in the issue, **please include path to notebook to particular commit that created the Figure** (also gives run information but you can include this in the post for convenience)
 - Try to include OM2 comparison!
 - Average the last 10 years of the RYF run
 - Suggestion: pcolor / contourf will handle NaNs in coordinate arrays (if you need pcolormesh/xgcm, use the hack)
 - Once you've created your Figure / uploaded your notebook, please tick off your assigned task in the below list.
 - If it turns out it is not currently possible to complete the metric due to missing diagnostics. Please note that here (example) so we can continue the existing run with the needed output.
([Source](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23#issue-3308829506))

## Notebooks

Notebooks should be grouped in topic-related subfolders in the [notebooks folder](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/blob/main/notebooks).

TODO: provide a template notebook - e.g. see [here](https://github.com/pedrocol/basal_mom5-collaborative-project/blob/main/notebooks/example_notebook.ipynb)

TODO: mention boiler plate

## TODO

TODO: As we figure out the main results and develop the storyline, we can add to the [Results_summary.md](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/blob/main/Results_summary.md) and [Figure_outline.md](https://github.com/ACCESS-Community-Hub/access-om3-25km-paper-1/blob/main/Figure_outline.md).

TODO: define common parameters - e.g. see [here](https://github.com/pedrocol/basal_mom5-collaborative-project?tab=readme-ov-file#plotting-formatsdict)
- experiment runs to use, and terminology for them
- line styles
- climatology start/end dates

