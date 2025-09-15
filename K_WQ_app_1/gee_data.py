import ee
import streamlit as st
import geemap.foliumap as geemap

# Area of interest
#aoi = ee.FeatureCollection("projects/jakub-hempel/assets/powiaty")
#aoi_flood = ee.FeatureCollection("projects/jakub-hempel/assets/aoi_flood_v2")
aoi = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017") \
    .filter(ee.Filter.eq('country_na', 'Poland'))

aoi_flood = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017") \
    .filter(ee.Filter.eq('country_na', 'Poland'))

aoi_turb = "/home/eouser/Desktop/K_WQ/tiff_to_bands/Turb.tif"

# Base asset path
asset_path = 'projects/jakub-hempel/assets/'

# Band renaming helper
def rename_bands(name, image):
    if name.startswith('S1'):
        return image.select(['b1'], ['VV'])
    elif name.startswith('S2') and 'indices' in name:
        return image.select([0, 1, 2, 3], ['AWEI', 'CGI', 'CDOM', 'DOC'])
    elif name.startswith('S2') and 'bands' in name:
        return image.select([0, 1, 2, 3, 4, 5], ['B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
    else:
        return image


# Helper: extract key like 'before', 'after_month'
def extract_key(name, prefix):
    # Remove the prefix
    key = name.replace(prefix, '')

    # Remove common suffix patterns
    for suffix in ['_Flood_Clip', '_indices_Clip', '_bands_Clip', '_Clip']:
        key = key.replace(suffix, '')

    return key.strip('_').lower()


# Sentinel-1 images
@st.cache_resource
def get_flood_S1_imagery():
    names = ['S1_before_Clip', 'S1_after_Clip', 'S1_after_month_Clip']
    return {
        extract_key(name, 'S1_'): rename_bands(name, ee.Image(asset_path + name))
        for name in names
    }


# Sentinel-2 RGB
@st.cache_resource
def get_flood_S2_imagery():
    names = ['S2_before_bands_Clip', 'S2_after_bands_Clip', 'S2_after_month_bands_Clip']
    return {
        extract_key(name, 'S2_'): rename_bands(name, ee.Image(asset_path + name))
        for name in names
    }


# Sentinel-2 Indices
@st.cache_resource
def get_flood_S2_indices_imagery():
    names = ['S2_before_indices_Clip', 'S2_after_indices_Clip', 'S2_after_month_indices_Clip']
    return {
        extract_key(name, 'S2_'): rename_bands(name, ee.Image(asset_path + name))
        for name in names
    }


# Water/wetness classification masks
@st.cache_resource
def get_flood_water_mask():
    names = [
        'Water_Wetness_Before_Flood_Clip',
        'Water_Wetness_After_Flood_Clip',
        'Water_Wetness_After_Month_Flood_Clip'
    ]
    return {
        extract_key(name, 'Water_Wetness_'): rename_bands(name, ee.Image(asset_path + name))
        for name in names
    }


# Static layers
@st.cache_resource
def get_water_wetness_layer():
    return rename_bands('WaterWetness_Layer', ee.Image(asset_path + 'WaterWetness_Layer'))


@st.cache_resource
def get_wwpi_layer():
    return rename_bands('WWPI_Layer', ee.Image(asset_path + 'WWPI_Layer'))

