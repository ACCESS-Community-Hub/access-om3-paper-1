#!/bin/bash
#PBS -l storage=gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17+gdata/x77+gdata/g40+gdata/v45+gdata/cj50
#PBS -M chris.bull@anu.edu.au
#PBS -m ae
#PBS -q normal
#PBS -W umask=0022
#PBS -l ncpus=16
#PBS -l mem=190GB
#PBS -l walltime=12:00:00
#PBS -o /g/data/tm70/cyb561/access-om3-paper-1/notebooks
#PBS -e /g/data/tm70/cyb561/access-om3-paper-1/notebooks

# bash script that runs all the notebooks
#set -x
module purge
module use /g/data/xp65/public/modules
#module load conda/analysis3-25.07 
#module load conda/analysis3-25.08
#module load conda/analysis3-25.09 #contains papermill 2.6.0 - https://github.com/ACCESS-NRI/ACCESS-Analysis-Conda/issues/310

module load conda/analysis3-26.02
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


# SET THESE START
WFOLDER=/g/data/tm70/cyb561/access-om3-paper-1/
ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json

#DS run from June 2025
#ESMDIR=/scratch/tm70/ds0092/access-om3/archive/om3_MC_25km_jra_ryf+wombatlite/intake_esm_ds.json

#AK iaf run 4/9/25
#ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/25km-iaf-test-for-AK-expt-7df5ef4c/datastore.json
#ENAME=25km-iaf-test-for-AK-expt-7df5ef4c

#AK iaf run 9-Dec-25
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-5165c0f8/datastore.json
ENAME=MC_25km_jra_iaf-1.0-beta-5165c0f8

#AHogg GM* runs
#ENAME=MC_25km_jra_iaf-1.0-beta-gm1-d968c801
#ENAME=MC_25km_jra_iaf-1.0-beta-gm2-5dc49da6
#ENAME=MC_25km_jra_iaf-1.0-beta-gm3-da330542
#ENAME=MC_25km_jra_iaf-1.0-beta-gm4-9fd08880
#ENAME=MC_25km_jra_iaf-1.0-beta-gm5-9b5dbfa9
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/${ENAME}/datastore.json

#WOMBAT run 19-Dec-25
ENAME=MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c
ESMDIR=/g/data/ol01/outputs/access-om3-100km/MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c/experiment_datastore.json

#WOMBAT run 22-Dec-25
#ENAME=MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a/experiment_datastore.json

OFOL=${WFOLDER}notebooks/mkfigs_output_${ENAME}/
# SET THESE END

#best not mess with the path here...

cd ${WFOLDER}
cd notebooks
mkdir -p ${OFOL}

#for mkmd
mkdir -p ${OFOL}mkmd/

echo ""
echo ""
echo "We are running ALL the notebooks."
echo "We are using ESMDIR: "${ESMDIR}
echo "We are using working folder (WFOLDER): "${WFOLDER}
echo "Output will be in: "${OFOL}
echo ""
echo ""

#chris progress -- status on all scripts working with mkfigs.sh
#Timeseries_daily_extreme_from_2D_fields ##do not have the outputs needed, see https://github.com/ACCESS-NRI/access-om3-configs/issues/1046#issuecomment-3924389373

#make the figures
array=( 
#   00_template_notebook
    Bottom_age_tracer_in_ACCESS_OM3
    MLD
    MLD_max
    Overturning_in_ACCESS_OM3
    SeaIce_area
    SeaIce_mass_budget_climatology
    SSS
    SST
    StraitTransports
    MeridionalHeatTransport
    temp-salt-vs-depth-time
    pPV
    Equatorial_pacific
    SSS_Restoring_Timeseries
#   Timeseries_daily_extreme_from_2D_fields
    timeseries
    SSH
    StraitTransports
)
#SSH uses a lot of memory !!

## loop through above array 
for FNAME in "${array[@]}"
do
   #this does not work but would be good to have something similar in the future...
   #echo "Running notebook: "${FNAME}".ipynb"
   #if ! grep -q "parameters" ${FNAME}.ipynb; then
   #    echo "Error: No parameters cell found. So skipping notebook: "${FNAME}".ipynb"
   #    exit 1
   #    echo "Notebook: "${FNAME}".ipynb FAILED"
   #else
   python3 run_nb.py ${FNAME}.ipynb; papermill ${FNAME}.ipynb ${OFOL}${FNAME}_rendered.ipynb -p notebook_name ${FNAME}_rendered.ipynb -p esm_file ${ESMDIR} -p plotfolder ${OFOL} ; STATUS=$? ; jupyter nbconvert --to markdown ${OFOL}${FNAME}_rendered.ipynb
   
   if [ "$STATUS" -ne 0 ]; then
       echo "Notebook: "${FNAME}".ipynb FAILED"
   else
       echo "Notebook: "${FNAME}".ipynb SUCCESS"
   fi
   #fi
done
