"""
Compare insertion time and traced allocation peak for four BST implementations.

Loads each example file as its own module so class names do not clash.
Includes bts_agent_assisted.py as “Agent-assisted” in charts.
Memory: tracemalloc peak in text tables; charts show time + tracemalloc only.
(RSS Δ still in printed table when psutil is installed.)

CLI (same output flags as benchmark_readability.py):
  python benchmark_bst_insert.py                 # text tables only
  python benchmark_bst_insert.py --quick         # smaller n, fewer repeats
  python benchmark_bst_insert.py --plot            # write PNG chart
  python benchmark_bst_insert.py --plot-show       # write PNG + open window
  python benchmark_bst_insert.py --plot --output path/to/chart.png
  # pip install -r requirements.txt (matplotlib for --plot / --plot-show)
"""

from __future__ import annotations

import argparse
import gc
import importlib.util
import math
import os
import random
import statistics
import sys
import time
import tracemalloc
from dataclasses import dataclass
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore[misc, assignment]


@dataclass(frozen=True)
class ImplResult:
    key: str
    label: str
    time_s: float
    peak_bytes: float  # median tracemalloc peak during build
    rss_delta_bytes: float  # median RSS_after − RSS_before (process RAM)


@dataclass(frozen=True)
class SizeBench:
    n: int
    impls: tuple[ImplResult, ...]


def _load(name: str, filename: str):
    path = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _median(xs: list[float]) -> float:
    return statistics.median(xs) if xs else float("nan")


def _fmt_mb(bytes_peak: float) -> str:
    return f"{bytes_peak / (1024 * 1024):.2f} MiB"


def _measure(build) -> tuple[float, int, float]:
    gc.collect()
    proc = psutil.Process(os.getpid()) if psutil is not None else None
    rss_before = proc.memory_info().rss if proc is not None else math.nan

    tracemalloc.stop()
    tracemalloc.start()
    t0 = time.perf_counter()
    build()
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    rss_after = proc.memory_info().rss if proc is not None else math.nan
    rss_delta = rss_after - rss_before if proc is not None else math.nan
    return elapsed, peak, rss_delta


def run_benchmark(
    *,
    quick: bool,
    seed: int = 42,
) -> tuple[SizeBench, ...]:
    human_mod = _load("bst_human", "bts_human.py")
    iterative_mod = _load("bst_iterative", "bts_human_in_the_loop.py")
    agent_mod = _load("bst_agent", "bts_agentic.py")
    agent_assisted_mod = _load("bst_agent_assisted", "bts_agent_assisted.py")

    sizes = [2_000, 10_000] if quick else [5_000, 25_000, 100_000]
    repeats = 2 if quick else 5

    def build_human(values: list[int]):
        t = human_mod.BinarySearchTree()
        t.insert(values)

    def build_iterative(values: list[int]):
        iterative_mod.BinarySearchTree(values)

    def build_agent(values: list[int]):
        agent_mod.BinarySearchTree(values)

    def build_agent_assisted(values: list[int]):
        t = agent_assisted_mod.BinarySearchTree()
        t.insert(values)

    def count_std(root) -> int:
        if root is None:
            return 0
        return 1 + count_std(root.left) + count_std(root.right)

    def count_human_tree(root) -> int:
        if root is None:
            return 0
        return (
            1
            + count_human_tree(root.left_child)
            + count_human_tree(root.right_child)
        )

    out: list[SizeBench] = []
    impl_specs = (
        ("human", "Human (bts_human.py)", build_human),
        (
            "agent_assisted",
            "Agent-assisted (bts_agent_assisted.py)",
            build_agent_assisted,
        ),
        (
            "iterative",
            "Human-in-the-loop (bts_human_in_the_loop.py)",
            build_iterative,
        ),
        ("agent", "Agentic (bts_agentic.py)", build_agent),
    )

    for n in sizes:
        rng = random.Random(seed)
        values = list(range(n))
        rng.shuffle(values)

        h = human_mod.BinarySearchTree()
        h.insert(values)
        assert count_human_tree(h.root) == n, "human node count"

        it = iterative_mod.BinarySearchTree(values)
        assert count_std(it.root) == n, "iterative node count"

        ag = agent_mod.BinarySearchTree(values)
        assert count_std(ag.root) == n, "agent node count"

        aa = agent_assisted_mod.BinarySearchTree()
        aa.insert(values)
        assert count_human_tree(aa.root) == n, "agent-assisted node count"

        impl_results: list[ImplResult] = []
        for key, label, builder in impl_specs:
            times: list[float] = []
            peaks: list[float] = []
            rss_deltas: list[float] = []
            for _ in range(repeats):
                el, pk, drss = _measure(lambda: builder(values))
                times.append(el)
                peaks.append(float(pk))
                rss_deltas.append(drss)
            impl_results.append(
                ImplResult(
                    key=key,
                    label=label,
                    time_s=_median(times),
                    peak_bytes=_median(peaks),
                    rss_delta_bytes=_median(rss_deltas),
                )
            )
        out.append(SizeBench(n=n, impls=tuple(impl_results)))

    return tuple(out)


def print_report(benches: tuple[SizeBench, ...], *, seed: int, repeats_note: str) -> None:
    rss_note = (
        "RSS Δ = median resident set size after build minus before (same process; noisy but OS-level RAM).\n"
        if psutil is not None
        else "RSS Δ unavailable (install psutil).\n"
    )
    print(
        "BST insertion benchmark — time: median wall seconds; "
        "tracemalloc peak: Python traced allocations during build.\n"
        + rss_note
        + "Human (bts_human) skips duplicates equal to an existing key.\n"
        "Human-in-the-loop, Agentic, and agent-assisted send duplicates to the right.\n"
    )
    for b in benches:
        print(f"n = {b.n:,} unique keys, shuffle seed = {seed}, repeats = {repeats_note}")
        impl_w = 48
        hdr = f"{'implementation':<{impl_w}} {'time (s)':>12} {'trace (MiB)':>12} {'RSS Δ (MiB)':>14}"
        print(hdr)
        for r in b.impls:
            rss_cell = (
                _fmt_mb(r.rss_delta_bytes)
                if not math.isnan(r.rss_delta_bytes)
                else "—"
            )
            print(
                f"{r.label:<{impl_w}} {r.time_s:12.4f} {_fmt_mb(r.peak_bytes):>12} {rss_cell:>14}"
            )
        print()
    print("Notes:")
    print("- Recursive insert (Agentic / bts_agentic) uses call stack depth O(tree height).")
    print("- Human / agent-assisted keep parent pointers; expect higher traced peak than val-only nodes.")
    print("- For worst-case height, use sorted order — recursion may fail for large n.")


def plot_benchmark(
    benches: tuple[SizeBench, ...],
    out_path: Path,
    *,
    show: bool = False,
) -> None:
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    keys_order = ("human", "agent_assisted", "iterative", "agent")
    short_labels = {
        "human": "Human",
        "agent_assisted": "Agent-assisted",
        "iterative": "Human-in-the-loop",
        "agent": "Agentic",
    }
    colors = {
        "human": "#e45756",
        "agent_assisted": "#eeca3b",
        "iterative": "#54a24b",
        "agent": "#4c78a8",
    }

    ns = [b.n for b in benches]
    x = np.arange(len(ns), dtype=float)
    n_impl = len(keys_order)
    # Bars in one n-group touch (pitch == width). Group span = n_impl * bar_width;
    # x ticks are 0,1,2,… so keep span < 1 to leave space between n values.
    bar_width = 0.2
    pitch = bar_width
    offsets = np.linspace(-(n_impl - 1) * pitch / 2, (n_impl - 1) * pitch / 2, n_impl)

    fig, (ax_time, ax_trace) = plt.subplots(
        2, 1, figsize=(10, 7), constrained_layout=True
    )
    fig.suptitle(
        "BST insertion (shuffled unique keys) — wall time · tracemalloc peak",
        fontsize=11,
    )

    for off, key in zip(offsets, keys_order):
        times = []
        trace_mib = []
        for b in benches:
            r = next(i for i in b.impls if i.key == key)
            times.append(r.time_s)
            trace_mib.append(r.peak_bytes / (1024 * 1024))
        ax_time.bar(
            x + off,
            times,
            bar_width,
            label=short_labels[key],
            color=colors[key],
            edgecolor="white",
            linewidth=0.5,
        )
        ax_trace.bar(
            x + off,
            trace_mib,
            bar_width,
            label=short_labels[key],
            color=colors[key],
            edgecolor="white",
            linewidth=0.5,
        )

    ax_time.set_ylabel("Time (s)")
    ax_time.set_title("Median wall time (insertion), seconds")
    ax_time.set_xticks(x)
    ax_time.set_xticklabels([f"n = {n:,}" for n in ns])
    ax_time.legend(loc="upper left", framealpha=0.9)
    ax_time.grid(axis="y", alpha=0.3)

    ax_trace.set_ylabel("Peak (MiB)")
    ax_trace.set_title("Median tracemalloc peak during build (Python traced allocations)")
    ax_trace.set_xticks(x)
    ax_trace.set_xticklabels([f"n = {n:,}" for n in ns])
    ax_trace.legend(loc="upper left", framealpha=0.9)
    ax_trace.grid(axis="y", alpha=0.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=500)
    if show:
        plt.show()
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="BST insertion benchmark")
    parser.add_argument("--quick", action="store_true", help="smaller n and fewer repeats")
    parser.add_argument(
        "--plot",
        action="store_true",
        help="write PNG chart next to this script",
    )
    parser.add_argument(
        "--plot-show",
        action="store_true",
        help="write PNG and open a display window (needs GUI backend)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="chart path (default: bst_benchmark_charts.png beside this script)",
    )
    args = parser.parse_args()

    seed = 42
    benches = run_benchmark(quick=args.quick)
    repeats_note = "2" if args.quick else "5"
    print_report(benches, seed=seed, repeats_note=repeats_note)

    out = args.output
    if out is None:
        out = Path(__file__).resolve().parent / "bst_benchmark_charts.png"

    if args.plot or args.plot_show:
        try:
            plot_benchmark(benches, out, show=args.plot_show)
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
