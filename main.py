import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger

from container_tracking import BBIContainerTracking

logger.remove()
logger.add(sys.stderr, level="DEBUG")

load_dotenv()

client = BBIContainerTracking(api_key=os.environ["CONTAINER_TRACKING_API_KEY"])

if __name__ == "__main__":
    shipment = client.read_shipment_by_booking_number("WECC2588AMS1032")
    if shipment is None:
        shipment = client.create_shipment(booking_number="GQL0408947")

    shipment = client.read_shipment_by_id(1)
    logger.info(shipment.booking_number if shipment else "Not found")

    shipment = client.read_shipment_by_booking_number("WECC2588AMS1032")
    logger.info(shipment.id if shipment else "Not found")

    for shipment in client.read_shipments_paginated(
        page_size=1, changed_at_gte=datetime(2025, 8, 28, 1, 0, 0)
    ):
        print(shipment)
        logger.info(
            f"{shipment.booking_number} has {len(shipment.containers)} containers"
        )
        for container in shipment.containers:
            print(container)
