# BBI Container Tracking Python SDK

This repository contains a Python package that can be installed to easily query the BBI Container Tracking REST API.

## Installation

To install this package run the following command:

```
pip install git+https://github.com/Bolk-Business-Improvements/bbi-container-tracking-python-sdk@<COMMIT_SHA>
```

## Usage

### Import

After installing the package, a client can be imported that can be used to query the REST API.

```
...

from container_tracking import BBIContainerTracking

client = BBIContainerTracking(api_key=os.environ["CONTAINER_TRACKING_API_KEY"])

...
```

### Create shipment

```
shipment = client.create_shipment(booking_number="WECC2588AMS1032")
```

### Read shipment by id

```
shipment = client.read_shipment_by_id(1)
```

### Read shipment by booking number (BL)

```
shipment = client.read_shipment_by_booking_number("WECC2588AMS1032")
```

### Read changed shipments

```
...

from datetime import datetime

for shipment in client.read_shipments_paginated(
        page_size=100, changed_at_gte=datetime(2025, 8, 28, 1, 0, 0)
    ):
    print(shipment)

...
```
