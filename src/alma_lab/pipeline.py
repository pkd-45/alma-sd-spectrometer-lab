from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from .models import PipelineResult, Scan
from .single_dish import grid_scans, process_scans


def simulate_raster_scans(
    n_side: int = 5,
    n_channels: int = 256,
    seed: int = 11,
) -> Tuple[List[Scan], Tuple[float, float]]:
    """Generate an ALMA-like *synthetic* total-power raster for software testing."""
    rng = np.random.default_rng(seed)
    frequency_hz = np.linspace(100.0e9, 100.2e9, n_channels)
    line_centre_hz = 100.1e9
    line_sigma_hz = 6.0e6
    positions = np.linspace(-24.0, 24.0, n_side)
    scans: List[Scan] = []
    scan_id = 0
    for y_arcsec in positions:
        for x_arcsec in positions:
            source_amplitude_k = 8.0 * np.exp(
                -0.5 * (x_arcsec**2 + y_arcsec**2) / 13.0**2
            )
            line = source_amplitude_k * np.exp(
                -0.5 * ((frequency_hz - line_centre_hz) / line_sigma_hz) ** 2
            )
            slope = rng.normal(0.0, 0.7)
            baseline_k = 0.8 + slope * (frequency_hz - np.mean(frequency_hz)) / np.ptp(
                frequency_hz
            )
            tsys_k = float(rng.uniform(70.0, 95.0))
            off_counts = 1000.0 + rng.normal(0.0, 1.5, n_channels)
            calibrated_target = line + baseline_k + rng.normal(0.0, 0.10, n_channels)
            on_counts = off_counts * (1.0 + calibrated_target / tsys_k)
            if scan_id % 7 == 0:
                on_counts[37] += 85.0
            scans.append(
                Scan(
                    scan_id=scan_id,
                    x_arcsec=float(x_arcsec),
                    y_arcsec=float(y_arcsec),
                    on_counts=on_counts,
                    off_counts=off_counts,
                    tsys_k=tsys_k,
                    frequency_hz=frequency_hz,
                )
            )
            scan_id += 1
    exclusion = (line_centre_hz - 4.0 * line_sigma_hz, line_centre_hz + 4.0 * line_sigma_hz)
    return scans, exclusion


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _qa(
    cube: np.ndarray,
    frequency_hz: np.ndarray,
    processed_baseline_rms: np.ndarray,
) -> Dict[str, float]:
    spatial_peak_spectrum = np.nanmax(cube, axis=(0, 1))
    peak_index = int(np.nanargmax(spatial_peak_spectrum))
    edge = np.r_[spatial_peak_spectrum[:40], spatial_peak_spectrum[-40:]]
    edge_rms = float(np.nanstd(edge))
    peak_k = float(spatial_peak_spectrum[peak_index])
    qa = {
        "finite_fraction": float(np.mean(np.isfinite(cube))),
        "peak_frequency_hz": float(frequency_hz[peak_index]),
        "peak_temperature_k": peak_k,
        "peak_snr": peak_k / max(edge_rms, 1e-12),
        "median_scan_baseline_rms_k": float(np.median(processed_baseline_rms)),
    }
    return qa


def run_demo_pipeline(output_dir: Path, workers: int = 1) -> PipelineResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    scans, exclusion = simulate_raster_scans()
    processed = process_scans(
        scans,
        line_exclusion_hz=exclusion,
        baseline_order=1,
        workers=workers,
    )
    frequency_hz = scans[0].frequency_hz
    x_grid = np.linspace(-30.0, 30.0, 21)
    y_grid = np.linspace(-30.0, 30.0, 21)
    cube = grid_scans(processed, x_grid, y_grid, frequency_hz)
    qa = _qa(
        cube,
        frequency_hz,
        np.asarray([scan.baseline_rms_k for scan in processed]),
    )
    if qa["finite_fraction"] < 0.99:
        raise RuntimeError("QA failed: finite cube fraction below 0.99")
    if qa["peak_snr"] < 10.0:
        raise RuntimeError("QA failed: line peak S/N below 10")
    if abs(qa["peak_frequency_hz"] - 100.1e9) > 2.0e6:
        raise RuntimeError("QA failed: recovered line frequency is outside tolerance")

    product_path = output_dir / "single_dish_cube.npz"
    qa_path = output_dir / "qa.json"
    manifest_path = output_dir / "manifest.json"
    np.savez_compressed(
        product_path,
        cube_k=cube,
        x_grid_arcsec=x_grid,
        y_grid_arcsec=y_grid,
        frequency_hz=frequency_hz,
    )
    qa_path.write_text(json.dumps(qa, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest: Dict[str, object] = {
        "software": "alma-sd-spectrometer-lab",
        "version": "0.1.1",
        "synthetic_data": True,
        "workers": workers,
        "inputs": {
            "scan_count": len(scans),
            "channels": int(frequency_hz.size),
            "line_exclusion_hz": list(exclusion),
        },
        "products": {
            product_path.name: _sha256(product_path),
            qa_path.name: _sha256(qa_path),
        },
        "qa": qa,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return PipelineResult(
        cube_k=cube,
        x_grid_arcsec=x_grid,
        y_grid_arcsec=y_grid,
        frequency_hz=frequency_hz,
        processed_scans=processed,
        qa=qa,
        manifest=manifest,
        product_paths=(str(product_path), str(qa_path), str(manifest_path)),
    )
