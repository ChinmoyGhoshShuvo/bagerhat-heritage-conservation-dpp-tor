"""
Charts rebuilt from the DPP and ToR tables (data/*.csv).
The ToR's activity-level dates contain typing errors (e.g. sub-tasks dated 2025 inside
2027 phases), so the schedule is drawn from the phase-level rows, which run
consecutively over the 36-month consultancy.
Run:  python make_figures.py   -> PNGs in ../images/
"""
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE.parent / "images"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200,
    "savefig.bbox": "tight", "figure.facecolor": "white",
})


def schedule():
    d = pd.read_csv(DATA / "tor_phase_schedule.csv", comment="#", parse_dates=["start", "end"])
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    for y, r in enumerate(d.itertuples()):
        col = "#D55E00" if r.phase.startswith("Conservation") else "#0072B2"
        ax.barh(y, (r.end - r.start).days + 1, left=r.start, height=0.55, color=col)
        ax.text(r.end + pd.Timedelta(days=12), y, f"{r.months} mo", va="center", fontsize=7.5)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d.phase)
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_xlim(pd.Timestamp("2024-06-15"), pd.Timestamp("2027-09-30"))
    ax.grid(axis="x", color="#eee")
    ax.set_axisbelow(True)
    ax.set_title("36-month implementation schedule (July 2024 - June 2027)", loc="left")
    fig.text(0, -0.06, "Rebuilt from ToR section 6.1, phase-level rows.", fontsize=7, color="#555")
    fig.savefig(OUT / "implementation-schedule-gantt.png")
    plt.close(fig)


def budget():
    d = pd.read_csv(DATA / "dpp_cost_components.csv", comment="#")
    g = d.groupby("component_group").lakh_bdt.sum().sort_values()
    total = g.sum()
    cols = ["#0072B2" if k.startswith("Revenue") else "#E69F00" if k.startswith("Capital") else "#999999"
            for k in g.index]
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    ax.barh(g.index, g.values, color=cols, height=0.6)
    for y, v in enumerate(g.values):
        ax.text(v + 2, y, f"{v:.1f} lakh ({v / total * 100:.1f}%)", va="center", fontsize=7.5)
    ax.set_xlim(0, 250)
    ax.set_xlabel("Estimated cost (lakh BDT)")
    ax.set_title(f"DPP budget: {total:.0f} lakh BDT (GOB grant)", loc="left")
    fig.text(0, -0.08, "Rebuilt from the DPP cost summary. Blue = revenue, orange = capital, grey = contingency.",
             fontsize=7, color="#555")
    fig.savefig(OUT / "dpp-budget-by-component.png")
    plt.close(fig)


if __name__ == "__main__":
    schedule()
    budget()
    print("written to", OUT.resolve())
