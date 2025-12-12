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
            "data_frequency": "1mon",
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
            "data_frequency": "1day",
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
    Falls back to OM3/CM3/Unknown based on simple string matching.
    """
    for key, cfg in exptdict.items():
        if cfg["esm_file"] == esm_file:
            return key, cfg