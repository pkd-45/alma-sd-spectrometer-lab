from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from .control import SpectrometerController
from .models import SpectrometerConfig
from .pipeline import run_demo_pipeline
from .spectrometer import simulate_adc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ALMA JD1/JD2 application demonstrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="run the synthetic single-dish pipeline")
    demo.add_argument("--output", type=Path, default=Path("products/demo"))
    demo.add_argument("--workers", type=int, default=1)

    spectrometer = subparsers.add_parser("spectrometer", help="run the simulated spectrometer")
    spectrometer.add_argument("--output", type=Path, default=Path("products/spectrometer"))
    spectrometer.add_argument("--backend", choices=["auto", "numpy", "cupy"], default="auto")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        result = run_demo_pipeline(args.output, workers=args.workers)
        print(json.dumps(result.qa, indent=2, sort_keys=True))
        return 0

    config = SpectrometerConfig(backend=args.backend)
    controller = SpectrometerController(config)
    controller.initialise()
    controller.arm("demo-0001")
    samples = simulate_adc(
        sample_rate_hz=config.sample_rate_hz,
        duration_s=config.fft_size * config.accumulation / config.sample_rate_hz,
        tones=[(512.0, 2.0)],
    )
    product = controller.acquire(samples)
    args.output.mkdir(parents=True, exist_ok=True)
    controller.write_telemetry_jsonl(args.output / "telemetry.jsonl")
    output = {
        "backend": product.backend,
        "frames": product.n_frames,
        "peak_frequency_hz": float(product.frequency_hz[1:][product.power[1:].argmax()]),
    }
    (args.output / "spectrum_summary.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
