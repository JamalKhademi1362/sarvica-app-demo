# Demo-only service layer: NO proprietary data/models here.
import numpy as np, pandas as pd

class CarbonAPI:
    def ndvi_series(self, year=2020):
        months = pd.date_range(f"{year}-01-01", periods=12, freq="MS")
        ndvi = np.clip(np.linspace(0.2, 0.8, 12) + np.random.normal(0, 0.03, 12), 0, 1)
        return pd.DataFrame({"month": months, "ndvi": ndvi})

    def predict_maps(self, size=120):
        rng = np.random.default_rng(42)
        cls = rng.integers(0, 4, size=(size, size))       # 4 demo classes
        hgt = np.clip(rng.normal(6, 2, size=(size, size)), 0, 20)  # meters
        return cls, hgt

    def carbon_stats(self):
        return {"total_tCO2e": 1234.5, "area_ha": 250.0, "avg_height_m": 6.8}
