#!/bin/bash
#PBS -l storage=scratch/x77+scratch/tm70+gdata/tm70+gdata/ik11+gdata/ol01+gdata/xp65+gdata/av17+gdata/x77+gdata/g40+gdata/v45+gdata/cj50+gdata/vk83+gdata/zv30+gdata/p73+gdata/rt52+gdata/ia39+gdata/oi10+gdata/fs38+gdata/ct11
#PBS -m ae
#PBS -q normal
#PBS -W umask=0022
#PBS -l ncpus=16
#PBS -l mem=190GB
#PBS -l walltime=24:00:00
#PBS -l jobfs=200GB

# Thin PBS wrapper. ENAME / ESMDIR below, then qsub.
#
# Requires the access-model-mkfigs package, which is provided via the
# external/access-model-mkfigs git submodule (pinned commit) and run
# directly as `python3 -m mkfigs.<module>`. This is an
# interim measure until access-model-mkfigs is installed centrally in
# access3-26.0x.
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


# access-model-mkfigs is loaded straight from the external/access-model-mkfigs
# submodule via PYTHONPATH -- no venv, no pip install, nothing per-experiment.
# Batch runs, interactive notebooks, and follow-up commands below all use the
# same pinned commit -- there's no venv to activate for any of them.
#
## To run interactively:
#   module purge; module use /g/data/xp65/public/modules; module load conda/analysis3
#   (open a notebook — notebooks/mkfigs_bootstrap.py handles the PYTHONPATH bit)
#
## To run follow-up commands (pushit / restore) from a login node:
#   module purge; module use /g/data/xp65/public/modules; module load conda/analysis3
#   export PYTHONPATH="<WFOLDER>/external/access-model-mkfigs/src:${PYTHONPATH}"
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

#
## ESMValTool recipes (optional) -- run alongside the notebooks, shown on the same website
# Recipes live in notebooks/recipes/<name>.yml (see notebooks/recipes/README.md) and are listed in the
# `recipes` list below. They usually need a different conda environment from the notebooks, so run them as a
# separate job that writes into the same mkfigs_output_<ENAME>/ folder, then run pushit once for both:
#1. Edit this file: the recipe list and, if needed, the MOPPY_* settings (raw-file patterns, supergrid)
#1. qsub mkfigs.sh                                                       # notebooks (unchanged)
#1. qsub -v MKFIGS_KIND=recipes,MKFIGS_CONDA_MODULE=conda/analysis3-26.11 mkfigs.sh   # recipes
#1. python3 -m mkfigs.pushit                                             # uploads / publishes both kinds

set -x
module purge
module use /g/data/xp65/public/modules
# MKFIGS_CONDA_MODULE and MKFIGS_KIND are set from the command line, with `qsub -v`, for recipe jobs.
module load "${MKFIGS_CONDA_MODULE:-conda/analysis3-26.08}"
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
    Closure_assessment
    IceOcean_flux_closure
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
# ESMValTool recipe list (optional)
# Recipes are notebooks/recipes/<name>.yml. Only run when this job is submitted with MKFIGS_KIND=recipes
# (or "all"); a plain `qsub mkfigs.sh` ignores them. pushit lists them next to the notebooks.
# ---------------------------------------------------------------------------

recipes=(
    om3_mlotst_basic      # minimal pipeline test: mlotst climatology map + global annual-mean timeseries
    om3_surface_fluxes    # pipeline test: 4 2D variables (u/v points), areacello, ESMValTool ocean scripts
    om3_temp_salt_vs_obs  # pipeline test: 3D thetao/so vs WOA18, EN4 and ACCESS-OM2-025 (needs data-hpc-nci)
    om3_arctic_ocean      # pipeline test: ESMValTool's recipe_arctic_ocean (native grid, PHC3)
    om3_russell18jgr_subset  # pipeline test: Russell et al. 2018 Figs 2, 3b, 3b-2 (NCL)
#    russell18jgr
)

# ACCESS-MOPPy CMORises the raw model output the recipes read, on the fly (via python -m mkfigs.moppy_prepare,
# which adds the ACCESS-OM3 workarounds MOPPy doesn't have yet). Set MOPPY_INPUT_ROOT to "" to skip CMORisation
# (e.g. the data is already CMORised and found by ESMValTool). Default: the experiment folder holding ESMDIR.
# Every MOPPY_* setting can be overridden at submission, e.g. qsub -v MKFIGS_MOPPY_CACHE=/g/data/xx/cache,...
MOPPY_INPUT_ROOT="${MKFIGS_MOPPY_INPUT_ROOT-$(dirname "${ESMDIR}")}"
MOPPY_MODEL_ID="${MKFIGS_MOPPY_MODEL_ID:-ACCESS-OM3}"
# The run's own MOM6 supergrid (see the experiment's config): MOPPy's bundled "25 km" grid is ACCESS-OM2's.
MOPPY_SUPERGRID="${MKFIGS_MOPPY_SUPERGRID:-/g/data/vk83/configurations/inputs/access-om3/share/grids/global.25km/2026.06.11/ocean_hgrid.nc}"
MOPPY_NOMINAL_RES="${MKFIGS_MOPPY_NOMINAL_RES:-25 km}"
MOPPY_WORKERS="${MKFIGS_MOPPY_WORKERS:-4}"
# Where MOPPy finds the raw files for each CMOR variable the recipes use (COMPOUND_NAME:GLOB, relative to
# MOPPY_INPUT_ROOT). MOPPy's defaults follow the ACCESS-ESM1.6 archive; ACCESS-OM3 writes flat outputNNN/ files.
# One entry per line. 3D fields are the z-level (+z) output; Ofx.areacello comes from the static file.
MOPPY_PATTERNS="${MKFIGS_MOPPY_PATTERNS:-
Omon.mlotst:output[0-9]*/access-om3.mom6.2d.mlotst.1mon.mean.*.nc
Omon.hfds:output[0-9]*/access-om3.mom6.2d.hfds.1mon.mean.*.nc
Omon.wfo:output[0-9]*/access-om3.mom6.2d.wfo.1mon.mean.*.nc
Omon.tauuo:output[0-9]*/access-om3.mom6.2d.tauuo.1mon.mean.*.nc
Omon.tauvo:output[0-9]*/access-om3.mom6.2d.tauvo.1mon.mean.*.nc
Omon.thetao:output[0-9]*/access-om3.mom6.3d.thetao+z.1mon.mean.*.nc
Omon.so:output[0-9]*/access-om3.mom6.3d.so+z.1mon.mean.*.nc
Ofx.areacello:output000/access-om3.mom6.static.nc
}"
# The CMORised cache can be large: keep it on /g/data, not in $HOME. One folder per experiment: MOPPy writes
# every ACCESS-OM3 run to the same CMIP6 path (ACCESS-OM3/omip2/r1i1p1f1/...), so a shared cache would mix runs.
MOPPY_CACHE="${MKFIGS_MOPPY_CACHE:-/g/data/tm70/${USER}/moppy-esmval-cache/${ENAME}}"
# ESMValCore's ready-made data-source config for Gadi (CMIP replicas in oi10/fs38, observations in ct11), for
# recipes that compare with other models or observations. Needs those projects in the #PBS -l storage line.
ESMVALTOOL_PRESETS="${MKFIGS_ESMVALTOOL_PRESETS-data-hpc-nci}"
# Minutes allowed per `esmvaltool run` (0 = no limit). ESMValTool can hang instead of exiting when a diagnostic
# script fails; the run is then killed, reported FAILED and the next recipe starts.
RECIPE_TIMEOUT="${MKFIGS_RECIPE_TIMEOUT-120}"

printf -v MKFIGS_RECIPES '%s:' "${recipes[@]}"
MKFIGS_RECIPES="${MKFIGS_RECIPES%:}"

# ---------------------------------------------------------------------------
# Hand off to mkfigs-run (inherits the conda environment loaded above)
# ---------------------------------------------------------------------------
export MKFIGS_NOTEBOOKS MKFIGS_RECIPES
export MKFIGS_MOPPY_INPUT_ROOT="${MOPPY_INPUT_ROOT}" MKFIGS_MOPPY_CACHE="${MOPPY_CACHE}"
export MKFIGS_MOPPY_MODEL_ID="${MOPPY_MODEL_ID}" MKFIGS_MOPPY_PATTERNS="${MOPPY_PATTERNS}"
export MKFIGS_MOPPY_SUPERGRID="${MOPPY_SUPERGRID}" MKFIGS_MOPPY_NOMINAL_RES="${MOPPY_NOMINAL_RES}"
export MKFIGS_MOPPY_WORKERS="${MOPPY_WORKERS}" MKFIGS_ESMVALTOOL_PRESETS="${ESMVALTOOL_PRESETS}" MKFIGS_RECIPE_TIMEOUT="${RECIPE_TIMEOUT}"

exec python3 -m mkfigs.run \
    --kind "${MKFIGS_KIND:-notebooks}" \
    --ename "${ENAME}" \
    --esmdir "${ESMDIR}" \
    --wfolder "${WFOLDER}" \
    "$@"
