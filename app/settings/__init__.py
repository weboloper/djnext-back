import os

if os.environ.get("ENV_NAME") == 'production':
    from .prod import *
elif os.environ.get("ENV_NAME") == 'staging':
    from .prod import *
else:
    from .dev import *