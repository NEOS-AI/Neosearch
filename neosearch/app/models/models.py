import ast
import datetime
# from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class Airport(BaseModel):
    id: int
    iata: str
    name: str
    city: str
    country: str


class Amenity(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    name: str
    description: str
    location: str
    terminal: str
    category: str
    hour: str
    content: Optional[str] = None
    embedding: Optional[list[float]] = None

    @field_validator("embedding", mode="before")
    def validate(cls, v):
        if isinstance(v, str):
            v = ast.literal_eval(v)
            v = [float(f) for f in v]
        return v


class Flight(BaseModel):
    id: int
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    departure_gate: str
    arrival_gate: str
