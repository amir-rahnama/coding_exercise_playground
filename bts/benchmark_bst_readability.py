"""
Static “readability” proxies for the four BST sources (not subjective readability).

Uses radon: SLOC, cyclomatic complexity (avg / max), maintainability index (MI).
Higher MI is better; lower complexity is often easier to follow. See printed caveats.

CLI (same flags as benchmark_bst_insert.py for plots; --quick is ignored here):
  python benchmark_readability.py
  python benchmark_readability.py --plot
  python benchmark_readability.py --quick --plot
  python benchmark_readability.py --plot-show
  python benchmark_readability.py --plot --output path/to/chart.png
  pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import ast
import math
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    from radon.raw import analyze
except ImportError:
    cc_visit = None  # type: ignore[misc, assignment]
    mi_visit = None  # type: ignore[misc, assignment]
    analyze = None  # type: ignore[misc, assignment]


ROOT = Path(__file__).resolve().parent

# Same order and keys as benchmark_bst_insert.plot_benchmark
IMPL_FILES: tuple[tuple[str, str, str], ...] = (
    ("human", "Human", "bts_human.py"),
    ("agent_assisted", "Agent-assisted", "bts_agent_assisted.py"),
    ("iterative", "Human-in-the-loop", "bts_human_in_the_loop.py"),
    ("agent", "Agentic", "bts_agentic.py"),
)


@dataclass(frozen=True)
class ReadabilityRow:
    key: str
    chart_label: str
    filename: str
    sloc: int
    lloc: int
    loc: int
    blank: int
    max_cc: float
    avg_cc: float
    mi: float
    max_ast_depth: int


class _MaxNestingVisitor(ast.NodeVisitor):
    """Max depth of nested compound statements (if/for/while/with/try/match)."""

    _COMPOUND = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.Match)

    def __init__(self) -> None:
        self._depth = 0
        self.max_depth = 0

    def generic_visit(self, node: ast.AST) -> None:
        push = isinstance(node, self._COMPOUND)
        if push:
            self._depth += 1
            self.max_depth = max(self.max_depth, self._depth)
        super().generic_visit(node)
        if push:
            self._depth -= 1


def _max_ast_nesting(source: str) -> int:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return -1
    v = _MaxNestingVisitor()
    v.visit(tree)
    return v.max_depth


def analyze_source(key: str, chart_label: str, filename: str, source: str) -> ReadabilityRow:
    if analyze is None or cc_visit is None or mi_visit is None:
        raise RuntimeError("radon is required")

    raw = analyze(source)
    blocks = cc_visit(source)
    if blocks:
        ccs = [float(b.complexity) for b in blocks]
        max_cc = max(ccs)
        avg_cc = sum(ccs) / len(ccs)
    else:
        max_cc = 0.0
        avg_cc = 0.0

    mi = float(mi_visit(source, multi=False))
    if math.isnan(mi):
        mi = float("nan")

    return ReadabilityRow(
        key=key,
        chart_label=chart_label,
        filename=filename,
        sloc=raw.sloc,
        lloc=raw.lloc,
        loc=raw.loc,
        blank=raw.blank,
        max_cc=max_cc,
        avg_cc=avg_cc,
        mi=mi,
        max_ast_depth=_max_ast_nesting(source),
    )


def run_analysis() -> tuple[ReadabilityRow, ...]:
    rows: list[ReadabilityRow] = []
    for key, chart_label, filename in IMPL_FILES:
        path = ROOT / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        source = path.read_text(encoding="utf-8")
        rows.append(analyze_source(key, chart_label, filename, source))
    return tuple(rows)


def print_report(rows: tuple[ReadabilityRow, ...]) -> None:
    print(
        "Static readability proxies (whole file, same rules for each).\n"
        "— SLOC: radon logical source lines (sloc).\n"
        "— CC: cyclomatic complexity per block; max/avg over functions & methods.\n"
        "— MI: radon maintainability index (roughly 0–100; higher is better).\n"
        "— Nest: max nesting depth of if/for/while/with/try/match (AST).\n"
        "These numbers do not measure naming, docs, or real human comprehension.\n"
        "Chart: use --plot; per-metric ranks 1–n (higher = better); last bar = mean of those ranks.\n"
    )
    rk, _ = _readability_ranks_matrix(rows)
    avg_rank = rk.mean(axis=1)
    w = 22
    hdr = (
        f"{'file':<{w}} {'chart':<20} {'sloc':>5} {'maxCC':>6} {'avgCC':>6} "
        f"{'MI':>6} {'nest':>5} {'mnRk':>6}"
    )
    print(hdr)
    print("-" * len(hdr))
    for i, r in enumerate(rows):
        mi_s = f"{r.mi:.1f}" if not math.isnan(r.mi) else "n/a"
        print(
            f"{r.filename:<{w}} {r.chart_label:<20} {r.sloc:5d} {r.max_cc:6.1f} "
            f"{r.avg_cc:6.2f} {mi_s:>6} {r.max_ast_depth:5d} {avg_rank[i]:6.2f}"
        )


def _rank_prefer_lower(v: np.ndarray) -> np.ndarray:
    """Ranks in [1, n]; larger rank = better (smaller raw is better). Ties → average rank."""
    import numpy as np

    n = len(v)
    order = np.argsort(v, kind="stable")
    out = np.empty(n, dtype=float)
    pos = 0
    next_rank = n  # best row gets rank n
    while pos < n:
        val = v[order[pos]]
        end = pos
        while end < n and v[order[end]] == val:
            end += 1
        k = end - pos
        avg = sum(next_rank - i for i in range(k)) / k
        for j in range(pos, end):
            out[order[j]] = avg
        next_rank -= k
        pos = end
    return out


def _rank_prefer_higher(v: np.ndarray) -> np.ndarray:
    """Ranks in [1, n]; larger rank = better (larger raw is better). Ties → average rank."""
    import numpy as np

    n = len(v)
    order = np.argsort(-v, kind="stable")
    out = np.empty(n, dtype=float)
    pos = 0
    next_rank = n
    while pos < n:
        val = v[order[pos]]
        end = pos
        while end < n and v[order[end]] == val:
            end += 1
        k = end - pos
        avg = sum(next_rank - i for i in range(k)) / k
        for j in range(pos, end):
            out[order[j]] = avg
        next_rank -= k
        pos = end
    return out


def _readability_ranks_matrix(rows: tuple[ReadabilityRow, ...]):
    """Shape (n_impl, 5): per-metric ranks; higher rank = more readable on that proxy.

    SLOC, max CC, avg CC, nest: lower raw value ranks higher.
    MI: higher raw ranks higher.
    """
    import numpy as np

    slocs = np.array([r.sloc for r in rows], dtype=float)
    max_cc = np.array([r.max_cc for r in rows], dtype=float)
    avg_cc = np.array([r.avg_cc for r in rows], dtype=float)
    mis = np.array([r.mi if not math.isnan(r.mi) else float("nan") for r in rows], dtype=float)
    nests = np.array([max(r.max_ast_depth, 0) for r in rows], dtype=float)

    if np.all(np.isnan(mis)):
        mi_ranks = np.full(len(rows), (1 + len(rows)) / 2)
    else:
        mi_filled = np.where(np.isnan(mis), np.nanmin(mis), mis)
        mi_ranks = _rank_prefer_higher(mi_filled)

    m = np.column_stack(
        [
            _rank_prefer_lower(slocs),
            _rank_prefer_lower(max_cc),
            _rank_prefer_lower(avg_cc),
            mi_ranks,
            _rank_prefer_lower(nests),
        ]
    )
    return m, ["SLOC", "max CC", "avg CC", "MI", "nest"]


def plot_readability(rows: tuple[ReadabilityRow, ...], out_path: Path, *, show: bool) -> None:
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    labels = [r.chart_label for r in rows]
    ranks, metric_names = _readability_ranks_matrix(rows)
    mean_ranks = ranks.mean(axis=1, keepdims=True)
    ranks_plot = np.hstack([ranks, mean_ranks])
    names_plot = list(metric_names) + ["mean rank"]
    n_impl, n_met = ranks_plot.shape

    metric_colors = ["#e45756", "#f58518", "#54a24b", "#4c78a8", "#b279a2", "#2f2f2f"]

    x = np.arange(n_impl, dtype=float)
    bar_width = 0.11
    pitch = bar_width
    offsets = np.linspace(-(n_met - 1) * pitch / 2, (n_met - 1) * pitch / 2, n_met)

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    for j in range(n_met):
        ax.bar(
            x + offsets[j],
            ranks_plot[:, j],
            bar_width,
            label=names_plot[j],
            color=metric_colors[j],
            edgecolor="white",
            linewidth=0.5,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=12, ha="right")
    ax.set_ylabel("Rank (↑ = more readable on that metric)")
    ax.set_ylim(0, n_impl + 0.5)
    ax.set_yticks([1, 2, 3, 4] if n_impl == 4 else list(range(1, n_impl + 1)))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper right", ncol=3, framealpha=0.92, fontsize=8)
    ax.set_title(
        "Readability ranks by implementation — five proxies + mean rank (rightmost dark bar)\n"
        f"(ranks 1–{n_impl} per metric; mean rank = average of those five; ties use average rank)",
        fontsize=10,
    )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=500)
    if show:
        plt.show()
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="BST static readability proxies")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="no effect here (same flag as benchmark_bst_insert.py for smaller insert runs)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="write chart image next to this script (default path below)",
    )
    parser.add_argument(
        "--plot-show",
        action="store_true",
        help="write chart and open a display window (needs GUI backend)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="chart path (default: bst_readability_charts.png beside this script)",
    )
    args = parser.parse_args()

    if cc_visit is None:
        print("This script needs radon. Install with:", file=sys.stderr)
        print("  pip install -r requirements.txt", file=sys.stderr)
        return 1

    rows = run_analysis()
    print_report(rows)

    out = args.output
    if out is None:
        out = ROOT / "bst_readability_charts.png"
    else:
        out = Path(out)

    if args.plot or args.plot_show:
        try:
            plot_readability(rows, out, show=args.plot_show)
        except ImportError as e:
            print("Plotting needs matplotlib. Install:", file=sys.stderr)
            print("  pip install -r requirements.txt", file=sys.stderr)
            raise SystemExit(1) from e
        print(f"Wrote chart: {out}")
        if args.plot_show:
            print("(Close the chart window to exit if it is blocking.)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
