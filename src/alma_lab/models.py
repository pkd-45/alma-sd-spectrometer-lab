from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class InstrumentState(str, Enum):
    OFF = "OFF"
    READY = "READY"
    ARMED = "ARMED"
    ACQUIRING = "ACQUIRING"
    FAULT = "FAULT"


@dataclass(frozen=True)
class SpectrometerConfig:
    sample_rate_hz: float = 4096.0
    fft_size: int = 1024
    accumulation: int = 8
    overlap_fraction: float = 0.0
    window: str = "hann"
    backend: str = "auto"

    def validate(self) -> None:
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if self.fft_size < 8 or self.fft_size & (self.fft_size - 1):
            raise ValueError("fft_size must be a power of two and at least 8")
        if self.accumulation < 1:
            raise ValueError("accumulation must be at least 1")
        if not 0.0 <= self.overlap_fraction < 1.0:
            raise ValueError("overlap_fraction must be in [0, 1)")
        if self.window not in {"hann", "rectangular"}:
            raise ValueError("window must be 'hann' or 'rectangular'")
        if self.backend not in {"auto", "numpy", "cupy"}:
            raise ValueError("backend must be auto, numpy or cupy")


@dataclass
class SpectrumProduct:
    frequency_hz: np.ndarray
    power: np.ndarray
    n_frames: int
    backend: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Scan:
    scan_id: int
    x_arcsec: float
    y_arcsec: float
    on_counts: np.ndarray
    off_counts: np.ndarray
    tsys_k: float
    frequency_hz: np.ndarray


@dataclass
class ProcessedScan:
    scan_id: int
    x_arcsec: float
    y_arcsec: float
    frequency_hz: np.ndarray
    calibrated_k: np.ndarray
    baseline_subtracted_k: np.ndarray
    flagged: np.ndarray
    baseline_coefficients: np.ndarray
    baseline_rms_k: float


@dataclass
class TelemetryEvent:
    timestamp_utc: str
    state: InstrumentState
    event: str
    detail: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    cube_k: np.ndarray
    x_grid_arcsec: np.ndarray
    y_grid_arcsec: np.ndarray
    frequency_hz: np.ndarray
    processed_scans: List[ProcessedScan]
    qa: Dict[str, float]
    manifest: Dict[str, Any]
    product_paths: Optional[Tuple[str, str, str]] = None
