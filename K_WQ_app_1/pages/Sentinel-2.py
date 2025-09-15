import streamlit as st
st.set_page_config(layout="wide", page_title="💧🛰️ Water quality by Sentinel-2")

import geemap.foliumap as geemap
import gee_data as gd
from folium import plugins
import pandas as pd


import rasterio
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os
from PIL import Image

def add_local_geotiff(map_object, tiff_path, layer_name, colormap='viridis', vmin=None, vmax=None):
    """Add a local GeoTIFF as an RGB overlay on a geemap folium-based map"""
    with rasterio.open(tiff_path) as src:
        array = src.read(1).astype(float)
        bounds = src.bounds

        # Normalize
        if vmin is None:
            vmin = np.nanmin(array)
        if vmax is None:
            vmax = np.nanmax(array)
        array = np.clip((array - vmin) / (vmax - vmin), 0, 1)

        # Apply colormap
        cmap = plt.get_cmap(colormap)
        rgba = cmap(array)
        rgb = (rgba[:, :, :3] * 255).astype(np.uint8)

        # Save image temporarily
        tmpfile = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        Image.fromarray(rgb).save(tmpfile.name)

        # Add to map
        map_object.add_image(
            image=tmpfile.name,
            bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
            layer_name=layer_name
        )

        os.unlink(tmpfile.name)  # Clean up

st.markdown("""
<style>
.index-font-1 {
    font-size: 17px;
    color: #20B2AA;
}
.index-font-2 {
    font-size: 17px;
    color: #B6D79A;    
}
.align-text {
    text-align: justify;
}
li {
    color: lightgray;
}
</style>
""", unsafe_allow_html=True)

st.subheader("💧🛰️ Water quality by Sentinel-2")

tab1, tab2, tab3, tab4 = st.tabs(["CDOM", "DOM", "Chla", "Turbidity"])

# Cache the result of the image loading function
@st.cache_data
def load_s1_images():
    return gd.get_flood_S1_imagery()
s1_images = load_s1_images()


@st.cache_data
def load_s2_images():
    return gd.get_flood_S2_imagery()
s2_images = load_s2_images()


@st.cache_data
def load_s2_indices_images():
    return gd.get_flood_S2_indices_imagery()
s2_indices_images = load_s2_indices_images()


@st.cache_data
def load_flood_water_mask():
    return gd.get_flood_water_mask()
water_masks = load_flood_water_mask()


with tab1:
    # Define display names and matching keys
    # Layer options
    #st.info("Use the selector below to switch between different **Sentinel-1 flood observations**.")

    layer_options_s1 = {
        "option1": "before",
        "option2": "after",
        "option3": "after_month"
    }

    selected_layers_s1 = st.pills(
        "Choose water index to display:",
        options=list(layer_options_s1.keys()),
        selection_mode="multi",
        key="S1"
    )

    with st.spinner("Wait for the map ..."):
        # --- Map Setup ---
        with st.spinner("Adding local turbidity layer..."):
            #turb_path = "/home/eouser/Desktop/K_WQ/tiff_to_bands/Turb.tif"  # update as needed
            Map = geemap.Map(layer_ctrl=True, center=[50.39, 17.05], zoom=10)
            Map.addLayer(gd.aoi_flood.style(color='red', fillColor='00000000', width=2), {}, 'Flood AOI')
    
        #add_local_geotiff(Map, turb_path, "Turbidity (Local TIFF)", colormap="nipy_spectral", vmin=0, vmax=30)
        Map.to_streamlit(height=700)

        # Add AOI boundary
        Map.addLayer(gd.aoi_flood.style(color='red', fillColor='00000000', width=2), {}, 'Flood AOI')
        #Map.addLayer(gd.aoi_turb)
        # Visualization parameters for Sentinel-1 VV band
        vis_params_s1 = {"min": -25, "max": 0}

        # Add selected layers
        for label_s1 in selected_layers_s1:
            key = layer_options_s1[label_s1]
            Map.addLayer(s1_images[key], vis_params_s1, f"S1: {label_s1}")

        st.markdown(
            "<div style='text-align: right; font-size: 0.90em; color: gray;'>"
            "💡 You can toggle layer visibility using the layer control pane in the upper-right corner of the map."
            "</div>",
            unsafe_allow_html=True
        )

        # Display map
        Map.to_streamlit(height=700)

with tab2:
    st.info("Use the selector below to switch between different **Sentinel-2 flood observations**.")

    layer_options_s2 = {
        "1️⃣🌤️ Before Flood": "before",
        "2️⃣🌊 After Flood": "after",
        "3️⃣🌱 One Month After": "after_month"
    }

    selected_layers_s2 = st.pills(
        "### Choose Sentinel-2 layers to display:",
        options=list(layer_options_s2.keys()),
        selection_mode="multi",
        key="S2"
    )

    with st.spinner("Wait for the map ..."):
        # --- Map Setup ---
        Map = geemap.Map(layer_ctrl=True, center=[50.39, 17.05], zoom=10, control_scale=True)
        minimap = plugins.MiniMap()
        Map.add_child(minimap)

        # Add AOI boundary
        Map.addLayer(gd.aoi_flood.style(color='red', fillColor='00000000', width=2), {}, 'Flood AOI')

        # Visualization parameters for Sentinel-1 VV band
        vis_params_rgb = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3, 'gamma': 1.3}
        vis_params_water = {'bands': ['B11', 'B8', 'B4'], 'min': 0, 'max': 0.3}

        for label_s2 in selected_layers_s2:
            key_s2 = layer_options_s2[label_s2]
            Map.addLayer(s2_images[key_s2], vis_params_rgb, f"S2: {label_s2} - RGB")
            Map.addLayer(s2_images[key_s2], vis_params_water, f"S2: {label_s2} - False Color")

        st.markdown(
            "<div style='text-align: right; font-size: 0.90em; color: gray;'>"
            "💡 You can toggle layer visibility using the layer control pane in the upper-right corner of the map."
            "</div>",
            unsafe_allow_html=True
        )

        # Display map
        Map.to_streamlit(height=700)

with tab3:
    st.info("Use the selector below to switch between different **Spectral Indices**.")

    layer_options_s2_indices = {
        "1️⃣🌤️ Before Flood": "before",
        "2️⃣🌊 After Flood": "after",
        "3️⃣🌱 One Month After": "after_month"
    }

    selected_layers_s2_indices = st.pills(
        "Choose Sentinel-2 layers to display:",
        options=list(layer_options_s2_indices.keys()),
        selection_mode="multi",
        default="1️⃣🌤️ Before Flood",
        key="S2_indices"
    )

    indices = {
        "AWEI": {
            "name": "💦 AWEI – Automated Water Extraction Index",
            "description": "Is designed to improve the detection of open surface water in satellite imagery. "
                           "It uses a specific combination of visible and infrared bands to effectively differentiate water bodies from shadows, dark soils, and built-up surfaces. "
                           "AWEI is especially useful in flood mapping and wetland monitoring, where traditional indices often confuse water with dark non-water features. "
                           "Its sensitivity to the spectral characteristics of water enables more accurate and automated water classification, even under challenging observation conditions (Feyisa et al. 2014).",
            "formula": r'''AWEI = 4 \cdot ({Green}-{SWIR1})- \\
            (0.25 \cdot {NIR}+2.75 \cdot {SWIR2})''',
            "ref": """<ul><li>Feyisa G.L., Meilby H., Fensholt R., Proud S.R. 2014 <i>"Automated Water Extraction Index: A new technique for surface water mapping using Landsat imagery"</i>, Remote Sensing of Environment, 140, 23-35. doi:10.1016/j.rse.2013.08.029.</li></ul>"""
        },
        "CGI": {
            "name": "🦠 CGI – Chlorophyll Green Index",
            "description": "In general, the chlorophyll index is applied to determine the total amount of chlorophyll in plants. "
                           "This variation uses the SWIR (resolution 60 meters and central wavelength at 945 nm) and Green channels in calculations.",
            "formula": r'''CGI = \frac{SWIR}{Green}-1''',
            "ref": """"""
        },
        "CDOM": {
            "name": "🦠 CDOM – Colored Dissolved Organic Matter",
            "description": "Is a water quality indicator used to assess optically active organic materials in water. "
                           "This parameter is influenced by two primary sources of organic matter. "
                           "The first source is the organic material that forms within the water body itself, such as phytoplankton. "
                           "The second source is organic matter that enters the water from external sources, like coal that may leach from the surrounding soil. "
                           "It has also been demonstrated that there is a correlation between content of methylmercury and CDOM in rivers (Fichot et al. 2016).",
            "formula": r'''CDOM = 537 \cdot \exp\left(-2.93 \cdot \frac{Green}{Red}\right)''',
            "ref": """<ul><li>Fichot C.G., Downing B.D., Bergamaschi B.A., Windham-Myers L., Marvin-DiPasquale M., Thompson D.R., Gierach M.M. 2016. <i>"High-Resolution Remote Sensing of Water Quality in the SanFrancisco Bay−Delta Estuary."</i>, Environmental Science and Technology, 50. doi:10.1021/acs.est.5b03518.</li></ul>"""
        },
        "DOC": {
            "name": "🦠 DOC – Dissolved Organic Carbon",
            "description": "Refers to the presence of organic carbon compounds that are dissolved in the water. "
                           "It serves as a key indicator of water quality, with higher levels often indicating pollution and potential for undesirable biological growth. "
                           "DOC may also be influenced by the density of other dissolved substances, such as metals. "
                           "Organic matter levels in the river are closely related to rainfall/runoff events, seasons and operational practices and typically range from 0.1 mg :small[$L^{-1}$] to 10-20 mg :small[$L^{-1}$] in fresh waters (Volk et al. 2002).",
            "formula": r'''DOC = 432 \cdot \exp\left(-2.24 \cdot \frac{Green}{Red}\right)''',
            "ref": """<ul><li>Volk C., Wood L., Johnson B., Robinson J., Wei Zhu H., Kaplan L. 2002. <i>"Monitoring dissolved organic carbon in surface and drinking waters."</i>, Journal of Environmental Monitoring, 4, 43-47. doi:10.1039/B107768F.</li></ul>"""
        }
    }

    col1, col2, col3 = st.columns([1, 0.05, 1.95])

    with col1:
        st.markdown("")
        selected_index = st.selectbox("Choose Spectral Index", list(indices.keys()))

        st.subheader(indices[selected_index]["name"])
        st.info(indices[selected_index]["description"])
        st.latex(indices[selected_index]["formula"])
        st.divider()
        st.markdown(indices[selected_index]["ref"], unsafe_allow_html=True)

    with col3:
        with st.spinner("Wait for the map ..."):
            # --- Map Setup ---
            Map = geemap.Map(layer_ctrl=True, center=[50.46, 17.19], zoom=12, control_scale=True)
            minimap = plugins.MiniMap()
            Map.add_child(minimap)

            # Add AOI boundary
            Map.addLayer(gd.aoi_flood.style(color='red', fillColor='00000000', width=2), {}, 'Flood AOI')

            colorScaleHex = [
                '#496FF2',
                '#82D35F',
                '#FEFD05',
                '#FD0004',
                '#8E2026',
                '#D97CF5'
            ]

            # Visualization parameters for Sentinel-1 VV band
            vis_params_indices = {
                'AWEI': {'min': -1, 'max': 1, 'palette': ['#f5f5dc', '#ffffcc', '#a1dab4', '#41b6c4', '#225ea8']},
                'CGI': {'min': 1, 'max': 5, 'palette': 'PuBuGn'},
                'CDOM': {'min': 5, 'max': 50, 'palette': colorScaleHex},
                'DOC': {'min': 10, 'max': 70, 'palette': colorScaleHex},
            }

            for label_s2_indices in selected_layers_s2_indices:
                key_s2 = layer_options_s2_indices[label_s2_indices]
                Map.addLayer(s2_indices_images[key_s2].select(selected_index), vis_params_indices[selected_index], f"S2: {label_s2_indices}")

            st.markdown(
                "<div style='text-align: right; font-size: 0.90em; color: gray;'>"
                "💡 You can toggle layer visibility using the layer control pane in the upper-right corner of the map."
                "</div>",
                unsafe_allow_html=True
            )

            #Map.add_colorbar(vis_params_indices[selected_index], label=selected_index)
            Map.add_colormap(width=3, height=0.15, vmin=vis_params_indices[selected_index]['min'],
                             vmax=vis_params_indices[selected_index]['max'],
                             palette=vis_params_indices[selected_index]['palette'],
                             label=selected_index, label_size=8, bg_color='white',
                             orientation='horizontal', position=(48, 4))
            # Display map
            Map.to_streamlit(height=750)


with tab4:
    data = {
        'Image': ['2024-08-10_S1', '2024-09-17_S1', '2024-10-16_S1'],
        'Flooded Area (m²)': [6.263716e+07, 9.072615e+07, 6.489486e+07],
        'Flooded Area (ha)': [6268.716207, 9072.614900, 6489.485646],
        'AOI Area (m²)': [2.528720e+09, 2.528720e+09, 2.528720e+09],
        'AOI Area (ha)': [252872.015348, 252872.015348, 252872.015348],
        'Flood % of AOI': [2.479007, 3.587829, 2.566312]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    st.info("Use the selector below to switch between different **Water Masks**.")

    layer_options_water = {
        "1️⃣🌤️ Before Flood": "before",
        "2️⃣🌊 After Flood": "after",
        "3️⃣🌱 One Month After": "after_month"
    }

    selected_layers_water = st.pills(
        "Choose Water Masks layers to display:",
        options=list(layer_options_water.keys()),
        selection_mode="multi",
        key="water_mask"
    )

    col1, col2 = st.columns([1.75, 1.25])

    with col1:
        with st.spinner("Wait for the map ..."):
            # --- Map Setup ---
            Map = geemap.Map(layer_ctrl=True, center=[50.39, 17.05], zoom=10, control_scale=True)
            minimap = plugins.MiniMap()
            Map.add_child(minimap)

            # Add AOI boundary
            Map.addLayer(gd.aoi_flood.style(color='red', fillColor='00000000', width=2), {}, 'Flood AOI')

            # Visualization parameters for Sentinel-1 VV band
            vis_params_water = {'palette': '#08519C'}

            # Add selected layers
            for label_water in selected_layers_water:
                key = layer_options_water[label_water]
                Map.addLayer(water_masks[key].selfMask(), vis_params_water, f"Water Mask: {label_water}")

            st.markdown(
                "<div style='text-align: right; font-size: 0.90em; color: gray;'>"
                "💡 You can toggle layer visibility using the layer control pane in the upper-right corner of the map."
                "</div>",
                unsafe_allow_html=True
            )

            # Display map
            Map.to_streamlit(height=700)

    with col2:
        st.markdown("### 📊 Flood Summary")
        st.caption("💡 Flooded area estimates for the selected AOI based on Sentinel-1 dates.")
        st.dataframe(df.style.format({
            "Flooded Area (m²)": "{:,.0f}",
            "Flooded Area (ha)": "{:,.2f}",
            "AOI Area (m²)": "{:,.0f}",
            "AOI Area (ha)": "{:,.2f}",
            "Flood % of AOI": "{:.2f}%"
        }))
