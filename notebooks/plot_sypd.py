#!/usr/bin/env python3
"""Plot simulated years per day (SYPD) against model date from CMEPS ``med.log`` files.

For each directory given on the command line, the script reads

    <DIR>/archive/outputXXX/log/med.log     runs already archived (payu control directory)
    <DIR>/outputXXX/log/med.log             only if archive/ has none, e.g. when DIR is
                                            an archive directory itself
    <DIR>/work/log/med.log                  the current run, while it is going; only looked
                                            for when DIR has an archive/

``archive`` and ``work`` are normally the symlinks that payu creates. The work-directory
log also turns up for a failed run that hasn't been swept yet.
The mediator writes one throughput line per profiling interval, e.g.

    Model Date: 1958-09-04T00:00:00 wall clock = 2026-10-09T10:09:05 avg dt =    32.78 s/day, dt =    33.38 s/day, rate =     7.09 ypd

The model date and the trailing ``... ypd`` value are taken from these lines and
drawn as one line per med.log, on an x-axis spanning the full range of model
dates found across all the files. Each directory gets one colour and one legend
entry listing its runs, e.g. ``expt_a (output000-004, work)``.

Example:
    plot_sypd.py ~/access-om3/expt_a ~/access-om3/expt_b -o sypd.png
"""
from __future__ import annotations

import argparse
import glob
import math
import os
import re
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import groupby

import matplotlib

matplotlib.use("Agg")  # render straight to file: no display needed (e.g. HPC login nodes)
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

# Throughput line written by the CMEPS mediator; the number just before "ypd" is the rate.
RATE_RE = re.compile(
    r"Model Date:\s*(?P<date>\S+).*?"
    r"(?P<ypd>[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*ypd\s*$"
)
DATE_RE = re.compile(r"(\d+)-(\d+)-(\d+)(?:[T ](\d+):(\d+):(\d+(?:\.\d*)?))?")  # ESMF time string
OUTPUT_RE = re.compile(r"output(\d+)")

# One categorical colour per directory, in command-line order (validated for colour-blind
# separation between neighbouring series). Past 8 directories the hues repeat with a new
# line style rather than inventing more colours.
PALETTE = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948")
LINESTYLES = ("-", "--", ":", "-.")
SURFACE, INK, INK_MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"
LEGEND_ROWS = 20  # legend entries per column (fits beside the axes) before adding a column


@dataclass
class Series:
    experiment: str  # directory name, as shown in the legend
    run: str  # outputXXX, or "work" for the run in progress
    dates: list
    rates: list
    color: str = PALETTE[0]
    linestyle: str = "-"

    @property
    def label(self) -> str:
        return f"{self.experiment}/{self.run}"

    @property
    def live(self) -> bool:
        return self.run == "work"


def warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot simulated years per day against model date, one line per "
        "DIR/archive/outputXXX/log/med.log (or DIR/outputXXX/log/med.log if archive/ has none), "
        "plus DIR/work/log/med.log for a run in progress when DIR has an archive/.",
    )
    parser.add_argument("dirs", nargs="+", metavar="DIR",
                        help="payu control directory (with archive/ and work/), "
                             "or a directory holding outputXXX/ directly")
    parser.add_argument("-o", "--output", default="sypd.png",
                        help="PNG file to write (default: %(default)s)")
    parser.add_argument("--title", default="Model throughput",
                        help="plot title (default: %(default)s)")
    parser.add_argument("--dpi", type=int, default=150,
                        help="resolution of the PNG (default: %(default)s)")
    return parser.parse_args(argv)


def short_names(dirs: list[str]) -> list[str]:
    """Shortest trailing part of each path that still tells the directories apart."""
    parts = [os.path.normpath(os.path.abspath(d)).split(os.sep) for d in dirs]
    names = []
    for i, p in enumerate(parts):
        n = 1
        while n < len(p) and any(q[-n:] == p[-n:] for j, q in enumerate(parts) if j != i):
            n += 1
        names.append("/".join(p[-n:]))
    return names


def output_logs(base: str) -> list[tuple[str, str]]:
    """[(outputXXX, path to med.log), ...] under base/outputXXX/log/, in output-number order."""
    found = []
    for path in glob.glob(os.path.join(glob.escape(base), "output*", "log", "med.log")):
        output = os.path.basename(os.path.dirname(os.path.dirname(path)))
        match = OUTPUT_RE.fullmatch(output)
        if match:
            found.append((int(match.group(1)), output, path))
    return [(output, path) for _, output, path in sorted(found)]


def find_med_logs(directory: str) -> list[tuple[str, str]]:
    """[(name, path to med.log), ...] for one experiment: the archived runs in output-number
    order, then "work" for the current run if its log exists."""
    if not os.path.isdir(directory):
        warn(f"{directory} is not a directory; skipping")
        return []
    archive = os.path.join(directory, "archive")
    if os.path.islink(archive) and not os.path.isdir(archive):
        warn(f"{archive} is a broken symlink (-> {os.readlink(archive)})")
    # outputXXX under archive/ (payu control dir); failing that, directly under DIR (e.g. DIR is
    # an archive directory itself). Nothing yet is fine while the first run is going.
    logs = output_logs(archive) or output_logs(directory)
    # work/ is only a payu run directory in a control dir, i.e. one with an archive/ (usually a
    # symlink, possibly dangling); no work/ or no log in it yet just means nothing is running
    work_log = os.path.join(directory, "work", "log", "med.log")
    if os.path.lexists(archive) and os.path.isfile(work_log):
        logs.append(("work", work_log))
    if not logs:
        warn(f"no med.log in {directory}/archive/output*/log, {directory}/output*/log "
             f"or (with an archive/) {directory}/work/log; skipping")
    return logs


def parse_model_date(text: str) -> datetime | None:
    """ESMF time string -> datetime, or None if it is not a valid Gregorian date."""
    m = DATE_RE.fullmatch(text)
    if not m:
        return None
    year, month, day, hour, minute = (int(g or 0) for g in m.groups()[:5])
    try:
        return datetime(year, month, day, hour, minute) + timedelta(seconds=float(m.group(6) or 0))
    except ValueError:  # e.g. year 0, or 30 Feb from a 360-day calendar
        return None


def read_med_log(path: str) -> tuple[list[datetime], list[float], int]:
    """Model dates and rates (ypd) from one med.log, plus the count of unparsable lines."""
    dates, rates, bad = [], [], 0
    with open(path, errors="replace") as f:
        for line in f:
            if "Model Date:" not in line or "ypd" not in line:
                continue  # cheap pre-filter: med.log holds plenty of other output
            m = RATE_RE.search(line)
            date = parse_model_date(m.group("date")) if m else None
            if date is None:
                bad += 1  # e.g. Fortran overflow ("********") or an unusual calendar date
                continue
            dates.append(date)
            rates.append(float(m.group("ypd")))
    return dates, rates, bad


def padded_year_format(fmt: str):
    """Date tick formatter for `fmt` that always writes 4-digit years (0001-04, not 1-04)."""
    def format_tick(x, pos=None):
        d = mdates.num2date(x)
        return d.strftime(fmt.replace("%Y", f"{d.year:04d}"))
    return format_tick


def collect(dirs: list[str]) -> list[Series]:
    """Read every med.log and turn each one with data into a styled, labelled Series."""
    experiments = []  # (directory, [(outputXXX, dates, rates), ...]) for directories with data
    for directory in dirs:
        runs = []
        for output, path in find_med_logs(directory):
            dates, rates, bad = read_med_log(path)
            if bad:
                warn(f"{path}: skipped {bad} unparsable 'Model Date: ... ypd' line(s)")
            if dates:
                runs.append((output, dates, rates))
            else:
                warn(f"{path}: no 'Model Date: ... ypd' lines; skipping")
        if runs:
            experiments.append((directory, runs))

    if len(experiments) > len(PALETTE):
        warn(f"more than {len(PALETTE)} directories: colours repeat with different line styles")

    series = []
    names = short_names([directory for directory, _ in experiments])
    for i, (name, (_, runs)) in enumerate(zip(names, experiments)):
        # One colour + line style per experiment directory, shared by all of its runs
        # (every outputXXX and work/), so an experiment looks the same wherever it appears.
        color = PALETTE[i % len(PALETTE)]
        style = LINESTYLES[(i // len(PALETTE)) % len(LINESTYLES)]
        for output, dates, rates in runs:
            series.append(Series(name, output, dates, rates, color, style))
    return series


def describe_runs(runs: list[str]) -> str:
    """'output000-004, output007, work': consecutive outputs are shown as a range."""
    numbers = [OUTPUT_RE.fullmatch(r).group(1) for r in runs if r != "work"]  # "000", "001", ...
    parts = []
    # consecutive output numbers share the same (number - position) key
    for _, group in groupby(enumerate(numbers), key=lambda item: int(item[1]) - item[0]):
        digits = [d for _, d in group]
        parts.append(f"output{digits[0]}" + (f"-{digits[-1]}" if len(digits) > 1 else ""))
    return ", ".join(parts + [r for r in runs if r == "work"])


def plot(series: list[Series], start: datetime, end: datetime,
         output: str, title: str, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    for s in series:
        ax.plot(s.dates, s.rates, color=s.color, linestyle=s.linestyle,
                linewidth=1.2, solid_joinstyle="round", solid_capstyle="round",
                marker="o" if len(s.dates) == 1 else None, markersize=4)
        if s.live:  # dot where the run in work/ has got to (its latest line in med.log)
            ax.plot(s.dates[-1], s.rates[-1], marker="o", markersize=6, color=s.color,
                    markeredgecolor=SURFACE, markeredgewidth=1, zorder=3,
                    clip_on=False)  # usually sits on the right edge of the axes

    if start == end:  # a single timestamp: avoid a zero-width axis
        start, end = start - timedelta(days=1), end + timedelta(days=1)
    ax.set_xlim(start, end)  # spans every model date found, across all med.log files
    ax.set_ylim(bottom=0)

    # ISO-style tick labels (1958, 1958-05, 1958-05-04, ...) so every tick carries its year
    locator = mdates.AutoDateLocator()
    formatter = mdates.AutoDateFormatter(locator)
    formatter.scaled = {scale: padded_year_format(fmt) for scale, fmt in formatter.scaled.items()}
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_title(title, loc="left", color=INK, fontsize=12, pad=10)
    ax.set_xlabel("Model date", color=INK_MUTED)
    ax.set_ylabel("Simulated years per day", color=INK_MUTED)
    ax.tick_params(color=AXIS, labelcolor=INK_MUTED, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)

    # One legend entry per directory, e.g. "name (output000-004, output006, work)", in the order given
    experiments = {}  # name -> (colour, line style, [runs])
    for s in series:
        experiments.setdefault(s.experiment, (s.color, s.linestyle, []))[2].append(s.run)
    handles = [Line2D([], [], color=color, linestyle=style, linewidth=2.5)  # thicker than the
               for color, style, _ in experiments.values()]                  # data, easier to match
    labels = [f"{name} ({describe_runs(runs)})" for name, (_, _, runs) in experiments.items()]
    ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False,
              fontsize=8, ncol=math.ceil(len(handles) / LEGEND_ROWS), handlelength=1.6)

    fig.savefig(output, dpi=dpi, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    dirs, seen = [], set()  # keep command-line order, drop repeats of the same directory
    for d in args.dirs:
        real = os.path.realpath(d)
        if real in seen:
            warn(f"{d} given more than once; using it once")
            continue
        seen.add(real)
        dirs.append(d)

    series = collect(dirs)
    if not series:
        sys.exit("error: no SYPD data in any DIR/archive/output*/log/med.log, "
                 "DIR/output*/log/med.log or DIR/work/log/med.log")

    start = min(min(s.dates) for s in series)
    end = max(max(s.dates) for s in series)
    plot(series, start, end, args.output, args.title, args.dpi)  # first, so `| head` can't stop it

    width = max(len(s.label) for s in series)
    print(f"Read {len(series)} med.log file(s), highest median rate first:")
    for median, s in sorted(((statistics.median(s.rates), s) for s in series),
                            key=lambda row: row[0], reverse=True):  # stable: ties keep order
        print(f"  {s.label:<{width}}  {len(s.rates):6d} points  "
              f"{min(s.dates).date()} to {max(s.dates).date()}  "
              f"median {median:6.2f} ypd")
    print(f"Model dates span {start.date()} to {end.date()}")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())