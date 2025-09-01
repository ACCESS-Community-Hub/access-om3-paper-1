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
module use /g/data/xp65/public/modules
module load conda/analysis3
module load conda/analysis3-25.07
module list


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
# SET THESE END

#best not mess with the path here...
OFOL=${WFOLDER}notebooks/mkfigs_output/

cd ${WFOLDER}
cd notebooks
mkdir -p ${OFOL}

#make the figures
python3 run_nb.py notebook_template.ipynb ${ESMDIR}         --plotfolder ${OFOL}
python3 run_nb.py DrakePassageTransport.ipynb ${ESMDIR}     --plotfolder ${OFOL}
python3 run_nb.py Overturning_in_ACCESS_OM3.ipynb ${ESMDIR} --plotfolder ${OFOL}

#make a html version of the notebook 
python3 run_nb.py notebook_template.ipynb ${ESMDIR}         
python3 run_nb.py DrakePassageTransport.ipynb ${ESMDIR}     
python3 run_nb.py Overturning_in_ACCESS_OM3.ipynb ${ESMDIR} 
