import os
from dotenv import load_dotenv

load_dotenv()

FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
IS_PRODUCTION = FLASK_ENV == 'production'

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-secret-change-in-production')

DATABASE_URL = os.environ.get('DATABASE_URL', None)

if DATABASE_URL:
    DB_ENGINE = 'mysql'
else:
    DB_ENGINE = 'sqlite'
    SQLITE_PATH = os.environ.get('SQLITE_PATH', 'archford.db')

SQLSERVER_HOST = os.environ.get('SQLSERVER_HOST', '64.250.34.124')
SQLSERVER_PORT = int(os.environ.get('SQLSERVER_PORT', '1433'))
SQLSERVER_DB = os.environ.get('SQLSERVER_DB', 'archford')
SQLSERVER_USER = os.environ.get('SQLSERVER_USER', '')
SQLSERVER_PASS = os.environ.get('SQLSERVER_PASS', '')
SQLSERVER_ENABLED = IS_PRODUCTION and bool(SQLSERVER_USER)

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'archford-admin-2026')

MAIL_ENABLED = False

def print_config_summary():
    if not IS_PRODUCTION:
        print("=" * 55)
        print("  Arch Ford Store — Configuration Summary")
        print("=" * 55)
        print(f"  Environment : {FLASK_ENV}")
        print(f"  Database    : {DB_ENGINE.upper()}")
        print(f"  SQL Server  : {'ENABLED' if SQLSERVER_ENABLED else 'disabled'}")
        print("=" * 55)
