from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .models import ProcessedScan, Scan


def calibrate_position_switch(
    on_counts: np.ndarray, off_counts: np.ndarray, tsys_k: float
) -> np.ndarray:
    """Demonstration ON/OFF calibration: Tsys * (ON - OFF) / OFF."""
    if on_counts.shape != off_counts.shape:
        raise ValueError("ON and OFF spectra must have identical shapes")
    if tsys_k <= 0:
        raise ValueError("tsys_k must be positive")
    if np.any(off_counts <= 0):
        raise ValueError("OFF counts must be strictly positive")
    calibrated = tsys_k * (on_counts - off_counts) / off_counts
    return np.asarray(calibrated, dtype=np.float64)


def robust_channel_flags(values: np.ndarray, sigma: float = 8.0) -> np.ndarray:
    """Flag impulsive spectral outliers using first-difference median absolute deviation."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    diff = np.diff(values, prepend=values[0])
    median = np.median(diff)
    mad = np.median(np.abs(diff - median))
    if mad == 0:
        flags = np.abs(diff - median) > 0
    else:
        robust_sigma = 1.4826 * mad
        flags = np.abs(diff - median) > sigma * robust_sigma
    # Expand one channel to catch both edges of an impulsive spike.
    expanded = flags | np.roll(flags, -1)
    return np.asarray(expanded, dtype=np.bool_)


def polynomial_baseline(
    frequency_hz: np.ndarray,
    spectrum_k: np.ndarray,
    fit_mask: np.ndarray,
    order: int = 1,
) -> Tuple[np.ndarray, np.ndarray, float]:
    if frequency_hz.shape != spectrum_k.shape or fit_mask.shape != spectrum_k.shape:
        raise ValueError("frequency, spectrum and fit_mask must have identical shapes")
    if order < 0:
        raise ValueError("order must be non-negative")
    valid = fit_mask & np.isfinite(spectrum_k)
    if np.count_nonzero(valid) <= order:
        raise ValueError("insufficient baseline channels")
    centre = np.mean(frequency_hz)
    scale = np.ptp(frequency_hz)
    if scale == 0:
        raise ValueError("frequency axis has zero span")
    x = (frequency_hz - centre) / scale
    coefficients = np.polyfit(x[valid], spectrum_k[valid], deg=order)
    model = np.polyval(coefficients, x)
    residual = spectrum_k - model
    rms = float(np.sqrt(np.mean(residual[valid] ** 2)))
    return residual, coefficients, rms


def process_scan(
    scan: Scan,
    line_exclusion_hz: Optional[Tuple[float, float]] = None,
    baseline_order: int = 1,
) -> ProcessedScan:
    calibrated = calibrate_position_switch(scan.on_counts, scan.off_counts, scan.tsys_k)
    flags = robust_channel_flags(calibrated)
    baseline_mask = ~flags & np.isfinite(calibrated)
    if line_exclusion_hz is not None:
        lower, upper = line_exclusion_hz
        baseline_mask &= ~((scan.frequency_hz >= lower) & (scan.frequency_hz <= upper))
    corrected, coefficients, rms = polynomial_baseline(
        scan.frequency_hz, calibrated, baseline_mask, order=baseline_order
    )
    corrected = corrected.copy()
    corrected[flags] = np.nan
    return ProcessedScan(
        scan_id=scan.scan_id,
        x_arcsec=scan.x_arcsec,
        y_arcsec=scan.y_arcsec,
        frequency_hz=scan.frequency_hz,
        calibrated_k=calibrated,
        baseline_subtracted_k=corrected,
        flagged=flags,
        baseline_coefficients=coefficients,
        baseline_rms_k=rms,
    )


def _process_scan_star(args: Tuple[Scan, Optional[Tuple[float, float]], int]) -> ProcessedScan:
    return process_scan(*args)


def process_scans(
    scans: Sequence[Scan],
    line_exclusion_hz: Optional[Tuple[float, float]],
    baseline_order: int = 1,
    workers: int = 1,
) -> List[ProcessedScan]:
    tasks = [(scan, line_exclusion_hz, baseline_order) for scan in scans]
    if workers <= 1:
        return [_process_scan_star(task) for task in tasks]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_process_scan_star, tasks))


def spectral_regrid(
    source_frequency_hz: np.ndarray,
    source_values: np.ndarray,
    target_frequency_hz: np.ndarray,
) -> np.ndarray:
    valid = np.isfinite(source_values)
    if np.count_nonzero(valid) < 2:
        return np.full(target_frequency_hz.shape, np.nan)
    return np.interp(
        target_frequency_hz,
        source_frequency_hz[valid],
        source_values[valid],
        left=np.nan,
        right=np.nan,
    )


def grid_scans(
    scans: Iterable[ProcessedScan],
    x_grid_arcsec: np.ndarray,
    y_grid_arcsec: np.ndarray,
    target_frequency_hz: np.ndarray,
    kernel_sigma_arcsec: float = 9.0,
) -> np.ndarray:
    if kernel_sigma_arcsec <= 0:
        raise ValueError("kernel_sigma_arcsec must be positive")
    scan_list = list(scans)
    cube = np.zeros(
        (y_grid_arcsec.size, x_grid_arcsec.size, target_frequency_hz.size), dtype=np.float64
    )
    weights = np.zeros((y_grid_arcsec.size, x_grid_arcsec.size), dtype=np.float64)
    xx, yy = np.meshgrid(x_grid_arcsec, y_grid_arcsec)
    for scan in scan_list:
        spectrum = spectral_regrid(
            scan.frequency_hz, scan.baseline_subtracted_k, target_frequency_hz
        )
        finite = np.isfinite(spectrum)
        if not np.any(finite):
            continue
        distance2 = (xx - scan.x_arcsec) ** 2 + (yy - scan.y_arcsec) ** 2
        spatial_weight = np.exp(-0.5 * distance2 / kernel_sigma_arcsec**2)
        cube[..., finite] += spatial_weight[..., None] * spectrum[finite]
        weights += spatial_weight
    valid_pixels = weights > 0
    cube[valid_pixels, :] /= weights[valid_pixels, None]
    cube[~valid_pixels, :] = np.nan
    return cube
