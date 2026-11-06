#!/bin/bash
#PBS -l storage=scratch/x77+gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17+gdata/x77+gdata/g40+gdata/v45+gdata/cj50+gdata/vk83+gdata/zv30+gdata/p73+gdata/rt52+gdata/ia39
#PBS -m ae
#PBS -q normal
#PBS -W umask=0022
#PBS -l ncpus=16
#PBS -l mem=190GB
#PBS -l walltime=10:00:00

# Thin PBS wrapper. ENAME / ESMDIR below, then qsub.
#
# Requires the access-model-mkfigs package, loaded directly from source
# via PYTHONPATH without pip installation. By default, the pinned git
# submodule at external/access-model-mkfigs is used. Set MKFIGS_SRC to
# override this with an external worktree's src directory.
#
# This is an interim measure until access-model-mkfigs is installed
# centrally in conda/analysis3.
#
## Workflow — first run for a new experiment
#1. Create a Figshare token and save it to ~/.figshare_token
#1. cd /g/data/tm70/$USER && git clone --recurse-submodules git@github.com:ACCESS-Community-Hub/access-om3-paper-1.git
#1.   (already cloned without submodules? run: git submodule update --init --recursive)
#1. Edit this file: ENAME, ESMDIR, and the notebook `array` below
#1. Ensure the experiment storage path is in the #PBS -l storage header above
#1. (optional) check the issue list is up to date by running check_mkfigs_issues.py
#1. qsub mkfigs.sh
#1. python3 -m mkfigs.pushit
#1. Log in to Figshare and publish the article
#1. python3 -m mkfigs.pushit --check-figshare-upload   (follow the git commands it prints)


# Batch runs and interactive notebooks use the same mkfigs source:
# the pinned submodule by default, or an external worktree via MKFIGS_SRC.
# No venv or per-experiment pip installation is required.
#
## To submit a PBS job:
#   From the repository root: qsub notebooks/mkfigs.sh
#   From notebooks/:         qsub mkfigs.sh
#
## To use an external mkfigs worktree:
#   qsub -v MKFIGS_SRC=/path/to/access-model-mkfigs/src mkfigs.sh
#
## To run interactively:
#   module purge; module use /g/data/xp65/public/modules; module load conda/analysis3
#   (notebooks/mkfigs_bootstrap.py selects the mkfigs source)
#   Set MKFIGS_SRC before importing mkfigs_bootstrap to use an external worktree.
#
## To run follow-up commands (pushit / restore) from a login node:
#   module purge; module use /g/data/xp65/public/modules; module load conda/analysis3
#   export MKFIGS_SRC="<WFOLDER>/external/access-model-mkfigs/src"
#   (or set MKFIGS_SRC to an external worktree's src directory)
#   export PYTHONPATH="${MKFIGS_SRC}:${PYTHONPATH:-}"
#   python3 -m mkfigs.pushit  [--dry-run] [--check-figshare-upload]
#   python3 -m mkfigs.restore [--ename ENAME] [--force]
#
## To upgrade access-model-mkfigs (bump the pinned submodule commit):
#   cd external/access-model-mkfigs && git fetch --tags && git checkout <tag>
#   cd ../.. && git add external/access-model-mkfigs && git commit -m "Bump access-model-mkfigs to <tag>"


#
## Workflow — adding notebooks to (or re-running) an existing experiment
#1. git fetch --tags
#1. git checkout <{ename}-YYYY.MM.NNN>  # the tag printed by the previous --check-figshare-upload
#1. git submodule update --init --recursive  # in case the pin moved since your last checkout
#1. python3 -m mkfigs.restore   # download previously committed notebooks from Figshare
#1. Edit the notebook array below: add new notebooks, or re-enable ones to re-run
#1. qsub mkfigs.sh
#1. python3 -m mkfigs.pushit    # merges new results with previously committed notebooks
#1. Log in to Figshare and publish the article
#1. python3 -m mkfigs.pushit --check-figshare-upload

set -x
module purge
module use /g/data/xp65/public/modules
module load conda/analysis3-26.08
module list

# ---------------------------------------------------------------------------
# SET THESE
# ---------------------------------------------------------------------------

if [ -n "${PBS_O_WORKDIR:-}" ]; then
    # PBS runs a spool copy, so use the submission directory rather than $0.
    # Support both `qsub notebooks/mkfigs.sh` from the repo root and
    # `qsub mkfigs.sh` from notebooks/.
    if [ -f "$PBS_O_WORKDIR/notebooks/mkfigs.sh" ]; then
        WFOLDER="${PBS_O_WORKDIR%/}/"
    elif [ -f "$PBS_O_WORKDIR/mkfigs.sh" ] && [ -f "$PBS_O_WORKDIR/mkfigs_bootstrap.py" ]; then
        WFOLDER="$(dirname "${PBS_O_WORKDIR%/}")/"
    else
        printf 'ERROR: Submit mkfigs.sh from the repository root or notebooks/ (PBS_O_WORKDIR=%s).\n' "$PBS_O_WORKDIR" >&2
        exit 1
    fi
else
    # Interactive mode: $0 is reliable here.
    WFOLDER="$(dirname "$(readlink -f "$0")")/../"
fi

# 21/7/26 https://access-om3-configs.access-hive.org.au/latest/Experiments/
#Date completed	 Base Configuration	         Model build	Length 	                ESM Datastore
#9-Aug-25	 release-MC_25km_jra_ryf	 2025.05.001	52 years	        /g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf-1.0-beta-cdfb3543/experiment_datastore.json
#16-Sep-25	 25km-iaf-test-for-AK	         2025.05.001	66 years (1958-2023)	/g/data/ol01/outputs/access-om3-25km/25km-iaf-test-for-AK-expt-7df5ef4c/datastore.json
#started 9-Dec-25 dev-MC_25km_jra_iaf	         2025.08.001	57 years (1958-2014) 	/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-5165c0f8/datastore.json
#19-Dec-25	 dev-MC_100km_jra_ryf+wombatlite 2025.08.001	50 years	        /g/data/ol01/outputs/access-om3-100km/MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c/experiment_datastore.json
#22-Dec-25	 dev-MC_25km_jra_ryf+wombatlite	 2025.08.001	30 years	        /g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a/experiment_datastore.json
#started 7-Apr-26 dev-MC_25km_jra_iaf+wombatlite 2025.08.003	66 years (1958-2023)	/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test3v2-00532b88/datastore.json
#1-Jul-26	 dev-MC_25km_jra_iaf+wombatlite	 2026.05.002	66 years (1958-2023)	/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test4-d28e0359/datastore.json
#26-Jun-26	 dev-MC_25km_jra_iaf+wombatlite	 2026.05.002	31 years (1900-1930)	/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf+wombatlite-test3-f4d79e82/experiment_datastore.json
#27-Jul-26	 ACCESS-CM3 PD-control	         --	        50 years	        /g/data/zv30/non-cmip/ACCESS-CM3/cm3-run-27-07-2026-PD-control/cm3-datastore/cm3-datastore.json

ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf-1.0-beta-cdfb3543/experiment_datastore.json
ENAME=MC_25km_jra_ryf-1.0-beta-cdfb3543

ESMDIR=/g/data/ol01/outputs/access-om3-25km/25km-iaf-test-for-AK-expt-7df5ef4c/datastore.json
ENAME=25km-iaf-test-for-AK-expt-7df5ef4c
#
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf-1.0-beta-5165c0f8/datastore.json
ENAME=MC_25km_jra_iaf-1.0-beta-5165c0f8
#
ESMDIR=/g/data/ol01/outputs/access-om3-100km/MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c/experiment_datastore.json
ENAME=MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c
#
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a/experiment_datastore.json
ENAME=MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a
#
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test3v2-00532b88/datastore.json
ENAME=MC_25km_jra_iaf+wombatlite-test3v2-00532b88
#
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test4-d28e0359/datastore.json
ENAME=MC_25km_jra_iaf+wombatlite-test4-d28e0359
#
ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite-test5.1-8f50b769/datastore.json
ENAME=MC_25km_jra_iaf+wombatlite-test5.1-8f50b769
#
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_ryf+wombatlite-test3-f4d79e82/experiment_datastore.json
#ENAME=MC_25km_jra_ryf+wombatlite-test3-f4d79e82

#ESMDIR=/g/data/zv30/non-cmip/ACCESS-CM3/cm3-run-27-07-2026-PD-control/cm3-datastore/cm3-datastore.json
#ENAME=cm3-run-27-07-2026-PD-control
#
#ESMDIR=/g/data/ol01/outputs/access-om3-100km/MC_100km_jra_iaf+wombatlite-test1-e1de2a94/experiment_datastore.json
#ENAME=MC_100km_jra_iaf+wombatlite-test1-e1de2a94

#supplementary
##AHogg GM* runs
#ENAME=MC_25km_jra_iaf-1.0-beta-gm1-d968c801
#ENAME=MC_25km_jra_iaf-1.0-beta-gm2-5dc49da6
#ENAME=MC_25km_jra_iaf-1.0-beta-gm3-da330542
#ENAME=MC_25km_jra_iaf-1.0-beta-gm4-9fd08880
#ENAME=MC_25km_jra_iaf-1.0-beta-gm5-9b5dbfa9
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/${ENAME}/datastore.json

#supplementary
##MPudig backscatter runs July 2026
#ENAME=MC_25km_jra_iaf+wombatlite_bs1-mpudig-backscat1-4c21c151
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite_bs1-mpudig-backscat1-4c21c151/datastore.json
#
#ENAME=MC_25km_jra_iaf+wombatlite_bs2-mpudig-backscat2-0578cc36
#ESMDIR=/g/data/ol01/outputs/access-om3-25km/MC_25km_jra_iaf+wombatlite_bs2-mpudig-backscat2-0578cc36/datastore.json

# ---------------------------------------------------------------------------
# access-model-mkfigs is provided via the external/access-model-mkfigs git
# submodule (pinned commit) rather than pip-installed, so batch runs and
# interactive notebooks use the exact same on-disk copy of the package.
# Use an external mkfigs worktree when MKFIGS_SRC is set.
# Otherwise, use the pinned git submodule.
MKFIGS_SRC="${MKFIGS_SRC:-${WFOLDER%/}/external/access-model-mkfigs/src}"

if [ ! -f "${MKFIGS_SRC}/mkfigs/__init__.py" ]; then
    printf 'ERROR: mkfigs package not found at %s\n' "$MKFIGS_SRC" >&2
    exit 1
fi

export MKFIGS_SRC
export PYTHONPATH="${MKFIGS_SRC}${PYTHONPATH:+:${PYTHONPATH}}"

printf 'Using mkfigs source: %s\n' "$MKFIGS_SRC"
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Notebook list
# Edit this list to control which notebooks are run.
# ---------------------------------------------------------------------------

#Timeseries_daily_extreme_from_2D_fields ##do not have the outputs needed, see https://github.com/ACCESS-NRI/access-om3-configs/issues/1046#issuecomment-3924389373

array=(
#    #00_template_notebook
    Bottom_age_tracer_in_ACCESS_OM3
    MLD
    MLD_max
    Overturning_in_ACCESS_OM3
    SeaIce_area
    SeaIce_mass_budget_climatology  #needs conda/analysis3-26.07 or 26.06
    SSS
    SST
    StraitTransports
    MeridionalHeatTransport
    temp-salt-vs-depth-time
    pPV
    Equatorial_pacific
    SSS_Restoring_Timeseries
    Timeseries_daily_extreme_from_2D_fields
    timeseries
    SSH
    wombatlite_global
    Currents_streamfunction_variability
    SeaIce_Vol
    temp-salt-vs-depth-latitude
    Transects
    WM_evaluation
    MLD_manual
    Transects-mixing
    numerical_mixing_ACCESS_OM3
)
#SSH uses a lot of memory !!

# Pack array into colon-separated env var consumed by mkfigs-run
printf -v MKFIGS_NOTEBOOKS '%s:' "${array[@]}"
MKFIGS_NOTEBOOKS="${MKFIGS_NOTEBOOKS%:}"

# ---------------------------------------------------------------------------
# Hand off to mkfigs-run (inherits the conda environment loaded above)
# ---------------------------------------------------------------------------
export MKFIGS_NOTEBOOKS

exec python3 -m mkfigs.run \
    --ename "${ENAME}" \
    --esmdir "${ESMDIR}" \
    --wfolder "${WFOLDER}" \
    "$@"
