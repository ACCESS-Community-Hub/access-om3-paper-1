# Copyright 2025 ACCESS-NRI and
# contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Centralised metadata and experiment info helper for ACCESS-OM3 and ACCESS-CM3
model-agnostic analysis notebooks.

Inspired by Andrew's https://github.com/COSIMA/ACCESS-OM2-1-025-010deg-report/blob/master/figures/exptdata.py, 
and simplified for OM3/CM3 workflows.

Author: Ezhilsabareesh Kannadasan
Email: ezhilsabareesh.kannadasan@anu.edu.au
"""

from collections import OrderedDict
import os

# Dictionary of known experiments with model name, datastore path, etc.
# Add new experiments here as needed.
exptdict = OrderedDict([
    (
        "cm3_demo",
        {
            "model": "ACCESS-CM3",
            "desc": "ACCESS-CM3 25 km beta demo",
            "esm_file":
                "/g/data/zv30/non-cmip/ACCESS-CM3/"
                "cm3-run-11-08-2025-25km-beta-om3-new-um-params/"
                "cm3-demo-datastore/cm3-demo-datastore.json",
        },
    ),
    (
        "om3_25km_iaf_7df5ef4c",
        {
            "model": "ACCESS-OM3",
            "desc": "ACCESS-OM3 25 km IAF test (7df5ef4c)",
            "esm_file":
                "/g/data/ol01/access-om3-output/access-om3-025/"
                "25km-iaf-test-for-AK-expt-7df5ef4c/datastore.json",
        },
    ),
    (
        "om3_25km_ryf_1_0_beta",
        {
            "model": "ACCESS-OM3",
            "desc": "ACCESS-OM3 25 km JRA RYF 1.0-beta",
            "esm_file":
                "/g/data/ol01/access-om3-output/access-om3-025/"
                "MC_25km_jra_ryf-1.0-beta/experiment_datastore.json",
        },
    ),
])

def get_experiment_info(key):
    """
    Retrieve metadata for the given experiment key.
    """
    if key not in exptdict:
        raise KeyError(f"Unknown experiment key: {key!r}")
    return exptdict[key]


def guess_experiment_from_esm_file(esm_file):
    """
    Identify experiment configuration based on the datastore path.

    Returns
    -------
    expt_key : str
        Experiment key if found in exptdict, otherwise "unknown_experiment".
    info : dict
        Metadata dictionary containing:
            - model : str ("ACCESS-OM3", "ACCESS-CM3", or "Unknown")
            - desc  : str (human-readable description)
            - esm_file : str (the path passed in)

    This function *always* returns a valid (key, info) tuple,
    so the notebook can safely unpack it.
    """
    # 1. Exact match with known experiments in exptdict
    for key, cfg in exptdict.items():
        if cfg["esm_file"] == esm_file:
            return key, cfg

    # 2. Fallback: infer model type from path
    lower = esm_file.lower()
    if "cm3" in lower:
        model_guess = "ACCESS-CM3"
    elif "om3" in lower:
        model_guess = "ACCESS-OM3"
    else:
        model_guess = "Unknown"

    # 3. Construct a usable fallback metadata record
    fallback_info = {
        "model": model_guess,
        "desc": f"{model_guess} (unregistered experiment)",
        "esm_file": esm_file,
    }

    # ---------------------------------------------------------
    # 4. Always return a tuple — never return None
    # ---------------------------------------------------------
    return "unknown_experiment", fallback_info