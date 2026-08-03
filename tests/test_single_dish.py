import numpy as np
import pytest

from alma_lab.pipeline import simulate_raster_scans
from alma_lab.single_dish import (
    calibrate_position_switch,
    process_scan,
    robust_channel_flags,
)


def test_position_switch_calibration() -> None:
    off = np.full(8, 1000.0)
    on = np.full(8, 1010.0)
    calibrated = calibrate_position_switch(on, off, 100.0)
    assert np.allclose(calibrated, 1.0)


def test_rfi_flagging_detects_spike() -> None:
    values = np.zeros(64)
    values[17] = 100.0
    flags = robust_channel_flags(values, sigma=5.0)
    assert flags[17]


def test_scan_processing_recovers_low_baseline_rms() -> None:
    scans, exclusion = simulate_raster_scans(n_side=3, n_channels=128)
    processed = process_scan(scans[4], exclusion, baseline_order=1)
    assert processed.baseline_rms_k < 0.5
    assert np.count_nonzero(processed.flagged) >= 0
    assert processed.baseline_coefficients.size == 2


def test_calibration_rejects_nonpositive_off() -> None:
    with pytest.raises(ValueError):
        calibrate_position_switch(np.ones(4), np.zeros(4), 100.0)
