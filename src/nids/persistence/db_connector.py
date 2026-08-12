from psycopg2 import pool
from nids.config.settings import settings
from nids.utils.logger import get_logger

logger = get_logger(__name__)

class DBConnector:
    _pool: pool.SimpleConnectionPool = None

    @classmethod
    def get_pool(cls) -> pool.SimpleConnectionPool:
        if cls._pool is None:
            cls._pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.db_host,
                port=settings.db_port,
                dbname=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
            )
            logger.info("Database connection pool dibuat")
        return cls._pool

    @classmethod
    def get_connection(cls):
        return cls.get_pool().getconn()

    @classmethod
    def release_connection(cls, conn):
        cls.get_pool().putconn(conn)
