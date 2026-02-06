#!/bin/bash
#PBS -l storage=gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17+gdata/x77
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
#module load conda/analysis3-25.07 
module load conda/analysis3-25.09 #contains papermill 2.6.0 - https://github.com/ACCESS-NRI/ACCESS-Analysis-Conda/issues/310

#module load conda/analysis3-26.02
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

#AK iaf run 9-Dec-25
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-5165c0f8/datastore.json

#AHogg GM* runs
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-gm1-d968c801/datastore.json
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-gm2-5dc49da6/datastore.json
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-gm3-da330542/datastore.json
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-gm4-9fd08880/datastore.json
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-gm5-9b5dbfa9/datastore.json

# SET THESE END

#best not mess with the path here...
OFOL=${WFOLDER}notebooks/mkfigs_output_MC_25km_jra_iaf-1.0-beta-gm4-9fd08880/

cd ${WFOLDER}
cd notebooks
mkdir -p ${OFOL}

mkdir -p ${WFOLDER}notebooks/mkmd/

echo ""
echo ""
echo "We are running ALL the notebooks."
echo "We are using ESMDIR: "${ESMDIR}
echo "We are using working folder (WFOLDER): "${WFOLDER}
echo "Output will be in: "${OFOL}
echo ""
echo ""

#make the figures
array=( 
#    00_template_notebook 
#    Bottom_age_tracer_in_ACCESS_OM3 
#    DrakePassageTransport       #WORKS (minor bug)
#    GlobalTimeseries            #WORKS (minor bug)
    MLD                         #WORKS
#    MLD_max                     #WORKS
#    Overturning_in_ACCESS_OM3
#    SeaIce_area
#    SeaIce_mass_budget_climatology
#    SSS 
#    SST 
#    StraitTransports 
#    salt-vs-depth-time 
#    temp-vs-depth-time 
#    timeseries 
#    MeridionalHeatTransport 
#    pPV
#    Equatorial_pacific
)
#array=( find_and_load_OM3_25km_ryf_1.0-beta )
for FNAME in "${array[@]}"
do
    echo "Running notebook: "${FNAME}".ipynb"
    python3 run_nb.py ${FNAME}.ipynb; papermill ${FNAME}.ipynb ${OFOL}${FNAME}_rendered.ipynb -p notebook_name ${FNAME}_rendered.ipynb -p esm_file ${ESMDIR} -p plotfolder ${OFOL} ; jupyter nbconvert --to markdown ${OFOL}${FNAME}_rendered.ipynb
done
