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
    "MLD_manual":                              f"[#38]({_GH}/38) — Max MLD calculated manually (OM3 vs OM2)",
    "Transects":                               f"[#13]({_GH}/13) — WOCE/GO-SHIP meridional T/S transects",
    "Transects-mixing":                        f"[#13]({_GH}/13) WOCE/GO-SHIP transects, [access-om3-configs#1525](https://github.com/ACCESS-NRI/access-om3-configs/issues/1525) Thermocline bias in 25km",
    "WM_evaluation":                           f"[#106]({_GH}/106) — Water mass density change Hovmöller",
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

# Figure explorer (access-om3-live) settings.
#
# FIGURE_TITLES: a display title for a figure whose own title is too generic (several "Sea Ice Area" figures).
# Keyed by the figure's file stem in the mkmd output, <notebook>_<NN>, as on the evaluation pages.
FIGURE_TITLES: dict[str, str] = {
    "MeridionalHeatTransport_06":        "Meridional Heat Transport by basin",
    "SeaIce_area_01":                    "Seasonal Sea Ice Area",
    "SeaIce_area_02":                    "Timeseries of Sea Ice Area",
    "SeaIce_area_03":                    "Timeseries of min/max Sea Ice Area",
    "SeaIce_mass_budget_climatology_01": "Seasonal Antarctic Sea Ice Mass Budget",
    "SeaIce_mass_budget_climatology_02": "Seasonal Arctic Sea Ice Mass Budget",
    "SeaIce_mass_budget_climatology_03": "Sea Ice Mass Budget Residual",
    "SeaIce_mass_budget_climatology_04": "Annual Antarctic Sea Ice Growth and Melt",
    "SeaIce_mass_budget_climatology_05": "Annual Arctic Sea Ice Growth and Melt",
    "SeaIce_mass_budget_climatology_06": "Seasonal Antarctic Sea Ice Growth and Melt",
    "SeaIce_mass_budget_climatology_07": "Seasonal Arctic Sea Ice Growth and Melt",
}

# RUN_COLOURS: each run's colour slot in the explorer's palette, so a run keeps its colour on every figure and
# as runs are added. A run not listed takes the lowest free slot (the build log says which): add it here to pin it.
RUN_COLOURS: dict[str, int] = {
    "MC_25km_jra_ryf-1.0-beta-cdfb3543":            0,
    "25km-iaf-test-for-AK-expt-7df5ef4c":           1,
    "MC_25km_jra_iaf-1.0-beta-5165c0f8":            2,
    "MC_100km_jra_ryf+wombatlite-1e74abf-11f9df5c": 3,
    "MC_25km_jra_ryf+wombatlite-81ad20e-c4347f5a":  4,
    "MC_25km_jra_iaf+wombatlite-test3v2-00532b88":  5,
    "MC_25km_jra_iaf+wombatlite-test4-d28e0359":    6,
    "MC_25km_jra_ryf+wombatlite-test3-f4d79e82":    7,
    "MC_25km_jra_iaf-1.0-beta-gm1-d968c801":        8,
    "MC_25km_jra_iaf-1.0-beta-gm2-5dc49da6":        9,
    "MC_25km_jra_iaf-1.0-beta-gm3-da330542":        10,
    "MC_25km_jra_iaf-1.0-beta-gm4-9fd08880":        11,
    "MC_25km_jra_iaf-1.0-beta-gm5-9b5dbfa9":        12,
    "MC_25km_jra_iaf+wombatlite_bs1-mpudig-backscat1-4c21c151": 13,
    "MC_25km_jra_iaf+wombatlite_bs2-mpudig-backscat2-0578cc36": 14,
}

# EXPLORER_CATEGORIES: extra sections for the explorer only (the landing page keeps CATEGORIES): a notebook listed here
# moves out of its CATEGORIES section into this one, placed right after it.
EXPLORER_CATEGORIES: dict[str, list[str]] = {
    "Strait transports": ["StraitTransports"],
}

# REFERENCE_SOURCES: where the comparison lines in the notebooks' figures come from, so the explorer can name them
# consistently and say where their data is. The notebooks label the same run in different ways (e.g.
# "ACCESS-OM2-025, cycle1" and "025deg_jra55_iaf_omip2_cycle1"). The first rule whose `match` (a regex, searched in
# the line's label; `notebook` limits it to one notebook) matches gives:
#   name    the label to show ({0}, {1}... are the regex groups), or the label as drawn if absent
#   intake  how to open it (ACCESS-NRI intake catalog entries), or
#   source  where the data is (a path, or the publication for values taken from one); write a literal { or } as {{ }}
# by_forcing: for a label that means a different run per forcing (the line's runs' forcing decides).
# drop: True leaves the line out of the explorer.
_OM2 = 'intake.cat.access_nri["{0}"]'
REFERENCE_SOURCES: list[dict] = [
    {"match": r"(0\d+deg_jra55\w*)(.*)", "name": "ACCESS-OM2 {0}{1}", "intake": _OM2},
    {"match": r"ACCESS-OM2-025,? cycle ?(\d)", "name": "ACCESS-OM2 025deg_jra55_iaf_omip2_cycle{0}",
     "intake": 'intake.cat.access_nri["025deg_jra55_iaf_omip2_cycle{0}"]'},
    {"match": r"ACCESS-OM2-01,? cycle ?(\d)", "name": "ACCESS-OM2 01deg_jra55v140_iaf_cycle{0}",
     "intake": 'intake.cat.access_nri["01deg_jra55v140_iaf_cycle{0}"]'},
    {"match": r"^(ACCESS-)?OM2$", "notebook": "SeaIce_mass_budget_climatology", "by_forcing": {
        "IAF": {"name": "ACCESS-OM2 025deg_jra55_iaf_omip2_cycle6", "intake": 'intake.cat.access_nri["025deg_jra55_iaf_omip2_cycle6"]'},
        "RYF": {"name": "ACCESS-OM2 025deg_jra55_ryf9091_gadi", "intake": 'intake.cat.access_nri["025deg_jra55_ryf9091_gadi"]'}}},
    {"match": r"cj877", "source": "ACCESS-CM2 run cj877: /g/data/p73/archive/CMIP6/non-CMIP/ACCESS-CM2/cj877/history/ocn/"},
    {"match": r"cm3-run-27-07-2026-PD-control",
     "source": "/g/data/zv30/non-cmip/ACCESS-CM3/cm3-run-27-07-2026-PD-control/cm3-datastore/cm3-datastore.json"},
    # not a comparison the explorer should offer (an OM3 test run drawn in MeridionalHeatTransport): left out
    {"match": r"MC_25km_jra_iaf\+wombatlite-test3v2-COARE-12fab415", "drop": True},
    {"match": r"Trenberth et al\.? 2019", "source": "Trenberth, Zhang, Fasullo & Cheng (2019): /g/data/ik11/observations/TrenberthZhangFasulloCheng2019/"},
    {"match": r"Fasullo and Trenberth 2008", "source": "Fasullo & Trenberth (2008), J. Climate 21: values as given in MeridionalHeatTransport.ipynb"},
    {"match": r"^Observations$", "notebook": "SeaIce_area", "name": "Observations (NSIDC CDR G02202 v6)",
     "source": "NSIDC sea ice concentration CDR G02202 v6: /g/data/av17/access-nri/OM3/CDR_G02202_V6/{{north,south}}/monthly/"},
    {"match": r"McCarthy et al\. \(2015\)", "source": "RAPID 26°N array, McCarthy et al. (2015), Prog. Oceanogr.: values as given in Overturning_in_ACCESS_OM3.ipynb"},
    {"match": r"\(\d{4}\)", "notebook": "StraitTransports",
     "source": "Observed mean and range from the publication named, as given in StraitTransports.ipynb (references in its comments)"},
]

# FIGURE_TITLE_RULES: explorer titles by pattern, for families of figures (applied after FIGURE_TITLES; `match` is a
# regex on the figure's title, `title` its replacement, `subtitle` an optional line under the title).
FIGURE_TITLE_RULES: list[dict] = [
    {"match": r"^(.*) sum of magnitude of transport through each cell$", "title": r"\1 gross transport",
     "subtitle": "Gross transport: |transport| summed over the section's cells and density layers, so flow in both "
                 "directions adds up (the figures named \"transport\" are the net, signed sum). The ACCESS-OM2 lines "
                 "in these figures are net transport."},
]

# EXPLORER_MERGE: figures shown as one in the explorer (keyed by figure file stem; every figure saved under a stem joins,
# also several under one stem). The `into` figure keeps its title and panels and gains the others' lines (all in its first
# panel, or `panels: "by_title"` to match panels by title); `series` renames a figure's own lines ("" = unnamed), `scale` multiplies them
# (e.g. W -> PW), and `hidden` lists series shown only when the reader ticks them.
EXPLORER_MERGE: list[dict] = [
    # the notebook draws tos/sos extremes for most runs and mlotst extremes for others: one entry, panels by title
    {"into": "Timeseries_daily_extreme_from_2D_fields_01", "panels": "by_title", "title": "Timeseries of monthly extreme values",
     "caption": "Global minimum of the monthly minimum and global maximum of the monthly maximum, from the model's online "
                "monthly min/max diagnostics: tos and sos for most runs, mlotst for runs whose notebook drew that instead. "
                "[GitHub issue: SST/SSS/SSH/MLD daily extrema](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/34)"},
    {"into": "MeridionalHeatTransport_03", "title": "Meridional Heat Transport Global",
     "from": ["MeridionalHeatTransport_04", "MeridionalHeatTransport_05", "MeridionalHeatTransport_01"],
     "series": {"MeridionalHeatTransport_03": {"": "Total (1990-2007 mean)"},
                "MeridionalHeatTransport_01": {"Total": "Total (whole-run mean)", "Advective": "Advective (whole-run mean)",
                                               "Diffusive": "Diffusive (whole-run mean)"}},
     "scale": {"MeridionalHeatTransport_01": 1e-15},
     "hidden": ["Advective (whole-run mean)", "Diffusive (whole-run mean)"],
     "caption": "Zonally integrated meridional heat transport: each run's 1990-2007 mean total, and its whole-run mean "
                "total, advective and diffusive parts (tick them under the series), with ACCESS-OM2 cycles, other models "
                "and observations to compare. [GitHub issue: Total meridional heat transport]"
                "(https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues/12)"},
]
