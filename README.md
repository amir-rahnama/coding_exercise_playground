# Coding exercise playground

Small Python exercises: **binary search trees (BST)** with benchmarks, and a **salary / clock-in** example with tests.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest         # needed for salary.py tests
```

## `bst/` — BST implementations and benchmarks

Four BST variants (same idea, different styles):

| File | Role |
|------|------|
| `bst_human.py` | Hand-written style; parent pointers; recursive insert |
| `bst_agent_assisted.py` | Iterative insert, `__slots__`, compact nodes |
| `bst_human_in_the_loop.py` | Iterative insert, class API |
| `bst_agentic.py` | Recursive insert, class API |

**Benchmarks** (run from repo root; they load the four `bts_*.py` files from `bts/`):

```bash
python bst/benchmark_bst_time_memroy.py --plot          # time + tracemalloc (+ RSS in table if psutil)
python bst/benchmark_bst_time_memroy.py --quick --plot  # smaller n, faster

python bst/benchmark_bst_readability.py --plot        # radon + rank chart (PNG)
```

Shared plot flags: `--plot`, `--plot-show`, `--output path/to/file.png`. Charts default to **500 dpi** in code.

## `Python/salary.py` — hourly pay from clock in/out

`Salary` tracks staff, hourly rate, clock-in/out strings (`"%Y-%m-%d %H:%M:%S"`), and computes pay from elapsed time.

```bash
python python/salary.py          # demo main
pytest python/salary.py -q       # tests
```

---

This repo is for learning and comparison; benchmarks measure **proxies** (time, allocations, static metrics), not definitive “quality.”
