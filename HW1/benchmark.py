
#!/usr/bin/env python3
"""
Benchmark sobel_orig and bin/3.1 ... bin/3.8.
 
Each program is run RUNS times. The lowest and highest times are discarded,
and the mean and standard deviation of the remaining runs are reported.
 
Run it from the project root (the same directory where you run `make`),
since the programs read/write their input/output files in the current directory.
 
Usage:
    python3 benchmark.py                 # build with make, then benchmark everything
    python3 benchmark.py --no-build      # skip make
    python3 benchmark.py -r 12 -v 3.1 3.4 sobel_orig   # choose runs / versions
"""
 
import argparse
import csv
import re
import statistics
import subprocess
import sys
from pathlib import Path
 
DEFAULT_VERSIONS = ["sobel_orig"] + [f"3.{i}" for i in range(1, 9)]
 
# Matches e.g. "Total time =  0.123456 seconds"
# Change this if your program prints the time differently.
TIME_RE = re.compile(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*seconds", re.IGNORECASE)
PSNR_RE = re.compile(r"PSNR.*?:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?|inf)", re.IGNORECASE)
 
 
def exe_path(version: str) -> Path:
    """sobel_orig lives in the project root, 3.X lives in bin/."""
    p = Path(version) if version == "sobel_orig" else Path("bin") / version
    # Absolute path: a bare name like "sobel_orig" would be searched in PATH, not the current dir
    return p.resolve()
 
 
def run_once(exe: Path):
    """Run the program once, return (time_in_seconds, psnr_string)."""
    proc = subprocess.run([str(exe)], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"{exe} exited with code {proc.returncode}\n{proc.stderr}")
    m = TIME_RE.search(proc.stdout)
    if not m:
        sys.exit(
            f"Could not find a time in the output of {exe}.\n"
            f"Output was:\n{proc.stdout}\n"
            "Make sure the program prints the elapsed time (see the notes) "
            "or adjust TIME_RE in this script."
        )
    p = PSNR_RE.search(proc.stdout)
    return float(m.group(1)), (p.group(1) if p else "?")
 
 
def summarize(times):
    """Drop min and max, return (mean, stdev) of the rest (sample stdev)."""
    trimmed = sorted(times)[1:-1]
    return statistics.mean(trimmed), statistics.stdev(trimmed)
 
 
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--runs", type=int, default=12, help="runs per version (default 12)")
    ap.add_argument("-v", "--versions", nargs="*", default=DEFAULT_VERSIONS)
    ap.add_argument("--no-build", action="store_true", help="skip running make")
    ap.add_argument("-o", "--csv", default="results.csv", help="CSV output file")
    args = ap.parse_args()
 
    if args.runs < 4:
        sys.exit("Use at least 4 runs (2 get discarded, and stdev needs 2 left).")
 
    if not args.no_build:
        subprocess.run(["make", "all"], check=True)
 
    rows = []
    for v in args.versions:
        exe = exe_path(v)
        if not exe.exists():
            print(f"[skip] {exe} not found")
            continue
 
        times, psnr = [], "?"
        for i in range(args.runs):
            t, psnr = run_once(exe)
            times.append(t)
            print(f"  {v:<11} run {i + 1:>2}/{args.runs}: {t:.6f} s", flush=True)
 
        mean, std = summarize(times)
        rows.append((v, mean, std, psnr, times))
        print(f"==> {v}: mean = {mean:.6f} s, std = {std:.6f} s\n")
 
    if not rows:
        sys.exit("Nothing was measured.")
 
    base = rows[0][1]
    print(f"{'version':<12}{'mean (s)':>12}{'std (s)':>12}{'speedup':>10}  PSNR")
    print("-" * 56)
    for v, mean, std, psnr, _ in rows:
        print(f"{v:<12}{mean:>12.6f}{std:>12.6f}{base / mean:>9.2f}x  {psnr}")
    print(f"\n(speedup is relative to {rows[0][0]}; min and max of {args.runs} runs discarded)")
 
    with open(args.csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["version", "mean_s", "std_s", "psnr"] + [f"run{i + 1}" for i in range(args.runs)])
        for v, mean, std, psnr, times in rows:
            w.writerow([v, mean, std, psnr] + times)
    print(f"Raw data written to {args.csv}")
 
 
if __name__ == "__main__":
    main()