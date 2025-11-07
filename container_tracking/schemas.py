from datetime import datetime
from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class Page(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]


class Carrier(BaseModel):
    scac: str
    name: str


class Country(BaseModel):
    code: str
    name: str


class Vessel(BaseModel):
    imo: Optional[int]
    name: Optional[str]


class Location(BaseModel):
    code: str
    name: str
    timezone: str
    country: Country


class PortOfLoading(BaseModel):
    location: Location
    date_of_loading: Optional[datetime]
    date_of_loading_initial: Optional[datetime]


class PortOfDischarge(BaseModel):
    location: Location
    date_of_discharge: Optional[datetime]
    date_of_discharge_initial: Optional[datetime]


class Route(BaseModel):
    port_of_loading: PortOfLoading
    port_of_discharge: PortOfDischarge
    transit_time: Optional[int]
    transit_percentage: Optional[int]
    co2_emission: Optional[float]


class Movement(BaseModel):
    event: Literal["EMSH", "GTIN", "LOAD", "DEPA", "ARRV", "DISC", "GTOT", "EMRT"]
    status: Literal["EST", "ACT"]
    location: Location
    vessel: Optional[Vessel]
    voyage: Optional[str]
    timestamp: datetime


class Container(BaseModel):
    number: str
    status: Literal[
        "EMPTY_SHIPPER",
        "GATE_IN",
        "LOADED",
        "SAILING",
        "ARRIVED",
        "DISCHARGED",
        "GATE_OUT",
        "EMPTY_RETURN",
        "UNKNOWN",
    ]
    size: Optional[int]
    type: Optional[str]
    movements: list[Movement]


class ShipmentCreate(BaseModel):
    booking_number: str


class ShipmentBase(BaseModel):
    id: int
    booking_number: str


class Shipment(ShipmentBase):
    carrier: Optional[Carrier]
    status: Literal[
        "NEW",
        "INPROGRESS",
        "BOOKED",
        "LOADED",
        "SAILING",
        "ARRIVED",
        "DISCHARGED",
        "UNTRACKED",
    ]
    route: Optional[Route]
    containers: list[Container]
    checked_at: Optional[datetime]
    discarded_at: Optional[datetime]
    changed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
