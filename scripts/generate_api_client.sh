#!/bin/bash
# Generate the typed API client + TanStack Query options from the OpenAPI schema.
# Configuration lives in openapi-ts.config.ts (hey-api v0.99+).
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Exporting OpenAPI schema..."
python scripts/export_openapi.py

echo "Generating API client (client-axios + @tanstack/react-query)..."
npx @hey-api/openapi-ts

echo "✓ Client generated in src/api/generated/ (sdk.gen.ts, @tanstack/react-query.gen.ts)"
