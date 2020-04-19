# geodjango

Projeto em Django para experimentar o PostGIS + GDAL.

Este projeto é baseado em [geopocos](https://github.com/marcellobenigno/geopocos) by [Marcello Benigno](https://github.com/marcellobenigno).

# Pré-requisitos

Instalar na sua máquina local:

```
apt install gdal-bin libgdal-dev
apt install python3-gdal
apt install binutils libproj-dev
```

Mais informações em [Make a Location-Based Web App With Django and GeoDjango](https://realpython.com/location-based-app-with-geodjango-tutorial/).


## Este projeto foi feito com:

* Python 3.7
* Django 2.2.12
* PostgreSQL 10.12 + PostGIS extension
* GDAL 2.2.3

## Como rodar o projeto?

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.

```
git clone https://github.com/rg3915/geodjango.git
cd geodjango
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py
```

* Crie um `.env` com as variáveis de ambiente:

Considere:

```
USER = myuser
PASSWORD = mypass
HOST = localhost
NAME = mygeodb  # database
```

```
cat << EOF > .env
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=127.0.0.1,.localhost
#DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
DATABASE_URL=postgres://myuser:mypass@localhost/mygeodb
EOF
```

* Rode as migrações.

```
python manage.py migrate
```

## Criando o banco e usuário

### Criando um usuário

```
sudo su - postgres

createuser --help

# -s --superuser
# -W --password

createuser -s -W myuser

exit
exit
```

Agora seu usuário pode criar um banco.

Vamos criar um template de banco de dados espacial.

```
createdb postgis

psql postgis
```

Vamos Habilitar a extensão espacial

```
CREATE ENTENSION postgis;
```

Se não tiver instalado, faça antes

```
sudo apt install -y postgis
```

Entra no banco novamente.

```
psql postgis

CREATE ENTENSION postgis;

\q
```

Este banco será um template para qualquer novo banco espacial.

```
# -T --template
createdb mygeodb -T postgis
```

Entrando no banco

```
psql mygeodb

\l
\d
```

Vamos editar o `settings.py`.

```
import os
from decouple import config, Csv
from dj_database_url import parse as dburl

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'leaflet',
    'django_extensions',
    'myproject.core',
    'myproject.poco',
]

...

DATABASES = {
    'default': config('DATABASE_URL', cast=dburl),
}
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (
        -39.2514038, -8.81179652676,
        -34.00817871, -5.656985355261,

    ),
    'TILES': [('GStreets', 'http://www.google.cn/maps/vt?lyrs=m@189&gl=cn&x={x}&y={y}&z={z}',
               {'attribution': '&copy; Google'}),
              ('GSatellite',
               'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
               {'attribution': '&copy; Google'})]
}
```

Se der problema de permissão de acesso, faça:

```
psql mygeodb
GRANT ALL PRIVILEGES ON DATABASE mygeodb TO myuser;
\q
```

Se não der certo faça tudo de novo:

```
sudo su - postgres
dropuser myuser
createuser myuser -s -W myuser
exit
exit
createdb postgis
psql postgis
GRANT ALL PRIVILEGES ON DATABASE postgis TO myuser;
CREATE EXTENSION postgis;
\q
createdb mygeodb -T postgis
```

Se ainda der erro faça:

```
psql mygeodb
# ALTER USER postgres WITH PASSWORD 'postgres';
# Coloque um espaço na frente do comando a seguir pra ele não ficar gravado no history.
 ALTER USER myuser WITH PASSWORD 'mypass';
\q
```

Agora vai

```
python manage.py migrate
```

## Criando um modelo espacial

https://github.com/marcellobenigno/geopocos

```
cd myproject
m startapp poco
```

Registre em `INSTALLED_APPS` em `settings.py`.

```
INSTALLED_APPS = [
    ...
    'myproject.core',
    'myproject.poco',
]
```

Faça clone do repositório

`git clone https://github.com/marcellobenigno/geopocos.git`

Copie a pasta

```
cd ..
# Corrija sua path
cp -r ~/geopocos/data/ .
```

#### Criando o modelo

`python manage.py ogrinspect data/pocos.shp Poco --srid 4326 --mapping > myproject/poco/models.py`

Criar um arquivo `load.py` na pasta da app `poco`.

```
cat << EOF > myproject/poco/load.py
import os

from django.contrib.gis.utils import LayerMapping

from .models import Poco

# Auto-generated `LayerMapping` dictionary for Poco model
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
EOF
```

Certifique-se ter feito o `migrate` antes.

```
python manage.py makemigrations
python manage.py migrate
```

Carregar os dados, estando na raiz do projeto:

```
python manage.py shell_plus

from myproject.poco.load import run_pocos

run_pocos()
```

#### Admin

```
cat << EOF > myproject/poco/admin.py
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Poco


@admin.register(Poco)
class PocoAdmin(LeafletGeoAdmin):
    pass
EOF
```



## Links:

https://realpython.com/location-based-app-with-geodjango-tutorial/

https://github.com/marcellobenigno/geopocos

