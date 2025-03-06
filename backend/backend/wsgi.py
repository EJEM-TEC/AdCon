import os
import sys

# Adiciona a pasta raiz ao caminho do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
