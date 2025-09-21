import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'DROWSSAP'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'salty'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_LOGIN_URL = "/fs-login"
    SECURITY_LOGOUT_URL = "/fs-logout"
    SECURITY_REGISTER_URL = "/fs-register"
    SECURITY_POST_LOGIN_VIEW = None
    SECURITY_POST_LOGOUT_VIEW = None
    SECURITY_POST_REGISTER_VIEW = None
    SECURITY_UNAUTHORIZED_VIEW = None
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = False
    SECURITY_REGISTERABLE = False
    SECURITY_CONFIRMABLE = False
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_TOKEN_AUTHENTICATION = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    BROKER_URL = 'redis://localhost:6379/0'
    RESULT_BACKEND = 'redis://localhost:6379/0'
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('GMAIL_USER')
    MAIL_PASSWORD = os.environ.get('GMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.environ.get('GMAIL_USER')


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz.db'
    DEBUG = False
    TESTING = False
