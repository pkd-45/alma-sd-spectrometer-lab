import pytest

from alma_lab.control import InvalidTransition, SpectrometerController
from alma_lab.models import InstrumentState, SpectrometerConfig
from alma_lab.spectrometer import simulate_adc


def test_state_machine_and_telemetry() -> None:
    config = SpectrometerConfig(fft_size=128, accumulation=2, sample_rate_hz=1024.0)
    controller = SpectrometerController(config)
    assert controller.state == InstrumentState.OFF
    controller.initialise()
    controller.arm("scan-1")
    samples = simulate_adc(1024.0, 0.25, [(128.0, 1.0)], noise_std=0.01)
    product = controller.acquire(samples)
    assert product.n_frames == 2
    assert controller.state == InstrumentState.READY
    assert controller.telemetry[-1].event == "acquisition_completed"


def test_invalid_transition_is_rejected() -> None:
    controller = SpectrometerController(SpectrometerConfig())
    with pytest.raises(InvalidTransition):
        controller.arm("bad")


def test_fault_reset() -> None:
    controller = SpectrometerController(SpectrometerConfig())
    controller.initialise()
    controller.inject_fault("simulated over-temperature")
    assert controller.state == InstrumentState.FAULT
    controller.reset_fault()
    assert controller.state == InstrumentState.READY
