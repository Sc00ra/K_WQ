import streamlit as st
import geemap.foliumap as geemap

st.set_page_config(layout="wide", page_title="Projet_description | Kraków water quality monitoring 🛰️")

try:
   from StringIO import StringIO
except ImportError:
    from io import StringIO

@st.cache_data
def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)

ee_authenticate(token_name="EARTHENGINE_TOKEN")


st.title("Kraków water quality monitoring🛰️")

st.markdown("""
The calibration of remote sensing water quality measurement using in-situ data is essential for improving its accuracy. This study aims to improve the reliability of Sentinel-2 derived measurements by calibrating them with in-situ spectroradiometric data collected from selected inland waters in the Kraków region. By integrating remote sensing with direct field observations, we enhance the precision of key water quality indicators. A dedicated measurement campaign will be conducted at two to three designated sites, where data collection will occur at regular intervals. Water samples will be taken near the shore and at the center of the water bodies to analyze key parameters such as colored dissolved organic matter (CDOM), dissolved organic matter (DOM), chlorophyll-a (Chla), and turbidity. Simultaneously, meteorological conditions will be recorded to assess environmental influences on water quality indicators. The calibration process involves for example the application of linear regression models to correlate satellite-derived measurements with in-situ observations. The study aims to enhance the accuracy and reliability of remote sensing techniques for water quality monitoring. The findings will contribute to improved methodologies for assessing aquatic ecosystems, with potential applications for regional and global water quality management.

""")
