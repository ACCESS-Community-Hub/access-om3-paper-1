#!/bin/bash
#PBS -l storage=gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17+gdata/x77+gdata/g40+gdata/v45+gdata/cj50+gdata/vk83
#PBS -M chris.bull@anu.edu.au
#PBS -m ae
#PBS -q normal
#PBS -W umask=0022
#PBS -l ncpus=16
#PBS -l mem=190GB
#PBS -l walltime=10:00:00
#PBS -o /g/data/tm70/cyb561/repos/access-om3-paper-1/notebooks/
#PBS -e /g/data/tm70/cyb561/repos/access-om3-paper-1/notebooks/

# Thin PBS wrapper. Edit WFOLDER / ENAME / ESMDIR below, then qsub.
# All notebook-execution logic lives in mkfigs_run.py.
#
## Workflow — first run for a new experiment
#1. Create a Figshare token and save it to ~/.figshare_token
#1. cd /g/data/tm70/cyb561 && git clone git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git
#1. Edit this file: set WFOLDER, ENAME, ESMDIR, and the notebook array below
#1. Ensure the experiment storage path is in the #PBS -l storage header above
#1. qsub mkfigs.sh
#1. python3 mkfigs_pushit.py
#1. Log in to Figshare and publish the article
#1. python3 mkfigs_pushit.py --check-figshare-upload   (follow the git commands it prints)
#
## Workflow — adding notebooks to (or re-running) an existing experiment
#1. git fetch --tags
#1. git checkout <docs-{ename}-YYYY.MM.NNN>  # the tag printed by the previous --check-figshare-upload
#1. python3 mkfigs_restore.py   # download previously committed notebooks from Figshare
#1. Edit the notebook array below: add new notebooks, or re-enable ones to re-run
#1. qsub mkfigs.sh
#1. python3 mkfigs_pushit.py    # merges new results with previously committed notebooks
#1. Log in to Figshare and publish the article
#1. python3 mkfigs_pushit.py --check-figshare-upload

#set -x
module purge
module use /g/data/xp65/public/modules
module load conda/analysis3
module list

# ---------------------------------------------------------------------------
# SET THESE
# ---------------------------------------------------------------------------

WFOLDER=/g/data/tm70/cyb561/repos/access-om3-paper-1/

#DS run from June 2025
#ESMDIR=/scratch/tm70/ds0092/access-om3/archive/om3_MC_25km_jra_ryf+wombatlite/intake_esm_ds.json

#AK iaf run 4/9/25
#ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/25km-iaf-test-for-AK-expt-7df5ef4c/datastore.json
#ENAME=25km-iaf-test-for-AK-expt-7df5ef4c

#AK iaf run 9-Dec-25
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-5165c0f8/datastore.json
#ENAME=MC_25km_jra_iaf-1.0-beta-5165c0f8

#AHogg GM* runs
#ENAME=MC_25km_jra_iaf-1.0-beta-gm1-d968c801
#ENAME=MC_25km_jra_iaf-1.0-beta-gm2-5dc49da6
#ENAME=MC_25km_jra_iaf-1.0-beta-gm3-da330542
#ENAME=MC_25km_jra_iaf-1.0-beta-gm4-9fd08880
#ENAME=MC_25km_jra_iaf-1.0-beta-gm5-9b5dbfa9
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/${ENAME}/datastore.json

#WOMBAT run 22-Dec-25
#ENAME=MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a/experiment_datastore.json

#AK iaf run Apr-26
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test3v2-00532b88/datastore.json
ENAME=MC_25km_jra_iaf+wombatlite-test3v2-00532b88

# ---------------------------------------------------------------------------
# Notebook list
# Edit this list to control which notebooks are run.
# ---------------------------------------------------------------------------

#Timeseries_daily_extreme_from_2D_fields ##do not have the outputs needed, see https://github.com/ACCESS-NRI/access-om3-configs/issues/1046#issuecomment-3924389373

array=(
    00_template_notebook
#    #Bottom_age_tracer_in_ACCESS_OM3
#    MLD
#    MLD_max
#    Overturning_in_ACCESS_OM3
#    SeaIce_area
#    #SeaIce_mass_budget_climatology
    SSS
#    SST
#    StraitTransports
#    MeridionalHeatTransport
#    temp-salt-vs-depth-time
#    pPV
#    Equatorial_pacific
#    SSS_Restoring_Timeseries
##   Timeseries_daily_extreme_from_2D_fields
#    timeseries
#    SSH
)
#SSH uses a lot of memory !!

# Pack array into colon-separated env var for mkfigs_run.py
printf -v MKFIGS_NOTEBOOKS '%s:' "${array[@]}"
MKFIGS_NOTEBOOKS="${MKFIGS_NOTEBOOKS%:}"

# ---------------------------------------------------------------------------
# Hand off to Python (inherits the conda environment loaded above)
# ---------------------------------------------------------------------------
export MKFIGS_NOTEBOOKS

exec python3 "${WFOLDER}notebooks/mkfigs_run.py" \
    --ename "${ENAME}" \
    --esmdir "${ESMDIR}" \
    --wfolder "${WFOLDER}" \
    "$@"
