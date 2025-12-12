# Copyright 2025 ACCESS-NRI and contributors.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

"""
Model-agnostic helper functions for ACCESS-OM3 / ACCESS-CM3
evaluation notebooks.

This module centralises logic for:
- Selecting variables in a model-agnostic way from intake-esm datastores.
- Discovering longitude/latitude fields for plotting.

Author: Ezhilsabareesh Kannadasan
Email: ezhilsabareesh.kannadasan@anu.edu.au
"""

from collections import OrderedDict
from typing import Optional, Tuple

import xarray as xr


def get_lon_lat_from_catalog(
    datastore,
    lon_candidates=("geolon", "geolon_t", "xt_ocean", "lon"),
    lat_candidates=("geolat", "geolat_t", "yt_ocean", "lat"),
) -> Tuple[xr.DataArray, xr.DataArray]:
    """
    Try to discover longitude and latitude fields from an intake-esm datastore.

    Parameters
    ----------
    datastore : intake_esm.core.esm_datastore
        The opened ESM datastore.
    lon_candidates, lat_candidates : tuple of str
        Candidate variable names to try in the catalog.

    Returns
    -------
    (lon, lat) : (xarray.DataArray, xarray.DataArray)
        Longitude and latitude arrays suitable for assigning as CF coords.
    """
    def _find_var(candidates):
        for name in candidates:
            try:
                cat = datastore.search(variable=name)
                if len(cat.df) == 0:
                    continue
                ds = cat.to_dask(
                    xarray_open_kwargs=dict(
                        chunks={},
                        decode_timedelta=True,
                        use_cftime=True,
                    ),
                    xarray_combine_by_coords_kwargs=dict(
                        compat="override",
                        data_vars="minimal",
                        coords="minimal",
                    ),
                )
                if name in ds:
                    da = ds[name]
                else:
                    # sometimes the DataArray is exposed as an attribute
                    da = getattr(ds, name)
                # drop any trivial time-like dims if present
                for d in ("time", "nv", "time_counter"):
                    if d in da.dims and da.sizes.get(d, 1) == 1:
                        da = da.isel({d: 0}, drop=True)
                return da
            except Exception:
                continue
        raise RuntimeError(f"Could not find any of {candidates} in datastore")

    lon = _find_var(lon_candidates)
    lat = _find_var(lat_candidates)

    return lon, lat
def select_variable(
    datastore,
    variable_standard_name: str,
    fallback_variable_names=None,
    data_frequency: Optional[str] = None,
) -> xr.DataArray:
    """
    Select a variable from an intake-esm datastore

    Strategy:
      1. Try CF standard_name via cf_xarray.
      2. If that fails, try user-provided fallback variable names (list).
      3. If that fails, inspect datastore metadata and show available candidates.

    Parameters
    ----------
    datastore : intake_esm.core.esm_datastore
    variable_standard_name : str
        CF standard_name (e.g. "sea_surface_temperature").
    fallback_variable_names : list of str or None
        Acceptable variable names (ordered by priority).
        Notebook should supply this per variable type.
    data_frequency : str or None
        Frequency filter ("1mon", "1day").

    Returns
    -------
    xarray.DataArray
    """
    import cf_xarray  # ensure cf accessor

    if fallback_variable_names is None:
        fallback_variable_names = []

    # Helper: search with or without frequency
    def _search(base_kwargs):
        cat = datastore.search(**base_kwargs)
        if len(cat.df) == 0 and "frequency" in base_kwargs:
            freq = base_kwargs["frequency"]
            base = {k: v for k, v in base_kwargs.items() if k != "frequency"}
            cat2 = datastore.search(**base)
            if len(cat2.df) > 0:
                print(
                    f"No files matched frequency={freq!r}; using any available frequency."
                )
                return cat2
        return cat

    search_base = {}
    if data_frequency:
        search_base["frequency"] = data_frequency

    # --- 1) Try CF standard_name ---
    try:
        cat = _search({**search_base, "variable_standard_name": variable_standard_name})
        if len(cat.df) == 0:
            raise ValueError("No entries found for this CF standard_name.")
        ds = cat.to_dask(
            xarray_open_kwargs={"chunks": {"time": -1}, "decode_timedelta": True, "use_cftime": True},
            xarray_combine_by_coords_kwargs={"compat": "override", "coords": "minimal", "data_vars": "minimal"},
        )
        da = ds.cf[variable_standard_name]
        print(f"Selected variable via CF standard_name: {variable_standard_name}")
        return da
    except Exception as e:
        print("CF-based lookup failed:", repr(e))

    # --- 2) Try fallback variable names ---
    for name in fallback_variable_names:
        try:
            cat = _search({**search_base, "variable": name})
            if len(cat.df) == 0:
                continue
            ds = cat.to_dask(
                xarray_open_kwargs={"chunks": {"time": -1}, "decode_timedelta": True, "use_cftime": True},
                xarray_combine_by_coords_kwargs={"compat": "override", "coords": "minimal", "data_vars": "minimal"},
            )
            da = ds[name]
            print(f"Selected variable via fallback name: {name}")
            return da
        except Exception:
            continue

    # --- 3) Nothing found → list candidates ###
    cat_any = _search(search_base)

    candidates = set()
    if "variable" in cat_any.df.columns:
        for entry in cat_any.df["variable"]:
            if isinstance(entry, str):
                candidates.add(entry)
            else:
                try:
                    candidates.update(entry)
                except TypeError:
                    pass

    raise RuntimeError(
        "\nCould not identify the requested variable.\n"
        f"CF standard_name tried: {variable_standard_name}\n"
        f"Fallback variable names tried: {fallback_variable_names}\n"
        f"Catalog variable candidates: {sorted(candidates)}\n"
    )