Python summit 2025
This is a short introduction to GeoDjango, prepared for Python Summit Warsaw 2025.

Start a sandbox
Start sandbox environment container in detached mode.

docker compose up sandbox -d
Enter sandbox terminal.

docker compose exec sandbox /bin/bash
Note, that all commands from now on should be run in the sandbox terminal.

Create django project
Create django project named "atm_nearby" in the directory sandbox

django-admin startproject atm_nearby .
Create django application named "app"

python3 manage.py startapp app
Enable geodjango in the project and add the newly created application to settings file

# ./atm_nearby/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'app'
]
Database
Connect django to postgres database

# ./atm_nearby/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv("POSTGRES_DB"),
        'USER': os.getenv("POSTGRES_USER"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD"),
        'HOST': os.getenv("POSTGRES_HOST"),
        'PORT': os.getenv("POSTGRES_PORT"),
    }
}
Create ORM model for our data

# ./app/model.py

from django.contrib.gis.db import models

class Atm(models.Model):

    geom = models.PointField(srid=3857, spatial_index=True)
    provider = models.CharField(max_length=64, null=True, blank=True)
Make migrations

python3 manage.py makemigrations
Apply migrations

python3 manage.py migrate
Load sample data
Download sample data

Create a script loading sample data

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
Execute data import script

python3 manage.py shell < load_data.py
Other settings
Alow application to be response to any host

# ./atm_nearby/settings.py

ALLOWED_HOSTS = ['*']
Add static files dir, to be able to use CSS

# ./atm_nearby/settings.py

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
Create first django view
Create urls.py in app module. This file will be responsible for connecting user to right service.

# ./app/urls.py

from django.urls import path

from app import views

urlpatterns = [
    path('', views.index),
]
Load our urls to project urls

# ./atm_nearby/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]
Create index view

# ./app/views.py

from django.shortcuts import render

def index(request):
    return render(request, "index.html")
index.html

<html>
    <head>
        <meta charset="UTF-8" />
        <title>ATM nearby</title>

        <script src="https://cdn.jsdelivr.net/npm/ol@v10.4.0/dist/ol.js"> </script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ol@v10.4.0/ol.css">
        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>

        <link rel="stylesheet" href="/static/style.css">
    </head>
<body>
    <div id="navbar">
        <img src="/static/atm.png">
        <h1>ATM nearby</h1>
    </div>
    <div id="map"></div>
    
    <script>
        const atmStyle = new ol.style.Style({
            image: new ol.style.Icon({
                src: '/static/atm.png',
                scale: 0.08,
                anchor: [0.5, 1],
            }),
        });
        const userIconStyle = new ol.style.Style({
            image: new ol.style.Icon({
                src: '/static/pin.png',
                scale: 0.08,
                anchor: [0.5, 1],
            }),
        });
        
        const geojsonFormat = new ol.format.GeoJSON();
        
        const osmLayer = new ol.layer.Tile({
            source: new ol.source.OSM(),
            className: 'ol_bw'
        });
        
        const positionVectorSource = new ol.source.Vector({ features: [] });
        const userPositionLayer = new ol.layer.Vector({ source: positionVectorSource });

        const view = new ol.View({
                center: [2337631, 6842158],
                zoom: 15,
            })

        const map = new ol.Map({
            layers: [
                osmLayer,
                userPositionLayer,
            ],
            target: 'map',
            view: view,

        });

        const geolocation = new ol.Geolocation({
            projection: view.getProjection(),
        });

        geolocation.setTracking(true);
        geolocation.on('change:position', async function () {
            
            const coordinates = geolocation.getPosition();
            const marker = new ol.Feature(new ol.geom.Point(coordinates))
            marker.setStyle(userIconStyle);
            positionVectorSource.clear();
            positionVectorSource.addFeature(marker);

            view.animate({
                    center: coordinates,
                    zoom:16,
                    duration: 2000,
                })

        //     const atms = await axios.get(`/atms?x=${coordinates[0]}&y=${coordinates[1]}`)
        //    
        //     const atmVectorSource = new ol.source.Vector({
        //         features: geojsonFormat.readFeatures(atms.data)
        //     });
        //    
        //     atmLayer = new ol.layer.Vector({
        //         source: atmVectorSource,
        //         style: atmStyle
        //     })
        //     map.addLayer(atmLayer)

        });
    </script>
</body>
</html>
Create service for finding ATMs nearby

# ./app/views.py

from django.http import HttpResponse
from django.shortcuts import render
from app.models import Atm
from django.contrib.gis.geos import Point
from django.core.serializers import serialize


def index(request):
    return render(request, "index.html")


def find_atms(request):

    x = float(request.GET.get("x"))
    y = float(request.GET.get("y"))
    buffer_m = int(request.GET.get("buffer", 5000))

    point = Point(x=x, y=y, srid=3857)
    buffer_area = point.buffer(buffer_m)

    atms = Atm.objects.filter(geom__intersects=buffer_area)
    res = serialize("geojson", atms, geometry_field="geom", fields=["provider"], srid=3857)

    return HttpResponse(res, content_type="application/json")

Publish the endpoing

# ./app/urls.py

from django.urls import path
from app import views

urlpatterns = [
    path('', views.index),
    path('atms', views.find_atms),
]