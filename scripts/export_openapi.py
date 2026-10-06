#!/usr/bin/env python
"""Export OpenAPI schema from the Snapcheck FastAPI app"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from snapserve.app import app

# Get the OpenAPI schema
openapi_schema = app.app.openapi()

# Write to file
output_file = Path(__file__).parent.parent / "openapi.json"
with open(output_file, "w") as f:
    json.dump(openapi_schema, f, indent=2)

print(f"OpenAPI schema exported to: {output_file}")
