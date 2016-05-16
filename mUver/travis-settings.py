from .settings import *


DATABASE = {
     'default': {
          'ENGINE':     'django.contrib.gis.db.backends.postgis',
          'NAME':     'muver_db',
          'USER':     'postgres',
          'PASSWORD':     '',
          'HOST':     'localhost',
          'PORT':     '',
     }
}