# BBI Container Tracking Python SDK

This repository contains a Python package that can be installed to easily query the BBI Container Tracking REST API.

## Installation

To install this package run the following command:

```
pip install git+https://github.com/Bolk-Business-Improvements/bbi-container-tracking-python-sdk@<COMMIT_SHA>
```

## Usage

After installing the package, import the client:

```
from container_tracking import BBIContainerTracking
import os

client = BBIContainerTracking(api_key=os.environ["CONTAINER_TRACKING_API_KEY"])
```

### Create ocean shipment

```
shipment = client.create_ocean_shipment(booking_number="WECC2588AMS1032")
```

### Read ocean shipment by ID

```
shipment = client.read_ocean_shipment_by_id(1)
```

### Read ocean shipment by booking number (BL)

```
shipment = client.read_ocean_shipment_by_booking_number("WECC2588AMS1032")
```

### Read all ocean shipments (paginated)

```
from datetime import datetime
for shipment in client.read_ocean_shipments_paginated(page_size=100, changed_at_gte=datetime(2025, 8, 28, 1, 0, 0)):
    print(shipment)
```

### List all ocean carriers

```
carriers = client.read_ocean_carriers()
```

### Create air shipment

```
shipment = client.create_air_shipment(awb_number="1234567890")
```

### Read air shipment by ID

```
shipment = client.read_air_shipment_by_id(1)
```

### Read air shipment by AWB number

```
shipment = client.read_air_shipment_by_awb_number("1234567890")
```

### Read all air shipments (paginated)

```
from datetime import datetime
for shipment in client.read_air_shipments_paginated(page_size=100, changed_at_gte=datetime(2025, 8, 28, 1, 0, 0)):
    print(shipment)
```
