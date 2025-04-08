import os
from sqlalchemy import create_engine
from flask_mail import Mail

# Configuración de la base de datos
DATABASE_URL = "mysql+pymysql://Guillermoppm:Utv26912@Guillermoppm.mysql.pythonanywhere-services.com/Guillermoppm$licitacionesdb1"
engine = create_engine(DATABASE_URL, pool_recycle=280)

# Configuración de Flask-Mail
MAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'licitaciones401@gmail.com',
    'MAIL_PASSWORD': 'nmql jacr edic zmfx',
    'MAIL_DEFAULT_SENDER': 'licitaciones401@gmail.com'
}

def init_mail(app):
    app.config.update(MAIL_CONFIG)
    return Mail(app)

# Clave secreta para la sesión
SECRET_KEY = os.urandom(24)