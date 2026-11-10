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

import operator
import warnings

import numpy as np
import pandas as pd
import xarray as xr


def _patch_broken_conda_env():
    """
    Workaround for conda/analysis3-26.03 .. 26.07 on Gadi: numba expects
    coverage.types attributes removed in coverage >= 7.x, which breaks
    `import sparse` and therefore all dask-chunked dataset loading
    (xr.open_dataset(chunks=...) and intake-esm to_dask()).
    No-op on healthy environments. Called internally before chunked opens.
    """
    try:
        import sys, types, coverage, coverage.types
        class _TypesProxy(types.ModuleType):
            def __getattr__(self, name):
                val = type(name, (), {})
                setattr(self, name, val)
                return val
        proxy = _TypesProxy('coverage.types')
        proxy.__dict__.update(vars(coverage.types))
        coverage.types = proxy
        sys.modules['coverage.types'] = proxy
    except Exception:
        pass


# Public name, for notebooks that do raw intake/xarray chunked loads
# (select_variable and get_lon_lat_from_catalog call the workaround themselves).
patch_broken_conda_env = _patch_broken_conda_env


def patch_dask_workers(client):
    """
    Apply the conda-env workaround on every dask worker of a distributed Client
    -- both the workers connected right now, and any worker (re)started later.

    A plain `client.run(...)` (as used previously) only reaches workers that
    are already connected: if a worker dies (e.g. OOM) and its nanny restarts
    it, the fresh process never gets patched, and the very first heavy import
    (dask.array -> sparse -> numba) crashes it again immediately with the same
    coverage.types AttributeError -- worker death then looks like it never
    recovers, even though the *cause* of the first death may have been
    unrelated (e.g. genuine memory pressure). Registering a WorkerPlugin makes
    the scheduler re-apply the patch to every worker that ever connects,
    including ones spawned after a restart.

    Uses a nested function/class so they are serialised by value (cloudpickle)
    -- workers start in their own scratch directory and can't import this
    module up front.
    """
    import os
    here = os.path.dirname(os.path.abspath(__file__))

    def _patch(path=here):
        import sys
        if path not in sys.path:
            sys.path.insert(0, path)
        import model_agnostic
        model_agnostic._patch_broken_conda_env()

    client.run(_patch)

    from distributed.diagnostics.plugin import WorkerPlugin

    class _CondaEnvPatchPlugin(WorkerPlugin):
        def setup(self, worker):
            _patch()

    try:
        client.register_plugin(_CondaEnvPatchPlugin())
    except AttributeError:
        # older distributed versions
        client.register_worker_plugin(_CondaEnvPatchPlugin())


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
    _patch_broken_conda_env()

    def _find_var(candidates):
        for name in candidates:
            try:
                cat = datastore.search(variable=name)
                if len(cat.df) == 0:
                    continue
                try:
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
                except Exception:
                    # Multiple files can expose the same grid variable (e.g. both
                    # a "geometry" and a "static" file per output cycle), sometimes
                    # under different dimension names for the same physical grid
                    # (observed: geometry.nc's geolon/geolat use lath/lonh, while
                    # static.nc's use yh/xh -- the latter matches the actual data
                    # variables' dims). Prefer a "static" file if one is present,
                    # rather than an arbitrary alphabetically-first path.
                    paths = sorted(cat.df["path"])
                    static_paths = [p for p in paths if "static" in p.lower()]
                    ds = xr.open_dataset(
                        (static_paths or paths)[0], decode_timedelta=True
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

    _patch_broken_conda_env()

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
        - If multiple: choose 'best' based on dataset-key dims, normalize zl->z_l
        - If prefer_dims cannot single out one dataset: raise rather than pick arbitrarily
        """
        open_kwargs = dict(chunks=chunks, decode_timedelta=True, use_cftime=True)
        combine_kwargs = dict(compat="override", coords="minimal", data_vars="minimal")

        if len(cat) == 1:
            return cat.to_dask(
                xarray_open_kwargs=open_kwargs,
                xarray_combine_by_coords_kwargs=combine_kwargs,
            )

        def key_score(key: str) -> Tuple[int, ...]:
            return tuple(int(f".{dim}:" in key or key.startswith(f"{dim}:")) for dim in prefer_dims)

        scores = {key: key_score(key) for key in cat.keys()}
        best_score = max(scores.values())
        best_keys = sorted(key for key, score in scores.items() if score == best_score)
        if len(best_keys) > 1:
            raise RuntimeError(
                f"Ambiguous match: cannot choose between dataset keys {best_keys}. "
                "Refine the search (variable name, frequency, ...) to match exactly one dataset."
            )
        best_key = best_keys[0]
        ds = cat[best_key].to_dask(
            xarray_open_kwargs=open_kwargs,
            xarray_combine_by_coords_kwargs=combine_kwargs,
        )

        # Normalize vertical dim name for downstream code
        if "zl" in ds.dims and "z_l" not in ds.dims:
            ds = ds.rename({"zl": "z_l"})

        if verbose:
            print(f"Selected dataset key: {best_key}")
            print(f"Dataset dims: {dict(ds.dims)}")

        return ds

    def _filter_exact_variable(cat, name: str):
        if not hasattr(cat, "df") or "variable" not in cat.df.columns:
            return cat

        def has_exact_variable(entry):
            if isinstance(entry, str):
                if entry == name:
                    return True
                if entry.startswith("["):
                    import ast
                    try:
                        return name in ast.literal_eval(entry)
                    except Exception:
                        return False
                return False
            try:
                return name in entry
            except TypeError:
                return False
        filtered = cat.df.loc[cat.df["variable"].map(has_exact_variable)].copy()
        out = cat.__class__({"esmcat": cat.esmcat.dict(), "df": filtered})
        out.esmcat.catalog_file = None
        out.derivedcat = cat.derivedcat
        out._requested_variables = [name]
        return out

    def _open_exact_variable_files(cat, name: str) -> xr.Dataset:
        paths = sorted(cat.df["path"].unique())
        # chunks -> lazy dask arrays; without them combine_by_coords eagerly
        # concatenates every file into memory (~120 GB for 25 km daily data).
        open_kwargs = dict(chunks=chunks, decode_timedelta=True, use_cftime=True)

        datasets = []
        for path in paths:
            ds = xr.open_dataset(path, **open_kwargs)
            if name in ds.data_vars:
                datasets.append(ds[[name]])

        if not datasets:
            raise RuntimeError(f"No files contained variable {name!r}")
        if len(datasets) == 1:
            return datasets[0]

        return xr.combine_by_coords(
            datasets,
            data_vars="minimal",
            coords="minimal",
            compat="override",
            combine_attrs="override",  # per-file attrs like 'history' differ; keep the first
        )

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
    fallback_errors = []
    for name in fallback_variable_names:
        try:
            cat = _search_with_freq({**search_base, "variable": name})
            cat = _filter_exact_variable(cat, name)
            if len(cat.df) == 0:
                continue
            ds = _open_exact_variable_files(cat, name)
            if name not in ds.data_vars:
                raise RuntimeError(
                    f"Exact file-path open for {name!r} did not contain {name!r}; "
                    f"found variables {list(ds.data_vars)}"
                )

            da = ds[name]
            if verbose:
                print(f"Selected variable via fallback name: {name}")
            return da
        except Exception as e:
            fallback_errors.append(f"{name!r}: {e!r}")
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
        f"Fallback errors: {fallback_errors}\n"
        f"Catalog variable candidates: {candidates}\n"
    )

_FREQUENCIES = ("annual", "monthly", "daily")


def _infer_frequency(values):
    """Classify a sorted time axis as "annual", "monthly" or "daily" from its median step."""
    if len(values) < 2:
        raise ValueError("cannot infer the sampling interval from fewer than two timestamps; "
                         f"pass frequency= one of {_FREQUENCIES}")
    step = pd.Series(pd.to_timedelta(np.diff(values))).median().total_seconds() / 86400
    for name, (lo, hi) in {"daily": (0.9, 1.1), "monthly": (27, 32), "annual": (360, 367)}.items():
        if lo <= step <= hi:
            return name
    raise ValueError(f"median sampling interval of {step:.4g} days is not daily, monthly or annual; "
                     "only those are supported (or pass frequency= if the axis is known to be one of them)")


def complete_years(time, *, frequency=None):
    """
    Return the sorted list of calendar years fully covered by a time coordinate.

    Supported sampling: annual, monthly or daily, with any cftime calendar or
    datetime64, in any order. `frequency` ("annual", "monthly" or "daily") is
    inferred from the median step unless given (needed for a single sample).
    A year is complete when each of its calendar periods occurs exactly once:
    one sample (annual), each month 1-12 (monthly), every day of the year
    (daily; 365, 366 or 360 days according to the calendar). Membership is by
    the calendar year/month/day of the timestamp, which must lie inside the
    interval it represents (mid-interval, start or last-day stamps are fine;
    end-of-interval stamps such as 1 Feb for January are not: use time bounds).

    Raises ValueError for duplicate timestamps (which would be silently averaged
    twice by the caller) and for a sampling that is not annual, monthly or daily.
    Returns [] for an empty axis.
    """
    if time.size == 0:
        return []
    time = time.isel(time=np.argsort(time.values))
    vals = time.values
    dups = vals[1:][vals[1:] == vals[:-1]]
    if dups.size:
        raise ValueError(f"{dups.size} duplicate timestamp(s), e.g. {dups[:3].tolist()}; "
                         "remove or resolve them before choosing a window")
    if frequency is None:
        frequency = _infer_frequency(vals)
    elif frequency not in _FREQUENCIES:
        raise ValueError(f"frequency must be one of {_FREQUENCIES}, got {frequency!r}")
    import cftime
    cal = time.dt.calendar
    years = time.dt.year.values
    months, doys = time.dt.month.values, time.dt.dayofyear.values
    complete = []
    for y in np.unique(years):
        here = years == y
        if frequency == "annual":
            ok = here.sum() == 1
        elif frequency == "monthly":
            ok = np.array_equal(months[here], np.arange(1, 13))
        else:
            ndays = (cftime.datetime(int(y) + 1, 1, 1, calendar=cal) - cftime.datetime(int(y), 1, 1, calendar=cal)).days
            ok = np.array_equal(doys[here], np.arange(1, ndays + 1))
        if ok:
            complete.append(int(y))
    return complete


def _runs(years):
    """Split a sorted list of years into runs of consecutive years."""
    runs = []
    for y in years:
        if runs and y == runs[-1][-1] + 1:
            runs[-1].append(y)
        else:
            runs.append([y])
    return runs


def years_window(time, nyears=None, *, within=None, period=None, fallback="first", frequency=None):
    """
    Choose a window of consecutive complete years of `time`: by default the last
    `nyears` of them. See complete_years() for what "complete" means and for
    `frequency`.

    nyears   -- number of years wanted (positive integer). The window is shorter,
                with a warning, if fewer consecutive complete years are available.
    period   -- optional explicit (firstyear, lastyear), e.g. from a notebook
                parameter. It takes precedence over nyears (which is then ignored)
                and cannot be combined with within. Every year in it must be
                complete in `time`, otherwise ValueError: it is never clipped.
    within   -- optional (firstyear, lastyear) to restrict the choice to, e.g.
                the window used for another experiment, so a reference is
                compared over the same model years. A warning is issued if only
                part of it is covered.
    fallback -- what to do if no complete year of `time` falls inside `within`:
                "first" (default) uses the first `nyears` complete years of `time`,
                with a warning; this is only the earliest available data, not a
                claim about spin-up stage or comparability. "raise" raises ValueError.

    Windows never span a gap: only the last (or, for the fallback, first) run of
    consecutive complete years is used, so year_slice() cannot re-include a
    partial year. Returns (firstyear, lastyear); use year_slice() to select with it.
    """
    years = complete_years(time, frequency=frequency)
    if not years:
        raise ValueError("no complete years in time coordinate")
    if period is not None:
        if within is not None:
            raise ValueError("period and within cannot be combined")
        first, last = period
        if first > last:
            raise ValueError(f"period {period} has first year > last year")
        missing = [y for y in range(first, last + 1) if y not in years]
        if missing:
            raise ValueError(f"period {period} is not fully covered by complete years of the "
                             f"time coordinate (complete: {years[0]}-{years[-1]}); missing {missing}")
        return first, last
    if nyears is None:
        raise ValueError("give nyears or period")
    nyears = operator.index(nyears)
    if nyears < 1:
        raise ValueError(f"nyears must be a positive integer, got {nyears}")
    if within is not None:
        if within[0] > within[1]:
            raise ValueError(f"within {within} has first year > last year")
        inside = [y for y in years if within[0] <= y <= within[1]]
        if inside:
            chosen = _runs(inside)[-1][-nyears:]
            if inside[0] > within[0] or inside[-1] < within[1] or len(inside) < within[1] - within[0] + 1:
                warnings.warn(f"years_window: only complete years {inside[0]}-{inside[-1]} of the requested "
                              f"{within[0]}-{within[1]} are available; using {chosen[0]}-{chosen[-1]}", stacklevel=2)
        elif fallback == "raise":
            raise ValueError(f"no complete year of the time coordinate ({years[0]}-{years[-1]}) "
                             f"falls inside {within}")
        elif fallback == "first":
            chosen = _runs(years)[0][:nyears]
            warnings.warn(f"years_window: no complete year inside {within}; falling back to the "
                          f"first {len(chosen)} complete years {chosen[0]}-{chosen[-1]}", stacklevel=2)
        elif fallback == "last":
            chosen = _runs(years)[-1][-nyears:]
            warnings.warn(f"years_window: no complete year inside {within}; falling back to the "
                          f"last {len(chosen)} complete years {chosen[0]}-{chosen[-1]}", stacklevel=2)
        else:
            raise ValueError(f"unknown fallback {fallback!r}")
    else:
        chosen = _runs(years)[-1][-nyears:]
    if len(chosen) < nyears:
        warnings.warn(f"years_window: wanted {nyears} complete years, using {len(chosen)} "
                      f"({chosen[0]}-{chosen[-1]})", stacklevel=2)
    return chosen[0], chosen[-1]


def year_slice(window):
    """
    Turn a (firstyear, lastyear) window into a slice for .sel(time=...).
    Year-only strings select whole calendar years for cftime (any calendar,
    including 360_day, which has no 31 December) and datetime64 indexes. The
    time index must be sorted and, for datetime64, within the nanosecond range
    (use cftime beyond year 2262). The window is not validated here; years_window
    guarantees complete years.
    """
    return slice(f"{window[0]:04d}", f"{window[1]:04d}")
