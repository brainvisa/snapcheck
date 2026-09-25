#!/bin/bash
# Generate typed API client from OpenAPI schema

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENAPI_FILE="$PROJECT_ROOT/openapi.json"

if [ ! -f "$OPENAPI_FILE" ]; then
    echo "Error: $OPENAPI_FILE not found"
    echo "Run: python scripts/export_openapi.py"
    exit 1
fi

echo "Generating API client from $OPENAPI_FILE..."

cd "$PROJECT_ROOT"

npx @hey-api/openapi-ts \
    --input "$OPENAPI_FILE" \
    --output ./src/api/generated \
    --client axios \
    --plugins @tanstack/react-query@7

echo "✓ API client generated in src/api/generated/"
echo ""
echo "Next steps:"
echo "  1. npm run typecheck   # Verify TypeScript compilation"
echo "  2. Update imports to use @lepton/api instead of @lepton/api-client"
