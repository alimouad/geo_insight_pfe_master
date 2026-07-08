import ee
from fastapi import APIRouter, Depends, HTTPException
from shapely.geometry import MultiPolygon, Polygon, mapping, shape

from app.api.endpoints.users import get_current_user
from app.models.user import User

router = APIRouter()

# Kept small and explicit per the spec's examples rather than listing every
# country in FAO/GAUL — this is a demo catalogue, not a full gazetteer.
COUNTRIES = ["Morocco", "Mauritania", "Mongolia", "Senegal"]

GAUL_LEVEL0 = "FAO/GAUL/2015/level0"
GAUL_LEVEL1 = "FAO/GAUL/2015/level1"


@router.get("/countries")
def list_countries(current_user: User = Depends(get_current_user)):
    return COUNTRIES


@router.get("/{country}/regions")
def list_regions(country: str, current_user: User = Depends(get_current_user)):
    if country not in COUNTRIES:
        raise HTTPException(status_code=404, detail="Unknown country.")

    fc = ee.FeatureCollection(GAUL_LEVEL1).filter(ee.Filter.eq("ADM0_NAME", country))
    names = fc.aggregate_array("ADM1_NAME").distinct().sort().getInfo()
    return names


@router.get("/geometry")
def get_region_geometry(country: str, region: str | None = None, current_user: User = Depends(get_current_user)):
    if country not in COUNTRIES:
        raise HTTPException(status_code=404, detail="Unknown country.")

    if region:
        feature = ee.FeatureCollection(GAUL_LEVEL1).filter(
            ee.Filter.And(ee.Filter.eq("ADM0_NAME", country), ee.Filter.eq("ADM1_NAME", region))
        ).first()
    else:
        feature = ee.FeatureCollection(GAUL_LEVEL0).filter(ee.Filter.eq("ADM0_NAME", country)).first()

    geometry = feature.geometry().simplify(300)
    info = geometry.getInfo()
    area_ha = geometry.area(1).divide(10_000).getInfo()

    shapely_geom = shape(info)
    if shapely_geom.geom_type == "GeometryCollection":
        # Simplification can degenerate slivers/exclaves into stray points or
        # lines — keep only the actual polygon parts.
        polygons = [g for g in shapely_geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
        shapely_geom = polygons[0] if len(polygons) == 1 else MultiPolygon(
            [p for g in polygons for p in (g.geoms if isinstance(g, MultiPolygon) else [g])]
        )

    return {"geometry": mapping(shapely_geom), "area": round(area_ha, 2)}
