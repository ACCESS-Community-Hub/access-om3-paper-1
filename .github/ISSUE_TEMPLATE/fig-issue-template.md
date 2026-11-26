---
name: Issue template for adding a Figure (aspirational)
about: Use this template to share a Figure 
title: 'Evaluation: INSERT DIAGNOSTIC NAME'
labels: ''
assignees: ''

---

### Issue description

Please describe your Figure here.

### Check list

_Don't panic!_ There's a lot of items below but many of them take a few seconds to do. We appreciate people sharing their analysis in _any form_, so if you can't complete the below that's ok.

Time permitting, please consider:

- [ ] When creating the notebook the template was [used](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/00_template_notebook.ipynb). Specifically:
   - [ ] using ESM datastore (e.g. the cell that reads "This cell must be in all notebooks!")
   - [ ] using intake (not an open netcdf command)
- [ ] check if there are observations being read in, are they on a project that we can access (see `SHARED_PROJECTS` in [`check_notebooks.py`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/check_notebooks.py)).
- [ ] Does `mkfigs.sh` run with the new notebook added? Add the name of your notebook to the `array` in [`mkfigs.sh`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/mkfigs.sh), and this issue to `ISSUES` in [`mkfigs_issues.py`](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/notebooks/mkfigs_issues.py), and try to run it as a script on ARE or submit it as a job (see `## workflow` [section for details](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/tree/main?tab=readme-ov-file#notebooks)).
- [ ] the [notebook checks](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/tree/main?tab=readme-ov-file#checks) pass on your pull request
- [ ] check that [figure creation guidelines](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/tree/main?tab=readme-ov-file#guidelines-for-creating-figures) have been followed (where practical)
- [ ] When posting the Figure in the issue below, you have included:
   - [ ] `include path to notebook`
   - [ ] `the commit hash that created the Figure` 
   - [ ] `the path to the OM3 datastore used in the analysis`
- [ ] added [authorship details](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/blob/main/CITATION.cff) to `CITATION.cff` (start your entry with `- given-names:`, like the others)

For [mega issue](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23):
- [ ] create issue for each evaluation diagnostic (using this template);
- [ ] assign yourself as the `assignees`;
- [ ] add new issue as a sub-issue to [the mega issue](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/23);
- [ ] check "ticked off" when you have uploaded the notebook;
- [ ] create link on mega issue to relevant script (once created);
- [ ] Think about sharing your work at a COSIMA or TWG meeting!
