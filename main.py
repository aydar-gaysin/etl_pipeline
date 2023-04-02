import collections.abc as collections_abc
import contextlib
import dataclasses
import sqlite3
import logging
import more_itertools
import os
import psycopg2
import typing
import utils.psycopg2 as psycopg2_utils
import uuid

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    datefmt='%H:%M:$S',
    filename='load_data.log',
    filemode='w',
    format='[!] %(asctime)s %(name)s {%(pathname)s:%(lineno)d: %(message)s',
    level=logging.DEBUG,
),
logger = logging.getLogger(__name__)

# Число записей, которые будут загружены в одном блоке
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "50"))

# Название схемы, в которую будут загружены данные
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "test")

SQLITE_PATH = os.getenv('SQLITE_DB_PATH')
db_path = os.environ.get('SQLITE_DB_PATH')

postgres_db_config = {
    'dbname': os.getenv('POSTGRES_NAME'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
}

T = typing.TypeVar("T")


def void_function(data: typing.Iterable[T]) -> typing.Iterator[T]:
    pass


@dataclass
class CreatedMixin:
    created_at: datetime = field(default_factory=datetime.now, init=False)

    def __post_init__(self):
        if not isinstance(self.created_at, datetime):
            self.created_at = datetime.strptime(self.created_at + '00',
                                                '%Y-%m-%d %H:%M:%S.%f%z')


@dataclass
class TimeStampedMixin(CreatedMixin):
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.updated_at, datetime):
            self.updated_at = datetime.strptime(self.updated_at + '00',
                                                '%Y-%m-%d %H:%M:%S.%f%z')


@dataclass
class Filmwork:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = None
    description: str = None
    creation_date: datetime = None
    file_path: str = None
    rating: float = field(default=0.0)
    type: str = field(default='movie')
    created_at: datetime = field(default=datetime.utcnow())
    updated_at: datetime = field(default=datetime.utcnow())


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    created_at: datetime
    updated_at: datetime


@dataclass
class PersonFilmwork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime


@dataclass
class Genre:
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


# @dataclass
# class Genre(TimeStampedMixin):
#     id: uuid.UUID = field(default_factory=uuid.uuid4)
#     name: str = None
#     description: str = None
#     created_at: datetime = field(default_factory=datetime.now, init=False)
#     updated_at: datetime = field(default_factory=datetime.now, init=False)

# class Genre(TimeStampedMixin, CreatedMixin):
#     id: uuid.UUID = field(default_factory=uuid.uuid4)
#     name: str = None
#     description: str = None
# created_at: datetime = field(default=datetime.utcnow())
# updated_at: datetime = field(default=datetime.utcnow())


@dataclass
class GenreFilmwork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime = field(default=datetime.utcnow())


Connection = sqlite3.Connection


@contextlib.contextmanager
def open_connection(db_path: str) -> \
        collections_abc.Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    except sqlite3.Error as error:
        logger.exception(f"Failed to open connection to {db_path}")
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def pg_connect(**postgres_db_config):
    conn = psycopg2.connect(**postgres_db_config)
    try:
        yield conn
    finally:
        conn.close()


def extract_data(db_path, table_name, sqlite_dataclass) -> \
        collections_abc.Iterator[T]:
    with open_connection(db_path) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table_name} ORDER BY id')
        while data_chunk := cursor.fetchmany(size=CHUNK_SIZE):
            print(dict(data_chunk[0]))
            print('--------------------')
            yield from (sqlite_dataclass(**data_row) for data_row in
                        data_chunk)


def load_data(
        pg_connection: psycopg2_utils.Connection,
        sqlite_dataclass: collections_abc.Iterator[T],
        table_name
) -> None:
    # if not sqlite_dataclass.is_dataclass(dataclass):
    #     raise ValueError
    field_names = [datafield.name for datafield in dataclasses.fields(
        sqlite_dataclass)]
    stmt = f"INSERT INTO {POSTGRES_SCHEMA}.{table_name} " \
           f"({','.join(field_names)}) " \
           f"VALUES ({', '.join('%s' for _ in field_names)}) ON " \
           "CONFLICT (id) DO NOTHING"
    with pg_connection.cursor() as cursor:
        for data_chunk in more_itertools.ichunked(sqlite_dataclass,
                                                  CHUNK_SIZE):
            data = [dataclasses.astuple(item) for item in data_chunk]
            cursor.executemany(stmt, data)
            pg_connection.commit()


TABLES_DATACLASSES_MATCH = {
    'genre': Genre,
    # 'person': Person,
    # 'film_work': Filmwork,
    # 'genre_film_work': GenreFilmwork,
    # 'person_film_work': PersonFilmwork,
}


def run() -> None:
    for table_name, sqlite_dataclass in TABLES_DATACLASSES_MATCH.items():
        print(table_name, sqlite_dataclass)

        with psycopg2_utils.open_connection(postgres_db_config) as connection:
            load_data(connection, extract_data(db_path, table_name,
                                               sqlite_dataclass), table_name)

        for value in extract_data(db_path, table_name, sqlite_dataclass):
            print(asdict(value))


if __name__ == "__main__":
    run()
