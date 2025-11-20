from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class Page(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]


# -- Ocean Shipment Schemas --


class OceanCarrierDetail(BaseModel):
    scac: str
    name: str
    status: Literal["ACTIVE", "PASSIVE"]


class OceanCarrier(BaseModel):
    scac: str
    name: str


class OceanCountry(BaseModel):
    code: str
    name: str


class OceanVessel(BaseModel):
    imo: int | None
    name: str | None


class OceanLocation(BaseModel):
    code: str
    name: str
    timezone: str
    country: OceanCountry


class OceanPortOfLoading(BaseModel):
    location: OceanLocation
    date_of_loading: datetime | None
    date_of_loading_initial: datetime | None


class OceanPortOfDischarge(BaseModel):
    location: OceanLocation
    date_of_discharge: datetime | None
    date_of_discharge_initial: datetime | None


class OceanRoute(BaseModel):
    port_of_loading: OceanPortOfLoading
    port_of_discharge: OceanPortOfDischarge
    transit_time: int | None
    transit_percentage: int | None
    co2_emission: float | None


class OceanMovement(BaseModel):
    event: Literal["EMSH", "GTIN", "LOAD", "DEPA", "ARRV", "DISC", "GTOT", "EMRT"]
    status: Literal["EST", "ACT"]
    location: OceanLocation
    vessel: OceanVessel | None
    voyage: str | None
    timestamp: datetime


class OceanContainer(BaseModel):
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
    size: int | None
    type: str | None
    movements: list[OceanMovement]


class OceanShipmentCreate(BaseModel):
    booking_number: str


class OceanShipmentBase(BaseModel):
    id: int
    booking_number: str


class OceanShipment(OceanShipmentBase):
    carrier: OceanCarrier | None
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
    route: OceanRoute | None
    containers: list[OceanContainer]
    checked_at: datetime | None
    discarded_at: datetime | None
    changed_at: datetime | None
    created_at: datetime
    updated_at: datetime


# -- Air Shipment Schemas --


class AirAirline(BaseModel):
    iata: str
    name: str


class AirCargo(BaseModel):
    pieces: int | None
    weight: float | None
    volume: float | None


class AirCountry(BaseModel):
    code: str
    name: str


class AirLocation(BaseModel):
    name: str
    iata: str
    timezone: str
    country: AirCountry


class AirRouteOrigin(BaseModel):
    location: AirLocation
    date_of_dep: datetime
    date_of_dep_initial: datetime


class AirRouteDestination(BaseModel):
    location: AirLocation
    date_of_rcf: datetime
    date_of_rcf_initial: datetime


class AirRoute(BaseModel):
    origin: AirRouteOrigin
    ts_count: int
    destination: AirRouteDestination
    transit_time: int
    transit_percentage: int


class AirMovement(BaseModel):
    event: Literal["RCS", "MAN", "DEP", "ARR", "RCF", "DLV"]
    status: Literal["EST", "ACT"]
    cargo: AirCargo
    location: AirLocation
    flight: str | None
    timestamp: datetime


class AirShipmentBase(BaseModel):
    id: int
    awb_number: str


class AirShipment(AirShipmentBase):
    airline: AirAirline | None
    cargo: AirCargo
    status: Literal[
        "NEW",
        "INPROGRESS",
        "BOOKED",
        "EN_ROUTE",
        "LANDED",
        "DELIVERED",
        "UNTRACKED",
    ]
    route: AirRoute | None
    movements: list[AirMovement]
    checked_at: datetime | None
    discarded_at: datetime | None
    changed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AirShipmentCreate(BaseModel):
    awb_number: str = Field(..., pattern=r"^[0-9]{3}(-)?[0-9]{8}$")
