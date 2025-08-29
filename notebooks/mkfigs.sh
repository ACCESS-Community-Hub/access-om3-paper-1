#!/bin/bash
#PBS -l storage=gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65
#PBS -M chris.bull@anu.edu.au
#PBS -m ae
#PBS -q normal
#PBS -W umask=0022
#PBS -l ncpus=8
#PBS -l mem=24gb
#PBS -l walltime=2:00:00
#PBS -o /g/data/tm70/cyb561/logs
#PBS -e /g/data/tm70/cyb561/logs

# bash script that runs all the notebooks
set -x
module use /g/data/xp65/public/modules
module load conda/analysis3
module load conda/analysis3-25.07
module list

# SET THESE START
#WFOLDER is where you have cloned: `git clone git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git `
WFOLDER=/g/data/tm70/cyb561/access-om3-paper-1/
ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json
# SET THESE END

PFOL=${WFOLDER}notebooks/plots/

cd ${WFOLDER}
cd notebooks
mkdir -p ${PFOL}

python3 run_nb.py notebook_template.ipynb ${ESMDIR} --plotfolder ${PFOL}
python3 run_nb.py DrakePassageTransport.ipynb ${ESMDIR} --plotfolder ${PFOL}


