"""Export supplied local boundary shapefiles as browser-ready GeoJSON."""
from pathlib import Path
import json
import shapefile

ROOT=Path(__file__).resolve().parents[1]
def features(path: Path, properties: list[str]):
    reader=shapefile.Reader(str(path),encoding='latin1'); names=[field[0] for field in reader.fields[1:]]; out=[]
    for item in reader.iterShapeRecords():
        if item.shape.shapeType == shapefile.NULL:
            continue
        record=dict(zip(names,item.record));out.append({'type':'Feature','properties':{key:record.get(key) for key in properties},'geometry':item.shape.__geo_interface__})
    return {'type':'FeatureCollection','features':out}
target=ROOT/'data'/'serving';target.mkdir(parents=True,exist_ok=True)
(target/'santa_catarina_municipios.geojson').write_text(json.dumps(features(ROOT/'shape'/'MUNICIPIOS_SC2014.shp',['NM_MUNICIP','CD_GEOCODI']),ensure_ascii=False),encoding='utf-8')
(target/'countries.geojson').write_text(json.dumps(features(ROOT/'shape'/'ne_10m_admin_0_countries.shp',['ADMIN','ISO_A3']),ensure_ascii=False),encoding='utf-8')
