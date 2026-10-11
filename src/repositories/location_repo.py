"""Campus boundary store (DFD D3).

TODAY: the boundary is read from a GeoJSON file (src/temp/campus_boundary.geojson).

WHEN THE DATABASE ARRIVES, this is the ONLY file that needs to change:
  1. Add a SQLModel table, e.g.
         class CampusBoundary(SQLModel, table=True):
             id: int | None = Field(default=None, primary_key=True)
             name: str
             geojson: dict = Field(sa_column=Column(JSON))   # the Polygon geometry
  2. Change `get_campus_polygons` to take a session and query that table:
         def get_campus_polygons(session: Session = Depends(get_session)) -> list[Ring]:
             rows = session.exec(select(CampusBoundary)).all()
             return [_geojson_to_ring(row.geojson) for row in rows]
  3. Delete the file loader and its @lru_cache (a cache would serve stale data
     once the boundary can be edited in the DB). Optionally keep the GeoJSON
     file as seed data to load into the table once.

The router and service do NOT change: the router already gets its rings through
`Depends(get_campus_polygons)`, so FastAPI will inject the session automatically.
"""
import json
from functools import lru_cache
from pathlib import Path

# A ring is a list of (latitude, longitude) points.
Ring = list[tuple[float, float]]

_BOUNDARY_FILE = Path(__file__).resolve().parent.parent / "temp" / "campus_boundary.geojson"


@lru_cache  # FILE-ONLY: remove when switching to the database (see note above)
def _load_rings_from_file(path: Path) -> list[Ring]:
    data = json.loads(path.read_text())
    rings: list[Ring] = []
    for feature in data["features"]:
        geom = feature["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for poly in polys:
            # GeoJSON is [lon, lat]; flip to (lat, lon). poly[0] is the outer ring.
            rings.append([(lat, lon) for lon, lat in poly[0]])
    return rings


def get_campus_polygons() -> list[Ring]:
    """Return every campus boundary ring as (lat, lon) points.

    Keep this signature's *return type* stable. Only the parameters (a DB session)
    and the body change when the database arrives.
    """
    return _load_rings_from_file(_BOUNDARY_FILE)