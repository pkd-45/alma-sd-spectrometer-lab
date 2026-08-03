import numpy as np
import pytest

from alma_lab.models import SpectrometerConfig
from alma_lab.spectrometer import accumulated_power_spectrum, simulate_adc


def test_fft_recovers_injected_tone() -> None:
    config = SpectrometerConfig(sample_rate_hz=4096.0, fft_size=1024, accumulation=8)
    samples = simulate_adc(
        sample_rate_hz=config.sample_rate_hz,
        duration_s=config.fft_size * config.accumulation / config.sample_rate_hz,
        tones=[(512.0, 2.0)],
        noise_std=0.05,
    )
    product = accumulated_power_spectrum(samples, config)
    peak = product.frequency_hz[1:][np.argmax(product.power[1:])]
    assert peak == pytest.approx(512.0, abs=config.sample_rate_hz / config.fft_size)
    assert product.n_frames == 8
    assert product.backend == "numpy"


def test_config_rejects_non_power_of_two_fft() -> None:
    with pytest.raises(ValueError):
        SpectrometerConfig(fft_size=1000).validate()
