import asyncio
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Literal, Optional

import asyncpg
from pgvector.asyncpg import register_vector
from pydantic import BaseModel

# custom modules
import neosearch.models as models
from .. import datastore


POSTGRES_IDENTIFIER = "postgres"


class Config(BaseModel, datastore.AbstractConfig):
    kind: Literal["postgres"]
    host: IPv4Address | IPv6Address = IPv4Address("127.0.0.1")
    port: int = 5432
    user: str
    password: str
    database: str


class Client(datastore.Client[Config]):
    __pool: asyncpg.Pool

    @datastore.classproperty
    def kind(cls):
        return "postgres"

    def __init__(self, pool: asyncpg.Pool):
        self.__pool = pool

    @classmethod
    async def create(cls, config: Config) -> "Client":
        async def init(conn):
            await register_vector(conn)

        pool = await asyncpg.create_pool(
            host=str(config.host),
            user=config.user,
            password=config.password,
            database=config.database,
            port=config.port,
            init=init,
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
        async with self.__pool.acquire() as conn:
            # If the table already exists, drop it to avoid conflicts
            await conn.execute("DROP TABLE IF EXISTS airports CASCADE")
            # Create a new table
            await conn.execute(
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
            # Insert all the data
            await conn.executemany(
                """INSERT INTO airports VALUES ($1, $2, $3, $4, $5)""",
                [(a.id, a.iata, a.name, a.city, a.country) for a in airports],
            )

            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            # If the table already exists, drop it to avoid conflicts
            await conn.execute("DROP TABLE IF EXISTS amenities CASCADE")
            # Create a new table
            await conn.execute(
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
            # Insert all the data
            await conn.executemany(
                """INSERT INTO amenities VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
                [
                    (
                        a.id,
                        a.name,
                        a.description,
                        a.location,
                        a.terminal,
                        a.category,
                        a.hour,
                        a.content,
                        a.embedding,
                    )
                    for a in amenities
                ],
            )

            # If the table already exists, drop it to avoid conflicts
            await conn.execute("DROP TABLE IF EXISTS flights CASCADE")
            # Create a new table
            await conn.execute(
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
            # Insert all the data
            await conn.executemany(
                """INSERT INTO flights VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
                [
                    (
                        f.id,
                        f.airline,
                        f.flight_number,
                        f.departure_airport,
                        f.arrival_airport,
                        f.departure_time,
                        f.arrival_time,
                        f.departure_gate,
                        f.arrival_gate,
                    )
                    for f in flights
                ],
            )

    async def export_data(
        self,
    ) -> tuple[list[models.Airport], list[models.Amenity], list[models.Flight]]:
        airport_task = asyncio.create_task(
            self.__pool.fetch("""SELECT * FROM airports""")
        )
        amenity_task = asyncio.create_task(
            self.__pool.fetch("""SELECT * FROM amenities""")
        )
        flight_task = asyncio.create_task(
            self.__pool.fetch("""SELECT * FROM flights""")
        )

        airports = [models.Airport.model_validate(dict(a)) for a in await airport_task]
        amenities = [models.Amenity.model_validate(dict(a)) for a in await amenity_task]
        flights = [models.Flight.model_validate(dict(f)) for f in await flight_task]
        return airports, amenities, flights

    async def get_airport_by_id(self, id: int) -> Optional[models.Airport]:
        result = await self.__pool.fetchrow(
            """
              SELECT * FROM airports WHERE id=$1
            """,
            id,
        )

        if result is None:
            return None

        result = models.Airport.model_validate(dict(result))
        return result

    async def get_airport_by_iata(self, iata: str) -> Optional[models.Airport]:
        result = await self.__pool.fetchrow(
            """
              SELECT * FROM airports WHERE iata ILIKE $1
            """,
            iata,
        )

        if result is None:
            return None

        result = models.Airport.model_validate(dict(result))
        return result

    async def search_airports(
        self,
        country: Optional[str] = None,
        city: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list[models.Airport]:
        results = await self.__pool.fetch(
            """
            SELECT * FROM airports
            WHERE ($1::TEXT IS NULL OR country ILIKE $1)
            AND ($2::TEXT IS NULL OR city ILIKE $2)
            AND ($3::TEXT IS NULL OR name ILIKE '%' || $3 || '%')
            """,
            country,
            city,
            name,
            timeout=10,
        )

        results = [models.Airport.model_validate(dict(r)) for r in results]
        return results

    async def get_amenity(self, id: int) -> Optional[models.Amenity]:
        result = await self.__pool.fetchrow(
            """
                SELECT id, name, description, location, terminal, category, hour
                FROM amenities WHERE id=$1
            """,
            id,
        )

        if result is None:
            return None

        result = models.Amenity.model_validate(dict(result))
        return result

    async def amenities_search(
        self, query_embedding: list[float], similarity_threshold: float, top_k: int
    ) -> list[models.Amenity]:
        results = await self.__pool.fetch(
            """
                SELECT id, name, description, location, terminal, category, hour
                FROM (
                    SELECT id, name, description, location, terminal, category, hour, 1 - (embedding <=> $1) AS similarity
                    FROM amenities
                    WHERE 1 - (embedding <=> $1) > $2
                    ORDER BY similarity DESC
                    LIMIT $3
                ) AS sorted_amenities
            """,
            query_embedding,
            similarity_threshold,
            top_k,
            timeout=10,
        )

        results = [models.Amenity.model_validate(dict(r)) for r in results]
        return results

    async def get_flight(self, flight_id: int) -> Optional[models.Flight]:
        result = await self.__pool.fetchrow(
            """
                SELECT * FROM flights
                WHERE id = $1
            """,
            flight_id,
            timeout=10,
        )

        if result is None:
            return None

        result = models.Flight.model_validate(dict(result))
        return result

    async def search_flights_by_number(
        self,
        airline: str,
        number: str,
    ) -> list[models.Flight]:
        results = await self.__pool.fetch(
            """
                SELECT * FROM flights
                WHERE airline = $1
                AND flight_number = $2;
            """,
            airline,
            number,
            timeout=10,
        )
        results = [models.Flight.model_validate(dict(r)) for r in results]
        return results

    async def search_flights_by_airports(
        self,
        date: str,
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
    ) -> list[models.Flight]:
        results = await self.__pool.fetch(
            """
                SELECT * FROM flights
                WHERE ($1::TEXT IS NULL OR departure_airport ILIKE $1)
                AND ($2::TEXT IS NULL OR arrival_airport ILIKE $2)
                AND departure_time > $3::timestamp - interval '1 day'
                AND departure_time < $3::timestamp + interval '1 day';
            """,
            departure_airport,
            arrival_airport,
            datetime.strptime(date, "%Y-%m-%d"),
            timeout=10,
        )
        results = [models.Flight.model_validate(dict(r)) for r in results]
        return results

    async def close(self):
        await self.__pool.close()
