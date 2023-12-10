import asyncio
from datetime import datetime
from typing import Literal, Optional

import asyncpg
from google.cloud.sql.connector import Connector
from pgvector.asyncpg import register_vector
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# custom modules
import neosearch.models as models
from .. import datastore


POSTGRES_IDENTIFIER = "cloudsql-postgres"


class Config(BaseModel, datastore.AbstractConfig):
    kind: Literal["cloudsql-postgres"]
    project: str
    region: str
    instance: str
    user: str
    password: str
    database: str


class Client(datastore.Client[Config]):
    __pool: AsyncEngine

    @datastore.classproperty
    def kind(cls):
        return "cloudsql-postgres"

    def __init__(self, pool: AsyncEngine):
        self.__pool = pool

    @classmethod
    async def create(cls, config: Config) -> "Client":
        loop = asyncio.get_running_loop()

        async def getconn() -> asyncpg.Connection:
            async with Connector(loop=loop) as connector:
                conn: asyncpg.Connection = await connector.connect_async(
                    # Cloud SQL instance connection name
                    f"{config.project}:{config.region}:{config.instance}",
                    "asyncpg",
                    user=f"{config.user}",
                    password=f"{config.password}",
                    db=f"{config.database}",
                )
            await register_vector(conn)
            return conn

        pool = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=getconn,
        )
        if pool is None:
            raise TypeError("pool not instantiated")
        return cls(pool)

    async def initialize_data(
        self,
        airports: list[models.Airport],
        amenities: list[models.Amenity],
        flights: list[models.Flight],
    ) -> None:
        async with self.__pool.connect() as conn:
            # If the table already exists, drop it to avoid conflicts
            await conn.execute(text("DROP TABLE IF EXISTS airports CASCADE"))
            # Create a new table
            await conn.execute(
                text(
                    """
                    CREATE TABLE airports(
                      id INT PRIMARY KEY,
                      iata TEXT,
                      name TEXT,
                      city TEXT,
                      country TEXT
                    )
                    """
                )
            )
            # Insert all the data
            await conn.execute(
                text(
                    """INSERT INTO airports VALUES (:id, :iata, :name, :city, :country)"""
                ),
                [
                    {
                        "id": a.id,
                        "iata": a.iata,
                        "name": a.name,
                        "city": a.city,
                        "country": a.country,
                    }
                    for a in airports
                ],
            )

            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            # If the table already exists, drop it to avoid conflicts
            await conn.execute(text("DROP TABLE IF EXISTS amenities CASCADE"))
            # Create a new table
            await conn.execute(
                text(
                    """
                    CREATE TABLE amenities(
                      id INT PRIMARY KEY,
                      name TEXT,
                      description TEXT,
                      location TEXT,
                      terminal TEXT,
                      category TEXT,
                      hour TEXT,
                      content TEXT NOT NULL,
                      embedding vector(768) NOT NULL
                    )
                    """
                )
            )
            # Insert all the data
            await conn.execute(
                text(
                    """INSERT INTO amenities VALUES (:id, :name, :description, :location, :terminal, :category, :hour, :content, :embedding)"""
                ),
                [
                    {
                        "id": a.id,
                        "name": a.name,
                        "description": a.description,
                        "location": a.location,
                        "terminal": a.terminal,
                        "category": a.category,
                        "hour": a.hour,
                        "content": a.content,
                        "embedding": a.embedding,
                    }
                    for a in amenities
                ],
            )

            # If the table already exists, drop it to avoid conflicts
            await conn.execute(text("DROP TABLE IF EXISTS flights CASCADE"))
            # Create a new table
            await conn.execute(
                text(
                    """
                    CREATE TABLE flights(
                      id INTEGER PRIMARY KEY,
                      airline TEXT,
                      flight_number TEXT,
                      departure_airport TEXT,
                      arrival_airport TEXT,
                      departure_time TIMESTAMP,
                      arrival_time TIMESTAMP,
                      departure_gate TEXT,
                      arrival_gate TEXT
                    )
                    """
                )
            )
            # Insert all the data
            await conn.execute(
                text(
                    """INSERT INTO flights VALUES (:id, :airline, :flight_number, :departure_airport, :arrival_airport, :departure_time, :arrival_time, :departure_gate, :arrival_gate)"""
                ),
                [
                    {
                        "id": f.id,
                        "airline": f.airline,
                        "flight_number": f.flight_number,
                        "departure_airport": f.departure_airport,
                        "arrival_airport": f.arrival_airport,
                        "departure_time": f.departure_time,
                        "arrival_time": f.arrival_time,
                        "departure_gate": f.departure_gate,
                        "arrival_gate": f.arrival_gate,
                    }
                    for f in flights
                ],
            )
            await conn.commit()

    async def export_data(
        self,
    ) -> tuple[list[models.Airport], list[models.Amenity], list[models.Flight]]:
        async with self.__pool.connect() as conn:
            airport_task = asyncio.create_task(
                conn.execute(text("""SELECT * FROM airports"""))
            )

            amenity_task = asyncio.create_task(
                conn.execute(text("""SELECT * FROM amenities"""))
            )
            flights_task = asyncio.create_task(
                conn.execute(text("""SELECT * FROM flights"""))
            )

            airport_results = (await airport_task).mappings().fetchall()
            amenity_results = (await amenity_task).mappings().fetchall()
            flights_results = (await flights_task).mappings().fetchall()

            airports = [models.Airport.model_validate(a) for a in airport_results]
            amenities = [models.Amenity.model_validate(a) for a in amenity_results]
            flights = [models.Flight.model_validate(f) for f in flights_results]
            return airports, amenities, flights

    async def get_airport_by_id(self, id: int) -> Optional[models.Airport]:
        async with self.__pool.connect() as conn:
            s = text("""SELECT * FROM airports WHERE id=:id""")
            params = {"id": id}
            result = (await conn.execute(s, params)).mappings().fetchone()

        if result is None:
            return None

        res = models.Airport.model_validate(result)
        return res

    async def get_airport_by_iata(self, iata: str) -> Optional[models.Airport]:
        async with self.__pool.connect() as conn:
            s = text("""SELECT * FROM airports WHERE iata ILIKE :iata""")
            params = {"iata": iata}
            result = (await conn.execute(s, params)).mappings().fetchone()

        if result is None:
            return None

        res = models.Airport.model_validate(result)
        return res

    async def search_airports(
        self,
        country: Optional[str] = None,
        city: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list[models.Airport]:
        async with self.__pool.connect() as conn:
            s = text(
                """
                SELECT * FROM airports
                  WHERE (CAST(:country AS TEXT) IS NULL OR country ILIKE :country)
                  AND (CAST(:city AS TEXT) IS NULL OR city ILIKE :city)
                  AND (CAST(:name AS TEXT) IS NULL OR name ILIKE '%' || :name || '%')
                """
            )
            params = {
                "country": country,
                "city": city,
                "name": name,
            }
            results = (await conn.execute(s, params)).mappings().fetchall()

        res = [models.Airport.model_validate(r) for r in results]
        return res

    async def get_amenity(self, id: int) -> Optional[models.Amenity]:
        async with self.__pool.connect() as conn:
            s = text(
                """
                SELECT id, name, description, location, terminal, category, hour
                  FROM amenities WHERE id=:id
                """
            )
            params = {"id": id}
            result = (await conn.execute(s, params)).mappings().fetchone()

        if result is None:
            return None

        res = models.Amenity.model_validate(result)
        return res

    async def amenities_search(
        self, query_embedding: list[float], similarity_threshold: float, top_k: int
    ) -> list[models.Amenity]:
        async with self.__pool.connect() as conn:
            s = text(
                """
                SELECT id, name, description, location, terminal, category, hour
                  FROM (
                      SELECT id, name, description, location, terminal, category, hour, 1 - (embedding <=> :query_embedding) AS similarity
                      FROM amenities
                      WHERE 1 - (embedding <=> :query_embedding) > :similarity_threshold
                      ORDER BY similarity DESC
                      LIMIT :top_k
                  ) AS sorted_amenities
                """
            )
            params = {
                "query_embedding": query_embedding,
                "similarity_threshold": similarity_threshold,
                "top_k": top_k,
            }
            results = (await conn.execute(s, params)).mappings().fetchall()

        res = [models.Amenity.model_validate(r) for r in results]
        return res

    async def get_flight(self, flight_id: int) -> Optional[models.Flight]:
        async with self.__pool.connect() as conn:
            s = text(
                """
                SELECT * FROM flights
                  WHERE id = :flight_id
                """
            )
            params = {"flight_id": flight_id}
            result = (await conn.execute(s, params)).mappings().fetchone()

        if result is None:
            return None

        res = models.Flight.model_validate(result)
        return res

    async def search_flights_by_number(
        self,
        airline: str,
        number: str,
    ) -> list[models.Flight]:
        async with self.__pool.connect() as conn:
            s = text(
                """
                SELECT * FROM flights
                  WHERE airline = :airline
                  AND flight_number = :number
                """
            )
            params = {
                "airline": airline,
                "number": number,
            }
            results = (await conn.execute(s, params)).mappings().fetchall()

        res = [models.Flight.model_validate(r) for r in results]
        return res

    async def search_flights_by_airports(
        self,
        date: str,
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
    ) -> list[models.Flight]:
        async with self.__pool.connect() as conn:
            s = text(
                """
                SELECT * FROM flights
                  WHERE (CAST(:departure_airport AS TEXT) IS NULL OR departure_airport ILIKE :departure_airport)
                  AND (CAST(:arrival_airport AS TEXT) IS NULL OR arrival_airport ILIKE :arrival_airport)
                  AND departure_time > CAST(:datetime AS timestamp) - interval '1 day'
                  AND departure_time < CAST(:datetime AS timestamp) + interval '1 day'
                """
            )
            params = {
                "departure_airport": departure_airport,
                "arrival_airport": arrival_airport,
                "datetime": datetime.strptime(date, "%Y-%m-%d"),
            }

            results = (await conn.execute(s, params)).mappings().fetchall()

        res = [models.Flight.model_validate(r) for r in results]
        return res

    async def close(self):
        await self.__pool.dispose()
