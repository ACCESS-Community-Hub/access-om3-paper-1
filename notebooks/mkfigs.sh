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
#set -x
module purge
module use /g/data/xp65/public/modules
module load conda/analysis3-25.07
module list

#enable venv with papermill
source /g/data/tm70/cyb561/access-om3-paper-1/venv/bin/activate

## workflow
#1. `cd /g/data/tm70/cyb561;git clone git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git`
#1. Edit this file and `chmod u+x mkfigs.sh`
#1. add path to WFOLDER
#1. set path to ESMDIR (ESM-datastore for experiment)
#1. ensure the experiment folder is availble in storage header above
#1. `qsub mkfigs.sh`

## Optional
#1. remove "plotfolder" if you would like a html rendered version of the notebook
#1. change email and log settings in above header


# SET THESE START
WFOLDER=/g/data/tm70/cyb561/access-om3-paper-1/
ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json

#DS run from June 2025
#ESMDIR=/scratch/tm70/ds0092/access-om3/archive/om3_MC_25km_jra_ryf+wombatlite/intake_esm_ds.json

# SET THESE END

#best not mess with the path here...
OFOL=${WFOLDER}notebooks/mkfigs_output/

cd ${WFOLDER}
cd notebooks
mkdir -p ${OFOL}

#make the figures
python3 run_nb.py notebook_template.ipynb; papermill notebook_template.ipynb ${OFOL}notebook_template_rendered.ipynb -p esm_file ${ESMDIR} -p plotfolder ${OFOL} ; jupyter nbconvert --to markdown ${OFOL}notebook_template_rendered.ipynb

#this didn't work for me...
#papermill notebook_template.ipynb notebook_template_rendered.ipynb -k analysis3-25.07 -p esm_file ${ESMDIR} -p plotfolder ${OFOL} 

