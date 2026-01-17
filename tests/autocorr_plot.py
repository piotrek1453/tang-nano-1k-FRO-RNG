#!/usr/bin/env python3
"""
Simple autocorrelation plotter for TRNG bit samples.

Reads a text file where each character is a bit ('0' or '1'),
computes the normalized autocorrelation for lags k = 0..max_lag,
and saves or shows a plot.

Usage:
    python tests/autocorr_plot.py --input tests/data/output/ascii/1.txt --max-lag 512 --clock-mhz 1 --output tests/data/output/autocorr.png

If --output is omitted, the plot is shown interactively.
"""

import argparse
from typing import List

try:
    import matplotlib.pyplot as plt
except Exception as e:
    raise SystemExit(
        f"{e}\nmatplotlib is required to plot. Install via 'pip install matplotlib'."
    )


def read_bits(path: str) -> List[int]:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    # Filter to 0/1 and convert
    bits = []
    for ch in data:
        if ch == "0":
            bits.append(0)
        elif ch == "1":
            bits.append(1)
        # silently ignore other characters (e.g., whitespace/newlines)
    if not bits:
        raise ValueError("No bits found in input file.")
    return bits


def autocorr(bits: List[int], max_lag: int) -> List[float]:
    n = len(bits)
    if max_lag >= n:
        max_lag = n - 1
    x = [float(b) for b in bits]
    mean = sum(x) / n
    var = sum((xi - mean) ** 2 for xi in x) / n
    # If variance is zero (all bits same), correlation is undefined -> return zeros
    if var == 0:
        return [0.0] * (max_lag + 1)

    r = []
    for k in range(max_lag + 1):
        s = 0.0
        denom = n - k
        for i in range(n - k):
            s += (x[i] - mean) * (x[i + k] - mean)
        r.append(s / (denom * var))
    return r


def _choose_time_unit(max_lag: int, fs_hz: float) -> tuple[str, float]:
    t_span = max_lag / fs_hz
    if t_span < 1e-6:
        return ("ns", 1e9)
    if t_span < 1e-3:
        return ("µs", 1e6)
    if t_span < 1.0:
        return ("ms", 1e3)
    return ("s", 1.0)


def plot_autocorr(r: List[float], output: str | None, title: str, fs_hz: float | None):
    plt.figure(figsize=(10, 4))
    ax = plt.gca()
    ax.plot(range(len(r)), r, lw=1.2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Lag [samples]")
    ax.set_ylabel("Autocorrelation")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    if fs_hz and fs_hz > 0:
        unit, factor = _choose_time_unit(len(r) - 1, fs_hz)

        def lag_to_time(k: float) -> float:
            return (k / fs_hz) * factor

        def time_to_lag(t: float) -> float:
            return (t / factor) * fs_hz

        secax = ax.secondary_xaxis("top", functions=(lag_to_time, time_to_lag))
        secax.set_xlabel(f"Time offset [{unit}]")

    plt.tight_layout()
    if output:
        plt.savefig(output, dpi=150)
        print(f"Saved autocorrelation plot to: {output}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot autocorrelation for TRNG bitstream"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="tests/data/output/ascii/1.txt",
        help="Path to input text file with bits (default: tests/data/output/ascii/1.txt)",
    )
    parser.add_argument(
        "--max-lag",
        "-m",
        type=int,
        default=512,
        help="Maximum lag for autocorrelation (default: 512)",
    )
    parser.add_argument(
        "--clock-mhz",
        type=float,
        required=True,
        help="Clock frequency that clocks RNG, in MHz (required)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output PNG path. If omitted, show interactive plot",
    )
    args = parser.parse_args()

    bits = read_bits(args.input)
    max_lag = args.max_lag
    if max_lag <= 0:
        # choose a reasonable default based on length
        max_lag = min(1024, max(1, len(bits) // 10))

    r = autocorr(bits, max_lag)
    fs_hz = args.clock_mhz * 1e6
    title = f"Autocorrelation: {args.input} (n={len(bits)}, max_lag={len(r) - 1}, f_clk={args.clock_mhz} MHz)"
    plot_autocorr(r, args.output, title, fs_hz)


if __name__ == "__main__":
    main()
