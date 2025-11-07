from datetime import datetime
from typing import Iterator, Optional, Type, TypeVar

import requests
from loguru import logger
from pydantic import BaseModel, TypeAdapter

from container_tracking.schemas import Page, Shipment, ShipmentBase

T = TypeVar("T", bound=BaseModel)


class BBIContainerTracking:
    def __init__(self, api_key: str, timeout: int = 10):
        self.base_url = "https://api.container-tracking.bolk-bi.com/v1"
        self.timeout = timeout
        self.api_key = api_key

    @property
    def headers(self) -> dict:
        """
        Returns the headers to include in API requests.
        """
        return {"X-API-Key": self.api_key}

    def _get_request(
        self, endpoint: str, params: Optional[dict] = None
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
        self, endpoint: str, model: Type[Page[T]], params: Optional[dict] = None
    ) -> tuple[list[T], int]:
        """
        Perform a GET request to the BBI API and return a list of items and the total count.
        """
        response = self._get_request(endpoint=endpoint, params=params)
        response.raise_for_status()

        data = TypeAdapter(model).validate_python(response.json())
        return data.items, data.total

    def _get_request_as_object(
        self, endpoint: str, model: Type[T], params: Optional[dict] = None
    ) -> Optional[T]:
        """
        Perform a GET request to the BBI API and return a list of items and the total count.
        """
        response = self._get_request(endpoint=endpoint, params=params)
        if response.status_code == 404:
            return None

        response.raise_for_status()
        return TypeAdapter(model).validate_python(response.json())

    def _post_request(
        self, endpoint: str, model: Type[T], data: Optional[dict] = None
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

    def create_shipment(
        self, booking_number: str, raise_on_conflict: bool = False
    ) -> ShipmentBase:
        """
        Track a booking by its booking number.
        """
        try:
            return self._post_request(
                endpoint="/shipments",
                model=ShipmentBase,
                data={"booking_number": booking_number},
            )

        except requests.exceptions.HTTPError as e:
            if raise_on_conflict is False and e.response.status_code == 409:
                shipment = self.read_shipment_by_booking_number(booking_number)
                if shipment is not None:
                    return ShipmentBase(
                        id=shipment.id,
                        booking_number=shipment.booking_number,
                    )

                logger.error(f"Shipment not found after conflict: {booking_number}")

            raise e

    def read_shipment_by_id(self, shipment_id: int) -> Optional[Shipment]:
        """
        Retrieve shipment details by ID.
        """
        return self._get_request_as_object(
            endpoint=f"/shipments/{shipment_id}", model=Shipment
        )

    def read_shipment_by_booking_number(
        self, booking_number: str
    ) -> Optional[Shipment]:
        """
        Retrieve shipment details by booking number (BL)
        """
        shipments, _ = self._get_request_as_list(
            endpoint="/shipments",
            model=Page[Shipment],
            params={"booking_number": booking_number},
        )
        if len(shipments) == 0:
            return None

        return shipments[0]

    def read_shipments(
        self, limit: int, offset: int, changed_at_gte: Optional[datetime] = None
    ) -> list[Shipment]:
        """
        Retrieve all shipments.
        """
        shipments, _ = self._get_request_as_list(
            endpoint="/shipments",
            model=Page[Shipment],
            params={
                "limit": limit,
                "offset": offset,
                **({"changed_at_gte": changed_at_gte} if changed_at_gte else {}),
            },
        )
        return shipments

    def read_shipments_paginated(
        self, page_size: int = 100, changed_at_gte: Optional[datetime] = None
    ) -> Iterator[Shipment]:
        """
        Retrieve all shipments with pagination.
        """
        offset = 0
        while True:
            shipments = self.read_shipments(
                limit=page_size, offset=offset, changed_at_gte=changed_at_gte
            )
            if not shipments:
                break

            yield from shipments
            offset += page_size
