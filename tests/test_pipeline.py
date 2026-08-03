import json
from pathlib import Path

import numpy as np

from alma_lab.pipeline import run_demo_pipeline


def test_end_to_end_pipeline_and_provenance(tmp_path: Path) -> None:
    result = run_demo_pipeline(tmp_path, workers=1)
    assert result.cube_k.shape == (21, 21, 256)
    assert result.qa["peak_snr"] > 10.0
    assert abs(result.qa["peak_frequency_hz"] - 100.1e9) < 2.0e6
    assert result.qa["finite_fraction"] > 0.99
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["synthetic_data"] is True
    assert "single_dish_cube.npz" in manifest["products"]
    with np.load(tmp_path / "single_dish_cube.npz") as product:
        assert product["cube_k"].shape == result.cube_k.shape
