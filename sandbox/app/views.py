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