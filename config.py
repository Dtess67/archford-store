import os

# Load a local .env for development convenience only. Never required in production;
# the import is guarded so a missing dependency can never break startup.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
IS_PRODUCTION = FLASK_ENV == 'production'


class ConfigError(RuntimeError):
    """Raised at startup when a required production credential is missing."""


def _required_credential(name, dev_fallback):
    """Return env var `name`.

    In production the value MUST be supplied by the environment (e.g. a mounted
    Secret Manager secret). If it is missing or empty, the application refuses to
    start — there is deliberately no built-in production fallback. In development
    a clearly non-production placeholder is used so local work stays easy.
    """
    value = os.environ.get(name)
    if value:
        return value
    if IS_PRODUCTION:
        raise ConfigError(
            f"Required credential '{name}' is not set. "
            "Refusing to start in production without it."
        )
    return dev_fallback


SECRET_KEY = _required_credential('SECRET_KEY', 'dev-only-secret-not-for-production')

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

ADMIN_USERNAME = _required_credential('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = _required_credential('ADMIN_PASSWORD', 'dev-only-password-not-for-production')

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
