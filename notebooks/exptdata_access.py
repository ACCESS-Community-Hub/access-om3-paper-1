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
import json

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
    (
        "MC_25km_jra_iaf-1.0-beta-5165c0f8",
        {
            "model": "ACCESS-OM3",
            "desc": "ACCESS-OM3 25 km JRA IAF 1.0-beta",
            "esm_file":
                "/g/data/ol01/outputs/access-om3-25km/"
                "MC_25km_jra_iaf-1.0-beta-5165c0f8/datastore.json",
        },
    ),
])

def get_exptname_from_path(path):
    """
    Derive a human-readable experiment name from a datastore path.

    Robust to intake-esm catalogs that live inside a generic intermediate
    directory rather than directly in the experiment directory -- e.g.
    ACCESS-CM3's <expt>/cm3-datastore/cm3-datastore.json, or ACCESS-OM3's
    <expt>/archive/experiment_datastore.json. In both cases the immediate
    parent directory name is a fixed catalog-layout constant, not the
    experiment name, so skip up one more level in those cases.
    """
    generic_parent_dirs = ("cm3-datastore", "archive")
    parts = os.path.normpath(path).split(os.sep)
    name = parts[-2] if len(parts) >= 2 else parts[-1]
    if name in generic_parent_dirs and len(parts) >= 3:
        name = parts[-3]
    return name


def get_experiment_info(key):
    """
    Retrieve metadata for the given experiment key.
    """
    if key not in exptdict:
        raise KeyError(f"Unknown experiment key: {key!r}")
    return exptdict[key]


def guess_experiment_from_esm_file(esm_file, *, model=None):
    """
    Identify experiment configuration, including catalogs staged in jobfs.

    ``model`` can explicitly specify ACCESS-OM3 or ACCESS-CM3. Otherwise use
    the original (resolved) path and, if needed, catalog provenance before
    falling back to the supplied path. Keep esm_file unchanged for loading.

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
    esm_file = os.fspath(esm_file)
    if model is not None and model not in ("ACCESS-OM3", "ACCESS-CM3"):
        raise ValueError(f"Unsupported model: {model!r}")
    original_path = os.path.realpath(esm_file)

    # Resolve the symlink used by live jobs before looking up metadata.
    for key, cfg in exptdict.items():
        if cfg["esm_file"] in (esm_file, original_path):
            return key, {**cfg, "esm_file": esm_file, "model": model or cfg["model"]}

    def model_from_text(text):
        lower = str(text).lower()
        if "cm3" in lower:
            return "ACCESS-CM3"
        if "om3" in lower:
            return "ACCESS-OM3"
        return None

    model_guess = model or model_from_text(original_path)
    if model_guess is None:
        # Copied/newly built catalogs need not be symlinks. Their catalog_file
        # or builder description can still identify the original output path.
        try:
            with open(esm_file) as stream:
                catalog = json.load(stream)
        except (OSError, ValueError):
            catalog = {}
        if isinstance(catalog, dict):
            for field in ("catalog_file", "description"):
                model_guess = model_from_text(catalog.get(field, ""))
                if model_guess:
                    break
    model_guess = model_guess or model_from_text(esm_file) or "Unknown"
    
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