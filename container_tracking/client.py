from typing import Optional, Type, TypeVar, overload

import requests
from pydantic import BaseModel, TypeAdapter

from container_tracking.schemas import Shipment, ShipmentBase

T = TypeVar("T", bound=BaseModel)


class BBIContainerTracking:
    def __init__(self, api_key: str, timeout: int = 10):
        self.base_url = "https://api.container-tracking.bolk-bi.com"
        self.timeout = timeout
        self.api_key = api_key

    @property
    def headers(self) -> dict:
        """
        Returns the headers to include in API requests.
        """
        return {"X-API-Key": self.api_key}

    @overload
    def _get_request(
        self, endpoint: str, model: Type[T], params: Optional[dict] = None
    ) -> Optional[T]: ...

    @overload
    def _get_request(
        self, endpoint: str, model: Type[list[T]], params: Optional[dict] = None
    ) -> list[T]: ...

    def _get_request(
        self,
        endpoint: str,
        model: Type[T] | Type[list[T]],
        params: Optional[dict] = None,
    ) -> Optional[T] | Optional[list[T]]:
        """
        Perform a GET request to the BBI API.
        """
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

        if model is not list and response.status_code == 404:
            return None

        response.raise_for_status()
        return TypeAdapter(model).validate_python(response.json())

    def _post_request(
        self, endpoint: str, model: Type[T], data: Optional[dict] = None
    ) -> T:
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return TypeAdapter(model).validate_python(response.json())

    def create_shipment(self, booking_number: str) -> ShipmentBase:
        """
        Track a booking by its booking number.
        """
        return self._post_request(
            endpoint="/shipments",
            model=ShipmentBase,
            data={"booking_number": booking_number},
        )

    def read_shipment_by_id(self, shipment_id: int) -> Optional[Shipment]:
        """
        Retrieve shipment details by ID.
        """
        return self._get_request(endpoint=f"/shipments/{shipment_id}", model=Shipment)

    def read_shipment_by_booking_number(
        self, booking_number: str
    ) -> Optional[Shipment]:
        """
        Retrieve shipment details by booking number (BL)
        """
        shipments = self._get_request(
            endpoint="/shipments",
            model=list[Shipment],
            params={"booking_number": booking_number},
        )
        if len(shipments) == 0:
            return None

        return shipments[0]
