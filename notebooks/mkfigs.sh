#!/bin/bash
#PBS -l storage=scratch/x77+scratch/tm70+gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17+gdata/x77+gdata/g40+gdata/v45+gdata/cj50+gdata/vk83+gdata/zv30+gdata/p73+gdata/rt52+gdata/ia39
#PBS -m ae
#PBS -q normal
#PBS -W umask=0022
#PBS -l ncpus=16
#PBS -l mem=190GB
#PBS -l walltime=24:00:00
#PBS -l jobfs=200GB

## Workflow — first run for a new experiment
# https://github.com/acCESS-nri/access-model-mkfigs#workflow-first-run-for-an-experiment

set -x
module purge
module use /g/data/xp65/public/modules
module load conda/analysis3-26.08
module list

# ---------------------------------------------------------------------------
# SET THESE
# ---------------------------------------------------------------------------

if [ -n "$PBS_O_WORKDIR" ]; then
    # Batch mode: $0 is unreliable under PBS (script runs from a spool dir),
    # but PBS_O_WORKDIR reliably points at the directory qsub was run from.
    WFOLDER="$(dirname "$PBS_O_WORKDIR")/"
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
#
ESMDIR=/g/data/tm70/cyb561/esm_datastores/ol01_full/MC_8km_jra_ryf-test2-expt-c349f800/datastore.json  # built from /g/data/ol01/outputs/access-om3-8km/MC_8km_jra_ryf-test2-expt-c349f800
ENAME=MC_8km_jra_ryf-test2-expt-c349f800

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
export PYTHONPATH="${WFOLDER%/}/external/access-model-mkfigs/src:${PYTHONPATH}"
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
    ocean_stats
    SSH
    wombatlite_global
    Currents_streamfunction_variability
    SeaIce_Vol
    SeaIce_speed
    temp-salt-vs-depth-latitude
    Transects
    WM_evaluation
    MLD_manual
    Transects-mixing
    numerical_mixing_ACCESS_OM3
    Truncation_locations
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
