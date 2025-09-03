import streamlit as st
import numpy as np, pandas as pd

# Try to import a private real service; fall back to the demo.
try:
    from services import CarbonAPI       # (private, not in this repo)
except Exception:
    from services_demo import CarbonAPI  # (public demo)
api = CarbonAPI()

st.set_page_config(page_title="SarviCa — Demo", layout="wide")
st.title("SarviCa — Public Demo (Synthetic Data)")

with st.sidebar:
    st.header("Controls")
    year = st.slider("Year", 2018, 2025, 2020)
    size = st.select_slider("Demo map size (px)", options=[80, 120, 160], value=120)
    show_ndvi = st.checkbox("Show NDVI series", True)
    show_maps = st.checkbox("Show maps", True)

# NDVI series
if show_ndvi:
    st.subheader("NDVI Monthly (demo)")
    df = api.ndvi_series(year=year)
    st.line_chart(df.set_index("month")["ndvi"])

# Maps
if show_maps:
    st.subheader("Demo classification & height maps")
    cls, hgt = api.predict_maps(size=size)
    # Normalize to [0,1] for display
    cls_disp = (cls / max(1, cls.max())).astype(float)
    hgt_disp = (hgt / max(1.0, hgt.max())).astype(float)

    col1, col2 = st.columns(2)
    with col1:
        st.caption("Classification (demo, 4 classes)")
        st.image(cls_disp, clamp=True)
    with col2:
        st.caption("Height (demo, normalized)")
        st.image(hgt_disp, clamp=True)

# KPIs
st.subheader("Summary stats (demo)")
stats = api.carbon_stats()
c1, c2, c3 = st.columns(3)
c1.metric("Total tCO₂e", f"{stats['total_tCO2e']:.1f}")
c2.metric("Area (ha)", f"{stats['area_ha']:.1f}")
c3.metric("Avg height (m)", f"{stats['avg_height_m']:.1f}")

st.info("This demo runs without Earth Engine, weights, or proprietary data.")
