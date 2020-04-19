import os

from django.contrib.gis.utils import LayerMapping

from .models import Poco

# Auto-generated  dictionary for Poco model
poco_mapping = {
    'proprietar': 'proprietar',
    'orgao': 'orgao',
    'data_perfu': 'data_perfu',
    'profundida': 'profundida',
    'q_m3h': 'q_m3h',
    'equipament': 'equipament',
    'geom': 'POINT',
}

poco_shp = os.path.abspath(os.path.join('data', 'pocos.shp'))


def run_pocos(verbose=True):
    lm = LayerMapping(Poco, poco_shp, poco_mapping)
    lm.save(strict=True, verbose=verbose)
