# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class Poco(models.Model):
    proprietar = models.CharField(max_length=254)
    orgao = models.CharField(max_length=254)
    data_perfu = models.DateField()
    profundida = models.FloatField()
    q_m3h = models.FloatField()
    equipament = models.CharField(max_length=254)
    geom = models.PointField(srid=4326)
