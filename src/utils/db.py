from sqlalchemy.orm import DeclarativeBase, create_session
from sqlalchemy.engine import URL, create_engine
from src.settings import settings
from src.args_parser import args


class Base(DeclarativeBase):
    ...


url = URL.create(drivername=settings.DB_DRIVER_NAME,
                 username=settings.POSTGRES_USER,
                 password=settings.POSTGRES_PASSWORD,
                 host=settings.PGHOST,
                 port=settings.PGPORT,
                 database=settings.POSTGRES_DB)
engine = create_engine(url)
connection = engine.connect()

session = create_session(bind=engine)


def create_tables():
    from src.models import Users, Messages

    if args.recreate:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
