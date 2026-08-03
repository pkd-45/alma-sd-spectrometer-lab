#!/usr/bin/env python3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> int:
    product_path = Path("products/demo/single_dish_cube.npz")
    output_path = Path("docs/demo_quicklook.png")
    with np.load(product_path) as product:
        cube = product["cube_k"]
        frequency = product["frequency_hz"]
        x_grid = product["x_grid_arcsec"]
        y_grid = product["y_grid_arcsec"]
    peak_channel = int(np.nanargmax(np.nanmax(cube, axis=(0, 1))))
    image = cube[:, :, peak_channel]
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    displayed = ax.imshow(
        image,
        origin="lower",
        extent=[x_grid.min(), x_grid.max(), y_grid.min(), y_grid.max()],
        aspect="equal",
    )
    ax.set_xlabel("Offset x (arcsec)")
    ax.set_ylabel("Offset y (arcsec)")
    ax.set_title(f"Synthetic total-power line map at {frequency[peak_channel] / 1e9:.6f} GHz")
    fig.colorbar(displayed, ax=ax, label="Brightness temperature (K)")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
