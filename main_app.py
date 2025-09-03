import streamlit as st
import numpy as np, pandas as pd


try:
    from services import CarbonAPI       # (private, not in this repo)
except Exception:
    from services_demo import CarbonAPI  # (public demo)


from streamlit_folium import st_folium
import folium
import branca.colormap as cm

api = CarbonAPI()
st.set_page_config(page_title="SarviCa — Demo", layout="wide")
st.title("SarviCa — Public Demo (Synthetic Data)")

with st.sidebar:
    st.header("Controls")
    year = st.slider("Year", 2018, 2025, 2020)
    size_choice = st.select_slider("Grid size", options=[10, 12, 16], value=12) 
    show_ndvi = st.checkbox("Show NDVI series", True)
    show_map  = st.checkbox("Show map", True)
    show_tbl  = st.checkbox("Show summary table", True)

tabs = st.tabs(["Overview", "Map", "Table", "About"])

# -------- Overview (NDVI + KPIs) --------
with tabs[0]:
    if show_ndvi:
        st.subheader("NDVI Monthly (demo)")
        df_ndvi = api.ndvi_series(year=year)
        st.line_chart(df_ndvi.set_index("month")["ndvi"])

    gj, classes, height = api.make_demo_grid(n=size_choice)
    df_sum = api.summary_table(classes, height)
    total_co2e = float(df_sum["tCO2e_total"].sum())
    total_area = float(df_sum["Area_ha"].sum())
    avg_height = float(height.mean())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total tCO₂e", f"{total_co2e:,.0f}")
    c2.metric("Area (ha)", f"{total_area:,.0f}")
    c3.metric("Avg height (m)", f"{avg_height:.1f}")

# -------- Map --------
with tabs[1]:
    if show_map:
        st.subheader("Demo map (height choropleth)")
        bounds = (48.05, 11.40, 48.20, 11.70)
        lat_c = (bounds[0] + bounds[2]) / 2
        lon_c = (bounds[1] + bounds[3]) / 2

        gj, classes, height = api.make_demo_grid(bounds=bounds, n=size_choice)

        m = folium.Map(location=[lat_c, lon_c], zoom_start=11, tiles="CartoDB positron")
        hmin, hmax = float(height.min()), float(height.max())
        cmap = cm.LinearColormap(colors=["#f7fcf5", "#74c476", "#006d2c"], vmin=hmin, vmax=hmax, caption="Height (m)")

        def style_fn(feat):
            h = feat["properties"]["height"]
            col = cmap(h)
            return {"fillColor": col, "color": col, "weight": 0.2, "fillOpacity": 0.6}

        folium.GeoJson(
            gj,
            name="Height (demo)",
            style_function=style_fn,
            tooltip=folium.GeoJsonTooltip(fields=["cell", "height", "klass"],
                                          aliases=["Cell", "Height (m)", "Class"]),
        ).add_to(m)
        cmap.add_to(m)
        folium.LayerControl().add_to(m)
        st_folium(m, height=520, use_container_width=True)

# -------- Table --------
with tabs[2]:
    if show_tbl:
        st.subheader("Carbon Estimation Summary (demo)")
        df_sum = api.summary_table(classes, height)
        st.dataframe(df_sum, use_container_width=True, hide_index=True)
        csv = df_sum.to_csv(index=False).encode("utf-8")
        st.download_button("Download summary (CSV)", data=csv, file_name="summary_demo.csv", mime="text/csv")

# -------- About --------
with tabs[3]:
    st.markdown("""
**Disclaimer:** This is a public demo with synthetic/open data. No Earth Engine, model weights, or proprietary code is used.  
**Production mapping:** the real app swaps `services_demo.CarbonAPI` with a private `services.CarbonAPI` that connects to GEE exports, model weights, and real AOIs.
    """)
