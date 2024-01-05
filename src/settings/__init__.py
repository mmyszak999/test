from decouple import config
from split_settings.tools import include


base_settings = [
    "basic.py",
    "stripe.py",
    "drf.py",
    "swagger.py",
]


include(*base_settings)
