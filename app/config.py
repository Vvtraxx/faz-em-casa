import os
from datetime import timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """Configurações base da aplicação"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'teste1234')
    API_EXTERNA_BASE_URL = os.getenv('API_EXTERNA_BASE_URL', 'https://oracleapex.com/ords/fazemcasa')
    API_EXTERNA_RETRIES = int(os.getenv('API_EXTERNA_RETRIES', 3))
    JWT_EXPIRATION_DELTA = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))


class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    TESTING = False
    API_EXTERNA_TIMEOUT = int(os.getenv('API_EXTERNA_TIMEOUT', 15))

# Dicionário de configurações
config = {
    'production': ProductionConfig
}
