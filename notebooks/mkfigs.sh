#!/bin/bash
# bash script that runs all the notebooks
set -x
ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json
PFOL=/home/561/cyb561/repos/access-om3-paper-1/notebooks/plots/

python run_nb.py notebook_template.ipynb ${ESMDIR} --plotfolder ${PFOL}
