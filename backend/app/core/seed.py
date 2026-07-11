from sqlalchemy.orm import Session

from app.models.app_settings import AppSettings
from app.models.dataset import Dataset, DatasetCategory, DatasetProvider
from app.models.indicator import Indicator, IndicatorCategory

DATASETS = [
    dict(name="Sentinel-2 SR", provider=DatasetProvider.SENTINEL_2, gee_collection="COPERNICUS/S2_SR_HARMONIZED",
         description="10-60m multispectral imagery, revisit every 5 days.", resolution="10 m", category=DatasetCategory.VEGETATION),
    dict(name="Landsat 8", provider=DatasetProvider.LANDSAT_8, gee_collection="LANDSAT/LC08/C02/T1_L2",
         description="30m multispectral imagery, revisit every 16 days.", resolution="30 m", category=DatasetCategory.LAND_COVER),
    dict(name="CHIRPS Daily", provider=DatasetProvider.CHIRPS, gee_collection="UCSB-CHG/CHIRPS/DAILY",
         description="Daily precipitation estimates, ~5km resolution.", resolution="5000 m", category=DatasetCategory.CLIMATE),
    dict(name="MODIS Land Surface Temperature", provider=DatasetProvider.MODIS, gee_collection="MODIS/061/MOD11A1",
         description="Daily land surface temperature, 1km resolution.", resolution="1000 m", category=DatasetCategory.CLIMATE),
    dict(name="WorldPop Population Density", provider=DatasetProvider.WORLDPOP, gee_collection="WorldPop/GP/100m/pop",
         description="100m gridded population estimates.", resolution="100 m", category=DatasetCategory.POPULATION),
]

INDICATORS = [
    # Végétation
    dict(name="NDVI", category=IndicatorCategory.VEGETATION, unit="index", color="#22c55e", icon="🌿",
         formula="(NIR - Red) / (NIR + Red)", description="Normalized Difference Vegetation Index.",
         documentation="NDVI measures vegetation greenness and vigor by contrasting near-infrared reflectance (high for healthy plants) with red reflectance (absorbed by chlorophyll). Values range from -1 to 1, with dense healthy vegetation typically above 0.6.",
         applications="Crop monitoring, biomass estimation, drought screening, forest health",
         supported_dataset="Sentinel-2, Landsat 8", default_resolution="10 m",
         min_value=-0.2, max_value=0.9, color_palette='["#a50026","#fee08b","#66bd63","#1a9850"]'),
    dict(name="EVI", category=IndicatorCategory.VEGETATION, unit="index", color="#16a34a", icon="🌱",
         formula="2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)", description="Enhanced Vegetation Index.",
         documentation="EVI improves on NDVI in areas of dense canopy by correcting for canopy background signal and atmospheric influences, using the blue band in addition to red and NIR.",
         applications="Dense canopy monitoring, tropical forest analysis, precision agriculture",
         supported_dataset="Sentinel-2, Landsat 8", default_resolution="10 m",
         min_value=-0.2, max_value=0.9, color_palette='["#a50026","#fee08b","#66bd63","#1a9850"]'),
    dict(name="SAVI", category=IndicatorCategory.VEGETATION, unit="index", color="#65a30d", icon="🍃",
         formula="((NIR - Red) / (NIR + Red + 0.5)) * 1.5", description="Soil-Adjusted Vegetation Index.",
         documentation="SAVI adjusts NDVI for soil brightness in areas of sparse vegetation using a soil-brightness correction factor (L=0.5), making it more reliable in arid and semi-arid regions.",
         applications="Sparse vegetation, arid land monitoring, early-season crop growth",
         supported_dataset="Sentinel-2, Landsat 8", default_resolution="10 m",
         min_value=-0.2, max_value=0.9, color_palette='["#a50026","#fee08b","#66bd63","#1a9850"]'),
    dict(name="Biomasse végétale", category=IndicatorCategory.VEGETATION, unit="t/ha", color="#4d7c0f", icon="🌳",
         formula="100 * NDVI²  (illustrative proxy, not calibrated)", description="Estimated above-ground vegetation biomass.",
         documentation="An illustrative NDVI-based proxy for above-ground biomass. This is not a field-calibrated allometric model — treat results as a relative indicator, not an absolute biomass measurement.",
         applications="Forest inventory (indicative), carbon stock screening, vegetation density comparison",
         supported_dataset="Sentinel-2, Landsat 8", default_resolution="10 m",
         min_value=0, max_value=100, color_palette='["#ffffcc","#78c679","#004529"]'),
    # Eau
    dict(name="NDWI", category=IndicatorCategory.WATER, unit="index", color="#0ea5e9", icon="💧",
         formula="(Green - NIR) / (Green + NIR)", description="Normalized Difference Water Index.",
         documentation="NDWI highlights open water bodies and surface moisture by contrasting green reflectance (high over water) with NIR reflectance (absorbed by water).",
         applications="Flood mapping, wetland delineation, surface water tracking, reservoir monitoring",
         supported_dataset="Sentinel-2, Landsat 8", default_resolution="10 m",
         min_value=-0.5, max_value=0.6, color_palette='["#f7fbff","#6baed6","#08306b"]'),
    dict(name="Humidité des sols", category=IndicatorCategory.WATER, unit="%", color="#38bdf8", icon="🌧️",
         formula="NASA SMAP L4 sm_surface × 100", description="Surface soil moisture content.",
         documentation="Volumetric surface soil moisture (0-5cm) from the NASA SMAP Level-4 model, expressed as a percentage.",
         applications="Irrigation planning, drought early-warning, agricultural water stress",
         supported_dataset="NASA SMAP L4", default_resolution="~9 km",
         min_value=0, max_value=50, color_palette='["#f6e8c3","#5ab4ac","#01665e"]'),
    dict(name="Disponibilité en eau", category=IndicatorCategory.WATER, unit="%", color="#0284c7", icon="🏞️",
         formula="JRC Global Surface Water occurrence", description="Water availability index over the AOI.",
         documentation="Historical frequency (1984-2021) with which a pixel was observed as water, from the JRC Global Surface Water dataset. A static reference layer, not date-filtered.",
         applications="Water resource inventory, reservoir/lake extent, seasonal water body mapping",
         supported_dataset="JRC Global Surface Water", default_resolution="30 m",
         min_value=0, max_value=100, color_palette='["#f7fbff","#6baed6","#08306b"]'),
    # Température
    dict(name="Température de surface", category=IndicatorCategory.TEMPERATURE, unit="°C", color="#ef4444", icon="🌡️",
         formula="LST_Day_1km * 0.02 - 273.15", description="Land Surface Temperature.",
         documentation="Daytime land surface temperature from MODIS, converted from Kelvin to Celsius.",
         applications="Urban heat islands, drought monitoring, agricultural stress detection",
         supported_dataset="MODIS", default_resolution="1000 m",
         min_value=0, max_value=45, color_palette='["#313695","#fee090","#a50026"]'),
    dict(name="Anomalies thermiques", category=IndicatorCategory.TEMPERATURE, unit="°C", color="#dc2626", icon="🔥",
         formula="LST(current) - LST(2015-2019 baseline, same season)", description="Deviation from the long-term temperature baseline.",
         documentation="Difference between the mean land surface temperature over the selected period and the mean over the same calendar-day window across a 2015-2019 reference baseline.",
         applications="Heatwave detection, climate change monitoring, urban heat island trends",
         supported_dataset="MODIS", default_resolution="1000 m",
         min_value=-5, max_value=5, color_palette='["#2166ac","#f7f7f7","#b2182b"]'),
    # Climat
    dict(name="Précipitations", category=IndicatorCategory.CLIMATE, unit="mm", color="#6366f1", icon="🌦️",
         formula="sum(precipitation)", description="Aggregated precipitation over the selected period.",
         documentation="Total precipitation accumulated over the selected date range, from CHIRPS daily rainfall estimates.",
         applications="Rainfall anomalies, seasonal monitoring, water resource planning",
         supported_dataset="CHIRPS", default_resolution="~5 km",
         min_value=0, max_value=200, color_palette='["#ffffcc","#41b6c4","#225ea8"]'),
    dict(name="Sécheresse", category=IndicatorCategory.CLIMATE, unit="index", color="#a16207", icon="🏜️",
         formula="(rainfall - baseline mean) / baseline stdDev  (2015-2019 reference)", description="Drought severity index.",
         documentation="A standardized precipitation anomaly (poor-man's SPI): current-period rainfall compared to the mean and spread of the same calendar window over a 2015-2019 baseline.",
         applications="Drought early-warning, agricultural risk assessment, water scarcity planning",
         supported_dataset="CHIRPS", default_resolution="~5 km",
         min_value=-3, max_value=3, color_palette='["#a50026","#ffffbf","#313695"]'),
    dict(name="Évapotranspiration", category=IndicatorCategory.CLIMATE, unit="mm", color="#0891b2", icon="💨",
         formula="sum(MOD16A2 ET) * 0.1", description="Actual evapotranspiration over the period.",
         documentation="Total actual evapotranspiration accumulated over the selected period, from the MODIS MOD16A2 8-day ET product.",
         applications="Water balance modeling, irrigation demand estimation, drought impact assessment",
         supported_dataset="MODIS", default_resolution="500 m",
         min_value=0, max_value=500, color_palette='["#ffffcc","#41b6c4","#225ea8"]'),
    # Occupation du Sol
    dict(name="Land Cover", category=IndicatorCategory.LAND_COVER, unit="class", color="#8b5cf6", icon="🗺️",
         formula="ESA WorldCover v200 classification", description="Dominant land cover classification.",
         documentation="11-class global land cover map at 10m resolution from ESA WorldCover (2021 snapshot): tree cover, shrubland, grassland, cropland, built-up, bare/sparse vegetation, snow/ice, water, wetland, mangroves, moss/lichen.",
         applications="Urban growth tracking, habitat mapping, land use planning",
         supported_dataset="ESA WorldCover", default_resolution="10 m",
         min_value=10, max_value=100, color_palette='["#006400","#ffbb22","#ffff4c","#f096ff","#fa0000","#b4b4b4","#f0f0f0","#0064c8","#0096a0","#00cf75","#fae6a0"]'),
    dict(name="Changement d'occupation du sol", category=IndicatorCategory.LAND_COVER, unit="%", color="#7c3aed", icon="🏗️",
         formula="% pixels where mode(label, period A) ≠ mode(label, period B)", description="Land cover change between two periods.",
         documentation="Percentage of the AOI where the dominant Dynamic World land cover class differs between the first and second half of the selected date range.",
         applications="Deforestation tracking, urban expansion, wetland loss detection",
         supported_dataset="Google Dynamic World", default_resolution="10 m",
         min_value=0, max_value=100, color_palette='["#ffffcc","#fd8d3c","#800026"]'),
    # Population
    dict(name="Densité de population", category=IndicatorCategory.POPULATION, unit="hab/km²", color="#ec4899", icon="🏙️",
         formula="WorldPop population / pixel area", description="Gridded population density.",
         documentation="Population count per pixel from WorldPop, normalized to inhabitants per square kilometer.",
         applications="Urban planning, service coverage analysis, disaster risk exposure",
         supported_dataset="WorldPop", default_resolution="100 m",
         min_value=0, max_value=2000, color_palette='["#ffffb2","#fd8d3c","#bd0026"]'),
    dict(name="Répartition spatiale", category=IndicatorCategory.POPULATION, unit="hab", color="#db2777", icon="👥",
         formula="WorldPop population (raw per-pixel headcount)", description="Spatial distribution of population counts.",
         documentation="Raw per-pixel population headcount from WorldPop, showing where people are concentrated within the AOI.",
         applications="Resource allocation, evacuation planning, service accessibility",
         supported_dataset="WorldPop", default_resolution="100 m",
         min_value=0, max_value=50, color_palette='["#ffffb2","#fd8d3c","#bd0026"]'),
    # Dégradation des Terres
    dict(name="Dégradation", category=IndicatorCategory.DEGRADATION, unit="NDVI/year", color="#b45309", icon="📉",
         formula="linearFit(year, NDVI) slope, last 5 years", description="Land degradation index.",
         documentation="Slope of a linear fit between year and Sentinel-2 NDVI over the last 5 years. A negative slope indicates declining vegetation vigor (potential degradation).",
         applications="Desertification monitoring, rangeland management, land degradation neutrality tracking",
         supported_dataset="Sentinel-2", default_resolution="30 m",
         min_value=-0.05, max_value=0.05, color_palette='["#a50026","#ffffbf","#1a9850"]'),
    dict(name="Restauration", category=IndicatorCategory.DEGRADATION, unit="NDVI/year", color="#92400e", icon="🌾",
         formula="linearFit(year, NDVI) slope, last 5 years", description="Land restoration progress index.",
         documentation="Same NDVI trend computation as Dégradation — a positive slope here indicates vegetation recovery (potential restoration progress).",
         applications="Restoration project monitoring, reforestation impact assessment",
         supported_dataset="Sentinel-2", default_resolution="30 m",
         min_value=-0.05, max_value=0.05, color_palette='["#a50026","#ffffbf","#1a9850"]'),
    dict(name="Zones critiques", category=IndicatorCategory.DEGRADATION, unit="%", color="#78350f", icon="⚠️",
         formula="% area where NDVI trend slope < -0.01/year", description="Areas flagged as critically degraded.",
         documentation="Percentage of the AOI where the 5-year NDVI trend slope falls below a critical degradation threshold (-0.01/year).",
         applications="Priority area targeting for land restoration, degradation hotspot mapping",
         supported_dataset="Sentinel-2", default_resolution="30 m",
         min_value=0, max_value=100, color_palette='["#ffffcc","#fd8d3c","#800026"]'),
    # Risques
    dict(name="Vulnérabilité", category=IndicatorCategory.RISK, unit="index", color="#e11d48", icon="🚨",
         formula="Not implemented — requires a defined composite methodology", description="Vulnerability to environmental hazards.",
         documentation="No standard, globally-applicable formula is encoded for this indicator yet — it requires defining a weighted composite of factors (e.g. slope, land cover, population, infrastructure). Running it will fail with a clear message rather than return a fabricated score.",
         applications="Disaster risk reduction, climate adaptation planning",
         supported_dataset="Not yet supported", default_resolution="—",
         min_value=None, max_value=None, color_palette=None),
    dict(name="Exposition", category=IndicatorCategory.RISK, unit="index", color="#be123c", icon="📡",
         formula="Not implemented — requires a defined hazard layer", description="Exposure to identified hazards.",
         documentation="No standard, globally-applicable formula is encoded for this indicator yet — it requires a defined hazard layer (flood, drought, etc.) to overlay against population/assets. Running it will fail with a clear message rather than return a fabricated score.",
         applications="Disaster risk reduction, insurance/asset risk screening",
         supported_dataset="Not yet supported", default_resolution="—",
         min_value=None, max_value=None, color_palette=None),
    dict(name="Sensibilité", category=IndicatorCategory.RISK, unit="index", color="#9f1239", icon="🎯",
         formula="Not implemented — requires a defined sensitivity model", description="Sensitivity of the AOI to the hazard.",
         documentation="No standard, globally-applicable formula is encoded for this indicator yet — it requires a defined sensitivity model specific to the hazard and sector of interest. Running it will fail with a clear message rather than return a fabricated score.",
         applications="Climate vulnerability assessments, adaptation prioritization",
         supported_dataset="Not yet supported", default_resolution="—",
         min_value=None, max_value=None, color_palette=None),
]


def seed_catalog(db: Session) -> None:
    existing_dataset_names = {name for (name,) in db.query(Dataset.name).all()}
    new_datasets = [d for d in DATASETS if d["name"] not in existing_dataset_names]
    if new_datasets:
        db.bulk_insert_mappings(Dataset, new_datasets)

    existing_indicators = {row.name: row for row in db.query(Indicator).all()}
    for indicator_data in INDICATORS:
        existing = existing_indicators.get(indicator_data["name"])
        if existing is None:
            db.add(Indicator(**indicator_data))
        else:
            for key, value in indicator_data.items():
                setattr(existing, key, value)

    if db.query(AppSettings).count() == 0:
        db.add(AppSettings())

    db.commit()
