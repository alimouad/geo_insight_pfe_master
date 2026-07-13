import json
import math
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_user
from app.core.activity_log import log_action
from app.core.gee_compute import NoImageryError, UnsupportedIndicatorError, get_export_image, safe_download_scale
from app.database import get_db
from app.models.analysis import Analysis
from app.models.dataset import Dataset
from app.models.export import Export, ExportType
from app.models.indicator import Indicator
from app.models.project import Project
from app.models.user import User
from app.schemas.export import ExportCreate, ExportResponse

router = APIRouter()

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "exports_storage"
STORAGE_DIR.mkdir(exist_ok=True)

MIME_TYPES = {
    ExportType.GEOTIFF: "image/tiff",
    ExportType.PNG: "image/png",
    ExportType.CSV: "text/csv",
    ExportType.GEOJSON: "application/geo+json",
    ExportType.SHAPEFILE: "application/zip",
}

EXTENSIONS = {
    ExportType.GEOTIFF: "tif",
    ExportType.PNG: "png",
    ExportType.CSV: "csv",
    ExportType.GEOJSON: "geojson",
    ExportType.SHAPEFILE: "zip",
}


def _owned_analysis(analysis_id: int, db: Session, current_user: User) -> Analysis:
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return analysis


def _owned_export(export_id: int, db: Session, current_user: User) -> Export:
    export = (
        db.query(Export)
        .join(Analysis, Export.analysis_id == Analysis.id)
        .filter(Export.id == export_id, Analysis.user_id == current_user.id)
        .first()
    )
    if export is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found.")
    return export


_OVERSIZE_RE = re.compile(r"Total request size \((\d+) bytes\) must be less than or equal to (\d+) bytes")


def _get_geotiff_download_url(value_image, geometry, requested_scale: int, max_attempts: int = 4) -> str:
    """getDownloadURL is a single synchronous call capped at 48 MiB by Earth Engine.
    safe_download_scale() gives a good first estimate, but actual GeoTIFF byte size
    depends on internal encoding we can't predict exactly — so if GEE still rejects
    it, read the *actual* size it reports back and coarsen the scale proportionally."""
    scale = safe_download_scale(geometry, requested_scale)
    last_error = None
    for _ in range(max_attempts):
        try:
            return value_image.getDownloadURL({"region": geometry, "scale": scale, "format": "GEO_TIFF"})
        except Exception as error:
            match = _OVERSIZE_RE.search(str(error))
            if not match:
                raise
            actual_bytes, limit_bytes = int(match.group(1)), int(match.group(2))
            scale = math.ceil(scale * ((actual_bytes / (limit_bytes * 0.85)) ** 0.5))
            last_error = error
    raise last_error


def _generate_file(export_type: ExportType, analysis: Analysis, db: Session) -> tuple[Path, int]:
    aoi_geojson = mapping(to_shape(analysis.aoi))

    if export_type in (ExportType.GEOTIFF, ExportType.PNG):
        dataset = db.query(Dataset).filter(Dataset.id == analysis.dataset_id).first()
        indicator = db.query(Indicator).filter(Indicator.id == analysis.indicator_id).first()
        if dataset is None or indicator is None:
            raise UnsupportedIndicatorError("The dataset or indicator for this analysis is no longer available.")

        value_image, vis_params, geometry = get_export_image(
            provider=dataset.provider,
            gee_collection=dataset.gee_collection,
            indicator_name=indicator.name,
            aoi_geojson=aoi_geojson,
            start_date=analysis.start_date.date().isoformat(),
            end_date=analysis.end_date.date().isoformat(),
            scale=analysis.scale or 30,
            cloud_percentage=analysis.cloud_percentage,
        )

        if export_type == ExportType.GEOTIFF:
            url = _get_geotiff_download_url(value_image, geometry, analysis.scale or 30)
        else:
            url = value_image.getThumbURL({**vis_params, "region": geometry, "dimensions": 1024, "format": "png"})

        response = requests.get(url, timeout=120)
        response.raise_for_status()
        content = response.content

    elif export_type == ExportType.CSV:
        rows = [["metric", "value"]]
        for key, value in (analysis.stats or {}).items():
            if key in ("histogram", "timeseries"):
                continue
            rows.append([key, value])
        csv_text = "\n".join(",".join(str(cell) for cell in row) for row in rows)
        content = csv_text.encode("utf-8")

    elif export_type == ExportType.GEOJSON:
        content = json.dumps(aoi_geojson).encode("utf-8")

    elif export_type == ExportType.SHAPEFILE:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            gdf = gpd.GeoDataFrame(geometry=[to_shape(analysis.aoi)], crs="EPSG:4326")
            shp_path = tmp_path / "aoi.shp"
            gdf.to_file(shp_path)

            zip_path = tmp_path / "bundle.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                for part in tmp_path.glob("aoi.*"):
                    archive.write(part, part.name)
            content = zip_path.read_bytes()
    else:
        raise UnsupportedIndicatorError(f"Unsupported export type: {export_type}")

    return content


def _to_response(export: Export) -> Export:
    return export


def execute_export(export: Export, analysis: Analysis, db: Session, *, log_user_id: int | None) -> None:
    """Generates the export file for an already-persisted export row and updates it in place."""
    extension = EXTENSIONS.get(export.type, "bin")

    log_action(db, user_id=log_user_id, action="Export Started", details=export.file_name)

    try:
        content = _generate_file(export.type, analysis, db)
        disk_path = STORAGE_DIR / f"{export.id}.{extension}"
        disk_path.write_bytes(content)

        export.file_url = f"/api/exports/download/{export.id}"
        export.file_size = len(content)
        export.status = "Completed"
        export.error_message = None
    except (NoImageryError, UnsupportedIndicatorError) as error:
        export.status = "Failed"
        export.error_message = str(error)
    except Exception as error:
        export.status = "Failed"
        export.error_message = f"Export generation failed: {error}"

    export.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(export)

    if export.status == "Completed":
        log_action(db, user_id=log_user_id, action="Export Finished", details=export.file_name)
    else:
        log_action(db, user_id=log_user_id, action="Export Failed", details=f"{export.file_name}: {export.error_message}")


@router.post("", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
def create_export(payload: ExportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = _owned_analysis(payload.analysis_id, db, current_user)
    if analysis.status != "Completed":
        raise HTTPException(status_code=400, detail="Only completed analyses can be exported.")

    indicator = db.query(Indicator).filter(Indicator.id == analysis.indicator_id).first()
    base_name = (indicator.name if indicator else analysis.name).replace(" ", "_").replace("'", "")
    extension = EXTENSIONS[payload.type]
    file_name = f"{base_name}.{extension}"

    export = Export(
        analysis_id=analysis.id,
        type=payload.type,
        file_name=file_name,
        mime_type=MIME_TYPES[payload.type],
        status="Processing",
    )
    db.add(export)
    db.commit()
    db.refresh(export)

    execute_export(export, analysis, db, log_user_id=current_user.id)
    return export


@router.get("", response_model=list[ExportResponse])
def list_exports(
    project_id: int | None = None,
    analysis_id: int | None = None,
    type: ExportType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Export).join(Analysis, Export.analysis_id == Analysis.id).filter(Analysis.user_id == current_user.id)
    if project_id is not None:
        query = query.filter(Analysis.project_id == project_id)
    if analysis_id is not None:
        query = query.filter(Export.analysis_id == analysis_id)
    if type is not None:
        query = query.filter(Export.type == type)
    return query.order_by(Export.created_at.desc()).all()


@router.get("/{export_id}", response_model=ExportResponse)
def get_export(export_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _owned_export(export_id, db, current_user)


@router.delete("/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_export(export_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    export = _owned_export(export_id, db, current_user)
    extension = EXTENSIONS.get(export.type, "bin")
    disk_path = STORAGE_DIR / f"{export.id}.{extension}"
    disk_path.unlink(missing_ok=True)
    db.delete(export)
    db.commit()


@router.get("/download/{export_id}")
def download_export(export_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    export = _owned_export(export_id, db, current_user)
    if export.status != "Completed":
        raise HTTPException(status_code=400, detail="This export is not ready for download.")

    extension = EXTENSIONS.get(export.type, "bin")
    disk_path = STORAGE_DIR / f"{export.id}.{extension}"
    if not disk_path.exists():
        raise HTTPException(status_code=404, detail="Export file is missing on disk.")

    export.download_count = (export.download_count or 0) + 1
    db.commit()

    return FileResponse(disk_path, media_type=export.mime_type, filename=export.file_name)
