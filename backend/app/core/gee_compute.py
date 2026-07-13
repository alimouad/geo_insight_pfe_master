import math
from datetime import datetime

import ee

from app.models.dataset import DatasetProvider

# ============================================================================
# Generic optical/climate index pipeline (NDVI, EVI, SAVI, NDWI, LST, Rainfall)
# (provider, indicator name) -> band expression builder taking a composite
# ee.Image (already reflectance-scaled to 0-1 for optical sensors) and
# returning a single-band ee.Image named "value".
# ============================================================================


def _sentinel2_scaled(img):
    optical = img.select("B.*").multiply(0.0001)
    return img.addBands(optical, overwrite=True)


def _sentinel2_ndvi(img):
    return img.normalizedDifference(["B8", "B4"]).rename("value")


def _sentinel2_ndwi(img):
    return img.normalizedDifference(["B3", "B8"]).rename("value")


def _sentinel2_evi(img):
    img = _sentinel2_scaled(img)
    return img.expression(
        "2.5 * (NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)",
        {"NIR": img.select("B8"), "RED": img.select("B4"), "BLUE": img.select("B2")},
    ).rename("value")


def _sentinel2_savi(img):
    img = _sentinel2_scaled(img)
    return img.expression(
        "((NIR - RED) / (NIR + RED + 0.5)) * 1.5",
        {"NIR": img.select("B8"), "RED": img.select("B4")},
    ).rename("value")


def _landsat8_scaled(img):
    optical = img.select("SR_B.").multiply(0.0000275).add(-0.2)
    return img.addBands(optical, overwrite=True)


def _landsat8_ndvi(img):
    img = _landsat8_scaled(img)
    return img.normalizedDifference(["SR_B5", "SR_B4"]).rename("value")


def _landsat8_ndwi(img):
    img = _landsat8_scaled(img)
    return img.normalizedDifference(["SR_B3", "SR_B5"]).rename("value")


def _landsat8_evi(img):
    img = _landsat8_scaled(img)
    return img.expression(
        "2.5 * (NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)",
        {"NIR": img.select("SR_B5"), "RED": img.select("SR_B4"), "BLUE": img.select("SR_B2")},
    ).rename("value")


def _landsat8_savi(img):
    img = _landsat8_scaled(img)
    return img.expression(
        "((NIR - RED) / (NIR + RED + 0.5)) * 1.5",
        {"NIR": img.select("SR_B5"), "RED": img.select("SR_B4")},
    ).rename("value")


def _modis_lst(img):
    return img.select("LST_Day_1km").multiply(0.02).add(-273.15).rename("value")


def _chirps_rainfall(img):
    return img.select("precipitation").rename("value")


BUILDERS = {
    (DatasetProvider.SENTINEL_2, "NDVI"): _sentinel2_ndvi,
    (DatasetProvider.SENTINEL_2, "NDWI"): _sentinel2_ndwi,
    (DatasetProvider.SENTINEL_2, "EVI"): _sentinel2_evi,
    (DatasetProvider.SENTINEL_2, "SAVI"): _sentinel2_savi,
    (DatasetProvider.LANDSAT_8, "NDVI"): _landsat8_ndvi,
    (DatasetProvider.LANDSAT_8, "NDWI"): _landsat8_ndwi,
    (DatasetProvider.LANDSAT_8, "EVI"): _landsat8_evi,
    (DatasetProvider.LANDSAT_8, "SAVI"): _landsat8_savi,
    (DatasetProvider.MODIS, "Land Surface Temperature (Température de surface)"): _modis_lst,
    (DatasetProvider.CHIRPS, "Precipitation (Précipitations)"): _chirps_rainfall,
}

VIS_PALETTES = {
    "NDVI": {"min": -0.2, "max": 0.9, "palette": ["#a50026", "#fee08b", "#66bd63", "#1a9850"]},
    "EVI": {"min": -0.2, "max": 0.9, "palette": ["#a50026", "#fee08b", "#66bd63", "#1a9850"]},
    "SAVI": {"min": -0.2, "max": 0.9, "palette": ["#a50026", "#fee08b", "#66bd63", "#1a9850"]},
    "NDWI": {"min": -0.5, "max": 0.6, "palette": ["#f7fbff", "#6baed6", "#08306b"]},
    "Land Surface Temperature (Température de surface)": {"min": 0, "max": 45, "palette": ["#313695", "#fee090", "#a50026"]},
    "Precipitation (Précipitations)": {"min": 0, "max": 200, "palette": ["#ffffcc", "#41b6c4", "#225ea8"]},
    "Vegetation Biomass (Biomasse végétale)": {"min": 0, "max": 100, "palette": ["#ffffcc", "#78c679", "#004529"]},
    "Soil Moisture (Humidité des sols)": {"min": 0, "max": 50, "palette": ["#f6e8c3", "#5ab4ac", "#01665e"]},
    "Water Availability (Disponibilité en eau)": {"min": 0, "max": 100, "palette": ["#f7fbff", "#6baed6", "#08306b"]},
    "Thermal Anomalies (Anomalies thermiques)": {"min": -5, "max": 5, "palette": ["#2166ac", "#f7f7f7", "#b2182b"]},
    "Drought Index (Sécheresse)": {"min": -3, "max": 3, "palette": ["#a50026", "#ffffbf", "#313695"]},
    "Evapotranspiration (Évapotranspiration)": {"min": 0, "max": 500, "palette": ["#ffffcc", "#41b6c4", "#225ea8"]},
    "Land Cover": {"min": 10, "max": 100, "palette": ["#006400", "#ffbb22", "#ffff4c", "#f096ff", "#fa0000", "#b4b4b4", "#f0f0f0", "#0064c8", "#0096a0", "#00cf75", "#fae6a0"]},
    "Land Cover Change (Changement d'occupation du sol)": {"min": 0, "max": 100, "palette": ["#ffffcc", "#fd8d3c", "#800026"]},
    "Population Density (Densité de population)": {"min": 0, "max": 2000, "palette": ["#ffffb2", "#fd8d3c", "#bd0026"]},
    "Population Distribution (Répartition spatiale)": {"min": 0, "max": 50, "palette": ["#ffffb2", "#fd8d3c", "#bd0026"]},
    "Land Degradation (Dégradation)": {"min": -0.05, "max": 0.05, "palette": ["#a50026", "#ffffbf", "#1a9850"]},
    "Land Restoration (Restauration)": {"min": -0.05, "max": 0.05, "palette": ["#a50026", "#ffffbf", "#1a9850"]},
    "Critical Zones (Zones critiques)": {"min": 0, "max": 100, "palette": ["#ffffcc", "#fd8d3c", "#800026"]},
}

DEFAULT_VIS = {"min": -1, "max": 1, "palette": ["#440154", "#21908c", "#fde725"]}

HISTOGRAM_BUCKETS = 10
MAX_TIMESERIES_POINTS = 12
BASELINE_YEARS = list(range(2015, 2020))  # fixed reference period for anomaly/trend indicators


class UnsupportedIndicatorError(Exception):
    pass


class NoImageryError(Exception):
    pass


# ============================================================================
# Shared helpers
# ============================================================================


def _stats(value_image, geometry, scale):
    reducer = (
        ee.Reducer.mean()
        .combine(ee.Reducer.minMax(), sharedInputs=True)
        .combine(ee.Reducer.stdDev(), sharedInputs=True)
        .combine(ee.Reducer.median(), sharedInputs=True)
    )
    result = value_image.reduceRegion(
        reducer=reducer, geometry=geometry, scale=scale, maxPixels=1_000_000_000, bestEffort=True, tileScale=8
    ).getInfo()
    return {
        "min": result.get("value_min"),
        "max": result.get("value_max"),
        "mean": result.get("value_mean"),
        "median": result.get("value_median"),
        "stdDev": result.get("value_stdDev"),
    }


def _histogram(value_image, geometry, scale, vis_params):
    raw = value_image.reduceRegion(
        reducer=ee.Reducer.fixedHistogram(vis_params["min"], vis_params["max"], HISTOGRAM_BUCKETS),
        geometry=geometry,
        scale=scale,
        maxPixels=1_000_000_000,
        bestEffort=True,
        tileScale=8,
    ).getInfo()
    rows = raw.get("value") or []
    return [{"bucketStart": row[0], "count": row[1]} for row in rows]


def _tile_and_png(value_image, vis_params, geometry):
    map_id = value_image.getMapId(vis_params)
    tile_url = map_id["tile_fetcher"].url_format
    png_url = value_image.getThumbURL({**vis_params, "region": geometry, "dimensions": 512, "format": "png"})
    return tile_url, png_url


def _assemble(value_image, geometry, scale, vis_params, timeseries):
    tile_url, png_url = _tile_and_png(value_image, vis_params, geometry)
    return {
        "stats": _stats(value_image, geometry, scale),
        "histogram": _histogram(value_image, geometry, scale, vis_params),
        "timeseries": timeseries,
        "tile_url": tile_url,
        "png_url": png_url,
    }


def _time_buckets(start_date: str, end_date: str):
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    total_days = max((end_dt - start_dt).days, 1)
    n_buckets = min(MAX_TIMESERIES_POINTS, total_days)
    interval_days = max(1, total_days // n_buckets)
    return n_buckets, interval_days


def _timeseries_generic(collection, build_fn, geometry, scale, start_date, end_date, agg="mean"):
    """build_fn(sub_collection) -> ee.Image named 'value'. agg picks the per-bucket reducer."""
    n_buckets, interval_days = _time_buckets(start_date, end_date)
    start = ee.Date(start_date)
    reducer = ee.Reducer.sum() if agg == "sum" else ee.Reducer.mean()

    def bucket_value(i):
        b_start = start.advance(ee.Number(i).multiply(interval_days), "day")
        b_end = b_start.advance(interval_days, "day")
        bucket_collection = collection.filterDate(b_start, b_end)

        def compute_value():
            value_image = build_fn(bucket_collection)
            result = value_image.reduceRegion(
                reducer=reducer, geometry=geometry, scale=scale, bestEffort=True, maxPixels=1_000_000_000, tileScale=8
            )
            return result.get("value")

        value = ee.Algorithms.If(bucket_collection.size().gt(0), compute_value(), None)
        return ee.Feature(None, {"date": b_start.format("YYYY-MM-dd"), "value": value})

    buckets = ee.List.sequence(0, n_buckets - 1)
    features = ee.FeatureCollection(buckets.map(bucket_value)).getInfo()["features"]
    return [
        {"date": f["properties"]["date"], "value": f["properties"]["value"]}
        for f in features
        if f["properties"].get("value") is not None
    ]


def _composite(collection, indicator_name, builder):
    if indicator_name == "Precipitation (Précipitations)":
        return collection.select("precipitation").sum().rename("value")
    return builder(collection.median())


def _require_imagery(collection):
    if collection.size().getInfo() == 0:
        raise NoImageryError(
            "No images found for this AOI, date range, and cloud cover setting. "
            "Try widening the date range, relaxing the cloud cover filter, or checking the AOI location."
        )


def _generic_pipeline(provider, gee_collection, indicator_name, builder, geometry, start_date, end_date, scale, cloud_percentage):
    collection = ee.ImageCollection(gee_collection).filterBounds(geometry).filterDate(start_date, end_date)
    if provider == DatasetProvider.SENTINEL_2 and cloud_percentage is not None:
        collection = collection.filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", cloud_percentage))

    _require_imagery(collection)

    value_image = _composite(collection, indicator_name, builder)
    vis_params = VIS_PALETTES.get(indicator_name, DEFAULT_VIS)
    agg = "sum" if indicator_name == "Precipitation (Précipitations)" else "mean"
    timeseries = _timeseries_generic(
        collection, lambda c: _composite(c, indicator_name, builder), geometry, scale, start_date, end_date, agg=agg
    )
    return value_image, vis_params, timeseries


# ============================================================================
# Special indicators — each uses a fixed, appropriate GEE dataset regardless
# of the "Dataset" the user picked in the form (e.g. Land Cover always reads
# ESA WorldCover, not whichever optical dataset was selected).
# ============================================================================


def _population_indicator(indicator_name, geometry, start_date, end_date, scale):
    # WorldPop ships one raster per country per year (e.g. "MAR_2020"), not a
    # single global mosaic — filterBounds can also match neighboring
    # countries' footprints, so we must mosaic same-year images rather than
    # pick an arbitrary "first" one (which can leave the AOI fully masked).
    all_years = ee.ImageCollection("WorldPop/GP/100m/pop").filterBounds(geometry)
    _require_imagery(all_years)

    not_after_end = all_years.filter(ee.Filter.lte("system:time_start", ee.Date(end_date).millis()))
    reference_collection = ee.ImageCollection(
        ee.Algorithms.If(not_after_end.size().gt(0), not_after_end.sort("system:time_start", False), all_years.sort("system:time_start", True))
    )
    latest_year = ee.Date(reference_collection.first().get("system:time_start")).get("year")

    collection = all_years.filter(ee.Filter.calendarRange(latest_year, latest_year, "year"))
    pop = collection.select("population").mosaic()

    if indicator_name == "Population Density (Densité de population)":
        value_image = pop.divide(ee.Image.pixelArea()).multiply(1_000_000).rename("value")
    else:  # Population Distribution (Répartition spatiale) — raw per-pixel headcount
        value_image = pop.rename("value")

    vis_params = VIS_PALETTES[indicator_name]
    return value_image, vis_params, []


def _soil_moisture(geometry, start_date, end_date, scale):
    # SMAP L4 is 3-hourly (~2920 images/year) — sampling one reading per day
    # (same hour) keeps the mean representative without blowing the memory
    # budget of compositing thousands of global 9km grids.
    collection = (
        ee.ImageCollection("NASA/SMAP/SPL4SMGP/008")
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.calendarRange(13, 13, "hour"))
    )
    _require_imagery(collection)
    value_image = collection.select("sm_surface").mean().multiply(100).rename("value")
    vis_params = VIS_PALETTES["Soil Moisture (Humidité des sols)"]
    timeseries = _timeseries_generic(
        collection, lambda c: c.select("sm_surface").mean().multiply(100).rename("value"), geometry, scale, start_date, end_date
    )
    return value_image, vis_params, timeseries


def _water_availability(geometry, scale):
    value_image = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").rename("value")
    vis_params = VIS_PALETTES["Water Availability (Disponibilité en eau)"]
    return value_image, vis_params, []


def _thermal_anomaly(geometry, start_date, end_date, scale):
    current_collection = ee.ImageCollection("MODIS/061/MOD11A1").filterBounds(geometry).filterDate(start_date, end_date)
    _require_imagery(current_collection)
    current = current_collection.select("LST_Day_1km").mean().multiply(0.02).add(-273.15)

    start_doy = ee.Date(start_date).getRelative("day", "year")
    end_doy = ee.Date(end_date).getRelative("day", "year")
    baseline_collection = (
        ee.ImageCollection("MODIS/061/MOD11A1")
        .filterBounds(geometry)
        .filter(ee.Filter.calendarRange(2015, 2019, "year"))
        .filter(ee.Filter.dayOfYear(start_doy, end_doy))
    )
    baseline = baseline_collection.select("LST_Day_1km").mean().multiply(0.02).add(-273.15)

    value_image = current.subtract(baseline).rename("value")
    vis_params = VIS_PALETTES["Thermal Anomalies (Anomalies thermiques)"]
    return value_image, vis_params, []


def _drought(geometry, start_date, end_date, scale):
    current_collection = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterBounds(geometry).filterDate(start_date, end_date)
    _require_imagery(current_collection)
    current_sum = current_collection.select("precipitation").sum()

    start_doy = ee.Date(start_date).getRelative("day", "year")
    end_doy = ee.Date(end_date).getRelative("day", "year")

    def year_sum(y):
        y = ee.Number(y)
        yearly = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterBounds(geometry)
            .filter(ee.Filter.calendarRange(y, y, "year"))
            .filter(ee.Filter.dayOfYear(start_doy, end_doy))
        )
        return yearly.select("precipitation").sum().set("year", y)

    baseline_years_collection = ee.ImageCollection(ee.List(BASELINE_YEARS).map(year_sum))
    baseline_mean = baseline_years_collection.reduce(ee.Reducer.mean())
    baseline_std = baseline_years_collection.reduce(ee.Reducer.stdDev())

    value_image = current_sum.subtract(baseline_mean).divide(baseline_std.max(1)).rename("value")
    vis_params = VIS_PALETTES["Drought Index (Sécheresse)"]
    return value_image, vis_params, []


def _evapotranspiration(geometry, start_date, end_date, scale):
    collection = ee.ImageCollection("MODIS/061/MOD16A2").filterBounds(geometry).filterDate(start_date, end_date)
    _require_imagery(collection)
    value_image = collection.select("ET").sum().multiply(0.1).rename("value")
    vis_params = VIS_PALETTES["Evapotranspiration (Évapotranspiration)"]
    timeseries = _timeseries_generic(
        collection, lambda c: c.select("ET").sum().multiply(0.1).rename("value"), geometry, scale, start_date, end_date, agg="sum"
    )
    return value_image, vis_params, timeseries


def _land_cover(geometry, scale):
    value_image = ee.ImageCollection("ESA/WorldCover/v200").first().select("Map").rename("value")
    vis_params = VIS_PALETTES["Land Cover"]
    return value_image, vis_params, []


def _land_cover_change(geometry, start_date, end_date, scale):
    start = ee.Date(start_date)
    end = ee.Date(end_date)
    midpoint = start.advance(end.difference(start, "day").divide(2), "day")

    period_a = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterBounds(geometry).filterDate(start, midpoint)
    period_b = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterBounds(geometry).filterDate(midpoint, end)
    _require_imagery(period_a)
    _require_imagery(period_b)

    label_a = period_a.select("label").mode()
    label_b = period_b.select("label").mode()
    value_image = label_a.neq(label_b).multiply(100).rename("value")

    vis_params = VIS_PALETTES["Land Cover Change (Changement d'occupation du sol)"]
    return value_image, vis_params, []


def _ndvi_yearly_collection(geometry, end_date):
    end_year = ee.Date(end_date).get("year")
    years = ee.List.sequence(ee.Number(end_year).subtract(5), ee.Number(end_year))

    def year_ndvi(y):
        y = ee.Number(y)
        yearly = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(geometry)
            .filter(ee.Filter.calendarRange(y, y, "year"))
            .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", 40))
        )
        ndvi = yearly.median().normalizedDifference(["B8", "B4"]).rename("ndvi")
        year_band = ee.Image.constant(y).toFloat().rename("year")
        return year_band.addBands(ndvi).set("year", y, "count", yearly.size())

    return ee.ImageCollection(years.map(year_ndvi)), years


def _ndvi_trend(geometry, end_date, scale):
    yearly_collection, years = _ndvi_yearly_collection(geometry, end_date)
    valid_years = yearly_collection.filter(ee.Filter.gt("count", 0))

    fit = valid_years.select(["year", "ndvi"]).reduce(ee.Reducer.linearFit())
    slope = fit.select("scale").rename("value")
    return slope, valid_years


def _degradation_or_restoration(geometry, end_date, scale):
    slope, _ = _ndvi_trend(geometry, end_date, scale)
    vis_params = VIS_PALETTES["Land Degradation (Dégradation)"]
    return slope, vis_params, []


def _critical_zones(geometry, end_date, scale):
    slope, _ = _ndvi_trend(geometry, end_date, scale)
    value_image = slope.lt(-0.01).multiply(100).rename("value")
    vis_params = VIS_PALETTES["Critical Zones (Zones critiques)"]
    return value_image, vis_params, []


def _biomass_proxy(provider, gee_collection, geometry, start_date, end_date, scale, cloud_percentage):
    collection = ee.ImageCollection(gee_collection).filterBounds(geometry).filterDate(start_date, end_date)
    if provider == DatasetProvider.SENTINEL_2 and cloud_percentage is not None:
        collection = collection.filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", cloud_percentage))
    _require_imagery(collection)

    builder = _sentinel2_ndvi if provider == DatasetProvider.SENTINEL_2 else _landsat8_ndvi
    ndvi = builder(collection.median())
    # Illustrative proxy only (AGB ~ 100 * NDVI^2) — not a calibrated biomass model.
    value_image = ndvi.pow(2).multiply(100).rename("value")
    vis_params = VIS_PALETTES["Vegetation Biomass (Biomasse végétale)"]
    timeseries = _timeseries_generic(collection, lambda c: builder(c.median()).pow(2).multiply(100).rename("value"), geometry, scale, start_date, end_date)
    return value_image, vis_params, timeseries


SPECIAL_INDICATORS = {
    "Population Density (Densité de population)",
    "Population Distribution (Répartition spatiale)",
    "Soil Moisture (Humidité des sols)",
    "Water Availability (Disponibilité en eau)",
    "Thermal Anomalies (Anomalies thermiques)",
    "Drought Index (Sécheresse)",
    "Evapotranspiration (Évapotranspiration)",
    "Land Cover",
    "Land Cover Change (Changement d'occupation du sol)",
    "Land Degradation (Dégradation)",
    "Land Restoration (Restauration)",
    "Critical Zones (Zones critiques)",
    "Vegetation Biomass (Biomasse végétale)",
}


def _compute_special(indicator_name, provider, gee_collection, geometry, start_date, end_date, scale, cloud_percentage):
    if indicator_name in ("Population Density (Densité de population)", "Population Distribution (Répartition spatiale)"):
        return _population_indicator(indicator_name, geometry, start_date, end_date, scale)
    if indicator_name == "Soil Moisture (Humidité des sols)":
        return _soil_moisture(geometry, start_date, end_date, scale)
    if indicator_name == "Water Availability (Disponibilité en eau)":
        return _water_availability(geometry, scale)
    if indicator_name == "Thermal Anomalies (Anomalies thermiques)":
        return _thermal_anomaly(geometry, start_date, end_date, scale)
    if indicator_name == "Drought Index (Sécheresse)":
        return _drought(geometry, start_date, end_date, scale)
    if indicator_name == "Evapotranspiration (Évapotranspiration)":
        return _evapotranspiration(geometry, start_date, end_date, scale)
    if indicator_name == "Land Cover":
        return _land_cover(geometry, scale)
    if indicator_name == "Land Cover Change (Changement d'occupation du sol)":
        return _land_cover_change(geometry, start_date, end_date, scale)
    if indicator_name in ("Land Degradation (Dégradation)", "Land Restoration (Restauration)"):
        return _degradation_or_restoration(geometry, end_date, scale)
    if indicator_name == "Critical Zones (Zones critiques)":
        return _critical_zones(geometry, end_date, scale)
    if indicator_name == "Vegetation Biomass (Biomasse végétale)":
        return _biomass_proxy(provider, gee_collection, geometry, start_date, end_date, scale, cloud_percentage)
    raise UnsupportedIndicatorError(f"No handler registered for {indicator_name}.")


def _dispatch(provider, gee_collection, indicator_name, aoi_geojson, start_date, end_date, scale, cloud_percentage):
    """Returns (value_image, vis_params, timeseries) without assembling stats/histogram/tiles."""
    geometry = ee.Geometry(aoi_geojson)

    if indicator_name in SPECIAL_INDICATORS:
        return _compute_special(indicator_name, provider, gee_collection, geometry, start_date, end_date, scale, cloud_percentage), geometry

    builder = BUILDERS.get((provider, indicator_name))
    if builder is None:
        raise UnsupportedIndicatorError(
            f"Real GEE computation is not implemented yet for {indicator_name} on {provider.value}."
        )

    return _generic_pipeline(provider, gee_collection, indicator_name, builder, geometry, start_date, end_date, scale, cloud_percentage), geometry


def compute_indicator(
    *,
    provider: DatasetProvider,
    gee_collection: str,
    indicator_name: str,
    aoi_geojson: dict,
    start_date: str,
    end_date: str,
    scale: int,
    cloud_percentage: float | None,
) -> dict:
    (value_image, vis_params, timeseries), geometry = _dispatch(
        provider, gee_collection, indicator_name, aoi_geojson, start_date, end_date, scale, cloud_percentage
    )
    return _assemble(value_image, geometry, scale, vis_params, timeseries)


def get_export_image(
    *,
    provider: DatasetProvider,
    gee_collection: str,
    indicator_name: str,
    aoi_geojson: dict,
    start_date: str,
    end_date: str,
    scale: int,
    cloud_percentage: float | None,
):
    """Rebuilds just the ee.Image (and its vis params) for on-demand export —
    skips stats/histogram/timeseries since exports only need the raster."""
    (value_image, vis_params, _), geometry = _dispatch(
        provider, gee_collection, indicator_name, aoi_geojson, start_date, end_date, scale, cloud_percentage
    )
    return value_image, vis_params, geometry


# ee.Image.getDownloadURL (synchronous, single-request download) hard-caps the
# response at 48 MiB — large AOIs at fine resolution routinely blow past this
# and fail with "Total request size (...) must be less than or equal to
# 50331648 bytes." Coarsening the scale just enough to fit keeps the export a
# single synchronous call instead of standing up an async Export.image task.
GEE_DOWNLOAD_BYTE_LIMIT = 50_331_648
BYTES_PER_PIXEL = 4  # single float32 "value" band


def safe_download_scale(geometry: "ee.Geometry", requested_scale: int) -> int:
    area_m2 = geometry.area(1).getInfo()
    if not area_m2:
        return requested_scale
    safe_budget = GEE_DOWNLOAD_BYTE_LIMIT * 0.85  # margin for GeoTIFF headers/tiling
    min_scale = (area_m2 * BYTES_PER_PIXEL / safe_budget) ** 0.5
    return max(requested_scale, math.ceil(min_scale))
