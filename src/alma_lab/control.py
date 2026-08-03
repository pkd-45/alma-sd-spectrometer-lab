from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from .models import InstrumentState, SpectrometerConfig, SpectrumProduct, TelemetryEvent
from .spectrometer import accumulated_power_spectrum


class InvalidTransition(RuntimeError):
    pass


class SpectrometerController:
    """Small deterministic instrument-control state machine with telemetry."""

    def __init__(self, config: SpectrometerConfig) -> None:
        config.validate()
        self.config = config
        self.state = InstrumentState.OFF
        self.telemetry: List[TelemetryEvent] = []
        self._armed_scan_id: Optional[str] = None
        self._record("created")

    def _record(self, event: str, detail: Optional[Dict[str, object]] = None) -> None:
        self.telemetry.append(
            TelemetryEvent(
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                state=self.state,
                event=event,
                detail={} if detail is None else dict(detail),
            )
        )

    def initialise(self) -> None:
        if self.state not in {InstrumentState.OFF, InstrumentState.FAULT}:
            raise InvalidTransition(f"cannot initialise from {self.state}")
        self.state = InstrumentState.READY
        self._record("initialised")

    def arm(self, scan_id: str) -> None:
        if self.state != InstrumentState.READY:
            raise InvalidTransition(f"cannot arm from {self.state}")
        self._armed_scan_id = scan_id
        self.state = InstrumentState.ARMED
        self._record("armed", {"scan_id": scan_id})

    def acquire(self, samples: np.ndarray) -> SpectrumProduct:
        if self.state != InstrumentState.ARMED:
            raise InvalidTransition(f"cannot acquire from {self.state}")
        self.state = InstrumentState.ACQUIRING
        self._record("acquisition_started", {"sample_count": int(samples.size)})
        try:
            product = accumulated_power_spectrum(samples, self.config)
        except Exception as exc:
            self.state = InstrumentState.FAULT
            self._record("acquisition_failed", {"error": str(exc)})
            raise
        self.state = InstrumentState.READY
        self._record(
            "acquisition_completed",
            {
                "scan_id": self._armed_scan_id,
                "frames": product.n_frames,
                "backend": product.backend,
            },
        )
        self._armed_scan_id = None
        return product

    def inject_fault(self, reason: str) -> None:
        self.state = InstrumentState.FAULT
        self._record("fault_injected", {"reason": reason})

    def reset_fault(self) -> None:
        if self.state != InstrumentState.FAULT:
            raise InvalidTransition(f"cannot reset fault from {self.state}")
        self.state = InstrumentState.READY
        self._record("fault_reset")

    def shutdown(self) -> None:
        if self.state == InstrumentState.ACQUIRING:
            raise InvalidTransition("cannot shutdown during acquisition")
        self.state = InstrumentState.OFF
        self._record("shutdown")

    def write_telemetry_jsonl(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for item in self.telemetry:
                handle.write(
                    json.dumps(
                        {
                            "timestamp_utc": item.timestamp_utc,
                            "state": item.state.value,
                            "event": item.event,
                            "detail": item.detail,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
