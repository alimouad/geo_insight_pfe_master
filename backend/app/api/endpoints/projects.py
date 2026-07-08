import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import geopandas as gpd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from shapely.geometry import MultiPolygon, Polygon, mapping
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_user
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectResponse, ProjectStatus
from app.projects.schemas import AoiPayload, ProjectCreateRequest, ProjectUpdateRequest

router = APIRouter()


def _to_response(project: Project) -> dict:
    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "geometry": project.geometry,
        "area": project.area,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return [_to_response(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        geometry=json.dumps(payload.geometry) if payload.geometry else None,
        area=payload.area,
        status=payload.status or ProjectStatus.RUNNING,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = _get_owned_project(project_id, db, current_user)
    return _to_response(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(project_id, db, current_user)

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.geometry is not None:
        project.geometry = json.dumps(payload.geometry)
    if payload.area is not None:
        project.area = payload.area
    if payload.status is not None:
        project.status = payload.status

    db.commit()
    db.refresh(project)
    return _to_response(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = _get_owned_project(project_id, db, current_user)
    db.delete(project)
    db.commit()


@router.post("/aoi/shapefile", response_model=AoiPayload)
async def parse_shapefile(file: UploadFile, current_user: User = Depends(get_current_user)):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip archive containing the shapefile (.shp, .shx, .dbf, .prj).")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        zip_path = tmp_path / "aoi.zip"

        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(tmp_path)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="The uploaded file is not a valid .zip archive.")

        shp_files = list(tmp_path.rglob("*.shp"))
        if not shp_files:
            raise HTTPException(status_code=400, detail="No .shp file found inside the archive.")

        try:
            gdf = gpd.read_file(shp_files[0])
        except Exception:
            raise HTTPException(status_code=400, detail="Unable to read the shapefile. Make sure .shp, .shx, and .dbf are all included.")

        if gdf.empty:
            raise HTTPException(status_code=400, detail="The shapefile does not contain any geometry.")

        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=4326)

        geometry = gdf.geometry.union_all() if hasattr(gdf.geometry, "union_all") else gdf.geometry.unary_union

        area_gdf = gpd.GeoDataFrame(geometry=[geometry], crs=gdf.crs)
        area_ha = area_gdf.to_crs(area_gdf.estimate_utm_crs()).area.iloc[0] / 10_000

        geometry_wgs84 = gpd.GeoSeries([geometry], crs=gdf.crs).to_crs(epsg=4326).iloc[0]

        return AoiPayload(geometry=json.loads(gpd.GeoSeries([geometry_wgs84]).to_json())["features"][0]["geometry"], area=round(area_ha, 2))


@router.post("/aoi/kml", response_model=AoiPayload)
async def parse_kml(file: UploadFile, current_user: User = Depends(get_current_user)):
    if not file.filename.lower().endswith(".kml"):
        raise HTTPException(status_code=400, detail="Please upload a .kml file.")

    raw = await file.read()
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError:
        raise HTTPException(status_code=400, detail="Invalid KML (not well-formed XML).")

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    coords_elements = root.findall(".//kml:Polygon//kml:coordinates", ns) or root.findall(".//Polygon//coordinates")
    if not coords_elements:
        raise HTTPException(status_code=400, detail="No <Polygon> found in this KML file.")

    def parse_ring(text: str) -> list[list[float]]:
        points = []
        for triplet in text.strip().split():
            parts = triplet.split(",")
            lng, lat = float(parts[0]), float(parts[1])
            points.append([lng, lat])
        return points

    polygons = [Polygon(parse_ring(el.text)) for el in coords_elements if el.text and el.text.strip()]
    if not polygons:
        raise HTTPException(status_code=400, detail="Could not parse any polygon coordinates from this KML file.")

    geometry = polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)

    gdf = gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:4326")
    area_ha = gdf.to_crs(gdf.estimate_utm_crs()).area.iloc[0] / 10_000

    return AoiPayload(geometry=mapping(geometry), area=round(area_ha, 2))


def _get_owned_project(project_id: int, db: Session, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project
