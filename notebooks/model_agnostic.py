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
from typing import Optional, Sequence, Tuple, Dict, Any

import xarray as xr


def get_lon_lat_from_catalog(
    datastore,
    lon_candidates=("geolon", "geolon_t", "lonh", "lonq", "xt_ocean", "lon"),
    lat_candidates=("geolat", "geolat_t", "lath", "latq", "yt_ocean", "lat"),
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

def ensure_2d_transport(da, *, name="umo_2d"):
    """
    If a transport-like DataArray is 3D (time, z, y, x), vertically integrate it
    so it becomes 2D (time, y, x). If it's already 2D, return unchanged.

    Notebook-local helper (transport notebooks only).
    """
    z_candidates = ("z_l", "zl", "st_ocean", "lev", "depth", "z")
    zdim = next((d for d in z_candidates if d in da.dims), None)

    if zdim is None:
        # Already 2D
        out = da
    else:
        # Vertically integrate
        out = da.sum(dim=zdim, skipna=True)

        # Preserve and extend long_name cleanly
        base_long_name = da.attrs.get("long_name", da.name or "")
        if base_long_name and not base_long_name.endswith("Vertical Sum"):
            out.attrs["long_name"] = f"{base_long_name} Vertical Sum"

        out.attrs["derived_from"] = da.name or "unknown"
        out.attrs["vertical_integration_dim"] = zdim

    return out.rename(name)

def select_variable(
    datastore,
    variable_standard_name: Optional[str] = None,
    fallback_variable_names: Optional[Sequence[str]] = None,
    data_frequency: Optional[str] = None,
    prefer_dims: Sequence[str] = ("z_l", "zl"),  # prefer z_l over zl when both exist
    chunks: Optional[Dict[str, Any]] = None,
    verbose: bool = True,
) -> xr.DataArray:
    """
    Select a variable from an intake-esm datastore, robust to:
      - missing standard_name in catalog
      - frequency not present (falls back to any frequency)
      - multiple matching datasets (uses to_dataset_dict + chooses a preferred one)

    Parameters
    ----------
    datastore : intake_esm.core.esm_datastore
    variable_standard_name : str or None
        CF standard_name, e.g. "sea_surface_temperature". If None, skip CF lookup.
    fallback_variable_names : sequence[str] or None
        Candidate variable names to try (in priority order), e.g. ["tos", "sst"].
    data_frequency : str or None
        Frequency filter such as "1mon" or "1day". If no matches, falls back to any frequency.
    prefer_dims : sequence[str]
        When multiple dataset-keys exist, prefer datasets that include these dims (earlier = higher priority).
        Default prefers z_l over zl.
    chunks : dict or None
        Xarray chunking. Default {"time": -1} (loads time as one chunk).
    verbose : bool
        Print what was selected and what fallbacks were used.

    Returns
    -------
    xarray.DataArray
    """
    import cf_xarray  # noqa: F401 (registers .cf accessor)

    if fallback_variable_names is None:
        fallback_variable_names = []
    if chunks is None:
        chunks = {"time": -1}

    def _search_with_freq(kwargs: Dict[str, Any]):
        """Search, and if frequency yields no results, retry without frequency."""
        cat = datastore.search(**kwargs)
        if len(cat.df) == 0 and "frequency" in kwargs:
            freq = kwargs["frequency"]
            kwargs2 = {k: v for k, v in kwargs.items() if k != "frequency"}
            cat2 = datastore.search(**kwargs2)
            if len(cat2.df) > 0 and verbose:
                print(f"No files matched frequency={freq!r}; using any available frequency.")
            return cat2
        return cat

    def _open_cat_best_dataset(cat) -> xr.Dataset:
        """
        Open an intake-esm catalog search result.
        - If exactly one dataset key: use to_dask()
        - If multiple: use to_dataset_dict(), choose 'best' based on prefer_dims, normalize zl->z_l
        """
        open_kwargs = dict(chunks=chunks, decode_timedelta=True, use_cftime=True)
        combine_kwargs = dict(compat="override", coords="minimal", data_vars="minimal")

        if len(cat) == 1:
            return cat.to_dask(
                xarray_open_kwargs=open_kwargs,
                xarray_combine_by_coords_kwargs=combine_kwargs,
            )

        ds_dict = cat.to_dataset_dict(
            xarray_open_kwargs=open_kwargs,
            xarray_combine_by_coords_kwargs=combine_kwargs,
            progressbar=False,
        )

        def ds_score(ds: xr.Dataset) -> Tuple[int, ...]:
            # Higher is better: presence of prefer_dims in order
            dims = set(ds.dims)
            return tuple(int(d in dims) for d in prefer_dims)

        best_key = max(ds_dict.keys(), key=lambda k: ds_score(ds_dict[k]))
        ds = ds_dict[best_key]

        # Normalize vertical dim name for downstream code
        if "zl" in ds.dims and "z_l" not in ds.dims:
            ds = ds.rename({"zl": "z_l"})

        if verbose:
            print(f"Selected dataset key: {best_key}")
            print(f"Dataset dims: {dict(ds.dims)}")

        return ds

    def _list_catalog_candidates(cat_any) -> Sequence[str]:
        candidates = set()
        if hasattr(cat_any, "df") and "variable" in cat_any.df.columns:
            for entry in cat_any.df["variable"]:
                if isinstance(entry, str):
                    candidates.add(entry)
                else:
                    try:
                        candidates.update(entry)
                    except TypeError:
                        pass
        return sorted(candidates)

    search_base: Dict[str, Any] = {}
    if data_frequency:
        search_base["frequency"] = data_frequency

    # --- 1) Try CF standard_name (if provided) ---
    if variable_standard_name:
        try:
            cat = _search_with_freq({**search_base, "variable_standard_name": variable_standard_name})
            if len(cat.df) == 0:
                raise ValueError("No entries found for this CF standard_name.")
            ds = _open_cat_best_dataset(cat)
            da = ds.cf[variable_standard_name]
            if verbose:
                print(f"Selected variable via CF standard_name: {variable_standard_name} -> {da.name}")
            return da
        except Exception as e:
            if verbose:
                print("CF-based lookup failed:", repr(e))

    # --- 2) Try fallback variable names ---
    for name in fallback_variable_names:
        try:
            cat = _search_with_freq({**search_base, "variable": name})
            if len(cat.df) == 0:
                continue
            ds = _open_cat_best_dataset(cat)

            # Some catalogs return datasets where the real var name differs slightly;
            # but usually it's exact. Keep it strict to avoid surprises.
            if name not in ds.data_vars:
                # If missing, skip rather than failing the whole function.
                continue

            da = ds[name]
            if verbose:
                print(f"Selected variable via fallback name: {name}")
            return da
        except Exception as e:
            if verbose:
                print(f"Fallback lookup failed for {name!r}: {repr(e)}")
            continue

    # --- 3) Nothing found → list candidates for debugging ---
    cat_any = _search_with_freq(search_base)
    candidates = _list_catalog_candidates(cat_any)

    raise RuntimeError(
        "Could not identify the requested variable.\n"
        f"CF standard_name tried: {variable_standard_name!r}\n"
        f"Fallback variable names tried: {list(fallback_variable_names)!r}\n"
        f"Frequency filter: {data_frequency!r}\n"
        f"Catalog variable candidates: {candidates}\n"
    )