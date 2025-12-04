from django.contrib.gis.db import models


class Atm(models.Model):

    geom = models.PointField(srid=3857, spatial_index=True)
    provider = models.CharField(max_length=64, null=True, blank=True)