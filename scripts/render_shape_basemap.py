"""Create a local radar-basemap raster from the user-supplied SHP boundaries."""
from pathlib import Path
import shapefile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import cos, pi

ROOT = Path(__file__).resolve().parents[1]
SHAPES = ROOT / 'shape'
OUT = ROOT / 'data' / 'serving' / 'santa_catarina_shp_basemap.png'
# The CAPPI grid is a local Cartesian plane, -240..240 km from Chapecó.  Plot
# the supplied geographic SHP data in that identical tangent-plane reference.
RADAR_LON, RADAR_LAT = -52.60374, -27.04879
GRID_KM = 240.0

def local_xy(lon: float, lat: float) -> tuple[float, float]:
    return (
        (lon - RADAR_LON) * 111.32 * cos(RADAR_LAT * pi / 180),
        (lat - RADAR_LAT) * 110.57,
    )

def draw(reader: shapefile.Reader, color: str, width: float, alpha: float) -> None:
    for shape in reader.shapes():
        points = shape.points
        for start, end in zip(list(shape.parts) + [len(points)], list(shape.parts[1:]) + [len(points)]):
            ring = points[start:end]
            if ring:
                x, y = zip(*(local_xy(lon, lat) for lon, lat in ring))
                plt.plot(x, y, color=color, linewidth=width, alpha=alpha)

plt.figure(figsize=(8, 8), dpi=160, facecolor='#07131f')
ax = plt.gca()
ax.set_facecolor('#102737')
draw(shapefile.Reader(str(SHAPES / 'ne_10m_admin_0_countries.shp'), encoding='latin1'), '#4f7489', 0.55, 0.8)
draw(shapefile.Reader(str(SHAPES / 'MUNICIPIOS_SC2014.shp'), encoding='latin1'), '#b7dce7', 0.42, 0.92)
ax.set_xlim(-GRID_KM, GRID_KM); ax.set_ylim(-GRID_KM, GRID_KM); ax.set_aspect('equal'); ax.axis('off')
plt.subplots_adjust(0, 0, 1, 1)
OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, dpi=160, facecolor='#07131f', bbox_inches=None, pad_inches=0)
plt.close()
print(OUT)
