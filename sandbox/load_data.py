from django.contrib.gis.gdal import DataSource
from app.models import Atm

geopackage_path = "test_data.gpkg"
ds = DataSource(geopackage_path)

layer = ds[0]

for feature in layer:

    Atm.objects.create(
        geom=feature.geom.wkt,
        provider=feature.get('name'),
    )

print("Import DONE!")