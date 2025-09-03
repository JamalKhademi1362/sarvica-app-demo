# Demo-only service layer: NO proprietary data/models here.
import numpy as np, pandas as pd

class CarbonAPI:
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def ndvi_series(self, year=2020):
        months = pd.date_range(f"{year}-01-01", periods=12, freq="MS")
        ndvi = np.clip(np.linspace(0.18, 0.8, 12) + self.rng.normal(0, 0.03, 12), 0, 1)
        return pd.DataFrame({"month": months, "ndvi": ndvi})

    def make_demo_grid(self, bounds=(48.05, 11.40, 48.20, 11.70), n=12):
        """
        می‌سازد: یک GeoJSON ساده از گرید مربعی روی حوالی مونیخ + آرایه‌ی کلاس/ارتفاع
        bounds = (lat_min, lon_min, lat_max, lon_max)
        """
        lat_min, lon_min, lat_max, lon_max = bounds
        lats = np.linspace(lat_min, lat_max, n + 1)
        lons = np.linspace(lon_min, lon_max, n + 1)

        classes = self.rng.integers(0, 4, size=(n, n))                     # 4 کلاس دمو
        height  = np.clip(self.rng.normal(6, 2, size=(n, n)), 0, 20)       # متر

        features = []
        for i in range(n):
            for j in range(n):
                # چهارگوش هر سلول (توجه: GeoJSON = [lon, lat])
                ring = [
                    [lons[j],   lats[i]],
                    [lons[j+1], lats[i]],
                    [lons[j+1], lats[i+1]],
                    [lons[j],   lats[i+1]],
                    [lons[j],   lats[i]],
                ]
                features.append({
                    "type": "Feature",
                    "properties": {
                        "cell": f"{i}-{j}",
                        "klass": int(classes[i, j]),
                        "height": float(height[i, j]),
                    },
                    "geometry": {"type": "Polygon", "coordinates": [ring]},
                })
        gj = {"type": "FeatureCollection", "features": features}
        return gj, classes, height

    def summary_table(self, classes, height, cell_area_ha: float = 12.5):
        names = {0: "Urban", 1: "Forest", 2: "Grassland", 3: "Cropland"}
        flat_c = classes.ravel()
        flat_h = height.ravel()
        rows = []
        for k in range(4):
            mask = (flat_c == k)
            area = mask.sum() * cell_area_ha
            avg_h = float(flat_h[mask].mean()) if mask.any() else 0.0
            agb_t_ha = round(avg_h * 15.0, 2)   # ضریب ساختگی برای دمو
            tco2e_total = round(agb_t_ha * 3.67 * area, 1)
            rows.append([names[k], area, agb_t_ha, tco2e_total])
        return pd.DataFrame(rows, columns=["Class", "Area_ha", "AGB_t/ha", "tCO2e_total"])
