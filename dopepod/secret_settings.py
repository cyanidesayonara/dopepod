"""
Secret settings
"""

SECRET_KEY = '##4ecs_i25ogkg34i8yddgte+%ohm=bnt0l%hk4t$h0tf@wja1'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dopepod',
        'USER': 'planetary',
        'PASSWORD': 'slamdancelowpostgokart',
        'HOST': 'localhost',
        'PORT': '',
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'cyanidesayonara@gmail.com'
EMAIL_HOST_PASSWORD = 'slamdancelowpostgokart'
EMAIL_PORT = 587
