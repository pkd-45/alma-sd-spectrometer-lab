#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time

from alma_lab.models import SpectrometerConfig
from alma_lab.spectrometer import accumulated_power_spectrum, simulate_adc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["numpy", "cupy", "auto"], default="auto")
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()
    config = SpectrometerConfig(fft_size=4096, accumulation=32, backend=args.backend)
    samples = simulate_adc(
        sample_rate_hz=config.sample_rate_hz,
        duration_s=config.fft_size * config.accumulation / config.sample_rate_hz,
        tones=[(512.0, 2.0)],
    )
    durations = []
    backend = "unknown"
    for _ in range(args.repeats):
        start = time.perf_counter()
        product = accumulated_power_spectrum(samples, config)
        durations.append(time.perf_counter() - start)
        backend = product.backend
    print(
        json.dumps(
            {
                "backend": backend,
                "fft_size": config.fft_size,
                "accumulation": config.accumulation,
                "repeats": args.repeats,
                "best_seconds": min(durations),
                "median_seconds": sorted(durations)[len(durations) // 2],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
