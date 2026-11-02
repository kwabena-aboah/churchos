from decouple import config

env = config("DJANGO_ENV", default="development")

if env == "production":
    from .production import *
elif env == "render":
    from .render import *
else:
    from .development import *
