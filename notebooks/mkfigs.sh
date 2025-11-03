#!/bin/bash
#PBS -l storage=gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17
#PBS -M chris.bull@anu.edu.au
#PBS -m ae
#PBS -q normalsr
#PBS -W umask=0022
#PBS -l ncpus=104
#PBS -l mem=496gb
#PBS -l walltime=5:00:00
#PBS -o /g/data/tm70/cyb561/logs
#PBS -e /g/data/tm70/cyb561/logs

# bash script that runs all the notebooks
#set -x
module purge
module use /g/data/xp65/public/modules
#module load conda/analysis3-25.07 
module load conda/analysis3-25.09 #contains papermill 2.6.0 - https://github.com/ACCESS-NRI/ACCESS-Analysis-Conda/issues/310
module list

## workflow
#1. `cd /g/data/tm70/cyb561;git clone git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git`
#1. Edit this file and `chmod u+x mkfigs.sh`
#1. add path to WFOLDER
#1. set path to ESMDIR (ESM-datastore for experiment)
#1. ensure the experiment folder is availble in storage header above
#1. `qsub mkfigs.sh`

## Optional
#1. change email and log settings in above header
#1. this script can also be run from an ARE session


# SET THESE START; for options see: https://access-om3-configs.access-hive.org.au/pr-preview-842/Experiments/
#WFOLDER=/g/data/tm70/cyb561/access-om3-paper-1/
#ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json

#AK iaf run 4/9/25
WFOLDER=/g/data/tm70/cyb561/access-om3-paper-1/
ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/25km-iaf-test-for-AK-expt-7df5ef4c/datastore.json

# SET THESE END

#best not mess with the path here...
OFOL=${WFOLDER}notebooks/mkfigs_output4/

cd ${WFOLDER}
cd notebooks
mkdir -p ${OFOL}

echo ""
echo ""
echo "We are running ALL the notebooks."
echo "We are using ESMDIR: "${ESMDIR}
echo "We are using working folder (WFOLDER): "${WFOLDER}
echo "Output will be in: "${OFOL}
echo ""
echo ""

#make the figures
array=( 00_template_notebook Bottom_age_tracer_in_ACCESS_OM3 DrakePassageTransport GlobalTimeseries MLD MLD_max Overturning_in_ACCESS_OM3 SSS SST StraitTransports salt-vs-depth-time temp-vs-depth-time timeseries MeridionalHeatTransport pPV )
#array=( find_and_load_OM3_25km_ryf_1.0-beta )
for FNAME in "${array[@]}"
do
    echo "Running notebook: "${FNAME}".ipynb"
    python3 run_nb.py ${FNAME}.ipynb; papermill ${FNAME}.ipynb ${OFOL}${FNAME}_rendered.ipynb -p esm_file ${ESMDIR} -p plotfolder ${OFOL} ; jupyter nbconvert --to markdown ${OFOL}${FNAME}_rendered.ipynb
done
