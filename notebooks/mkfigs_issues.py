"""
Notebook → GitHub issue mappings for access-om3-paper-1.

Used by mkfigs-pushit to populate the "GitHub Issue(s)" column in the
run summary table on the documentation website.  Add an entry here for
each notebook you want linked to one or more GitHub issues.  Notebooks
not listed will show an empty cell.

ISSUES maps notebook stem (filename without .ipynb) to a Markdown string.

CATEGORIES groups the landing-page run-summary table into one sub-headed
table per category. The headings follow the tracking issue CATEGORIES_SOURCE
(#23) -- when that issue changes, update this to match. Each entry lists issue
numbers (int, matched against the links in ISSUES) and/or notebook stems
(str). Every notebook appears exactly once: a stem listed under a category
puts it there (this overrides issue matches); otherwise it goes to the first
category matching one of its issue numbers; anything unmatched goes last,
under "Miscellaneous". The left-hand nav stays a flat, alphabetical list of
notebooks so it looks the same from run to run.
"""

_GH = "https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues"
_CONFIGS = "https://github.com/ACCESS-NRI/access-om3-configs/issues"

ISSUES: dict[str, str] = {
    "timeseries":                              f"[#3]({_GH}/3) — Global average annual mean time series",
    "StraitTransports":                        f"[#1]({_GH}/1) Drake Passage, [#16]({_GH}/16) Indonesian straits",
    "SSH":                                     f"[#4]({_GH}/4) Global dynamic sea level, [#5]({_GH}/5) Sea level anomaly std dev",
    "Currents_streamfunction_variability":     f"[#18]({_GH}/18) Evaluation: mean surface current speed, standard deviation of sea level anomaly and mean barotropic streamfunction",
    "Overturning_in_ACCESS_OM3":               f"[#6]({_GH}/6) Overturning circulation, [#7]({_GH}/7) AMOC time series",
    "SST":                                     f"[#9]({_GH}/9) — Global SST bias",
    "SST-OM2":                                 f"[#9]({_GH}/9) — Global SST bias (OM2 comparison)",
    "SSS":                                     f"[#10]({_GH}/10) — Global SSS bias",
    "SSS-OM2":                                 f"[#10]({_GH}/10) — Global SSS bias (OM2 comparison)",
    "temp-salt-vs-depth-time":                 f"[#8]({_GH}/8) — Hovmoller temperature anomaly (depth-time)",
    "temp-salt-vs-depth-latitude":             f"[#11]({_GH}/11) Zonally averaged T/S bias, [#13]({_GH}/13) WOCE/GO-SHIP meridional transects",
    "MeridionalHeatTransport":                 f"[#12]({_GH}/12) — Total meridional heat transport",
    "pPV":                                     f"[#14]({_GH}/14) — Planetary geostrophic potential vorticity / SAMW transects",
    "Equatorial_pacific":                      f"[#17]({_GH}/17) Equatorial T & zonal velocity contours, [#19]({_GH}/19) 20°C isotherm depth",
    "SeaIce_area":                             f"[#20]({_GH}/20) Sea ice extent time series, [#21]({_GH}/21) Sea ice annual cycle",
    "SeaIce_Vol":                              f"[#20]({_GH}/20) Sea ice volume time series, [#22]({_GH}/22) Sea ice thickness/concentration",
    "Significant_wave_height_ERA5_comparison": f"[#78]({_GH}/78) — ERA5 wave parameter comparison",
    "Mean_wave_period_ERA5_comparison":        f"[#78]({_GH}/78) — ERA5 wave parameter comparison",
    "Timeseries_daily_extreme_from_2D_fields": f"[#34]({_GH}/34) — SST/SSS/SSH/MLD daily extrema",
    "MLD":                                     f"[#38]({_GH}/38) — Time-max mixed layer depth maps",
    "MLD_max":                                 f"[#38]({_GH}/38) — Time-max mixed layer depth maps",
    "MLD_max-OM2":                             f"[#38]({_GH}/38) — Time-max MLD (OM2 comparison)",
    "SSS_Restoring_Timeseries":                f"[#44]({_GH}/44) — SSS restoring maps/timeseries",
    "SeaIce_mass_budget_climatology":          f"[#52]({_GH}/52) — Sea ice mass budget climatology",
    "Bottom_age_tracer_in_ACCESS_OM3":         f"[#31]({_GH}/31) — Bottom age after 50 years",
    "GM-Testing-in-ACCESS-OM3":                f"[#74]({_GH}/74) — GM coefficients comparison",
    "wombatlite_global":                       f"[#47]({_GH}/47) — WOMBATlite global metrics",
    "FloeSizeTendencies":                      f"[#72]({_GH}/72) — Floe-size distribution tendencies",
    "LangmuirTurbulence":                      f"[access-om3-configs#950]({_CONFIGS}/950) — Langmuir turbulence influence on MLD",
}

CATEGORIES_SOURCE = f"{_GH}/23"

# Headings and issue numbers follow issue #23, in the same order. Notebook
# stems are placements agreed in the 2026-10 triage (they win over issue matches).
CATEGORIES: dict[str, list[int | str]] = {
    "Temperature and salinity structure":            [9, 10, 11, 13, 3, 8, 34, 38,
                                                      "MLD_manual", "MLD-OM2", "MLD_manual_OM2",
                                                      "Equatorial_pacific", "Transects", "Transects-mixing"],
    "Circulation":                                   [4, 1, 16, 6, 7, 74, 41, 12,
                                                      "Currents_streamfunction_variability"],
    "Regional analysis":                             [31, 107, 14, 17, 19, 18],
    "Surface forcing / budget closure / mixing etc": [44, 62, 103, 106],
    "Sea ice":                                       [20, 21, 22, 51, 53, 52, 48, "SeaIce_Stuck_Points"],
    "WOMBAT":                                        [47],
    "WW3":                                           [71, 72, 78, "LangmuirTurbulence"],
    "Other possible bonus figures":                  [120],
    "Miscellaneous":                                 ["GM-Testing-in-ACCESS-OM3"],
}
