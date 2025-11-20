import time
from datetime import datetime
from typing import Iterator, Type, TypeVar

import requests
from loguru import logger
from pydantic import BaseModel, TypeAdapter

from container_tracking.schemas import (
    AirShipment,
    AirShipmentBase,
    OceanCarrierDetail,
    OceanShipment,
    OceanShipmentBase,
    Page,
)

T = TypeVar("T", bound=BaseModel)


class BBIContainerTracking:
    def __init__(self, api_key: str, timeout: int = 10):
        self.base_url = "https://api.container-tracking.bolk-bi.com/v1"
        # self.base_url = "http://localhost:8080/v1"
        self.timeout = timeout
        self.api_key = api_key

    @property
    def headers(self) -> dict:
        """
        Returns the headers to include in API requests.
        """
        return {"X-API-Key": self.api_key}

    def _get_request(
        self, endpoint: str, params: dict | None = None
    ) -> requests.Response:
        """
        Perform a GET request to the BBI API.
        """
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"GET {url} with params {params}")
        response = requests.get(
            url=url,
            headers=self.headers,
            timeout=self.timeout,
            params=params,
        )
        logger.debug(f"GET {response.status_code}: {response.json()}")
        return response

    def _get_request_as_list(
        self,
        endpoint: str,
        model: Type[Page[T] | list[T]],
        params: dict | None = None,
    ) -> tuple[list[T], int]:
        """
        Perform a GET request to the BBI API and return a list of items and the total count.
        """
        response = self._get_request(endpoint=endpoint, params=params)
        response.raise_for_status()

        data = TypeAdapter(model).validate_python(response.json())

        if isinstance(data, list):
            return data, len(data)

        return data.items, data.total

    def _get_request_as_object(
        self, endpoint: str, model: Type[T], params: dict | None = None
    ) -> T | None:
        """
        Perform a GET request to the BBI API and return a list of items and the total count.
        """
        response = self._get_request(endpoint=endpoint, params=params)
        if response.status_code == 404:
            return None

        response.raise_for_status()
        return TypeAdapter(model).validate_python(response.json())

    def _post_request(
        self, endpoint: str, model: Type[T], data: dict | None = None
    ) -> T:
        logger.debug(f"POST {self.base_url}{endpoint} with data {data}")
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data,
            timeout=self.timeout,
        )
        logger.debug(f"POST {response.status_code}: {response.json()}")
        response.raise_for_status()
        return TypeAdapter(model).validate_python(response.json())

    # -- Ocean Shipment Methods --

    def create_ocean_shipment(
        self,
        booking_number: str,
        carrier_scac: str | None = None,
        raise_on_conflict: bool = False,
    ) -> OceanShipmentBase:
        """
        Track a booking by its booking number.
        """
        try:
            return self._post_request(
                endpoint="/ocean/shipments",
                model=OceanShipmentBase,
                data={"booking_number": booking_number, "carrier_scac": carrier_scac},
            )

        except requests.exceptions.HTTPError as e:
            if raise_on_conflict is False and e.response.status_code == 409:
                shipment = self.read_ocean_shipment_by_booking_number(booking_number)
                if shipment is not None:
                    return OceanShipmentBase(
                        id=shipment.id,
                        booking_number=shipment.booking_number,
                    )

                logger.error(f"Shipment not found after conflict: {booking_number}")

            raise e

    def read_ocean_shipment_by_id(self, shipment_id: int) -> OceanShipment | None:
        """
        Retrieve ocean shipment details by ID.
        """
        return self._get_request_as_object(
            endpoint=f"/ocean/shipments/{shipment_id}", model=OceanShipment
        )

    def read_ocean_shipment_by_booking_number(
        self, booking_number: str
    ) -> OceanShipment | None:
        """
        Retrieve ocean shipment details by booking number (BL)
        """
        shipments, _ = self._get_request_as_list(
            endpoint="/ocean/shipments",
            model=Page[OceanShipment],
            params={"booking_number": booking_number},
        )
        if len(shipments) == 0:
            return None

        return shipments[0]

    def read_ocean_shipments(
        self, limit: int, offset: int, changed_at_gte: datetime | None = None
    ) -> list[OceanShipment]:
        """
        Retrieve all ocean shipments.
        """
        shipments, _ = self._get_request_as_list(
            endpoint="/ocean/shipments",
            model=Page[OceanShipment],
            params={
                "limit": limit,
                "offset": offset,
                **({"changed_at_gte": changed_at_gte} if changed_at_gte else {}),
            },
        )
        return shipments

    def read_ocean_shipments_paginated(
        self, page_size: int = 100, changed_at_gte: datetime | None = None
    ) -> Iterator[OceanShipment]:
        """
        Retrieve all ocean shipments with pagination.
        """
        offset = 0
        while True:
            shipments = self.read_ocean_shipments(
                limit=page_size, offset=offset, changed_at_gte=changed_at_gte
            )
            if not shipments:
                break

            yield from shipments
            time.sleep(1)
            offset += page_size

    def read_ocean_carriers(self) -> list[OceanCarrierDetail]:
        """
        Retrieve all ocean carriers.
        """
        carriers, _ = self._get_request_as_list(
            endpoint="/ocean/carriers",
            model=list[OceanCarrierDetail],
        )
        return carriers

    # -- Air Shipment Methods --

    def create_air_shipment(
        self, awb_number: str, raise_on_conflict: bool = False
    ) -> AirShipmentBase:
        """
        Track a booking by its booking number.
        """
        try:
            return self._post_request(
                endpoint="/air/shipments",
                model=AirShipmentBase,
                data={"awb_number": awb_number},
            )

        except requests.exceptions.HTTPError as e:
            if raise_on_conflict is False and e.response.status_code == 409:
                shipment = self.read_air_shipment_by_awb_number(awb_number)
                if shipment is not None:
                    return AirShipmentBase(
                        id=shipment.id,
                        awb_number=shipment.awb_number,
                    )

                logger.error(f"Shipment not found after conflict: {awb_number}")

            raise e

    def read_air_shipment_by_id(self, shipment_id: int) -> AirShipment | None:
        """
        Retrieve air shipment details by ID.
        """
        return self._get_request_as_object(
            endpoint=f"/air/shipments/{shipment_id}", model=AirShipment
        )

    def read_air_shipment_by_awb_number(self, awb_number: str) -> AirShipment | None:
        """
        Retrieve air shipment details by awb number (AWB)
        """
        shipments, _ = self._get_request_as_list(
            endpoint="/air/shipments",
            model=Page[AirShipment],
            params={"awb_number": awb_number},
        )
        if len(shipments) == 0:
            return None

        return shipments[0]

    def read_air_shipments(
        self, limit: int, offset: int, changed_at_gte: datetime | None = None
    ) -> list[AirShipment]:
        """
        Retrieve all air shipments.
        """
        shipments, _ = self._get_request_as_list(
            endpoint="/air/shipments",
            model=Page[AirShipment],
            params={
                "limit": limit,
                "offset": offset,
                **({"changed_at_gte": changed_at_gte} if changed_at_gte else {}),
            },
        )
        return shipments

    def read_air_shipments_paginated(
        self, page_size: int = 100, changed_at_gte: datetime | None = None
    ) -> Iterator[AirShipment]:
        """
        Retrieve all air shipments with pagination.
        """
        offset = 0
        while True:
            shipments = self.read_air_shipments(
                limit=page_size, offset=offset, changed_at_gte=changed_at_gte
            )
            if not shipments:
                break

            yield from shipments
            offset += page_size
