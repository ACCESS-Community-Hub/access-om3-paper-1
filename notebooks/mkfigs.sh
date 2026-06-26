#!/bin/bash
#PBS -l storage=gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17+gdata/x77+gdata/g40+gdata/v45+gdata/cj50+gdata/vk83
#PBS -M chris.bull@anu.edu.au
#PBS -m ae
#PBS -q normal
#PBS -W umask=0022
#PBS -l ncpus=16
#PBS -l mem=190GB
#PBS -l walltime=12:00:00
#PBS -o /g/data/tm70/cyb561/repos/access-om3-paper-1/notebooks/
#PBS -e /g/data/tm70/cyb561/repos/access-om3-paper-1/notebooks/

# bash script that runs all the notebooks and then uploads output figures to figshare.
#
# Figshare upload
# ---------------
# Set FIGSHARE_TOKEN before running, e.g.:
#
#   export FIGSHARE_TOKEN="$(cat ~/.figshare_token)"
#   qsub mkfigs.sh
#
# or put the token in ~/.figshare_token and this script will read it
# automatically.  If no token is found the upload step is silently skipped
# and only the local markdown files are produced.
#
# The first time the script runs a new private figshare article is created
# for the experiment.  Subsequent runs reuse the same article and skip
# files whose MD5 hash has not changed (incremental uploads).  A manifest
# (mkfigs_output_<ENAME>/mkmd/figshare_manifest.json) records article IDs
# and per-file download URLs so they survive reruns.

#set -x
module purge
module use /g/data/xp65/public/modules
module load conda/analysis3
module list

## workflow
#1. create figshare token
#1. `cd /g/data/tm70/cyb561;git clone git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git`
#1. Edit this file
#1. add path to WFOLDER
#1. set path to ESMDIR (ESM-datastore for experiment)
#1. ensure the experiment folder is availble in storage header above
#1. `qsub mkfigs.sh`

## Optional
#1. change email and log settings in above header
#1. this script can also be run from an ARE session

# SET THESE START

#WFOLDER=/g/data/tm70/cyb561/access-om3-paper-1/
WFOLDER=/g/data/tm70/cyb561/repos/access-om3-paper-1/

#ESMDIR=/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json

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

#WOMBAT run 19-Dec-25
#ENAME=MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c
#ESMDIR=/g/data/ol01/outputs/access-om3-100km/MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c/experiment_datastore.json

#WOMBAT run 22-Dec-25
#ENAME=MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a/experiment_datastore.json

#AK iaf run Apr-26
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test3v2-00532b88/datastore.json
ENAME=MC_25km_jra_iaf+wombatlite-test3v2-00532b88

OFOL=${WFOLDER}notebooks/mkfigs_output_${ENAME}/

# SET THESE END

# ---------------------------------------------------------------------------
# Figshare token resolution
# Read from env var FIGSHARE_TOKEN first; fall back to ~/.figshare_token file.
# ---------------------------------------------------------------------------
if [ -z "${FIGSHARE_TOKEN}" ]; then
    if [ -f "${HOME}/.figshare_token" ]; then
        FIGSHARE_TOKEN="$(cat ${HOME}/.figshare_token | tr -d '[:space:]')"
        echo "Loaded figshare token from ~/.figshare_token"
    else
        echo "WARNING: FIGSHARE_TOKEN not set and ~/.figshare_token not found."
        echo "         Notebook rendering will proceed but figshare upload will be skipped."
        echo "         To enable uploads, run:"
        echo "           export FIGSHARE_TOKEN='<your-personal-access-token>'"
        echo "         or store the token in ~/.figshare_token"
    fi
fi

# ---------------------------------------------------------------------------
# Prepare directories
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Notebook list
# ---------------------------------------------------------------------------

#chris progress -- status on all scripts working with mkfigs.sh
#Timeseries_daily_extreme_from_2D_fields ##do not have the outputs needed, see https://github.com/ACCESS-NRI/access-om3-configs/issues/1046#issuecomment-3924389373

array=(
    00_template_notebook
#    Bottom_age_tracer_in_ACCESS_OM3
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
    # Timeseries_daily_extreme_from_2D_fields
    timeseries
    SSH
    StraitTransports
)

#SSH uses a lot of memory !!

# ---------------------------------------------------------------------------
# Main notebook execution loop
# ---------------------------------------------------------------------------

FAILED_NOTEBOOKS=()
SUCCEEDED_NOTEBOOKS=()

for FNAME in "${array[@]}"
do
    #note: adding "--log-output" can be useful for understanding papermill output
    python3 run_nb.py ${FNAME}.ipynb
    papermill ${FNAME}.ipynb \
        ${OFOL}${FNAME}_rendered.ipynb \
        -p esm_file ${ESMDIR} \
        -p papermill True \
        -p cwd ${OFOL} \
        -p nbname ${FNAME}.ipynb
    STATUS=$?
    jupyter nbconvert --to markdown ${OFOL}${FNAME}_rendered.ipynb
    if [ "$STATUS" -eq 0 ]; then
        jupyter nbconvert --clear-output --to notebook --inplace ${OFOL}${FNAME}_rendered.ipynb
    fi

    if [ "$STATUS" -ne 0 ]; then
        echo "Notebook: ${FNAME}.ipynb FAILED"
        FAILED_NOTEBOOKS+=("${FNAME}")
    else
        echo "Notebook: ${FNAME}.ipynb SUCCESS"
        SUCCEEDED_NOTEBOOKS+=("${FNAME}")
    fi
done

# ---------------------------------------------------------------------------
# Figshare upload
# Upload all PNGs from mkmd/ to figshare and rewrite markdown image URLs.
# This step is skipped if FIGSHARE_TOKEN is empty.
# ---------------------------------------------------------------------------

MDFOL="${OFOL}mkmd/"

if [ -n "${FIGSHARE_TOKEN}" ]; then
    echo ""
    echo "========================================================"
    echo " Uploading figures to figshare"
    echo " Experiment : ${ENAME}"
    echo " Source dir : ${MDFOL}"
    echo "========================================================"

    python3 - <<PYEOF
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath('${WFOLDER}notebooks/mkfigs_configdoc.py')))
# Ensure we import from the working folder of the repo
sys.path.insert(0, '${WFOLDER}notebooks')

from mkfigs_configdoc import figshare_upload_and_rewrite

token      = os.environ.get('FIGSHARE_TOKEN', '${FIGSHARE_TOKEN}')
mdfol      = '${MDFOL}'
experiment = '${ENAME}'

if not token:
    print("[figshare] No token – skipping upload.")
    sys.exit(0)

if not os.path.isdir(mdfol):
    print(f"[figshare] mkmd directory not found: {mdfol} – skipping upload.")
    sys.exit(0)

url_map = figshare_upload_and_rewrite(mdfol=mdfol, experiment=experiment, token=token)

if url_map:
    print("\n[figshare] Summary of uploaded files:")
    for fname, url in sorted(url_map.items()):
        print(f"  {fname}")
        print(f"    {url}")
else:
    print("[figshare] No files were uploaded (nothing new or no PNGs found).")
PYEOF

    FIGSHARE_STATUS=$?
    if [ "$FIGSHARE_STATUS" -ne 0 ]; then
        echo "WARNING: Figshare upload step exited with status ${FIGSHARE_STATUS}"
        echo "         Local markdown files are still available in ${MDFOL}"
    else
        echo ""
        echo "Figshare upload complete."
        echo "Manifest: ${MDFOL}figshare_manifest.json"
        # Print the article URL from the manifest if it exists
        python3 - <<PYEOF2
import json, os
manifest = '${MDFOL}figshare_manifest.json'
if os.path.exists(manifest):
    with open(manifest) as f:
        data = json.load(f)
    art_id = data.get('article_id_${ENAME}')
    if art_id:
        print(f"Figshare article: https://figshare.com/articles/figure/{art_id}")
PYEOF2
    fi
else
    echo ""
    echo "Figshare upload skipped (no token)."
fi

# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------

echo ""
echo "========================================================"
echo " Run complete"
echo "========================================================"
echo "Output folder : ${OFOL}"
echo "Markdown dir  : ${MDFOL}"
if [ ${#SUCCEEDED_NOTEBOOKS[@]} -gt 0 ]; then
    echo "Succeeded (${#SUCCEEDED_NOTEBOOKS[@]}):"
    for nb in "${SUCCEEDED_NOTEBOOKS[@]}"; do echo "  - $nb"; done
fi
if [ ${#FAILED_NOTEBOOKS[@]} -gt 0 ]; then
    echo "FAILED (${#FAILED_NOTEBOOKS[@]}):"
    for nb in "${FAILED_NOTEBOOKS[@]}"; do echo "  - $nb"; done
    echo "Check the PBS error log for details."
fi
echo "========================================================"
