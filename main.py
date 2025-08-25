import os

from dotenv import load_dotenv

from container_tracking import BBIContainerTracking

load_dotenv()

api_key = os.environ["CONTAINER_TRACKING_KEY"]
ct = BBIContainerTracking(api_key=api_key)


if __name__ == "__main__":
    shipment = ct.read_shipment_by_id(shipment_id=1)
    if shipment is None or shipment.booking_number is None:
        raise ValueError("Shipment with ID 1 not found")
    print(shipment.booking_number)

    shipment = ct.read_shipment_by_booking_number(
        booking_number=shipment.booking_number
    )

    if shipment is None:
        raise ValueError("Shipment was not found")

    print(shipment)
